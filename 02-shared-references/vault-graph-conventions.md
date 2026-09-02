---
tags: [shared-reference, graph, conventions]
created: 2026-07-23
status: active
---

# Vault Graph Conventions — typed edges & the retrieval preamble

_Two conventions that keep the vault a **connected, retrieval-friendly graph** rather than
a pile of loosely-linked notes. Companion to the freshness rule in
[[epistemic-standards]] §2 and the routing map in
[[workspace-ontology]]. Adopted 2026-07-23 (borrowed from the
`obsidian-second-brain` prior art during the bootstrap-generator feedback pass)._

## For future agent
- **TL;DR:** durable notes may declare **typed edges** (`relations:` frontmatter) and should
  open with a **`## For future agent`** retrieval block. Both are optional-but-encouraged on
  knowledge entries and decisions; skip them on ephemeral logs.
- **As of:** 2026-07 · **Status:** current
- **Audience:** `for: agent`

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

> **Scope — three distinct graphs, don't cross them.** (1) Skills already have their own richer typed
> graph in the `## Related` block (`foundation`/`applies-in`, `hub`/`spoke`, `peer`, `governed-by`/
> `governs`, `encodes-into`), validated by `09-tools/validate-links.py`. That
> is the **skill-load** graph — leave it exactly as it is. (2) This `relations:` frontmatter is the
> **epistemic** graph over *knowledge entries and decisions*. (3) The **domain artifact** graph is
> DSDS 0.20 for design-systems ([[dsds-constitution]]) and `domain-constitution/1.0` for other job
> contexts ([[domain-constitutions]]). They coexist; do not mix edge vocabularies.

Obsidian Graph View is a fourth picture: it only draws markdown `[[wikilinks]]` (and markdown
hrefs to `.md` files). Dataview is not an edge. Native Graph labels are filename stems, so
`SKILL.md` / `SESSION-STATE.md` collide unless you hover the path. Juggl is the alias-label
view (YAML `name` / `title`). Color groups + filter recipes: [[00-bootstrap/OBSIDIAN-SETUP]].

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

**Audience stamp (DSDS 0.20 `for:`).** Add one line when the note is durable:

- `**Audience:** for: agent` — retrieval / routing / anti-hallucination notes
- `**Audience:** for: all` — laws, floors, invariants (humans and agents)
- Omit or `for: human` — narrative rationale (agents may still read it)

Do not bulk-rewrite the vault. Stamp notes as they are touched. The machine-readable
projection of these stamps is [[dsds-constitution]] for design-systems and
[[domain-constitutions]] for other job contexts.

---

## Checking it

`/health` (workspace) and `wsx health` (generated workspaces) flag **orphan notes** (nothing
links to them), **dangling typed edges** (`relations:` pointing at a missing note), and **stale
claims** (`#stale` tags or `as of` dates past horizon). Run it as part of `/optimize`.

## Retrieving it

Trigger routing (Layer 0) is still the high-precision hot path. When vocabulary misses, use
Layer-1 lexical retrieval:

```
python3 09-tools/vault-retrieve.py "<free text>"
```

It FTS-searches frameworks / references / skills / preferences / memory / knowledge, prefers
`## For future agent` TL;DRs as snippets, and can one-hop expand via `relations:` and skill
`## Related`. Index is machine-local (`.claude/state/vault-retrieve/`), rebuilt from git.

**Claude Code wiring:** SessionStart refreshes the index; UserPromptSubmit runs
`--cached` (stopwords + OR min-overlap) only when Layer 0 under-fires
(< 2 unique targets), cap 2. Golden set: `python3 09-tools/vault-retrieve.py --eval`.
**Cursor / other surfaces:** call the CLI on demand (no prompt-hook equivalent).
