---
name: sec-supply-chain
description: >
  Software supply-chain, secrets, and build-pipeline security for enterprise B2B SaaS.
  Owns the dependency intake gate (what a new dependency must earn), pinning and
  reproducible installs, vulnerability response with reachability triage and expiring
  waivers, SBOM and provenance as customer-facing evidence, the six-stage secret
  lifecycle plus the leaked-credential runbook, the secret-sprawl inventory, pipeline
  identity (federated short-lived credentials over static keys), and third-party risk
  inside the product itself. Use when adding or upgrading dependencies, handling
  credentials, wiring release automation, or answering a customer security questionnaire.
  Triggers: supply chain, dependency, sbom, provenance, slsa, sigstore, lockfile, pinning,
  secrets, secret management, vault, secret rotation, ci/cd security, access token,
  dependabot, typosquatting, postinstall.
aliases: [sec-supply-chain]
triggers: [supply chain, dependency, sbom, provenance, slsa, sigstore, lockfile, pinning, secrets, secret management, hashicorp vault, secret rotation, ci/cd security, access token, dependabot, typosquatting, postinstall, artifact signing]
tier: cross-cutting
hub: lead-security-architect
prerequisites: [lead-security-architect]
related: [devops-ci-cd, be-security-posture, devops-release-engineering, sec-threat-modeling, sec-authn-authz, sec-appsec-owasp]
domain: security
surfaces: ["*"]
defers_to: [framework-16]
rigor_role: load-chain
spec_version: "2.2"
---

# Security: Supply Chain and Secrets

Most of the code you ship was written by strangers, and most of the credentials that could end your
company are not in your source tree. This spoke owns both, plus the pipeline that joins them, because
a build system holds deploy credentials and therefore is a production system.

It carries stage 3 of [[16-security-operating-model]] ("scan in CI") and the credential half of stage
2. Governed by [[lead-security-architect]]. Tool commands and audit-evidence formatting live in
[[be-security-posture]]; pipeline implementation, caching, and workflow structure live in
[[devops-ci-cd]]. This spoke owns the **policy and the gates**: what may enter, what must be proven,
and what happens when a credential leaks.

---

## The supply-chain threat model

Seven distinct threats, each needing a different control. Treating "dependency risk" as one thing is
why most programs stop at a vulnerability scanner and miss the rest.

| Threat | What it looks like | Primary control |
|---|---|---|
| Known vulnerability in a dependency | A CVE lands in something you already ship | Continuous scanning plus a patch SLA |
| Malicious package | Typosquat, a name an AI tool hallucinated and someone registered, a look-alike scoped package | Intake gate, lockfile review, private registry allowlist |
| Compromised maintainer or hijacked release | A trusted package publishes a malicious version | Pinning, delayed adoption for non-security upgrades, provenance verification |
| Install-time execution | A lifecycle or build script runs on every developer machine and CI runner | Disable install scripts by default, allowlist the few that need them |
| Build-system compromise | The pipeline is modified, or a workflow is tricked into running attacker code with secrets | Pipeline identity, protected triggers, ephemeral runners, review-gated workflow changes |
| Artifact tampering | The deployed artifact is not the one that was built and tested | Immutable artifacts addressed by digest, signing plus verification at deploy |
| Transitive opacity | You cannot answer what you actually ship | SBOM generated at release and stored where it can be queried |

Model these against your own pipeline in [[sec-threat-modeling]] when the pipeline changes. A new
release path is a new trust boundary.

---

## Dependency intake

Adding a dependency is granting arbitrary code your process privileges, your environment variables,
and your network access. It deserves a decision, not a reflex.

| Question | Disqualifier |
|---|---|
| Does this earn its place, or is it a few lines of our own code? | A trivial utility with a large transitive tree |
| Is it maintained? Recent releases, responsive issues, more than one maintainer | Abandoned, or a single maintainer with no succession |
| How large is the transitive tree, and what is in it? | A tree you cannot skim, or one that duplicates existing dependencies |
| Does the name match exactly what the documentation says? | Any doubt at all, especially for a name a tool suggested rather than a human chose |
| Does it run install-time scripts? | Scripts with no stated reason |
| Is the license compatible with how you ship? | Copyleft in a distributed client, or an unclear license |
| Does the publisher provide provenance or signed releases? | Not a blocker today, but a strong tiebreaker |
| Can it be scoped narrowly, for example to build time only? | A build tool that lands in the runtime dependency set |

Practices that make the gate hold:

- **Review the lockfile diff, not just the manifest.** One added line in the manifest can add dozens
  of packages, which is where the risk actually arrives.
- **Disable install scripts by default** in the package manager configuration, and allowlist the
  handful that genuinely need them.
- **Prefer a delay on non-security upgrades.** Most malicious releases are discovered and pulled
  within days, so lagging slightly on convenience upgrades is a real control.
- **Proxy public registries through an internal one** where the organization supports it, so you gain
  caching, allowlisting, and scanning before a package is reachable.
- **Verify any package name a code-generation tool produced.** Registering names that AI tools
  hallucinate is an active technique, and the failure mode is that the install simply works.

---

## Pinning and reproducible installs

The install must produce the same bytes on a developer machine, in CI, and in the release job.
Anything else means the artifact you tested is not the artifact you shipped.

| Ecosystem | Committed lock | Verifying install |
|---|---|---|
| npm and compatible | `package-lock.json` | `npm ci`, never `npm install` in CI |
| Python | A hash-pinned requirements file, or a `uv` or Poetry lock | `pip install --require-hashes`, or the tool's own locked sync |
| Go | `go.sum` | `go mod verify`, and `GOFLAGS=-mod=readonly` |
| Rust | `Cargo.lock`, committed for binaries | `cargo build --locked` |
| Containers | Base images referenced by digest | Rebuild and compare, never rely on a moving tag |
| CI actions and plugins | Third-party actions pinned to a full commit SHA | A policy check that fails on tag references |

Additional rules:

- **No floating references anywhere**: not `latest`, not a major-version range on a build-critical
  tool, not a branch reference for an action.
- **A temporary version pin needs a comment** naming the advisory and the date you intend to remove
  it, so the pin cannot quietly become permanent.
- **Lockfile changes are reviewed by a human.** An automated upgrade bot may open the pull request; it
  may not merge without review on anything that changes the tree.

---

## Vulnerability response

Scanning is the easy part. The value is in triage that neither ignores real risk nor blocks the team
on unreachable noise.

| Severity on a shipped surface | Patch target | Gate behavior |
|---|---|---|
| Critical | Days, with an out-of-band release if needed | Blocks the build |
| High | Two weeks | Blocks the build |
| Medium | The next scheduled release, within about 90 days | Warns, tracked with an owner |
| Low | Next convenient upgrade cycle | Tracked only |

**Reachability triage before effort.** Ask, in order: is the vulnerable package in the runtime
dependency set or only in build tooling, is the vulnerable code path reachable from our own calls, and
does exploitation require an input we accept? A high-severity CVE in a build-only dependency is real
but not urgent; the same CVE on a request path is. Record the reasoning, because the next person will
ask the same question.

**Waivers are records, not silences.** A waiver names the finding, the reason, the accepting owner,
the compensating control if any, and an expiry date. An expired waiver fails the build. There is no
permanent waiver, and a waiver is never a global rule disable.

**Zero-day drill.** When a widely-publicized advisory lands, three questions decide your day: do we
ship this component anywhere, in which versions and services, and how fast can we release. If the
answers require investigation rather than a query, the SBOM below is the fix.

---

## SBOM and provenance

An SBOM is not paperwork. It is the query surface that answers the three zero-day questions in minutes
and the artifact enterprise procurement increasingly requires.

- **Generate at release, from the build**, not by re-resolving dependencies afterwards. An SBOM
  produced separately describes a different tree than the one you shipped.
- **Store it where it can be queried across releases**, so a new advisory can be matched against
  every version still running in production or at a customer.
- **Attach it to the release artifact** and keep it for as long as the version is supported.
- **CycloneDX or SPDX**, chosen for the consumer: format mechanics and generation commands are in
  [[be-security-posture]].

Provenance is the next rung and increasingly expected in enterprise deals:

- **Sign artifacts and verify at deploy.** An unverified signature is decoration; the gate is the
  verification step in the deploy path.
- **Emit build provenance** that records which source commit, which builder, and which inputs
  produced the artifact, so a tampered artifact fails verification rather than merely looking odd.
- **Know your maturity level and state it plainly** in questionnaires: scripted builds, then
  provenance generated by the build platform, then non-falsifiable provenance with a hardened builder.
  Claiming a level you cannot evidence is worse than claiming a lower one.

---

## The secret lifecycle

Six stages. A gap at any one of them is the gap that gets exploited.

| Stage | Requirement |
|---|---|
| Create | Generated with a cryptographic random source, adequate length, scoped to one consumer and one purpose |
| Store | In a managed secrets store, encrypted at rest, access controlled and access logged; never in source, never in an image layer, never in a wiki or ticket |
| Distribute | Injected at runtime, not baked into artifacts; the application reads it from the store or the platform, not from a repository |
| Use | Held in memory only, never logged, never in an error payload, never echoed to a support tool or an LLM prompt |
| Rotate | On a schedule, and instantly on suspicion; dual-read overlap so rotation is not an outage |
| Revoke | Immediate, with a known propagation time, and rehearsed at least once |

**Prefer credentials that cannot be stolen usefully.** Ranked best to worst: a federated workload
identity with no stored secret, a dynamically issued short-lived credential, a managed static secret
with automated rotation, a manually rotated static secret. Every step down that list adds an incident
you will eventually have.

**The leaked-credential runbook.** Order matters, and it is counterintuitive under pressure.

1. **Rotate first, investigate second.** The credential is compromised the moment it is exposed;
   nobody gets to argue about whether the repository was private.
2. **Revoke the old value** and confirm it now fails.
3. **Determine exposure window and blast radius**: what the credential could reach, and what it did
   reach, from access logs.
4. **Look for use**, not just for exposure. Absence of evidence in logs you never enabled is not
   absence of use.
5. **Purge where feasible**, but treat git history rewriting as cleanup, never as remediation.
6. **Fix the path that leaked it**, which is usually a missing scanner, a logging default, or a
   convenience workflow.
7. **Record it** as a threat-model delta and, if it revealed a durable lesson, a knowledge entry.

---

## Where secrets actually leak

Scanning source is table stakes. These are the paths that leak credentials in practice, and each needs
an owner:

- **Git history**, including deleted files, old branches, and commits in forks.
- **CI logs**, where masking fails on transformed values such as base64 or JSON-embedded secrets.
- **Client bundles and mobile binaries**, where any "private" key shipped to a device is public.
- **Error trackers and observability tools**, which capture request bodies, headers, and environment
  by default.
- **Infrastructure state files**, which store resource attributes including generated credentials in
  plaintext unless the backend is encrypted and access controlled.
- **Notebooks, scratch scripts, and local `.env` files** that get committed or shared.
- **Support and admin tooling** that renders a raw credential rather than a masked reference.
- **Screenshots and pasted logs in tickets and chat**, which no scanner covers.
- **LLM prompts and agent context**, where an environment dump or a config file becomes part of a
  request to a third party. Treat any agent context as an egress path.

Run secret detection in two places, because they catch different things: pre-commit on staged changes
to stop the leak, and in CI over full history to find what already happened. Verified-only mode keeps
the signal usable.

---

## The pipeline is production

The build system can deploy, so it is at least as sensitive as the environment it deploys to.

- **Federated identity instead of stored cloud keys.** The pipeline exchanges a short-lived
  workflow-scoped token for cloud credentials, so there is nothing to steal at rest. This is the
  single highest-value change most teams can make.
- **Separate build credentials from deploy credentials.** A build job needs registry write; it does
  not need production database access.
- **Scope per job, per environment.** Production secrets belong to a protected environment with
  required approvals, not to the repository's general secret set.
- **Never expose secrets to untrusted-contributor triggers.** Workflows that check out and run code
  from a fork while holding write-scoped credentials are the classic pipeline compromise, so keep
  those jobs secretless and split any privileged step into a separate, gated workflow.
- **Pin third-party actions and plugins to a commit SHA**, and review changes to workflow files with
  the same seriousness as changes to authorization code, because they are equivalent in power.
- **Ephemeral runners.** A reused runner carries the previous job's leftovers, including cached
  credentials and poisoned tool caches. Self-hosted runners handling untrusted code need isolation
  per job.
- **Protect the cache.** Build and dependency caches are writable by jobs and read by later builds,
  which makes them a persistence mechanism if a lower-trust branch can write what a release job reads.
- **Two-person control on release**, with the deploy path requiring an approval that the requester
  cannot grant themselves.

Workflow structure, caching mechanics, and gate configuration belong to [[devops-ci-cd]] and
[[devops-release-engineering]]; the policy above is the part that does not change with the vendor.

---

## Third-party risk inside the product

Supply chain is not only your build. It is anything executing in your customer's session or your
runtime.

- **Browser third-party scripts.** Analytics, chat widgets, and tag managers execute with full access
  to your authenticated page. Minimize them, load them with integrity checks where the vendor
  supports it, constrain them with CSP, and remember that a tag manager grants whoever holds its
  credentials the ability to inject script into your product.
- **Customer-installed integrations and OAuth apps.** Once you have a marketplace, third parties hold
  tokens into customer tenants. Scope grants narrowly, show customers what is installed and what it
  can reach, and make revocation self-service.
- **AI model and data provenance.** For product features built on models, record which model version,
  which provider, and what data leaves your boundary. Enterprise questionnaires now ask, and contracts
  increasingly forbid training on customer data.
- **Sub-processor obligations.** Every vendor that processes customer data usually must be disclosed,
  and adding one is a contractual event, not only an engineering one. Check before you introduce a new
  data-handling dependency.

---

## Verification and evidence

What must exist to call stage 3 complete, and what is retained as audit evidence:

| In CI, per pull request | In the release artifact | Retained |
|---|---|---|
| Dependency scan on the changed tree, gating on high and critical | SBOM for the exact build | Scan results and dispositions for the audit period |
| Secret scan on the diff, with full-history scanning on a schedule | Signature and provenance attestation | Waiver register with owners and expiries |
| Lockfile consistency check, failing on drift | Immutable digest reference | Rotation records for managed secrets |
| Container and infrastructure configuration scan where applicable | Verified base image digests | Deploy approvals and pipeline run logs |
| Action and plugin pinning policy check | Release notes naming the security-relevant upgrades | Access reviews for pipeline and secret-store permissions |

Audit-evidence framing for compliance conversations lives in [[be-security-posture]].

---

## Done-gates

Before supply-chain or credential work is ready for review:

- New dependencies passed the **intake questions**, and the **lockfile diff was reviewed**, not just
  the manifest.
- Installs are **reproducible and verifying**, with nothing floating and third-party automation pinned
  by digest or SHA.
- Scanners **gate on high and critical** for the changed surface, and every finding has a disposition
  with an owner and, if waived, an **expiry**.
- **SBOM generation is part of the release job**, not a side script, and the artifact is addressable
  by digest.
- Every new credential has a **named store, scope, expiry, rotation method, and revocation path**, and
  no static secret was added where a federated identity was available.
- **Secret detection covers the diff and the history**, and no secret appears in logs, bundles, state
  files, or agent context.
- Pipeline changes were reviewed as **privileged changes**, with no secret reachable from an
  untrusted-contributor trigger.
- Anything accepted rather than fixed is in the **accepted-risk register** with a review trigger, per
  [[sec-threat-modeling]].

---

## Absolute bans

- A secret committed to source control, an image layer, a client bundle, or a ticket.
- Long-lived cloud keys in CI where federated identity is available.
- Merging an automated dependency upgrade without a human reviewing the lockfile diff.
- Disabling a scanner, or applying a global suppression, to turn a build green.
- A waiver with no owner or no expiry.
- Deploying an artifact that was not built by the pipeline, or one whose signature is not verified.
- Running untrusted contributor code in a job that holds write-scoped credentials.
- Treating a git history rewrite as remediation for a leaked credential.

---

## Defers-to

- **Framework [[16-security-operating-model]] wins** on pipeline order, done-gates, and bans.
- **Implementation depth defers outward**: tool commands and compliance evidence to
  [[be-security-posture]], workflow and gate mechanics to [[devops-ci-cd]], release and rollback
  process to [[devops-release-engineering]]. Identity for humans and services is
  [[sec-authn-authz]]; exploit classes in your own code are [[sec-appsec-owasp]].
- **Scanners and the Cursor `review-security` plugin detect; this spoke decides.** Their output enters
  the triage and waiver rules above, and their silence is not evidence about maintainer compromise,
  pipeline permissions, or secret sprawl outside the repository.

## Related
- peer ↔ [[sec-threat-modeling]] · [[sec-authn-authz]] · [[sec-appsec-owasp]]
