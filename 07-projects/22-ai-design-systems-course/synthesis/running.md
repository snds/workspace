---
title: Running synthesis
project: 22-ai-design-systems-course
as-of: 2026-09-10
status: graduated
---

# Running synthesis — AI and Design Systems

Original notes, not a transcript. Update after each section. Graduate to `08-knowledge/` only when a claim survives later chapters.

## For future agent

Intro + **Ch1–Ch6** + recap + **jams** + **appendix** + extras are on disk. Extra-track videos that duplicate Ch3/Ch4 are `status: pointer`. **Surviving claims graduated 2026-09-11** to [[18-design-systems-ai-operating-model]], [[ai-design-systems]], and [[ai-and-design-systems]]. Do not download videos.

## Thesis so far

A design system is **critical UI infrastructure** — the *story* of how the org designs and builds interfaces — made of standards + the three-legged stool (design lib, code lib, docs) + people/process. History’s punchline: dotted-line copy-paste became **solid-line dependencies**. That graph is hard-earned and fragile. **AI is mortar**, not a replacement: it fills cracks between existing bricks.

Pair of problem statements:

- **DS hard:** living standards vs product reality; asset sync; docs nobody reads; politics/ROI; makers vs consumers; governance, versioning, contribution.
- **AI hard:** non-determinism, confident hallucinations, sycophancy; unknown quality; human pace/wellbeing; org adoption; “no good UX on a dead planet.”

The combination: DS still does quality-at-scale; AI supplies speed and connective power; the system **reins in the chaos**. “Is it good?” is the defining question once generation is cheap.

Three use-case buckets: (1) check-engine / AI-ready foundations → Ch 3, (2) better products with the system → Ch 4, (3) invent next UX → Ch 5. Process/ops → Ch 6.

## Chapter 2

Operational chapter. Install stack (Claude Desktop Chat/Cowork/Code, Cursor editor+agent, Claude Code; Warp/Codex/Antigravity/Windsurf as also-rans). Keys: one per app; Figma PAT has scopes. Figma MCP in Cursor is OAuth; Claude Desktop install + connectors lesson had **no captions** (partially filled by Ch3 Figma MCP installs).

**Load-bearing:** Git is the sandbox because AI can nuke a codebase. New handoff: non-devs prototype *and* carry work over the line via PR/review. Payoff demo: Claude Code + `gh` files **cross-linked issues** on the product repo *and* Eddie (with Eddie Brain MCP), so DS intake carries product context. Grown-up vs vibe-coding in a chat window.

## Chapter 3

Don’t generate a DS from scratch (same failure as adopting Material wholesale). Assume you have one. **Check engine:** cosmetic vs structural vs “AI will generate garbage.” Five qualities: complete, sound, synchronized, extensible, AI-ready. Ten stations. Kit (plus Design System Ops / modern web guidance) on Eddie: calibrate **why + team size + live gen test**. First score **70**; after station work **83**. Coverage didn’t rise because wiring a design-systems MCP *found more holes*. Feedback & adoption stayed yellow.

**Context-based DS (Station 6):** design ideation → design QA (FigmaLint) → design-to-dev protocol (MCP; designers own first code draft on a design branch) → context engineer PR → tests → publish → playground that consumes the **validated package** (Story UI / Make / v0 / Claude Design) → product integration. Culture over auto-sync tools. Eddie Brain / `CLAUDE.md` must not drift from HEAD.

FigmaLint = deterministic + LLM-as-judge. Console MCP sits in the design↔code seam (read/write, multi-file, tokens). Language is the **contract** AI reasons with (`inverted`→`knockout` with deprecation). Dead props erode trust. A11y: feed the spec; components ≠ products. Machine-readable docs ≠ “docs exist.” Agent access = remote MCP in the tools people already use (Company Docs / Eddie Brain on Netlify).

Demo labs: Eddie (prod), Soul Patrol, Altitude, Eventz, College Town, CBDS.

## Chapter 4

Product flavors: ongoing / greenfield / legacy adoption / retheme. Discovery is where DS ROI used to be tap-dance; AI wrangles scattered context. bradfrost.com lab: SPEC gate + `bfw-process` + **product inspection** skill. Baseline **42/100** — good bones, three load-bearing (not mobile, no tests/CI, archive unretrievable); Eddie recipes not installed.

**On-rails vs off-rails:** bake-off (Make/Bolt/v0/Claude Design/Lovable) is education + a handoff *into* an on-rails rebuild. Most important lesson: without guardrails the footer ignores Eddie. Steel curtain = deterministic CI + evals (“does this PR solve the ticket?”) before users see vibe-coded slop.

**Adoption is a DS workout:** FOUC was the real “not mobile” bug (DSD / progressive enhancement). Outside-in page shell (4% coverage). Global **adoption-plan** skill (garage + baseline). He overrides the plan: article template before listings (publisher instinct), then timeline motif. Four/five Eddie releases during the product pass. Retheme = **Theme Orchestrator** + `create-theme` script across Figma/Storybook/RN; Axe stays the a11y steel curtain, not LLM-as-judge.

**Homework:** name each workstream’s flavor; inspect a priority *and* a neglected legacy; run an adoption plan; codify a prototyping strategy (riff vs ship bright line).

No captions: Ch4 site intro 04–06; login-page Figma MCP (~15m); `bfw-process` rails (~17m).

## Chapter 5

Widen “user” to agents. Themes: redesigned / fluid / hyperpersonalized / frontier.

**Agents as users:** illegible to machines = invisible to people using agents. Dual publish: HTML canon + markdown twin (Kaelig). DS packages meaning beyond the org wall.

**Generative UI:** assemble blessed catalog on the fly (not rigid screens). Mapping to existing components is the speed trick vs emitting new code. A2UI lesson had **no captions**; the resources-site demo is the stand-in: agent speaks **JSON not code**, Eddie Brain do’s/don’ts as the only shapes, recipes (video grid), on-device deterministic map + optional Claude, **confidence under 50% it says so**, views are ephemeral.

**Hyperpersonalization:** tokens as handshake between user prefs and system; a11y is the moral center. Burndown plugin: CSS/JS in localStorage; rebuild Nike/legacy with Eddie MCP; Target protanopia restyle; Amazon “Death to Bullshit.” Recap: MySpace expression vs Facebook singular UX; risks = bubbles/bias/exploitation; more context requires **proportionally more safety** and user agency.

**Frontier:** speech → text is the unlock (keyword latches, not always gen UI). Realtime UI = talk a meeting into an on-rails snapshot (dumplings / pierogi / Busch Gardens). Creative infinite (BF Visuals canvas + tokens + live transcript): when anyone can create, **what we make and whether it’s good** is the job. Recap: protect roadmap and mental health; combine new with old; venture cautiously. Homework: agents in kickoff; small-slice play; Slack/jams. Next is ops (Ch6).

## Tool stack they compose

LLM → agents → subagents → **MCP** (official Figma vs Console MCP vs Company Docs vs Eddie Brain) → **skills** (inspection kit, evals, Playwright loop). Resource hub: https://resources.aianddesign.systems

## Fit to this workspace

- Mortar = don’t generate a parallel universe.
- MCP-as-live-SoR vs smoothed testimony — still live; Console MCP write path is messy (clones outside component sets, missed icon rebinds).
- Skills = our `SKILL.md` graph.
- Context-based DS = designer-owned first draft against the **published** library, named reviewer/context-engineer, playgrounds that import the package.
- Cross-repo issues with product context = Centric DS intake.
- Record architecture explicitly so inspectors stop scoring the wrong missing leg (Eddie documented Figma as unmaintained; Centric Figma *is* a maintained leg).
- Dead props / language contract / learning.json flywheel.
- Steel curtain before opening designer-owned drafts.
- On-rails vs off-rails (look-done CEO trap).
- Dual publishing for agent users (HTML + markdown).
- Gen UI = JSON + recipes + confidence, not LLM emitting React.
- Sanctioned play on a small slice; protect the meat-and-potatoes roadmap.

Still ahead: optional caption-gap revisits (Ch6 selling, course recap, early jams, Ch5 A2UI). Durable claims live in workspace doctrine, not only this file.

## Chapter 6

Org arc: **sell → pilot → rollout → govern**. Sell/pilot is blurry — the pilot *is* the pitch. Tether to real product (checkout), shrink scope, inspection baseline, stack quick wins. Document pass/fail into markdown that becomes rails. Rollout is where orgs fumble (comms/governance); steel curtain makes DS default not goodwill; inform don’t pitch; AI as mortar *between people*. Govern from day one of the still-living pilot: dual-filed issues, cron inspection, GitHub hooks, token budgets, new tools must **earn a place**. Care for humans; curated signal not every-model pings. Selling lesson (~44m) had **no captions**; summary cites Lou/Waypoint as sandbox→sell.

**Homework:** name the phase; who must be sold and what success looks like *for them*; pick planned-not-started pilots; copy existing rebrand/replatform rollout; install the feedback loop early.

## Open questions

- Whether MCP reduces hallucination or relocates trust.
- Empty-caption lessons: Ch2 Figma MCP connectors; Ch3 intro; Ch4 SPEC review (~17 min) and login Figma MCP demo; Ch5 A2UI (~20m) and gen-UI recap.
- Product inspection kit vs DS inspection kit — same repo, second skill.
- Whether 27’s rails gates get named in later recaps.
