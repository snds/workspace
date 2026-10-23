---
title: Routing architecture across every domain — the routing suite's findings and the fixes applied
status: applied; three decisions open
date: 2026-10-23
tags: [skills, routing, architecture, harness, synapse]
related_projects: [19-workspace-brain, 26-synapse]
---

# Routing architecture across every domain

**Answer.** The design-skill rearchitecture's rules now hold in every domain. Every hub with spokes
declares its `area`, and every spoke has triggers of its own. Before, **129 spokes** in design,
engineering, data, product, quality, accessibility and game could be reached only if an agent read
their hub's prose and picked them. Now none can't be reached. Two everyday words that fired skills
(`battery`, `pasta`) and a cluster of one-word cinematography triggers (`shot`, `framing`,
`blocking`) are fixed. The other architecture problems the design audit found mostly don't
repeat outside design: no prefix spans two domains now, and no clear duplicate spoke exists
outside the design-system and Figma pair. Three choices are Sean's (section 4).

Asked by Sean, 2026-10-23: "The above work also identified good architecture changes which would
be good to apply against all domains." Measured with the routing suite Synapse gained the same day
(`sy routing test`, [plan 11](https://github.com/snds/synapse/blob/claude/synapse-generator-harnesses-w6fan1/docs/plan/11-routing-suite.md)).

---

## 1. What was measured

The routing suite routes these against the live vault:
- every trigger, both bare and inside three neutral carrier sentences (10,328 requests);
- every phrase a description quotes (476);
- 82 everyday and work-chatter sentences that should load nothing;
- the 143 routing cases.

It also checks every load chain and the architecture rules from
[design-skill-architecture](design-skill-architecture_v1.0_2026-10-22.md) §4.

## 2. Before and after

| | Before | After |
|---|---|---|
| Triggers | 1,806 | 2,586 |
| Spokes reachable only through hub prose | **129** | **0** |
| Hubs with spokes that declare an `area` | 15 of 31 | 31 of 31 |
| Description phrases that reach their skill | 155 of 476 (33%) | 234 of 476 (49%) |
| Everyday sentences that load a skill | 2 of 60 | 0 of 82 |
| Own triggers that reach their skill | 100% | 100% |
| Routing cases | 143 of 143 | 143 of 143 |
| Tokens per answer p50 / p95 / max | 4,552 / 13,181 / 22,741 | 7,223 / 13,387 / 28,687 |
| `workspace-harness` skill reachability | 130 hub-prose only | 1 |
| Cross-chain trigger collisions (harness ceiling 25) | 23 | 23 |

The p50 rose because requests now reach the spoke that owns them, and a spoke loads its hub and
foundation too. That is the right reading costing more than a hub alone; p95 barely moved. The
widest answer is "generate a design system in Figma", which loads the design-system and Figma chains
(28,687 tokens, under the suite's 32,000 warning).

## 3. What changed

**Areas (16 hubs).**

| Hub | Area |
|---|---|
| `figma` | `figma-authoring` |
| `job-search-strategist` | `career` |
| `lead-backend-engineer` | `backend` |
| `lead-data-scientist` | `data-science` |
| `lead-devops-engineer` | `devops` |
| `lead-frontend-engineer` | `frontend` |
| `lead-game-designer` | `game-design` |
| `lead-game-developer` | `game-development` |
| `lead-mobile-engineer` | `mobile` |
| `lead-product-manager` | `product-management` |
| `lead-security-architect` | `security` |
| `lead-visual-qa` | `visual-qa` |
| `legion-project` | `legion` |
| `material-symbols-project` | `material-symbols` |
| `realtime-visual-craft` | `realtime-visuals` |
| `variable-icon-font-architect` | `icon-fonts` |

[skill-areas](../../../02-shared-references/skill-areas.md) now lists all 31.

**Spoke triggers (129 spokes, about 780 triggers).**

*Where they came from.* Each spoke's triggers come from its own description: the "Use this skill whenever the conversation touches: …" lists and the asks it quotes. That keeps them in the author's words.

*What was filtered out:*
- one-word and everyday terms (for example `react`, `hooks`, `carbon`, `lightning`, `material`, `dependency management`);
- phrases taken from "not this" clauses;
- phrases two spokes both claimed, unless one clearly owns them;
- anything another skill already triggers on.

*Written by hand.* 37 spokes got some or all of their triggers written by hand, mostly where the description lists no asks: the Figma mechanics spokes, the information-design spokes, the backend spokes, i18n and others.

*By domain:* design 58, engineering 39, data 10, product 7, quality 7, accessibility 5, game 3.

**Everyday words:**
- `mobile-platform-craft`: `battery` and `permissions` became `battery drain`, `battery life`, `runtime permissions` and `app permissions`.
- `sec-threat-modeling`: `stride`, `pasta` and `dread` became `stride model`, `stride analysis`, `pasta methodology`, `pasta threat model` and `dread scoring`. The two copies on `be-security-posture` were dropped, because threat modeling's home is `sec-threat-modeling`.
- `img-cinematography`: `shot`, `framing`, `composition`, `dolly`, `crane` and `blocking` became camera phrases (`camera shot`, `shot framing`, `scene blocking` …). `framing` had loaded cinematography for "A/B test framing".

**Synapse's noise corpus** gained the senses that caught these: "I dread Mondays", "She took the bad news in stride", "This is blocking me", "Give it a shot", and others. Every workspace's run now checks them.

## 4. Decisions for Sean

1. **Foundations first across chains (Synapse D133).** Each load chain is in order, but when a
   request matches skills in two chains, the merge can load one chain's foundation after the other
   chain's hub or spoke: 515 of 10,700 answers. Recommended: sort foundations first across the merged
   load. It changes those answers in the routing oracle, so it waits for your word.
2. **Thin hubs.** 20 hubs are over 1,500 words and load in full before any spoke. The largest:

   | Hub | Words |
   |---|---|
   | `lead-information-designer` | 2,514 |
   | `lead-graphic-designer` | 2,353 |
   | `lead-motion-designer` | 2,315 |
   | `lead-type-designer` | 2,294 |
   | `figma` | 2,240 |
   | `lead-visual-qa` | 2,200 |
   | `lead-data-scientist` | 2,191 |
   | `lead-ux-designer` | 2,165 |

   Recommended: move depth into spokes, as `ds-advisor` did (its general visual foundations went to a reference file it reads on demand). Each hub is its own reviewed change, nothing deleted.

   **Reviewed 2026-10-23 (Sean: "go ahead with the next step that reviews hubs for spoke depth").**
   Synapse's `sy routing hubs` compares each hub section with its spokes and foundations, by shared wording and shared subject. Its rules are in [plan 11 §7](https://github.com/snds/synapse/blob/main/docs/plan/11-routing-suite.md#7-hub-depth). Calibration: on the vault as it was before 2026-10-22, it finds `ds-advisor`'s 2,689-word visual-principles section as `design-foundations`' territory, the same call the design audit made by hand.

   The big hubs are big with hub material: spoke tables, principles, the execution protocol #13 asks for, and cross-hub references. Five hubs were flagged:

   - **`material-symbols-project`: one move.** Its 581-word Figma icon-positioning technique went word for word to `references/figma-icon-positioning.md`. The hub keeps the rule in four lines (1,159 → 671 words).
   - **`lead-visual-qa`: kept.** Its delta-analysis method is the one every visual-QA spoke shares.
   - **`lead-game-developer`: kept.** Its Legion principles fit the Legion context the hub is scoped to.
   - **`lead-motion-designer`: kept.** Its directive is area-wide.
   - **`realtime-visual-craft`: kept.** Its intro shares phrasing with a spoke by design.

   Two heavy contract sections are left for a later, separate change: `figma`'s execution protocol (1,122 words) and `lead-accessibility-architect`'s principles (810).
3. **Description recall (49%).** Half the asks that descriptions quote still miss. Many are whole
   sentences written as examples ("how should this look AND how do I code it"). Either make
   short quoted asks triggers too, or leave the metric as a guide. Recommended: leave it, and add
   triggers when a real ask misses. Every new trigger is a chance to fire on ordinary English.

**Not found outside design:**
- **Duplicate spokes.** The closest pairs are `ds-generation-pipeline` and `figma-ds-generation-pipeline`, a deliberate split between the design-system side and Figma mechanics, and `fe-design-tokens` with the Figma variable spokes, the code side of the same tokens.
- **Prefix collisions.** None now.

## Related
- [[decision-design-skill-architecture]] · [[decision-skill-prefixes]] · [[decision-routing-every-domain]] · [[skill-frontmatter]]
