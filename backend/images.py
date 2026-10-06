import hashlib
import io
import warnings
from dataclasses import dataclass
from time import monotonic
from uuid import uuid4

from PIL import Image, ImageOps, UnidentifiedImageError

from backend.errors import ServiceError
from backend.models import Hints, ImageInput


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass(frozen=True)
class PreparedImage:
    identity: ImageInput
    original: bytes
    canonical: bytes
    transforms: list[str]
    duration_ms: float


def prepare_image(data: bytes, hints: Hints) -> PreparedImage:
    start = monotonic()
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(io.BytesIO(data)) as source:
                if source.format not in {"JPEG", "PNG"}:
                    raise ServiceError(
                        415, "unsupported_image", "Only JPEG and PNG images are supported."
                    )
                if getattr(source, "n_frames", 1) != 1:
                    raise ServiceError(415, "unsupported_image", "One still image is required.")
                source.verify()
            with Image.open(io.BytesIO(data)) as source:
                source.load()
                orientation = source.getexif().get(274, 1)
                oriented = ImageOps.exif_transpose(source).convert("RGBA")
                # Flatten transparency on white; canonical PNG is lossless and metadata-free.
                canonical = Image.new("RGB", oriented.size, "white")
                canonical.paste(oriented, mask=oriented.getchannel("A"))
                output = io.BytesIO()
                canonical.save(output, format="PNG")
                content = output.getvalue()
                identity = ImageInput(
                    image_id="image-" + uuid4().hex,
                    original_sha256=sha256(data),
                    canonical_sha256=sha256(content),
                    width=canonical.width,
                    height=canonical.height,
                    mime_type="image/png",
                    hints=hints,
                )
                return PreparedImage(
                    identity,
                    data,
                    content,
                    [
                        f"exif_orientation:{orientation}",
                        "flatten_alpha_white",
                        "rgb_png_metadata_removed",
                    ],
                    (monotonic() - start) * 1000,
                )
    except UnidentifiedImageError as exc:
        if data.startswith((b"%PDF", b"GIF", b"RIFF")) or data[4:8] == b"ftyp":
            raise ServiceError(
                415, "unsupported_image", "Only JPEG and PNG images are supported."
            ) from exc
        raise ServiceError(400, "invalid_image", "Image bytes cannot be decoded.") from exc
    except (
        OSError,
        ValueError,
        SyntaxError,
        Image.DecompressionBombError,
        Image.DecompressionBombWarning,
    ) as exc:
        raise ServiceError(
            400, "invalid_image", "Image bytes could not be decoded safely."
        ) from exc
