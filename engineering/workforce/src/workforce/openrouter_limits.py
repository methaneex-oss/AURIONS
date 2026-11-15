"""Fail-closed checks for the OpenRouter free-model daily request allowance."""
from __future__ import annotations

from datetime import timezone
from email.utils import parsedate_to_datetime
import threading
import time
from typing import Any

import httpx

from workforce.provider_http import authorization_headers

OPENROUTER_KEY_INFO_URL = "https://openrouter.ai/api/v1/key"

# OpenRouter free variants are limited to 20 requests per minute across the
# account. A process-wide gate spaces requests even when multiple workers share
# one orchestrator process.
FREE_MODEL_MIN_REQUEST_INTERVAL_SECONDS = 3.05
_free_model_request_lock = threading.Lock()
_last_free_model_request_at = 0.0


def parse_retry_after_seconds(value: str | None) -> float:
    """Parse Retry-After as seconds or an HTTP date; invalid values mean no hint."""
    if not isinstance(value, str) or not value.strip():
        return 0.0
    try:
        return max(0.0, float(value.strip()))
    except ValueError:
        try:
            retry_at = parsedate_to_datetime(value)
            if retry_at.tzinfo is None:
                retry_at = retry_at.replace(tzinfo=timezone.utc)
            return max(0.0, retry_at.timestamp() - time.time())
        except (TypeError, ValueError, OverflowError):
            return 0.0


def free_model_request_delay(
    last_request_at: float,
    now: float,
    retry_after_seconds: float = 0.0,
) -> float:
    """Return the greater of account-wide pacing and the provider retry hint."""
    spacing = max(0.0, FREE_MODEL_MIN_REQUEST_INTERVAL_SECONDS - max(0.0, now - last_request_at))
    return max(spacing, max(0.0, retry_after_seconds))


def wait_for_free_model_request_slot(
    retry_after: str | None = None,
    *,
    remaining_seconds: float | None = None,
) -> float:
    """Pace free-router requests and honor Retry-After without exceeding role deadlines."""
    global _last_free_model_request_at
    retry_delay = parse_retry_after_seconds(retry_after)
    with _free_model_request_lock:
        now = time.monotonic()
        delay = free_model_request_delay(_last_free_model_request_at, now, retry_delay)
        if remaining_seconds is not None:
            if remaining_seconds <= 0 or delay >= remaining_seconds:
                raise RuntimeError(
                    f"OpenRouter retry/pacing delay ({delay:.2f}s) exceeds remaining role time"
                )
        if delay:
            time.sleep(delay)
        _last_free_model_request_at = time.monotonic()
        return delay


def get_free_model_quota(api_key: str) -> dict[str, int]:
    if not isinstance(api_key, str) or not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is missing for free-quota verification")
    try:
        response = httpx.get(
            OPENROUTER_KEY_INFO_URL,
            headers=authorization_headers(api_key),
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
