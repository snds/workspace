---
name: research-scoping
description: >
  The first step of any research: turns an ask into a question that could be wrong, reads how
  deep it deserves, and proposes more or less depth with reasons before any search. Owns the
  depth tiers (D0 answer, D1 brief, D2 review, D3 systematic, D4 original), the ask-or-proceed
  rule, and the domain complexity profile that picks the method spoke. Use for scoping research,
  "how deep should this go", a rapid review, or when a quick ask carries a big decision.
aliases: [research-scoping]
triggers: [scope this research, research depth, how deep should this go, rapid review, research scope]
tier: spoke
domain: research
hub: lead-research
prerequisites: [lead-research]
spec_version: "2.0"
---

# Research Scoping

Stages 1–3 of [[19-research-operating-model]]: frame, scope the depth, profile the field. Five
minutes here saves hours of the wrong search.

## 1. Frame

Write four lines before anything else:

- **Question:** one sentence, answerable, with a possible wrong answer.
- **For:** who reads the answer.
- **Serves:** the decision, artifact or curiosity it feeds.
- **Done looks like:** what the person will hold at the end (a fact, a brief, a review, a new
  result).

If the question can't be wrong yet, split or sharpen it: *"Is Rust good for this?"* becomes *"Does
Rust's ecosystem have a maintained library for X, and what do teams report about build times at
our scale?"*

## 2. Read the depth

Depth follows **stakes**, **reversibility**, **novelty** and **contestedness**, not the length of
the ask.

| Signal | Points lighter | Points deeper |
|---|---|---|
| Stakes | Curiosity, a draft, a reversible call | Money, safety, a long-lived standard, other people relying on it |
| Reversibility | Easy to change later | Locked in for months or years |
| Novelty | Well-trodden, textbook | New, fast-moving, or new to this workspace |
| Contestedness | Settled consensus | Live disagreement, interests involved |
| Existing knowledge | `08-knowledge/` already covers it, fresh | Nothing in the vault, or stale |

Pick the tier (D0–D4, #19 §2), then **say it with its cost and its limit**:

> "This is D1: about six good sources, one pass, maybe 20 minutes. It'll give you the main
> positions, not completeness."

### Propose more or less depth

Propose when the ask and the signals disagree, and always give the trade:

- **Deeper:** *"You asked for a quick look, but this sets the token architecture for three
  products. D2 is the honest tier: a planned search and appraisal. D1 gets an orientation in a
  third of the time but can't tell you what it missed."*
- **Lighter:** *"A systematic review here would take days for a choice you can reverse next sprint.
  A D1 brief answers the decision. Want that instead?"*

**Ask or proceed.** Proceed when your proposal moves the tier by one or less and the person isn't
reachable; say which tier you used. Ask when it moves by two or more, or when D3/D4 would spend real
time or money.

### Check the vault first

Before searching outside: `python3 09-tools/vault-retrieve.py "<terms>"` and the knowledge index.
A fresh entry may answer at D0; a stale one is a starting point with a known date.

## 3. Profile the field

Name what makes this field hard (#19 §3) and load its spoke. Spanning fields → the strictest
profile of those touched. Two prompts help:

- *What's the most common way a careful person gets this wrong in this field?*
- *Where does the best evidence live, and who controls access to it?*
- *What does each tradition call this?* A term that several fields use ("intent", "model", "agent") returns one camp when searched alone; list each field's own word before searching.

| Field | Load |
|---|---|
| Sciences | [[research-scientific]] |
| Mathematics | [[research-mathematical]] |
| History, humanities | [[research-historical]] |
| Computing, software | [[research-computing]] |
| Social, qualitative | [[research-qualitative]] |
| Industry, markets, policy | [[research-industry]] |
| People using this product | [[ux-research-synthesis]] (not this network) |

## Calibration notes

Record wrong calls here via [[research-retro]], so the tiers sharpen with use. Each note: the ask,
the tier chosen, the tier it should have been, the signal missed.

- 2026-10-22 · "research intent in relation to agentic systems" · D2 · D2 was right · the polysemy of "intent" (seven traditions, seven meanings) was the signal; it also produced the synonym prompt in §3.

## Mistakes to avoid

- Matching depth to how long the ask was rather than to its stakes.
- Starting a D3 search for a D1 decision because the topic is interesting.
- Answering at D0 when the vault's entry on it is two years old.
- Proposing more depth without saying what it costs.

## Related
- hub → [[lead-research]]
- peer ↔ [[research-literature-review]] · [[research-retro]] · [[research-synthesis]]
