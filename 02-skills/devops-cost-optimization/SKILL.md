---
name: devops-cost-optimization
description: >
  Cloud cost management and FinOps for enterprise SaaS. Specialist spoke in the
  lead-devops-engineer network. Use this skill whenever the conversation touches:
  FinOps, FinOps Foundation, Inform Optimize Operate, unit economics, cost per
  customer, cost per request, showback, chargeback, cost attribution, tagging
  strategy, AWS Config tag enforcement, GCP Organization Policy, Reserved
  Instances, Savings Plans, Spot instances, preemptible instances, On-Demand,
  Compute Optimizer, S3 storage tiers, Intelligent-Tiering, lifecycle policies,
  data transfer costs, egress costs, RDS vs Aurora, Kubernetes cost optimization,
  right-sizing, Goldilocks, VPA recommendations, spot node pools, cluster
  autoscaler, Descheduler, bin-packing, Kubecost, OpenCost, namespace cost
  attribution, Prometheus cardinality, metric retention, log sampling, trace
  sampling as cost control, AWS Cost Anomaly Detection, GCP Budget Alerts,
  Slack cost alerts, daily spend delta, weekly cost review, GitHub Actions cost,
  self-hosted runner economics, cache hit rate, CI build minutes.
  Not for: general Kubernetes resource design — route to
  devops-container-orchestration. Not for: sampling strategy for observability
  accuracy (vs. cost) — start with devops-observability.
---

# DevOps: Cost Optimization

Specialist lens for cloud cost management and FinOps in enterprise SaaS. Part
of the lead-devops-engineer skill network.

---

## Domain Boundary

This skill owns: **FinOps framework, AWS/GCP/Azure cost levers, Kubernetes cost
optimization, observability cost management, cost anomaly detection, and CI/CD
spend economics**.

- Sampling strategy for observability accuracy → `devops-observability`; cost
  dimension of that decision → here
- Kubernetes resource requests and limits (correctness) → `devops-container-orchestration`;
  right-sizing those values for cost → here
- IaC for Reserved Instance purchases → `devops-infrastructure-as-code`

---

## FinOps Fundamentals

### The FinOps Foundation Framework

**Inform**: achieve visibility. Tag everything. Get a cost dashboard with
per-service, per-team attribution. Publish unit cost metrics. This phase is
often underestimated — organizations spend months getting tagging right.

**Optimize**: act on the visibility. Right-size compute. Move to reserved capacity.
Delete waste (orphaned volumes, idle load balancers, unused NAT gateways). Implement
lifecycle policies on storage.

**Operate**: embed cost into the engineering workflow. Cost in sprint reviews.
Weekly cost anomaly checks. Engineers own the cost of what they build.

The mistake is jumping to Optimize before Inform is complete. You cannot right-size
what you cannot attribute. Tagging is the prerequisite.

### Unit Economics

Unit economics translate infrastructure cost into business metrics:

```
Cost per customer (monthly):
  Total cloud spend / active customer count
  Target: defined by the gross margin model (typically < 20-30% of ARPU for SaaS)

Cost per API request:
  (Compute + DB + network costs for the API tier) / monthly request count
  Useful for: validating pricing models for usage-based billing

Cost per GB stored:
  (Storage costs across all tiers) / total GB under management
  Useful for: data products where storage is the primary cost driver
```

Build a Grafana dashboard with these unit metrics alongside cloud spend. When unit
costs increase while load stays flat, it signals waste or a cost regression. When
unit costs decrease as load increases, it signals the architecture is scaling efficiently.

### Showback vs. Chargeback

**Showback**: teams see their costs but are not charged internally. Lower friction,
builds cost awareness, appropriate when teams are early in their FinOps journey.

**Chargeback**: internal billing. Teams own a budget and are accountable for overruns.
Higher friction, requires accurate attribution, appropriate for mature organizations
with established unit economics.

Start with showback. Chargeback requires a high confidence that attribution is correct —
getting charged for another team's workload due to a tagging error destroys trust in
the system.

### Tagging Strategy

```
Mandatory tags (enforced via AWS Config or GCP Organization Policy):
  - Environment: production | staging | development
  - Service: api-server | worker | data-pipeline
  - Team: platform | backend | data
  - Project: PLM | analytics | shared-infra
  - CostCenter: optional but enables finance integration

Enforcement: AWS Config rule "required-tags" with notification or auto-remediation
  GCP: Organization Policy with tag bindings
  Azure: Azure Policy for required tags
```

**Tag enforcement via AWS Config:**
```hcl
resource "aws_config_config_rule" "required_tags" {
  name = "required-tags"
  source {
    owner             = "AWS"
    source_identifier = "REQUIRED_TAGS"
  }
  input_parameters = jsonencode({
    tag1Key   = "Environment"
    tag2Key   = "Service"
    tag3Key   = "Team"
  })
}
```

Untagged resources are invisible in cost attribution. A single large EC2 instance
without tags can distort per-team spend by 30%+. Enforce at resource creation time,
not retroactively.

---

## AWS Cost Levers

### Reserved Instances vs. Savings Plans vs. On-Demand vs. Spot

| Option | Commitment | Discount | Flexibility | Use for |
|--------|-----------|---------|------------|---------|
| On-Demand | None | 0% | Full | Unpredictable workloads, short-lived experiments |
| Reserved Instance (1-year, no upfront) | 1 year, specific instance type | 30-40% | Low (specific instance family + region) | Stable production compute you know you'll run for 1+ year |
| Reserved Instance (3-year, all upfront) | 3 years | 50-65% | Lowest | Core database instances, stable baseline |
| Savings Plans (Compute) | 1 or 3 years, spend commitment | 40-66% | High (any EC2 + Fargate + Lambda) | Better than RIs for most modern workloads — flexibility with similar savings |
| Savings Plans (EC2 Instance) | 1 or 3 years, specific family | Up to 72% | Medium (any size within instance family) | When you know the instance family but not the size |
| Spot | None | 60-90% | Preemption risk (2-min notice) | Stateless workers, batch jobs, dev environments, k8s spot node pools |

**Decision rule**: Compute Savings Plans over Reserved Instances for most workloads.
They cover EC2, Fargate, and Lambda, and allow you to change instance families without
penalty. Purchase based on baseline On-Demand spend, not peak.

**Spot purchasing strategy**:
- Only for stateless, interruptible workloads
- Use Spot Fleet with multiple instance types to reduce interruption probability
- Always handle SIGTERM gracefully (drain in-flight requests, checkpoint state)
- Blend: 60% on-demand (stable baseline) + 40% spot (burst capacity) for workers

### S3 Storage Tiers and Lifecycle Policies

```hcl
resource "aws_s3_bucket_lifecycle_configuration" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id

  rule {
    id     = "transition-to-ia"
    status = "Enabled"

    transition {
      days          = 30
      storage_class = "STANDARD_IA"    # 30 days → Infrequent Access (-46% cost)
    }

    transition {
      days          = 90
      storage_class = "GLACIER_IR"     # 90 days → Glacier Instant Retrieval (-68%)
    }

    transition {
      days          = 365
      storage_class = "DEEP_ARCHIVE"   # 1 year → Deep Archive (-95%)
    }

    expiration {
      days = 2555    # 7 years → delete (typical compliance retention)
    }
  }
}
```

**Intelligent-Tiering**: automatically moves objects between tiers based on access
patterns. Use for data where access patterns are unpredictable. Has a small monitoring
fee per object — only cost-effective for objects > 128KB.

**The hidden S3 cost**: requests. S3 charges per GET/PUT/LIST. A service that lists
objects on every request to check for new files is generating unnecessary cost. Use
SQS/SNS event notifications instead.

### Data Transfer Costs

Data transfer is the "hidden" cost that surprises teams:

| Transfer type | Cost (AWS us-east-1) |
|--------------|---------------------|
| Intra-AZ (same AZ) | Free |
| Cross-AZ (different AZ, same region) | ~$0.01/GB each direction |
| Cross-region | ~$0.02/GB |
| Internet egress | ~$0.09/GB (first 10TB/month) |
| CloudFront → Internet | ~$0.0085/GB (cheaper than direct egress) |

Cost optimization for data transfer:
- **Keep compute and data in the same AZ** where possible — use topology-aware service
  placement in k8s to keep pods and their backing storage co-located
- **Use CloudFront for user-facing content** — always cheaper than direct S3/EC2 egress
- **VPC endpoints** for S3 and DynamoDB — traffic stays in AWS network, avoids NAT gateway cost
- **NAT gateway cost** surprises teams: $0.045/GB processed + hourly fee per AZ.
  A service with high egress through a NAT gateway can easily generate $500+/month.
  Consider PrivateLink or direct internet gateway for egress-heavy workloads.

---

## Kubernetes Cost Optimization

### Right-Sizing with Goldilocks

Goldilocks runs VPA in recommendation mode and surfaces results in a dashboard:

```bash
kubectl label namespace production goldilocks.fairwinds.com/enabled=true
# Access dashboard: kubectl port-forward svc/goldilocks-dashboard 8080:80 -n goldilocks
```

Goldilocks shows per-workload VPA recommendations (Guaranteed, Burstable, BestEffort
QoS classes) alongside current requests. Run a right-sizing review monthly:
- Identify workloads where requests > 2× P95 actual usage → over-provisioned, reduce requests
- Identify workloads where requests < P50 actual usage → under-provisioned, increase requests
  (under-provisioning causes OOM kills and performance issues, not just cost)

### Spot/Preemptible Node Pools for Stateless Workloads

```hcl
# EKS: spot node group for stateless workers
resource "aws_eks_node_group" "workers_spot" {
  cluster_name    = aws_eks_cluster.main.name
  node_group_name = "workers-spot"
  node_role_arn   = aws_iam_role.node.arn
  subnet_ids      = var.private_subnet_ids

  capacity_type = "SPOT"

  instance_types = [
    "m6i.xlarge",
    "m6a.xlarge",
    "m5.xlarge",     # multiple instance types reduce interruption probability
    "m5a.xlarge",
  ]

  taint {
    key    = "workload"
    value  = "worker"
    effect = "NO_SCHEDULE"    # only pods with matching toleration land here
  }
}
```

Applications on spot nodes must handle SIGTERM gracefully. The 2-minute interruption
notice should trigger: stop accepting new work, finish current tasks, exit cleanly.

Spot savings: 60-90% over On-Demand for worker pools. For a $10,000/month worker fleet,
this is a $6,000–$9,000/month reduction for the same compute capacity.

### Cluster Autoscaler — Aggressive Downscaling

```yaml
# cluster-autoscaler deployment args (EKS)
- --scale-down-utilization-threshold=0.5   # scale down when node < 50% utilized (default 0.5)
- --scale-down-delay-after-add=5m          # wait 5m after scale-up before scale-down (default 10m)
- --scale-down-unneeded-time=5m            # node must be unneeded for 5m before removal (default 10m)
- --max-node-provision-time=15m
```

Idle nodes are pure waste. Aggressive scale-down settings (reduce delay times, lower
utilization threshold) save money at the cost of slightly slower scale-up on traffic
spikes. Use with HPA/KEDA to ensure scale-up happens before the node is needed.

### Descheduler — Pod Bin-Packing

Over time, pods may cluster on certain nodes after scaling events, leaving other nodes
underutilized. The Descheduler evicts and reschedules pods to improve bin-packing:

```yaml
apiVersion: policy/v1
kind: Policy
strategies:
  RemoveDuplicates:
    enabled: true
  LowNodeUtilization:
    enabled: true
    params:
      nodeResourceUtilizationThresholds:
        underUtilizationThresholds:
          cpu: 20
          memory: 20
        targetThresholds:
          cpu: 50
          memory: 50
```

Run the Descheduler as a CronJob (every 2-4 hours). It doesn't forcibly evict pods
that would violate PDBs — safe to run on production clusters.

### Kubecost / OpenCost

```yaml
# Install Kubecost via Helm
helm install kubecost cost-analyzer \
  --repo https://kubecost.github.io/cost-analyzer/ \
  --namespace kubecost
```

Kubecost provides:
- Cost per namespace, deployment, pod, label
- Idle capacity cost (reserved but unused resources)
- Efficiency scores (requests vs. actual usage ratio)
- Savings recommendations (right-sizing, spot migration)

OpenCost is the open-source CNCF project (Kubecost donated the core). Use OpenCost
for attribution if cost is a concern; pay for Kubecost if you want the governance
features (RBAC per team, alerts, budget enforcement).

---

## Observability Cost Management

### Prometheus Cardinality

The most common source of runaway Prometheus cost is cardinality explosion.

```
Cardinality = number of unique time series
= product of unique values for each label

Example: http_requests_total{method, status, path}
  10 methods × 10 statuses × 500 paths = 50,000 time series   ← manageable

Example after bad decision: http_requests_total{method, status, path, user_id}
  10 × 10 × 500 × 100,000 users = 5,000,000,000 time series  ← OOM
```

**Rules**:
- Never use user IDs, session IDs, request IDs, or UUIDs as label values
- Keep cardinality per metric below ~10,000 time series
- Use `topk` for high-cardinality dimensions (show top 10 paths, not all 500)

Tools for cardinality analysis:
```promql
# Find metrics with the most series
topk(10, count by (__name__)({__name__=~".+"}))

# Count series for a specific metric
count(http_requests_total)
```

### Metric Retention Tiering

```yaml
# Prometheus local retention: short (hot data for dashboards and alerts)
--storage.tsdb.retention.time=15d
--storage.tsdb.retention.size=50GB

# Remote write high-resolution data: 90 days (for incident investigation)
# Remote write 5-minute downsampled data: 1 year (for trend analysis and SLO reporting)

# Thanos sidecar handles downsampling and long-term object storage:
compact:
  downsampling:
    disable: false
  retentionResolutionRaw: 90d      # raw data (15-second scrape interval)
  retentionResolution5m: 180d      # 5-minute downsampled
  retentionResolution1h: 365d      # 1-hour downsampled
```

### Log Sampling

High-volume DEBUG and INFO logs at 100% are the largest log cost driver.

```yaml
# OTel Collector: probabilistic sampling for high-volume log streams
processors:
  probabilistic_sampler:
    hash_seed: 22
    sampling_percentage: 10    # sample 10% of logs matching this filter
```

Structured sampling strategy:
- `error` logs: 100% always (you cannot miss errors)
- `warn` logs: 100% always
- `info` logs: 100% for key business events (order created, payment processed), 10% for routine operations
- `debug` logs: 0% in production by default; 1-5% via feature flag for targeted investigation

This alone typically reduces log volume by 60-80% for high-traffic services.

---

## Cost Anomaly Detection

### AWS Cost Anomaly Detection

```hcl
resource "aws_ce_anomaly_monitor" "main" {
  name              = "master-anomaly-monitor"
  monitor_type      = "DIMENSIONAL"
  monitor_dimension = "SERVICE"
}

resource "aws_ce_anomaly_subscription" "daily_alert" {
  name      = "daily-cost-anomaly-alert"
  monitor_arn_list = [aws_ce_anomaly_monitor.main.arn]
  threshold_expression {
    and {
      dimension {
        key           = "ANOMALY_TOTAL_IMPACT_ABSOLUTE"
        values        = ["100"]    # alert on anomalies > $100
        match_options = ["GREATER_THAN_OR_EQUAL"]
      }
    }
  }
  frequency = "DAILY"
  subscriber {
    address = "aws-cost-alerts@company.com"
    type    = "EMAIL"
  }
}
```

### Daily Spend Delta Alerting

A Slack alert when today's spend deviates significantly from the 7-day average:

```python
# Lambda function (runs nightly):
import boto3

def check_cost_delta():
    ce = boto3.client('ce')
    response = ce.get_cost_and_usage(
        TimePeriod={"Start": "2025-03-08", "End": "2025-03-15"},
        Granularity="DAILY",
        Metrics=["BlendedCost"]
    )
    
    costs = [float(r["Total"]["BlendedCost"]["Amount"])
             for r in response["ResultsByTime"]]
    
    avg_7d = sum(costs[:-1]) / len(costs[:-1])
    today = costs[-1]
    delta_pct = (today - avg_7d) / avg_7d * 100
    
    if abs(delta_pct) > 20:   # alert on > 20% deviation
        post_to_slack(f"Cost anomaly: today ${today:.2f} vs. 7-day avg ${avg_7d:.2f} ({delta_pct:+.1f}%)")
```

### Weekly Cost Review Ritual

What to look at in a weekly 30-minute review:

1. **Total spend vs. prior week** — is the trend flat, growing, shrinking?
2. **Per-service spend** — which service had the biggest week-over-week increase?
3. **Idle/waste** — orphaned volumes (EBS snapshots, unattached EBS), stopped EC2 instances,
   idle load balancers, old AMIs taking up snapshot storage
4. **Reserved/Savings Plan coverage** — what % of On-Demand spend is covered?
   Coverage below 60% means savings are being left on the table.
5. **Data transfer** — any spike in egress cost? Cross-AZ traffic increase?
6. **Spot interruption rate** — are workers losing too many spot instances?

A cost regression looks like: a service's per-request cost increases while request
volume stays flat. This signals: a new code path hitting an expensive dependency
more often, a query becoming less efficient, a caching layer failing, or a new
background job that wasn't accounted for.

---

## Build/CI Cost

### GitHub Actions Minute Economics

| Runner type | Cost per minute (2024) |
|-------------|----------------------|
| ubuntu-latest (2-core) | $0.008 |
| ubuntu-latest-4-core | $0.016 |
| macos-latest (3-core) | $0.08 |
| windows-latest (2-core) | $0.016 |

macOS runners cost 10× more than Linux. Every job that runs on macOS by default
is 10× more expensive. Audit macOS-required jobs — often tests that were written
for macOS but don't require it.

### Self-Hosted Runner Economics

Break-even analysis:

```
GitHub-hosted cost:
  50 developers × 20 PRs/day × 15 min CI × $0.008/min = $1,200/month

Self-hosted cost:
  4 × c5.2xlarge (8 vCPU, 16GB) spot instances
  = 4 × $0.10/hr × 730 hr/month = $292/month
  + runner management time: ~4 hours/month at $150/hr = $600/month
  Total: ~$892/month

Savings: ~$300/month at this scale — marginal.
Break-even is around 100+ developers or 30+ min average build time.
```

Self-hosted runners become economically compelling when:
- Build times are long (30+ minutes) — you need high-memory or fast-I/O machines
- You have high build volume (1,000+ minutes/day consistently)
- You need private VPC access regardless of cost

### Caching ROI

```
Cache ROI = cache hit rate × average cache save time × number of builds/month × cost per minute

Example:
  Cache hit rate: 80%
  Average install time saved: 3 minutes
  Builds per month: 2,000
  Cost per minute: $0.008

  ROI = 0.80 × 3 min × 2,000 × $0.008 = $38.40/month saved
```

A well-tuned cache with 80%+ hit rate saves 2-3 minutes per build. At scale, this
is significant. Track cache hit rate in CI metrics — a dropping hit rate (from cache
key drift or cache eviction) means the caching investment is eroding.

### Parallelism Cost Analysis

More parallelism = shorter wall time + more total minutes consumed:

```
Sequential: 20 min × 1 runner = 20 minutes consumed
4-way parallel: 6 min × 4 runners = 24 minutes consumed (20% more expensive, 70% faster)
8-way parallel: 4 min × 8 runners = 32 minutes consumed (60% more expensive, 80% faster)
```

The right answer depends on the cost of developer waiting time vs. the cost of
extra CI minutes. For most teams, the developer time cost far exceeds the CI minute
cost — err toward more parallelism.

---

## Cross-Spoke Routing

| Topic | Route To |
|-------|----------|
| Kubernetes resource requests (correctness) | `devops-container-orchestration` |
| Spot node pool configuration | `devops-container-orchestration` |
| Observability sampling (accuracy vs. cost) | `devops-observability` |
| IaC for Reserved Instance / Savings Plan purchases | `devops-infrastructure-as-code` |
| CI pipeline design (parallelism, caching) | `devops-ci-cd` |
