"""Image LLM protocols. No tools, remote image URLs, retries, or implicit fallback."""

import json
from typing import Any

from backend.config import ModelOption
from backend.errors import ProviderError
from backend.models import Evidence, Payment, Routing
from backend.providers import PROMPT, VisionExtraction, structured_schema
from backend.runtime import Context, Extraction


def vision_request(
    option: ModelOption, encoded: str, key: str
) -> tuple[str, dict[str, str], dict[str, Any]]:
    provider = option.provider
    model, limit = option.model, option.max_output_tokens
    schema = structured_schema()
    instructions = PROMPT
    if option.protocol_version in {"4", "5", "6"}:
        from backend.adapters.compact import PROMPT as compact_prompt
        from backend.adapters.compact import schema as compact_schema

        schema, instructions = compact_schema(option.protocol_version), compact_prompt
        if option.protocol_version in {"5", "6"}:
            from backend.adapters.compact import PROMPT_V5

            instructions = PROMPT_V5
        if option.interpretation_policy == "draft_v1":
            from backend.draft_policy import prompt_v1

            instructions = prompt_v1(instructions)
        elif option.interpretation_policy == "draft_v2":
            from backend.recipient_roles import prompt_v2, role_schema

            instructions, schema = prompt_v2(instructions), role_schema(schema)
        elif option.interpretation_policy == "draft_v3":
            from backend.recipient_roles import prompt_v2, role_schema_v2

            instructions, schema = prompt_v2(instructions), role_schema_v2(schema)
        elif option.interpretation_policy == "draft_v4":
            from backend.recipient_roles import prompt_v3, role_schema_v2

            instructions, schema = prompt_v3(instructions), role_schema_v2(schema)
        if option.context_policy == "invoice_v1":
            from backend.invoice_context import context_prompt, context_schema

            instructions, schema = context_prompt(instructions), context_schema(schema)
        # Together recommends both constrained output and a prompt copy of the schema.
        if provider == "together":
            instructions += "\nJSON schema:\n" + json.dumps(schema)
    if option.protocol_version == "3":
        instructions += "\nEvidence boxes, if supplied, MUST be normalized [x, y, width, height] within the image: every number is between 0 and 1, x+width <=1 and y+height <=1. Never use pixels or 0-1000 coordinates. Use bbox:null when uncertain, and retain a verbatim excerpt. Return only JSON without markdown fences."
        box = schema["$defs"]["Claim"]["properties"]["bbox"]
        box["description"] = (
            "Optional normalized [x,y,width,height], not pixels; use null if uncertain."
        )
        for variant in box["anyOf"]:
            if variant.get("type") == "array":
                variant["items"].update(minimum=0, maximum=1)
    if provider == "anthropic":
        if option.protocol_version in {"2", "3", "4", "5", "6"} and option.schema_mode == "native":

            def simplify(node: Any) -> Any:
                if isinstance(node, list):
                    return [simplify(item) for item in node]
                if not isinstance(node, dict):
                    return node
                unsupported = {
                    key: value
                    for key, value in node.items()
                    if key
                    in {
                        "minimum",
                        "maximum",
                        "exclusiveMinimum",
                        "exclusiveMaximum",
                        "multipleOf",
                        "minLength",
                        "maxLength",
                        "minItems",
                        "maxItems",
                    }
                }
                result = {
                    key: simplify(value) for key, value in node.items() if key not in unsupported
                }
                if unsupported:
                    result["description"] = (
                        result.get("description", "")
                        + " Constraints validated locally: "
                        + json.dumps(unsupported)
                    )
                return result

            schema = simplify(schema)
        anthropic_body: dict[str, Any] = {
            "model": model,
            "max_tokens": limit,
            "system": instructions,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": encoded,
                            },
                        },
                        {"type": "text", "text": "Extract the printed payment fields."},
                    ],
                }
            ],
        }
        if option.reasoning == "adaptive":
            anthropic_body["thinking"] = {"type": "adaptive"}
        if option.schema_mode == "prompt_json":
            anthropic_body["system"] += (
                "\nReturn only JSON, without markdown fences, matching this schema:\n"
                + json.dumps(schema)
            )
        else:
            anthropic_body["output_config"] = {"format": {"type": "json_schema", "schema": schema}}
        return (
            "/v1/messages",
            {"x-api-key": key, "anthropic-version": "2023-06-01"},
            anthropic_body,
        )
    if provider == "gemini":
        generation = {"maxOutputTokens": limit, "responseMimeType": "application/json"}
        if option.schema_mode == "prompt_json":
            instructions += "\nReturn JSON matching this schema:\n" + json.dumps(schema)
        else:
            generation["responseJsonSchema"] = schema
        return (
            f"/v1beta/models/{model}:generateContent",
            {"x-goog-api-key": key},
            {
                "systemInstruction": {"parts": [{"text": instructions}]},
                "contents": [
                    {
                        "role": "user",
                        "parts": [
                            {"inline_data": {"mime_type": "image/png", "data": encoded}},
                            {"text": "Extract the printed payment fields."},
                        ],
                    }
                ],
                "generationConfig": generation,
            },
        )
    if provider == "openai":
        body: dict[str, Any] = {
            "model": model,
            "instructions": instructions,
            "input": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_image",
                            "image_url": "data:image/png;base64," + encoded,
                            "detail": "high",
                        }
                    ],
                }
            ],
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "payment_extraction",
                    "strict": True,
                    "schema": schema,
                }
            },
            "max_output_tokens": limit,
            "store": False,
            "tools": [],
            "tool_choice": "none",
            "service_tier": "default",
        }
        if option.reasoning is not None:
            body["reasoning"] = {"effort": option.reasoning}
        return "/v1/responses", {"Authorization": "Bearer " + key}, body
    # Each compatible host remains its own selected recipient/model.
    extra: dict[str, Any] = (
        {"reasoning_effort": option.reasoning} if provider == "xai" and option.reasoning else {}
    )
    if provider == "together" and option.reasoning is not None:
        extra["chat_template_kwargs"] = {"enable_thinking": option.reasoning != "none"}
    return (
        "/v1/chat/completions",
        {"Authorization": "Bearer " + key},
        {
            "model": model,
            "max_tokens": limit,
            **extra,
            "messages": [
                {"role": "system", "content": instructions},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract the printed payment fields."},
                        {
                            "type": "image_url",
                            "image_url": {"url": "data:image/png;base64," + encoded},
                        },
                    ],
                },
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "payment_extraction",
                    "strict": True,
                    "schema": schema,
                },
            },
        },
    )


def vision_text(
    body: dict[str, Any], provider: str, *, adaptive_thinking: bool = False
) -> tuple[str, str | None]:
    if provider == "anthropic":
        if body.get("stop_reason") == "refusal":
            raise ProviderError("provider_refusal")
        parts = body["content"]
        allowed = {"text", "thinking", "redacted_thinking"} if adaptive_thinking else {"text"}
        if body["stop_reason"] != "end_turn" or any(p["type"] not in allowed for p in parts):
            raise ProviderError("invalid_provider_output")
        return "".join(p["text"] for p in parts if p["type"] == "text"), body.get("model")
    if provider == "gemini":
        if body.get("promptFeedback", {}).get("blockReason"):
            raise ProviderError("provider_refusal")
        (candidate,) = body["candidates"]
        if candidate.get("finishReason") in {"SAFETY", "RECITATION", "PROHIBITED_CONTENT"}:
            raise ProviderError("provider_refusal")
        parts = candidate["content"]["parts"]
        if candidate["finishReason"] != "STOP" or any(
            set(p) - {"text", "thought", "thoughtSignature"} for p in parts
        ):
            raise ProviderError("invalid_provider_output")
        return "".join(p["text"] for p in parts if not p.get("thought")), body.get("modelVersion")
    if provider == "openai":
        parts = [p for item in body["output"] if item["type"] == "message" for p in item["content"]]
        if any(p["type"] == "refusal" for p in parts):
            raise ProviderError("provider_refusal")
        if body["status"] != "completed" or any(
            i["type"] not in {"message", "reasoning"} for i in body["output"]
        ):
            raise ProviderError("invalid_provider_output")
        return "".join(p["text"] for p in parts if p["type"] == "output_text"), body.get("model")
    (choice,) = body["choices"]
    message = choice["message"]
    if message.get("refusal") or choice["finish_reason"] == "content_filter":
        raise ProviderError("provider_refusal")
    if (
        choice["finish_reason"] != "stop"
        or message.get("tool_calls")
        or message.get("function_call")
    ):
        raise ProviderError("invalid_provider_output")
    return str(message["content"]), body.get("model")


def claims(text: str, context: Context, stage_id: str) -> Extraction:
    parsed = VisionExtraction.model_validate(json.loads(text))
    evidence = [
        Evidence(
            **e.model_dump(),
            image_id=context.scan.input.image_id,
            grounding="model_claim",
            source_stage_id=stage_id,
        )
        for e in parsed.evidence
    ]
    return Extraction(
        Payment(**parsed.payment.model_dump()),
        evidence,
        Routing(applied_rule_packs=["generic-review@2"], reasons=["Unverified model claims."]),
    )
