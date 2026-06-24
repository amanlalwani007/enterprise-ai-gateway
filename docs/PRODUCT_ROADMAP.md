# Enterprise AI Gateway — Product Roadmap

> **Vision:** The single control plane every organization needs to safely, efficiently, and observably use 100+ LLM providers — from prototype to production at scale.

---

## Guiding Principles

1. **Safety first** — Every feature is designed with enterprise compliance and data protection as the default.
2. **Open-core, not open-source afterthought** — The free tier is genuinely useful; paid features are justified by complexity (not artificial gates).
3. **Drop-in compatible** — Zero changes to existing OpenAI SDK code. Integrate by changing `base_url`.
4. **Observability by default** — Every request is traceable, accountable, and explainable.

---

## Phase 1: Safety & Observability (v0.3 – v0.5) ← *Current focus*

The #1 blocker for enterprise LLM adoption is **loss of control** — over what goes in, what comes out, and how much it costs. This phase turns the gateway from a proxy into a **policy enforcement point**.

| Feature | Effort | Impact | Issue |
|---|---|---|---|
| Guardrails Pipeline Framework | Medium | Very High | #7 |
| Input Guardrails (Prompt Injection, Jailbreak Detection) | Medium | Very High | #8 |
| Output Guardrails (Toxicity, JSON Schema, Refusal Detection) | Medium | Very High | #9 |
| Cost Intelligence & Budget Forecasting | Small | High | #10 |
| Quality Metrics & Drift Detection | Medium | High | #11 |

**Target:** By the end of Phase 1, the gateway is the most trusted LLM proxy in open source — every request is guarded, every dollar is tracked, every regression is caught.

---

## Phase 2: Developer Productivity (v0.6 – v0.8)

Once safety and cost are under control, the next bottleneck is **developer velocity**. This phase turns the gateway into the team's daily LLM workspace.

| Feature | Effort | Impact | Issue |
|---|---|---|---|
| Prompt Playground (multi-model side-by-side) | Medium | Very High | #12 |
| Prompt Versioning & Collaboration | Medium | High | #13 |
| A/B Testing & Prompt Experimentation | High | Very High | #14 |
| Team Workspaces & Role-Based Access | Medium | High | #15 |
| Admin Dashboard (live data, real charts) | Medium | Very High | — |

**Target:** Engineering teams manage their entire LLM workflow through the gateway — from prompt iteration to production deployment.

---

## Phase 3: Advanced AI Ops (v0.9 – v1.0+)

The final phase builds the infrastructure needed for **agentic, production-grade AI systems**.

| Feature | Effort | Impact | Issue |
|---|---|---|---|
| First-Class Agent/Chain Support | High | Very High | #16 |
| Canary Deployments & Model Eval Pipeline | Medium | Very High | #17 |
| Distributed Tracing (OpenTelemetry) | High | Very High | #18 |
| Self-Hosted Fine-Tuning Pipeline | High | Medium | — |

**Target:** The gateway supports the full lifecycle of modern AI applications — from single-turn chat to complex agentic chains, with enterprise-grade reliability.

---

## How to Contribute

Each issue in the roadmap links to a GitHub issue with:
- Clear acceptance criteria
- Suggested approach
- Test expectations

Labels used:
- `phase-1` / `phase-2` / `phase-3` — which phase the feature belongs to
- `enhancement` — new feature
- `good first issue` — approachable for new contributors

See [CONTRIBUTING.md](../CONTRIBUTING.md) for development setup.

---

## Current Status

- **Latest release:** v0.2.0
- **Completed:** OpenAI-compatible proxy, streaming, API key auth, rate limiting, budget enforcement, semantic caching, PII masking, model routing, admin API, audit logs, health checks, basic dashboard
- **In progress:** Phase 1 features listed above
