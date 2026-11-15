"""Shared HTTP identity and headers for every AURIONS provider request."""

USER_AGENT = "AURIONS-Workforce/1.0 (+https://github.com/methaneex-oss/AURIONS)"
OPENROUTER_REFERER = "https://github.com/methaneex-oss/AURIONS"


def authorization_headers(api_key: str) -> dict[str, str]:
    return {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
        "User-Agent": USER_AGENT,
    }


def chat_completion_headers(
    api_key: str,
    *,
    openrouter: bool = False,
    title: str = "AURIONS workforce",
) -> dict[str, str]:
    headers = authorization_headers(api_key)
    headers["Content-Type"] = "application/json"
    if openrouter:
        headers["HTTP-Referer"] = OPENROUTER_REFERER
        headers["X-Title"] = title
    return headers
