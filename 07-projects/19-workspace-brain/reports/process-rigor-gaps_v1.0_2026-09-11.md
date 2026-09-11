---
title: Process rigor gaps — whole workspace
version: 1.0
date: 2026-09-11
surface: Cursor + workspace-core
branch: main
sha: 40d9f8e
agent: Cursor Grok 4.6
status: applied 2026-09-11 — recs R1–R16 + load-miss 1–15
companion: harness-map_v2.0_2026-09-11.md
---

# Process rigor gaps v1.0 — 2026-09-11

Hub-gated adversarial review of **expertise and process that exists but does not run**, across every domain cluster — not only coded order-of-operations, Figma construction, and hub self-test.

Sean's three examples are **instances of the same failure**: doctrine without a load edge, measurement without an attach point, human confirmation as a sentence instead of a step.

## 1. Boundary

| Field | Value |
|---|---|
| Workspace | `~/Projects/workspace` · `main` @ `40d9f8e` |
| Surface | Workspace core + Cursor · Work MBP |
| Companion | Load-miss map v2.0 (recs **1–15** still open). This file is recs **R1–R16**. |
| Target user | Sean as designer-of-designers + any cold LLM he will cross-check |
| Bar | Agent self-polices; Sean's last act is visual/Proofboard confirmation — not CI red, unbound fills, or a merge surprise |
| Grade legend | `VERIFIED` · `INFERRED` · `INACCESSIBLE` · `NOT_EXPOSED` |

**Read-only.** No always-on edits. Do not paste a close-out essay into 47 hubs.

Registry snapshot (`VERIFIED`): 297 skills · 47 hubs · **34 hubs with empty `triggers`** · **8/297** `governed_by` · **0** `governs` · 131/185 spokes silent · foundations all have triggers.

## 2. Whole-workspace system map (rigor, not load)

What already **protects** (keep):

- #13 L1–L5 contract and the domain instantiation table
- #06 pre-output gate (detector + judge/leave-the-building + human read-with-care)
- #07 reviewability / stacking / author-owns-drift
- #10 native pixels · #11 technique premortem · #12 triple done-gate (best instantiated cluster)
- #14 five-stage engineering pipeline · #15 analysis frame · #16 threat-model pipeline · #17 intent-run · #18 steel curtain
- Proofboard ([[05-validation-harness]]) as Sean's no-read-code done definition
- `plan-ahead` for cds/proto Pages vs overlay
- Workspace validators (integrity / links / workspace / capabilities)
- `mission-fit` for false `done`

What is **drag**: the same close-out said six ways (#06, mission-fit, Proofboard, #14 verify, #11, plan-ahead) with **no one invocation**. Agents pick the essay they already have open.

## 3. Cluster findings

### Command wrappers (the intended self-police surfaces)

`/qa` `/ds` `/figma` `/motion` `/type` `/redesign` — verb grammar, “never duplicate a spoke,” then **no `triggers:` on the committed files** (figma confirmed: HEAD frontmatter ends at `prerequisites`; vendor `figma-use` is still the documented first load). `/eng` is the exception (has triggers + `defers_to` + `rigor_role`). Grade: `VERIFIED`.

Local uncommitted WIP on `figma/SKILL.md` adds triggers and reverses plugin precedence. GitHub-only agents still see the weaker hub. Grade: `VERIFIED` (HEAD vs worktree).

### Producer hubs that never get judged

`design-engineer`, `figma-*`, `lead-ui-designer`, `lead-frontend-engineer` have **empty `governed_by`**. After they produce, nothing in the graph loads `/qa`, visual-qa, or a11y. `ai-design-systems` is almost the only design spoke that declares `governed_by: [qa]` — and `/qa` itself is silent, so the edge is navigational only. Grade: `VERIFIED`.

### Coded work — order of operations (Sean's example, generalized)

Exists: `plan-ahead` (cds/proto), #14 `/eng`, #07, git safety in Cursor User Rules, `cds-exports-check` in proto.

Missing:

- `plan-ahead` triggers are dual-repo/Pages phrases. `"implement this"`, `"fix CI"`, `"open a PR"`, `"merge"` do not fire it. Grade: `VERIFIED`.
- No merge-conflict premortem (lockfiles, generated registry, files two branches touch).
- No per-repo **CI-contract card** (what GHA/Pages vendors vs what the laptop overlays) except the one cds/proto knowledge note.
- Proofboard is not a step of `/eng ship`.
- `lead-frontend-engineer` / `lead-backend-engineer` / `lead-devops-engineer` silent — #14 depth never Layer-0 loads.
- This session's own rebase: claiming #17 / project 21 without fetch. Rec 14 of the load-miss map.

### Figma construction (Sean's example, generalized)

Exists: 14 construction rules + build-from-real-components + props-first (`figma-ds-surface-authoring`); design-engineer hard gate in **uncommitted** WIP; component-generation spoke hard-gate prose.

Missing on **committed** path:

- Hub does not load `design-engineer` first; it tells the agent to load `figma-use` first. Grade: `VERIFIED` (HEAD).
- No machine check that fills are bound to semantic/mode tokens vs `Color/*`.
- No check that controls are library instances vs rectangles.
- Execution protocol has no native-zoom screenshot and no **stop for Sean**.
- `component` curated route still equals generate (load-miss rec 4) — construction rigor loses to volume.

### Visual QA + human in the mix (Sean's example, generalized)

#06 already says the agent is never the sole witness. `lead-visual-qa` even says it should run as the natural final step when other skills produce visuals — and it has **no `triggers:` key**. `visual-qa-toolkit` triggers are `visual qa`, `screenshot audit`, … not “I just generated a component.” Human confirmation is therefore optional manners, not a gate. Grade: `VERIFIED`.

### Analysis / PM / evidence

#15 is strong L1. Both `lead-data-scientist` and `lead-product-manager` are silent. “What does the data say?” never loads the decision-frame. Charts inherit #11 only if someone already opened it. Grade: `VERIFIED`.

### Accessibility and security as sideways lenses

Intended to cut across all visual/eng work. Attach is opt-in: a11y hub silent; security hub *does* trigger on `security` (hair-trigger token tax) but only three spokes list `governed_by` sec-*. Figma generate does not load a11y. Grade: `VERIFIED`.

### Motion / type / graphic / infod / icon

#13 maps L3 to `/qa` lenses. Those lenses never attach. `/motion` and `/type` silent. Icon-font hub has triggers but only `variable axis`. Grade: `VERIFIED`.

### Photoreal / game (the positive control)

#12 + `realtime-visual-craft` + render-qa + #11 is the cluster that *almost* matches the bar. Do not cargo-cult GPU scripts into career or science. **Replicate the attach pattern**: named done-gate + measurement + refuse. Grade: `VERIFIED`.

### Intent / multi-agent

#17 + `intent-run.py` is real enforcement for swarms. Ordinary single-agent coded/Figma work never hits it. Do not make Intent always-on (token tax). Point plan-ahead / close-out at the small-work case; keep Intent for N-agent. Grade: `VERIFIED`.

### Workspace contribution / session / context

#08 write gates + validators run when *this* repo is edited. They do not run as close-out of centric-ui / proto / Figma files. Context profile is Layer-0 only on the exact phrase `context profile`. Session protocol updates Live handoff; it does not require a close-out receipt (detector named, human stop pending). Grade: `VERIFIED`.

### Career / Adobe / Vision / Science

Thin L1 is allowed by #13 if honest. Measurement = checklists/CLIs. Mark **INCOMPLETE**, don't invent fake L3. Grade: `VERIFIED`.

### GitHub-blind and surface-blind (from load-miss, still in force)

Most `07-projects/` SESSION-STATE never syncs. Perplexity adapter forks. `prompt_route.py` gitignored. This chat's root is `~/Projects` so Cursor `brain.mdc` does not attach. Grade: `VERIFIED`.

### Context and intent awareness (whole workspace, not a domain)

This is the other half of "the agent did the work and still missed the point."

| Intent question | Where it lives | What actually happens |
|---|---|---|
| Who owns this / who reviews? | `00-context-profiles.md`. AGENTS says resolve before any repo action. | Layer 0 only on the exact phrase `context profile`. Ordinary "implement / commit / Figma write" never loads it. Grade: `VERIFIED`. |
| Who is the target user of *this* output? | #06 originating lens | Curated `audit`/`review` loads the framework file, not `/qa`. Non-review prompts skip the lens entirely. Grade: `VERIFIED`. |
| Is this CREATE or JUDGE? | Wrapper split: `/figma` `/ds` `/redesign` `/eng` vs `/qa` | CREATE hubs have no `governed_by`. `/redesign` (impeccable) can ship a variant without `/qa`. Grade: `VERIFIED`. |
| What does `done` mean for this user? | Proofboard · mission-fit · #06 detector check · #14 verify | Six languages, no single invoke. `visual-qa-toolkit` will not hunt screenshots — if the hub didn't capture, self-test is a no-op. Grade: `VERIFIED`. |
| Who is the decision owner of a claim? | #15 | `lead-data-scientist` / `lead-product-manager` silent. Narrative can ship without a named owner. Grade: `VERIFIED`. |
| Does this work cross a trust boundary? | #16 | Security hub hair-triggers on the word; FE/DS generate does not attach a threat-model. Grade: `VERIFIED`. |

Sean's three seeds (coded OOO, Figma construction, hub self-test + human VQA) are the CREATE/JUDGE/`done` rows under specific crafts. The table is the same miss everywhere else.

## 4. Numbered recs (R-series)

Approve by number. Complementary to load-miss **1–15** (especially 3 silent hubs, 4 `component` route, 6 #18 in AGENTS, 9 figma `defers_to`, 13 prompt-route hook).

| # | Disposition | Owner | Change | If skipped |
|---|---|---|---|---|
| **R1** | **One home** | new `03-skills/close-out/SKILL.md` (thin) | The four steps: self-test · self-validate (named detector or honest skip) · self-confirm (#06 honesty) · **human visual or Proofboard stop**. Every command hub's execution protocol *invokes* it. Do not copy the body into 47 files. | Agents keep freestyling “looks good.” |
| **R2** | **Turn into check** | `validate-integrity` or `build-registry` | Fail CI when a hub or foundation has empty `triggers`. Quote multi-word YAML trigger phrases. | Wrappers stay description-only; parser zeros bad flow lists. |
| **R3** | **Turn into check** | `/qa` `/ds` `/figma` `/motion` `/type` `/redesign` | Add real triggers; `/figma` `defers_to: [design-engineer]` and **stop telling agents to load `figma-use` first** (land the local WIP doctrine, not the HEAD fork). | Vendor mechanics win; judge hubs stay dark. |
| **R4** | **Turn into check** | producer hubs | `governed_by: [qa]` (visual) or `[eng]`/`mission-fit` (code-heavy). Populate `governs` on `qa` / `lead-visual-qa` / `a11y-visual`. Registry must treat `governed_by` as a **post-output load**, not a Related suggestion. | Graph remains a wiki. |
| **R5** | **Load later** | `plan-ahead` | Generalize beyond cds/proto: fetch before write; CI-contract vs overlay; merge-conflict hot files; generated artifacts; first later-breaker. Triggers: `implement`, `open a PR`, `merge`, `fix CI`, plus existing dual-repo keys. Pair with #07 — do not fork a second stacking essay. | Local green, Pages/GHA red; rebase collisions. |
| **R6** | **One home** | `/eng` ship + Proofboard | `/eng ship` (and any code-heavy `/qa spec` / analysis readout) must name or build the Proofboard. Playbook stays canonical; the hub *invokes* it. | Sean still has to read code to believe `done`. |
| **R7** | **Turn into check** | Figma prove-gate | After generate: inspect bound fills/strokes (refuse `Color/*` on components); every control is a library or `local/…` instance; variant matrix complete; native-zoom screenshot; **stop for Sean**. Binary pieces → MCP/script; judgment stays #06. | Construction rules remain advice. |
| **R8** | **Load later** | `trigger-routes.json` | `PR` / `pull request` / `rebase` / `stack these diffs` → #07. Do not also dump the 717-line #09. | Reviewability framework never loads at PR time. |
| **R9** | **Keep** (tiny) | `lead-ux-designer` | Triggers today: `challenge this`, `tear this apart`. Add the UX work the description already claims (`information architecture`, `enterprise ux`, `how should this work`) — or the hub is a roast button. | UX depth never Layer-0 loads. |
| **R10** | **Load later** | analysis / PM | Triggers on `lead-data-scientist` / `lead-product-manager` for `what does the data say`, `experiment`, `decision owner`. Close-out = #15 frame + Proofboard for the claim. | Narrative theater ships. |
| **R11** | **Turn into check** | a11y sideways | Figma generate + UI code close-out always loads `a11y-visual` (contrast/CVD) before human stop. Not a full axe dump on every chat. | Inaccessible UI reaches Sean first. |
| **R12** | **Probation** | security sideways | Don't hair-trigger the whole `lead-security-architect` on the word `security`. `governed_by` on boundary-crossing eng spokes; threat-model file as the check. | Either miss or token bomb. |
| **R13** | **Load later** | context profile | Repo actions (commit, PR, Figma write to a product file) resolve `00-context-profiles.md` without requiring the user to say “context profile.” One sentence in close-out / plan-ahead, not AGENTS bloat. | Employer-repo self-merge risk. |
| **R14** | **Keep** | photoreal cluster | Do **not** clone GPU toolkits into other domains. Use it as the **attach template** for R1. | Fake L3 / token waste. |
| **R15** | **Probation** | Intent #17 | Keep off ordinary single-agent work. If close-out (R1) + plan-ahead (R5) exist, Intent stays N-agent. Revisit if single-agent still ships false `done`. | Always-on living-spec tax. |
| **R16** | **One home** | close-out languages | After R1 exists: #06 gate, mission-fit, Proofboard, #14 verify, #11, plan-ahead become **invoke targets**, not parallel checklists. Point, don't restatement-grow. | Six “done” definitions, none fire. |

Invalid: “add visual-qa-toolkit as a spoke of every hub.” Measurement intent yes; cargo-cult SSIM on a threat model no (#13).

## 5. Gaps

| Item | Grade |
|---|---|
| Whether Cursor truncates skill descriptions (so wrapper `description` triggers never reach the model) | `NOT_EXPOSED` |
| Runtime proof that `governed_by` is ignored by `prompt_route.py` | `VERIFIED` (code never loads related/governed_by; earlier load-miss map) |
| Human VQA of a live Figma file this session | `NOT_APPLICABLE` (map-only) |
| Employer-repo CI contracts besides cds/proto | `INACCESSIBLE` without opening those repos |

## 6. Verification after any approved R-rec

1. Registry rebuild + validators
2. `evaluate-skill-routing.py` fixtures: `"implement the button"`, `"build this in figma"`, `"qa this screenshot"`, `"what does the data say"`, `"open a PR"`
3. One Figma generate + prove-gate dry run; one proto consume with plan-ahead printed first
4. Confirm `/qa` actually loads after `design-engineer` output once R4 is wired
5. Other-model cross-check against this file + [[process-rigor-gaps]]
