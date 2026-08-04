# Domain Rigor Stack

*The meta-operating model for every skill hub in this workspace. UI/UX already embodies this stack. Realtime photoreal (#12) is instantiating it for game/3D. This document makes the pattern mandatory for every other domain — and for any new skill, hub, spoke, command surface, or improvement.*

---

## The core conviction

**Knowledge without enforcement is advice. A domain is operationally ready only when agents can decide, measure, route, and refuse shallow overrides — not merely recite principles.**

Deep spokes alone are not enough. A hub with excellent reference text and no pipeline, no done-gate, no measurement surface, and no doctrine precedence will feel "anemic" in production even when the knowledge is strong. That is the failure mode this framework prevents.

---

## When this framework invokes

Load whenever you:

- Create or materially expand a foundation, hub, spoke, command hub, or measurement toolkit
- Add a plugin wrapper or mirror an external skill pack into `03-skills/`
- Audit whether a domain cluster is "complete"
- Author a new domain operating framework (#02, #12, #14+)

It sits beside [#08 Workspace Contribution](08-workspace-contribution-framework.md): #08 answers *where* content belongs; **this framework answers whether a domain's connective tissue is sufficient**.

---

## The five layers (intent, not a rigid template)

Every mature domain cluster must realize **all five intents**. Instantiation varies by domain; omission of an intent is a defect.

| Layer | Intent | UI/UX exemplar | Photoreal exemplar (#12) | Engineering-shaped exemplar |
|---|---|---|---|---|
| **L1 · Domain operating model** | Ordered decision pipeline + explicit done-gates | `#02` UI/UX ops | `#12` Realtime photoreal ops | `#14` Engineering ops |
| **L2 · Command / contract hub** | Verb grammar, project contracts, absolute bans, evaluate→refine loop | `/qa`, Impeccable, `DESIGN.md` | `realtime-visual-craft`, `RENDER.md`/`BUDGET.md`/`NORTHSTAR.md` | `/eng` or lead done-gates + ADR/runbook contracts |
| **L3 · Measurement toolkit** | Instrumented checks (scripts/harnesses), not judgment prose alone | `visual-qa-toolkit` | `render-qa-toolkit` | `a11y-audit-toolkit`, perf budgets, CI scanners |
| **L4 · Hub → spoke load chain** | Foundation → lead hub → specialty spokes with `prerequisites` / `hub` / reciprocal `## Related` | `design-foundations` → `lead-ui-designer` → `uid-*` | `imaging-foundations` → `lead-3d-designer` → production spokes | `eng-foundations` → `lead-*-engineer` → `be-*`/`fe-*`/`devops-*` |
| **L5 · Multi-voice / doctrine routing** | Orthogonal lenses + precedence so shallow plugins cannot override workspace doctrine | `lead-visual-qa` + `/qa --lens` + Impeccable preserve clause | `rendering-guild` + plugin conflict guard | `arch-guild` wrapper + security/a11y cross-cuts + **Doctrine precedence** in `AGENTS.md` |

### What "varies by domain" means

- **Design / visual domains** lean on visual QA, native pixels (#10), and craft bans.
- **Engineering domains** lean on contracts, CI gates, SLOs, threat models, and incident done-gates.
- **Analysis / data domains** lean on question→method→validity→decision pipelines and reproducibility checks.
- **Security** treats fail-closed done-gates as non-negotiable; measurement includes scanners and threat-model artifacts.
- **Process / career / tooling** domains still need L1–L5, but "measurement" may be checklists + validators rather than GPU/perf scripts.

Do **not** cargo-cult a `visual-qa-*` spoke into a domain that has no visual surface. Do **replicate the intent**: something that turns "done" from opinion into evidence.

---

## Absolute rules (all domains)

1. **No orphan hubs.** Every `tier: hub` declares `prerequisites` (usually a `*-foundations`) and a typed `## Related` block. Every spoke declares `hub:` and reciprocal Related edges.
2. **No doctrine without precedence.** Workspace frameworks > workspace skills > installed plugin skills. Plugin depth is welcome only behind a workspace **wrapper** that owns triggers and bans (see `/motion`, `/qa`, Figma Defers-to).
3. **Audit ≠ critique.** If a domain claims "audit," it must have an L3 measurement path. Judgment without measurement is `critique`.
4. **Done-gates are named.** A domain operating model (L1) lists what must be true before "ready for review." Cross-cutting: always honor #06, #10, #11 where visual/failure surfaces exist.
5. **No unreachable packs.** A directory under `03-skills/` without a root `SKILL.md` is incomplete — wire it or archive it (`_archive/` + `ARCHIVE-LOG.md`).
6. **Token frugality still wins.** Foundations stay short. Do not restate foundation principles in spokes. Prefer extending L1–L3 over adding redundant spokes.

---

## Acceptance checklist — new or improved domain cluster

Before calling a hub/spoke/addendum done, the authoring agent must answer **yes** (or explicitly N/A with reason) to:

### Placement (#08)
- [ ] Correct layer (`01-frameworks` vs `03-skills` vs `08-knowledge` vs plugin adapter)
- [ ] Frontmatter v2+ complete (`tier`, `domain`, `triggers` for hubs/foundations, `hub` for spokes)
- [ ] Reciprocal `## Related`; registry rebuild planned

### L1 Operating model
- [ ] Named pipeline (ordered stages) exists for this domain — new framework **or** explicit extension of #02/#12/#14/#15/#16
- [ ] Done-gates listed (what "finished" means)
- [ ] Failure / refuse cases named (when to stop or degrade)

### L2 Command / contract
- [ ] Entry surface exists: slash/command hub **or** lead-hub "Execution protocol" with verb-like stages
- [ ] Project contract artifact named when work is project-scoped (`DESIGN.md`, `RENDER.md`, ADR, threat model, PRD, etc.)
- [ ] Absolute bans listed (what never counts as evidence or done)

### L3 Measurement
- [ ] At least one instrumented or checklist-with-artifacts path for `audit`
- [ ] Registered in [[capability-registry]] if it needs external tools (`requires:`)
- [ ] Degrade path when the tool is absent

### L4 Load chain
- [ ] Foundation → hub → spoke edges resolve in `skills.registry.json`
- [ ] No missing `prerequisites` on the hub
- [ ] Cross-links to sibling hubs (a11y, security, QA) where sideways quality applies

### L5 Multi-voice + doctrine
- [ ] Lens table or guild/router for orthogonal review (or documented single-voice with rationale)
- [ ] `defers_to:` / Defers-to section if a plugin supplies overlapping depth
- [ ] `CLAUDE.md` / `_SKILLS.md` routing row if the domain is user-triggered by name

### Knowledge
- [ ] If durable insight emerged, `08-knowledge/<domain>/` entry proposed or written
- [ ] Empty knowledge folders are not left as forever-stubs after substantive domain work

---

## Authoring algorithm (supersedes naive "write a skill")

When the user asks to add or improve skills in a domain:

1. **Read this framework + #08 + the domain's L1** (create L1 first if missing and 3+ consumers exist).
2. **Map the five layers** for that domain — what already exists, what is missing.
3. **Prefer connective tissue over volume.** If spokes are already deep, invest in L1–L3 and linkage, not more prose.
4. **Wrapper before plugin depth.** If a Cursor/Claude plugin already holds technique depth, author a thin workspace hub that owns triggers, bans, and routing; do not fork the plugin into the vault.
5. **Measure before declaring audit.** Add or extend an L3 toolkit before marketing a new `--lens` or "security audit" claim.
6. **Run the acceptance checklist.** Then `build-related.py` → `build-registry.py` → validators.

Surfaces' native "create a skill" flows are **insufficient** if they skip this algorithm. Point them here.

---

## Domain instantiation map (workspace)

| Domain cluster | L1 | L2 | L3 | L4 | L5 |
|---|---|---|---|---|---|
| UI/UX / DS | #02, #09 | `/qa`, Impeccable, `DESIGN.md` | `visual-qa-toolkit` | `design-foundations` → leads → `uid-*`/`ux-*`/`ds-*` | `/qa --lens`, `lead-visual-qa` |
| Realtime photoreal / game look | #12 | `realtime-visual-craft` | `render-qa-toolkit` | imaging → 3D/game leads → production spokes | rendering guild |
| Accessibility | #02 (inclusive) + a11y done-gates | lead-a11y protocol | `a11y-audit-toolkit` | design/eng foundations → `lead-accessibility-architect` → `a11y-*` | `/qa --lens a11y` |
| Security | #16 | lead-security protocol + threat-model contract | scanners via `requires` + review-security | `eng-foundations` → `lead-security-architect` → `sec-*` | security as sideways lens |
| Engineering (FE/BE/DevOps) | #14 | `/eng` + ADRs/runbooks | perf/test/CI harnesses | `eng-foundations` → leads → `fe-*`/`be-*`/`devops-*` | arch-guild wrapper |
| Analysis / DS / PM evidence | #15 | lead-DS / lead-PM protocols | experiment validity + data-quality checks | `data-foundations` / `product-foundations` → leads → spokes | peer review lenses |
| Motion / Type / Graphic / Infod / Icon | #02 + craft notes | `/motion`, `/type`, lead protocols | `/qa` lenses + toolkit scripts | design-foundations → leads → spokes | visual-qa discipline spokes |
| Figma | #09 + DS ops | `/figma` | MCP + source-audit | `figma` hub → `figma-*` | Defers-to contracts |
| Career / Obsidian / Adobe / Vision / Science | thin L1 in hub or knowledge | wrapper hubs | validators / CLI where applicable | foundation or cross-cutting | doctrine precedence + routing rows |

Update this table when a cluster gains or loses a layer.

---

## Relationship to other frameworks

- **#08** — placement and write gates; this framework adds *rigor completeness*.
- **#06 / #10 / #11** — universal QA, perception, and failure premortem; domain L1s specialize them, never replace them.
- **#02 / #12 / #14 / #15 / #16** — concrete L1 instantiations.
- **Skill frontmatter `defers_to`** — machine-readable L5 plugin precedence.
- **Capability registry** — L3 external tools.

---

## Anti-patterns

- Adding a 40-line "hub" that only restates a backend spoke (security stubs).
- Shipping a vendored skill pack under `03-skills/` with no root `SKILL.md`.
- Declaring `--lens X` without a measurement path or discipline spoke.
- Letting plugin marketing-3D / generic TDD skills override workspace frameworks.
- Growing `08-knowledge/research/` for one domain while leaving other domain folders empty after years of use — retrieval trains agents to skip knowledge.

---

## Related

- [[08-workspace-contribution-framework]]
- [[02-ui-ux-operational-framework]]
- [[12-realtime-photoreal-operational-framework]]
- [[14-engineering-operating-model]]
- [[15-analysis-operating-model]]
- [[16-security-operating-model]]
- [[skill-frontmatter]]
- [[capability-registry]]
- [[AGENTS]]
