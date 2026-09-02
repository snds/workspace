# Security Operating Model

*Domain L1 for application security as a sideways quality dimension, instantiating the [Domain Rigor Stack](13-domain-rigor-stack.md) for the security cluster. Where `eng-foundations` answers "what makes a boundary correct?" and [#11 Anticipatory Failure Analysis](11-anticipatory-failure-analysis.md) answers "how will this fail before anyone sees it fail?", this framework answers "how do we decide what to protect, prove it is protected, and refuse to ship what is not?" It sits above every security skill. Implementation depth for SaaS APIs lives in `be-security-posture`; this framework owns the pipeline and the done-gates for the whole discipline.*

---

## The core conviction

**Threat-model at design time, verify continuously, fail closed.** Security is a property designed in and verified continuously, never a phase at the end. Every change crossing a trust boundary names its threats before the code exists, enforces authorization server-side on every request, passes automated scans in CI, and is observable in production. Where a control's state is unknown, the system denies.

Security bolted on after ship is theater. "We will harden later" is not a plan; it is a decision to ship a known vulnerability with a promise attached. A passing test suite is not evidence of a security control, and an author's assertion that a check exists is not evidence that it fires. Every new trust boundary is a design decision about blast radius.

The operating context for this workspace is **enterprise B2B SaaS**: multi-tenant, SSO-integrated, audited. That makes **tenant isolation the highest-consequence invariant in the system**. A cross-tenant read is not a bug of the same class as a broken button; it is a reportable breach.

---

## When this framework invokes

Default-active for any work touching: authentication or authorization, new external interfaces, multi-tenancy, untrusted input, secrets or credentials, a new or upgraded dependency, the CI/CD pipeline, PII or payment data, a new integration or webhook, OWASP-class bugs, incident response, SOC 2 engineering evidence, or anything that can exfiltrate or corrupt tenant data.

Load at minimum with [#11 Anticipatory Failure Analysis](11-anticipatory-failure-analysis.md) (security failure modes are the most catalogued failure modes in software; retrieving them at planning time is the whole game) and [#14 Engineering Operating Model](14-engineering-operating-model.md) (this framework specializes its contract, review, and CI stages rather than replacing them). Foundation: `eng-foundations`.

Operational surface: `lead-security-architect` (the L2 execution protocol and router) into the `sec-*` spokes. Backend implementation detail: `be-security-posture`. Evaluate aid: the Cursor `review-security` plugin, where **workspace doctrine wins** (see [AGENTS.md](../AGENTS.md) and the Defers-to section on the hub).

Security is applied **sideways**, the same posture as accessibility. It is a dimension of every discipline's work, not a stage that follows them.

---

## 1. Asset and adversary contract (before design)

No technique is chosen until the thing being defended and the party it is defended against are written down. Record in the feature's `THREAT-MODEL.md`, or the threat-model section of its ADR:

| Field | What it fixes |
|---|---|
| **Assets** | What an attacker wants here: tenant data, credentials, money, compute, reputation, availability |
| **Data classification** | Public / internal / confidential / regulated (PII, PHI, PCI). Drives retention, logging, and encryption obligations |
| **Adversary classes** | Unauthenticated internet, authenticated tenant user, cross-tenant user, insider or support agent, compromised dependency, compromised CI runner |
| **Trust boundaries** | Every place data moves from a less-trusted zone to a more-trusted one |
| **Blast radius budget** | What one compromised credential, token, or service may reach at most |
| **Compliance scope** | Which controls this surface must produce audit evidence for |

Vague direction ("make it secure", "add auth") is rejected at threat-model time the same way an unnamed reference is rejected in visual work. Name the adversary or there is no contract.

---

## 2. The pipeline

Four ordered stages. Each has a **done-gate** and **required artifacts**. A stage is not complete because its work happened; it is complete because its artifact exists and its gate is satisfied.

```
threat-model-at-design  →  secure-build  →  scan-in-CI  →  monitor / respond
        (cheap fixes)        (enforcement)   (regression)     (detect + recover)
```

### Stage 1: Threat model at design

**Activity.** Draw the data-flow diagram, mark trust boundaries, run **STRIDE** per element for feature-level work or **PASTA** for architecture-level work (new service, new integration, acquisition review). Build attack trees for the highest-value goals. Rank by likelihood times impact. Assign each ranked threat a control, an owner, and a verification method.

**Done-gate.**
- Data-flow diagram exists with trust boundaries, assets, and actors marked.
- STRIDE covered per boundary-crossing element, or a documented reason a category is not applicable.
- Risks ranked; every Critical and High threat has a named control, an owner, and a verification method.
- Accepted risks are explicit, in writing, with who accepted them and an **expiry or review trigger**, not silently dropped.

**Required artifacts.** `THREAT-MODEL.md` containing the DFD, the **STRIDE or PASTA notes**, the ranked threat table, and the accepted-risk register. Attach it to the ADR or PR so a reviewer can check the code against it.

### Stage 2: Secure build

**Activity.** Implement the controls. Authorization is enforced server-side, at the object level, on every request, scoped to the authenticated tenant. Input is validated against a schema at the boundary; output is encoded for its sink. Least-privilege identities throughout. Secrets come from a manager at runtime, never from git. Errors are generic to the caller and detailed only in internal logs. Security-relevant events are logged in structured form.

**Done-gate.**
- The **auth decision table** is filled: for every endpoint, operation, or resource, which principal, which authn mechanism (which flow for which client), which scope or role, which tenant condition, enforced where in the code.
- Every tenant-scoped query is tenant-filtered at the data layer, verified by reading the enforcement point rather than by assumption.
- Negative tests exist and fail correctly: unauthenticated, wrong tenant, wrong role, expired or tampered token.
- No secret is present in source, fixture, bundle, log, or error path. No new long-lived god tokens.

**Required artifacts.** The **auth decision table** (in `THREAT-MODEL.md` or its own ADR, and referenced from the PR), the negative test cases, and the **secrets policy** entry naming where each new secret lives, who owns it, and how it rotates.

### Stage 3: Scan in CI

**Activity.** Make the controls regression-proof. Secret scanning on staged changes and over history. SAST on the diff. Dependency vulnerability scanning with a severity policy. Container and IaC scanning where applicable. SBOM generation attached to the release artifact. These run as blocking checks, not advisory annotations.

**Done-gate.**
- Pipeline gates on High and Critical for the changed surface. Findings are triaged into fix, waive-with-owner, or false-positive, and **waivers expire**.
- Secret scanning is blocking, and the pre-commit path is installed locally.
- SBOM is generated from the built artifact and attached to the release.
- CI credentials are short-lived and federated (OIDC), not long-lived static keys.
- **Scanner results** are stored with tool name, version, and ruleset recorded, so a later "it was clean" claim stays checkable.

**Required artifacts.** **Scanner results** (secret scan, SAST, dependency scan, container/IaC where applicable) with tool/version/ruleset, the SBOM, and the exception register with owners and dates.

### Stage 4: Monitor and respond

**Activity.** Assume the controls will be probed and eventually one will fail. Ship the detection and the recovery path with the feature, not after the first incident.

**Done-gate.**
- Authentication and authorization outcomes, privilege changes, and sensitive-data access emit structured events with actor, tenant, and request-correlation ids.
- At least one detection exists for each new risk class, plus alerts for the threats ranked Critical or High. Runtime signals include auth anomalies, rate-limit and WAF events, and integrity checks.
- A runbook names the revocation and rotation path for every credential this feature introduced, and the containment step for its worst-case threat. Linked from the PR if the risk is customer-impacting.
- Log content is checked against the never-log list (see bans).

**Required artifacts.** The audit-event schema, the alert definitions, and the runbook section covering revoke, rotate, and contain.

---

## 3. Done-gate summary

| Stage | Gate in one line | Artifact that proves it |
|---|---|---|
| Threat model | Every Critical/High threat has a control, owner, and verification method; accepted risks have expiries | `THREAT-MODEL.md`: DFD + STRIDE/PASTA notes + ranked table + accepted-risk register |
| Secure build | Authorization enforced server-side per request, and negative tests fail correctly | Auth decision table + negative test cases + secrets policy entry |
| Scan in CI | Blocking secret, SAST, and dependency scans pass, or waivers are owned and dated | Scanner results (tool/version/ruleset) + SBOM + exception register |
| Monitor/respond | The Critical threats are detectable and every credential is revocable on a named path | Audit-event schema + alerts + runbook (revoke/rotate/contain) |

A security claim citing only "reviewed the code" is **incomplete**. So is one citing only a green pipeline.

---

## 4. Evidence hierarchy

Highest trust to lowest:

1. **Reproduced attack, then a test that fails before the fix and passes after.** The strongest evidence a control works is a demonstration that its absence was exploitable.
2. **Scanner or harness output**, with tool name, version, and ruleset named.
3. **Read the enforcement point.** The actual line where the tenant filter or role check executes, on the path the request takes.
4. **Author or agent assertion** that the control exists. A locator for where to look, never a verdict.

Tier 4 presented as tier 1 is the security equivalent of judging a render from a thumbnail. Name the tier.

---

## 5. Absolute bans

- **Secrets or private keys committed to git.** Source, config, fixtures, comments, commit messages, client bundles. Once committed, treat as compromised and rotate; scrubbing history is cleanup, not remediation.
- **"We will harden later"** on anything, and especially on authorization for tenant isolation. Deferring a control is a risk acceptance with a named owner and expiry, or it does not ship.
- **Trusting client input.** Client-supplied tenant ids, user ids, roles, or prices without server-side checks. Also hidden fields, `Origin` echoes, and anything a proxy could have set.
- **Hide-the-button as authorization.** Absence of UI is not access control. Every enforcement point is server-side.
- **Disabling or downgrading scanners to go green.** A scan nobody can fail is documentation, not a gate.
- **Copy-pasting JWTs, tokens, or credentials into logs**, tickets, or chat. Also passwords (even wrong ones), session ids, full card numbers, full SSNs. Log a hash for correlation.
- **Unpinned algorithm verification.** Accepting the token's own `alg` claim, or verifying without pinning issuer, audience, and expiry.
- **Wildcard or reflected CORS with credentials.** Allowlist explicit origins.
- **Verbose errors to the caller.** Stack traces, SQL text, internal hostnames, and file paths are disclosure.
- **String-built queries or commands.** Parameterize, or use the safe API. Prior sanitization does not license concatenation.
- **Long-lived static credentials in CI.** Use federated short-lived tokens.
- **Treating `be-security-posture` as a substitute for this pipeline.** It is depth, not the gate.
- **Plugin or marketplace security defaults overriding workspace doctrine.** Workspace frameworks beat workspace skills beat installed plugin skills.

---

## 6. Fail-closed rules

When the state of a control is unknown, the answer is deny. Concretely:

- Authorization decision cannot be computed (policy service down, claim missing): deny, do not fall through to the permissive branch.
- Token signature, issuer, audience, or expiry cannot be verified: reject.
- Tenant context is absent from a tenant-scoped query path: error, never query unscoped.
- A blocking scanner cannot run in CI: the pipeline fails. A skipped gate is a failed gate.
- Rate limiter or bot-detection dependency is unavailable on an authentication endpoint: throttle conservatively rather than open the gate.

Fail-closed has a usability cost and that cost is the point. Where fail-closed is genuinely unacceptable (availability-critical read paths), the exception is written into the threat model with its compensating control.

---

## 7. Operating sequence

1. **`scope`**: Resolve the asset and adversary contract (section 1). Confirm compliance scope and data classification.
2. **`model`**: STRIDE or PASTA, attack trees, ranked threats, controls assigned. Gate 1.
3. **`decide`**: Fill the auth decision table and the identity/token model choices before writing the handler.
4. **`build`**: Implement controls; negative tests alongside. Gate 2.
5. **`scan`**: Wire or run the blocking CI checks; generate the SBOM. Gate 3.
6. **`prove`**: Reproduce at least the top-ranked threat against the built system and show it now fails. Evidence tier 1 or 2.
7. **`instrument`**: Audit events, alerts, runbook. Gate 4.
8. **`evaluate`**: Run the `review-security` plugin over the diff as a second pass. Triage its findings against this doctrine; it detects, this framework decides.
9. **`accept`**: Anything unfixed goes into the accepted-risk register with owner and expiry, or the work is not done.

---

## 8. `be-security-posture` versus `lead-security-architect`

Two different jobs; both are needed, and the distinction is what keeps the cluster from collapsing into one over-long file.

| | `lead-security-architect` (discipline hub) | `be-security-posture` (implementation depth) |
|---|---|---|
| **Tier** | `hub`, domain `security`, prerequisite `eng-foundations` | `spoke` of `lead-backend-engineer`, domain `engineering` |
| **Owns** | The discipline: convictions, the L2 execution protocol, the done-gate checklist, spoke routing, doctrine precedence | Backend mechanics: concrete header values, rate-limiter algorithm choice, secret-rotation phases, SOC 2 evidence tables, code-level snippets |
| **Answers** | "What must be true before this ships, and which lens do I load?" | "What exactly do I type in the backend to make it true?" |
| **Applies** | Sideways to design, frontend, backend, and devops work alike | Inside backend service work |
| **Authority** | Authoritative on doctrine and gates | Authoritative on backend implementation detail; defers to the hub on doctrine |

Routing rule: **enter through the hub, descend to the spoke.** Whether a control is required, which threat it answers, or whether the work is done routes to `lead-security-architect` and this framework. The exact CSP directive, bcrypt cost factor, token-bucket parameters, or SOC 2 evidence artifact routes to `be-security-posture`. When they disagree, the hub and this framework win; the spoke's depth is technique, not doctrine.

The four `sec-*` spokes sit between them: discipline-level depth (threat modeling, identity, OWASP classes, supply chain) that applies at any layer, not only the backend.

---

## Spoke routing

| Spoke | Owns |
|---|---|
| `sec-threat-modeling` | What can go wrong: STRIDE/PASTA, trust boundaries, attack trees, risk ranking, the `THREAT-MODEL.md` artifact |
| `sec-authn-authz` | Identity and permission models: OAuth/OIDC/JWT, sessions vs tokens, RBAC/ABAC/ReBAC, SSO/SAML/SCIM, the auth decision table |
| `sec-appsec-owasp` | Common exploit classes and SDLC checks: OWASP Top 10 + API Top 10, validate-at-entry vs encode-at-exit |
| `sec-supply-chain` | Dependencies, SBOM and provenance, signing, secrets, CI identity and token hygiene |

---

## Relationship to other frameworks

| Framework | Role relative to #16 |
|---|---|
| [#04 Research and Evidence](04-research-and-evidence-framework.md) | Confidence tiers behind the evidence hierarchy in section 4 |
| [#06 QA Operating Model](06-qa-operating-model.md) | Output-time honesty gate; a security report runs its pre-output gate |
| [#07 Integration and Review](07-integration-and-review-framework.md) | Security-relevant diffs stay small and single-purpose so the enforcement point is actually reviewable |
| [#11 Anticipatory Failure Analysis](11-anticipatory-failure-analysis.md) | Input-time twin: retrieve the known failure modes of the technique before building, not after the finding |
| [#13 Domain Rigor Stack](13-domain-rigor-stack.md) | This document is the security cluster's L1; the hub is L2, the scanners are L3 |
| [#14 Engineering Operating Model](14-engineering-operating-model.md) | The general engineering pipeline this one specializes at the security-relevant stages |
| `eng-foundations` | Boundary validation, contracts, and failure thinking, with teeth added here |

---

## Skills that carry the mechanics

- `lead-security-architect`: the L2 execution protocol, done-gate checklist, and routing hub
- `sec-threat-modeling`: STRIDE/PASTA, trust boundaries, attack trees, risk ranking
- `sec-authn-authz`: identity, tokens, sessions, RBAC/ABAC/ReBAC, enterprise SSO
- `sec-appsec-owasp`: the vulnerability classes and their fixes, secure SDLC checkpoints
- `sec-supply-chain`: dependencies, SBOM, provenance, secrets, CI/CD hygiene, signing
- `be-security-posture`: backend implementation depth
- `review-security` (plugin): the evaluate half; detection over a diff, subordinate to this doctrine

---

## Operating habits

- Name the adversary before naming the control.
- Fill the auth decision table before writing the handler.
- Enforce server-side, at the object level, scoped to the tenant, on every request.
- Write the negative test, not just the happy path.
- Make the scanner blocking, and record tool, version, and ruleset.
- Reproduce the threat, then show it fails. That is the only tier-1 evidence.
- Unfixed means registered, owned, and dated. Never merely mentioned.
- On unknown state, deny.

---

## Related

- [[13-domain-rigor-stack]]
- [[14-engineering-operating-model]]
- [[11-anticipatory-failure-analysis]]
- [[eng-foundations]]
- [[lead-security-architect]]
- [[be-security-posture]]
