# AURIONS Workforce — Model Selection and Assignment

**Snapshot:** 13 November 2026  
**Status:** Selected provisional assignments; not qualification  
**Policy:** Free inference only; no paid fallback; one exclusive role and one unique model per agent

## Selection method

Models were compared using currently published provider documentation and model capability descriptions. Selection prioritizes:
- coding and tool-use capability for builders;
- long-context reasoning for architecture review;
- code reasoning and structured outputs for code review;
- reasoning and tool use for adversarial testing;
- evidence reconciliation and consistent structured reporting for integration verification;
- direct provider terms, predictable free limits, and role/model separation.

These are informed assignments, not empirical qualification results. No claim is made that a model is already competent in its assigned role. The previous six-agent screening remains incomplete and does not qualify the team.

## Selected six-agent roster

| Agent | Exclusive responsibility | Provider | Exact model | Why selected |
|---|---|---|---|---|
| 1 — Lead Builder | One approved work package: plan, implement, self-review, test, correct and hand off | Groq direct | `openai/gpt-oss-120b` | Strongest available Groq free-tier reasoning/coding candidate with tool use |
| 2 — Specialist Builder | One separately owned, non-overlapping component only | OpenRouter | `cohere/north-mini-code:free` | Purpose-built agentic coding model with tool use |
| 3 — Architecture Reviewer | Architecture and principle alignment only; read-only | OpenRouter | `nvidia/nemotron-3-ultra-550b-a55b:free` | Long-context reasoning and multi-step architecture analysis |
| 4 — Code Reviewer | Correctness, security, edge cases and regression review only; read-only | Groq direct | `qwen/qwen3.8-27b` | Coding-oriented model with tool use and structured outputs |
| 5 — Negative Tester | Falsification and adversarial test execution only; read-only | OpenRouter | `nvidia/nemotron-3.5-super-vl:free` | Reasoning-capable long-context agent model with tool use |
| 6 — Integration Verifier | Evidence, ancestry, SHA and finding reconciliation only; read-only | Groq direct | `openai/gpt-oss-20b` | Tool use and structured-output support suited to bounded evidence reconciliation |

**No model is assigned to more than one agent. No agent may combine another role's responsibility.** The orchestrator remains deterministic control software, not a seventh agent.

## Better free provider outside OpenRouter

**Groq is the best direct-provider alternative identified for this workload.** Its current free-plan rate-limit documentation lists GPT-OSS 120B, GPT-OSS 20B and Qwen 3.8 27B at up to 30 requests/minute, 1,000 requests/day, 8,000 tokens/minute and 200,000 tokens/day per model, subject to account-specific limits. Groq documents tool use for these models. This is materially more useful for repeated agent runs than relying exclusively on OpenRouter's free-model cap of 50 requests/day (20/minute) for accounts below its credit threshold.

Groq also states that inference inputs/outputs are not retained by default and are not used to train its models. Reliability/abuse troubleshooting may temporarily retain data for up to 30 days unless Zero Data Retention is enabled. Enable ZDR in the Groq console before sending sensitive repository content if available to the account.

OpenRouter remains in the roster because its current free catalogue provides specialist models not available in Groq's free-plan list. Its free model variants are capped at 20 requests/minute and 50 requests/day until the account has purchased the qualifying credit amount. Provider data practices vary; this configuration requests providers that declare data collection denied. If no eligible endpoint is available, the run must fail closed rather than route to an unapproved provider.

## Credentials required

Store these only as GitHub Actions repository secrets:
- `GROQ_API_KEY` — required by agents 1, 4 and 6.
- `OPENROUTER_API_KEY` — required by agents 2, 3 and 5.

Do not put keys in repository files, workflow literals, prompts, logs or artifacts. Do not configure a paid fallback. Missing credentials must stop only the affected run with a clear error.

## Operating constraints

1. Each agent receives only its exclusive role contract and one assigned model.
2. All six receive the same mandatory, freshly read governance and induction sources from the pinned repository revision.
3. Role assignments are pinned in `engineering/workforce/src/workforce/model_registry.py`; model or endpoint overrides are rejected by the runner.
4. OpenRouter requests require a provider with data collection denied. No automatic provider fallback is permitted.
5. Model availability, free quota and endpoint compatibility must be checked at run time. Published quotas are not guarantees of available capacity.
6. A model response, onboarding run or policy acknowledgment does not qualify an agent.
7. Qualification requires repeated role-specific evidence, including a practical failure case, independently scored against the induction rubric.
8. A model/provider change requires a reviewed registry change and new role-specific regression evaluation.
9. The current long-run workflow contains a prewritten WF-01 workforce-infrastructure task. Do not dispatch it as the user's first task; replace it with the Director's actual task contract first.

## Current status

- **Model assignments:** selected and pinned in code.
- **Role separation:** six exclusive roles; six distinct model IDs.
- **Training context:** mandatory induction, role curricula, governance and EBT-01 are freshly injected by the runner.
- **Model execution:** not yet tested with the newly selected roster.
- **Agent qualification:** not established.
- **Overnight supervision:** not established; the current workflow is a finite GitHub Actions pipeline, not a persistent worker supervisor.
