import asyncio
import hmac
import json
import logging
import sqlite3
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated, Any

from fastapi import Depends, FastAPI, File, Form, Header, Request, Response, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import ValidationError
from starlette.exceptions import HTTPException

from backend.config import Settings
from backend.errors import ServiceError
from backend.images import prepare_image
from backend.models import Accepted, Error, ErrorResponse, Options, Scan
from backend.profiles import Definition, ProfilesResponse, registry, resolve, validate_limits
from backend.runtime import Adapter, Runtime
from backend.store import Store, request_digest


def create_app(
    settings: Settings | None = None,
    definitions: dict[str, Definition] | None = None,
    adapters: dict[str, Adapter] | None = None,
) -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        for logger in ("openai", "httpx", "httpcore"):
            logging.getLogger(logger).setLevel(logging.WARNING)
        active_settings = settings or Settings.from_env()
        active_definitions = definitions if definitions is not None else registry(active_settings)
        if adapters is None:
            from backend.providers import MistralAdapter, OpenAIAdapter

            active_adapters: dict[str, Adapter] = {
                "openai": OpenAIAdapter(active_settings),
                "mistral": MistralAdapter(active_settings),
            }
        else:
            active_adapters = adapters
        store = Store(active_settings)
        runtime = Runtime(store, active_settings, active_adapters)
        app.state.settings, app.state.definitions = active_settings, active_definitions
        app.state.store, app.state.runtime = store, runtime
        app.state.decode_slots = asyncio.Semaphore(2)
        runtime.start()
        try:
            yield
        finally:
            await runtime.stop()
            store.close()

    # Deliberately no browser UI or unauthenticated docs/OpenAPI route.
    app = FastAPI(
        title="Scan and Pay",
        version="1.0",
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    bearer = HTTPBearer(auto_error=False)

    def auth(
        request: Request,
        credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
    ) -> None:
        if credentials is None or not hmac.compare_digest(
            credentials.credentials, request.app.state.settings.token.get_secret_value()
        ):
            raise ServiceError(401, "unauthorized", "A valid local bearer token is required.")

    @app.exception_handler(ServiceError)
    async def service_error(request: Request, exc: ServiceError) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status,
            content=ErrorResponse(error=exc.error).model_dump(),
            headers={"WWW-Authenticate": "Bearer"} if exc.status == 401 else None,
        )

    @app.exception_handler(RequestValidationError)
    async def validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content=ErrorResponse(
                error=Error(
                    code="invalid_request", message="Request fields do not match the v1 contract."
                )
            ).model_dump(),
        )

    @app.exception_handler(HTTPException)
    async def http_error(request: Request, exc: HTTPException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content=ErrorResponse(
                error=Error(code="invalid_request", message="Request could not be processed.")
            ).model_dump(),
        )

    @app.exception_handler(OSError)
    @app.exception_handler(sqlite3.Error)
    async def storage_error(request: Request, exc: Exception) -> JSONResponse:
        return JSONResponse(
            status_code=503,
            content=ErrorResponse(
                error=Error(
                    code="service_unavailable",
                    message="Local storage is unavailable.",
                    retryable=True,
                )
            ).model_dump(),
        )

    @app.get("/health")
    async def health(request: Request) -> Response:
        try:
            ready = request.app.state.runtime.healthy and await asyncio.to_thread(
                request.app.state.store.ready
            )
        except (OSError, sqlite3.Error):
            ready = False
        return JSONResponse(
            {"status": "ok" if ready else "unavailable"}, status_code=200 if ready else 503
        )

    @app.get("/v1/profiles", response_model=ProfilesResponse, dependencies=[Depends(auth)])
    async def profiles(request: Request) -> ProfilesResponse:
        store: Store = request.app.state.store
        values = []
        for _, definition in sorted(request.app.state.definitions.items()):
            value = definition.metadata.model_copy(deep=True)
            value.live_validated = store.is_validated(value.id, value.version)
            values.append(value)
        return ProfilesResponse(
            profiles=values,
            default_extract_profile_id=request.app.state.settings.providers.default_extract_profile_id,
        )

    error_models: dict[int | str, dict[str, Any]] = {
        code: {"model": ErrorResponse}
        for code in (400, 401, 404, 409, 410, 413, 415, 422, 429, 503)
    }

    @app.post(
        "/v1/scans",
        response_model=Accepted,
        status_code=202,
        responses=error_models,
        dependencies=[Depends(auth)],
    )
    async def submit(
        request: Request,
        response: Response,
        image: Annotated[UploadFile, File()],
        options: Annotated[str, Form()],
        idempotency_key: Annotated[str, Header(min_length=1)],
    ) -> Accepted:
        form = await request.form()
        if (
            set(form) != {"image", "options"}
            or len(form.getlist("image")) != 1
            or len(form.getlist("options")) != 1
        ):
            raise ServiceError(
                422, "invalid_request", "Exactly one image and options object are required."
            )
        try:
            parsed = json.loads(options)
        except (ValueError, RecursionError):
            raise ServiceError(400, "invalid_json", "Options must be valid JSON.") from None
        try:
            selected = Options.model_validate(parsed)
        except ValidationError:
            raise ServiceError(
                422, "invalid_options", "Options do not match the v1 contract."
            ) from None
        runtime: Runtime = request.app.state.runtime
        store: Store = request.app.state.store
        if not runtime.healthy:
            raise ServiceError(503, "service_unavailable", "Worker storage requires recovery.")
        async with request.app.state.decode_slots:
            data = await image.read()
            digest = await asyncio.to_thread(request_digest, data, selected)
            existing = await asyncio.to_thread(store.existing, idempotency_key, digest)
            if existing:
                scan = existing
            else:
                prepared = await asyncio.to_thread(prepare_image, data, selected.hints)
                resolved, excluded = resolve(
                    selected, prepared.identity.mime_type, request.app.state.definitions
                )
                validate_limits(prepared, resolved)
                # Atomic acceptance happens before dispatch; no await between these steps.
                scan, created = store.accept(
                    idempotency_key, digest, prepared, selected, resolved, excluded
                )
                if created:
                    runtime.submit(scan.scan_id, resolved)
        status_url = "/v1/scans/" + scan.scan_id
        response.headers["Location"] = status_url
        return Accepted(scan_id=scan.scan_id, state=scan.state, status_url=status_url)

    @app.get(
        "/v1/scans/{scan_id}",
        response_model=Scan,
        responses=error_models,
        dependencies=[Depends(auth)],
    )
    async def get_scan(request: Request, scan_id: str) -> Scan:
        return await asyncio.to_thread(request.app.state.store.get, scan_id)

    @app.delete(
        "/v1/scans/{scan_id}", status_code=204, responses=error_models, dependencies=[Depends(auth)]
    )
    async def delete_scan(request: Request, scan_id: str) -> Response:
        await asyncio.to_thread(request.app.state.store.delete, scan_id)
        return Response(status_code=204)

    return app
