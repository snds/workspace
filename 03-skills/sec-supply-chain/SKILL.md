---
name: sec-supply-chain
description: >
  Software supply-chain + secrets security — dependency risk (typosquatting, malicious/
  vulnerable packages), pinning + lockfiles + SBOM + provenance, secrets management (never
  in code/bundles; vaults + rotation), and CI/CD pipeline security (least-privilege tokens,
  protected runners). Use when adding dependencies, handling credentials, or securing a build
  pipeline. Triggers: supply chain, dependency, SBOM, provenance, lockfile, secrets, secret
  management, vault, CI/CD security, token, dependabot, typosquatting.
aliases: [sec-supply-chain]
triggers: [supply chain, dependency, sbom, provenance, lockfile, secrets, secret management, vault, ci/cd security, access token, dependabot, typosquatting]
tier: cross-cutting
hub: lead-security-architect
domain: security
surfaces: ["*"]
spec_version: "2.0"
---

# Security — Supply Chain & Secrets

Most code in your app is someone else's, and most breaches start with a leaked credential. This spoke owns
both.

## Dependencies are attack surface
Every package is code you run with your privileges. Risks: known vulnerabilities, **typosquatting**,
malicious updates, abandoned maintainers. Defend: **pin + lockfile** (reproducible installs), automated
vulnerability scanning (Dependabot/audit), an **SBOM** + provenance/signing where it matters, minimize the
dependency count, and review what a new dependency pulls in transitively.

## Secrets — never in code, ever
No secrets in source, client bundles, logs, or error messages (the integrity check + review back this).
Use a **secrets manager / vault**, inject at runtime, **rotate** regularly, and scope each secret to one
job. A leaked key is a when-not-if; design for fast rotation and detection (secret scanning in CI).

## CI/CD is production
The pipeline can deploy and holds powerful credentials — treat it as a high-value target. **Least-privilege
tokens** (short-lived, narrowly scoped — OIDC over long-lived keys), protected/ephemeral runners, pinned
action versions, and no untrusted code in privileged contexts. Ties to [[devops-ci-cd]].

## Related
- hub → [[lead-security-architect]]
- governs → [[devops-ci-cd]]
- peer ↔ [[sec-threat-modeling]] · [[sec-authn-authz]] · [[sec-appsec-owasp]]
