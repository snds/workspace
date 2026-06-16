---
name: be-auth-patterns
description: >
  OAuth 2.0 flows, OIDC and JWT design, RBAC/ABAC/ReBAC permission models,
  SAML 2.0, SCIM provisioning, enterprise SSO architecture, and API security
  for enterprise B2B SaaS. Use this skill whenever the conversation touches:
  OAuth 2.0 authorization code + PKCE flow, client credentials flow, refresh
  token rotation, token storage security, ID token vs. access token vs. refresh
  token, JWT claims design and validation, opaque tokens vs. JWTs, token
  introspection (RFC 7662), RBAC design, ABAC attribute policies, ReBAC
  (relationship-based access control), Google Zanzibar model, OpenFGA,
  enterprise SSO with SAML 2.0 or OIDC, SP-initiated vs. IdP-initiated SSO,
  just-in-time provisioning vs. SCIM sync, SCIM 2.0 protocol, multi-tenant
  SSO routing, API key generation, hashing, rotation, scope restriction,
  audit logging for compliance, SOC 2 auth requirements, or any question about
  who can do what, how they prove it, and how you record that they did it.
  Not for: session management in a web framework (handled at app layer),
  encryption at rest (infrastructure concern), or network-level security.
---

# Be: Auth Patterns

Specialist lens for authentication, authorization, and identity management in
enterprise B2B SaaS. Part of the backend engineering skill network.

---

## Domain Boundary

This skill owns: **authentication flows, token design, permission modeling,
enterprise identity integration (SSO, SCIM), API key management, and
compliance-driven audit logging**.

- Authorization enforcement in API endpoints → `be-api-design`
- Multi-tenancy enforcement at query layer → `be-data-modeling`
- LLM API key management for third-party services → `ds-nlp-llm`
- SSO as a sales/GTM requirement → `pm-enterprise-gtm`

---

## OAuth 2.0 Flows

### Authorization Code + PKCE — The Only Correct Flow for User-Facing Apps

PKCE (Proof Key for Code Exchange) is required for all public clients (SPAs,
mobile apps) and recommended for confidential clients (server-side web apps).

```
1. Client generates code_verifier (random, 43-128 chars)
   code_challenge = BASE64URL(SHA256(code_verifier))

2. Authorization request:
   GET /authorize?
     response_type=code
     &client_id=CLIENT_ID
     &redirect_uri=https://app.example.com/callback
     &scope=openid profile email
     &state=RANDOM_CSRF_TOKEN          ← validate on return
     &code_challenge=BASE64URL(SHA256(verifier))
     &code_challenge_method=S256

3. Token exchange (server-side):
   POST /token
   grant_type=authorization_code
   &code=AUTH_CODE
   &redirect_uri=SAME_AS_STEP_2
   &code_verifier=ORIGINAL_VERIFIER   ← server verifies SHA256(verifier) == challenge

4. Returns: access_token, id_token, refresh_token
```

Never use the implicit flow. It returns tokens in the URL fragment, which are
logged by browsers and servers, and it doesn't support refresh tokens.

### Client Credentials — Service-to-Service

For machine-to-machine (no user context): client presents client_id + client_secret,
receives an access token scoped to the service's permissions.

```http
POST /token
Content-Type: application/x-www-form-urlencoded

grant_type=client_credentials
&client_id=SERVICE_CLIENT_ID
&client_secret=CLIENT_SECRET
&scope=orders:read inventory:write
```

Rotate client secrets on a schedule (quarterly) and on suspected compromise.
Store client secrets in a secrets manager (AWS Secrets Manager, HashiCorp Vault),
never in environment variables in plaintext.

### Refresh Token Rotation

Single-use refresh tokens with rotation detection:

1. Issue refresh token RT1 on initial authentication
2. When AT expires, client presents RT1 → server issues AT2 + RT2, invalidates RT1
3. If RT1 is presented again (replay attack), invalidate the entire token family

```
Token family: all refresh tokens issued from the same authorization grant
If a reused refresh token is detected → invalidate all tokens in the family
→ forces re-authentication → user is notified of potential compromise
```

Refresh token rotation is a requirement for SOC 2 and enterprise security reviews.

### Token Storage

| Surface | Access Token | Refresh Token |
|---------|-------------|--------------|
| SPA | Memory (not localStorage) | HttpOnly, Secure cookie |
| SSR web app | HttpOnly, Secure, SameSite=Strict cookie | Same |
| Mobile (native) | Secure storage (Keychain/Keystore) | Same |
| Backend service | In-memory or secrets manager | Same |

**Never** store tokens in localStorage or sessionStorage. XSS reads localStorage.
HttpOnly cookies are not accessible to JavaScript — XSS cannot steal them.

---

## OIDC and JWT Design

### Token Types and Their Purposes

| Token | Audience | Lifetime | Contains |
|-------|----------|---------|---------|
| ID token | The client application | Short (1 hour) | User identity claims (sub, email, name) |
| Access token | The resource server (your API) | Short (15 min–1 hour) | Authorization claims (scopes, roles, tenant) |
| Refresh token | The authorization server | Long (days–weeks) | No claims — opaque reference |

**The ID token is for the client, not the API.** Never send an ID token to your
backend as proof of authorization. The API validates the access token.

### JWT Claims Design

```json
{
  "iss": "https://auth.example.com",           // issuer — validate against expected value
  "sub": "user_abc123",                        // subject — stable user identifier
  "aud": ["https://api.example.com"],          // audience — validate your service is listed
  "exp": 1704067200,                           // expiry — validate strictly
  "iat": 1704063600,                           // issued at — for age checks
  "jti": "unique-token-id",                    // JWT ID — for revocation checks if needed
  
  // Custom claims for RBAC context
  "tenant_id": "t_789",                        // required — every token must carry tenant
  "roles": ["admin", "product-manager"],
  "permissions": ["orders:read", "orders:write"],
  "org_id": "org_012"
}
```

**JWT validation checklist** — all four, every time, no exceptions:
1. Signature: verify against the issuer's public key (fetched from JWKS endpoint)
2. Expiry (`exp`): reject expired tokens — don't accept "close enough"
3. Issuer (`iss`): must match your expected issuer URL
4. Audience (`aud`): your service's identifier must be in the audience array

Missing any of these validations is a security vulnerability.

### Opaque Tokens vs. JWTs

| | Opaque Token | JWT |
|--|-------------|-----|
| Validation | Requires introspection call to auth server | Local validation — no network call |
| Revocation | Immediate — invalidate at auth server | Delayed — valid until expiry |
| Performance | Network call per validation | In-process — fast |
| Use when | Revocability is critical (user logout, compromised token) | Distributed services need fast local validation |

**Hybrid approach**: short-lived JWTs (15 minutes) for most validation, with
a revocation list checked on sensitive operations. This is the common enterprise
pattern — fast for most requests, correct for logout/revocation.

---

## Permission Models

### RBAC — Role-Based Access Control

Roles define permission sets. Users have roles. Role membership determines access.

```sql
-- Core tables
users (id, tenant_id, email, ...)
roles (id, tenant_id, name, ...)          -- e.g., 'admin', 'viewer', 'product-manager'
permissions (id, name, description)       -- e.g., 'orders:write', 'products:delete'
role_permissions (role_id, permission_id)
user_roles (user_id, role_id, tenant_id)  -- tenant_id on assignment, not just definition
```

RBAC fails at scale when: you need row-level access control ("this user can only
see products in their region"), when permissions depend on resource attributes,
or when resource sharing across organizational boundaries is a core feature.

### ABAC — Attribute-Based Access Control

Policies reference subject attributes (user properties), resource attributes,
and environment attributes.

```
Policy: ALLOW orders:write
  IF subject.role IN ['admin', 'product-manager']
  AND subject.tenant_id == resource.tenant_id   ← attribute condition
  AND resource.status != 'archived'              ← resource attribute
  AND environment.time BETWEEN 09:00 AND 18:00   ← environment (uncommon)
```

ABAC is expressive but hard to audit ("what can this user do?" requires policy
evaluation, not a simple query). Use it when the conditions are genuinely
attribute-driven, not as a workaround for a poorly designed role model.

### ReBAC — Relationship-Based Access Control

Permissions are derived from entity relationships in a graph. Google's Zanzibar
paper is the canonical reference; OpenFGA is the open-source implementation.

```
# Tuple store: (user, relation, object)
user:alice, member, group:eng-team
group:eng-team, viewer, document:spec-123
user:alice, editor, document:draft-456

# Check: can alice view document:spec-123?
# Expand: alice member-of eng-team, eng-team viewer-of spec-123 → YES
```

**When ReBAC is the right model**: the resource sharing model is complex and
user-defined (e.g., "this product line is shared with my partner organization"),
or when permissions are deeply nested through organizational hierarchies.

**When it's over-engineering**: most enterprise SaaS with fixed organizational
structures and tenant-scoped data. RBAC with some attribute conditions handles
99% of cases without the operational complexity of a relationship graph store.

### Decision Matrix

| Scenario | Recommended Model |
|----------|------------------|
| Tenant-scoped CRUD with a few roles | RBAC |
| Tenant-scoped CRUD with row-level conditions | RBAC + attribute conditions (hybrid) |
| Resources shared across org boundaries | ReBAC (OpenFGA) |
| Compliance-driven fine-grained policies | ABAC |
| Start of a new SaaS product | RBAC — you can migrate later |

---

## Enterprise SSO

### SAML 2.0

Still dominant in enterprise. SP-initiated vs. IdP-initiated:

```
SP-initiated (preferred):
  User → Your App (SP) → Redirects to IdP with AuthnRequest
  IdP authenticates user → POSTs SAMLResponse to your ACS endpoint
  Your app validates SAMLResponse → creates session

IdP-initiated:
  User logs into IdP portal → IdP POSTs SAMLResponse directly to your ACS
  Your app must accept unsolicited responses — security risk, validate carefully
```

**SAML XML signature validation is required.** Verify:
- `SignatureValue` using the IdP's X.509 certificate
- `Conditions.NotBefore` and `Conditions.NotOnOrAfter`
- `AudienceRestriction` matches your SP entity ID
- `InResponseTo` matches your AuthnRequest ID (SP-initiated only)

Use a battle-tested SAML library (passport-saml, python-saml, saml2). Do not
implement SAML parsing yourself — XML signature validation has subtle attack
surface.

### Per-Tenant SSO Configuration

Enterprise SaaS with SSO must support multiple IdPs (one per enterprise customer).

```sql
-- Per-tenant IdP configuration
sso_configurations (
  id, tenant_id,
  provider_type,        -- 'saml' | 'oidc'
  entity_id,            -- SAML: IdP entity ID
  sso_url,              -- SAML: SSO URL; OIDC: authorization endpoint
  certificate,          -- SAML: IdP signing certificate (PEM)
  client_id,            -- OIDC: client ID at the IdP
  client_secret_enc,    -- OIDC: encrypted client secret
  email_domains,        -- ['acme.com', 'acme-corp.com'] — routing domains
  jit_provisioning,     -- bool: auto-create users on first login
  created_at, updated_at
)
```

Route to the correct IdP by email domain: when a user provides `alice@acme.com`,
look up the SSO configuration for `acme.com`.

### SCIM 2.0 Provisioning

SCIM is a REST protocol for syncing user directories. Enterprise customers require
it for automated provisioning/deprovisioning.

```
SCIM Resources:
  /Users     — individual user accounts
  /Groups    — groups and their memberships

SCIM Operations (you must handle all of these):
  POST   /Users                  — create user (provision)
  GET    /Users?filter=...       — list/search users
  GET    /Users/{id}             — get specific user
  PUT    /Users/{id}             — replace user (full update)
  PATCH  /Users/{id}             — partial update (Operations array)
  DELETE /Users/{id}             — deprovision user

PATCH format (RFC 7644):
{
  "schemas": ["urn:ietf:params:scim:api:messages:2.0:PatchOp"],
  "Operations": [
    { "op": "replace", "path": "active", "value": false },   // deactivate
    { "op": "replace", "path": "emails[type eq \"work\"].value", "value": "new@acme.com" }
  ]
}
```

**Critical**: handle DELETE and `active: false` differently. DELETE is hard
deprovision (account removed). `active: false` is soft deprovision (account
disabled, data retained). Enterprise customers use both depending on their HR
process — support both.

SCIM is required for enterprise tier. "We support SSO but not SCIM" means
the customer's IT admin has to manually create and deactivate accounts.
This is a blocker for procurement at most enterprises.

---

## API Key Management

Enterprise customers need API keys for integrations, automation, and server-side
access to your API.

### Generation and Storage

```python
# Generate: crypto-random, not UUID (UUIDs have predictable structure)
import secrets
key_value = secrets.token_urlsafe(32)  # 256 bits of entropy
key_prefix = "sk_live_"               # prefix identifies key type, not a secret

# Store: hash before persisting — the plaintext is only shown once at creation
import hashlib
key_hash = hashlib.sha256(key_value.encode()).hexdigest()

# Schema
api_keys (
  id, tenant_id, user_id,
  name,                  -- human-readable label ("Production integration")
  key_prefix,            -- first 8 chars of key, for identification in logs
  key_hash,              -- SHA-256 hash of full key
  scopes,                -- ['orders:read', 'products:write']
  last_used_at,
  expires_at,            -- optional expiry
  created_at, revoked_at
)
```

Show the full key value exactly once, at creation. After that, only the prefix
is displayed. Users who lose the key must rotate it.

### Rotation Pattern

```
1. User creates new key (key2) — both key1 and key2 are valid
2. User updates their integration to use key2
3. User verifies their integration works with key2
4. User revokes key1
```

The overlap window is required. Revoke-first destroys active integrations.
Set a suggested rotation interval (90 days) and surface approaching expiry.

### Audit Every Use

Every API key request must be logged:
- Timestamp, tenant_id, key_id (not the key itself), endpoint, IP address, HTTP status
- Aggregate usage in a materialized view for the management UI
- Alert on anomalous usage patterns (sudden volume spike, new IP, unusual hours)

---

## Audit Logging Requirements

Audit logs answer: who did what, to what resource, when, from where.

```sql
-- Append-only audit log table (never UPDATE or DELETE rows)
audit_logs (
  id              BIGSERIAL PRIMARY KEY,
  tenant_id       UUID NOT NULL,
  actor_id        UUID,             -- NULL for system actions
  actor_type      TEXT,             -- 'user' | 'api_key' | 'system' | 'support_agent'
  action          TEXT NOT NULL,    -- 'order.created', 'user.deactivated', 'export.downloaded'
  resource_type   TEXT NOT NULL,    -- 'order', 'user', 'product'
  resource_id     TEXT NOT NULL,    -- the affected resource's ID
  before_state    JSONB,            -- state before the change (for updates)
  after_state     JSONB,            -- state after the change
  ip_address      INET,
  user_agent      TEXT,
  request_id      TEXT,             -- correlates to application logs
  created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
)
-- Partition by created_at (monthly) — audit logs are write-heavy and archive-friendly
-- Write to append-only replica or object storage for tamper-evidence
```

**For SOC 2 Type II**: audit logs must cover all authentication events, privilege
changes, data exports, configuration changes, and data deletion. Retention minimum
is typically 1 year hot, 7 years cold.

---

## Cross-Spoke Routing

| Topic | Route To |
|-------|----------|
| Auth enforcement in API endpoints | `be-api-design` |
| Multi-tenancy query-layer enforcement | `be-data-modeling` |
| API key management for LLM services | `ds-nlp-llm` |
| SSO as enterprise GTM requirement | `pm-enterprise-gtm` |
| SCIM as enterprise feature in roadmap | `pm-enterprise-gtm` |
