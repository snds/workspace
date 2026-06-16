---
status: draft
version: 0.1
date: 2026-06-13
tags: [bootstrap-generator, brain, synthesis, profile, interview]
part-of: "[[SPEC]]"
---

# Synthesis — interview answers → `profile.yaml` → seeded workspace

_How the **brain** turns what it heard in the interview into the machine-readable `profile.yaml`, then hands off to the **hands** (`wsx`) to scaffold the workspace._

> 🚧 **Early.** This describes the *intended* behaviour of the brain's synthesis step. The brain (the interview/judgment layer) and `wsx` (the deterministic CLI) are still being built. Where a behaviour is not yet implemented, it says so. Read this as the design contract synthesis must satisfy, not a record of shipped code.

---

## 0. Where synthesis sits

The interview (movements **M0–M5**, defined in `brain/interview.md` and SPEC §2) is a conversation. Synthesis is the quiet step *between* the last question and the first file: the brain reads everything it heard, decides each profile field, plays the result back for a yes (the **synthesize-and-confirm gate**), and only then writes anything.

```
M0–M5 answers ──▶ synthesis (this doc) ──▶ confirm gate ──▶ wsx profile set …  ──▶ profile.yaml
                                                          └▶ wsx init / resolve  ──▶ seeded workspace
```

Two hard rules govern everything below:

1. **The brain never hand-edits files.** Every value reaches disk through a `wsx` subcommand — synthesis emits a *plan of `wsx` calls*, not a YAML blob it pastes. (SPEC §6: "Everything mechanical is a `wsx` subcommand the skill invokes, never does inline.")
2. **Nothing is written before the confirm gate passes.** Synthesis is reversible up to that point; it is a proposal until the person says yes.

`profile.yaml` is one half of the seam contract (`manifest.json` is the other). Synthesis owns producing `profile.yaml`; the Resolver (SPEC §4, summarized in §6 here) owns what becomes `manifest.json`.

---

## 1. The `profile.yaml` shape (target)

Synthesis fills exactly this shape. It is the seam the CLI consumes — no field the CLI doesn't know about, no field left structurally absent (unknowns are written as explicit defaults or `null`, never silently dropped).

```yaml
schema_version: 1
identity:
  name: ""             # M0/M4
  handle: ""           # M0 — derived if not given (see §3)
surfaces:
  primary: ""          # M0 — the assistant they live in
  agents: []           # M0 — every assistant to emit for
  machines: []         # M0 — device labels (drives offline + separation)
models:
  tier: ""             # M0 — frontier | mixed | small-local
  offline: false       # M0 — do they need it to work with no network?
transport:
  type: "git"          # M0/M5 — git is the default; "local-only" if they refuse sync
  remote: ""           # M0 — repo URL, or "" if not chosen yet
contexts:
  work:
    role: ""           # M1
    summary: ""        # M1 — one-paragraph synthesis, the brain's words
  professional:
    crafts: []         # M2 — each becomes a lead-* hub candidate
  personal:
    private: true      # M5 — walled by default (see §4)
    interests: []      # M3
preferences:
  tone: ""             # M4
  verbosity: ""        # M4 — terse | balanced | thorough
  audience: ""         # M4 — who the output is usually for
  banned: []           # M4 — anti-patterns to never produce
lifecycle:
  continuity: ""       # M5 — session-log | daily-note | none
  separation: ""       # M5 — walled | blended
  automation: ""       # M5 — manual | assisted | auto
privacy:
  personal_local_only: true   # M5 — derived with separation (see §4)
  encrypt: false              # M5
imports: []            # M0 — existing assets to bring in
```

Synthesis writes **every** key. A field it could not determine gets its **sensible default** (§3), not omission — a structurally complete profile is what lets `wsx lint`/`verify` reason about it and what lets later sessions fill gaps without guessing whether a field was "never asked" or "asked and skipped."

---

## 2. Field-by-field mapping (movement → field)

Each row: the movement that surfaces it, the profile field it sets, and the synthesis judgment that turns prose into a value. "Judgment" is the part only the brain can do; everything after it is mechanical.

### M0 — Surfaces & infra → `surfaces`, `models`, `transport`, `imports`

| Heard | Field | Synthesis judgment |
|---|---|---|
| "I mostly use Claude / Cursor / Copilot…" | `surfaces.primary` | The one they *live in* becomes primary; it gets the richest adapter. |
| Every assistant named | `surfaces.agents[]` | Each named assistant is an **emit target** (`claude-code`, `cursor`, `agents-md`, `mcp`, `pack`). Primary is always included. Dedupe. |
| Their machines (laptop, work laptop, phone) | `surfaces.machines[]` | Normalize to short labels. Presence of a **work machine** is a signal for walled separation (§4). A phone signals "needs a no-terminal path." |
| Model access ("Pro plan", "local Llama", "frontier") | `models.tier` | `frontier` if they have on-demand strong models; `small-local` if local/limited; `mixed` if both. Tier drives capability tiering (SPEC §5): frontier → full on-demand network; small-local → pre-flattened pack of 8–15 highest-value skills. |
| "I need it to work on a plane / offline" | `models.offline` | `true` triggers the offline snapshot (a flattened context pack) at emit time. |
| How they sync today (Drive, git, nothing) | `transport.type` / `transport.remote` | Default `git`. If they have a repo, capture `remote`. If they actively refuse cloud sync, `transport.type: local-only` and leave `remote: ""`. |
| "I already have notes / a vault / docs…" | `imports[]` | Each importable asset is recorded as a path/URL + a short note on what it is. The brain does **not** read or move them here — `wsx` imports them later; synthesis only registers intent. |

### M1 — Work context → `contexts.work`

| Heard | Field | Synthesis judgment |
|---|---|---|
| Role / domain | `contexts.work.role` | Verbatim-ish title, normalized ("Senior PM, fintech"). |
| Recurring deliverables, constraints, standards, where time is lost | `contexts.work.summary` | The brain **synthesizes one paragraph in its own words** — not a transcript. This paragraph also seeds the work `project-context` file. Recurring-deliverable + standards language here is the raw material the Resolver uses to propose **work hubs/spokes**. |

### M2 — Professional craft → `contexts.professional.crafts[]`

| Heard | Field | Synthesis judgment |
|---|---|---|
| Deep expertise; craft pursued *outside* the employer; north-star standards | `contexts.professional.crafts[]` | Each distinct craft where the person shows **expertise-with-opinions** becomes a craft entry and a candidate **`lead-*` hub** (e.g. `lead-ux-designer`). **Energy is the hub-vs-spoke signal:** a craft they're merely dabbling in is recorded as a single spoke under a broader hub; a craft they have strong, opinionated standards in becomes a hub with 4–8 spokes. Synthesis records the craft; the Resolver (§6) decides pull/adapt/generate per craft. |

### M3 — Personal context → `contexts.personal.interests[]`

| Heard | Field | Synthesis judgment |
|---|---|---|
| Dream builds, hobbies, life admin (finances, taxes, health, language), creative pursuits, learning goals | `contexts.personal.interests[]` | Recorded **only for things the person volunteered** — M3 is guide-and-suggest, never push. Anything they skip is simply absent (not `null`-with-a-note, not inferred). These feed the **private** personal context file and personal-project scaffolding, governed by §4's privacy policy. |

### M4 — Operating preferences → `preferences`, `identity.name`

| Heard | Field | Synthesis judgment |
|---|---|---|
| "Be terse / explain your reasoning / talk to me like a peer" | `preferences.tone`, `preferences.verbosity` | Map to a small controlled vocab: `verbosity ∈ {terse, balanced, thorough}`; `tone` is a short phrase. |
| Who consumes the output (just me / my team / clients) | `preferences.audience` | Sets default audience for generated prose. |
| "Never do X" (em-dashes, emoji, hedging, marketing voice…) | `preferences.banned[]` | Each becomes a hard anti-pattern. These flow into `user-preferences` and into every adapter's instruction file. |
| Their name (if not already from M0) | `identity.name` | Captured here if M0 didn't get it. |

### M5 — Lifecycle & ambition → `lifecycle`, `privacy`, and the separation policy

| Heard | Field | Synthesis judgment |
|---|---|---|
| "I want it to remember where we left off" | `lifecycle.continuity` | `session-log`, `daily-note`, or `none`. Drives whether `wsx session start/end` writes history. |
| Walled vs blended work/personal | `lifecycle.separation` + the policy in §4 | `walled` or `blended`. **This single answer is load-bearing** — it sets three things at once (§4). |
| How much automation they want | `lifecycle.automation` | `manual`, `assisted`, or `auto` — how aggressively `wsx session`/`sync` run without asking. |
| Privacy / encryption appetite | `privacy.encrypt`, `privacy.personal_local_only` | See §4. |

---

## 3. Defaults when a field is unknown

A field can be unknown because it wasn't reached, the person deferred, or M3 was (rightly) skipped. Synthesis **never blocks on a missing field** and never guesses a person-specific value — it writes a safe, reversible default and notes the gap in the confirm playback so the person can correct it. Defaults bias toward **privacy, portability, and low surprise**.

| Field | Default when unknown | Why this default |
|---|---|---|
| `identity.handle` | slug of `identity.name` (e.g. "Maya Okafor" → `maya-okafor`); if no name, `user` | Namespacing pulled skills needs *some* stable handle; derivable, low-stakes. |
| `surfaces.primary` | `claude-code` | The recommended, fully-tested path (README); least likely to dead-end a first run. |
| `surfaces.agents` | `[surfaces.primary]` | Emit only what we're sure of; add targets later, non-destructively. |
| `surfaces.machines` | `[]` | Empty is honest; an empty machine list defaults separation toward walled (§4) on the safe side. |
| `models.tier` | `frontier` | Matches the recommended Claude path; if wrong, the only cost is offering a bigger network than needed. |
| `models.offline` | `false` | Offline is the special case; assume connected. |
| `transport.type` | `git` | The whole point is sync + history; `git` unless explicitly refused. |
| `transport.remote` | `""` | Never invent a remote. `wsx init` can create a local repo with no remote and add one later. |
| `contexts.work.*` | `""` | Empty work context is valid (e.g. a personal-only user). |
| `contexts.professional.crafts` | `[]` | No craft → no `lead-*` hub; nothing forced. |
| `contexts.personal.private` | `true` | **Privacy is the default, not an afterthought** (README/Privacy). Unknown ⇒ walled. |
| `contexts.personal.interests` | `[]` | M3 is opt-in; absence is expected and fine. |
| `preferences.tone` | `"neutral, direct"` | A defensible house style; easy to override. |
| `preferences.verbosity` | `balanced` | Middle of the ramp. |
| `preferences.audience` | `"self"` | Most second-brain output is for the owner first. |
| `preferences.banned` | `[]` | Don't invent prohibitions the person didn't state. |
| `lifecycle.continuity` | `session-log` | Continuity is the headline feature; default it on. |
| `lifecycle.separation` | `walled` | Safer default (§4). Blend is an explicit opt-in. |
| `lifecycle.automation` | `assisted` | Acts on routine ops but confirms anything destructive — matches "ask before changing privacy." |
| `privacy.personal_local_only` | `true` | Derived with separation; defaults locked-down. |
| `privacy.encrypt` | `false` | Offered, never imposed; local-only already covers most of the risk. |
| `imports` | `[]` | Only what the person pointed at. |

`schema_version` is **never** unknown — it's set by the tool, not the interview, and gates how `wsx` reads the file across versions.

---

## 4. How the M5 separation answer cascades (the load-bearing decision)

The single walled-vs-blended answer in M5 sets **three** independent mechanisms. Synthesis derives them together so they can't drift out of sync.

```
M5 separation answer ─┬─▶ contexts.personal.private   (the in-profile flag)
                      ├─▶ privacy.personal_local_only  (the never-sync rule)
                      └─▶ separation policy            (file layout + gitignore + encryption offer)
```

**If `walled` (the default):**

- `contexts.personal.private = true` and `privacy.personal_local_only = true`.
- **File layout:** work / professional / personal context live in **separate files** (SPEC decision #4). The personal file is the one that's gated.
- **Gitignore policy:** `wsx init` writes a `.gitignore` that **excludes the personal context file(s) from the repo entirely**, so `transport.type: git` never pushes them. Personal context is local-only — present on the machine, absent from every remote and every sync.
- **On-demand pull:** a one-word trigger pulls personal context into a session when the person explicitly asks (SPEC decision #4) — walled does not mean unreachable, it means not-synced and not-default-loaded.
- **Encryption:** if `privacy.encrypt = true`, synthesis records that the personal file should be written through `wsx`'s at-rest encryption (offered in the confirm gate for anyone walled).

**If `blended`:**

- `contexts.personal.private = false`, `privacy.personal_local_only = false`.
- Personal context may be committed and synced alongside work context. The gitignore does **not** exclude it.
- Synthesis still surfaces the consequence in the confirm playback in plain words ("your personal notes *will* sync to your repo — is that what you want?"), because this is the one place a wrong default leaks private life online. Blend is never inferred; it requires an explicit, informed yes.

**Safety overrides** (applied before the gate):

- A **work machine** in `surfaces.machines[]` with no explicit blend request ⇒ force `walled`. (SPEC decision #4: "wall it for anyone with a work machine.")
- `transport.type: local-only` makes the sync question moot but synthesis still sets `private`/`personal_local_only` truthfully so a *later* switch to `git` inherits the right policy.

The principle (README/Privacy): **err on the side of keeping private life private, and ask before changing that.** When the separation answer is ambiguous, synthesis defaults walled and confirms.

---

## 5. Writing the profile mechanically (`wsx profile set`)

Synthesis does not produce a YAML file. It produces an ordered **plan of `wsx profile set key=value` calls**, then executes them after the confirm gate. The brain's only filesystem verb here is `wsx`.

**Address syntax.** Dotted paths address nested keys; `[]` appends to a list; lists of scalars may be set in one call with a comma-separated value (the CLI validates and splits). Strings with spaces are quoted.

```bash
wsx profile set schema_version=1
wsx profile set identity.name="Maya Okafor"
wsx profile set identity.handle=maya-okafor
wsx profile set surfaces.primary=claude-code
wsx profile set surfaces.agents="claude-code,cursor"
wsx profile set surfaces.machines="personal-laptop,phone"
wsx profile set models.tier=frontier
wsx profile set models.offline=false
wsx profile set transport.type=git
wsx profile set contexts.work.role="Senior product designer, fintech"
wsx profile set contexts.work.summary="Owns the design system and ships flows for a payments app; loses time re-deriving token decisions and writing the same accessibility notes."
wsx profile set contexts.professional.crafts="design-systems,typography"
wsx profile set contexts.personal.private=true
wsx profile set contexts.personal.interests="bread-baking,japanese-language-learning"
wsx profile set preferences.tone="peer, direct, no hedging"
wsx profile set preferences.verbosity=balanced
wsx profile set preferences.banned="emoji,marketing-voice"
wsx profile set lifecycle.continuity=session-log
wsx profile set lifecycle.separation=walled
wsx profile set lifecycle.automation=assisted
wsx profile set privacy.personal_local_only=true
wsx profile set privacy.encrypt=false
```

**Contract the brain relies on (CLI-owned):**

- **`wsx profile set` validates against the schema and rejects unknown keys / bad enums.** If the brain emits an out-of-vocab value (e.g. `verbosity=chatty`), the call fails loudly rather than writing garbage — synthesis must map to the controlled vocab in §2 first.
- **`set` is idempotent and order-independent for scalars**, so a later session can correct one field with one call without rewriting the file.
- **`wsx profile get [key]`** reads back the written value — synthesis uses it to verify the round-trip before declaring the profile seeded.
- After the full plan runs, **`wsx lint`** confirms the profile is structurally complete and internally consistent (e.g. `private=true` ⟺ `personal_local_only=true`); the brain does not assert "done" until lint is clean (mirrors the workspace's verify-the-gate discipline).

**Why a plan, not a paste:** keeping every write behind `wsx` means the same synthesis output is replayable, diffable, and adapter-agnostic — and it preserves the seam (SPEC §6) that lets the CLI evolve its on-disk format without the brain knowing or caring.

---

## 6. Recording the skill plan (handoff to the Resolver)

The profile says *who the person is*; the **skill plan** says *what their workspace will know how to do*. Synthesis doesn't resolve skills itself — that's the Resolver (SPEC §4) — but it produces the Resolver's input and records the Resolver's output into `manifest.json` (again, via `wsx`, never by hand).

**What synthesis hands the Resolver:** for each capability/domain surfaced by M1 (work) and M2 (craft) — and any M3 personal project the person had real energy for — a candidate entry:

```
{ domain, hub-or-spoke (from energy), source-hint (M1 standards / M2 north-stars), surfaces }
```

**What the Resolver decides, per candidate** (recorded back into the plan):

- **PULL** — a strong registry match exists → pin + namespace; pulled skills are **read-only**.
- **PULL + PATCH** — ~70% match → pull it, put deltas in a **sibling overlay** (never edit the pulled skill).
- **GENERATE** — no match, or it's the person's unique IP / judgment / a personal project → author a new skill.

Bias (SPEC §4): **PULL** for generic, well-trodden domains; **ADAPT at ~70%**; **GENERATE** for what's uniquely theirs. Registries are pluggable, each with trust notes — `anthropics/skills` is high-trust; `skills.sh` is real but **unvetted** and must be audited before install.

**After resolution**, two mandatory steps the brain narrates and `wsx` records:

1. **Assign each skill to a hub and register its triggers** in `manifest.json`.
2. **Overlap reconciliation** (non-negotiable, SPEC §4): dedupe triggers across the network and name **one canonical owner per concern** so two skills never fight over the same trigger phrase.

The skill plan is written through `wsx resolve` (fetch/pin) and the manifest writes — synthesis's job is to *seed and order* the plan and to make the pull/adapt/generate intent legible in the confirm gate, not to fetch anything itself.

---

## 7. The confirm gate (what synthesis plays back)

Before a single `wsx` write, synthesis plays back a plain-language summary and waits for an explicit yes (SPEC §2: "ends with synthesize-and-confirm"). The playback covers:

- **Who I heard you are** — name, role, the one-paragraph work summary, the crafts that became hubs.
- **What I'll set up** — surfaces/adapters to emit, model tier, continuity + automation level.
- **Your privacy posture, stated plainly** — walled or blended, what syncs vs. stays local, encryption on/off — with the explicit "your personal notes *will* / *will not* sync" sentence.
- **The skill plan** — which capabilities will be pulled (and from where, with trust notes), which adapted, which generated fresh.
- **Anything I defaulted** — every field that fell back to §3, flagged so the person can correct it now.

Only on an explicit yes does synthesis run the `wsx profile set` plan, then `wsx init` / `wsx resolve` / `wsx emit`. A "not quite" loops back into the relevant movement, re-synthesizes, and re-plays. The gate is the last reversible point.

---

## 8. Worked example

A short fictional persona, run through synthesis end to end.

### 8.1 What the interview heard

> **Maya Okafor.** Lives in **Claude** day to day, but also uses **Cursor** for code. One **personal MacBook** and a **work-issued laptop**; an **iPhone**. On Claude's Pro plan ("whatever the good model is"), always online. Syncs nothing today but "would love history across machines."
>
> **Work:** senior product designer at a fintech; owns the **design system**, ships payment flows. Loses time re-deriving token decisions and re-writing the same accessibility notes on every handoff. Standard she holds the line on: **WCAG AA, no exceptions.**
>
> **Craft:** strong, opinionated about **design systems** generally and **typography** specifically — reads type history for fun, has Hard Opinions. Dabbles a little in **motion** but "wouldn't call myself good at it."
>
> **Personal (volunteered):** **bread baking**; learning **Japanese**. Skipped the finances/health prompts. Wants personal stuff kept **off her work laptop and out of any cloud**.
>
> **Preferences:** talk to her **like a peer, no hedging**; **no emoji**, **no marketing voice**; output is usually for **her team**.
>
> **Lifecycle:** wants it to **remember where we left off**; **walled** work/personal; happy for it to **act on routine stuff but ask before anything destructive**; interested in **encrypting** the personal notes.

### 8.2 Synthesis decisions

- Two emit targets (`claude-code` primary, `cursor`); `mcp` is available later but not asked-for, so not added now.
- A **work machine present + explicit "off my work laptop"** ⇒ `separation: walled`, `personal.private: true`, `personal_local_only: true`, and `encrypt: true` (she opted in). The personal context file will be **gitignored**.
- **Design systems** and **typography** show expertise-with-opinions ⇒ each a **hub candidate** (`lead-ds`, `lead-type-designer`). **Motion** is a dabble ⇒ a single spoke, not a hub.
- Resolver intent (for the confirm gate, resolved in the next step): design-systems and typography are well-trodden ⇒ **PULL** strong registry skills + **PATCH** Maya's "WCAG-AA-no-exceptions" and token-decision standards as an overlay; the payments-flow specifics and her personal projects ⇒ **GENERATE**.
- M3 finances/health were skipped ⇒ simply absent. `interests` holds only what she gave.
- `handle` derived from name (`maya-okafor`); `transport.remote` left `""` (she has no repo yet — `wsx init` makes a local one).

### 8.3 Resulting `profile.yaml`

```yaml
schema_version: 1
identity:
  name: "Maya Okafor"
  handle: "maya-okafor"
surfaces:
  primary: "claude-code"
  agents: ["claude-code", "cursor"]
  machines: ["personal-macbook", "work-laptop", "iphone"]
models:
  tier: "frontier"
  offline: false
transport:
  type: "git"
  remote: ""
contexts:
  work:
    role: "Senior product designer, fintech"
    summary: >-
      Owns the design system and ships payment flows for a fintech app.
      Holds WCAG AA with no exceptions. Loses time re-deriving token
      decisions and re-writing the same accessibility notes on every
      design-to-dev handoff.
  professional:
    crafts: ["design-systems", "typography"]
  personal:
    private: true
    interests: ["bread-baking", "japanese-language-learning"]
preferences:
  tone: "peer, direct, no hedging"
  verbosity: "balanced"
  audience: "team"
  banned: ["emoji", "marketing-voice"]
lifecycle:
  continuity: "session-log"
  separation: "walled"
  automation: "assisted"
privacy:
  personal_local_only: true
  encrypt: true
imports: []
```

### 8.4 The `wsx` plan that produced it (excerpt)

```bash
wsx profile set schema_version=1
wsx profile set identity.name="Maya Okafor"
wsx profile set identity.handle=maya-okafor
wsx profile set surfaces.primary=claude-code
wsx profile set surfaces.agents="claude-code,cursor"
wsx profile set surfaces.machines="personal-macbook,work-laptop,iphone"
wsx profile set models.tier=frontier
wsx profile set contexts.work.role="Senior product designer, fintech"
wsx profile set contexts.work.summary="Owns the design system and ships payment flows for a fintech app. Holds WCAG AA with no exceptions. Loses time re-deriving token decisions and re-writing the same accessibility notes on every design-to-dev handoff."
wsx profile set contexts.professional.crafts="design-systems,typography"
wsx profile set contexts.personal.private=true
wsx profile set contexts.personal.interests="bread-baking,japanese-language-learning"
wsx profile set preferences.tone="peer, direct, no hedging"
wsx profile set preferences.verbosity=balanced
wsx profile set preferences.audience=team
wsx profile set preferences.banned="emoji,marketing-voice"
wsx profile set lifecycle.continuity=session-log
wsx profile set lifecycle.separation=walled
wsx profile set lifecycle.automation=assisted
wsx profile set privacy.personal_local_only=true
wsx profile set privacy.encrypt=true
# verify round-trip, then lint
wsx profile get
wsx lint
```

Then, separately (the Resolver, SPEC §4): `wsx resolve` pulls + pins the design-systems and typography skills, the overlay carries Maya's WCAG/token standards, generated skills cover her payments work, hubs/triggers land in `manifest.json`, and overlap reconciliation names one canonical owner per concern — all surfaced in the confirm playback before anything is fetched.

---

## 9. Open questions (synthesis-specific)

- **Controlled-vocab boundaries.** The exact enums for `tone`/`verbosity`/`automation` need pinning in the `profile.yaml` schema (Phase 0) so `wsx profile set` can validate them — §2 names the intent, not the final list.
- **Multi-value `set` vs. repeated `[]` appends.** Whether comma-joined scalars or explicit `key[]=` appends is the canonical list-write form is a CLI decision (Phase 0); this doc assumes comma-join for brevity.
- **Re-synthesis on later sessions.** How synthesis behaves when a profile already exists (patch only changed fields vs. full re-confirm) — likely "patch + mini-confirm," but unspecified until the lifecycle adapter lands.
- **Where the skill plan physically lives** before it's committed to `manifest.json` (a staged plan file vs. in-memory) is a Resolver/CLI concern this doc defers to SPEC §4.
