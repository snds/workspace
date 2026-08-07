---
type: decision
description: Defer dense/embedding vault retrieval until lexical golden-set shows unfixable paraphrase gaps.
created: 2026-08-05
confidence: high
relations:
  builds-on: ["[[decision-externalize-everything-to-workspace]]"]
  relates-to: ["[[vault-graph-conventions]]"]
---

## For future agent
- **TL;DR:** Dense (embedding) Layer-2 vault retrieval is **not** earned yet. Layer-1 lexical FTS + stopwords + OR min-overlap clears the golden set (13/13 as of 2026-08-05); add embeddings only when measured paraphrase misses remain after lexical fixes.
- **As of:** 2026-08 · **Status:** current

## Context — what forced a choice
Shipping `09-tools/vault-retrieve.py` raised whether to immediately add an embedding index (capability-registry, local/API model, hybrid rank). Dense retrieval costs dependency surface, index freshness complexity, and token/ops overhead against a portable-first, stdlib-preferring brain.

## Decision — what we chose
**Defer dense Layer 2.** Keep Layer 0 triggers primary and Layer 1 lexical as the fallback. Revisit only if `python3 09-tools/vault-retrieve.py --eval` accumulates FAIL cases that are true paraphrase gaps (not fixable by stopwords, chunking, or boosts).

## Rationale
- Golden set covers paraphrase hits, dispatcher-shaped queries, and negative procedural chatter — all green after stopword + OR min-overlap hardening.
- A capability with `fallback: degrade` is still a maintenance surface; earn it with measured misses.
- Token frugality: auto-inject stays capped at 2 and only when Layer 0 under-fires.

## Consequences
- No `embedding-*` capability in the registry for now.
- Eval fixture `09-tools/vault-retrieve.golden.json` is the gate for reopening this decision.
- Interactive CLI may still use non-strict OR fill; dispatcher uses `--cached` without graph expand.
