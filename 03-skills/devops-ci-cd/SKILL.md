---
name: devops-ci-cd
description: >
  CI/CD pipeline architecture, build systems, and deployment strategy for
  enterprise SaaS. Specialist spoke in the lead-devops-engineer network. Use
  this skill whenever the conversation touches: GitHub Actions, reusable
  workflows, workflow_call, composite actions, job matrices, concurrency groups,
  self-hosted runners, OIDC-based secrets, trunk-based development, GitFlow,
  merge queues, branch protection, artifact immutability, build once promote
  artifact, container registry, artifact promotion, dependency caching, Docker
  layer caching, BuildKit, test sharding, Playwright sharding, Jest sharding,
  fan-out fan-in, build time SLO, SAST, Semgrep, CodeQL, Snyk, Dependabot,
  Trivy, Grype, GitLeaks, secret scanning, SBOM, CycloneDX, Syft, shift-left,
  smoke tests, rollback triggers, environment protection rules, MLOps pipelines,
  frontend build pipeline, CDN publishing, performance budget enforcement in CI.
  Not for: deep deployment strategy (blue-green, canary, feature flags) — route
  to devops-release-engineering. Not for: Kubernetes resource design — route to
  devops-container-orchestration.
aliases: [devops-ci-cd]
tier: spoke
domain: engineering
hub: lead-devops-engineer
prerequisites: [lead-devops-engineer]
spec_version: "2.0"
governed_by: [sec-supply-chain]
---

# DevOps: CI/CD

Specialist lens for CI/CD pipeline architecture, build systems, and deployment
pipeline design in enterprise SaaS. Part of the lead-devops-engineer skill
network.

---

## Domain Boundary

This skill owns: **pipeline design, GitHub Actions depth, build optimization,
security scanning in CI, artifact management, and environment promotion chains**.

- Deep deployment strategies (blue-green, canary, Argo Rollouts) → `devops-release-engineering`
- Kubernetes mechanics for routing canary traffic → `devops-container-orchestration`
- ML model pipelines (MLOps) → `devops-ci-cd` for the pipeline pattern + `ds-ml-engineering` for ML specifics
- Frontend build pipeline and CDN → here for pipeline mechanics + `fe-performance` for perf budget enforcement

---

## Pipeline Architecture

### Trunk-Based Development vs. GitFlow

**Use trunk-based development.** GitFlow optimizes for release trains with long-lived
branches. Enterprise SaaS optimizes for frequent, safe deployment — which requires
short-lived branches that merge to trunk daily.

The case for trunk-based:
- Long-lived feature branches accumulate merge debt. The longer the branch lives,
  the more expensive the merge and the more likely the post-merge test failures.
- A main branch that is always deployable forces feature completeness discipline
  (use feature flags to decouple deployment from release).
- Metrics that matter (DORA: lead time for changes, deployment frequency) improve
  when the path from commit to production is short.

The case for GitFlow is limited to regulated environments with mandatory release
windows and audit requirements for every change set — and even then, only if the
release engineering team explicitly requires it.

### Branch Protection Strategy

Required settings for `main`/`master`:

```yaml
Branch protection rules:
  - Require pull request reviews: 1 minimum (2 for security-sensitive paths)
  - Require status checks to pass:
      - ci/lint
      - ci/test
      - ci/build
      - security/sast
      - security/dependency-scan
  - Require branches to be up to date before merging
  - Restrict force pushes: true
  - Require merge queue: true  # at scale, prevents simultaneous merges breaking CI
```

**Merge queues** (GitHub's merge queue feature) serialize PRs through CI before
merging. Prevents the scenario where two PRs each pass CI independently but break
each other when merged simultaneously. Use at teams of 10+ engineers or whenever
main is broken more than once/week.

### Build Artifact Immutability

**Build once. Promote the artifact.**

A container image built from commit `abc123` is the artifact. It goes to dev, staging,
and production — the same bits, same digest. Do not rebuild for each environment.

```
commit → build → publish to registry:sha → dev (immutable tag) → staging → production
                                          ↑
                              registry:latest is a lie at scale
                              tag by git sha or semantic version
```

**What changes between environments is configuration**, not the artifact. Config
is injected at deploy time via environment variables, ConfigMaps, or secrets — not
baked into the image.

Container registry patterns:
- **Single registry with environment namespacing**: `registry.example.com/prod/service:sha`
- **Promotion by tagging**: image is built → tagged `:dev` → testing passes → retag `:staging` → retag `:prod`. No rebuild.
- **Artifact registry per environment** (more isolation): build pushes to dev registry, promotion copies to staging and prod registries.

For npm packages, PyPI packages, or other artifacts: same principle. Publish once,
promote by reference. A staging environment that `npm publish`s its own version is
building twice.

---

## GitHub Actions Depth

### Workflow Structure

```yaml
# .github/workflows/ci.yml
name: CI

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: ${{ github.ref != 'refs/heads/main' }}
  # Cancel in-progress runs on PRs, never on main

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/setup-node   # composite action for shared setup
      - run: npm run lint

  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        shard: [1, 2, 3, 4]    # fan-out: 4 parallel test shards
    steps:
      - uses: actions/checkout@v4
      - uses: ./.github/actions/setup-node
      - run: npx jest --shard=${{ matrix.shard }}/4

  build:
    needs: [lint, test]         # fan-in: build only after lint + test pass
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build and push
        uses: ./.github/workflows/build-push.yml   # reusable workflow call
```

### Reusable Workflows (`workflow_call`)

Share pipeline logic across repos without copy-paste:

```yaml
# .github/workflows/build-push.yml — the reusable workflow
on:
  workflow_call:
    inputs:
      image-name:
        required: true
        type: string
      registry:
        required: false
        type: string
        default: ghcr.io
    secrets:
      # OIDC handles auth — no explicit secrets needed for cloud providers

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write
      id-token: write    # required for OIDC
    steps:
      - uses: actions/checkout@v4
      - name: Configure AWS credentials (OIDC)
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: arn:aws:iam::123456789:role/github-actions-ecr
          aws-region: us-east-1
      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          push: true
          tags: ${{ inputs.registry }}/${{ inputs.image-name }}:${{ github.sha }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

### OIDC-Based Secrets (No Long-Lived Credentials)

Never store AWS/GCP/Azure credentials as GitHub secrets. Use OIDC:

```yaml
# GitHub Actions requests a short-lived OIDC token
# AWS role trust policy allows the token if it comes from the right repo/branch

# AWS IAM trust policy:
{
  "Effect": "Allow",
  "Principal": { "Federated": "arn:aws:iam::123456789:oidc-provider/token.actions.githubusercontent.com" },
  "Action": "sts:AssumeRoleWithWebIdentity",
  "Condition": {
    "StringEquals": {
      "token.actions.githubusercontent.com:aud": "sts.amazonaws.com",
      "token.actions.githubusercontent.com:sub": "repo:your-org/your-repo:ref:refs/heads/main"
    }
  }
}
```

Benefits: credentials are scoped to a 15-minute token, never stored, automatically
rotated. No secret rotation maintenance. Auditable at the IAM level.

### Secrets vs. Variables vs. Environment Protection

| Mechanism | Encrypted at rest | Visible in logs | Scope | Use for |
|-----------|-------------------|-----------------|-------|---------|
| `secrets` | Yes | Never | Repo, org, environment | Credentials, tokens, API keys |
| `vars` | No | Yes | Repo, org, environment | Config values (non-secret) |
| Environment protection rules | N/A — gate mechanism | N/A | Per-environment | Prod deploys requiring approval |

**Environment protection rules** create approval gates for production:

```yaml
jobs:
  deploy-prod:
    environment: production    # triggers the approval gate defined in repo settings
    needs: [deploy-staging]
    steps:
      - run: ./scripts/deploy.sh production
```

Set `production` environment to require manual approval from a specific team before
the job runs. Combine with a 5-minute deployment freeze window for extra safety.

### Self-Hosted Runners vs. GitHub-Hosted

| | GitHub-hosted | Self-hosted |
|--|---------------|-------------|
| Cost | Per-minute billing | Fixed infra cost |
| Security | Ephemeral, isolated | Must harden (isolated VMs required) |
| Network access | Public internet | Can access private resources |
| Maintenance | None | Runner fleet management |
| Scale | Burst-capable | Limited by fleet size |

Use self-hosted when:
- You need access to private VPC resources (internal artifact registries, databases)
- GitHub-hosted minute cost exceeds self-hosted infrastructure cost (roughly > 5,000 minutes/month for large teams)
- You need specific hardware (GPU, ARM, high-memory)

Self-hosted security requirements: always use ephemeral runners (spin up per job, tear down after), never reuse runners across jobs, run in isolated VMs (not containers on shared hosts).

---

## Build Optimization

### Dependency Caching Strategy

Cache key design determines cache hit rate:

```yaml
- uses: actions/cache@v4
  with:
    path: ~/.npm
    key: ${{ runner.os }}-npm-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-npm-
      # Falls back to any npm cache if exact key misses
      # This prevents cold starts — partial cache is usually better than none
```

Cache key rules:
- Key must change when dependencies change: always hash the lockfile (`package-lock.json`, `yarn.lock`, `Pipfile.lock`, `go.sum`)
- Use `restore-keys` as a fallback — a partial cache avoids downloading the whole dependency tree
- Separate caches for separate build stages (install, build output) — don't cache build output in the same key as dependencies

### Docker Layer Caching

BuildKit with GitHub Actions cache backend:

```yaml
- uses: docker/setup-buildx-action@v3

- uses: docker/build-push-action@v5
  with:
    context: .
    cache-from: type=gha
    cache-to: type=gha,mode=max
    # mode=max: cache every layer, not just final image
```

Dockerfile layer ordering matters for cache efficiency:

```dockerfile
# GOOD: stable layers first, changing layers last
FROM node:20-alpine
WORKDIR /app

COPY package*.json ./         # ← changes only when deps change
RUN npm ci --only=production  # ← cached until package-lock.json changes

COPY . .                      # ← changes every commit — but deps are cached above
RUN npm run build
```

```dockerfile
# BAD: mixing stable and volatile layers
FROM node:20-alpine
WORKDIR /app
COPY . .                      # ← changes every commit, busts all downstream cache
RUN npm ci && npm run build   # ← reinstalls all deps every build
```

### Test Sharding

Parallelism cuts wall time without cutting coverage:

```yaml
# Jest
npx jest --shard=1/4   # run 25% of test suite, determined by file hash
npx jest --shard=2/4
npx jest --shard=3/4
npx jest --shard=4/4

# Playwright
npx playwright test --shard=1/4

# pytest
pytest tests/ --split-by-file -n auto   # via pytest-split
```

Combine with matrix strategy for automatic fan-out:
```yaml
strategy:
  matrix:
    shard: [1, 2, 3, 4]
steps:
  - run: npx jest --shard=${{ matrix.shard }}/4
```

### Build Time SLOs

"Fast enough" is defined, not assumed:

| Pipeline stage | Target (P95 wall time) |
|---------------|----------------------|
| Lint | < 2 minutes |
| Unit tests (sharded) | < 5 minutes |
| Build (Docker, with cache hit) | < 5 minutes |
| Integration tests | < 10 minutes |
| Total CI (lint → deploy to dev) | < 15 minutes |
| Total CD (staging → production) | < 30 minutes |

Measure actual P95 with GitHub Actions Insights or a custom metric exported to
your observability stack. A CI pipeline that takes 45 minutes is a product defect
that compounds across every PR merged. Track it as a leading indicator of
developer velocity.

---

## Deployment Pipeline Stages

The canonical pipeline for enterprise SaaS:

```
lint → unit tests → build → integration tests → security scan → publish → deploy dev
                                                                              ↓
                                                                    smoke test + health check
                                                                              ↓
                                                                 (promote artifact) → staging
                                                                              ↓
                                                                    smoke test + approval gate
                                                                              ↓
                                                                         production
                                                                              ↓
                                                                    smoke test + auto-rollback
```

### Environment Promotion Chain

```yaml
# dev: auto-deploy on every merge to main
deploy-dev:
  needs: [build]
  environment: development

# staging: auto-deploy after dev smoke tests pass
deploy-staging:
  needs: [smoke-test-dev]
  environment: staging

# production: requires approval
deploy-production:
  needs: [smoke-test-staging]
  environment: production   # approval gate configured in repo settings
```

### Smoke Tests Post-Deploy

Smoke tests run after each environment deploy. They test the deployed artifact
in the real environment — not mocks.

Minimum smoke test set:
- Health check endpoint returns 200
- Auth endpoint is reachable (not necessarily login, just 401/403 response)
- One critical read path returns expected shape (a product list, a user profile)
- One critical write path completes without error

**Auto-rollback trigger**: if smoke tests fail, redeploy the previous artifact
automatically. Never leave a broken deployment in place waiting for human intervention.

```yaml
smoke-test-production:
  needs: [deploy-production]
  steps:
    - run: ./scripts/smoke-test.sh production
    - if: failure()
      run: ./scripts/rollback.sh production ${{ env.PREVIOUS_SHA }}
```

---

## Security in CI (Shift-Left)

Run security gates in CI, not as post-deploy audits.

### SAST (Static Analysis Security Testing)

```yaml
- name: Semgrep
  uses: returntocorp/semgrep-action@v1
  with:
    config: >-
      p/default
      p/owasp-top-ten
      p/secrets

- name: CodeQL
  uses: github/codeql-action/analyze@v3
  # configured via .github/codeql/codeql-config.yml
```

SAST runs on every PR. Findings block merge for HIGH/CRITICAL severity.
LOW/MEDIUM creates a comment but does not block (reduces alert fatigue on
findings that require context to evaluate).

### Dependency Scanning

```yaml
# Dependabot (configured in .github/dependabot.yml) — automated PRs for outdated deps
# Snyk for deeper analysis:
- name: Snyk test
  run: npx snyk test --severity-threshold=high
  env:
    SNYK_TOKEN: ${{ secrets.SNYK_TOKEN }}
```

### Container Image Scanning

```yaml
- name: Scan image with Trivy
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: ${{ env.IMAGE_TAG }}
    format: sarif
    output: trivy-results.sarif
    severity: CRITICAL,HIGH
    exit-code: 1    # fail the pipeline on CRITICAL/HIGH
```

Block promotion to staging or production on any CRITICAL CVE in the container image.
Accept risk explicitly via an allowlist (`.trivyignore`) with a documented
justification and review date — not by setting `exit-code: 0`.

### Secret Scanning (GitLeaks)

```yaml
# As a pre-commit hook (developer workstation):
pre-commit install
# .pre-commit-config.yaml:
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks

# As a CI step (catches anything that slipped through):
- name: GitLeaks scan
  uses: gitleaks/gitleaks-action@v2
```

Both layers are required. Pre-commit catches secrets before they hit the remote.
CI catches anything committed without the pre-commit hook installed.

### SBOM Generation

```yaml
- name: Generate SBOM with Syft
  uses: anchore/sbom-action@v0
  with:
    image: ${{ env.IMAGE_TAG }}
    format: cyclonedx-json
    output-file: sbom.json

- name: Attest SBOM to image
  uses: actions/attest-sbom@v1
  with:
    subject-name: ${{ env.IMAGE_NAME }}
    subject-digest: ${{ env.IMAGE_DIGEST }}
    sbom-path: sbom.json
```

SBOM generation is required for SOC 2 and increasingly for enterprise procurement.
Attach the SBOM to the artifact, not just the build job. It must travel with the image.

---

## Cross-Spoke Routing

| Topic | Route To |
|-------|----------|
| Blue-green, canary, Argo Rollouts | `devops-release-engineering` |
| Feature flags | `devops-release-engineering` |
| Database migration in the pipeline | `devops-release-engineering` |
| Kubernetes deployment resource | `devops-container-orchestration` |
| Helm chart publishing to registry | here for publishing; `devops-container-orchestration` for chart design |
| SLO on CI build times | `devops-observability` |
| Terraform plan in CI | `devops-infrastructure-as-code` (Atlantis pattern) |
| Application security (OWASP, auth) | `be-security-posture` |
| MLOps pipeline specifics | `ds-ml-engineering` |
| Frontend performance budget in CI | `fe-performance` |

## Related
- hub → [[lead-devops-engineer]]
- governed-by → [[sec-supply-chain]]
