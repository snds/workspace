---
name: sec-authn-authz
description: >
  Identity and permission models for enterprise B2B SaaS. Owns the authn/authz decision
  table required by stage 2 of the security operating model: which authentication flow
  belongs to which client class, session and token lifetime policy with a real revocation
  path, the authorization model choice (RBAC / ABAC / ReBAC), tenant-scope derivation,
  the single enforcement choke point, delegated admin and support impersonation, machine
  identity and least privilege, and the negative-test matrix that proves access control
  holds. Use when building login, SSO, sessions, API auth, permissions, service accounts,
  or any multi-tenant access path. Triggers: authentication, authorization, oauth, oidc,
  jwt, session management, session hijacking, rbac, abac, rebac, access control, idor,
  least privilege, sso, scim, mfa, impersonation, tenant scope, permission model.
aliases: [sec-authn-authz]
triggers: [authentication, authorization, oauth, oidc, jwt, session management, session hijacking, rbac, abac, rebac, access control, idor, least privilege, sso, scim, mfa, impersonation, tenant scope, permission model, service account]
tier: cross-cutting
hub: lead-security-architect
prerequisites: [lead-security-architect]
related: [be-auth-patterns, be-security-posture, sec-threat-modeling, sec-appsec-owasp, sec-supply-chain]
domain: security
surfaces: ["*"]
defers_to: [framework-16]
rigor_role: load-chain
spec_version: "2.2"
---

# Security: Authentication and Authorization

Authentication establishes who is calling. Authorization decides whether that caller may perform
this action, on this object, in this tenant. Conflating them is the root of the most common serious
vulnerability class in enterprise SaaS, and the reason broken access control sits at the top of the
OWASP list.

This spoke owns the **decision surface**: which flow for which client, which permission model, where
enforcement lives, and how it is proven. It is the identity half of stage 2 ("secure build") in
[[16-security-operating-model]], and its decision table is the artifact that stage requires in the PR.

Governed by [[lead-security-architect]]. Protocol mechanics live in [[be-auth-patterns]]: OAuth 2.x
flow diagrams, PKCE parameters, JWT claim layouts, SAML assertion handling, SCIM payloads, and API
key hashing. Read that spoke rather than re-deriving the protocol here. This spoke decides *what to
choose and how to prove it*; that spoke implements the choice.

---

## The two questions, and where each is answered

| | Authentication | Authorization |
|---|---|---|
| Question | Who is this principal? | May this principal do this, here, now? |
| Frequency | Once per session or token issuance | Every request, and again per object touched |
| Produces | A verified principal: subject, tenant, roles, scopes, auth method, issued-at | An allow or deny decision, plus the reason |
| Lives in | Middleware, gateway, identity provider | The handler and the data-access layer, close to the object |
| Failure cost | Account takeover for one identity | Cross-tenant data exposure, which is a reportable breach |
| Fails closed by | Rejecting the request with no principal | Denying when no policy explicitly allows |

The asymmetry matters: authentication is a solved problem you should delegate to an identity provider
and a well-maintained library, while authorization is domain logic that only you can write, and it is
where nearly all of the real risk sits. Budget your review time accordingly.

---

## Step 1: the authentication decision table

Stage 2 of [[16-security-operating-model]] requires a decision table in the pull request. One row per
client class. If a client does not fit an existing row, it is a new row plus a threat-model delta in
[[sec-threat-modeling]], not an exception squeezed into an existing flow.

| Client class | Flow | Credential held by the client | Notes |
|---|---|---|---|
| First-party browser SPA | OAuth 2.x authorization code with PKCE, or a first-party session cookie | Short-lived access token in memory, refresh in an httpOnly cookie | Never persist tokens in `localStorage` where any script can read them |
| First-party server-rendered web app | Server-side session, cookie is an opaque reference | Nothing but the cookie | The simplest correct option; revocation is trivial |
| Native mobile | Authorization code with PKCE, system browser, not an embedded webview | Tokens in the platform keystore | Embedded webviews defeat the user's ability to verify the login origin |
| Public CLI or desktop tool | Device authorization grant, or loopback redirect with PKCE | Refresh token in the OS credential store | Never a client secret; a public client cannot keep one |
| Service-to-service inside your trust boundary | Workload identity (mTLS or a platform-issued identity token) | No static secret | Preferred over any long-lived key |
| Service-to-service across a boundary | OAuth client credentials, or mTLS | Client secret in a secrets manager, or a certificate | Scope the token to the specific operation, not to the whole API |
| Third-party integration acting for a user | Authorization code with explicit consent screen and scopes | Tokens held by the third party | Users must be able to see and revoke the grant themselves |
| Partner server calling your API | Client credentials, or a scoped and expiring API key | Secret in the partner's vault | Bind the key to a tenant and an IP or mTLS identity where the partner can support it |
| Inbound webhook from a vendor | HMAC signature over the raw body, plus a timestamp and replay window | Shared signing secret | Verify before parsing; reject stale timestamps; support two active secrets so rotation is not an outage |
| Customer workforce login | Federated SSO per tenant: OIDC preferred, SAML 2.0 where the customer requires it | Nothing; the customer's IdP authenticates | Per-tenant configuration, per-tenant signing keys, and no cross-tenant IdP reuse |
| Customer directory sync | SCIM 2.0 with a tenant-scoped bearer token | Token held by the customer's IdP | Provisioning is an authorization surface: it decides who becomes a member of which tenant |
| Automation with no user context | Scoped API key or service account with a mandatory expiry | Secret in the customer's or your own vault | Keys without expiry become permanent, undocumented root access |
| Agentic client (an LLM tool caller, an MCP client) | Delegated, user-consented token with the narrowest possible scope and a short TTL | Token held by the agent runtime | Treat the agent as a hostile-capable confused deputy; never give it a credential broader than the user's own rights |

Three rules that keep the table honest:

- **Every row names its revocation path.** A flow whose credentials cannot be revoked in minutes is
  not finished, no matter how standard the protocol.
- **Multi-factor is a property of the identity, not of the flow.** Decide where MFA is enforced (your
  own login, or asserted by the customer's IdP), record which, and never assume a federated
  assertion carries a factor it does not claim.
- **No "internal only" row.** Internal clients get the same table. Network position is not identity.

---

## Step 2: session and token lifetime policy

The lifetime table is the other half of stage 2. It exists to answer one question for every
credential: how much damage can a leaked copy do, and for how long?

| Credential | Lifetime | Rotation | Revocation path | Blast radius while valid |
|---|---|---|---|---|
| Access token | 5 to 15 minutes | Not rotated; re-minted from the refresh token | Expiry, plus a deny-list for emergencies | The subject's own rights for the remaining TTL |
| Refresh token | Days to weeks, with an absolute cap | Rotate on every use, detect reuse of a consumed token as theft | Server-side revoke, and revoke the whole family on reuse detection | Continuous re-minting until detected |
| Browser session cookie | Idle timeout plus an absolute maximum | New session id on privilege change and on login | Server-side session store delete | Full interactive access |
| API key | Mandatory expiry, one year at the very most | Overlapping two-key window so rotation is not an outage | Immediate delete, keys stored hashed so a database read cannot reuse them | Whatever scope the key carries, unattended |
| Webhook signing secret | Rotate on a schedule | Two active secrets during the overlap | Retire the old secret after the window | Forged inbound events |
| Impersonation token | Minutes, single tenant, single session | Never reused | Automatic expiry plus an explicit end-session action | Support-level view of one customer's data |
| Password reset or invite token | Minutes to hours, single use | Invalidate on use and on a newer request | Consumed on use | Account takeover if the email is compromised |
| Remembered MFA device | Weeks, bound to a device fingerprint | Re-challenge on risk signals | Revoke all devices on credential change | Skips the second factor |

**Revocation is a design requirement, not a feature request.** Stateless tokens trade revocation for
scale, so you must buy it back deliberately with one of: short TTLs plus a stateful refresh endpoint,
a deny-list keyed by token id with a TTL equal to the token lifetime, or a generation counter claim
compared against a per-principal value on each request. Pick one explicitly and write it down.

These events must invalidate outstanding credentials, and each one deserves a test:

- Logout, on the device and on all devices.
- Password change, MFA reset, or any credential recovery flow.
- Role or permission change that reduces access, including removal from a tenant.
- Deprovisioning through SCIM, or the customer disabling the user in their IdP.
- Tenant offboarding or contract termination, which must invalidate every credential scoped to it.
- Suspected compromise, where the answer to "how fast" should be minutes and should be rehearsed.

---

## Step 3: choose the permission model deliberately

| Model | Decides on | Fits | Cost |
|---|---|---|---|
| **RBAC** | Role membership | Function-level access, admin consoles, the coarse layer nearly every product needs | Role explosion once customers want exceptions |
| **ABAC** | Attributes of subject, resource, action, environment | Row-level and conditional rules: region, data classification, ownership, time windows | Hard to answer "what can this user do?" without evaluating everything |
| **ReBAC** | Relationships in a graph | Sharing, nested containers, org hierarchies, guest access, "everyone in this workspace" | Needs a purpose-built store and careful consistency handling |

Most enterprise B2B products need RBAC for function-level checks, plus attribute or relationship
conditions for object-level checks. That combination, not a single pure model, is the default. Model
selection mechanics and store choices belong to [[be-auth-patterns]].

What enterprise buyers actually require, and what therefore belongs in the model from the start:

- **Customer-defined roles**, or at minimum customer-configurable mapping from their IdP groups to
  your roles, per tenant.
- **Delegated administration**, so a customer admin manages their own users without contacting you.
- **A read-only auditor role**, because compliance reviewers should never need a role that can write.
- **Least-privilege defaults.** A newly invited user gets the minimum, and an unmapped IdP group
  grants nothing rather than falling back to a member role.
- **Permissions as data, not as conditionals scattered through handlers.** A queryable catalogue lets
  you answer support questions, generate customer-facing documentation, and diff a release for
  privilege drift.
- **An introspection path**: given a principal, list effective permissions and where each came from.
  Without it, every access question becomes an archaeology exercise.
- **Service accounts as first-class principals**, with roles, owners, and expiry, not as users with a
  shared mailbox.

---

## Step 4: derive the tenant scope, never accept it

In a multi-tenant product this is the highest-consequence rule in the whole discipline. The tenant
identifier used in every query comes from the verified credential and from nowhere else. Not from a
path parameter, not from a header, not from a request body, not from a cached client hint, not from a
subdomain the client controls.

Build it so the unsafe form is hard to write rather than merely discouraged:

```python
# The principal is the only source of tenancy. A repository handed a scope
# cannot be asked for another tenant's rows, so the correct call is the easy one.
class TenantScope:
    def __init__(self, principal: Principal):
        self.tenant_id = principal.tenant_id      # from the verified token, never the request

class InvoiceRepository:
    def __init__(self, db, scope: TenantScope):
        self._db, self._scope = db, scope

    def get(self, invoice_id: str) -> Invoice | None:
        # tenant predicate is structural, not something a caller remembers to add
        return self._db.fetch_one(
            "SELECT * FROM invoices WHERE id = %s AND tenant_id = %s",
            (invoice_id, self._scope.tenant_id),
        )
```

Then add a backstop at a different layer, because a single mechanism will eventually be bypassed by
a report query, a migration script, or an admin tool: database row-level security bound to a session
variable, or per-tenant schemas, or a separate database per tenant for your highest-tier customers.
Defense in depth here is not paranoia, it is the difference between a bug and a breach.

Cross-tenant surfaces that legitimately exist (support tooling, billing rollups, platform analytics)
are separate services or separate code paths with their own principal type and their own audit
trail. They are never the same handler with a flag.

---

## Step 5: one enforcement choke point

Authorization that is enforced in many places is enforced inconsistently. Give the system exactly one
decision function and make every data path go through it.

```typescript
// The only place an allow/deny decision is made. Handlers call it; nothing bypasses it.
type Decision = { allow: true } | { allow: false; reason: string };

function authorize(
  principal: Principal,
  action: Action,          // 'invoice:read', 'member:invite', 'settings:write'
  resource: Resource,      // loaded object, carrying its own tenant_id and owner
): Decision;
```

The rules that make the choke point real:

- **Deny by default.** The decision function returns deny unless a policy explicitly allows. A new
  action with no policy is inaccessible, which is the safe direction to fail.
- **Authorize the object, not the route.** Load the object, then decide. Route-level checks cannot
  see which record the id refers to, which is exactly what the attacker is changing.
- **Filter list endpoints in the query.** Derive the predicate from policy and push it into the
  query. Fetching broadly and filtering afterwards leaks through counts, pagination totals,
  aggregate numbers, and error timing.
- **Check function-level and object-level separately.** A read-only auditor with a valid object
  reference must still be denied on write. Object ownership is not permission to mutate.
- **Never authorize in the client.** Hiding a button is user experience. The server behaves as if
  every request came from a hostile script, because eventually one will.
- **Make it greppable.** A reviewer must be able to find the enforcement point in the diff. If you
  cannot point at the line, the reviewer cannot approve the change, which is the practical meaning of
  the small-diff rule in [[07-integration-and-review-framework]] for security work.
- **Log the deny with its reason.** Denials are the highest-value security signal you own, and they
  feed stage 4 detection.

---

## Delegated admin, impersonation, and support access

Every B2B SaaS eventually builds a way for staff to see what a customer sees. Done casually, it is
the largest single-credential blast radius in the product, and it is the control auditors probe
first.

Requirements, all of them:

- A **distinct principal type** for support access. Never a login as the customer's own user, and
  never a shared support account.
- **A stated reason** with a ticket or case reference, captured at session start, not backfilled.
- **Time-boxed** sessions measured in minutes, with automatic expiry and an explicit end action.
- **Scoped to one tenant**, chosen deliberately, with no ability to pivot without a new session.
- **Read-only by default.** Write access requires a second approver, and it is recorded as such.
- **Dual identity in every audit event**: the acting staff member and the impersonated subject.
- **Visible to the customer**, through an in-product indicator, a notification, or at minimum an
  audit log the customer can read themselves. Enterprise contracts increasingly require this.
- **Excluded from customer-facing metrics**, so support activity does not pollute usage analytics.

---

## Machine identity and least privilege

- **One identity per workload.** Shared credentials make attribution impossible and rotation
  frightening, which is how a credential becomes permanent.
- **Federated workload identity over static keys.** A short-lived credential exchanged from a
  platform identity cannot be pasted into a wiki. Pipeline identity specifics are owned by
  [[sec-supply-chain]].
- **Scope narrowly, and downward only.** A service calling another service on behalf of a user should
  propagate a token that carries the user's rights, not collapse into a service identity with full
  access. Collapsing identity is how a low-privilege user reaches a high-privilege path.
- **No standing god tokens.** If an operation needs elevated rights, mint them for the operation and
  let them expire.
- **Expiry on everything.** A credential with no expiry is a credential you will find in an incident
  timeline years from now.

---

## The failure catalogue

Each row is a real class, phrased so you can look for it, with the check that catches it.

| Failure | How it happens | The check that catches it |
|---|---|---|
| IDOR | Handler trusts an object id and omits the tenant or owner predicate | Two-tenant test: tenant A requests tenant B's id and must receive 404 |
| Missing function-level check | Object check exists, action check does not | Role matrix test: every role against every action |
| Tenant id from the request | Path, header, or body supplies the scope | Grep for the scope's provenance; assert it comes from the principal |
| Mass assignment | Update accepts the whole body, including `role`, `tenant_id`, or `is_admin` | Schema with an explicit allowlist; test that a privileged field in the payload is rejected |
| Nested resource escalation | Parent is authorized, child is not re-checked | Test a child object whose parent belongs to the caller but whose own owner does not |
| Post-filtering a broad query | Query fetches all, code filters after | Assert the query text or plan contains the tenant predicate |
| Shared cache key | Cache key omits tenant or principal | Test a cache hit across two tenants for the same logical key |
| Token confusion | Verifier accepts any algorithm, or skips `aud` and `iss` | Negative token tests: unsigned, wrong algorithm, wrong audience, expired |
| Replay | No nonce, timestamp, or single-use guarantee on sensitive requests | Replay the same signed request and require rejection |
| Invitation grafting | Invite or SSO flow accepts an unverified domain or email claim | Test that an unverified claim cannot join an existing tenant |
| Provisioning drift | SCIM group mapping grants more than intended, or deprovisioning does not revoke | Test that removal in the directory ends access within the agreed window |
| Session fixation | Session id survives authentication | Assert the identifier changes on login and on privilege change |
| Silent privilege creep | Roles gain permissions release over release without review | Diff the permission catalogue in CI and require sign-off on additions |

---

## Verification: the tests that must exist

This is the measurement path for identity work. Judgment does not substitute for it.

1. **A two-tenant fixture** available to every test that touches data, so cross-tenant assertions are
   cheap enough that nobody skips them.
2. **A role matrix test** generated from the permission catalogue, asserting allow and deny for every
   role against every action. Generated, so a new action appears as a failing case rather than an
   untested one.
3. **Negative tests as first-class citizens.** For each endpoint: no credential, expired credential,
   wrong tenant, insufficient role, valid credential and someone else's object.
4. **Token verification tests** covering algorithm pinning, audience, issuer, expiry, and clock skew.
5. **Session lifecycle tests** for the invalidation events listed in step 2.
6. **An impersonation audit test** asserting both identities and the reason are recorded.
7. **A route inventory gate** in CI that fails when a registered route reaches data without passing
   through the decision function. This is the one check that keeps the choke point real as the team
   grows.

---

## Done-gates

Before identity or permission work is ready for review, all of the following are true:

- The **decision table** (step 1) and the **lifetime table** (step 2) are in the pull request, with
  new or changed rows called out.
- The permission model change is expressed in the **catalogue**, and the catalogue diff is in the
  review.
- The **enforcement point is locatable in the diff**, and the reviewer confirmed it matches the
  control the threat model promised.
- **Tenant scope is derived from the credential** everywhere the diff touches data, with the
  database-level backstop still intact.
- The **negative and two-tenant tests** exist and fail when the check is removed, verified by
  removing it once locally.
- **Revocation is answerable in a sentence**: what invalidates this credential, and how fast.
- **Denials are logged** with actor, action, resource, tenant, and reason, feeding stage 4 detection.
- Any accepted risk is in the register with an owner and an expiry, per [[sec-threat-modeling]].

---

## Absolute bans

- Trusting a client-supplied tenant id, role, price, or permission claim.
- Shipping authorization as a follow-up while the feature goes live.
- A credential with no revocation path or no expiry.
- Logging tokens, cookies, assertions, or password material, including on failure paths.
- Rolling your own password storage or your own signature verification when a maintained library
  exists.
- Using an unverified email or domain claim to place a user into an existing tenant.
- A shared support or admin account, or impersonation without dual-identity audit.
- Treating network position, an obscure identifier, or a hidden control as an access control.

---

## Defers-to

- **Framework [[16-security-operating-model]] wins** on pipeline order, done-gates, and bans.
- **Protocol depth defers to [[be-auth-patterns]]**: flows, claim layouts, SAML and SCIM handling,
  key hashing. Do not restate it here.
- **Plugin security reviewers detect, this spoke decides.** The Cursor `review-security` pass over a
  diff is a finding generator. Triage its output against the model and this spoke's catalogue: a
  finding that contradicts a verified control is a regression, and a finding with no matching threat
  means the model has a gap.

## Related
- hub → [[lead-security-architect]]
- governs → [[be-api-design]]
- peer ↔ [[sec-threat-modeling]] · [[sec-appsec-owasp]] · [[sec-supply-chain]]
