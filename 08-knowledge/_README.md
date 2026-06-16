---
tags: [knowledge-vault, meta]
created: 2026-04-28
status: active
---

# 08-knowledge — Domain Knowledge Vault

This vault section holds **accumulated domain insights** — the kind of knowledge that grows
over multiple sessions, spans multiple projects, and doesn't fit neatly into a skill file,
a session log, or a project state.

---

## What belongs here vs. elsewhere

| Type of content | Where it lives |
|----------------|---------------|
| How to do something (operational) | `03-skills/` |
| Active project state and decisions | `07-projects/NN-name/SESSION-STATE.md` |
| Session recap and what happened | `06-context/session-log.md` |
| Cross-session, cross-project insight | **`08-knowledge/`** ← here |
| Accumulated evidence from real work | **`08-knowledge/`** ← here |
| Research references and synthesis | **`08-knowledge/research/`** ← here |
| Working theories that evolve over time | **`08-knowledge/`** ← here |

The distinction: skills tell you *how*. Knowledge tells you *what we've learned* and *why
it matters in our specific context*.

---

## Structure

```
08-knowledge/
  _README.md          ← this file
  _INDEX.md           ← navigable index of all entries (auto-updated by Claude)
  design/             ← design domain insights (UX, visual, typography, motion, IA)
  engineering/        ← backend, frontend, devops insights
  data-science/       ← DS, ML, analytics, BI insights
  game-dev/           ← Legion-specific + general game dev knowledge
  research/           ← external research refs, synthesis, evidence
  cross-domain/       ← insights that span multiple domains
```

---

## Entry format

Each knowledge entry is a standalone markdown file. Suggested frontmatter:

```yaml
---
tags: [domain-tag, topic-tag]
created: YYYY-MM-DD
updated: YYYY-MM-DD
status: working | stable | superseded
confidence: high | medium | low | speculative
sources: [optional list of refs or session dates]
related_skills: [skill-name, ...]
related_projects: [project-name, ...]
---
```

**Status meanings:**
- `working` — actively being refined; treat as provisional
- `stable` — well-validated; treat as reliable context
- `superseded` — replaced by a newer entry; do not delete, link to replacement

**Confidence meanings:**
- `high` — validated by evidence or repeated experience
- `medium` — plausible and internally consistent, not yet validated
- `low` — early hypothesis; needs more evidence
- `speculative` — worth tracking but not yet actionable

---

## How Claude uses this vault

### Surfacing mechanism (automatic)

Two hooks make the vault active rather than passive:

1. **SessionStart** — `_INDEX.md` is loaded into every session's context automatically.
   Claude knows what entries exist from the moment the session opens.

2. **UserPromptSubmit** — `KNOWLEDGE_HINTS` in `dispatcher.py` maps trigger keywords
   (same ones used for skill routing) to entry paths. When a prompt contains "legion",
   "centric", "icon font", etc., the dispatcher injects a reminder to read the relevant
   entry *before proceeding*. The reminder appears alongside any skill hint.

3. **CLAUDE.md rule** — Before substantive domain work, Claude is instructed to check
   the index and read the relevant entry. This is the last line of defense if a trigger
   word wasn't in the prompt.

### What Claude does with entries

- **Reads** relevant entries before domain work begins — carries forward constraints and
  decisions from prior sessions without re-explanation
- **Writes** new entries when a session produces a durable insight worth preserving
- **Updates** existing entries when new evidence refines or contradicts a prior conclusion
- **Links** via frontmatter (`related_skills`, `related_projects`) and `[[wikilinks]]`

### When to write a new entry

Write an entry when:
- A decision is made whose *why* isn't captured anywhere else
- A constraint or hard-won lesson will affect future work in this domain
- Research synthesis produces a finding that should outlast the session
- A pattern is validated (or anti-pattern discovered) from real work

Do NOT write entries for:
- Session recaps → `06-context/session-log.md`
- Project-specific decisions → `SESSION-STATE.md`
- Operational how-to patterns → `03-skills/`

### Adding new triggers

To surface a new entry automatically on prompt match, add an entry to `KNOWLEDGE_HINTS`
in `.claude/hooks/dispatcher.py`. Format: `"keyword": "08-knowledge/domain/file.md"`.
Also add to `TRIGGER_WORDS` if a skill should also load.

---

## Relationship to skills

Skills and knowledge entries are complementary:

- A **skill** says: "when you encounter X, do Y"
- A **knowledge entry** says: "here's what we've learned about X from our actual work"

Example: `ds-experimentation/SKILL.md` covers how to design an A/B test. A knowledge
entry in `08-knowledge/data-science/experiment-learnings.md` might capture what specific
experiment designs have worked or failed in our context, what the stakeholders actually
care about, and where the canonical skill guidance doesn't quite fit our situation.

---

## Adding entries

1. Choose the right subdirectory (or `cross-domain/` if it genuinely spans multiple)
2. Use a descriptive filename: `topic-subtopic.md`
3. Add frontmatter
4. Write the insight, not the how-to
5. Add to `_INDEX.md`
6. Link via `[[wikilinks]]` to related entries, skills, and projects
