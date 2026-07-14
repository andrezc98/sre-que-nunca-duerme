# CLAUDE.md — El SRE que Nunca Duerme (KCD Lima 2026 demo)

## Always use up-to-date docs — every task, every agent
This stack moves monthly (Kagent, K8sGPT, Prometheus, Grafana, Fluent Bit,
OpenTelemetry, Argo CD, OpenTofu, Bedrock/Claude). **Do NOT rely on training
memory for versions, CRD schemas, fields, flags, or APIs** — it goes stale fast
and guessing here breaks reproducibility.

Before writing or changing any code, manifest, or config, verify against current
sources:
- Library / framework / SDK / CLI / tool docs → **Context7 MCP**
  (`resolve-library-id` → `query-docs`).
- Current versions, release notes, project docs, CRD schemas →
  **WebFetch / WebSearch** on the official site or GitHub repo.
- AWS / Bedrock specifics → official AWS docs.

**Every dispatched subagent MUST do the same** — include this instruction in the
agent's prompt. Pin the exact versions / tags / model IDs you verify, and cite
the source.

## Cloud (EKS / Bedrock) is gated on the user
The AWS account / credentials will be provided by the user "when the time comes."
Until then: build and test on the **local kind path only**. Do NOT run
`tofu apply`, create cloud resources, or call Bedrock. You may *write* the cloud
IaC/manifests — just don't apply them.

## Project shape
- Talk plan: `plan-kcd-lima-2026.md`. Build order + repo layout: `README.md`.
- kind-first = live demo path; EKS + Bedrock = recorded / production path.
- Keep it minimal and reproducible (ponytail is on): reuse official charts and
  modules, don't hand-roll, don't build what the talk doesn't need.
