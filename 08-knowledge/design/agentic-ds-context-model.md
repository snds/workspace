---
tags: [design-systems, ontology, knowledge-graph, context-model, agentic, dsds, harness]
created: 2026-09-01
updated: 2026-09-01
status: working
confidence: medium
sources:
  - "Workspace ontology + Framework #09 + ds-agents-binding (vault, current)"
  - "DSDS 0.20.0 — designsystemdocspec.org (fetched 2026-09-01)"
  - "Naeem Ul Haq — Agentic System Design guide, grokkingthesystemdesign.com (2026-01-21)"
  - "gtzheng/Awesome-Agentic-System-Design README (fetched 2026-09-01)"
  - "alirezadir/Agentic-AI-Systems — 2026 Agentic AI System Design Update (fetched 2026-09-01)"
  - "@ai-created/ui — ui.ai-created.com (fetched 2026-09-01)"
related_skills: [ds-advisor, ux-component-library, design-engineer, design-foundations]
related_projects: [19-workspace-brain]
relations:
  builds-on:
    - "[[component-contracts-and-schemas]]"
    - "[[09-component-and-pattern-framework]]"
  relates-to:
    - "[[agentic-error-correction-foundations]]"
    - "[[nate-jones-harness-enrichments]]"
    - "[[idempotent-design-decisions]]"
---

# Agentic design-system context model

A remapping of this workspace's ontology, graphs, and design-system context stack onto 2026
agentic specs. The operating claim: keep the intent model; project documentation onto DSDS 0.20;
do not invent a sixth schema.

## For future agent
- **TL;DR:** Three graphs (skill load, epistemic, DSDS artifact) + four intent types + a named
  harness loop. DSDS is the portable *documentation* view of facets 1–17. The contract schema
  still arbitrates. DESIGN.md stays lean visual identity.
- **Key claims:**
  - Complements, not competitors: DTCG = values · DSDS = meaning/usage · contract = arbitration ·
    DESIGN.md = look · A2UI = agent-to-UI wire format. (timeless, given those specs)
  - DSDS 0.20.0 collapsed the 0.15.2 shape (6 entity types × 17 kind blocks) into 5 well-known
    entry kinds + custom, and 3 section kinds + generic `section` / `freeform`. (dated 2026-09-01)
  - The vault already implements 2026 "context engineering" (select / compress / isolate / prove)
    under other names. The gap is a DSDS projection, not a new brain. (dated 2026-09-01)
- **As of:** 2026-09 · **Status:** working
- **Audience:** `for: agent`

---

## 1. What we already have

| Layer | Job | Canonical home |
|---|---|---|
| Ontology / routing | Where a write belongs | [[workspace-ontology]] |
| Skill load graph | Foundation → hub → spoke; lenses sideways | `skills.registry.json` + [[skill-frontmatter]] |
| Epistemic graph | builds-on / relates-to / contradicts / refutes / exemplifies | [[vault-graph-conventions]] |
| Intent delivery | Framing / workflow / guidelines / constraints | [[09-component-and-pattern-framework]] §1 |
| Documentation schema | 18 facets | Framework #09 §5 |
| Arbitration schema | Typed subset that can refuse | [[component-contract-schema]] |
| Always-on rules | Import, states, tokens, a11y, stay-in-system | [[ds-agents-binding]] |
| Visual identity | Portable look + rationale | `DESIGN.md` protocol, framework §12 |
| Agent-to-UI runtime | Trusted catalog, no tokens of its own | A2UI projection, framework §11a |

The 2026-07-28 contracts entry already mapped **facets 1–17 → DSDS**, **facet 18 → Specs/contracts**,
**token values → DTCG**. That mapping still holds. What changed is DSDS's own shape.

## 2. What the five sources own

| Source | Owns | Does not own |
|---|---|---|
| **DSDS 0.20.0** | Documentation as data. Entry kinds `system` / `component` / `token` / `theme` / `entry` (+ custom). Sections `guidelines` / `definitions` / `steps` / `section` + `freeform`. Audience `for: human \| agent \| all`. `shared[]`, `refs`, `combos`, `traits`, `sourceFiles`, `specs`. `$extensions`. | Token values (DTCG). Generated API (CEM / our contract). Runtime UI. |
| **Grokking agentic SD** | Roles, goals, tools-as-contracts, 3-tier memory, control strategies, multi-agent patterns, guardrail layers. | Design-system schemas. |
| **Awesome-Agentic-System-Design** | An index (IBM/Anthropic MCP, Gulli patterns, OpenAI/Anthropic guides, MCP/A2A/ANP/ACP survey). | A schema or a context model. |
| **2026 harness update** | Context engineering, long-running agents, AgentOps, eval-driven development, MCP (agent↔tool) vs A2A (agent↔agent), security, cost. | Component anatomy or brand. |
| **@ai-created/ui** | A living coded system: semantic-first tokens, accent vs meaning independence, product UX patterns as contract, same-pass doc discipline. | A multi-repo ontology or vault graph. |

Agreement across sources: prompts/policies/memory are architecture; tools are contracts with blast
radius; one file cannot hold the whole system; meaning stays separate from values and from runtime
API; agents need stop, escalate, and audit.

Conflict to keep explicit:

- Grokking optimizes autonomy. This workspace optimizes **refusal** and token cost. Keep refusal.
- @ai-created can keep one living `DESIGN-SYSTEM.md` because it *is* the product. A vault plus
  multi-surface DS cannot. The Atlassian field test still forbids a monolithic always-loaded dump.
- DSDS informs. The contract arbitrates. Do not merge them.
- A2A/A2UI are runtime. The vault is author-time context. Project a catalog; do not store the wire
  format as the ontology.

## 3. DSDS 0.20 projection

Map vault homes onto DSDS kinds. Do not invent a sixth kind.

| DSDS kind | Vault home | Must not copy into the DSDS file |
|---|---|---|
| `system` | DESIGN.md + [[ds-agents-binding]] + #09 constitution | Per-component anatomy |
| `component` | MCP intent record + 18-facet doc + signed contract | Token hex, CEM props |
| `token` | DTCG / Figma variables / DESIGN.md groups | The value itself (pointer only) |
| `theme` | DESIGN.md modes + density / accent axes | A second visual language |
| `entry` | `08-knowledge/design` patterns, foundations, guides | Live handoff / session state |
| `shared` | `a11y-visual`, `found-*`, #09 §8 laws | Component-local exceptions restated |

Audience stamp:

- Existing `## For future agent` blocks → `for: agent`
- Framework laws, invariants, a11y floors → `for: all`
- Narrative usage / rationale → `for: human` (agents still read them)

`combos` is the machine form of #09 composition laws (must / must-not pairing). Encode those
before inventing new pairing prose.

## 4. Seven-layer remap (name the loop, do not rebuild it)

```
L0 Harness            request → policy → context builder → act → eval → human gate
L1 Profile + route    who owns / reviews; where a write belongs
L2 Intent delivery    Wolosin four types → five delivery artifacts
L3 Three graphs       skill load · epistemic · DSDS artifact   (do not cross)
L4 Schema stack       DTCG · DSDS · contract · DESIGN.md · A2UI catalog
L5 Memory             short = session/working · long = knowledge/memory · shared = Live handoff
L6 AgentOps           validators, vqa, trust levels; later: cost/task, approval rate, traces
```

L0 is the dispatcher, doctor, ritual, and walls drawn as one path. L6 is already validators +
prove artifacts; do not build a new observability stack before a scheduled runner exists.

## 5. Moves worth doing / refuse

Worth doing:

1. Emit a **project-independent** DSDS 0.20 constitution as a view (done 2026-09-01:
   [[dsds-constitution]]). Projects extend it; they do not fork it.
2. Standing design *methods* live in [[idempotent-design-decisions]] (APCA/role-scale,
   overlay emphasis, one-light elevation). Values stay in the target system.
3. Stamp `for:` on preambles as notes are touched ([[vault-graph-conventions]]).
4. Composition `combos` live in the DSDS constitution, sourced from framework #09 §7.
5. Review upstream sources with [[ds-source-watch]] (report-first; never auto-edit ontology).
6. Keep [[component-contract-schema]] as facet-18 arbitration.

Refuse:

- A general-purpose agent role (Grokking's production failure mode).
- One always-loaded DS dump (Atlassian measurement).
- Merging the three graphs.
- Treating DSDS as the contract.

## 6. Working view

Interactive canvas (Cursor, not vault):
`/Users/snds/.cursor/projects/Users-snds-Projects-Workspace/canvases/ds-agentic-ontology.canvas.tsx`

Coverage bars on that canvas are a 2026-09-01 judgment, not a measured benchmark.

## Related

- [[component-contracts-and-schemas]] — four words, seven gates, the 0.15.2 DSDS note this entry updates
- [[09-component-and-pattern-framework]] — intent layers, 18 facets, AI-legible layer
- [[ds-agents-binding]] — always-on constraints
- [[workspace-ontology]] — routing map
- [[agentic-error-correction-foundations]] — independent measurement vs self-critique
- [[idempotent-design-decisions]] — standing methods (not style)
- [[dsds-constitution]] — DSDS 0.20 constitution view
- `ds-source-watch` skill — upstream source review (report-first)
