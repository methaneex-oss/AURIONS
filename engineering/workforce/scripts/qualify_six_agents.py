"""Read-only qualification of the six pinned AURIONS workforce roles.

Checks connectivity, plain-text generation, bounded structured reasoning, and a
real read-only repository tool call. OpenRouter is a free-only fallback for
transient primary-provider failures; it is never used for auth/contract errors.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from workforce.model_registry import ROLE_MODEL_ASSIGNMENTS

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_MODEL = "openrouter/free"
TIMEOUT_SECONDS = 45
MAX_RESPONSE_BYTES = 1_000_000

READ_FILE_TOOL = [{
    "type": "function",
    "function": {
        "name": "read_file",
        "description": "Read a bounded UTF-8 text file from the checked-out repository. This qualification tool is read-only and only permits README.md.",
        "parameters": {
            "type": "object",
            "properties": {"path": {"type": "string"}},
            "required": ["path"],
            "additionalProperties": False,
        },
    },
}]


class ProviderFailure(Exception):
    def __init__(self, message: str, retryable: bool = False):
        super().__init__(message)
        self.retryable = retryable


def _post(url: str, token: str, payload: dict[str, Any], openrouter: bool = False) -> dict[str, Any]:
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    if openrouter:
        headers["HTTP-Referer"] = "https://github.com/methaneex-oss/AURIONS"
        headers["X-Title"] = "AURIONS free-only agent qualification"
    request = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            raw = response.read(MAX_RESPONSE_BYTES + 1)
            if len(raw) > MAX_RESPONSE_BYTES:
                raise ProviderFailure("provider response exceeded 1 MB")
            data = json.loads(raw.decode("utf-8"))
    except urllib.error.HTTPError as exc:
        # Do not print raw provider bodies: they can contain reflected credentials.
        retryable = exc.code == 429 or exc.code >= 500
        raise ProviderFailure(f"HTTP {exc.code}", retryable=retryable) from None
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise ProviderFailure(f"network {type(exc).__name__}", retryable=True) from None
    except (UnicodeDecodeError, json.JSONDecodeError):
        raise ProviderFailure("provider returned invalid JSON/UTF-8") from None
    if not isinstance(data, dict):
        raise ProviderFailure("provider response was not a JSON object")
    return data


def _call(role: str, payload: dict[str, Any]) -> tuple[dict[str, Any], str, str]:
    profile = ROLE_MODEL_ASSIGNMENTS[role]
    primary_key = os.environ.get(profile["key_env"], "")
    if not primary_key:
        raise ProviderFailure(f"missing {profile['key_env']}")
    url = profile["api_url"]
    if profile["provider"] == "cloudflare":
        account = os.environ.get(profile["account_env"], "")
        if not account:
            raise ProviderFailure(f"missing {profile['account_env']}")
        url = url.format(account_id=account)
    primary_payload = dict(payload)
    primary_payload["model"] = profile["model"]
    primary_payload[profile["completion_tokens_parameter"]] = 256
    if profile["provider"] == "groq" and profile["model"] in {"openai/gpt-oss-20b", "openai/gpt-oss-120b"}:
        primary_payload["parallel_tool_calls"] = False
    try:
        data = _post(url, primary_key, primary_payload)
        returned_model = data.get("model", profile["model"])
        if returned_model != profile["model"]:
            raise ProviderFailure(f"primary returned unexpected model identity: {str(returned_model)[:120]}")
        return data, profile["provider"], profile["model"]
    except ProviderFailure as exc:
        if not exc.retryable:
            raise
        fallback_key = os.environ.get("OPENROUTER_API_KEY", "")
        if not fallback_key:
            raise ProviderFailure(f"primary {exc}; OpenRouter fallback key unavailable") from None
        fallback_payload = dict(payload)
        fallback_payload["model"] = OPENROUTER_MODEL
        fallback_payload["max_tokens"] = 256
        fallback_data = _post(OPENROUTER_URL, fallback_key, fallback_payload, openrouter=True)
        actual_model = fallback_data.get("model")
        if not isinstance(actual_model, str) or not actual_model.endswith(":free"):
            raise ProviderFailure("OpenRouter fallback did not identify a verified :free model")
        return fallback_data, "openrouter-free-fallback", actual_model


def _choice(data: dict[str, Any]) -> dict[str, Any]:
    choices = data.get("choices")
    if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
        raise ProviderFailure("response omitted choices[0]")
    message = choices[0].get("message")
    if not isinstance(message, dict):
        raise ProviderFailure("response omitted assistant message")
    return message


def _record(results: list[dict[str, Any]], role: str, check: str, fn) -> None:
    try:
        detail = fn()
        results.append({"role": role, "check": check, "status": "PASS", **detail})
    except Exception as exc:
        results.append({
            "role": role, "check": check, "status": "FAIL",
            "error": f"{type(exc).__name__}: {str(exc)[:240]}",
        })


def qualify_role(role: str, repo_root: Path, results: list[dict[str, Any]]) -> None:
    def connectivity():
        data, provider, model = _call(role, {
            "messages": [{"role": "user", "content": "Reply with exactly: AURIONS_CONNECTIVITY_OK"}],
            "temperature": 0,
        })
        _choice(data)
        return {"provider": provider, "model": model, "evidence": "HTTP success and valid chat-completions envelope"}

    def text_response():
        data, provider, model = _call(role, {
            "messages": [{"role": "user", "content": "Write one short sentence confirming you can generate text. Include the exact token TEXT_RESPONSE_OK."}],
            "temperature": 0,
        })
        content = _choice(data).get("content")
        if not isinstance(content, str) or not content.strip() or "TEXT_RESPONSE_OK" not in content:
            raise ProviderFailure("assistant returned empty text or omitted TEXT_RESPONSE_OK")
        return {"provider": provider, "model": model, "evidence": content.strip()[:240]}

    def reasoning_simulation():
        data, provider, model = _call(role, {
            "messages": [{
                "role": "user",
                "content": (
                    "Complete this bounded reasoning exercise. Compute (19 * 7) - 23, "
                    "then classify the result as even or odd. Return ONLY JSON with keys "
                    "value, parity, and method. Expected value is 110 and parity is even. "
                    "Do not reveal hidden chain-of-thought; a short method label is sufficient."
                ),
            }],
            "temperature": 0,
        })
        content = _choice(data).get("content")
        if not isinstance(content, str) or not content.strip():
            raise ProviderFailure("assistant returned no reasoning-exercise text")
        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`").replace("json", "", 1).strip()
        try:
            answer = json.loads(cleaned)
        except json.JSONDecodeError:
            raise ProviderFailure("reasoning exercise did not return valid JSON") from None
        if answer.get("value") != 110 or answer.get("parity") != "even":
            raise ProviderFailure("reasoning exercise produced an incorrect result")
        return {"provider": provider, "model": model, "evidence": "structured arithmetic result correct; simulation only"}

    def repository_access():
        data, provider, model = _call(role, {
            "messages": [{
                "role": "user",
                "content": (
                    "Use the read_file tool exactly once with path README.md. "
                    "Do not guess its contents and do not answer before calling the tool."
                ),
            }],
            "tools": READ_FILE_TOOL,
            "tool_choice": "required",
            "temperature": 0,
        })
        message = _choice(data)
        calls = message.get("tool_calls") or []
        if not calls:
            raise ProviderFailure("assistant did not request the required read_file tool")
        call = calls[0]
        function = call.get("function", {})
        if function.get("name") != "read_file":
            raise ProviderFailure("assistant requested the wrong repository tool")
        try:
            args = json.loads(function.get("arguments") or "{}")
        except json.JSONDecodeError:
            raise ProviderFailure("assistant returned invalid tool arguments") from None
        if args.get("path") != "README.md":
            raise ProviderFailure("assistant requested an unexpected repository path")
        target = (repo_root / "README.md").resolve()
        if target != repo_root.resolve() / "README.md" or not target.is_file():
            raise ProviderFailure("README.md is unavailable in the checked-out repository")
        content = target.read_text(encoding="utf-8")
        tool_result = content[:1200]
        if not tool_result.strip():
            raise ProviderFailure("repository tool returned an empty README")
        return {"provider": provider, "model": model, "evidence": f"read-only README.md access; {len(content)} characters available"}

    _record(results, role, "connectivity", connectivity)
    _record(results, role, "text_response", text_response)
    _record(results, role, "reasoning_training_simulation", reasoning_simulation)
    _record(results, role, "repository_tool_access", repository_access)


def main() -> int:
    repo_root = Path(os.environ.get("GITHUB_WORKSPACE", Path.cwd())).resolve()
    results: list[dict[str, Any]] = []
    for role in ROLE_MODEL_ASSIGNMENTS:
        qualify_role(role, repo_root, results)
    summary = {
        "suite": "AURIONS six-agent read-only qualification",
        "training": "simulation only; no model weights or persistent learning changed",
        "fallback_policy": "OpenRouter openrouter/free only after primary transient failure; require returned :free model identity",
        "checks_per_role": ["connectivity", "text_response", "reasoning_training_simulation", "repository_tool_access"],
        "results": results,
        "passed": sum(item["status"] == "PASS" for item in results),
        "failed": sum(item["status"] == "FAIL" for item in results),
        "total": len(results),
    }
    output = json.dumps(summary, indent=2, ensure_ascii=False)
    print(output)
    report_path = Path(os.environ.get("QUALIFICATION_REPORT", "agent-qualification-report.json"))
    report_path.write_text(output + "\n", encoding="utf-8")
    return 0 if summary["failed"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
