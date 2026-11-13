# AURIONS Workforce Model Selection and Evaluation

**Selection date:** 13 November 2026  
**Status:** Selected configuration; live endpoint probes and credentials pending  
**Policy:** Free inference only; no paid fallback; one exclusive role per agent.

## Selection basis

Models were compared for coding/reasoning fit, multi-turn tool calling, context capacity for the mandatory governance snapshot, free access, provider independence and operational limits. Public model claims are screening evidence, not proof of AURIONS role competence. The previous AURIONS screen did not qualify all six agents.

## Dedicated assignments

| Agent | Exclusive responsibility | Provider / model | Selection rationale |
|---|---|---|---|
| 1 — Lead Builder | One authorized work package end-to-end | **Z.ai — `glm-4.7-flash`** | Coding/agent-oriented Flash model with tool calling and a free API lane; strong builder candidate. Quota is not publicly stated as a stable numeric allowance. |
| 2 — Specialist Builder | One non-overlapping component or test package | **Groq — `qwen/qwen3.8-27b`** | Groq documents tool use and JSON mode; distinct model family from lead builder. Free-plan limits are organization-wide. |
| 3 — Architecture Reviewer | Read-only architecture and principle-alignment review | **NVIDIA NIM — `nvidia/nemotron-3.5-super-vl-120b-a12b`** | Free endpoint; designed for agentic, coding, reasoning and tool-calling workloads. |
| 4 — Code Reviewer | Read-only correctness, security, concurrency and regression review | **Google AI Studio — `gemini-3.8-flash`** | Current function-calling support and standing free tier. Caveat: Google says free-tier content may be used to improve its products. Do not send secrets or sensitive non-public material. |
| 5 — Negative Tester | Read-only adversarial testing against exact candidate SHA | **Cloudflare Workers AI — `@cf/qwen/qwen3-30b-a3b-fp8`** | Cloudflare lists function calling/reasoning for the Qwen3 model family; 10,000 Neurons/day free allocation. Actual token capacity varies. |
| 6 — Integration Verifier | Read-only exact-SHA/evidence reconciliation and Director packet | **Groq — `openai/gpt-oss-120b`** | Tool use, JSON mode, reasoning and long context; published free-plan limits. Must run after the Groq specialist builder, not concurrently, to avoid quota contention. |

Each agent has one role, one role contract, one model assignment and one evidence responsibility. The integration verifier reconciles the other roles' evidence; it does not redo their work.

## Direct provider endpoints and required secrets

- Z.ai: `https://api.z.ai/api/paas/v4/chat/completions` — `ZAI_API_KEY`
- Groq: `https://api.groq.com/openai/v1/chat/completions` — `GROQ_API_KEY`
- NVIDIA NIM: `https://integrate.api.nvidia.com/v1/chat/completions` — `NVIDIA_API_KEY`
- Google Gemini OpenAI-compatible API: `https://generativelanguage.googleapis.com/v1beta/openai/chat/completions` — `GEMINI_API_KEY`
- Cloudflare: `https://api.cloudflare.com/client/v4/accounts/<ACCOUNT_ID>/ai/v1/chat/completions` — `CLOUDFLARE_API_TOKEN` and `CLOUDFLARE_ACCOUNT_ID`

Secrets must be stored only in GitHub Actions secrets or a secret manager. Missing credentials must fail closed. No silent routing to OpenRouter, model substitution or paid fallback.

## Candidates not selected

- **Cerebras GLM-4.7:** strong coding/tool-use candidate and very fast, but its published free tier documents an 8,192-token context allowance. That is too tight for the full mandatory governance snapshot plus repository context.
- **Mistral API / Devstral:** technically attractive for code agents, but current Mistral plan documentation says Free mode does not include API access; API use requires billing activation. Excluded from a strict free-only setup.
- **OpenRouter:** retain as an optional compatibility adapter only, not primary routing. Direct providers provide role-specific options and reduce single-gateway dependency.

## Quota and privacy constraints

- Groq currently publishes 30 RPM, 1,000 RPD and 8K TPM for both selected model IDs on the listed free-plan table. Limits are organization-wide; serialize the two Groq roles.
- Cloudflare's free allocation is 10,000 Neurons/day, not a fixed token allowance.
- NVIDIA free endpoints may be traffic-limited; no numeric quota is assumed.
- Z.ai's Flash quota is account-specific/not publicly stated as a stable numeric allowance.
- Gemini free-tier content may be used to improve Google products. Use only public project context and never include secrets.
- Any 429, quota exhaustion, provider error or budget exhaustion pauses that role. No automatic fallback or quota evasion.

## Qualification status

**Not qualified yet.** This is model selection from current public documentation and prior AURIONS screening evidence, not a claim that the models passed live AURIONS role tests. The next validation is a bounded tool-call/context/role-calibration run per assigned agent, with one role per run. The user's waiver of separate pre-selection screening does not waive live setup verification or subsequent role qualification.

## Source register

- Google pricing/data-use terms: https://ai.google.dev/gemini-api/docs/pricing
- Google function calling: https://ai.google.dev/gemini-api/docs/function-calling
- Groq model catalog: https://console.groq.com/docs/models
- Groq tool-use support: https://console.groq.com/docs/tool-use/overview
- Groq rate limits: https://console.groq.com/docs/rate-limits
- NVIDIA free model catalog: https://build.nvidia.com/models
- NVIDIA tool-calling support: https://docs.nvidia.com/nim/large-language-models/1.15.0/function-calling.html
- Cloudflare pricing: https://developers.cloudflare.com/workers-ai/platform/pricing/
- Cloudflare function calling: https://developers.cloudflare.com/workers-ai/features/function-calling/
- Cloudflare model catalog: https://developers.cloudflare.com/workers-ai/models/
- Cerebras free tier/context: https://inference-docs.cerebras.ai/support/pricing
- Mistral Free/API distinction: https://docs.mistral.ai/admin/billing-usage/usage-limits
