# AURIONS Workforce — Model Selection and Assignment

**Snapshot:** 13 November 2026  
**Status:** Selected provisional assignments; not qualification  
**Policy:** Free inference only; one exclusive role and one unique primary model per agent; OpenRouter `openrouter/free` is permitted only as a transient-failure fallback; paid inference is prohibited

## Selection method

Models were compared against current provider documentation for:
- software engineering and tool/function-calling capability;
- reasoning and long-context suitability for each role;
- free-tier availability and practical quota;
- data retention and training policy;
- API compatibility with the existing worker runner.

Selection is a reasoned engineering choice, not an empirical qualification result. The previous six-agent screening did not qualify the team. No model is represented as proven competent in its role.

## Selected six-agent roster

| Agent | Exclusive responsibility | Provider | Exact model | Selection rationale |
|---|---|---|---|---|
| 1 — Lead Builder | One approved work package: plan, implement, self-review, test, correct and hand off | Groq direct | `openai/gpt-oss-120b` | Strong reasoning/coding candidate with tool use; Groq publishes a standing free plan for this model |
| 2 — Specialist Builder | One separately owned, non-overlapping component only | Cloudflare Workers AI | `@cf/google/gemma-4-26b-a4b-it` | 256K context, reasoning, coding and function calling |
| 3 — Architecture Reviewer | Architecture and principle alignment only; read-only | Cloudflare Workers AI | `@cf/zai-org/glm-4.7-flash` | Reasoning, multi-turn tool calling, 131K context and multilingual instruction following |
| 4 — Code Reviewer | Correctness, security, edge cases and regression review only; read-only | Groq direct | `qwen/qwen3.8-27b` | Coding-oriented model with tool use and structured outputs |
| 5 — Negative Tester | Falsification and adversarial test execution only; read-only | Groq direct | `openai/gpt-oss-20b` | Tool-capable reasoning model suitable for bounded adversarial test work |
| 6 — Integration Verifier | Evidence, ancestry, SHA and finding reconciliation only | Cloudflare Workers AI | `@cf/mistralai/mistral-small-3.1-24b-instruct` | Function calling and 128K context for bounded evidence reconciliation |

**All six model IDs are distinct. Each agent has exactly one role. No agent may take on another role's responsibility or claim another role's gate.** The orchestrator remains deterministic control software, not a seventh agent.

## Better free providers outside OpenRouter

**Groq is the strongest direct provider for the high-volume part of this workforce.** It exposes the selected GPT-OSS 120B, GPT-OSS 20B and Qwen 3.8 27B models through its API and provides a no-charge Free tier. Groq's public rate-limit page is not a reliable substitute for the account's live Free-tier limits: it notes tier differences and account-specific exceptions. The runner must treat 429 responses as a hard stop, and the Director should verify the actual Free-tier limits in the Groq console before a long run. Groq documents tool use and reasoning for the selected models.

**Cloudflare Workers AI is the second selected direct provider.** The Workers Free plan includes 10,000 Neurons per day across Workers AI; on the Free plan, exceeding the allowance causes further requests to fail. On the Workers Paid plan, usage above the free allocation is billable. Therefore the model registry's `free_daily_allowance` label is not proof that an account cannot incur charges. Every inference workflow now requires an explicit Director attestation that the selected account is on Workers Free, not Workers Paid. Do not dispatch unless that account-plan check has been made in the Cloudflare dashboard. The daily Neuron allowance is shared across all three Cloudflare agents. The three selected models support function calling; Cloudflare states that standard inference inputs and outputs are not retained after processing and are not used to train models.

OpenRouter is not a primary role assignment. It is permitted only as a last-resort transport fallback for transient primary-provider failures (HTTP 429, HTTP 5xx, or network failure), using exactly `openrouter/free`. It must not conceal HTTP 401/403 authentication or permission failures, invalid requests, or model-contract errors; those stop the run and require correction. The runtime must verify that OpenRouter's returned model ID ends in `:free` before accepting the response, record the primary failure and actual fallback model, and preserve usage accounting. The free variants are currently limited to 20 requests/minute and 50 requests/day; failed attempts count toward the daily cap. Do not purchase credits to raise the quota. Free routing is dynamic and provider data practices vary; the Free plan does not provide the data-policy-based routing filter. Therefore fallback requests may contain only public repository material and non-sensitive task context. Never include secrets, private data or confidential project material in OpenRouter requests.

Google AI Studio's free Gemini tier is technically attractive, but Google's pricing documentation explicitly marks free-tier content as used to improve its products. It is therefore not selected for private repository code. Z.ai GLM Flash models are also listed as free, but their public rate limits are not specified and the individual-user data terms are not sufficiently clear for this repository workflow. These are not preferred over Groq and Cloudflare for this use.

## Credentials required

Store only as GitHub Actions repository secrets:
- `GROQ_API_KEY` — lead builder, code reviewer and negative tester.
- `CLOUDFLARE_API_TOKEN` — specialist builder, architecture reviewer and integration verifier.
- `CLOUDFLARE_ACCOUNT_ID` — required with the Cloudflare token.
- `OPENROUTER_API_KEY` — required for the free-only transient-failure fallback.

The Cloudflare token should have only the Workers AI inference permissions required for the account. Never place credentials in source files, workflow literals, prompts, logs or artifacts. No paid fallback or unapproved model/provider substitution is permitted; the only automatic route change is the explicitly bounded OpenRouter free fallback for transient failures.

## Provider request contracts verified

The worker and preflight use provider-specific authentication but the OpenAI-compatible Chat Completions request shape. Both send `Content-Type: application/json` and `Accept: application/json` so Cloudflare returns structured JSON errors where supported:

| Model assignment | Endpoint | Authentication | Completion limit | Tool calling |
|---|---|---|---|---|
| Groq — all three pinned models | `POST https://api.groq.com/openai/v1/chat/completions` | `Authorization: Bearer GROQ_API_KEY` | `max_completion_tokens` | `tools` with `tool_choice`; all three pinned models document local function calling |
| Cloudflare — Gemma 4 26B and GLM-4.7-Flash | `POST https://api.cloudflare.com/client/v4/accounts/{account_id}/ai/v1/chat/completions` | `Authorization: Bearer CLOUDFLARE_API_TOKEN`; token requires Account > Workers AI > Read | `max_completion_tokens`; model pages mark `max_tokens` deprecated | Both model pages document function calling; GLM explicitly documents `tool_choice: required` |
| Cloudflare — Mistral Small 3.1 24B | Same account-scoped endpoint | Same token permission | `max_tokens` as listed by its current model page | Model page documents function calling and tool-call output |

Cloudflare's standard API error envelope uses an `errors` array containing `code` and `message`; some Cloudflare-generated errors use RFC 9457 problem details. Diagnostics must parse only bounded, allowlisted fields from these formats, redact credentials, and never dump arbitrary response bodies. Groq uses an OpenAI-style `error` object with `message` and `type`; its documented rate-limit headers distinguish daily request limits from per-minute token limits.

The selected Cloudflare models are not among the models Cloudflare currently marks as requiring Workers Paid. Workers AI's Free allocation is 10,000 Neurons per account per day, shared by all three Cloudflare roles and resetting at 00:00 UTC. This allowance is not a per-agent allowance. Confirm the account is on Workers Free and monitor remaining Neurons before dispatch; never treat a model's published per-million-token unit price as proof that a given account is on a free plan.

## Operating constraints

1. Each agent receives only its exclusive role contract and one pinned model.
2. All six receive the same mandatory, freshly read governance and induction sources from the pinned repository revision.
3. Role/model/endpoint overrides are rejected by the runner; assignments are pinned in `engineering/workforce/src/workforce/model_registry.py`.
4. Cloudflare's daily Neuron allowance is shared; per-role and global consumption must be measured and bounded.
5. OpenRouter fallback is limited to transient failures only; HTTP 401/403 and request-contract failures remain hard stops. Its 20 RPM / 50 RPD free cap is shared and failed attempts count toward it.
6. Fallback responses must identify an actual `:free` model, and the report must record the primary provider failure and actual fallback model.
7. Model availability, free quota and endpoint compatibility must be checked at run time. Published quotas are not guarantees of available capacity.
8. A model response, onboarding run or policy acknowledgment does not qualify an agent.
9. Qualification requires repeated role-specific evidence, including a practical failure case, independently scored against the induction rubric.
10. A model/provider change requires a reviewed registry change and new role-specific regression evaluation.
11. The current long-run workflow contains a prewritten WF-01 workforce-infrastructure task. Do not dispatch it as the user's first task; replace it with the Director's actual task contract first.

## Current status

- **Model assignments:** selected and pinned in code.
- **Role separation:** six exclusive roles; six distinct model IDs.
- **Training context:** mandatory induction, role curricula, governance and EBT-01 are freshly injected by the runner.
- **Model execution:** primary provider preflight remains blocked until all six pinned endpoints pass; OpenRouter free fallback is implemented in the candidate runtime but requires full automated regression and live preflight verification.
- **Agent qualification:** not established.
- **Overnight supervision:** not established; the current workflow is a finite GitHub Actions pipeline, not a persistent worker supervisor.

## Provider documentation reviewed

- Groq [Free-tier billing FAQ](https://console.groq.com/docs/billing-faqs), [rate limits and response headers](https://console.groq.com/docs/rate-limits), [API errors](https://console.groq.com/docs/errors), [local tool calling](https://console.groq.com/docs/tool-use/overview), [Chat Completions API reference](https://console.groq.com/docs/api-reference), [data retention controls](https://console.groq.com/docs/your-data), [GPT-OSS 120B](https://console.groq.com/docs/model/openai/gpt-oss-120b), [GPT-OSS 20B](https://console.groq.com/docs/model/openai/gpt-oss-20b), [Qwen 3.8 27B](https://console.groq.com/docs/model/qwen/qwen3.8-27b).
- Cloudflare [Workers AI pricing](https://developers.cloudflare.com/workers-ai/platform/pricing/), [model rate limits](https://developers.cloudflare.com/workers-ai/platform/limits/), [data usage commitments](https://developers.cloudflare.com/workers-ai/platform/data-usage/), [OpenAI-compatible endpoint](https://developers.cloudflare.com/workers-ai/configuration/open-ai-compatibility/), [AI REST API and authentication](https://developers.cloudflare.com/ai-gateway/usage/rest-api/), [Cloudflare API error formats](https://developers.cloudflare.com/fundamentals/reference/error-responses/), [Gemma 4 26B](https://developers.cloudflare.com/workers-ai/models/gemma-4-26b-a4b-it/), [GLM 4.7 Flash](https://developers.cloudflare.com/workers-ai/models/glm-4.7-flash/), [Mistral Small 3.1 24B](https://developers.cloudflare.com/workers-ai/models/mistral-small-3.1-24b-instruct/).
- OpenRouter [Free model limits and pricing](https://openrouter.ai/collections/free-models), [plan comparison and routing limits](https://openrouter.ai/pricing), [NVIDIA Nemotron free endpoint data notice](https://openrouter.ai/nvidia/nemotron-3-ultra-550b-a55b:free).
- Google [Gemini API pricing and data-use distinctions](https://ai.google.dev/gemini-api/docs/pricing).
