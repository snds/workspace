---
name: sec-threat-modeling
description: >
  Structured threat modeling as a repeatable design-time practice for enterprise B2B SaaS.
  Owns the method: data-flow diagrams and trust boundaries, STRIDE per element, PASTA for
  architecture-level scope, attack trees and abuse cases, likelihood-times-impact risk ranking
  (DREAD/CVSS), the THREAT-MODEL.md artifact shape, and how a model plugs into design review,
  PR review, and the accepted-risk register. Use at design time for any feature handling
  untrusted input, secrets, money, PII, or cross-tenant data. Triggers: threat model, STRIDE,
  PASTA, attack tree, trust boundary, data flow diagram, attack surface, risk assessment,
  abuse case, DREAD, security design review, tenant isolation.
aliases: [sec-threat-modeling]
triggers: [threat model, stride, pasta, attack tree, trust boundary, data flow diagram, attack surface, risk assessment, abuse case, dread, security design review, tenant isolation, blast radius, accepted risk]
tier: cross-cutting
hub: lead-security-architect
prerequisites: [lead-security-architect]
related: [be-security-posture, sec-authn-authz, sec-appsec-owasp, sec-supply-chain]
domain: security
surfaces: ["*"]
defers_to: [framework-16]
rigor_role: measurement
spec_version: "2.2"
---

# Security: Threat Modeling

Asking "what can go wrong?" systematically, at design time, when the fix is a paragraph instead of
an incident. This spoke owns the **method and its artifact**. It is the first stage of the pipeline in
[[16-security-operating-model]], and its output is the gate that lets the rest of the work start.

Governed by [[lead-security-architect]]. Backend-specific application of STRIDE to SaaS API
endpoints, plus the concrete DFD notation and DREAD scoring mechanics, live in
[[be-security-posture]]; this spoke owns the discipline-level practice that applies to frontend,
backend, infrastructure, and integration work alike.

---

## When to threat-model (and when not to)

Threat modeling is a design activity with a real time cost. Spend it where the surface warrants it.

| Situation | Method | Scope and effort |
|---|---|---|
| New feature touching untrusted input, secrets, money, PII, or another tenant's data | STRIDE | Feature DFD, 2 to 4 hours |
| New endpoint on an existing, already-modelled surface | STRIDE delta | Diff against the existing model, 30 minutes |
| New service, new datastore, or major refactor of a trust boundary | STRIDE plus PASTA stages 1 to 3 | Service boundary, half a day |
| New third-party integration, webhook, or outbound callback | STRIDE, focused on Spoofing and Information disclosure | Integration boundary, 1 to 2 hours |
| New architectural pattern (queue, cache, edge worker, AI/LLM call) | PASTA | Full system segment |
| Post-incident review | STRIDE retrospective on the affected components | Whatever the incident touched |
| Annual review, SOC 2 readiness, or customer security questionnaire | PASTA | Full system |

**Skip it** for changes with no boundary effect: copy edits, styling, refactors that move code without
changing who can call it, and additions behind an existing, already-modelled authorization check. Say
so explicitly rather than silently skipping, so the absence is a decision and not an oversight.

**Never skip it** for anything that introduces a new trust boundary, a new credential, a new
cross-tenant code path, or a new way for a user to cause the server to fetch, execute, or render
something.

---

## Step 1: Map the system

You cannot model what you have not mapped. Draw the **data-flow diagram** before enumerating anything.

Identify, for the scope you chose:

- **External entities**: user browsers, mobile clients, the identity provider, partner APIs, webhook
  senders and receivers, support tooling, the CI runner.
- **Processes**: gateway, service, background worker, scheduled job, edge function, LLM call.
- **Data stores**: primary database, cache, object storage, search index, message queue, audit log,
  analytics warehouse.
- **Data flows**: each arrow labelled with its protocol and the data classification it carries.

Then mark the **trust boundaries**: every place data moves from a less-trusted zone to a more-trusted
one. In enterprise B2B SaaS the recurring ones are:

1. Internet to edge/gateway (unauthenticated to authenticated).
2. Authenticated user to tenant-scoped data (**the tenant isolation boundary**, the highest-consequence
   one in a multi-tenant product).
3. Tenant user to admin or cross-tenant surface (support console, back office, internal tooling).
4. Application to third-party service, and third-party callback back into the application.
5. CI/CD pipeline to production (the pipeline holds deploy credentials, so it is a production system).
6. Customer's IdP to your session layer (SSO, SCIM provisioning, group-to-role mapping).

Threat density is highest at boundary crossings. Model those first; interior flows rarely repay the
same effort.

---

## Step 2: STRIDE per element

STRIDE is a **prompt set**, not a taxonomy to admire. Its value is that it stops you enumerating only
the threats you already had in mind. Walk every boundary-crossing element and ask all six.

| Prompt | The question to ask of this element | Typical B2B SaaS instance |
|---|---|---|
| **S**poofing | Can someone claim an identity that is not theirs? | Forged or replayed token, stolen API key, unverified webhook sender, SAML assertion replay |
| **T**ampering | Can data be modified in flight or at rest without detection? | Parameter or price tampering, mass assignment, mutable audit log, cache poisoning |
| **R**epudiation | Could an actor deny having done this? | No audit event, no request-correlation id, log written by the actor being audited |
| **I**nformation disclosure | Can data reach a party not entitled to it? | Cross-tenant read, over-fetched response fields, stack trace, PII in logs or analytics |
| **D**enial of service | Can availability be degraded cheaply? | Unbounded query or page size, expensive nested query, no rate limit on an expensive path |
| **E**levation of privilege | Can an actor gain rights they were not granted? | Missing function-level check, role escalation via nested resource, tenant id taken from the request |

Two discipline rules that separate a real pass from a checkbox:

- **Cover the category or say why not.** "Repudiation: not applicable, this endpoint is read-only and
  emits no state change" is a complete answer. Silence is not.
- **One threat per row, phrased as an attacker action.** "An authenticated user in tenant A changes the
  `account_id` path parameter and reads tenant B's invoices" is actionable. "Access control issues" is not.

For the backend-endpoint form of this table, with SaaS-specific examples per category, read
[[be-security-posture]] rather than re-deriving it.

---

## Step 3: PASTA for architecture-level scope

STRIDE enumerates threats against a design you already have. **PASTA** (Process for Attack Simulation
and Threat Analysis) works backwards from business impact and is the right instrument when the
architecture itself is the question. Its seven stages, and what each produces here:

1. **Business objectives**: what data, which SLAs, which compliance scope, what a breach would cost
   commercially (contract terms, breach notification obligations, customer trust).
2. **Technical scope**: which systems, APIs, and third parties are in play.
3. **Application decomposition**: the DFD, trust boundaries, and data classification from step 1.
4. **Threat analysis**: which adversary classes realistically target this, and with what tactics.
5. **Vulnerability analysis**: map known weaknesses and CVEs onto the decomposed architecture.
6. **Attack modelling**: build the attack trees (step 4 below) for the highest-value goals.
7. **Risk and impact analysis**: business impact, likelihood, prioritized residual risk.

Use PASTA when evaluating a new system architecture, assessing an acquisition or vendor, or preparing
for a SOC 2 Type II readiness assessment. Use STRIDE for the feature ticket. Running PASTA on a form
field is theatre; running STRIDE on a platform migration misses the interesting threats.

---

## Step 4: Think like the attacker

STRIDE finds threat categories. **Attack trees** find the path an adversary actually takes, which is
usually a chain of individually-acceptable weaknesses.

Structure: **goal** at the root, **sub-goals** beneath it, **methods** as leaves, with AND/OR
semantics on the branches.

```
Goal: read tenant B's data while authenticated as a tenant A user
├── OR  guess or enumerate a tenant B resource id
│        └── AND ids are sequential  AND  the handler omits the tenant filter
├── OR  get the server to fetch it on my behalf
│        └── AND an export/report endpoint accepts a resource reference
│                 AND that reference is resolved without re-checking tenancy
├── OR  become a tenant B principal
│        └── OR  SCIM provisioning maps my email into tenant B's directory
│            OR  an invitation flow accepts an unverified domain claim
└── OR  read it from a shared surface
         └── OR  a shared cache key omits the tenant id
             OR  a search index is not tenant-partitioned
             OR  an analytics export aggregates across tenants
```

Two habits that make trees productive:

- **Abuse cases**, not just misuse. Ask what a *legitimate* feature does when used with hostile
  intent: bulk export used for exfiltration, invitations used for tenant grafting, webhooks used as an
  SSRF primitive, a rich-text field used as a stored XSS vector, an AI prompt field used to exfiltrate
  system context.
- **Assume the attacker has more than you think.** They have your client source, they control the
  client entirely, they can replay and forge requests, they can read your public docs and your job
  postings, and they are patient. The question is never "would someone bother?" but "what happens when
  someone does?"

---

## Step 5: Rank, then mitigate

Ranking exists to decide **what to fix first**, not to produce a number. Two scoring models, both
acceptable:

- **Likelihood times impact**, on a simple 1 to 5 scale each. Fast, sufficient for feature-level work,
  and legible to non-security reviewers.
- **DREAD or CVSS**, when you need to align with a security team's tooling or a customer's expected
  format. See [[be-security-posture]] for the mechanics.

Whichever you use, apply these adjustments, which matter specifically in B2B SaaS:

- **Cross-tenant impact escalates by one band, minimum.** A confidentiality failure that crosses the
  tenant boundary is a reportable breach with contractual consequences, not a bug.
- **Regulated data escalates.** PII, PHI, and payment data carry notification obligations that dwarf
  the engineering cost of the fix.
- **Discoverability is not a control.** "The id is a UUID so nobody will find it" lowers likelihood
  slightly and lowers impact not at all. Never let obscurity carry a ranking.

Then, for every threat, exactly one of four dispositions. There is no fifth, and there is no blank:

| Disposition | What it requires |
|---|---|
| **Mitigate** | A named control, an owner, and a **verification method** (the test, scan, or reproduction that proves it works) |
| **Transfer** | The party now carrying it, named, with the contractual or architectural mechanism |
| **Accept** | An entry in the accepted-risk register: the risk, who accepted it, the date, and the review trigger |
| **Eliminate** | The feature, field, or flow is removed. Frequently the cheapest and most overlooked option |

Route the control specifics outward rather than restating them here: identity and access controls to
[[sec-authn-authz]], input/output and vulnerability-class controls to [[sec-appsec-owasp]], dependency,
secret, and pipeline controls to [[sec-supply-chain]].

---

## The artifact: `THREAT-MODEL.md`

The model is only real if it is written down in a shape a later reader can check. This is the required
artifact for stage 1 of [[16-security-operating-model]]. Keep it next to the code it describes, in the
repository, versioned with the feature.

```markdown
# Threat model: <feature or service>

Scope: <what is in, what is explicitly out>
Method: STRIDE | PASTA (stages n to m)
Authors + date: <who, when>
Reviewed by: <who, when>

## 1. Asset and adversary contract
Assets: ...
Data classification: public | internal | confidential | regulated (PII/PHI/PCI)
Adversary classes: unauthenticated internet | authenticated tenant user | cross-tenant user |
                   insider or support agent | compromised dependency | compromised CI runner
Blast radius budget: <what one compromised credential may reach, at most>
Compliance scope: <controls this surface must produce evidence for>

## 2. Data-flow diagram
<diagram or mermaid, with trust boundaries marked and numbered>

## 3. Threats
| # | Boundary | STRIDE | Threat (attacker action) | Likelihood | Impact | Disposition | Control | Owner | Verified by |
|---|---|---|---|---|---|---|---|---|---|

## 4. Attack trees
<trees for the highest-value goals>

## 5. Accepted risks
| # | Risk | Accepted by | Date | Review trigger |
|---|---|---|---|---|

## 6. Out of scope
<what this model deliberately does not cover, and which model does>
```

The two columns that make this artifact load-bearing are **Verified by** and **Accepted by**. Without
them it is a document; with them it is a gate. A model whose Verified-by column is empty has not
completed stage 1, regardless of how thorough the threat table looks.

---

## Integration with reviews

A threat model that lives only in its own file gets written once and never consulted. Wire it into the
review surfaces the team already uses.

**Design review.** The model is an input to the design review, not an output of it. Bring the DFD and
the ranked threat table; walk the boundaries. The design review's security question is exactly one
question: *does every Critical and High threat have a control, an owner, and a verification method?*
If the answer is no, the design is not approved, in the same way an unresolved layout question blocks
a visual design review.

**PR review.** The model turns into review criteria. In the PR description, link the model and name
which threats this diff mitigates. The reviewer's job is then concrete: find the enforcement point in
the diff and confirm it matches the control the model promised. This is what makes
[[07-integration-and-review-framework]]'s small-diff rule load-bearing for security work: an
enforcement point you cannot locate in the diff is one you cannot review.

**Change triggers.** Re-open the model when any of these happen, and record the delta rather than
rewriting from scratch: a new trust boundary, a new external integration, a new credential, a change
to the tenancy model or the identity provider relationship, a new data classification on an existing
flow, or an incident touching the modelled components.

**Handoff to the evaluate pass.** The `review-security` plugin runs over a diff and detects findings.
The model is what lets you triage those findings: a finding that maps to an accepted risk is noise, a
finding that contradicts a Verified-by claim is a regression, and a finding with no corresponding
threat means the model has a gap. Detection is the plugin's job; deciding is this spoke's job.

---

## Failure modes of the practice itself

The practice fails in predictable ways. Watch for these in your own output:

- **Enumerating without ranking.** A 60-row threat table with no priority is a way of doing nothing
  thoroughly.
- **Modelling the design you wish you had.** Model the system as built, including the shortcut that
  shipped last quarter.
- **Stopping at the categories.** STRIDE without attack trees misses chained weaknesses, which is how
  real compromises happen.
- **Treating obscurity, client-side checks, or "internal only" as controls.** None survive contact with
  an attacker who has your client.
- **Letting the model go stale.** An unmaintained model is worse than none, because it launders a stale
  assumption as a reviewed one.
- **Modelling after the code is written.** Then it is a justification exercise, not a design activity.
  The whole economic argument for threat modeling is that design-time fixes are nearly free.

## Related
- hub → [[lead-security-architect]]
- peer ↔ [[sec-authn-authz]] · [[sec-appsec-owasp]] · [[sec-supply-chain]]
