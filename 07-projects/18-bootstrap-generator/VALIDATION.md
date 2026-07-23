# Validation — the generator, proven end-to-end

_A colleague-facing proofboard. Plain-English contracts on the left, the actual evidence
on the right. If you want to try it yourself, jump to [Run it yourself](#run-it-yourself)._

**What this tool does, in one sentence:** it interviews you, then generates a personal
"second brain" — an Obsidian vault that is also a git repo and a set of AI skills tuned to
*how you actually work* — and wires it into your AI assistant (Claude, Cursor, and others).

**Status:** the whole command surface is built and green — 11 commands, ~2,270 lines of
zero-dependency Python. The *guided interview* (your AI filling everything in for you) is
early but works; the mechanical engine underneath it is solid and tested.

---

## The headline guarantee: skills are written at *your* altitude, per domain

The thing that makes this personal rather than generic: **expertise is captured per domain,
not as one global rating.** The same person is usually an expert in one area and a beginner
in another — and each generated skill is written at the right altitude for *its* domain.

**Proof (a real run).** Persona "Priya Nair" — a **staff-level UX expert** who is a
**hobbyist** in game design and 3D rendering, mixed work/personal workspace. One profile:

```yaml
use_context: mixed
expertise:
  ux-research:  { level: expert, seniority: staff, years: 12 }
  game-design:  { level: hobbyist }
  3d-rendering: { level: hobbyist }
```

The **same person's** two generated skills come out at opposite altitudes:

| Her **UX Research** skill (expert/staff) | Her **Game Design** skill (hobbyist) |
|---|---|
| _"Do NOT re-explain fundamentals — capture THEIR judgment: the hard-won calls, the edge cases, where even good practitioners slip. Peer-level and terse."_ | _"TEACH: define the jargon, explain the why, scaffold each step. Assume enthusiasm, not fluency; never assume prior knowledge."_ |
| Sections: When to use · How · Worked example · **Judgment calls & edge cases** · **Setting the bar & leading** · Anti-patterns · **Sources** | Sections: When to use · How · Worked example · **Foundations to learn** · Anti-patterns |

A hobbyist skill teaches; an expert skill assumes fluency and captures judgment (and, because
she's staff-level, how she sets the bar for others). Wrong altitude makes a skill useless —
fundamentals bore an expert, shorthand strands a beginner — so this is the core of the value.

---

## Plain-English contracts, and the evidence for each

| The tool promises… | Proven by |
|---|---|
| **Your workspace is yours** — Obsidian vault + git repo, no cloud-vendor lock-in. | `wsx init` scaffolds 16 files (vault + `git init` + first commit). ✓ |
| **Personal context stays walled.** Work/professional/personal live in separate files; anything personal-private is local-only and never synced. | Personal context is `.gitignored`; the MCP server excludes it unless you explicitly opt in. ✓ |
| **Skills match your level, per domain.** | The Priya proof above — same person, two altitudes. ✓ |
| **The best skills fuse your judgment with industry-leading references** — not just copied library skills. | Composite skills cite their sources in your own voice (`## Sources & further reading`, "distilled… not copied text"); `wsx lint` fails a composite that forgets to cite. ✓ |
| **Nothing from an unvetted source installs silently.** | A skill from an unvetted directory (`skills.sh`) is *refused* unless you've audited it. ✓ |
| **It works with more than one AI.** | Emits Claude Code, a universal MCP server (Cursor/Codex/Claude Desktop), Cursor rules, AGENTS.md, and a tool-less context pack. `emit all` → 10 files. ✓ |
| **A stranger can't accidentally ship a half-built workspace.** | `wsx lint` fails on un-enriched skeletons and missing citations; `wsx verify` re-checks that every pinned item still matches its pin. ✓ (the two lint flags in the run above are this gate working) |
| **The rigor keeps working after the generator is done.** Anything you build later — a new skill, hub, framework, or playbook — carries the same discipline. | Every workspace ships `frameworks/skill-authoring.md`, a supreme rule that **supersedes your AI's native skill-builder**; the emitted CLAUDE.md / AGENTS.md / Cursor rule / pack all point to it. ✓ |
| **You choose where it lives, on free hosting.** | `wsx remote` recommends a private GitHub/GitLab/Codeberg repo (or local-only) and wires it; you create your own repo, `wsx` never touches your accounts. ✓ |

Every claim here was produced by running the tool — not asserted. The commands are
`init · profile · emit · resolve · search · lint · verify · session · sync · remote · doctor · skill`.

---

## Run it yourself

You need an **AI assistant** (Claude recommended) and, to browse the result,
[Obsidian](https://obsidian.md). Then pick one:

### Path A — easiest (recommended): let your AI do it
1. Open **this generator folder** in your AI assistant (in Claude Code: open the folder, or
   run `claude` from inside it).
2. Say: **"set up my workspace."** In Claude Code the generator is a registered skill, so that
   phrase alone starts the interview — no need to name any file. *(On other assistants, nudge
   it once: "Read `brain/SKILL.md` and set up my workspace for me.")*
3. It interviews you — your tools, your work, your craft, your personal side, your preferences
   — **including how deep you go in each area** — then builds your workspace and tells you where
   it is.

### Path B — one double-click (no AI, nothing to type)
Double-click **`start.command`** (macOS) or **`start.bat`** (Windows). It checks Python, asks
two questions (where + your name), and creates a starter workspace you and your AI grow into.

### Path C — one terminal command
```bash
python3 generator/bin/wsx init ~/Documents/my-workspace --name "Your Name"
```
Stuck? `python3 generator/bin/wsx doctor` tells you where you are and the next step.

> **Tip for the interview:** it will ask, early, whether this workspace is for **work**,
> **personal life**, or **a blend** — and, per skill area, whether you're just getting into it
> or you go deep / do it professionally. Answer honestly per area; that's what tunes each skill
> to you. "A blend" and "a mix of levels" are the common, expected answers.

---

## Honest limitations (so nothing surprises you)

- **The guided interview is early.** In Claude Code the trigger is wired; elsewhere it may need
  the one-line nudge above. Paths B/C always work and never depend on the AI.
- **Reference *finding* is your AI's research, not a magic index.** The tool cites and pins the
  references your AI gathers; the built-in skill registries don't yet expose a public search
  index, so `wsx search` currently points you at their homepages (a local index works today).
- **Generated skills arrive as guided skeletons.** Your AI fills them with your actual know-how
  during the interview; the tool refuses to call them "done" while they're still blank.
