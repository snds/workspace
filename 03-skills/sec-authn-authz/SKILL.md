---
name: sec-authn-authz
description: >
  Authentication + authorization done right — identity, sessions vs. tokens (OAuth 2.x,
  OIDC, JWT pitfalls), the authn/authz distinction, RBAC vs. ABAC, least privilege, and the
  common failure modes (broken access control, IDOR, missing function-level checks). Use when
  building login, sessions, API auth, permissions, or multi-tenant access. Triggers:
  authentication, authorization, oauth, oidc, jwt, session, rbac, abac, access control, idor,
  least privilege, sso, mfa.
aliases: [sec-authn-authz]
triggers: [authentication, authorization, oauth, oidc, jwt, session, rbac, abac, access control, idor, least privilege, sso, mfa]
tier: cross-cutting
hub: lead-security-architect
domain: security
surfaces: ["*"]
spec_version: "2.0"
---

# Security — Authentication & Authorization

The two are different and both are load-bearing. **Authentication** = who you are; **authorization** = what
you may do. Conflating them is the root of most access-control bugs.

## Authentication
Prefer delegated identity (**OIDC** on top of OAuth 2.x) over rolling your own password store. Know the
token model: **sessions** (server state, easy revoke) vs. **JWTs** (stateless, hard to revoke — short TTLs +
refresh, never trust an unverified token, validate `alg`/`iss`/`aud`/`exp`). MFA where it matters. Store
password hashes with a slow KDF (argon2/bcrypt) — never plaintext or fast hashes.

## Authorization (the OWASP #1 failure)
**Broken access control** is the most common serious vuln. Enforce authorization **server-side, on every
request, at the object level** — never trust the client or hide-the-button. Watch for **IDOR** (changing an
ID to access another's data) and missing function-level checks. Choose **RBAC** (roles) for coarse, **ABAC**
(attributes/policy) for fine-grained or multi-tenant.

## Least privilege + sessions
Grant the minimum scope for the minimum time; scope tokens narrowly. Manage session lifecycle (rotation on
login, invalidation on logout/breach, secure + httpOnly + SameSite cookies). This is [[lead-security-architect]]'s
least-privilege conviction applied to identity.

## Related
- hub → [[lead-security-architect]]
- governs → [[be-api-design]]
- peer ↔ [[sec-threat-modeling]] · [[sec-appsec-owasp]] · [[sec-supply-chain]]
