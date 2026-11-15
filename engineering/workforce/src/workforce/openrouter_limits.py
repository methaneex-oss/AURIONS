"""Fail-closed checks for the OpenRouter free-model daily request allowance."""
from __future__ import annotations

from typing import Any

import httpx

OPENROUTER_KEY_INFO_URL = "https://openrouter.ai/api/v1/key"


def get_free_model_quota(api_key: str) -> dict[str, int]:
    if not isinstance(api_key, str) or not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is missing for free-quota verification")
    try:
        response = httpx.get(
            OPENROUTER_KEY_INFO_URL,
            headers={"Authorization": f"Bearer {api_key}", "Accept": "application/json"},
            timeout=15,
        )
    except httpx.HTTPError as exc:
        raise RuntimeError(f"OpenRouter free-quota lookup failed ({type(exc).__name__})") from None
    if response.status_code >= 400:
        raise RuntimeError(f"OpenRouter free-quota lookup rejected the key (HTTP {response.status_code})")
    try:
        body: Any = response.json()
    except ValueError:
        raise RuntimeError("OpenRouter free-quota lookup returned invalid JSON") from None
    data = body.get("data") if isinstance(body, dict) else None
    quota = data.get("free_model_daily_requests") if isinstance(data, dict) else None
    if not isinstance(quota, dict):
        raise RuntimeError("OpenRouter did not return free_model_daily_requests; refusing to assume quota")
    values = {key: quota.get(key) for key in ("used", "limit", "remaining")}
    if any(not isinstance(value, int) or isinstance(value, bool) or value < 0 for value in values.values()):
        raise RuntimeError("OpenRouter returned an invalid free-model daily quota")
    if values["remaining"] > values["limit"] or values["used"] + values["remaining"] > values["limit"]:
        raise RuntimeError("OpenRouter free-model daily quota counters are inconsistent")
    limit_remaining = data.get("limit_remaining")
    if isinstance(limit_remaining, (int, float)) and limit_remaining < 0:
        raise RuntimeError("OpenRouter account has a negative credit balance; free-model requests may be blocked")
    return values


def require_free_model_quota(api_key: str, minimum_remaining: int, purpose: str) -> dict[str, int]:
    if not isinstance(minimum_remaining, int) or isinstance(minimum_remaining, bool) or minimum_remaining < 0:
        raise ValueError("minimum_remaining must be a non-negative integer")
    quota = get_free_model_quota(api_key)
    if quota["remaining"] < minimum_remaining:
        raise RuntimeError(
            f"OpenRouter free-model quota is insufficient for {purpose}: "
            f"{quota['remaining']} remaining, {minimum_remaining} required; no paid fallback is permitted"
        )
    return quota
