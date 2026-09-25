---
lifecycle: define
---

## Project intent

### Problem & audience

People who want a personal "second brain" that works with any AI assistant should get one built from
an interview, not hand-assembled. The audience is a friend or colleague with a folder-capable AI
assistant (Claude recommended), who is not necessarily a developer.

### Knowns & unknowns

| claim | label | tier | evidence | decision rule |
|---|---|---|---|---|
| The `wsx` CLI interviews, scaffolds a vault and emits thin adapters for many surfaces | known | T1 | README "Early, but real"; waves 0–7 proved (wsx 0.3.0) | — |
| Install polish and chat-only surfaces are not ready for non-developers yet | known | T1 | README | — |
| A colleague can run `start.bat` on a PC with Cursor as the default | unknown | T5 | the pending colleague test (SESSION-STATE next action) | if the first run needs agent help to finish, fix the Path B handoff before sharing wider |

### Out of scope & later

A finished consumer app; copying personal trigger tables, employer names or tool slug tables into the
templates. Later: the fuller interview path when someone asks for it.
