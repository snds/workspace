---
name: be-security-posture
description: >
  Security engineering for enterprise SaaS backend systems at staff/principal IC
  level. Use this skill whenever the conversation touches: threat modeling with
  STRIDE or PASTA methodology, OWASP Top 10 as applied to SaaS APIs, IDOR and
  horizontal privilege escalation, injection vulnerabilities (SQL, NoSQL, SSRF,
  template), secrets management (Vault, AWS Secrets Manager, GCP Secret Manager),
  secret rotation patterns, CI/CD secrets injection, secret scanning (GitLeaks,
  truffleHog), supply chain security (Snyk, Dependabot, SBOM, CycloneDX, SPDX),
  lock file integrity, security headers (CSP, HSTS, X-Frame-Options,
  Permissions-Policy), rate limiting strategy (token bucket, sliding window,
  fixed window), API key vs. OAuth token use-case selection, input validation at
  API boundary, response filtering as information disclosure mitigation, or
  SOC 2 Type II operational requirements as they apply to engineering decisions.
  Not for: authentication flow design (be-auth-patterns), infrastructure-level
  network security, or penetration testing methodology.
hub: lead-backend-engineer
aliases: [be-security-posture]
tier: spoke
domain: engineering
prerequisites: [lead-backend-engineer]
spec_version: "2.0"
---

# Be: Security Posture

Specialist lens for security engineering in enterprise SaaS backends. Part of the
backend engineering skill network. Staff/principal IC level — presumes familiarity
with security concepts, not a certification introduction.

---

## Domain Boundary

This skill owns: **threat modeling, OWASP Top 10 application to SaaS APIs, secrets
management, supply chain security, security headers, rate limiting, and SOC 2
operational requirements for engineering**.

- Authentication flows, JWT design, RBAC/ABAC → `be-auth-patterns`
- API endpoint design, input validation middleware placement → `be-api-design`
- Service mesh, network policy, infrastructure hardening → infrastructure concern
- Legal/compliance framework beyond SOC 2 → `a11y-legal-compliance`

---

## Threat Modeling

### STRIDE Applied to SaaS API Endpoints

STRIDE is a per-component threat enumeration. Work through it at the data flow
diagram level, not the feature level.

| Threat | What it means for a SaaS API | Example |
|--------|------------------------------|---------|
| **Spoofing** | Impersonating another user, tenant, or service | JWT signature bypass, API key theft, SSRF to internal metadata service |
| **Tampering** | Modifying data in transit or at rest | Parameter tampering, IDOR to update another tenant's record, log injection |
| **Repudiation** | Denying an action was taken | Missing audit log, mutable audit trail, no request ID correlation |
| **Information Disclosure** | Exposing data to unauthorized parties | Over-fetching in API responses, stack traces in error messages, PII in logs |
| **Denial of Service** | Making the service unavailable | Missing rate limiting, unbounded query parameters, expensive GraphQL queries |
| **Elevation of Privilege** | Gaining access beyond authorization | Missing function-level checks, JWT algorithm confusion, RBAC bypass via nested resource |

### STRIDE Threat Modeling Workflow

```
1. Draw the Data Flow Diagram
   - Identify all external entities (user, IdP, partner API, webhook consumer)
   - Identify all processes (API gateway, service, worker, background job)
   - Identify all data stores (primary DB, cache, object storage, audit log)
   - Draw data flows between them, labeled with protocols and data types

2. Identify Trust Boundaries
   - Where does data cross a trust boundary? (internet → API gateway,
     API service → internal DB, API service → third-party service)
   - Each trust boundary crossing is a candidate for threat entry

3. Apply STRIDE Per Component
   - For every process and data store in the DFD, enumerate applicable STRIDE
     threats
   - Focus on trust boundary crossings first — highest risk density

4. Rank Risks
   - DREAD (Damage, Reproducibility, Exploitability, Affected users, Discoverability)
     as a lightweight scoring model
   - Or CVSS base score if you need to align with a security team's tooling
   - Priority order: Critical → High → Medium, park Low for a backlog

5. Define Mitigations
   - For each threat ranked Critical or High: name the control, the owner,
     and the verification method (how you know the control works)
```

### PASTA — Process for Attack Simulation and Threat Analysis

PASTA is for architectural decisions, not feature-level tickets. Seven stages:

```
Stage 1: Define business objectives — what data, what SLAs, what compliance scope?
Stage 2: Define technical scope — what systems, APIs, third-party integrations?
Stage 3: Decompose application — DFD, trust boundaries, data classification
Stage 4: Analyze threats — threat actor profiles, TTPs (tactics, techniques, procedures)
Stage 5: Vulnerability analysis — map known CVEs and architecture weaknesses to the DFD
Stage 6: Attack modeling — model realistic attack scenarios, build attack trees
Stage 7: Risk and impact analysis — business impact, likelihood, prioritized residual risk
```

Use PASTA when: evaluating a new system architecture, assessing a potential acquisition's
security posture, or preparing for a SOC 2 Type II readiness assessment.

### When to Run Threat Modeling

| Trigger | Model Type | Scope |
|---------|-----------|-------|
| New feature in design phase | STRIDE | Feature DFD, 2-4 hours |
| New service or major refactor | STRIDE + PASTA elements | Service boundary, half-day |
| Post-incident review | STRIDE retrospective | Affected components |
| New architectural pattern (e.g., adding a message queue) | PASTA | Full system segment |
| Annual security review | PASTA | Full system |

Threat modeling is a design activity, not a pre-launch checkbox. The best time to
find threats is before the code exists.

### DFD Notation Basics

```
[ External Entity ]  — rectangle  — outside the system (user browser, IdP, partner)
( Process )          — circle     — transforms data (API handler, worker, ETL job)
=== Data Store ===   — parallel lines — persists data (DB table, cache, S3 bucket)
--->                 — arrow      — data flow, labeled with protocol + data type

Trust boundary: dashed rectangle enclosing components that share a trust level
```

---

## OWASP Top 10 for SaaS APIs

### A01 — Broken Access Control

The most critical category. In SaaS APIs:

**IDOR (Insecure Direct Object Reference)**: API accepts a resource ID directly
in the request and returns the resource without verifying the caller owns it.

```http
# Vulnerable: GET /api/orders/12345 returns order 12345 regardless of who asks
# Fix: every query must scope to the authenticated tenant/user

# Wrong
SELECT * FROM orders WHERE id = $1

# Right — tenant_id from the validated JWT, not from the request
SELECT * FROM orders WHERE id = $1 AND tenant_id = $2
```

**Horizontal privilege escalation**: User A can access User B's resources because
the API only checks authentication, not that A is authorized for B's data.

**Missing function-level authorization**: REST endpoints enforce object-level
access but not action-level. A user with read-only role can POST or DELETE
because the route handler doesn't check the role for write operations.

```typescript
// GraphQL-specific risk: field resolvers need authorization independently
// A query that resolves fine at the root may expose sensitive nested fields
// without field-level auth checks on the resolver
```

**RBAC vs. ABAC at the API layer**:
- RBAC: role membership gates endpoints. Simple, auditable, breaks down at row-level.
- ABAC: policy evaluations gate endpoints using subject + resource + environment
  attributes. Expressive, harder to audit ("what can this user do?").
- For SaaS: RBAC for function-level, attribute conditions for row-level. See `be-auth-patterns`.

### A02 — Cryptographic Failures

**Plaintext secrets in logs/responses**: Any log line that echoes request
parameters can capture API keys, tokens, or passwords if the field is not filtered.
PII in logs is also a cryptographic failure with GDPR implications.

**Weak hashing for passwords**: MD5 and SHA-1 are not password hashing algorithms.
Use bcrypt, scrypt, or Argon2id. bcrypt cost factor 12+ for new systems.

```python
# Wrong — SHA-256 is not a password hash
import hashlib
stored = hashlib.sha256(password.encode()).hexdigest()

# Right — bcrypt with work factor
import bcrypt
stored = bcrypt.hashpw(password.encode(), bcrypt.gensalt(rounds=12))
```

**Missing TLS validation**: Internal service-to-service calls that skip certificate
verification (`verify=False` in requests, `rejectUnauthorized: false` in Node)
defeat TLS entirely. CI environments where certs are self-signed do not justify
disabling verification in production code paths.

**Insecure token generation**: UUIDs are not cryptographically secure tokens.
Use OS CSPRNG for anything security-sensitive.

```python
import secrets
token = secrets.token_urlsafe(32)  # 256 bits — correct
```

### A03 — Injection

**SQL injection**: Parameterized queries are the only correct defense. ORMs
parameterize by default but raw query escape hatches (`raw()`, `$queryRaw`) bypass
this. String-interpolated SQL is never acceptable regardless of prior sanitization.

```typescript
// Vulnerable — even with 'safe' input
const result = await db.query(`SELECT * FROM users WHERE email = '${email}'`);

// Correct
const result = await db.query('SELECT * FROM users WHERE email = $1', [email]);
```

**NoSQL injection**: MongoDB query operators in user-supplied JSON. If a field
expects a string but receives `{"$gt": ""}`, the query semantics change.

```javascript
// Vulnerable
User.find({ email: req.body.email })  // body: {"email": {"$gt": ""}} → returns all users

// Fix: validate and sanitize input types before query construction
// Use a schema validator (Zod, Joi, ajv) at the API boundary
```

**SSRF (Server-Side Request Forgery)**: The API fetches a URL supplied by the
user. Attackers supply internal URLs (`http://169.254.169.254/latest/meta-data/`
for AWS IMDSv1, internal service hostnames, `file://` URIs).

```
SSRF mitigations:
1. Allowlist of permitted domains/IP ranges — deny everything else
2. Resolve the URL, check the resolved IP against an allowlist before fetching
3. Use IMDSv2 (token-required) on AWS — reduces SSRF impact on metadata endpoint
4. Network egress filtering at the infrastructure layer as defense-in-depth
```

**Template injection**: Dynamic content rendered via a template engine (Jinja2,
Handlebars, Pebble) where user input reaches the template context unsanitized.
`{{7*7}}` → `49` in output is the canary test.

### A04 — Insecure Design

Design-phase failures that cannot be fixed with code changes alone:

- **No threat model**: security assumptions weren't validated at design time
- **Missing rate limiting**: high-value endpoints (login, password reset, API)
  have no rate limit baked into the design
- **Over-permissive CORS**: CORS policy not considered at design time, defaults
  to `*` or echoes the `Origin` header without validation

### A05 — Security Misconfiguration

**Debug endpoints in production**: `/debug`, `/actuator`, `/metrics` without
authentication. Spring Boot Actuator endpoints, Prometheus `/metrics`, and
profiling endpoints are common culprits. All management endpoints require
authentication or network-level restriction.

**Default credentials**: Database users with default passwords, admin panels
with `admin/admin`, third-party integrations left on demo credentials.

**Overly permissive CORS headers**:

```http
# Wrong — reflects any origin, allows credentials
Access-Control-Allow-Origin: *
Access-Control-Allow-Credentials: true
# Note: browsers block credentials with wildcard origin, but this is still wrong

# Wrong — echoes request origin without validation
Access-Control-Allow-Origin: <Request.Origin>

# Right — explicit allowlist
Access-Control-Allow-Origin: https://app.example.com
Access-Control-Allow-Credentials: true
```

**Verbose error messages**: Stack traces, file paths, SQL query text, and
internal hostnames in HTTP error responses disclose system architecture to
attackers. Production error responses must be generic; detail goes to internal
logs only.

### A07 — Identification and Authentication Failures

**Session fixation**: Regenerate the session ID after successful authentication.
Failure to do so lets an attacker pre-set a session ID, then wait for a victim
to authenticate into it.

**JWT algorithm confusion**: The `alg: none` attack — an attacker strips the
signature and sets the algorithm to `none`, and a naive verifier accepts it.
Also the RS256 → HS256 confusion attack: if a server accepts both algorithms, an
attacker can use the public key as the HMAC secret.

```typescript
// Wrong — trusts the algorithm claim in the token header
jwt.verify(token, secret)

// Right — pin the expected algorithm explicitly
jwt.verify(token, secret, { algorithms: ['RS256'] })
```

**Insufficient token expiry**: Access tokens with 24-hour or longer lifetimes
greatly expand the window for compromised token abuse. 15 minutes for access
tokens, with refresh token rotation, is the correct enterprise baseline.

**Credential stuffing defense**: Rate limiting alone is insufficient because
credential stuffing distributes requests across IPs. Required controls:
- CAPTCHA or bot-detection on login
- MFA enforcement (TOTP or WebAuthn)
- Breach password detection (Have I Been Pwned API / k-anonymity model)
- Anomaly detection (login from new geography, device fingerprint mismatch)

### A09 — Security Logging and Monitoring Failures

**What to log** (every event must be structured JSON for SIEM ingestion):

```json
{
  "timestamp": "2026-04-28T14:23:00.000Z",   // ISO 8601 UTC
  "level": "INFO",
  "event_type": "auth.login.success",         // namespaced event type
  "actor_id": "user_abc123",
  "actor_type": "user",
  "tenant_id": "t_789",
  "ip_address": "1.2.3.4",
  "user_agent": "Mozilla/5.0...",
  "request_id": "req_xyz",                    // correlates to other log lines
  "session_id_hash": "sha256:abc..."          // hash, not plaintext
}
```

Required events: authentication success/failure, MFA events, password changes,
privilege changes (role assignment/removal), sensitive data access (exports,
PII queries), API key creation/revocation, configuration changes, data deletion.

**What NOT to log**: passwords (even wrong ones), session tokens, API keys,
credit card numbers, full SSNs, raw PII in query parameters. Log the hash of a
token for correlation; never the token itself.

**Structured logging for SIEM**: Every log line must be machine-parseable JSON.
Free-text messages are acceptable as a `message` field but the structured fields
must carry the queryable data. Ship logs to your SIEM (Splunk, Datadog, Elastic)
as they are written — batch shipping loses events on crash.

---

## Secrets Management

### The Rule

Secrets never appear in source control. Not in `.env` files, not in comments,
not in test fixtures, not in commit messages. Once in history, assume compromised.

### Environment Variables vs. Secrets Managers

| Approach | When to use | Risk |
|----------|------------|------|
| Environment variables (12-factor) | Development, simple deployments, values injected at runtime by platform | Secrets visible in process list, child processes inherit, accidental logging |
| Platform secrets (Heroku Config Vars, Fly.io secrets) | PaaS deployments where the platform manages injection | Vendor trust, limited rotation control |
| HashiCorp Vault | Self-managed infrastructure, dynamic secrets, audit trail requirement | Operational complexity, Vault availability is now a dependency |
| AWS Secrets Manager | AWS-native deployments | Cost per secret per month, IAM policy discipline required |
| GCP Secret Manager | GCP-native deployments | Same trade-offs as AWS |

**Preference order for enterprise SaaS**: cloud-native secrets manager (AWS/GCP)
for production, Vault for multi-cloud or on-prem requirements, environment
variables never in production for sensitive credentials.

### Zero-Downtime Secret Rotation

Rotating a secret without downtime requires a dual-read period:

```
Phase 1: Add new secret version alongside old
  - New secret version is written to secrets manager
  - Application is updated to read both old and new versions
  - Validation: application can authenticate with both

Phase 2: Switch primary to new secret
  - Update the downstream system (database password, API key, etc.) to the new value
  - Application now uses new version as primary
  - Old version retained as fallback during propagation

Phase 3: Remove old secret version (after propagation confirmed)
  - Confirm no requests are failing
  - Revoke old secret version
  - Remove fallback read path from application code
```

For database passwords: AWS Secrets Manager has native RDS rotation support that
handles the dual-read period automatically via Lambda rotation functions.

### CI/CD Secrets Injection

**GitHub Actions secrets**: Repository or organization secrets injected as
environment variables. Not visible in logs (masked). Avoid putting production
database credentials here; use OIDC instead.

```yaml
# OIDC-based role assumption — no static secrets in CI
- uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::123456789:role/github-actions-deploy
    aws-region: us-east-1
    # GitHub exchanges OIDC token for AWS credentials — no stored secret
```

OIDC is the correct pattern for CI/CD → cloud access. Static long-lived
credentials in CI secrets are a rotation and least-privilege problem.

### Secret Scanning

Run as pre-commit hook AND in CI:

```bash
# GitLeaks as pre-commit
gitleaks protect --staged --redact

# truffleHog in CI (scans git history, not just staged changes)
trufflehog git file://. --only-verified
```

GitLeaks rule sets cover AWS keys, GCP service account keys, GitHub tokens, Stripe
keys, and generic high-entropy strings. Add custom rules for your own API key
format patterns.

---

## Supply Chain Security

### Dependency Vulnerability Scanning

| Tool | Coverage | Integration |
|------|---------|-------------|
| Snyk | CVEs + license issues, container images | IDE plugin, CLI, CI, PR checks |
| Dependabot | CVEs + auto-PRs for upgrades | Native GitHub, zero-config |
| OWASP Dependency-Check | CVEs via NVD, Java/JS/Python | CI plugin, good for compliance reports |

Run at least one in CI as a blocking check. Dependabot alone is insufficient for
high-velocity teams because it doesn't block PRs that introduce new vulnerable
dependencies.

### SBOM — Software Bill of Materials

An SBOM is a machine-readable inventory of all components in your software.
Required by US executive order for software sold to federal government; increasingly
required in enterprise procurement.

**CycloneDX**: JSON/XML format, strong tool support, preferred for dynamic analysis.
**SPDX**: ISO standard (ISO/IEC 5962), preferred for license compliance.

```bash
# Generate CycloneDX SBOM for a Node project
npx @cyclonedx/cyclonedx-npm --output-format json --output-file sbom.json

# Generate SPDX SBOM
npx spdx-sbom-generator -p . -o sbom.spdx
```

Generate SBOM as part of the release pipeline, attach to the release artifact.
Store in a queryable registry (Dependency-Track) for continuous vulnerability
matching against new CVEs.

### Lock File Integrity

```bash
# Node — always npm ci in CI, never npm install
# npm ci: reads package-lock.json exactly, fails if lock is inconsistent
npm ci

# Cargo — Cargo.lock is committed for binaries, checked in CI
cargo build  # reads Cargo.lock

# Go — go.sum is the integrity hash file, committed and verified
go mod verify
```

**Known-bad version pinning**: when a vulnerability is discovered in a transitive
dependency you can't immediately update, pin to the last safe version in the lock
file and add a comment with the CVE reference and resolution target date. This is a
temporary control, not a solution.

### Private Registry Proxying

Proxying public registries (npm, PyPI, Maven Central) through an internal registry
(Artifactory, Nexus, AWS CodeArtifact) enables:
- Caching for reliability
- Allowlisting of approved packages
- Blocking malicious or typosquatted packages
- Automatic scanning before packages are available internally

---

## Security Headers

### Content-Security-Policy

CSP is the primary XSS mitigation layer in the browser. Construct it directive
by directive:

```
Content-Security-Policy:
  default-src 'none';              ← deny everything not explicitly allowed
  script-src 'self'                ← scripts from same origin only
    'nonce-{random-per-request}';  ← allow specific inline scripts via nonce
  style-src 'self' 'unsafe-inline'; ← unsafe-inline needed for most CSS-in-JS
  img-src 'self' data: https://cdn.example.com;
  font-src 'self' https://fonts.gstatic.com;
  connect-src 'self' https://api.example.com;
  frame-ancestors 'none';          ← blocks iframe embedding (replaces X-Frame-Options)
  base-uri 'self';
  form-action 'self';
  upgrade-insecure-requests;
```

**Nonce-based CSP for inline scripts**: generate a cryptographically random nonce
per request, add it to the CSP header and to every `<script>` tag that must be
inline. This allows inline scripts without `'unsafe-inline'`.

```typescript
const nonce = crypto.randomBytes(16).toString('base64');
// CSP header: script-src 'nonce-{nonce}'
// HTML: <script nonce="{nonce}">...</script>
```

**Report-only mode for rollout**: `Content-Security-Policy-Report-Only` sends
violations to a report endpoint without blocking. Use this to audit violations
before switching to enforcing mode.

```
Content-Security-Policy-Report-Only: default-src 'self'; report-uri /csp-report
```

### Required Headers for Enterprise SaaS

```http
# HSTS — forces HTTPS for the specified duration
# includeSubDomains: all subdomains must have valid TLS
# preload: submit to browser preload list (permanent, irreversible — be sure)
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload

# Prevents browsers from MIME-sniffing — serves file as declared Content-Type
X-Content-Type-Options: nosniff

# Clickjacking prevention (superseded by CSP frame-ancestors, but add both)
X-Frame-Options: DENY

# Controls referrer information sent on navigation
Referrer-Policy: strict-origin-when-cross-origin

# Controls browser feature access (camera, microphone, geolocation)
Permissions-Policy: camera=(), microphone=(), geolocation=()

# Remove server fingerprinting
Server: (omit or set to generic value)
X-Powered-By: (omit)
```

### Auditing Headers

Run your production URLs through [securityheaders.com](https://securityheaders.com)
and aim for an A grade. The tool grades each header and explains failures. Include
a header audit in your security review process — headers change silently when
infrastructure changes (CDN, reverse proxy configuration updates).

---

## API-Specific Controls

### Rate Limiting Strategies

| Strategy | Behavior | Best for | Risk |
|----------|----------|---------|------|
| **Fixed window** | N requests per time window, resets at interval boundary | Simple implementation | Burst at window boundary: 2x burst rate possible |
| **Sliding window** | N requests in any rolling window of duration T | More accurate enforcement | Higher memory per key |
| **Token bucket** | Tokens replenish at rate R, burst up to capacity B | Smooth throughput, allows controlled bursting | Implementation complexity |
| **Leaky bucket** | Requests processed at fixed rate; overflow dropped | Strict output rate limiting | No burst allowance |

**Token bucket is the standard for API rate limiting** — it accurately models "N
requests per period with burst headroom" which matches legitimate usage patterns.

Rate limit by: API key (per-client enforcement) first, then by IP (anonymous
protection), then by tenant (fair-use enforcement). Apply at the API gateway
level, not the application level, for performance.

Return rate limit metadata in response headers:

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 847
X-RateLimit-Reset: 1714310400
Retry-After: 60  # on 429 response
```

### API Key vs. OAuth Token

| Use case | Use |
|----------|-----|
| Server-to-server integration (no user) | API key or client credentials OAuth |
| User-facing SPA or mobile app | OAuth 2.0 authorization code + PKCE |
| Third-party integration acting as a specific user | OAuth 2.0 authorization code |
| Webhook consumer verifying your webhook signature | HMAC-signed shared secret |
| Long-lived automation with no user context | API key (with expiry + scope restriction) |

API keys are simpler to implement but have no built-in scoping, expiry, or
revocation model unless you build one. OAuth tokens are more complex but carry
scopes and have standardized revocation. For developer-facing APIs, OAuth client
credentials provide the better security properties; API keys are acceptable when
the audience is internal or when OAuth is a barrier to adoption.

### Input Validation at the API Boundary

Schema validation is the first line of defense — validate before any business
logic executes.

```typescript
// Zod schema validation as Express middleware
import { z } from 'zod';

const createOrderSchema = z.object({
  product_id: z.string().uuid(),
  quantity: z.number().int().positive().max(10000),
  shipping_address: z.object({
    country: z.enum(['US', 'CA', 'GB']),  // explicit allowlist, not string
    postal_code: z.string().regex(/^[A-Z0-9\s-]{3,10}$/i)
  })
});

// Validate early — before auth, before DB, before business logic
const result = createOrderSchema.safeParse(req.body);
if (!result.success) return res.status(400).json({ errors: result.error.flatten() });
```

Reject requests with unknown fields (strip or error) — unknown fields are a vector
for mass-assignment vulnerabilities.

### Response Filtering — Over-fetching as Information Disclosure

REST APIs that return full database rows for every GET response leak:
- Internal IDs and foreign keys that enable IDOR
- System metadata (created_by_admin, internal_flags, deleted_at)
- PII of other users in nested objects
- Sensitive business data beyond what the endpoint purpose requires

Every response shape should be explicitly defined. ORMs make it easy to `SELECT *`
— always project to the specific fields the response contract requires.

For GraphQL: field-level authorization on resolvers, not just root query authorization.
The `@auth` directive pattern applied per-field.

---

## SOC 2 Type II — Engineering Requirements

SOC 2 Type II audits whether your security controls are operating effectively over
a period (typically 6-12 months). The audit is evidence-based — assertions without
logs and config exports don't count.

### What Engineering Must Provide

| Control | Engineering implementation | Audit evidence |
|---------|--------------------------|----------------|
| Access logging | Structured auth event logs (A09 above) | Log exports covering the audit period |
| Change management | PR-based deploys, no direct production access | Git history, deploy pipeline runs |
| Encryption at rest | Database encryption, object storage encryption | Cloud console config, key management logs |
| Encryption in transit | TLS 1.2+ enforced, no plaintext fallback | TLS scan results, load balancer config |
| Access control | RBAC with least privilege, regular access reviews | Role assignments, quarterly review records |
| Incident response | Written runbook, incident log | Runbook doc, incident tickets with timestamps |
| Vulnerability management | Dependency scanning in CI, patching SLAs | Snyk/Dependabot reports, patch records |

**Access reviews**: quarterly review of who has access to what, with documented
remediation of overprivileged accounts. Engineering owns the technical query;
the security/compliance function owns the review sign-off.

**Patching SLAs** (typical SOC 2 expectation):
- Critical/High CVEs: 30 days from disclosure
- Medium CVEs: 90 days from disclosure
- Low CVEs: at next scheduled release

### Connection to Security Posture Decisions

Every security architecture decision made here (rate limiting, secret rotation,
audit logging, CSP) is also audit evidence. Document decisions in ADRs (Architecture
Decision Records) with the security rationale — auditors look for evidence of
intentional security design, not just reactive patching.

---

## Cross-Spoke Routing

| Topic | Route To |
|-------|----------|
| OAuth 2.0 flows, JWT design, RBAC/ABAC models | `be-auth-patterns` |
| API endpoint design, middleware stack, versioning | `be-api-design` |
| Service-to-service communication, event-driven security | `be-service-architecture` |
| Legal/regulatory compliance beyond SOC 2 (GDPR, HIPAA) | `a11y-legal-compliance` |
| Accessibility and security overlap in UI/form design | `a11y-legal-compliance` |
