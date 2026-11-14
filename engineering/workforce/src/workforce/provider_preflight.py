"""Bounded live qualification of every pinned workforce model before agent execution.

This performs one small inference per role. It verifies endpoint acceptance, tool-call
compatibility, returned model identity, and usage accounting required by the runner.
"""
from __future__ import annotations

import json
import os
import sys

import httpx

from workforce.agents.runner import TOOLS
from workforce.model_registry import ROLE_MODEL_ASSIGNMENTS


def main() -> int:
    groq_key = os.environ.get("GROQ_API_KEY", "")
    cf_token = os.environ.get("CLOUDFLARE_API_TOKEN", "")
    cf_account = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "")
    missing = [
        name for name, value in (
            ("GROQ_API_KEY", groq_key),
            ("CLOUDFLARE_API_TOKEN", cf_token),
            ("CLOUDFLARE_ACCOUNT_ID", cf_account),
        ) if not value
    ]
    if missing:
        print("PREFLIGHT BLOCKED: missing required credentials: " + ", ".join(missing))
        return 2

    failures: list[str] = []
    for role, profile in ROLE_MODEL_ASSIGNMENTS.items():
        provider = profile["provider"]
        model = profile["model"]
        if provider == "groq":
            url = profile["api_url"]
            token = groq_key
            output_key = "max_completion_tokens"
        else:
            url = profile["api_url"].format(account_id=cf_account)
            token = cf_token
            output_key = "max_tokens"

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
                headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
                json=payload,
                timeout=45,
            )
        except httpx.HTTPError as exc:
            print(f"FAIL {role}: {type(exc).__name__}: {str(exc)[:240]}")
            failures.append(role)
            continue

        if response.status_code >= 400:
            try:
                body = response.json()
            except ValueError:
                body = {}
            error = body.get("error", body) if isinstance(body, dict) else {}
            safe = {
                key: error[key]
                for key in ("message", "type", "code", "param")
                if isinstance(error, dict) and isinstance(error.get(key), (str, int, float, bool))
            }
            print(f"FAIL {role}: HTTP {response.status_code} " +
                  (json.dumps(safe, ensure_ascii=True)[:600] if safe else "provider returned no structured error"))
            failures.append(role)
            continue

        try:
            data = response.json()
            choices = data.get("choices") or []
            message = choices[0].get("message", {}) if choices else {}
            calls = message.get("tool_calls") or []
            usage = data.get("usage") or {}
            total = usage.get("total_tokens")
            returned_model = data.get("model", model)
            if returned_model != model:
                raise ValueError(f"provider returned unexpected model identity {returned_model!r}")
            if not calls:
                raise ValueError("model did not produce the required function call")
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

    print(f"PROVIDER PREFLIGHT: {len(ROLE_MODEL_ASSIGNMENTS) - len(failures)}/{len(ROLE_MODEL_ASSIGNMENTS)} passed.")
    if failures:
        print("BLOCKED ROLES: " + ", ".join(failures))
        return 1
    print("All six pinned model endpoints passed. Orchestrated agent execution may proceed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
