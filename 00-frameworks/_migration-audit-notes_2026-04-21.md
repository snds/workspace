# Framework Audit Notes

_Audit session: 2026-04-21 — Sean + Claude_
_Methodology: preservation-biased token-optimization pass across five framework documents._

---

## Audit philosophy

Cut, not compress. Targets:
- Meta-commentary that restates what the doc already demonstrated.
- Parallel-structure repetition between intro/body/summary sections (e.g., the "what this framework changes" section re-stating points the body just made).
- Doubled phrasing within single claims ("clear and direct", "useful and valuable").
- Parenthetical restatements that add no information.
- "As noted above" / "as discussed" that can become direct references or disappear.

Preserved:
- Parallel structure that carries meaning (tier descriptions, category lists, state enums).
- Specific examples, named references, citations, canon authors.
- Nuance carriers — phrases doing real semantic work even if they sound "extra."
- Reference material in appendices (users expect completeness there).
- Summary sections when their redundancy is structurally purposeful (last-mile recap).

Per-doc entry format:
- **Before → After** line count and rough token delta.
- **Cuts made** — categorized, with the specific change.
- **Considered but preserved** — candidates rejected for preservation reasons, with reasoning. (So anything I flagged as potential-cut is visible even when I decided against.)

---

## 01 — aesthetic-lens.md

**Before:** 153 lines. **After:** 153 lines. **Delta:** 0.

**Verdict: passes audit with zero changes.** Already tight. No meta-commentary restating the body. Every principle statement does unique semantic work. The six lists (Foundational principles, Through-lines, Stances, Heroes, Anti-patterns, Decision-making, Integration across domains) are distinct enough that partial overlaps are deliberate structural choices, not redundancy.

**Considered but preserved:**
- **Through-lines vs. Decision-making overlap.** Six "look for" questions vs. six "ask in this order" questions with partial semantic overlap ("Inevitability over novelty" ↔ "Inevitable or surprising?"; "Earned density" ↔ "Earned or decorative?"; "Authored constraint" ↔ "Authored or generic?"; "Coherence under scale" ↔ "Scalable without loss?" + "Coherent under its own rigor?"). Structurally distinct use-cases (passive evaluation lens vs. active decision framework). **Flagged for future pass if Sean wants a merged variant** — not cut here.
- **Palette section's two frames.** Opening names Sean's personal default ("warmth as home base"), closing names the operating principle ("palette serves intent"). Both load-bearing, different work.
- **Italic sub-header domain list.** Seven domains explicitly listed. The list tells the reader non-UI domains are covered — load-bearing for the multi-domain framing.

---

## 02 — ui-ux-operational-framework.md

**Before:** 169 lines. **After:** 164 lines. **Delta:** −5 lines, ~80 tokens.

**Cuts made:**
- **"Integration with the Aesthetic Lens" intro bullets.** Removed `The two documents work together:` and the two bullets describing each framework's role. They restated what the italic sub-header at the top of the doc already says ("Where the lens answers 'why does this feel right?', this framework answers 'how do we systematically make decisions...'"). The four bullets under "Every design decision should pass through both:" do distinct work (naming what the integration produces) and stay.

**Considered but preserved:**
- **Italic sub-header second half.** "Neither is project-gated. Both stay holistic and contiguous." partially echoes "Both sit at the top tier — above project-specific skills." The "holistic and contiguous" phrase is load-bearing (it's the tell that these frameworks carry across conversations); cutting "Neither is project-gated" alone saves one clause but breaks the rhythm. Left intact.
- **"The data table as an illustration" section.** Concrete, specific, and load-bearing. The example is exactly the kind of thing that makes the framework legible.
- **"Three-layer design thinking" intro lines for each layer.** Could compress "This isn't about hiding information. It's about sequencing it so cognitive load matches actual need." but the contrast pattern ("isn't X — it's Y") is one Sean explicitly flagged as avoiding in user preferences. Left intact because the positive framing ("sequencing it so cognitive load matches actual need") is the substance.

---

## 03 — collaboration-and-critique-framework.md

**Before:** 215 lines. **After:** 215 lines. **Delta:** 0.

**Verdict: passes audit with zero changes.** Dense, purpose-specific sections. No structural redundancy.

**Considered but preserved:**
- **"Challenging assertions and defending the user" vs. "Pushback: when and how".** Surface overlap, but the first is me-at-Sean and the second covers Sean-at-me (bidirectional disagreement). The political/genuine constraint distinction is uniquely in the "Challenging assertions" section and is load-bearing.
- **"What this framework changes" summary section.** Echoes body by design. Sean explicitly structured these as recap sections; cutting them would break the pattern across all five frameworks.
- **"Common constraint citations" list.** Appears here and in the research framework — each context uses the same citations to set up different machinery (shared archive here, counter-evidence in research). Cross-doc redundancy is purposeful, not accidental.
- **"Communication tone" bullets including the explicitly-flagged "(Already in user preferences)" item.** Deliberate inclusion; Sean knows it duplicates and chose to. Not my call to override.

---

## 04 — research-and-evidence-framework.md

**Before:** 210 lines. **After:** 210 lines. **Delta:** 0.

**Verdict: passes audit with zero changes.** Parallel tier structure carries substantive meaning (each of the five tiers has distinct Threshold/Advocacy/Challenge/Usage-note). The "Usage note" field occasionally previews what "Evidence against managerial intransigence" later makes explicit — but previewing is appropriate since tier descriptions should stand on their own.

**Considered but preserved:**
- **"What counters them effectively" recaps the tier hierarchy.** Not redundant — it's applied summary re-contextualizing tiers specifically against intransigence.
- **"When research time is genuinely unavailable" section.** Could arguably fold into Tier 4 description, but it's doing distinct operating-principle work (the framework's explicit permission to operate at Tier 4 with honesty) separate from the tier definition.

---

## 05 — last-mile-craft-framework.md

**Before:** 611 lines. **After:** 608 lines. **Delta:** −3 lines, ~60 tokens.

**Cuts made:**
- **Visual QA toolkit closing paragraph.** Removed `This capability is large enough to deserve its own skill and dedicated build session — scoped separately from framework migration work.` The preceding header `**The visual QA toolkit (planned skill — to be built in a dedicated session):**` already communicates this. The "scoped separately from framework migration work" framing is stale the day after the migration.
- **Token economics hype sentence.** Removed `This is one of the highest-leverage pieces of infrastructure we can add to the collaboration.` The preceding two sentences do the math — the third is opinion that adds nothing specific.

**Considered but preserved:**
- **The 10 Categories of craft.** Some bullets duplicate concepts mentioned in Tier 2 Construction discipline. But Categories is the expanded reference treatment (with canon citations and deeper bullets), while Tier 2 is the when-to-check summary. Both doing distinct structural work. Cutting the duplicates inside Categories would break the "each category reads complete" pattern.
- **"Operating habits" vs. "What this framework changes" vs. "Relationship to existing skills" overlap.** Three summary-adjacent sections. Each does distinct work: Operating habits = how I operate procedurally; What changes = strategic shifts; Relationship = specific skill mappings. Same frame on different planes.
- **Operational state section's detail level.** Could trim prose but the content is the spec for today's `SESSION-STATE.md` implementation — detail is load-bearing for the build.
- **"Augmented perception as deliberate tool" appearing in both body and operating habits.** Body frames it as a limit; habits frames it as a behavior. Different-enough framings that both earn their place.
- **Four mentions of `team-practices-and-decisions.md` across the doc.** Each in different context (intro, closing of code-level craft, tooling subsection, appendix). Not redundant — each surfaces the relationship where relevant to the local reader-attention.
- **Appendix checklist (~125 lines).** Reference material. Users expect completeness.

---

## Audit summary

| Doc | Before | After | Δ lines | % reduction |
|---|---|---|---|---|
| 01 aesthetic-lens | 153 | 153 | 0 | 0% |
| 02 ui-ux-operational-framework | 169 | 164 | −5 | 3.0% |
| 03 collaboration-and-critique-framework | 215 | 215 | 0 | 0% |
| 04 research-and-evidence-framework | 210 | 210 | 0 | 0% |
| 05 last-mile-craft-framework | 611 | 608 | −3 | 0.5% |
| **Total** | **1358** | **1350** | **−8** | **0.6%** |

**Honest finding:** these documents were already well-edited when drafted. Preservation bias was validated — the actual cut surface was much smaller than a first-pass estimate suggested. The discipline of looking was still worth the pass, because it verified tightness rather than assumed it. Any more-aggressive cutting would start compromising load-bearing prose.

**What was not attempted in this pass:**
- Restructuring (merging Through-lines + Decision-making in Aesthetic Lens, flagged for future).
- Cross-doc deduplication (the four "Common constraint citations" mentions across collab and research, the five-framework italic metadata repetition).
- Tighter paragraph forms (would require heavier rewriting, risks voice drift).

These are separate passes Sean can request when/if the token surface becomes a real constraint.
