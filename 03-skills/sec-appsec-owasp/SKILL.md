---
name: sec-appsec-owasp
description: >
  Application security against the OWASP Top 10 — injection (SQL/command), XSS, CSRF, SSRF,
  insecure deserialization, security misconfiguration — via input validation, output
  encoding/parameterization, secure defaults, and a secure SDLC. Covers both backend and
  frontend (CSP, sanitization). Use when handling untrusted input, rendering user content,
  building APIs, or hardening an app. Triggers: owasp, injection, sql injection, xss, csrf,
  ssrf, input validation, output encoding, content security policy, sanitization, secure SDLC.
aliases: [sec-appsec-owasp]
triggers: [owasp, injection, sql injection, xss, csrf, ssrf, input validation, output encoding, content security policy, sanitization, secure sdlc]
tier: cross-cutting
hub: lead-security-architect
domain: security
surfaces: ["*"]
spec_version: "2.0"
---

# Security — Application Security (OWASP)

The concrete vulnerability classes and their fixes. Applies to backend *and* frontend — most are about the
same root cause: trusting untrusted data.

## Injection — parameterize, never concatenate
SQL/NoSQL/command/template injection all come from mixing data into code. **Parameterized queries / prepared
statements** and safe APIs eliminate them; string-building a query with user input is the canonical mistake.
Validate input against an allowlist at the boundary ([[eng-foundations]] rule).

## The web trio: XSS, CSRF, SSRF
- **XSS** — untrusted data rendered as markup. Fix: context-aware **output encoding**, framework
  auto-escaping, sanitize rich input, and a strict **Content-Security-Policy**.
- **CSRF** — the browser auto-sends credentials. Fix: SameSite cookies + anti-CSRF tokens for state-changing
  requests.
- **SSRF** — server fetches an attacker-controlled URL. Fix: allowlist destinations, block internal ranges.

## Secure defaults + misconfiguration
Security misconfiguration is rampant: verbose errors, open buckets, default creds, missing headers. Ship
secure-by-default (least privilege, hardened headers, no secrets in client bundles), and treat security as
acceptance criteria. Pairs with the QA Operating Model (framework 06).

## Secure SDLC
Bake it in: threat-model ([[sec-threat-modeling]]) at design, secure code + review during build, SAST/DAST +
dependency scanning ([[sec-supply-chain]]) in CI, monitoring in prod.

## Related
- hub → [[lead-security-architect]]
- governs → [[be-api-design]] · [[fe-api-integration]]
- peer ↔ [[sec-threat-modeling]] · [[sec-authn-authz]] · [[sec-supply-chain]]
