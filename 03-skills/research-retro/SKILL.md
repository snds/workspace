---
name: research-retro
description: >
  The last step of every piece of research: what the approach taught, not what the topic taught,
  turned into workspace improvements. Sorts each lesson to where it belongs: a domain spoke's
  method, the depth calibration notes, a research-check fixture, a Synapse harness proposal, a
  rule-of-three row, or a self-improve mint. Use for a research retro, research lessons learned,
  or improving the research harness, skills or workspace from research done.
aliases: [research-retro]
triggers: [research retro, research lessons, improve the research harness, what did this research teach]
tier: spoke
domain: research
hub: lead-research
prerequisites: [lead-research]
related: [self-improve, close-out]
spec_version: "2.0"
---

# Research Retro

Stage 10 of [[19-research-operating-model]]. The topic's content goes where the topic lives. This
spoke harvests the *approach*, so each piece of research makes the next one better.

## The five questions

Answer each in a line; "nothing" is a valid answer.

1. **Depth:** was the tier right? If not, what signal was missed? → [[research-scoping]]'s
   calibration notes.
2. **Search:** what source, term or path worked or failed in this field? → the domain spoke, as a
   proposed edit.
3. **Appraisal:** did a weak source get through, or a good one get dropped? → the spoke, or a
   `research-check.py` fixture.
4. **Gate:** did a done-gate miss a real problem, or fire on nothing? → a fixture in
   `09-tools/research-check.py --self-test`, or a harness proposal (below).
5. **Workspace:** did a skill, route, knowledge entry or check turn out missing or wrong? → a
   [[self-improve]] class.

## Where each lesson goes

| Lesson | Write to | How |
|---|---|---|
| A method fact about a field | The domain spoke | An edit with the evidence: this research |
| A wrong depth call | [[research-scoping]] → Calibration notes | One line: ask, tier chosen, tier needed, signal missed |
| A check that should exist | `09-tools/research-check.py` | A rule plus a planted fixture, via [[close-out]] |
| A harness criterion that's wrong or missing | Synapse's `research.finding` | A proposal with §4.1's evidence (task, what it required, friction, change, proof); a person approves (D116) |
| The same gap again | `06-context/rule-of-three.jsonl` | `python3 09-tools/rule_of_three.py add --pattern <slug> --evidence <path-or-sha>`; the third earns a fix |
| A route that didn't fire | Routing fixtures / triggers | [[self-improve]] "corollary access" |
| A durable finding about research itself | `08-knowledge/research/` | A knowledge entry, dated |

## Rules

- **Approach over topic.** "Rust is fast" is the topic. "Benchmarks in this space rarely publish
  hardware, so start from reproduction" is the approach.
- **Evidence, not vibes.** Each improvement names the research that showed it.
- **Smallest fix.** A line in a spoke beats a new spoke; a fixture beats a paragraph.
- **Reviewed.** Harness changes are proposals; frameworks and new hubs follow [[self-improve]]'s
  sign-off rules.

## The retro line in the report

Every finding's `## Retro` section carries at least one line: the lesson and where it was recorded,
or "nothing to improve". `research-check.py` checks it's there.

## Related
- hub → [[lead-research]]
- peer ↔ [[research-scoping]] · [[research-synthesis]] · [[self-improve]]
