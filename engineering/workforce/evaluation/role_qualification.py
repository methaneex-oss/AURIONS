"""One-shot, role-specific model screening. No repository tools or write access."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import httpx

CASES = {
    "lead_builder": """A Python task-state service accepts QUEUED->RUNNING and RUNNING->ACCEPTED transitions. The second transition currently trusts an actor string supplied in the request body. Director acceptance must require a separate approval credential and durable decision reference. Give a minimal implementation plan: invariants, smallest safe change, tests, and what you would refuse to change. Do not write generic advice.""",
    "specialist_builder": """A lease system issues expiring worker leases; checkpoint writes must be accepted only from the current live lease holder. Design six concrete unit tests covering expiry, replay, wrong worker, renewal race, duplicate checkpoint, and valid write. For each state exact setup, action, and expected result. Avoid tests that merely assert implementation details.""",
    "architecture_reviewer": """A project constitution says runtime implementation is not authorized. A planning document proposes a prototype runtime in src/aurions to validate an architecture assumption. Assess the conflict. Separate what can proceed, what is blocked, what decision is reserved to the Director, and the evidence needed. Do not treat a document proposal as authorization.""",
    "code_reviewer": """Review this path check: candidate=(root / user_path).resolve(); if root not in candidate.parents: deny; then write candidate. Identify at least three correctness/security issues or explain precisely why fewer exist. Consider root itself, symlinks, platform/path edge cases, and race conditions. Give concrete mitigations and tests.""",
    "negative_tester": """A task API has CLAIMED->RUNNING, leases expire after 60 seconds, and a worker may checkpoint progress. Construct an adversarial test sequence that tries to make an expired worker overwrite a newer worker's checkpoint. Include timing/order, expected safe behavior, and the exact invariant being falsified. Include at least one retry or duplicate-request case.""",
    "integration_verifier": """Evidence manifest says base_sha=A, builder_candidate_sha=B, architecture_review_sha=B, code_review_sha=C, test_sha=B, integrated_sha=B. All SHAs are distinct placeholders except where repeated. Determine whether the evidence is coherent, identify every mismatch, state what must be rerun, and whether the candidate can be presented for Director acceptance. Never infer acceptance.""",
}

ROLE_CRITERIA = {
    "lead_builder": "Scope discipline, minimal implementation reasoning, explicit invariants, actionable tests, no unauthorized scope.",
    "specialist_builder": "Test specificity, meaningful expected outcomes, edge coverage, independence from implementation details.",
    "architecture_reviewer": "Authority boundary reasoning, contradiction detection, clear separation of proposal and authorization.",
    "code_reviewer": "Technical accuracy, concrete exploit/edge cases, prioritized mitigations, evidence discipline.",
    "negative_tester": "Reproducible adversarial sequence, concurrency/race reasoning, falsifiable invariant.",
    "integration_verifier": "Exact-SHA reconciliation, correct rerun requirements, no false acceptance.",
}


def main() -> int:
    role = os.environ["ROLE"]
    model = os.environ.get("OPENROUTER_MODEL", "nvidia/nemotron-3.5-lightning:free")
    if role not in CASES:
        raise SystemExit(f"unknown role: {role}")
    if not model.endswith(":free"):
        raise SystemExit("free-only policy: model ID must end in :free")
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise SystemExit("OPENROUTER_API_KEY missing")
    system = (
        "You are being screened for one engineering role. This is an independent practical test, "
        "not a discussion of other agents or reviews. Be precise, technical, and concise. "
        "Do not claim to have executed code or tests. Do not invent evidence. "
        "Return plain text with these headings: ANSWER, FAILURE MODES, EVIDENCE NEEDED, CONFIDENCE."
    )
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system + "\nRole: " + role + "\nAssessment criteria: " + ROLE_CRITERIA[role]},
            {"role": "user", "content": CASES[role]},
        ],
        "max_tokens": 1400,
        "reasoning": {"effort": "low"},
        "temperature": 0,
    }
    response = httpx.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/methaneex-oss/AURIONS",
            "X-Title": "AURIONS role qualification screening",
        },
        json=payload,
        timeout=90,
    )
    if response.status_code != 200:
        # No automatic retry: failed free requests may still consume daily quota.
        raise SystemExit(f"provider request failed: HTTP {response.status_code}; no retry attempted")
    data = response.json()
    message = data["choices"][0]["message"]
    content = message.get("content")
    finish_reason = data["choices"][0].get("finish_reason")
    result = {
        "role": role,
        "model": data.get("model", model),
        "screening_only": True,
        "calls": 1,
        "usage": data.get("usage", {}),
        "response": content,
        "finish_reason": finish_reason,
        "tool_use_tested": False,
        "qualification_status": "PENDING_INDEPENDENT_HUMAN_SCORING",
    }
    output = Path(os.environ.get("OUTPUT_FILE", f"{role}-screening.json"))
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    if not isinstance(content, str) or not content.strip():
        raise SystemExit(f"screening produced no visible answer; finish_reason={finish_reason}; usage={data.get('usage', {})}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
