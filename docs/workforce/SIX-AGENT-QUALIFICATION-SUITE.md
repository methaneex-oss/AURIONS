# Six-agent qualification suite

The `six-agent-qualification.yml` workflow runs a read-only, bounded qualification
of all six pinned workforce roles.

Each role is checked independently for four capabilities (24 role checks total)
using one bounded two-request conversation: the first request must call the read-only
repository tool, and the second must use the returned tool data while producing
machine-checkable text and reasoning results. This workflow is deliberately primary-only:
it receives no OpenRouter credential and does not test or consume fallback quota. The
separate provider preflight is run by the supervised WF-03 workflow (and can also be
run through the provider-smoke workflow) before any workforce task is dispatched.

1. **Connectivity** — successful provider response and valid Chat Completions envelope.
2. **Text response** — non-empty assistant text containing a test marker.
3. **Reasoning/training simulation** — a deterministic arithmetic and classification
   exercise with a machine-checked JSON result. This does not train models, change
   weights, or establish persistent learning.
4. **Repository tool access** — the model must request `read_file(README.md)`;
   the test runtime reads the actual checked-out file and returns its contents as
   untrusted tool data together with a fresh, unpredictable challenge token. The
   model must reproduce both the first non-empty README line and that token in its
   structured response. A tool call without verified use of the returned content
   is recorded as PARTIAL, not PASS, and blocks a fully passing qualification result.

## Provider policy

- Pinned Groq and Cloudflare role assignments remain primary.
- OpenRouter is attempted after Groq HTTP 403 model-permission denial, or any primary
  HTTP 429, HTTP 5xx, or network failure. HTTP 401, Cloudflare HTTP 403 and malformed/
  invalid requests stop immediately. Every fallback result retains the primary failure.
- During a worker conversation, the first verified OpenRouter `:free` model is pinned
  for the remainder of that run; it cannot silently switch models mid-conversation.
- Every fallback-passed check records the primary provider failure; fallback success
  does not make the primary endpoint healthy.
- The only configured OpenRouter model is `openrouter/free`.
- The supervised WF-03 workflow runs a live provider preflight after primary-only
  qualification. It checks all six pinned primary endpoints and makes one explicit
  OpenRouter `openrouter/free` tool-call probe. A primary failure may cause one
  additional OpenRouter probe for that role.
- The fallback response must report a model identifier ending in `:free`; otherwise
  the fallback is rejected.
- OpenRouter free variants are rate-limited (currently 20 requests/minute and 50
  requests/day); failed attempts count toward the daily cap. The committed WF-03
  manifest currently permits 37 role model calls. Provider preflight can consume at
  most seven OpenRouter requests (one fallback per primary role probe plus one explicit
  free-router probe). The gate therefore requires 46 requests before preflight
  (37 + 7 + 2 safety) and at least 39 after preflight (37 + 2 safety). The orchestrated
  workflow checks the 39-request reserve again immediately before worker execution.
  These values are calculated from the committed manifest, not copied as fixed
  assumptions. Treat the quota as a hard ceiling and never purchase credits to raise it.
- In WF-03, once a worker falls back, it pins the actual returned `:free` model for
  the remainder of that worker conversation. Every retry uses the same pinned model.
- No paid model, paid credit, automatic paid upgrade, or non-free router is allowed.
- HTTP 401, Cloudflare HTTP 403 and request-contract errors do not trigger fallback; Groq model-permission HTTP 403 is the explicit exception.
- The workflow does not print provider response bodies or credentials.

## Required GitHub Actions secrets

The isolated primary-only qualification workflow requires:
- `GROQ_API_KEY`
- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ACCOUNT_ID`

The provider-smoke and supervised WF-03 workflows additionally require:
- `OPENROUTER_API_KEY` for the explicitly free-only fallback and live fallback preflight.

The primary-only workflow is available through **Actions → Six-agent qualification → Run workflow**.
It is manual-only and requires explicit confirmation of the run, Groq Free tier and
Cloudflare Workers Free plan. It does not run on pushes. The JSON report is uploaded
as a workflow artifact even when one or more checks fail. OpenRouter credentials and
free-only confirmation are required separately by the provider preflight and WF-03
orchestration workflows, not by this isolated qualification workflow.

A passing result establishes only these four bounded capabilities at the tested
commit and time. PARTIAL results count as non-passing and must be corrected or
retested; a successful tool invocation alone does not establish context use. It does not qualify the agents for unsupervised repository changes,
prove independent review competence, or constitute real training.
