# Six-agent qualification suite

The `six-agent-qualification.yml` workflow runs a read-only, bounded qualification
of all six pinned workforce roles.

Each role is checked independently for four capabilities (24 role checks total).
A separate OpenRouter free-router smoke check verifies the fallback credential,
free-model identity, and function-call support.

1. **Connectivity** — successful provider response and valid Chat Completions envelope.
2. **Text response** — non-empty assistant text containing a test marker.
3. **Reasoning/training simulation** — a deterministic arithmetic and classification
   exercise with a machine-checked JSON result. This does not train models, change
   weights, or establish persistent learning.
4. **Repository tool access** — the model must request `read_file(README.md)`;
   the test runtime reads the actual checked-out file and returns its contents as
   untrusted tool data; the model must then identify the first non-empty line.
   A tool call without correct use of the returned content is recorded as PARTIAL,
   not PASS, and blocks a fully passing qualification result.

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
- A separate fallback smoke check verifies OpenRouter connectivity and required
  function calling.
- The fallback response must report a model identifier ending in `:free`; otherwise
  the fallback is rejected.
- OpenRouter free variants are rate-limited (currently 20 requests/minute and 50
  requests/day without a qualifying credit purchase); failed attempts count toward
  the daily cap. Treat the quota as a hard ceiling and never purchase credits to raise it.
- No paid model, paid credit, automatic paid upgrade, or non-free router is allowed.
- HTTP 401, Cloudflare HTTP 403 and request-contract errors do not trigger fallback; Groq model-permission HTTP 403 is the explicit exception.
- The workflow does not print provider response bodies or credentials.

## Required GitHub Actions secrets

- `GROQ_API_KEY`
- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ACCOUNT_ID`
- `OPENROUTER_API_KEY`

The workflow is available through **Actions → Six-agent qualification → Run workflow**.
It is manual-only and requires explicit confirmation of the run, Groq Free tier,
Cloudflare Workers Free plan, and OpenRouter free-only routing. It does not run on
pushes. The JSON report is uploaded as a workflow artifact even when one or more
checks fail.

A passing result establishes only these four bounded capabilities at the tested
commit and time. PARTIAL results count as non-passing and must be corrected or
retested; a successful tool invocation alone does not establish context use. It does not qualify the agents for unsupervised repository changes,
prove independent review competence, or constitute real training.
