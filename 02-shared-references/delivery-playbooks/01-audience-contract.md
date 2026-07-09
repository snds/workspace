---
title: Audience Contract — who reads this, and who do they read it out to?
status: canonical
date: 2026-07-09
tags: [audience, voice, jargon, explanation, delivery]
---

# Audience contract — who reads this, and who do they read it out to?

The standing default for every deliverable, explanation, and artifact. Derived from the
context profile ([[00-context-profiles]]) — resolve that first.

---

## The default reader

**Primary:** Sean — a Staff/Lead UX designer. Expert in design systems, components, tokens,
Figma, UX patterns. *Not* an engineer: no assumed fluency in back-end architecture, data
science, infrastructure, or code-level vocabulary.

**Mandatory second reader:** Sean's design-focused managers — the people he reads deliverables
out to. Every artifact is written for two hops.

**The engineer-voiced exception:** only when the deliverable itself lives in an engineering
surface for engineer review — PR descriptions, commit messages, code comments in
`centric-engineering` repos. Even then, anything delivered *to Sean about* that work
(summaries, findings, explanations) stays designer-first.

---

## The forward test

Before delivering: **could Sean forward this to his manager unedited, with no translation
layer?** If he'd have to explain the explanation, it failed — regardless of technical accuracy.

## The jargon rule

Any unavoidable technical term gets a one-line plain definition at first use, inline. Terms
from Sean's own domain (tokens, variants, states, anatomy, primitives, semantic aliases) are
native vocabulary and need no definition. Terms from engineering domains (endpoint, cron,
webhook, migration, cache, regression) are foreign until defined.

Prefer replacing jargon over defining it: "the system checks every five minutes" beats
"a cron job polls the endpoint" even with definitions attached.

---

## The three-altitude explanation model

Every substantive explanation offers three levels, in this order:

1. **Plain english** (default, always present). What it does and why it matters, in the
   reader's vocabulary. Barney-the-dinosaur simple is acceptable; condescending is not.
2. **How it works** (one step down). A picture, analogy, or annotated diagram — the mental
   model, not the implementation.
3. **Full detail** (on request or one click away). The actual technical trace, for the moment
   an engineer joins the conversation.

**The caveats-at-the-top rule — what keeps ELI5 honest:** anything that would change the
reader's *decision* — a limitation, a risk, an assumption Claude made, a thing that isn't
covered — must appear at the plain-english level. Detail may be progressive; caveats may not.
Simplifying the language never licenses omitting the load-bearing facts.

---

## Voice lookup by profile

| Profile | Voice for artifacts and explanations | Voice inside the repo surface |
|---|---|---|
| `personal-solo` | Designer-first | Sean's call — he's the only reader |
| `centric-engineering` | Designer-first to Sean | Engineer-voiced (PRs, commits, code comments) |
| `centric-design` | Designer-first, zero translation, two-hop ready | n/a |

## Anti-patterns

- Engineering vocabulary as the default register ("the ingestion pipeline dedupes on a
  composite key") when the reader is a designer.
- Accuracy used to excuse illegibility — technically correct but unforwardable.
- ELI5 that glosses: simplification achieved by silently dropping the caveats.
- Explaining in terms of Claude's implementation ("I refactored the handler") instead of the
  reader's outcome ("dismissing an article can no longer delete it").
