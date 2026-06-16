---
name: devops-container-orchestration
description: >
  Kubernetes and service mesh for enterprise SaaS. Specialist spoke in the
  lead-devops-engineer network. Use this skill whenever the conversation touches:
  Kubernetes, k8s, Pod, ReplicaSet, Deployment, StatefulSet, DaemonSet, Service,
  Ingress, Gateway API, ConfigMap, Secret, external-secrets-operator, resource
  requests, resource limits, CPU throttling, VPA, Vertical Pod Autoscaler, HPA,
  Horizontal Pod Autoscaler, KEDA, Pod Disruption Budget, PDB, Helm, Helm chart,
  values.yaml, Helmfile, Kustomize, base overlay, strategic merge patch,
  Istio, Envoy, VirtualService, DestinationRule, PeerAuthentication, mTLS,
  Linkerd, service mesh, traffic management, weighted routing, distributed
  tracing from mesh, namespace isolation, NetworkPolicy, ResourceQuota, RBAC in
  k8s, pod security standards, image pull policy, node pool design,
  PodTopologySpread, cluster autoscaler, etcd backup, node drain, cordon.
  Not for: CI/CD pipeline design — route to devops-ci-cd. Not for: deployment
  strategies (blue-green, canary logic) — route to devops-release-engineering.
  Not for: Prometheus/metrics/SLO — route to devops-observability.
---

# DevOps: Container Orchestration

Specialist lens for Kubernetes and service mesh in enterprise SaaS. Part of the
lead-devops-engineer skill network.

---

## Domain Boundary

This skill owns: **Kubernetes resource design, Helm and Kustomize, service mesh
configuration, multi-tenancy in k8s, and cluster operations**.

- Deployment strategy selection (canary %, blue-green) → `devops-release-engineering`
- Prometheus and metrics from the mesh → `devops-observability`
- CI/CD pipeline that deploys to k8s → `devops-ci-cd`
- IaC that provisions the cluster → `devops-infrastructure-as-code`

---

## Kubernetes Core Model

### Workload Abstractions — When to Use Each

| Abstraction | Use when |
|-------------|---------|
| `Deployment` | Stateless services (APIs, workers). The default choice. Manages rolling updates, rollback, replica count. |
| `StatefulSet` | Stateful workloads requiring stable network identity and persistent storage: databases, message brokers, caches. Pods get stable hostnames (`pod-0`, `pod-1`). |
| `DaemonSet` | One pod per node, always. Log collectors (Fluent Bit), monitoring agents (node-exporter), network plugins. |
| `ReplicaSet` | Rarely used directly. Deployments manage ReplicaSets. Only reference directly if you need to inspect rollout history. |
| `Job` / `CronJob` | Batch workloads (data migrations, report generation) and scheduled tasks. |

### Service Types

```yaml
# ClusterIP (default): internal-only, stable DNS name
# Use for: service-to-service communication inside the cluster
apiVersion: v1
kind: Service
spec:
  type: ClusterIP
  selector:
    app: api-server
  ports:
    - port: 80
      targetPort: 8080

# LoadBalancer: external IP via cloud provider
# Use for: production ingress entry points (usually prefer Ingress over raw LoadBalancer)
spec:
  type: LoadBalancer

# ExternalName: CNAME alias for an external service
# Use for: routing traffic to external dependencies by internal DNS name
spec:
  type: ExternalName
  externalName: postgres.rds.amazonaws.com
```

### Ingress vs. Gateway API

**Ingress** is the current standard but shows its age: annotation-heavy, annotation
semantics vary by controller (nginx vs. ALB vs. Traefik), and the spec is too thin.

**Gateway API** (SIG-Network project, v1 stable as of k8s 1.28) is the successor:
- Separates concerns: `GatewayClass` (infrastructure) → `Gateway` (cluster operator) → `HTTPRoute` (app team)
- Role-based: app teams own `HTTPRoute`; platform team owns `Gateway`. Avoids annotation sprawl.
- First-class traffic-splitting: `HTTPRoute` has native weight-based routing without ingress controller-specific annotations.

**Adopt Gateway API** for new clusters. Migrate Ingress resources when it's practical — the existing nginx/ALB controllers are implementing Gateway API support.

### ConfigMap vs. Secret vs. External Secrets Operator

| Mechanism | Encrypted | Versioned | Use for |
|-----------|-----------|-----------|---------|
| `ConfigMap` | No | In Git | Non-sensitive config: feature flags, env-specific URLs, app settings |
| `Secret` | Base64 only (effectively no) | Sensitive if in Git | Only for k8s-internal secrets. Never put real secrets here if GitOps is used. |
| `external-secrets-operator` | Yes (in source) | Via source vault | Production secrets: DB passwords, API keys, TLS certs. Syncs from AWS Secrets Manager, GCP Secret Manager, HashiCorp Vault into k8s Secrets. |

The ESO pattern:
```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: database-credentials
spec:
  refreshInterval: 1h
  secretStoreRef:
    name: aws-secrets-manager
    kind: ClusterSecretStore
  target:
    name: database-credentials   # creates/updates this k8s Secret
  data:
    - secretKey: DATABASE_URL
      remoteRef:
        key: /prod/api/database-url
```

---

## Resource Management

### Requests vs. Limits — The Rules

**Requests**: what the pod is guaranteed. Used by the scheduler to select a node.
**Limits**: the maximum. CPU limits cause throttling; memory limits cause OOM kill.

Rules that are often violated:
1. **Always set requests.** Pods without requests are treated as BestEffort and
   evicted first under pressure. Unpredictable behavior in production.
2. **Set memory limits equal to (or slightly above) memory requests.** Memory is
   non-compressible. A pod that exceeds its memory limit is OOM-killed immediately.
   A pod with no memory limit can consume all node memory and crash the node.
3. **Be careful with CPU limits.** CPU is compressible — exceeding the limit causes
   throttling, not termination. But CPU limits can cause severe latency spikes in
   latency-sensitive services (the Linux CFS scheduler will throttle even during
   a burst that lasts microseconds). Consider omitting CPU limits for latency-
   sensitive services and relying on requests + Guaranteed QoS class instead.

```yaml
resources:
  requests:
    cpu: "250m"      # 0.25 cores guaranteed
    memory: "256Mi"  # 256MB guaranteed
  limits:
    cpu: "1000m"     # throttle above 1 core (consider omitting for API services)
    memory: "512Mi"  # OOM-kill above 512MB
```

QoS classes (determined by relationship between requests and limits):
- **Guaranteed**: requests == limits. Highest priority. Use for production API pods.
- **Burstable**: requests < limits. Middle priority. Use for background workers.
- **BestEffort**: no requests/limits. Evicted first. Never use in production.

### VPA vs. Manual Tuning

VPA (Vertical Pod Autoscaler) recommends resource values based on historical usage.
Use it in recommendation mode (not auto-update mode) for production:

```yaml
apiVersion: autoscaling.k8s.io/v1
kind: VerticalPodAutoscaler
metadata:
  name: api-server-vpa
spec:
  targetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-server
  updatePolicy:
    updateMode: "Off"    # recommendation-only; don't auto-update production pods
```

Check recommendations weekly. Apply via a PR to the deployment manifest. VPA in
`Auto` mode restarts pods to resize them — acceptable for batch workloads, disruptive
for stateless APIs.

**Goldilocks** (Fairwinds) runs VPA in recommendation mode across all namespaces and
surfaces recommendations in a dashboard. Use it for right-sizing exercises.

### HPA — Horizontal Pod Autoscaler

CPU-based HPA is the default. Custom-metrics HPA (via KEDA) is better for most
real-world workloads:

```yaml
# CPU-based HPA (simple, not always meaningful)
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: api-server
  minReplicas: 3
  maxReplicas: 20
  metrics:
    - type: Resource
      resource:
        name: cpu
        target:
          type: Utilization
          averageUtilization: 60
```

**KEDA** (Kubernetes Event-Driven Autoscaling): scales based on external metrics
(queue depth, HTTP request rate, custom Prometheus metrics). Better for:
- Worker pools: scale based on SQS queue depth or Kafka consumer lag
- API services: scale based on HTTP requests per second (from Prometheus)
- Batch jobs: scale to zero when there's no work, burst on demand

```yaml
apiVersion: keda.sh/v1alpha1
kind: ScaledObject
metadata:
  name: api-server-scaler
spec:
  scaleTargetRef:
    name: api-server
  minReplicaCount: 3
  maxReplicaCount: 50
  triggers:
    - type: prometheus
      metadata:
        serverAddress: http://prometheus:9090
        metricName: http_requests_per_second
        threshold: "100"
        query: sum(rate(http_requests_total{deployment="api-server"}[2m]))
```

### Pod Disruption Budgets

PDBs prevent too many pods from being unavailable simultaneously during voluntary
disruptions (node drain, rolling update, cluster upgrade):

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: api-server-pdb
spec:
  minAvailable: 2    # OR use maxUnavailable: 1
  selector:
    matchLabels:
      app: api-server
```

**Required for every production Deployment with more than 1 replica.** Without a PDB,
a node drain during a cluster upgrade can evict all pods of a service simultaneously.
Use `minAvailable: 2` for services that need at least 2 instances for availability.
Use `maxUnavailable: 1` for rolling update control.

---

## Helm

### Chart Structure

```
my-service/
├── Chart.yaml           # name, version, appVersion, dependencies
├── values.yaml          # defaults (safe, non-production values)
├── values-dev.yaml      # environment overlay (gitops: not in chart, in deploy repo)
├── templates/
│   ├── _helpers.tpl     # named templates and helpers
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── ingress.yaml
│   ├── hpa.yaml
│   ├── pdb.yaml
│   └── serviceaccount.yaml
└── tests/
    └── test-connection.yaml   # helm test hook
```

### Values Hierarchy

```yaml
# chart/values.yaml — safe defaults
replicaCount: 1
image:
  repository: ghcr.io/example/api
  tag: ""               # required at deploy time — no default
  pullPolicy: IfNotPresent
resources:
  requests:
    cpu: 100m
    memory: 128Mi
  limits:
    memory: 256Mi
autoscaling:
  enabled: false
```

Override at deploy time:
```bash
helm upgrade --install api-server ./chart \
  --set image.tag=$GIT_SHA \
  --set replicaCount=3 \
  -f values-production.yaml    # production-specific overrides
```

### Helm Hooks

Hooks run at specific lifecycle points. Common uses:

```yaml
# Pre-upgrade hook: run database migration before new pods start
annotations:
  "helm.sh/hook": pre-upgrade
  "helm.sh/hook-weight": "-5"    # lower weight runs first
  "helm.sh/hook-delete-policy": before-hook-creation,hook-succeeded
```

Hook ordering for a zero-downtime upgrade:
1. `pre-upgrade`: run migration (adds columns, never removes)
2. `upgrade`: rolling update to new pods (can read old and new schema)
3. `post-upgrade`: smoke test

### Helm vs. Kustomize Decision

| Use Helm when | Use Kustomize when |
|---------------|-------------------|
| Publishing a reusable chart (shared across teams or public) | Deploying internal services where the team controls the manifests |
| The chart has many configurable parameters requiring defaults | You want plain YAML that kubectl can read without rendering |
| You need hook lifecycle management | You want to patch manifests from an upstream source without forking |
| The chart already exists (don't rewrite in Kustomize) | You're overlaying small changes on a base (e.g., change image tag per env) |

The case against Helm: Helm templates are Go templates in YAML — difficult to debug,
error messages are often cryptic, and templating logic can become deeply nested.
If the chart is only deployed by one team, Kustomize is often simpler.

---

## Kustomize

### Base + Overlay Pattern

```
deploy/
├── base/
│   ├── kustomization.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   └── hpa.yaml
└── overlays/
    ├── development/
    │   ├── kustomization.yaml   # patches for dev
    │   └── replica-patch.yaml
    ├── staging/
    │   └── kustomization.yaml
    └── production/
        ├── kustomization.yaml   # patches for prod
        └── resource-patch.yaml
```

```yaml
# overlays/production/kustomization.yaml
apiVersion: kustomize.config.k8s.io/v1beta1
kind: Kustomization

resources:
  - ../../base

images:
  - name: ghcr.io/example/api
    newTag: abc1234    # image tag set per deploy

patches:
  - path: resource-patch.yaml   # strategic merge patch for production resources

replicas:
  - name: api-server
    count: 5
```

---

## Networking and Service Mesh

### Istio Architecture

- **Control plane** (`istiod`): manages configuration, certificate distribution, service discovery
- **Data plane**: Envoy sidecar injected into each pod (automatically via namespace label `istio-injection=enabled`)
- Sidecars intercept all inbound and outbound traffic — transparent to the application

### Traffic Management

```yaml
# VirtualService: routing rules applied to traffic entering a service
apiVersion: networking.istio.io/v1beta1
kind: VirtualService
metadata:
  name: api-server
spec:
  hosts:
    - api-server
  http:
    - match:
        - headers:
            x-canary:
              exact: "true"
      route:
        - destination:
            host: api-server
            subset: canary
    - route:
        - destination:
            host: api-server
            subset: stable
          weight: 95
        - destination:
            host: api-server
            subset: canary
          weight: 5    # 5% canary traffic

---
# DestinationRule: defines subsets and load balancing
apiVersion: networking.istio.io/v1beta1
kind: DestinationRule
metadata:
  name: api-server
spec:
  host: api-server
  trafficPolicy:
    connectionPool:
      tcp:
        maxConnections: 100
      http:
        http2MaxRequests: 1000
        pendingHttpRequests: 100
  subsets:
    - name: stable
      labels:
        version: stable
    - name: canary
      labels:
        version: canary
```

### mTLS Between Services

```yaml
# Enforce mTLS for all traffic in a namespace
apiVersion: security.istio.io/v1beta1
kind: PeerAuthentication
metadata:
  name: default
  namespace: production
spec:
  mtls:
    mode: STRICT    # STRICT: mTLS required. PERMISSIVE: mTLS optional (migration mode)
```

mTLS with Istio gives you: automatic certificate rotation, cryptographic service identity,
encrypted service-to-service traffic, and a foundation for zero-trust networking — all
without application code changes.

### Linkerd as a Simpler Alternative

Linkerd's value proposition over Istio: lighter resource footprint (~50MB per proxy
vs. ~100MB+ for Envoy), simpler control plane, faster proxy (written in Rust vs. C++).
Trade-offs: less traffic management capability (no weighted routing in the HTTP layer,
requires SMI or Gateway API for that), less mature ecosystem.

**Use Linkerd when**: you want mTLS, observability, and basic retries without the full
Istio control surface. **Use Istio when**: you need advanced traffic management (weighted
routing, fault injection, circuit breaking at the mesh layer), JWT validation at the proxy,
or the Envoy filter extension model.

---

## Multi-Tenancy Patterns

### Namespace-Based Isolation

```yaml
# One namespace per tenant (strong isolation, high namespace count)
# OR one namespace per environment per service tier (common for shared-platform SaaS)
# Enforce isolation with NetworkPolicy:

apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-cross-namespace
  namespace: tenant-acme
spec:
  podSelector: {}       # applies to all pods in namespace
  policyTypes:
    - Ingress
    - Egress
  ingress:
    - from:
        - namespaceSelector:
            matchLabels:
              kubernetes.io/metadata.name: tenant-acme   # only from own namespace
        - namespaceSelector:
            matchLabels:
              role: shared-services   # allow ingress from shared services (monitoring, ingress)
```

### Resource Quotas Per Namespace

```yaml
apiVersion: v1
kind: ResourceQuota
metadata:
  name: tenant-quota
  namespace: tenant-acme
spec:
  hard:
    requests.cpu: "4"
    requests.memory: 8Gi
    limits.cpu: "8"
    limits.memory: 16Gi
    count/pods: "50"
    count/services: "10"
```

### Pod Security Standards

```yaml
# Applied at namespace level via label:
kubectl label namespace production \
  pod-security.kubernetes.io/enforce=restricted \
  pod-security.kubernetes.io/audit=restricted \
  pod-security.kubernetes.io/warn=restricted

# restricted profile requires:
# - non-root user
# - read-only root filesystem (where possible)
# - dropped capabilities (at least ALL)
# - no privilege escalation
# - seccomp profile set
```

Use `restricted` for application namespaces. `baseline` for system namespaces where
you don't control the workloads. Never `privileged` for application workloads.

---

## Cluster Operations

### Node Pool Design

Separate node pools for different workload types:

| Pool | Instance type | Labels/Taints | For |
|------|--------------|---------------|-----|
| `system` | Small, stable | `kubernetes.io/role=system` | kube-system, cluster infra |
| `api` | CPU-optimized, on-demand | `workload=api` | Latency-sensitive API pods |
| `workers` | Memory-optimized, spot | `workload=worker:NoSchedule` | Background job processors |
| `gpu` | GPU instances | `nvidia.com/gpu:NoSchedule` | ML inference workloads |

Spot/preemptible for stateless workers cuts cost by 60-90%. Pair with PDB and
graceful shutdown (SIGTERM → drain in-flight requests → exit) to handle spot interruptions.

### Pod Topology Spread

Distribute pods across availability zones:

```yaml
topologySpreadConstraints:
  - maxSkew: 1                            # max imbalance between zones
    topologyKey: topology.kubernetes.io/zone
    whenUnsatisfiable: DoNotSchedule     # hard constraint; use ScheduleAnyway for soft
    labelSelector:
      matchLabels:
        app: api-server
```

Without this, the scheduler may place all pods in one AZ. A single AZ outage
takes down the service. Always set this for production Deployments.

### etcd Backup

etcd is the source of truth for all cluster state. Back it up:
- Frequency: every 30 minutes (or before every cluster upgrade)
- Retention: 7 days minimum
- Storage: separate from the cluster (S3, GCS) — a cluster-destroying event must not also destroy the backup
- Test restore quarterly: backup that has never been restored is a hypothesis, not a backup

---

## Cross-Spoke Routing

| Topic | Route To |
|-------|----------|
| Canary percentage, blue-green, Argo Rollouts | `devops-release-engineering` |
| Prometheus metrics from Istio | `devops-observability` |
| CI/CD pipeline deploying to k8s | `devops-ci-cd` |
| Terraform/Pulumi provisioning the cluster | `devops-infrastructure-as-code` |
| ArgoCD/Flux GitOps deploying to k8s | `devops-infrastructure-as-code` |
| Application secrets (auth tokens, API keys) | `be-auth-patterns` |
| Secrets in IaC, ESO configuration | `devops-infrastructure-as-code` |
| Cloud cost of k8s node pools | `devops-cost-optimization` |
