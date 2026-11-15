"""Bounded live qualification of every pinned workforce model before agent execution.

This performs one small inference per role. It verifies endpoint acceptance, tool-call
compatibility, returned model identity, and usage accounting required by the runner.
"""
from __future__ import annotations

import json
import os
import sys

import httpx

from workforce.agents.runner import TOOLS, is_groq_model_permission_block, provider_error_detail
from workforce.model_registry import ROLE_MODEL_ASSIGNMENTS
from workforce.openrouter_limits import require_free_model_quota
from workforce.provider_http import chat_completion_headers


def _verify_free_fallback(payload: dict, openrouter_key: str) -> tuple[str, int]:
    fallback_payload = dict(payload)
    fallback_payload["model"] = "openrouter/free"
    if "max_completion_tokens" in fallback_payload:
        fallback_payload["max_tokens"] = fallback_payload.pop("max_completion_tokens")
    response = httpx.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers=chat_completion_headers(
            openrouter_key,
            openrouter=True,
            title="AURIONS free-only workforce preflight",
        ),
        json=fallback_payload,
        timeout=45,
    )
    if response.status_code >= 400:
        raise ValueError(
            f"OpenRouter fallback HTTP {response.status_code}: "
            + provider_error_detail(response, (openrouter_key,))
        )
    data = response.json()
    actual_model = data.get("model") if isinstance(data, dict) else None
    if not isinstance(actual_model, str) or not actual_model.endswith(":free"):
        raise ValueError("fallback did not identify a verified :free model")
    choices = data.get("choices") or []
    message = choices[0].get("message", {}) if choices else {}
    calls = message.get("tool_calls") or []
    usage = data.get("usage") or {}
    total = usage.get("total_tokens")
    if len(calls) != 1 or calls[0].get("function", {}).get("name") != "read_file":
        raise ValueError("fallback did not return exactly one required read_file tool call")
    args = json.loads(calls[0]["function"].get("arguments") or "{}")
    if args.get("path") != "README.md":
        raise ValueError("fallback returned invalid read_file arguments")
    if not isinstance(total, int) or isinstance(total, bool) or total <= 0:
        raise ValueError("fallback omitted valid usage.total_tokens")
    return actual_model, total


def main() -> int:
    groq_key = os.environ.get("GROQ_API_KEY", "")
    cf_token = os.environ.get("CLOUDFLARE_API_TOKEN", "")
    cf_account = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "")
    openrouter_key = os.environ.get("OPENROUTER_API_KEY", "")
    missing = [
        name for name, value in (
            ("GROQ_API_KEY", groq_key),
            ("CLOUDFLARE_API_TOKEN", cf_token),
            ("CLOUDFLARE_ACCOUNT_ID", cf_account),
            ("OPENROUTER_API_KEY", openrouter_key),
        ) if not value
    ]
    if missing:
        print("PREFLIGHT BLOCKED: missing required credentials: " + ", ".join(missing))
        return 2

    try:
        quota = require_free_model_quota(
            openrouter_key,
            minimum_remaining=27,
            purpose="provider preflight plus the 20-request WF-03 fallback reserve",
        )
        print(
            "OpenRouter free quota verified before provider preflight: "
            f"{quota['remaining']}/{quota['limit']} daily requests remain."
        )
    except Exception as exc:
        print(f"PREFLIGHT BLOCKED: {type(exc).__name__}: {str(exc)[:300]}")
        return 2

    failures: list[str] = []
    for role, profile in ROLE_MODEL_ASSIGNMENTS.items():
        provider = profile["provider"]
        model = profile["model"]
        if provider == "groq":
            url = profile["api_url"]
            token = groq_key
        else:
            url = profile["api_url"].format(account_id=cf_account)
            token = cf_token
        # The registry is the source of truth: Cloudflare models do not all
        # share one completion-limit parameter (Gemma/GLM use
        # max_completion_tokens; Mistral Small 3.1 uses max_tokens).
        output_key = profile["completion_tokens_parameter"]

        payload = {
            "model": model,
            "messages": [{
                "role": "user",
                "content": "Call the read_file function exactly once with path README.md. Do not answer without calling the function.",
            }],
            "tools": TOOLS,
            "tool_choice": "required",
            "temperature": 0.2,
            output_key: 384,
        }
        if provider == "groq" and model in {"openai/gpt-oss-20b", "openai/gpt-oss-120b"}:
            payload["parallel_tool_calls"] = False

        try:
            response = httpx.post(
                url,
                headers=chat_completion_headers(token),
                json=payload,
                timeout=45,
            )
        except httpx.HTTPError as exc:
            try:
                fallback_model, fallback_tokens = _verify_free_fallback(payload, openrouter_key)
                print(
                    f"PASS_WITH_FREE_FALLBACK {role}: primary network failure "
                    f"({type(exc).__name__}); OpenRouter/{fallback_model}; "
                    f"function call valid; usage={fallback_tokens} tokens"
                )
            except Exception as fallback_exc:
                print(
                    f"FAIL {role}: primary network failure ({type(exc).__name__}); "
                    f"free fallback failed: {type(fallback_exc).__name__}: {str(fallback_exc)[:300]}"
                )
                failures.append(role)
            continue

        fallback_eligible = (
            response.status_code == 429
            or response.status_code >= 500
            or (provider == "groq" and is_groq_model_permission_block(response))
        )
        if fallback_eligible:
            detail = provider_error_detail(response, (token,))
            failure_kind = (
                "Groq model-permission block" if provider == "groq" and response.status_code == 403
                else f"HTTP {response.status_code}"
            )
            try:
                fallback_model, fallback_tokens = _verify_free_fallback(payload, openrouter_key)
                print(
                    f"PASS_WITH_FREE_FALLBACK {role}: primary {failure_kind}; "
                    f"OpenRouter/{fallback_model}; function call valid; usage={fallback_tokens} tokens; "
                    f"primary diagnostic={detail}"
                )
            except Exception as fallback_exc:
                print(
                    f"FAIL {role}: primary {failure_kind}: {detail}; free fallback failed: "
                    f"{type(fallback_exc).__name__}: {str(fallback_exc)[:300]}"
                )
                failures.append(role)
            continue
        if response.status_code >= 400:
            detail = provider_error_detail(response, (token,))
            print(f"FAIL {role}: HTTP {response.status_code}: {detail}")
            failures.append(role)
            continue

        try:
            data = response.json()
            choices = data.get("choices") or []
            message = choices[0].get("message", {}) if choices else {}
            calls = message.get("tool_calls") or []
            usage = data.get("usage") or {}
            total = usage.get("total_tokens")
            returned_model = data.get("model")
            if returned_model != model:
                raise ValueError(f"provider returned unexpected model identity {returned_model!r}")
            if len(calls) != 1:
                raise ValueError("model did not produce exactly one required function call")
            if not isinstance(total, int) or isinstance(total, bool) or total <= 0:
                raise ValueError("provider omitted valid usage.total_tokens required by durable budget accounting")
            call = calls[0]
            if call.get("function", {}).get("name") != "read_file":
                raise ValueError("model returned the wrong function name")
            args = json.loads(call.get("function", {}).get("arguments") or "{}")
            if args.get("path") != "README.md":
                raise ValueError("model returned invalid read_file arguments")
        except (ValueError, TypeError, KeyError, IndexError, json.JSONDecodeError) as exc:
            print(f"FAIL {role}: response contract: {str(exc)[:400]}")
            failures.append(role)
            continue

        print(f"PASS {role}: {provider}/{model}; function call valid; usage={total} tokens")

    # Verify the production fallback independently, including free-model identity,
    # required tool calling and usage accounting. Never accept a paid model response.
    fallback_payload = {
        "model": "openrouter/free",
        "messages": [{
            "role": "user",
            "content": "Call the read_file function exactly once with path README.md. Do not answer without calling the function.",
        }],
        "tools": TOOLS,
        "tool_choice": "required",
        "temperature": 0.2,
        "max_tokens": 384,
    }
    try:
        response = httpx.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=chat_completion_headers(
                openrouter_key,
                openrouter=True,
                title="AURIONS free-only workforce preflight",
            ),
            json=fallback_payload,
            timeout=45,
        )
        if response.status_code >= 400:
            detail = provider_error_detail(response, (openrouter_key,))
            raise ValueError(f"HTTP {response.status_code}: {detail}")
        data = response.json()
        actual_model = data.get("model")
        if not isinstance(actual_model, str) or not actual_model.endswith(":free"):
            raise ValueError("router did not identify a verified :free model")
        choices = data.get("choices") or []
        message = choices[0].get("message", {}) if choices else {}
        calls = message.get("tool_calls") or []
        usage = data.get("usage") or {}
        total = usage.get("total_tokens")
        if not isinstance(total, int) or isinstance(total, bool) or total <= 0:
            raise ValueError("router omitted valid usage.total_tokens")
        if len(calls) != 1 or calls[0].get("function", {}).get("name") != "read_file":
            raise ValueError("router did not return exactly one required read_file function call")
        args = json.loads(calls[0]["function"].get("arguments") or "{}")
        if args.get("path") != "README.md":
            raise ValueError("router returned invalid read_file arguments")
        print(f"PASS openrouter_free_fallback: {actual_model}; function call valid; usage={total} tokens")
    except Exception as exc:
        print(f"FAIL openrouter_free_fallback: {type(exc).__name__}: {str(exc)[:400]}")
        failures.append("openrouter_free_fallback")

    print(f"PROVIDER PREFLIGHT: {len(ROLE_MODEL_ASSIGNMENTS) + 1 - len(failures)}/{len(ROLE_MODEL_ASSIGNMENTS) + 1} checks passed.")
    if failures:
        print("BLOCKED ROLES: " + ", ".join(failures))
        return 1
    print("All six roles have a verified primary or OpenRouter free-only fallback route. Orchestrated agent execution may proceed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
