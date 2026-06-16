---
name: devops-infrastructure-as-code
description: >
  Terraform, Pulumi, CDK, and GitOps for enterprise SaaS. Specialist spoke in
  the lead-devops-engineer network. Use this skill whenever the conversation
  touches: Terraform, HCL, providers, resources, data sources, modules, state,
  remote state, S3 backend, DynamoDB lock, Terraform Cloud, workspaces, plan
  apply workflow, module design, module versioning, Terratest, Atlantis, drift
  detection, import, moved blocks, Pulumi, Pulumi automation API, AWS CDK, L1
  L2 L3 constructs, CDK Pipelines, GitOps, ArgoCD, Flux, App of Apps, sync
  policy, pull model, push model, secrets in IaC, Vault dynamic secrets, AWS
  Secrets Manager, SOPS, external-secrets-operator, sealed-secrets, age
  encryption, Terraform kubernetes provider, Helm provider, IaC for data
  infrastructure, data lake provisioning, Spark cluster IaC.
  Not for: Kubernetes resource design (Deployment, Service, Helm chart authoring)
  — route to devops-container-orchestration. Not for: secrets at the application
  auth layer — route to be-auth-patterns.
---

# DevOps: Infrastructure as Code

Specialist lens for Terraform, Pulumi, CDK, secrets management in IaC, and
GitOps in enterprise SaaS. Part of the lead-devops-engineer skill network.

---

## Domain Boundary

This skill owns: **IaC authoring (Terraform, Pulumi, CDK), state management,
GitOps (ArgoCD, Flux), and secrets in IaC**.

- Application-layer auth secrets (JWT signing keys, OAuth credentials) → `be-auth-patterns`
- Kubernetes resource authoring (Deployments, Helm charts) → `devops-container-orchestration`
- CI pipeline for running `terraform plan/apply` → `devops-ci-cd` (Atlantis is covered here as the IaC-specific PR workflow)
- Data infrastructure specifics (Spark, data lake design) → `ds-data-engineering`

---

## Terraform Fundamentals

### HCL Syntax and Core Concepts

```hcl
# provider.tf — declare providers and their versions
terraform {
  required_version = ">= 1.6.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"    # allow 5.x, not 6.x
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.24"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

# main.tf — resources
resource "aws_s3_bucket" "artifacts" {
  bucket = "${var.environment}-${var.project}-artifacts"
  tags   = local.common_tags
}

# data sources — read existing infrastructure without managing it
data "aws_vpc" "main" {
  filter {
    name   = "tag:Environment"
    values = [var.environment]
  }
}

# locals — computed values
locals {
  common_tags = {
    Environment = var.environment
    Project     = var.project
    ManagedBy   = "terraform"
    Team        = var.team
  }
}

# outputs — expose values for consumption by other modules or humans
output "bucket_arn" {
  value       = aws_s3_bucket.artifacts.arn
  description = "ARN of the artifact storage bucket"
}
```

### State — Remote and Locking

```hcl
# backend.tf — remote state
terraform {
  backend "s3" {
    bucket         = "company-terraform-state"
    key            = "services/api-server/production/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-lock"    # prevents concurrent applies
  }
}
```

State isolation strategy:
- **Per-service, per-environment state files**: `services/api-server/production/terraform.tfstate`
- Prevents a failed apply in one service from locking others
- Enables per-team ownership: the API team owns `services/api-server/*`, not the entire state

State security: state files contain secrets in plaintext (database passwords, SSH keys).
Encrypt at rest (`encrypt = true`). Restrict access via IAM policies to CI/CD roles
and senior engineers only.

### Plan → Apply as a Deployment Gate

```bash
# In CI (Atlantis or manual):
terraform plan -out=tfplan -var-file=production.tfvars

# Review the plan output before applying.
# The plan shows: resources to add (+), change (~), or destroy (-)
# Destruction of production resources requires explicit confirmation or a separate workflow.

terraform apply tfplan
```

Never run `terraform apply` without a plan review on production. The plan is the diff —
review it like a PR. Auto-apply is acceptable for development environments only.

---

## Module Design

### Module Interface

```hcl
# modules/rds-postgres/variables.tf
variable "identifier" {
  description = "RDS instance identifier. Must be unique per region."
  type        = string
}

variable "instance_class" {
  description = "RDS instance type."
  type        = string
  default     = "db.t4g.medium"
}

variable "allocated_storage_gb" {
  description = "Initial storage in GB. Auto-scales up with storage_autoscaling_max_gb."
  type        = number
  default     = 20
}

variable "tags" {
  description = "Tags to apply to all resources."
  type        = map(string)
  default     = {}
}

# modules/rds-postgres/outputs.tf
output "endpoint" {
  description = "RDS endpoint for application connection strings."
  value       = aws_db_instance.this.endpoint
  sensitive   = false
}

output "secret_arn" {
  description = "ARN of the Secrets Manager secret containing credentials."
  value       = aws_secretsmanager_secret.rds_credentials.arn
}
```

Module interface rules:
- Every variable needs a description. Future readers (and Terraform Registry docs) depend on it.
- Use `sensitive = true` on output values that contain secrets — Terraform will redact them in plan output.
- Keep module interfaces stable. Changing a variable name is a breaking change for all callers.
- Version modules with Git tags. Callers pin to a version, not `main`.

### The DRY Trap

Modules reduce duplication when the abstraction is right. They add complexity when
the abstraction is premature or too generic.

Signs a module is wrong:
- The module has 40+ variables to cover every possible configuration
- Callers pass empty strings or `null` to disable features
- The module's `main.tf` is full of `count = var.enable_X ? 1 : 0` blocks

The fix: separate modules for distinct use cases rather than a single generic module
with too many knobs. Three focused modules are better than one that tries to do everything.

A "module" that is just a copy of the resource block with a thin wrapper is not worth
the abstraction overhead — inline it.

### Module Testing with Terratest

```go
// tests/rds_postgres_test.go
func TestRDSPostgresModule(t *testing.T) {
    t.Parallel()

    terraformOptions := &terraform.Options{
        TerraformDir: "../modules/rds-postgres",
        Vars: map[string]interface{}{
            "identifier":           "terratest-rds",
            "instance_class":       "db.t4g.micro",
            "allocated_storage_gb": 5,
            "tags": map[string]string{
                "Purpose": "terratest",
            },
        },
    }

    defer terraform.Destroy(t, terraformOptions)
    terraform.InitAndApply(t, terraformOptions)

    endpoint := terraform.Output(t, terraformOptions, "endpoint")
    assert.NotEmpty(t, endpoint)
}
```

Run Terratest against a dedicated test account (never production or staging).
Tests provision real infrastructure, validate outputs, then destroy. Slow but
catches IaC bugs before they reach production.

---

## Terraform at Scale

### Monorepo vs. Module Repos

| Approach | Pros | Cons |
|----------|------|------|
| Monorepo (all IaC in one repo) | Single PR for cross-module changes, unified CI | State isolation more complex to implement, single blast radius if CI breaks |
| Module repos (separate repo per module) | Clean versioning, independent CI | Cross-module changes require multiple PRs, dependency management overhead |
| Hybrid (monorepo for service configs, separate repo for shared modules) | Best of both | Two conventions to maintain |

Recommendation for teams < 50 engineers: monorepo with state isolation by path.
Above 50 engineers or with multiple teams owning infrastructure: hybrid.

### Atlantis — PR-Based Apply Workflow

Atlantis runs `terraform plan` on every PR touching IaC files and posts the plan as
a PR comment. Merge triggers `terraform apply`.

```yaml
# atlantis.yaml (repo root)
version: 3
projects:
  - name: api-server-production
    dir: infrastructure/services/api-server
    workspace: production
    terraform_version: 1.6.0
    autoplan:
      when_modified: ["*.tf", "*.tfvars"]
      enabled: true
    apply_requirements:
      - approved     # require PR approval before applying
      - mergeable    # PR must pass all status checks
```

Atlantis gives IaC the same PR review culture as application code. No more "someone
ran apply manually and it worked, we don't know what changed."

### Drift Detection

Drift = difference between IaC state and actual infrastructure. Causes: manual
console changes, external automation modifying resources, provider bugs.

Detection options:
- **Atlantis**: `atlantis plan` on a schedule detects drift (differences appear as plan output)
- **Driftctl**: dedicated drift detection tool; produces a JSON report of drifted resources
- **Terraform Cloud**: built-in drift detection with notifications

When drift is detected: create a PR to fix it. Never `terraform apply` to override
production drift without review — the drift may be intentional (a hotfix that hasn't
been codified yet).

### Import and Moved Blocks

```hcl
# Import existing resource into Terraform state (Terraform 1.5+)
import {
  to = aws_s3_bucket.legacy_artifacts
  id = "legacy-artifacts-bucket-name"
}

# Moved block — refactor without destroying and recreating
# (Rename a resource or move it into a module)
moved {
  from = aws_s3_bucket.artifacts
  to   = module.storage.aws_s3_bucket.artifacts
}
```

`moved` blocks are the safe way to refactor Terraform code. Without a `moved` block,
renaming a resource deletes the old one and creates a new one — destroying production
infrastructure. With a `moved` block, Terraform updates the state reference only.

---

## Pulumi

### The Case for Imperative IaC

Pulumi expresses infrastructure in real programming languages (TypeScript, Python, Go).
This unlocks:
- **Real loops**: provision 10 S3 buckets with a `for` loop, not Terraform's `count`/`for_each`
- **Conditionals**: full language conditionals, not HCL's limited `condition ? a : b`
- **Test frameworks**: Jest, pytest, Go test — test infrastructure like code
- **Libraries**: import NPM/PyPI packages directly in IaC code

```typescript
// pulumi/index.ts
import * as aws from "@pulumi/aws";

const tenants = ["acme", "globex", "initech"];

// Real loop — no Terraform for_each workarounds
const buckets = tenants.map(tenant => new aws.s3.Bucket(`${tenant}-data`, {
  bucket: `company-${tenant}-data`,
  tags: { Tenant: tenant, ManagedBy: "pulumi" },
  serverSideEncryptionConfiguration: {
    rule: {
      applyServerSideEncryptionByDefault: {
        sseAlgorithm: "aws:kms",
      },
    },
  },
}));
```

### Pulumi vs. Terraform Decision Matrix

| Factor | Favor Terraform | Favor Pulumi |
|--------|-----------------|-------------|
| Team language | Team knows HCL or prefers declarative | Team is strong in TypeScript/Python/Go |
| Existing state | Large existing Terraform codebase | Greenfield or willing to migrate |
| Testing | Terratest is acceptable | Want native language test frameworks |
| Provider coverage | Need a provider Terraform has and Pulumi doesn't (rare) | Need Pulumi Automation API for programmatic infra |
| Community patterns | Lots of existing Terraform modules to reference | Building custom abstractions |

### Pulumi Automation API

The Automation API allows embedding Pulumi inside application code — infrastructure
as a function call:

```python
# Provision a tenant environment programmatically from the SaaS application
from pulumi import automation as auto

async def provision_tenant(tenant_id: str):
    stack = await auto.create_or_select_stack_async(
        stack_name=f"tenant-{tenant_id}",
        work_dir="./infrastructure",
        opts=auto.LocalWorkspaceOptions(
            env_vars={"TENANT_ID": tenant_id}
        )
    )
    result = await stack.up_async()
    return result.outputs["namespace"].value
```

Use case: SaaS products that provision infrastructure per customer (dedicated k8s
namespace, database schema, S3 prefix) as part of onboarding. Replaces manual
provisioning scripts with version-controlled, tested IaC.

---

## AWS CDK

### Construct Levels

| Level | What it is | Use for |
|-------|-----------|---------|
| L1 (CfnXxx) | Direct CloudFormation resource mapping | When you need a property that L2 doesn't expose |
| L2 | High-level abstraction with sane defaults | Most resources — ECS, RDS, Lambda, S3, VPC |
| L3 (Patterns) | Multi-resource patterns | Common architectures: `ApplicationLoadBalancedFargateService`, `ServerlessRestApi` |

```typescript
// L2: Fargate service with sane defaults
const service = new ecs_patterns.ApplicationLoadBalancedFargateService(this, "ApiService", {
  cluster,
  taskImageOptions: {
    image: ecs.ContainerImage.fromEcrRepository(repo, imageTag),
    environment: { NODE_ENV: "production" },
    secrets: {
      DATABASE_URL: ecs.Secret.fromSecretsManager(dbSecret, "url"),
    },
  },
  desiredCount: 3,
  cpu: 512,
  memoryLimitMiB: 1024,
  publicLoadBalancer: true,
});
```

### CDK Pipelines — Self-Mutating Pipelines

CDK Pipelines create a pipeline that updates itself when the CDK app changes:

```typescript
const pipeline = new pipelines.CodePipeline(this, "Pipeline", {
  synth: new pipelines.ShellStep("Synth", {
    input: pipelines.CodePipelineSource.gitHub("org/repo", "main"),
    commands: ["npm ci", "npm run build", "npx cdk synth"],
  }),
});

pipeline.addStage(new AppStage(this, "Staging", { env: stagingEnv }));
pipeline.addStage(new AppStage(this, "Production", { env: prodEnv }), {
  pre: [new pipelines.ManualApprovalStep("PromoteToProduction")],
});
```

When to use CDK over Terraform: AWS-specific workload, team is TypeScript or Python,
you want the L2/L3 abstraction level, or you're already using CDK Pipelines for
a self-mutating deployment pattern. CDK is harder to test cross-cloud.

---

## Secrets in IaC

### The Core Rule

**Never store secrets in Terraform state.** Terraform state is not a secrets manager.
State files are stored in S3/GCS and accessible to everyone with state access — which
includes CI/CD. Use secrets management services and reference them by ARN/path.

### Patterns

**AWS Secrets Manager with rotation:**
```hcl
resource "aws_secretsmanager_secret" "db_password" {
  name = "/${var.environment}/api-server/db-password"
  recovery_window_in_days = 7
}

# Application reads the secret at runtime, not from Terraform output
# Terraform only creates the secret and rotation configuration
resource "aws_secretsmanager_secret_rotation" "db_password" {
  secret_id           = aws_secretsmanager_secret.db_password.id
  rotation_lambda_arn = module.rotation_lambda.arn
  rotation_rules {
    automatically_after_days = 30
  }
}
```

**SOPS for encrypted secrets in Git:**
```bash
# Encrypt secrets file with AWS KMS key before committing
sops --encrypt --kms arn:aws:kms:us-east-1:123456789:key/abc-123 \
  secrets.yaml > secrets.enc.yaml

# Decrypt at apply time in CI (CI role has KMS decrypt permission)
sops --decrypt secrets.enc.yaml > secrets.yaml
terraform apply -var-file=secrets.yaml
```

SOPS allows secrets to live in Git (encrypted) without a separate secrets server.
The KMS key controls access. Appropriate for bootstrapping infrastructure where
Vault/Secrets Manager isn't available yet.

**Vault dynamic secrets (the strongest pattern):**
```hcl
# Vault issues short-lived database credentials on demand
# Application requests creds at startup; Vault issues and auto-rotates them
resource "vault_database_secret_backend_role" "api_server" {
  name    = "api-server"
  backend = vault_mount.db.path
  db_name = vault_database_secret_backend_connection.postgres.name

  creation_statements = [
    "CREATE ROLE \"{{name}}\" WITH LOGIN PASSWORD '{{password}}' VALID UNTIL '{{expiration}}'",
    "GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA public TO \"{{name}}\"",
  ]
  default_ttl = "1h"
  max_ttl     = "24h"
}
```

Dynamic secrets mean no long-lived database passwords. Every application instance
gets unique, short-lived credentials. A leaked credential expires in 1 hour.

---

## GitOps

### ArgoCD — Application Model

ArgoCD reconciles a Git repository with cluster state continuously:

```yaml
# argocd-app.yaml — the ArgoCD Application resource
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: api-server-production
  namespace: argocd
spec:
  project: production
  source:
    repoURL: https://github.com/example/k8s-manifests
    targetRevision: main
    path: services/api-server/production
  destination:
    server: https://kubernetes.default.svc
    namespace: api-server
  syncPolicy:
    automated:
      prune: true       # delete resources removed from Git
      selfHeal: true    # revert manual kubectl changes
    syncOptions:
      - CreateNamespace=true
```

### App of Apps Pattern

A parent Application manages child Applications, allowing entire environments to be
bootstrapped from a single manifest:

```yaml
# apps/production/kustomization.yaml defines all services
# A single ArgoCD Application points to this directory
# ArgoCD discovers and manages all service Applications from it
```

### Flux as an Alternative

Flux takes a more "GitOps primitives" approach vs. ArgoCD's richer UI:
- Flux: two controllers (`source-controller`, `kustomize-controller`). Simple, scriptable.
- ArgoCD: more features (sync waves, resource hooks, health assessment), better UI for
  visualizing application state.

For teams that want UI visibility and multi-cluster management: ArgoCD.
For teams that prefer pure k8s-native controllers: Flux.

### The IaC / GitOps Boundary

**IaC provisions the cluster.** GitOps manages the workloads running on the cluster.

```
Terraform/Pulumi/CDK:
  - VPC, subnets, node groups
  - EKS/GKE/AKS cluster
  - IAM roles
  - RDS, ElastiCache, S3
  - ArgoCD installation (the bootstrap)

ArgoCD/Flux:
  - All application Deployments, Services, Ingresses
  - Namespace configuration
  - RBAC for application teams
  - ConfigMaps and (ESO-managed) Secrets for apps
```

Never manage application Deployments with Terraform. The Terraform state cycle (plan/apply)
is too slow for application deployments. Use GitOps for that layer.

---

## Cross-Spoke Routing

| Topic | Route To |
|-------|----------|
| Kubernetes resource authoring (Deployment, Service) | `devops-container-orchestration` |
| Helm chart authoring | `devops-container-orchestration` |
| CI pipeline running Terraform | `devops-ci-cd` (Atlantis is here) |
| Auth secrets at application layer | `be-auth-patterns` |
| Data infrastructure specifics | `ds-data-engineering` |
| MLOps infrastructure | `ds-ml-engineering` |
| IaC cost (Reserved Instances, spot, right-sizing) | `devops-cost-optimization` |
