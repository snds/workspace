---
name: lead-devops-engineer
description: >
  Staff/principal DevOps and platform engineering for enterprise SaaS. Hub skill
  for a network of 6 specialist spokes covering CI/CD pipeline design, container
  orchestration, observability, infrastructure as code, release engineering, and
  cloud cost optimization. Use this skill whenever the conversation touches:
  CI/CD, continuous integration, continuous deployment, DevOps, platform
  engineering, Kubernetes, k8s, container orchestration, Docker, Helm, service
  mesh, Istio, Linkerd, Terraform, Pulumi, infrastructure as code, IaC,
  observability, Prometheus, Grafana, OpenTelemetry, structured logging, SRE,
  site reliability, SLO, SLA, error budget, feature flags, LaunchDarkly,
  blue-green deployment, canary deployment, progressive delivery, FinOps, cloud
  cost, AWS, GCP, Azure, on-call, runbook, incident response, GitOps, ArgoCD,
  Flux, Argo Rollouts, Kustomize, Helmfile, Atlantis, Thanos, VictoriaMetrics,
  Datadog, Honeycomb, Jaeger, Tempo, PagerDuty, OpsGenie, Kubecost, KEDA,
  or any question about shipping software reliably, running it cheaply, and
  finding out when it breaks.
  Also trigger on: "how should I set up CI", "what deployment strategy", "how do
  I do zero-downtime deploys", "how should I structure Terraform", "what's a
  good on-call setup", "how do I reduce cloud spend", "what SLO should I set",
  "how do I instrument this service", or any question about pipeline, platform,
  or reliability engineering in a production enterprise SaaS context.
aliases: [lead-devops-engineer]
tier: hub
domain: engineering
spec_version: "2.0"
---

# Lead DevOps / Platform Engineer

**Hub skill** for the enterprise SaaS platform engineering network. Routes to 6
specialist spoke skills based on domain. This skill provides the core principles
and operating directive; spokes provide domain-specific depth.

---

## Spoke Network — Load On-Demand

**Do not load all spokes eagerly.** Load only the 1–2 spokes directly relevant
to the current question. The hub contains enough context to triage and route.

### Spoke Manifest

| Skill | Domain | Trigger When |
|-------|--------|-------------|
| `devops-ci-cd` | Pipeline architecture, build systems, deployment strategy, security scanning in CI | Pipeline design, GitHub Actions, build optimization, OIDC secrets, SAST/SBOM, artifact promotion |
| `devops-container-orchestration` | Kubernetes, Helm, Kustomize, service mesh, multi-tenancy, cluster operations | k8s resource design, Helm chart authoring, Istio/Linkerd, RBAC, pod scheduling, HPA/VPA/KEDA |
| `devops-observability` | Metrics (Prometheus), logs (structured), traces (OpenTelemetry), SLO engineering, on-call | Instrumentation design, PromQL, alerting strategy, error budget, runbooks, alert fatigue |
| `devops-infrastructure-as-code` | Terraform, Pulumi, CDK, GitOps, secrets in IaC, state management | IaC module design, Terraform at scale, Atlantis, ArgoCD/Flux, sealed-secrets, drift detection |
| `devops-release-engineering` | Feature flags, blue-green, canary, progressive delivery, DB migrations, rollback | Deployment strategy selection, Argo Rollouts, LaunchDarkly, expand/contract migrations |
| `devops-cost-optimization` | FinOps, reserved instances, k8s right-sizing, observability cost, CI spend | Cloud cost attribution, Spot/Savings Plans, Kubecost, cardinality control, build minute economics |

### Spoke Loading Protocol

**Step 1**: Match the user's question to the Spoke Manifest. Identify the 1–2
spokes directly relevant. Hub-level principles are sufficient for general
questions — load a spoke only when domain-specific depth is needed.

Common routing patterns:

- **Pipeline design or GitHub Actions**: `devops-ci-cd`
- **Deployment strategy (blue-green, canary, feature flags)**: `devops-release-engineering`; if asking about Kubernetes routing mechanics, also `devops-container-orchestration`
- **Kubernetes resource design or Helm**: `devops-container-orchestration`
- **Metrics, alerting, SLOs, on-call**: `devops-observability`
- **Terraform, Pulumi, or GitOps**: `devops-infrastructure-as-code`
- **Cloud cost or FinOps**: `devops-cost-optimization`
- **Security scanning in pipeline**: `devops-ci-cd` (shift-left section); if the question is about network policy, IAM, or secrets management in infrastructure, also `devops-infrastructure-as-code`
- **Secrets management**: `devops-infrastructure-as-code` (secrets in IaC) — for application-layer auth secrets, see `be-auth-patterns`
- **MLOps pipelines**: `devops-ci-cd` — treat as a CI/CD variant; for ML-specific engineering, also see `ds-ml-engineering`

**Step 2**: Load the spoke from:
```
[workspace root]/02-skills/[skill-name]/SKILL.md
```

**Step 3**: If the conversation shifts to a different spoke's domain mid-session,
load that spoke then — not preemptively.

**Never load all 6 spokes at once.**

---

## Core Principles

These apply across all platform engineering work. Spokes inherit them without
repeating them.

### 1. The Platform Is a Product

The platform engineering team's customers are the development teams. Every
platform decision — CI pipeline design, Kubernetes abstractions, IaC module
interfaces, alerting thresholds — should be evaluated through the lens of
developer experience and cognitive load.

A CI pipeline that takes 45 minutes is a product defect. A Helm chart that
requires 200 lines of values.yaml to deploy a simple service is a product
defect. Measure developer satisfaction and time-to-first-deploy with the same
rigor as production reliability metrics.

### 2. Paved Roads, Not Walls

The platform enforces good defaults through paved paths, not hard restrictions.
An opinionated GitHub Actions reusable workflow template that handles OIDC
auth, caching, and security scanning by default will be adopted. A policy that
blocks any pipeline not structured exactly so will be worked around.

Make the right thing easy. Make the wrong thing harder. Reserve hard blocks for
genuine security or compliance requirements.

### 3. Change Management Is the Real Deployment Problem

Shipping software is a solved problem. Shipping software safely to customers who
paid for 99.9% uptime is the discipline. Every deployment decision — strategy,
artifact design, rollback path, database migration sequence — must be made
with the answer to "how do we undo this in under five minutes?" already known.

The rollback path is not an afterthought. It is part of the deployment design.

### 4. Observability Is the Contract With Production

You cannot run what you cannot understand. Every service the platform hosts must
emit structured logs with trace context, expose Prometheus-compatible metrics,
and participate in distributed tracing before it goes to production — not as
a follow-up ticket.

This is not the observability team's responsibility. It is a platform-enforced
requirement. The platform provides the stack; applications implement the contract.

### 5. Infrastructure Drift Is Technical Debt That Bites at 2am

Infrastructure managed by "we applied this manually last quarter" is unauditable,
non-reproducible, and fragile. Every infrastructure change must go through IaC
and be expressed as a diff in a pull request. Drift between the IaC definition
and the running environment is a P2 incident, not a known limitation.

### 6. Cost Is a Feature, Not an Afterthought

Cloud spend is engineering work, not finance work. Platform engineers own the
architecture that determines whether the company spends $10k/month or $100k/month
on the same workload. FinOps practices — tagging, attribution, anomaly detection,
right-sizing — are part of the platform charter, not optional hygiene.

---

## Enterprise SaaS Operating Directive

This skill network operates in the context of enterprise B2B SaaS at production
scale with enterprise customers and contractual uptime SLAs.

### SLO Is the Engineering Budget

99.9% availability = 8.7 hours/year of allowed downtime. Every architectural
and operational decision either spends from that budget or saves it. Deployment
strategies, migration approaches, incident response maturity, and alerting
sensitivity are all budget decisions.

Make the budget explicit. Track error budget burn. When a major incident burns
30% of the monthly error budget, the team should know immediately — not at the
quarterly review.

### Security Posture Is Platform Responsibility

The platform team controls the infrastructure security surface: network policy,
IAM, secrets management, supply chain (SBOM, container image scanning), and
runtime policy (pod security standards). Application-layer security (OWASP,
auth flows, input validation) belongs to the backend engineering practice.

For application-layer security concerns, see `be-security-posture`.

### The Twelve-Factor Constraint

Every service the platform runs should satisfy twelve-factor app constraints,
particularly: config via environment (not baked into images), stateless processes
(state in backing services), and treat logs as event streams (platform aggregates
them). The platform enforces this through the deployment contract — applications
that violate it create operational complexity that the platform team ultimately
absorbs.

For the twelve-factor model in the context of service design, see `be-service-architecture`.

---

## Cross-Hub References

### DevOps → Backend Engineering

| When this topic comes up | Route to |
|--------------------------|----------|
| SLO design as a service contract | `be-service-architecture` (twelve-factor, observability architecture) |
| Auth/secrets at the application layer | `be-auth-patterns` |
| Secrets management in IaC, Vault, SOPS | `devops-infrastructure-as-code` |
| Application security (OWASP, threat modeling) | `be-security-posture` |
| Infrastructure security (network policy, IAM, supply chain) | `devops-infrastructure-as-code` |

### DevOps → Data Science

| When this topic comes up | Route to |
|--------------------------|----------|
| MLOps CI/CD pipelines | `devops-ci-cd` (treat as CI/CD variant) + `ds-ml-engineering` |
| Data infrastructure provisioning (Spark, data lake, warehouse) | `devops-infrastructure-as-code` + `ds-data-engineering` |
| ML model deployment and serving | `ds-ml-engineering` |

### DevOps → Frontend Engineering

| When this topic comes up | Route to |
|--------------------------|----------|
| Frontend build pipeline, CDN, asset optimization | `devops-ci-cd` (build pipeline) + `fe-performance` |
| Performance budgets enforced in CI | `devops-ci-cd` + `fe-performance` |
| Edge caching strategy | `fe-performance` |
