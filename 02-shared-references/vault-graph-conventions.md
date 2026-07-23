---
tags: [shared-reference, graph, conventions]
created: 2026-07-23
status: active
---

# Vault Graph Conventions — typed edges & the retrieval preamble

_Two conventions that keep the vault a **connected, retrieval-friendly graph** rather than
a pile of loosely-linked notes. Companion to the freshness rule in
[epistemic-standards](epistemic-standards.md) §2 and the routing map in
[workspace-ontology](workspace-ontology.md). Adopted 2026-07-23 (borrowed from the
`obsidian-second-brain` prior art during the bootstrap-generator feedback pass)._

## For future agent
- **TL;DR:** durable notes may declare **typed edges** (`relations:` frontmatter) and should
  open with a **`## For future agent`** retrieval block. Both are optional-but-encouraged on
  knowledge entries and decisions; skip them on ephemeral logs.
- **As of:** 2026-07 · **Status:** current

---

## 1. Typed edges (`relations:`)

Beyond plain `[[wikilinks]]`, a durable note may declare *typed* relationships in its
frontmatter, so the graph is queryable by **relationship kind**, not just "linked":

```yaml
relations:
  builds-on:   ["[[radix-derived-color-system]]"]  # extends / depends on it
  relates-to:  ["[[a2ui-catalog]]"]                 # same topic area
  contradicts: ["[[some-other-note]]"]              # tension with; both currently held
  refutes:     ["[[an-earlier-claim]]"]             # supersedes / disproves it (target now wrong)
  exemplifies: ["[[a-general-principle]]"]          # a concrete instance of its general idea
```

Five relations, no more — the value is a *small, shared* vocabulary. Use them where the
relationship carries meaning (knowledge entries, `memory/decision-*`, framework cross-refs);
don't bother on session logs or daily notes. `refutes` is especially load-bearing: it's how a
superseded claim is *marked* superseded instead of silently lingering.

> **Scope — two distinct graphs, don't cross them.** Skills already have their own richer typed
> graph in the `## Related` block (`foundation`/`applies-in`, `hub`/`spoke`, `peer`, `governed-by`/
> `governs`, `encodes-into`), validated by [validate-links.py](../09-tools/validate-links.py). That
> is the **skill-dependency** graph — leave it exactly as it is. This `relations:` frontmatter is the
> **epistemic** graph over *knowledge entries and decisions* (what builds on / refutes what). They
> coexist: skills → `## Related`; knowledge/memory → `relations:`.

## 2. The `## For future agent` preamble

Durable notes (knowledge entries, decisions, project SESSION-STATE, longer references) open
with a short block written **for the next agent's retrieval**, not for human reading:

```markdown
## For future agent
- **TL;DR:** one line — what this note is and its current bottom line.
- **Key claims:** the load-bearing facts (each timeless / dated / pointer per §2 of epistemic-standards).
- **As of:** YYYY-MM · **Status:** current | aging | stale
```

Token-frugal by design (the workspace's #1 priority): an agent reads this block, then decides
whether the rest is worth the tokens. It also front-loads the recency markers so stale content
announces itself.

---

## Checking it

`/health` (workspace) and `wsx health` (generated workspaces) flag **orphan notes** (nothing
links to them), **dangling typed edges** (`relations:` pointing at a missing note), and **stale
claims** (`#stale` tags or `as of` dates past horizon). Run it as part of `/optimize`.
