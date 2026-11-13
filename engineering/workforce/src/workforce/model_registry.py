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
        "cost_class": "free",
        "selection_basis": "Large reasoning model with coding and tool-use support.",
    },
    "specialist_builder": {
        "provider": "openrouter",
        "model": "cohere/north-mini-code:free",
        "api_url": "https://openrouter.ai/api/v1/chat/completions",
        "key_env": "OPENROUTER_API_KEY",
        "cost_class": "free",
        "selection_basis": "Code-specialized agentic model with tool use and long context.",
    },
    "architecture_reviewer": {
        "provider": "openrouter",
        "model": "nvidia/nemotron-3-ultra-550b-a55b:free",
        "api_url": "https://openrouter.ai/api/v1/chat/completions",
        "key_env": "OPENROUTER_API_KEY",
        "cost_class": "free",
        "selection_basis": "Long-context reasoning model suited to architecture and multi-step analysis.",
    },
    "code_reviewer": {
        "provider": "groq",
        "model": "qwen/qwen3.8-27b",
        "api_url": "https://api.groq.com/openai/v1/chat/completions",
        "key_env": "GROQ_API_KEY",
        "cost_class": "free",
        "selection_basis": "Code-capable model with native tool calling and structured-output support.",
    },
    "negative_tester": {
        "provider": "openrouter",
        "model": "nvidia/nemotron-3.5-super-vl:free",
        "api_url": "https://openrouter.ai/api/v1/chat/completions",
        "key_env": "OPENROUTER_API_KEY",
        "cost_class": "free",
        "selection_basis": "Reasoning-capable long-context agent model with tool use for adversarial test exploration.",
    },
    "integration_verifier": {
        "provider": "groq",
        "model": "openai/gpt-oss-20b",
        "api_url": "https://api.groq.com/openai/v1/chat/completions",
        "key_env": "GROQ_API_KEY",
        "cost_class": "free",
        "selection_basis": "Lower-latency structured/tool-using model for evidence reconciliation and consistency checks.",
    },
}


def role_assignment(role: str) -> dict[str, str]:
    try:
        return ROLE_MODEL_ASSIGNMENTS[role].copy()
    except KeyError as exc:
        raise ValueError(f"no model assignment exists for role: {role}") from exc


def validate_registry() -> None:
    roles = set(ROLE_MODEL_ASSIGNMENTS)
    expected_roles = {
        "lead_builder",
        "specialist_builder",
        "architecture_reviewer",
        "code_reviewer",
        "negative_tester",
        "integration_verifier",
    }
    if roles != expected_roles:
        raise ValueError("model registry must define exactly the six workforce roles")
    models = [entry["model"] for entry in ROLE_MODEL_ASSIGNMENTS.values()]
    if len(models) != len(set(models)):
        raise ValueError("each workforce role must have a distinct model assignment")
    for role, entry in ROLE_MODEL_ASSIGNMENTS.items():
        if entry["provider"] not in {"groq", "openrouter"}:
            raise ValueError(f"unsupported provider for {role}")
        if entry["cost_class"] != "free":
            raise ValueError(f"non-free model registered for {role}")
        if entry["provider"] == "openrouter" and not entry["model"].endswith(":free"):
            raise ValueError(f"OpenRouter model for {role} is not pinned to a free variant")


validate_registry()
