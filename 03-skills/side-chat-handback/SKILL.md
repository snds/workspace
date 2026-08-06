---
name: side-chat-handback
description: >
  Close a Cursor (or any-surface) side chat / detour and hand the outcome back to the
  parent thread automatically via a workspace inbox — no copy/paste. Run when Sean says
  "/handback", "handback", "end side chat", "close side chat", "hand this back", or
  "injection for the main chat". Writes 06-context/side-chat-inbox.md for the parent
  to consume on its next turn; optionally pbcopy; optionally mints an Open Engine
  Agent Todo pointer when claimable work remains. Not a full /session-end.
aliases: [side-chat-handback, handback]
triggers:
  - handback
  - /handback
  - end side chat
  - close side chat
  - hand this back
  - hand back
  - injection for the main chat
  - side chat done
tier: cross-cutting
domain: workspace
related: [workspace-bootstrap, open-agent-engine]
surfaces: ["*"]
spec_version: "2.0"
---

# Side-chat handback — end the detour, not the session

Closes a **side chat / by-the-way detour** and delivers its outcome to the **parent**
thread without Sean copy/pasting. This is the automated form of the preference in
[[user-preferences]] → "Side Detours — Injection Handback".

**Not** `/session-end`. No session fragment, no commit, no push, no Live-handoff rewrite
unless Sean asks. Durable file edits from the detour are already on disk; this only
moves the *continuity note* the parent needs.

**Not** Open Engine by default. The inbox is local continuity (desk sticky between two
tabs). Mint an Open Engine `Agent Todo` **only** when the detour left claimable work
that should survive if the parent dies — same "movement, never substance" rule as
[[open-agent-engine]] ritual integration.

## Trigger phrases

`/handback`, "handback", "end side chat", "close side chat", "hand this back",
"hand back", "injection for the main chat", "side chat done".

## Resolve the workspace root

Nearest ancestor of cwd (or the known brain path) that contains `AGENTS.md`. Fallbacks
the doctor already uses: `~/.claude/workspace-brain-path`, `~/Projects/Workspace`,
`~/Projects/workspace`. All paths below are relative to that root.

Inbox path (always):

```
06-context/side-chat-inbox.md
```

Gitignored on purpose — ephemeral, one pending slot, not session history.

## Protocol

### 1 — Draft the handback (one screen, no essay)

From this side chat only, produce:

| Field | What to write |
|---|---|
| **For the parent** | One paragraph Sean could have pasted: outcome + what it means for the main work + any next action for the parent |
| **On disk** | Bullet list of files this detour created/updated (paths relative to workspace or owning repo). Empty → `none` |
| **Open Engine** | `none` **or** a lane-qualified pointer (`personal:SEA-N`) if you create a Todo in step 3 |
| **Parent hint** | Short label for which main thread this belongs to (project / topic), best-effort |

Omit empty fluff. Prefer pointers over substance (link the memory/decision file; don't re-paste the whole decision).

### 2 — Write the inbox (overwrite the single pending slot)

If `06-context/side-chat-inbox.md` already exists with `status: pending`, keep a short
`## Prior unconsumed` section at the bottom quoting its old "For the parent" paragraph
(so nothing silently disappears), then write the new handback as the primary body.

Write the file with this shape:

```markdown
---
status: pending
created: {ISO-8601 with offset}
source: side-chat
parent_hint: {short label}
surface: {Cursor | Claude Code | …}
agent: {model or agent id if known}
---

# Side-chat handback

## For the parent

{one paragraph}

## On disk

- {path} — {what changed}
- none

## Open Engine

none
# or: minted personal:SEA-N — {title}; substance at {path}

## Consume

Parent thread: fold **For the parent** into your next reply, act on any next action,
then set `status: consumed` in the frontmatter (or delete this file). Do not leave
`pending` after you have used it.
```

### 3 — Optional Open Engine Todo (only when claimable)

Create an `Agent Todo` **only if** all of:

1. Something still needs doing after this chat is gone, **and**
2. It is not already captured as durable pending in `project-context.md` / Live handoff, **and**
3. Sean did not say this was "just a terminology / docs note" with no follow-up.

Pointer-shaped only — title + reference to where substance lives. Follow
[[open-agent-engine]] (lane ask if ambiguous; never put employer substance on `personal`).
Put the lane-qualified id under **Open Engine** in the inbox.

Most handbacks are `none` here. Today's vendor-term correction is a `none`.

### 4 — Clipboard (best-effort, never blocking)

If a shell is available, copy the **For the parent** paragraph only:

```bash
# macOS
printf '%s' "$PARAGRAPH" | pbcopy
# or via the helper:
python3 09-tools/side-chat-handback.py --clip-from-inbox
```

If clipboard fails, continue — the inbox is the source of truth.

### 5 — Confirm to Sean (then stop)

One short reply, then **do not keep chatting** unless he asks:

```
Handed back → 06-context/side-chat-inbox.md (pending).
Parent will pick it up on its next turn. Clipboard: {ok|skipped}.
Open Engine: {none|personal:SEA-N}.
```

You may close with nothing else. This *is* the end of the side chat.

## Parent pickup (the other half)

Any **parent / main** agent — before continuing substantive work on a turn — MUST:

1. Resolve the workspace root (same fallbacks as above).
2. If `06-context/side-chat-inbox.md` exists and frontmatter `status:` is `pending`, **read it first**.
3. Fold **For the parent** into the reply (or act on it silently if the user message already continues that work).
4. Mark consumed: set `status: consumed` **or** delete the file.
5. If **Open Engine** names an issue, treat it as queued work to acknowledge — do not auto-claim at pickup.

Wired in: `.cursor/rules/brain.mdc`, `04-preferences/user-preferences.md`, and the Claude
`/handback` slash command under `.claude/skills/side-chat-handback/`.

## Anti-patterns

- Running `/session-end` from a side chat "to be safe" — wrong tool; pollutes the session log.
- Pasting the full detour transcript into the inbox — handback is a paragraph + pointers.
- Filing every handback as an Open Engine issue — over-tracking; inbox is enough for continuity.
- Calling our own bespoke edits "vendored" in the handback prose — see [[feedback-vendor-terminology]].
