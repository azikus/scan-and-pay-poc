"""Transport/version/contract guards; real model role behavior needs fresh inference."""

import copy
import json
from decimal import Decimal

import pytest
from pydantic import ValidationError

from backend.adapters.compact import PROMPT_V5, schema
from backend.adapters.vision import vision_request
from backend.config import BudgetPlan, ModelOption, Settings
from backend.draft_policy import prompt_v1
from backend.profiles import registry
from backend.recipient_roles import prompt_v2, role_schema
from backend.tests.test_extended import configured


@pytest.mark.parametrize(
    "provider", ["openai", "mistral", "anthropic", "gemini", "xai", "together"]
)
@pytest.mark.parametrize(
    "policy,revision", [("draft_v2", "1"), ("draft_v3", "2"), ("draft_v4", "3")]
)
def test_new_role_definitions_are_sent_without_mutating_prior_profiles(
    settings, provider, policy, revision
):
    configured(settings, provider)
    option = settings.providers.options["test-profile"]
    option.protocol_version = "6" if provider == "gemini" else "5"
    previous = {}
    for old_policy in ["strict", "draft_v1"]:
        option.interpretation_policy = old_policy
        previous[old_policy] = (
            registry(settings)["test-profile"].snapshot(),
            vision_request(option, "synthetic", "secret"),
        )
    option.interpretation_policy = policy
    definition = registry(settings)["test-profile"]
    request = vision_request(option, "synthetic", "secret")
    serialized = json.dumps(request[2])
    assert "Ente creditore" in serialized and "RECIPIENT BANK ACCOUNT" in serialized
    assert "follow the" in serialized and "printed direction" in serialized
    assert "payment-party-roles@" + revision in definition.metadata.component_ids
    assert definition.parameters["prompt"].endswith("+party-roles@" + revision)
    assert all(
        definition.metadata.version != old[0]["profile"]["version"] for old in previous.values()
    )
    for policy, old in previous.items():
        option.interpretation_policy = policy
        assert (
            registry(settings)["test-profile"].snapshot(),
            vision_request(option, "synthetic", "secret"),
        ) == old


@pytest.mark.parametrize("version", ["5", "6"])
def test_schema_role_help_does_not_change_response_shape_or_old_schema(version):
    old = schema(version)
    saved = copy.deepcopy(old)
    new = role_schema(old)
    assert old == saved and new != old
    changes = []
    for node in [new, *new["$defs"].values()]:
        for name, field in node.get("properties", {}).items():
            if name in {"beneficiary_name", "account_holder_name", "supplier_name"}:
                changes.append(name)
                field.pop("description")
    assert set(changes) == {"beneficiary_name", "account_holder_name", "supplier_name"}
    assert new == old


def test_role_revision_retains_other_instructions_and_avoids_ambiguous_recipient_language():
    old = prompt_v1(PROMPT_V5)
    new = prompt_v2(PROMPT_V5)
    assert (
        new[new.index("Copy amount_text exactly") :] == old[old.index("Copy amount_text exactly") :]
    )
    assert (
        new[: new.index("Payment-party roles")].strip()
        == old[: old.index("Keep supplier, billed")].strip()
    )
    assert (
        "Keep supplier, billed customer, beneficiary and account holder as distinct printed roles."
        not in new
    )
    assert (
        "refund" in new
        and "manager" in new
        and "Personal names are not inherently payer or payee" in new
    )


@pytest.mark.parametrize("operation,protocol", [("vision", "1"), ("ocr", "5")])
def test_role_prompt_cannot_be_attached_to_unsupported_operation(operation, protocol):
    with pytest.raises(ValidationError):
        ModelOption(
            provider="mistral",
            model="synthetic",
            operation=operation,
            protocol_version=protocol,
            interpretation_policy="draft_v2",
        )


@pytest.mark.parametrize("with_plan", [False, True])
def test_legacy_runtime_limits_need_no_plan_or_matching_values(settings, with_plan):
    data = settings.model_dump()
    data.update(max_calls=10001, smoke_budget_eur=Decimal("501"))
    if with_plan:
        data["providers"]["budget_plan"] = BudgetPlan(
            reference="legacy", cumulative_call_cap=1, cumulative_hold_eur="0"
        ).model_dump()
    assert Settings.model_validate(data).max_calls == 10001
    assert Settings.model_validate(data).smoke_budget_eur == Decimal("501")


@pytest.mark.parametrize("version", ["5", "6"])
def test_native_role_schema_has_no_ref_siblings_and_preserves_validation(version):
    import jsonschema

    from backend.recipient_roles import role_schema_v2
    from backend.tests.test_compact import example_v5

    old = schema(version)
    saved = copy.deepcopy(old)
    new = role_schema_v2(old)

    def inspect(node):
        if isinstance(node, dict):
            if "$ref" in node:
                assert set(node) == {"$ref"}
            for value in node.values():
                inspect(value)
        elif isinstance(node, list):
            for value in node:
                inspect(value)

    inspect(new)
    assert old == saved
    data = example_v5()
    jsonschema.validate(data, new)
    data["candidates"][0]["beneficiary_name"]["values"] = "wrong type"
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(data, new)
    assert "description" in new["$defs"]["PaymentOptionV5"]["properties"]["beneficiary_name"]


def test_represented_issuer_revision_preserves_previous_prompt():
    from backend.recipient_roles import prompt_v3

    previous = prompt_v2(PROMPT_V5)
    new = prompt_v3(PROMPT_V5)
    assert new.startswith(previous)
    assert "represented by" in new and "Retain every printed payment option" in new
    assert "manager billing its own fees" in new
