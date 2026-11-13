"""Pinned, role-exclusive free-model assignments for the AURIONS workforce.

Assignments are selection hypotheses based on documented capabilities, not proof of
qualification. Changing an assignment requires a reviewed registry change and new
role-specific evaluation.
"""

from __future__ import annotations

ROLE_MODEL_ASSIGNMENTS = {
    "lead_builder": {
        "provider": "groq",
        "model": "openai/gpt-oss-120b",
        "api_url": "https://api.groq.com/openai/v1/chat/completions",
        "key_env": "GROQ_API_KEY",
        "account_env": "",
        "cost_class": "free",
        "selection_basis": "Large reasoning model with coding and tool-use support for the primary implementation owner.",
    },
    "specialist_builder": {
        "provider": "cloudflare",
        "model": "@cf/google/gemma-4-26b-a4b-it",
        "api_url": "https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/v1/chat/completions",
        "key_env": "CLOUDFLARE_API_TOKEN",
        "account_env": "CLOUDFLARE_ACCOUNT_ID",
        "cost_class": "free_daily_allowance",
        "selection_basis": "Reasoning, code generation, vision and native function calling with a 256K context.",
    },
    "architecture_reviewer": {
        "provider": "cloudflare",
        "model": "@cf/zai-org/glm-4.7-flash",
        "api_url": "https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/v1/chat/completions",
        "key_env": "CLOUDFLARE_API_TOKEN",
        "account_env": "CLOUDFLARE_ACCOUNT_ID",
        "cost_class": "free_daily_allowance",
        "selection_basis": "Reasoning and multi-turn function calling, 131K context, suitable for bounded architecture review.",
    },
    "code_reviewer": {
        "provider": "groq",
        "model": "qwen/qwen3.8-27b",
        "api_url": "https://api.groq.com/openai/v1/chat/completions",
        "key_env": "GROQ_API_KEY",
        "account_env": "",
        "cost_class": "free",
        "selection_basis": "Code-capable model with native tool calling and structured-output support.",
    },
    "negative_tester": {
        "provider": "groq",
        "model": "openai/gpt-oss-20b",
        "api_url": "https://api.groq.com/openai/v1/chat/completions",
        "key_env": "GROQ_API_KEY",
        "account_env": "",
        "cost_class": "free",
        "selection_basis": "Tool-capable reasoning model for generating and executing bounded adversarial test hypotheses.",
    },
    "integration_verifier": {
        "provider": "cloudflare",
        "model": "@cf/mistralai/mistral-small-3.1-24b-instruct",
        "api_url": "https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/v1/chat/completions",
        "key_env": "CLOUDFLARE_API_TOKEN",
        "account_env": "CLOUDFLARE_ACCOUNT_ID",
        "cost_class": "free_daily_allowance",
        "selection_basis": "Function-calling model with 128K context for evidence reconciliation and consistency verification.",
    },
}


def role_assignment(role: str) -> dict[str, str]:
    try:
        return ROLE_MODEL_ASSIGNMENTS[role].copy()
    except KeyError as exc:
        raise ValueError(f"no model assignment exists for role: {role}") from exc


def validate_registry() -> None:
    expected_roles = {
        "lead_builder",
        "specialist_builder",
        "architecture_reviewer",
        "code_reviewer",
        "negative_tester",
        "integration_verifier",
    }
    if set(ROLE_MODEL_ASSIGNMENTS) != expected_roles:
        raise ValueError("model registry must define exactly the six workforce roles")
    models = [entry["model"] for entry in ROLE_MODEL_ASSIGNMENTS.values()]
    if len(models) != len(set(models)):
        raise ValueError("each workforce role must have a distinct model assignment")
    for role, entry in ROLE_MODEL_ASSIGNMENTS.items():
        if entry["provider"] not in {"groq", "cloudflare"}:
            raise ValueError(f"unsupported provider for {role}")
        if entry["cost_class"] not in {"free", "free_daily_allowance"}:
            raise ValueError(f"non-free model registered for {role}")
        if entry["provider"] == "cloudflare" and not entry["account_env"]:
            raise ValueError(f"Cloudflare account identifier is missing for {role}")
        if entry["provider"] == "groq" and entry["account_env"]:
            raise ValueError(f"unexpected account identifier configured for {role}")


validate_registry()
