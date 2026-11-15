# AURIONS Workforce — Model Selection and Assignment

**Snapshot:** 13 November 2026  
**Status:** Selected provisional assignments; not qualification  
**Policy:** Free inference only; one exclusive role and one unique primary model per agent; OpenRouter `openrouter/free` is permitted only as a free-only fallback for transient primary failures and Groq model-permission HTTP 403; paid inference is prohibited

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

**Groq is the strongest direct provider for the high-volume part of this workforce.** It exposes the selected GPT-OSS 120B, GPT-OSS 20B and Qwen 3.8 27B models through its API and provides a no-charge Free tier. Groq's public rate-limit page is not a reliable substitute for the account's live Free-tier limits: it notes tier differences and account-specific exceptions. The runner may use the explicitly configured OpenRouter free fallback after transient 429, 5xx or network failures, and after Groq model-permission HTTP 403. Groq 403 remains recorded as a primary-provider defect; HTTP 401, Cloudflare 403 and invalid requests remain hard stops. The Director should verify the actual Free-tier limits in the Groq console before a long run. Groq documents tool use and reasoning for the selected models.

**Cloudflare Workers AI is the second selected direct provider.** The Workers Free plan includes 10,000 Neurons per day across Workers AI; on the Free plan, exceeding the allowance causes further requests to fail. On the Workers Paid plan, usage above the free allocation is billable. Therefore the model registry's `free_daily_allowance` label is not proof that an account cannot incur charges. Every inference workflow now requires an explicit Director attestation that the selected account is on Workers Free, not Workers Paid. Do not dispatch unless that account-plan check has been made in the Cloudflare dashboard. The daily Neuron allowance is shared across all three Cloudflare agents. The three selected models support function calling; Cloudflare states that standard inference inputs and outputs are not retained after processing and are not used to train models.

OpenRouter is not a primary role assignment. It is permitted only as a last-resort fallback using exactly `openrouter/free`, after primary HTTP 429, HTTP 5xx or network failure, or a Groq model-permission HTTP 403. A Groq 403 is retained as an explicit primary-provider defect in route history and qualification reports; fallback does not qualify Groq itself as healthy. HTTP 401, Cloudflare 403, invalid requests and model-contract errors remain hard stops. The runtime verifies the returned model ID ends in `:free`, pins that actual model for the remainder of each worker conversation, rejects mid-run model changes, records the primary failure and actual fallback model, and preserves usage accounting. Free variants are currently limited to 20 requests/minute and 50 requests/day; failed attempts count toward the daily cap. Do not purchase credits to raise the quota. The initial `openrouter/free` selection is dynamic, but the runtime pins the returned `:free` model for the remainder of that worker conversation and fails closed if the model changes. Provider data practices vary; the Free plan does not provide the data-policy-based routing filter. Therefore fallback requests may contain only public repository material and non-sensitive task context. Never include secrets, private data or confidential project material in OpenRouter requests.

Google AI Studio's free Gemini tier is technically attractive, but Google's pricing documentation explicitly marks free-tier content as used to improve its products. It is therefore not selected for private repository code. Z.ai GLM Flash models are also listed as free, but their public rate limits are not specified and the individual-user data terms are not sufficiently clear for this repository workflow. These are not preferred over Groq and Cloudflare for this use.

## Credentials required

Store only as GitHub Actions repository secrets:
- `GROQ_API_KEY` — lead builder, code reviewer and negative tester.
- `CLOUDFLARE_API_TOKEN` — specialist builder, architecture reviewer and integration verifier.
- `CLOUDFLARE_ACCOUNT_ID` — required with the Cloudflare token.
- `OPENROUTER_API_KEY` — required for the free-only fallback after transient failures and Groq model-permission HTTP 403.

The Cloudflare token should have only the Workers AI inference permissions required for the account. Never place credentials in source files, workflow literals, prompts, logs or artifacts. No paid fallback or unapproved model/provider substitution is permitted; the only automatic route change is the explicitly bounded OpenRouter free fallback for transient failures and Groq model-permission HTTP 403.

## Operating constraints

1. Each agent receives only its exclusive role contract and one pinned model.
2. All six receive the same mandatory, freshly read governance and induction sources from the pinned repository revision.
3. Role/model/endpoint overrides are rejected by the runner; assignments are pinned in `engineering/workforce/src/workforce/model_registry.py`.
4. Cloudflare's daily Neuron allowance is shared; per-role and global consumption must be measured and bounded.
5. OpenRouter fallback is limited to transient failures and Groq model-permission HTTP 403; HTTP 401, Cloudflare 403 and request-contract failures remain hard stops. Its 20 RPM / 50 RPD free cap is shared and failed attempts count toward it.
6. Fallback responses must identify an actual `:free` model, and the report must record the primary provider failure and actual fallback model.
7. Model availability, free quota and endpoint compatibility must be checked at run time. Published quotas are not guarantees of available capacity.
8. A model response, onboarding run or policy acknowledgment does not qualify an agent.
9. Qualification requires repeated role-specific evidence, including a practical failure case, independently scored against the induction rubric.
10. A model/provider change requires a reviewed registry change and new role-specific regression evaluation.
11. The current long-run workflow contains a bounded WF-03 Unicode label-normalization qualification task. Dispatch only after every role has a verified primary or approved free-fallback route; preserve and report every primary-provider failure.

## Current status

- **Model assignments:** selected and pinned in code.
- **Role separation:** six exclusive roles; six distinct model IDs.
- **Training context:** mandatory induction, role curricula, governance and EBT-01 are freshly injected by the runner.
- **Model execution:** the latest recorded live diagnostic returned HTTP 403 for Groq, but the response body was not preserved, so the exact cause was not established. Groq documents distinct organization/project model-permission error codes; the runtime now permits fallback only for those exact codes and stops on unrelated 403 responses. A fresh live diagnostic is still required. Cloudflare assignments connected in earlier provider checks; role qualification remains incomplete. The OpenRouter free fallback passed an earlier independent smoke test; the new daily-quota guard has not yet been exercised against live credentials.
- **Agent qualification:** not established.
- **Overnight supervision:** not established; the current workflow is a finite GitHub Actions pipeline, not a persistent worker supervisor.

## Provider documentation reviewed

- Groq [Free-tier billing FAQ](https://console.groq.com/docs/billing-faqs), [rate limits](https://console.groq.com/docs/rate-limits), [data retention controls](https://console.groq.com/docs/your-data), [GPT-OSS 120B](https://console.groq.com/docs/model/openai/gpt-oss-120b), [Qwen 3.8 27B](https://console.groq.com/docs/model/qwen/qwen3.8-27b).
- Cloudflare [Workers AI pricing](https://developers.cloudflare.com/workers-ai/platform/pricing/), [data usage commitments](https://developers.cloudflare.com/workers-ai/platform/data-usage/), [OpenAI-compatible endpoint](https://developers.cloudflare.com/workers-ai/configuration/open-ai-compatibility/), [Gemma 4 26B](https://developers.cloudflare.com/workers-ai/models/gemma-4-26b-a4b-it/), [GLM 4.7 Flash](https://developers.cloudflare.com/workers-ai/models/glm-4.7-flash/), [Mistral Small 3.1 24B](https://developers.cloudflare.com/workers-ai/models/mistral-small-3.1-24b-instruct/).
- OpenRouter [Free model limits and pricing](https://openrouter.ai/collections/free-models), [plan comparison and routing limits](https://openrouter.ai/pricing), [NVIDIA Nemotron free endpoint data notice](https://openrouter.ai/nvidia/nemotron-3-ultra-550b-a55b:free).
- Google [Gemini API pricing and data-use distinctions](https://ai.google.dev/gemini-api/docs/pricing).
