# Six-agent qualification suite

The `six-agent-qualification.yml` workflow runs a read-only, bounded qualification
of all six pinned workforce roles.

Each role is checked independently for:

1. **Connectivity** — successful provider response and valid Chat Completions envelope.
2. **Text response** — non-empty assistant text containing a test marker.
3. **Reasoning/training simulation** — a deterministic arithmetic and classification
   exercise with a machine-checked JSON result. This does not train models, change
   weights, or establish persistent learning.
4. **Repository tool access** — the model must request `read_file(README.md)`;
   the test runtime reads the actual checked-out file and returns its contents as
   untrusted tool data; the model must then identify the first non-empty line.

## Provider policy

- Pinned Groq and Cloudflare role assignments remain primary.
- OpenRouter is attempted only after a primary transient failure (network failure,
  HTTP 429, or HTTP 5xx).
- The only configured OpenRouter model is `openrouter/free`.
- The fallback response must report a model identifier ending in `:free`; otherwise
  the fallback is rejected.
- No paid model, paid credit, automatic paid upgrade, or non-free router is allowed.
- Authentication and request-contract errors do not trigger fallback.
- The workflow does not print provider response bodies or credentials.

## Required GitHub Actions secrets

- `GROQ_API_KEY`
- `CLOUDFLARE_API_TOKEN`
- `CLOUDFLARE_ACCOUNT_ID`
- `OPENROUTER_API_KEY`

The workflow is available through **Actions → Six-agent qualification → Run workflow**.
It also runs on pushes to `test/six-agent-qualification-suite`. The JSON report is
uploaded as a workflow artifact even when one or more checks fail.

A passing result establishes only these four bounded capabilities at the tested
commit and time. It does not qualify the agents for unsupervised repository changes,
prove independent review competence, or constitute real training.
