# The Resolver — skill-sourcing decision protocol

_Brain-side protocol. Authored once as neutral markdown; emitted to each surface (Claude skill, `AGENTS.md`, context pack). This is judgment and narration — the **brain** decides; it never touches the filesystem. Every mechanical step (fetch, pin, namespace, write) is handed to `wsx resolve`._

---

## What the Resolver is for

The interview (M0–M5) surfaces a set of **capabilities** the person needs their assistant to be good at — domains where they have recurring work, deep craft, or personal projects. The Resolver turns that list into an actual skill network: for each capability, it decides **where the skill comes from**, **which hub owns it**, and **what triggers fire it** — then reconciles the whole set so no two skills fight over the same concern.

It runs once per capability surfaced, in a single pass, after the synthesize-and-confirm gate has locked the profile. Its inputs are `profile.yaml` (who the person is) and the capability list distilled from the interview. Its output is a **skill plan** the person approves before anything is fetched or written.

The Resolver is the second half of a clean seam:

- **Brain (this protocol):** read registries, judge match quality, decide PULL / PULL+PATCH / GENERATE, assign hubs, draft triggers, reconcile overlaps, narrate the plan, ask for the go-ahead.
- **Hands (`wsx resolve`):** given the approved plan, do the deterministic work — fetch each pulled skill, pin it to a content hash, drop it into a namespaced read-only path, scaffold overlay and generated-skill directories, and update `manifest.json`.

The brain calls `wsx resolve` once, at the end, with the approved plan. It never fetches a URL, writes a file, or edits the manifest inline.

---

## The funnel: PULL → PULL+PATCH → GENERATE

For each capability, walk it through three gates in order. Stop at the first that fits.

```
capability
   │
   ▼
 search registries ──► STRONG match (well-trodden, license-clean, trusted)
   │                        └─► PULL          (pin + namespace; read-only)
   │
   ├──────────────────► PARTIAL match (~70%: right shape, wrong details)
   │                        └─► PULL + PATCH  (pull read-only + sibling overlay)
   │
   └──────────────────► NONE / proprietary / personal / uniquely-yours
                            └─► GENERATE      (new canonical skill, from scratch)
```

### PULL — a strong match exists

**When:** the capability is **generic and well-trodden** — a domain many people need, where a mature public skill already encodes the standard. Accessibility auditing, conventional-commit hygiene, Markdown/MDX authoring, SQL formatting, common framework idioms. If a vetted skill covers it at high fidelity and its license/trust are clean, pull it.

**Decision heuristic — bias toward PULL when:**
- The domain is common knowledge, not the person's differentiator.
- A skill from a **trusted anchor** registry (see below) matches the capability's intent and scope.
- The skill's instructions would be roughly what you'd write anyway — adopting it saves work and inherits upstream maintenance.

**What happens:** the brain records `source: pull` with the exact skill id and registry. `wsx resolve` fetches it, **pins it to a content hash**, and places it under a **namespaced, read-only** path. Pulled skills are never edited — see [Pin, namespace, read-only](#pin-namespace-read-only).

### PULL + PATCH — a partial match (~70%)

**When:** a public skill is the **right shape but wrong in the details** — its anatomy, structure, and most of its guidance fit, but it assumes conventions the person doesn't hold, names tools they don't use, or misses a constraint specific to them. Roughly **70% match** is the sweet spot: enough that rewriting from scratch is wasteful, not so much that you can adopt it untouched.

**Decision heuristic — choose ADAPT (PULL+PATCH) when:**
- The skill's *bones* are right (correct domain, sensible structure) but it carries assumptions to override — a different framework, a house style, an extra rule.
- You'd keep most of it and change a minority — terminology, a few examples, one or two added guardrails.
- Above ~70% match but below "adopt as-is": patch it. Below ~70%, it's usually cleaner to GENERATE than to fight a large overlay.

**What happens:** the brain records `source: pull`, plus a sibling **overlay** describing the deltas (added triggers, overridden rules, house-style notes). `wsx resolve` pulls and pins the upstream skill **read-only**, then scaffolds the overlay **next to it, never inside it**. The pulled skill stays pristine and re-fetchable; the patch is a separate, owned artifact. See [Patches live in an overlay](#patches-live-in-an-overlay).

### GENERATE — nothing fits, or it's uniquely theirs

**When:** no registry has a real match, **or** the capability is the person's own IP, judgment, or a personal project — the things that make their assistant *theirs* rather than a generic install. Their employer's internal standards, the way they specifically run a craft, their named side projects, household-specific life admin. Pulling a stranger's approximation here is worse than useless; it imports someone else's opinions into the person's most personal surface.

**Decision heuristic — choose GENERATE when:**
- The capability encodes the person's **unique IP or judgment** — proprietary process, hard-won opinions, a signature method.
- It's a **personal project** or life-admin domain with no meaningful public analogue.
- Registry search returns nothing close (below the ~70% ADAPT floor), or every candidate is license-encumbered or untrusted.

**What happens:** the brain authors a fresh **canonical** skill (markdown + frontmatter, in the canonical format) grounded in what the interview captured. `wsx resolve` scaffolds the skill directory under the canonical `skills/` tree (owned, editable — not read-only, since it's the person's own). Generated skills are the workspace's first-class citizens; pulled and patched ones orbit them.

### One-line bias summary

> **PULL** for generic, well-trodden domains · **ADAPT** at the ~70% mark · **GENERATE** for the person's unique IP, judgment, and personal projects.

When genuinely torn between two gates, prefer the one that keeps the person's distinctiveness in **owned** files: ADAPT over a strained PULL, GENERATE over a strained ADAPT.

---

## The registry model

Registries are **pluggable sources**. The Resolver doesn't hardcode one directory; it queries a configured list, each with its own **fetch mechanism** and its own **license / trust profile**. Trust is not uniform — a match's *provenance* changes the decision.

| Registry | What it is | Trust | Fetch / license notes |
|---|---|---|---|
| **`anthropics/skills`** | Official example skills (the standard's reference set) | **High — trusted anchor** | Reference-quality, license-clear. Default first stop for a PULL. |
| **`agentskills.io`** | The open Agent Skills standard / directory | **High — trusted anchor** | Vendor-neutral standard. The format itself; matches here are safe to pull. |
| **`skills.sh`** | Vercel's community skill directory | **Low — UNVETTED** | **Real and useful, but community-submitted and not officially reviewed. AUDIT before installing anything.** Never auto-pull; read the skill's contents, check the license, confirm it does what it claims. |
| **Community sources** | Other public skill repos / indexes | **Varies — verify per source** | Treat like `skills.sh` unless a source has established trust. License + content check mandatory. |
| **The person's own imports** | Assets named in M0 (existing skills, notes, configs) | **High — it's theirs** | Pulled from `profile.imports[]`. Owned content; can be adopted or used as raw material for GENERATE. |

**Rules of the registry model:**

- **Trusted anchors first.** When searching, weight `anthropics/skills` and `agentskills.io` as the high-confidence anchors. A clean match there is the most defensible PULL.
- **`skills.sh` is unvetted — audit before install.** This caveat is load-bearing. `skills.sh` is genuinely valuable and worth searching, but it is a **community** directory with no official vetting. The brain must **audit any `skills.sh` candidate before recommending a PULL**: read the actual skill body, confirm the license permits use, and sanity-check that its triggers and instructions match its description. Flag it in the plan as community-sourced so the person sees the provenance. Never silently pull from `skills.sh`.
- **License and trust notes ride with every candidate.** When a capability matches a skill, the brain carries that skill's `source registry`, `license`, and a one-line `trust` note into the plan. The person sees where each skill came from before approving.
- **Sources are pluggable.** New registries can be configured in; the protocol is the same for each — fetch capability + license/trust note. Don't assume the list above is exhaustive; treat it as the default set.

---

## Pin, namespace, read-only

Three invariants protect the workspace from supply-chain drift and from the person accidentally diverging from upstream.

### Pin

Every pulled skill is **pinned to a content hash** at resolve time. The plan records the exact version fetched; `wsx resolve` writes that pin into `manifest.json`. A later `wsx resolve` re-fetches against the pin, so a remote skill changing under the person's feet is a deliberate, visible bump — never a silent mutation.

### Namespace

Pulled skills live under a **namespaced** path that records their origin (e.g. keyed by registry + skill id), kept separate from the person's canonical `skills/` tree. Namespacing prevents two registries' identically-named skills from colliding, and makes provenance obvious at a glance: canonical = theirs, namespaced = pulled.

### Read-only

**Pulled skills are READ-ONLY.** The brain never edits a pulled skill in place, and the emitted workspace treats those paths as immutable. The reasons: a pinned skill must stay byte-identical to its pin to be verifiable and re-fetchable; and an edit in place would be silently lost on the next resolve. If a pulled skill needs to change, that's not an edit — it's a **patch**, and patches go in an overlay.

### Patches live in an overlay

When a capability resolves to **PULL+PATCH**, the deltas live in a **sibling overlay** — a separate, owned artifact next to the read-only pulled skill, never inside it. The overlay holds: added or overridden triggers, rules that supersede the upstream skill, house-style notes, swapped examples. At load time the surface composes `pulled skill (read-only base) + overlay (the person's deltas)`. This keeps the upstream skill pristine and re-fetchable while the person's customizations remain a first-class, version-controlled thing they own.

> **Never edit a pulled skill. Patch it in the overlay.** This is the single most important invariant in the Resolver.

---

## Hub / spoke assignment — from interview energy

Where a skill lands in the network is decided by the **energy signal** the interview captured, not by the registry it came from.

- **The energy heuristic.** When the person was a **dabbler** in a domain — interested, but without strong opinions or depth — the capability becomes a **single spoke**. When they were an **expert with opinions** — fluent, opinionated, the domain is part of their identity — it becomes a **hub** with its own **4–8 spokes** beneath it. Breadth surfaced lightly → spoke; depth surfaced with energy → hub.
- **Hubs by context.** M1 (work) yields work hubs/spokes; M2 (professional craft) yields the `lead-*` craft hubs; M3 (personal) yields private personal hubs/spokes. A skill's hub assignment follows the movement that surfaced it.
- **Every skill gets exactly one hub.** A spoke belongs to one hub. A pulled or patched skill is assigned to whichever hub owns its concern — provenance doesn't change ownership; the person's network topology does.
- **Overlaps are the prize.** The three contexts (work / professional / personal) deliberately overlap — a Venn, not silos. Where a capability sits in the overlap (a craft the person does both at work and on the side), it's often the **highest-value skill**, and it needs a deliberate single owner — which is exactly what reconciliation settles next.

Record each skill's `hub` (or `hub: <name>` + `role: hub` for the hub itself) in the plan, derived from the energy and the movement that surfaced it.

---

## MANDATORY overlap reconciliation

After every capability has a source decision, a hub, and draft triggers, the Resolver runs a **required** reconciliation pass over the whole set. This is not optional and not skippable — overlapping triggers are the most common failure mode of a multi-skill network, and the interview's deliberate context-overlap guarantees they'll occur.

**The pass does two things:**

1. **Dedupe triggers.** Walk every skill's trigger list against every other's. Where two skills would fire on the same word or phrase, resolve the collision: narrow one skill's triggers, hand the shared trigger to a single skill, or split the concern. No trigger should route to two skills ambiguously.
2. **Name one canonical owner per concern.** For each concern (a topic, a deliverable, a domain), exactly **one** skill is the canonical owner — the one that fires and, if needed, delegates to others. Overlapping skills get an explicit ownership decision: who owns the concern, who defers. This is most acute in the work/professional/personal overlap, where the same craft may have surfaced in two movements.

The reconciliation decisions (which trigger went where, who owns each contested concern) are part of the plan the person approves, and are written into `manifest.json` by `wsx resolve` so the routing index reflects the resolved, de-conflicted state. `wsx lint` later re-checks for trigger overlaps and will flag any that slipped through — but the brain reconciles **before** install, not after.

---

## The hand-off to `wsx resolve`

The seam is strict. The brain produces a fully-decided plan; `wsx resolve` executes the mechanical half.

**The brain has done (judgment):**
- Searched registries; judged each match's quality and provenance.
- Chosen PULL / PULL+PATCH / GENERATE per capability.
- Assigned each skill a hub (from interview energy) and drafted triggers.
- Run the mandatory overlap reconciliation; named a canonical owner per concern.
- Carried license/trust notes (and any `skills.sh` audit result) into the plan.

**`wsx resolve` then does (mechanics, no model):**
- **Fetch** each pulled skill from its registry.
- **Pin** each to a content hash.
- **Namespace** pulled skills into read-only paths; scaffold **overlay** dirs for patches; scaffold canonical dirs for generated skills.
- **Register** the de-conflicted triggers and hub assignments into `manifest.json` (the routing index).

The brain invokes `wsx resolve` **once**, with the approved plan as input. It does not fetch, pin, namespace, or write anything itself — if a step is mechanical, it belongs to `wsx`.

### The machine plan — `context/skill-plan.json`

The plan the brain hands over is a **JSON file** (the brain authors it as its decision record, the same way it writes prose context notes; every *structural* effect that follows — skill dirs, pins, the manifest — is `wsx`'s to make). One object per capability, in a top-level `skills[]`:

```json
{
  "skills": [
    { "name": "a11y-audit", "source": "pulled",
      "registry": "anthropics/skills", "url": "https://…/SKILL.md",
      "hub": "lead-frontend", "triggers": ["a11y", "wcag"],
      "license": "MIT", "trust": "trusted anchor" },

    { "name": "react-house-style", "source": "pulled+patched",
      "registry": "agentskills.io", "url": "https://…/SKILL.md",
      "hub": "lead-frontend", "triggers": ["react"] },

    { "name": "zine-layout", "source": "pulled",
      "registry": "skills.sh", "url": "https://…/SKILL.md",
      "hub": "lead-graphic", "triggers": ["zine"], "audited": true },

    { "name": "internal-plm", "source": "generated",
      "hub": "work", "kind": "spoke", "triggers": ["plm"],
      "desc": "Our proprietary PLM data-table workflow." }
  ]
}
```

Per-entry fields: `name`, `source` (`pulled` | `pulled+patched` | `generated`); for pulls also `registry`, `url` (the fetch source — `http(s)://`, `file://`, or a local path), and optional `license` / `trust`; for generates, `desc` + `kind` (`hub` | `spoke`). `hub` and `triggers` carry the brain's hub assignment and **reconciled** triggers. **`audited: true` is mandatory on any entry from an unvetted registry** (`skills.sh`, community) — `wsx resolve` refuses it otherwise.

Then, after the review gate below passes, run it once:

```
wsx resolve                 # executes context/skill-plan.json
wsx resolve --plan <file>   # point at a plan elsewhere
wsx resolve --update        # bump the pin when an upstream skill has changed
wsx resolve --allow-unvetted# permit unvetted pulls not marked audited (use sparingly)
```

`wsx resolve` fetches + **pins** each pull (stored byte-identical, `0o444` read-only under `skills/pulled-<registry>-<name>/`), scaffolds an editable `overlay.md` beside each PULL+PATCH, delegates each GENERATE to the `wsx skill add` skeleton, and registers every skill (with pin, registry, provenance, and the assigned hub/triggers) into `manifest.json`. It is idempotent: an unchanged pull is a no-op; a changed upstream is **skipped with a visible warning** until you pass `--update`. Afterwards, `wsx verify` re-checks that every pinned skill still matches its pin.

> **Note on pulled-skill triggers.** A pulled skill is byte-identical to upstream, so the emitted surface routes on *its* front-matter triggers. To override or add triggers for a pulled skill, put them in its **overlay** — never edit the pulled file. (Overlay→surface composition is wired for the recommended Claude-Code path; treat other surfaces as base-only for now.)

---

## The review gate — the skill plan

**Nothing is fetched, pinned, or written until the person says yes.** Before calling `wsx resolve`, the brain plays back the full plan as a single review table and asks for a go-ahead. This is the Resolver's analogue to the interview's synthesize-and-confirm gate.

Present it like this — one row per capability:

| Capability | Source decision | Registry / provenance | Hub · spoke | Triggers | Notes |
|---|---|---|---|---|---|
| Accessibility auditing | **PULL** | `anthropics/skills` · trusted, MIT | `lead-frontend` · a11y spoke | `a11y`, `wcag`, `contrast` | Adopt as-is. |
| House React conventions | **ADAPT** (pull+patch) | `agentskills.io` base + overlay | `lead-frontend` · react spoke | `react`, `component` | ~70% match; overlay adds house style, bans class components. |
| Internal PLM workflow | **GENERATE** | — (proprietary IP) | `work` hub · PLM spoke | `plm`, `data table` | Authored from M1; uniquely theirs. |
| Print zine layout | **PULL** | `skills.sh` · ⚠ community, audited | `lead-graphic` · layout spoke | `zine`, `print layout` | **From skills.sh — unvetted directory; audited contents + license before recommending.** |
| Woodworking projects | **GENERATE** | — (personal project) | `personal` hub · woodworking spoke | `workshop`, `joinery` | Private context; local-only. |

**What the table makes visible — and what the person is approving:**
- **Every source decision** and the heuristic behind it (generic→pull, ~70%→adapt, unique→generate).
- **Provenance and trust**, including an explicit ⚠ marker and audit note on anything from `skills.sh` or another unvetted source.
- **The network shape** — which hub owns each skill, derived from the energy they showed.
- **The de-conflicted triggers** — the output of the mandatory reconciliation pass, so the person can spot a routing they'd want changed.

The brain narrates the table, calls out anything noteworthy (every ADAPT's deltas, every unvetted source, every reconciliation tie-break), and asks plainly: **"Approve this plan, or change anything before I build it?"** Only on an explicit yes does it hand the approved plan to `wsx resolve`. Changes loop back into the table; the gate runs again. No silent installs, ever.
