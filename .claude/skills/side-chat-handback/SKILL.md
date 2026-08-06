---
name: side-chat-handback
description: Close a side chat / detour and hand the outcome to the parent thread via 06-context/side-chat-inbox.md (no copy/paste). Invoked as /handback or "end side chat" / "hand this back". Not a full /session-end.
---

# /handback — End the side chat, hand back to parent

Canonical procedure: **`03-skills/side-chat-handback/SKILL.md`**. Follow that file
end-to-end (this slash command is the Claude surface entry; do not fork the protocol here).

## Quick path

1. Load `03-skills/side-chat-handback/SKILL.md`.
2. Draft the one-paragraph **For the parent** + on-disk bullets.
3. Write `06-context/side-chat-inbox.md` (`status: pending`).
4. Optional: `python3 09-tools/side-chat-handback.py --clip-from-inbox`.
5. Optional Open Engine Todo only if claimable work remains.
6. Confirm to Sean in one short line, then stop.

Trigger phrases: `/handback`, "handback", "end side chat", "close side chat",
"hand this back", "injection for the main chat".
