---
name: sec-supply-chain
description: >
  Software supply-chain and secrets security for enterprise B2B SaaS. Owns dependency risk and
  intake policy (typosquatting, malicious updates, transitive blast radius), pinning and lockfile
  integrity, SBOM (CycloneDX/SPDX) and provenance, artifact signing and verified attestation
  (Sigstore, SLSA levels), secrets management and rotation, secret scanning, and CI/CD pipeline
  hardening (short-lived federated tokens, pinned actions, ephemeral runners, protected
  environments). Use when adding or upgrading a dependency, handling credentials, generating an
  SBOM, responding to a leaked key, or securing a build and release pipeline. Triggers: supply
  chain, dependency, SBOM, provenance, SLSA, sigstore, signing, lockfile, secrets, secret
  management, vault, rotation, CI/CD security, OIDC, access token, dependabot, typosquatting.
aliases: [sec-supply-chain]
triggers: [supply chain, dependency, sbom, cyclonedx, spdx, provenance, slsa, sigstore, artifact signing, lockfile, secrets, secret management, secret scanning, hashicorp vault, secret rotation, ci/cd security, oidc federation, access token, dependabot, typosquatting, leaked credential]
tier: cross-cutting
hub: lead-security-architect
prerequisites: [lead-security-architect]
related: [be-security-posture, devops-ci-cd, sec-threat-modeling, sec-appsec-owasp]
domain: security
surfaces: ["*"]
requires: [gitleaks, syft]
defers_to: [framework-16]
rigor_role: measurement
spec_version: "2.2"
---

# Security: Supply Chain and Secrets

Most of the code you ship is someone else's, and most breaches start with a credential that should never
have been reachable. This spoke owns both, plus the pipeline that joins them, because in practice they
fail together: a compromised dependency runs in CI, and CI holds the credentials.

Three convictions frame everything below.

1. **Every dependency is code you execute with your own privileges.** Installing a package is a trust
   decision, and it is transitive.
2. **A leaked credential is a when, not an if.** Design for fast detection and fast rotation rather than
   for perfect secrecy.
3. **CI/CD is production.** It can deploy, it holds deploy credentials, and it runs untrusted code from
   pull requests. Treat it as the high-value target it is.

Backend-specific mechanics (tool comparison tables, concrete rotation Lambda patterns, SOC 2 evidence
mapping) are in [[be-security-posture]]; pipeline construction is in [[devops-ci-cd]]. Governed by
[[lead-security-architect]] and gated by [[16-security-operating-model]].

---

## Dependencies are attack surface

### The risk classes

| Risk | Mechanism | Signal to look for |
|---|---|---|
| **Known vulnerability** | A published CVE in a package you depend on, often transitively | Scanner findings, advisory feeds |
| **Typosquatting** | A package named to be confused with a real one | Name similarity, low download count, recent creation |
| **Malicious update** | A legitimate package's new version ships hostile code, via a compromised or sold maintainer account | Sudden maintainer change, new install scripts, new network calls, unexplained new dependencies |
| **Dependency confusion** | A public package shadows your internal package name because the resolver prefers the public registry | Internal package names that are unclaimed publicly |
| **Abandonment** | No maintainer, so vulnerabilities are never fixed | Last release age, open issue backlog, single maintainer |
| **Protestware or license change** | Deliberate behaviour change or a license flip that makes continued use untenable | Release notes, license diffs |
| **Build-time execution** | Install scripts and build plugins run arbitrary code on developer machines and in CI | Presence of post-install hooks |

### Intake policy

Adding a dependency is a decision with a security cost, and it deserves a moment of scrutiny
proportional to what it can reach. Before adding one, answer:

- **What does it pull in transitively?** The direct dependency is not the attack surface; the resolved
  tree is. A package with 200 transitive dependencies is 200 trust decisions.
- **Is it maintained?** Recent releases, more than one maintainer, responsive to security reports.
- **Is the name right?** Check character-by-character against the package you intended, and check that
  you reached it from official documentation rather than from a search result.
- **Does it run at install time?** Install hooks execute before any of your code does.
- **Could this be a few lines instead?** A one-function utility is rarely worth a permanent trust
  relationship and a permanent update obligation.
- **Is the internal name claimed?** For private packages, claim the name on the public registry or scope
  it, so dependency confusion is not available.

Record the decision for anything non-trivial. "Why is this here?" is the question that makes dependency
pruning possible two years later.

### Pinning and lockfile integrity

Reproducible installs are the baseline control, and they are frequently undermined by using the wrong
install command in CI.

- **Commit the lockfile.** For applications, always. It is the record of exactly what was resolved.
- **Install from the lockfile in CI**, with the command that fails when the lockfile is inconsistent
  with the manifest rather than silently updating it.
- **Verify integrity hashes.** Lockfiles carry them; the install must check them.
- **Pin by digest where the ecosystem supports it**, particularly container base images and CI actions.
  A mutable tag is not a pin: the same tag can point at different content tomorrow.
- **Pin known-bad exclusions explicitly.** When a transitive dependency has a vulnerability you cannot
  immediately upgrade past, pin the safe version with a comment carrying the CVE reference and a
  resolution date. This is a temporary control with an expiry, not a fix.

### Scanning policy

A scanner without a policy produces a dashboard nobody reads. Decide, and write down:

- **What blocks.** Severity threshold for failing a build, typically Critical and High for anything
  reachable from production code.
- **What the exception process is.** CVE reference, justification, compensating control, owner, and
  resolution date. Time-boxed, and the box actually expires.
- **What the patching SLA is.** A common enterprise baseline: Critical and High within 30 days of
  disclosure, Medium within 90, Low at the next scheduled release. Customer contracts and SOC 2
  expectations often set this for you.
- **Whether reachability matters.** A vulnerability in a dev-only or unreachable code path is real but
  lower priority. Distinguishing them is what stops alert fatigue, and it must be a documented judgment,
  not a silent dismissal.

---

## SBOM and provenance

### SBOM

An SBOM is a machine-readable inventory of every component in a build. It matters for two reasons: it is
increasingly a procurement requirement in enterprise sales and government contracting, and it is what
lets you answer "are we affected?" in hours rather than weeks when the next widely-used library has a
critical vulnerability.

- **CycloneDX** is the pragmatic default: JSON, strong tooling, designed with vulnerability analysis in
  mind.
- **SPDX** is the ISO-standardized option and is generally preferred where license compliance is the
  driver.

Generate the SBOM **as part of the release pipeline, from the built artifact**, not by re-reading the
manifest afterwards. An SBOM produced from source can differ from what actually shipped, which defeats
its purpose. Attach it to the release, and store it somewhere queryable so new advisories can be matched
against historical releases rather than only against `main`.

Preflight the `syft` capability before generating one; if it is absent, follow the registry's fallback
rather than claiming an SBOM exists.

### Provenance and signing

An SBOM says what is inside. **Provenance** says where it came from and that it has not been altered
since. The two together are what a customer's security review is actually asking about.

| Control | What it establishes |
|---|---|
| **Artifact signing** (Sigstore/cosign, or ecosystem-native signing) | This artifact was produced by us and has not been modified |
| **Build provenance attestation** | This artifact was built from this commit, by this workflow, in this environment |
| **Verification at deploy** | The thing being deployed is one we actually built, refusing anything unsigned or unverifiable |

The **SLSA** levels are a useful ladder for naming where you are and what the next rung buys, rather than
a badge to collect: from scripted builds, to a hosted build service producing signed provenance, to
hardened, non-falsifiable provenance. Name your current level in the threat model and name the specific
threat the next level would close.

The rule that makes signing worth anything: **verification must be enforced at deploy time.** Signing
artifacts nobody verifies is bookkeeping. The control is the refusal.

---

## Secrets

### The rule

Secrets never enter source control. Not in code, not in config, not in comments, not in commit messages,
not in test fixtures, not in a `.env` that gets committed once, and never in anything shipped to a
browser. Anything in a client bundle is public by construction.

Once a secret reaches history, **assume it is compromised**. Rewriting history is cleanup, not
remediation; rotation is remediation. The clone that already exists on someone's laptop, or in a CI cache,
or in a fork, is not affected by your rewrite.

### Where secrets live

Preference order for enterprise B2B SaaS:

1. **Cloud-native secrets manager** for production on a single cloud, with strict access policy and an
   audit trail.
2. **A dedicated secrets manager or vault** for multi-cloud, on-premise, or when you need dynamic
   short-lived credentials.
3. **Platform-managed secrets** where a PaaS owns injection, accepting reduced rotation control.
4. **Environment variables** for local development. Not for production sensitive credentials: they leak
   into process listings, child processes, crash dumps, and logs.

Best of all is **no stored secret**: workload identity or federated short-lived credentials, where the
platform mints a credential per execution and nothing durable exists to leak.

### Rotation

Rotation is only a real control if it can be performed under load without an outage, which requires
overlapping validity.

1. **Add** the new secret version alongside the old, and update the consumer to accept both.
2. **Switch** the primary to the new version, keeping the old accepted while the change propagates.
3. **Revoke** the old version once no traffic uses it, then remove the dual-read path.

Two consequences worth designing for up front: **every secret needs a documented rotation path before it
ships** (the runbook entry is part of the stage-4 gate), and **rotation should be rehearsed**, because an
untested rotation procedure discovered during an incident is not a control.

Scope each secret to a single consumer. A credential shared across services cannot be rotated without
coordinating every consumer, which is precisely why shared credentials are never rotated in practice.

### Secret scanning

Run it in two places, because they catch different things:

- **Pre-commit**, on staged changes, to stop the leak before it exists. Use `gitleaks` for this; preflight
  the capability first and fall back per the registry if it is absent.
- **In CI, over history**, to catch what bypassed the hook and what was committed before the hook existed.

Extend the default rule sets with patterns for your own credential formats, since generic entropy rules
will not recognise your API key shape. And wire up **provider-side push protection and revocation
webhooks** where available; the fastest remediation path for a leaked cloud or provider key is the
provider revoking it automatically.

### When a secret leaks

The order matters, and the instinct to clean up first is the wrong one.

1. **Rotate or revoke** the credential. First, before anything else.
2. **Assess reach**: what did it grant, and for how long was it exposed?
3. **Look for use**: audit logs for that credential over the whole exposure window, not just since
   discovery.
4. **Close the path** that allowed it: the missing hook, the unscanned file type, the process gap.
5. **Then** clean history, and record the incident with a timeline.

---

## CI/CD is production

The pipeline can deploy to production, holds credentials for production, and on many projects executes
code from untrusted pull requests. That combination makes it the highest-leverage target in the system
and the one most often left unmodelled.

| Control | The rule | The threat it closes |
|---|---|---|
| **Federated short-lived tokens** | Use OIDC to exchange a workflow identity for a scoped, minutes-long cloud credential. No long-lived static keys in CI | A stolen CI secret granting indefinite production access |
| **Least-privilege job permissions** | Default the pipeline's token to read-only and grant write per job that needs it | A compromised build step pushing code, packages, or releases |
| **Pin actions and images by digest** | Third-party CI actions are dependencies that run with your pipeline's privileges | A mutable tag on a popular action being repointed at hostile code |
| **No secrets in untrusted contexts** | Workflows triggered by forked pull requests get no secrets and no write permissions | An attacker opening a PR that exfiltrates your credentials |
| **Ephemeral runners** | Fresh environment per job; never reuse a runner that ran untrusted code | Cache and workspace poisoning between jobs |
| **Protected environments** | Production deploys require approval and are restricted to protected branches | A direct push or a rogue workflow reaching production |
| **Isolate build from publish** | The job that builds does not hold publishing credentials; publishing is a separate, gated step | Arbitrary build code reaching the registry |
| **Audit the pipeline** | Workflow changes are reviewed like production code, because they are | A quiet workflow edit adding an exfiltration step |
| **Guard cache and artifacts** | Treat caches as untrusted input; scope keys so one job cannot poison another | Cache poisoning as a persistence mechanism |

The recurring self-inflicted wound: **a pipeline change is a production change** and often bypasses the
review rigor applied to application code. A workflow file edit that adds a step with access to secrets
deserves the same scrutiny as a change to the authentication handler.

---

## Review checklist

Run against any diff that adds a dependency, touches a credential, or changes the pipeline.

- [ ] New dependencies: transitive tree reviewed, name verified, maintenance checked, install hooks noted.
- [ ] Lockfile committed and updated; CI installs from the lockfile with integrity verification.
- [ ] Container base images and CI actions pinned by digest, not by mutable tag.
- [ ] Dependency scan passes the severity policy, or the exception has a CVE reference, justification,
      owner, and resolution date.
- [ ] SBOM generated from the built artifact and attached to the release.
- [ ] Release artifacts signed, and verification is enforced at deploy rather than merely available.
- [ ] Secret scanning runs pre-commit locally and over history in CI, both blocking.
- [ ] No new secret appears in source, fixtures, config, client bundle, log, or error path.
- [ ] Every new secret has a named owner, a single consumer scope, a storage location, and a documented
      rotation path in the runbook.
- [ ] CI credentials are federated and short-lived; no long-lived static cloud keys remain.
- [ ] Pipeline token permissions default to read-only, with write granted per job.
- [ ] Workflows triggered by forked pull requests receive no secrets and no write permissions.
- [ ] Production deployment is gated by approval and restricted to protected branches.
- [ ] Scanner results recorded with tool, version, and ruleset, so "it was clean" stays checkable.

## Related
- hub → [[lead-security-architect]]
- governs → [[devops-ci-cd]]
- peer ↔ [[sec-threat-modeling]] · [[sec-authn-authz]] · [[sec-appsec-owasp]]
