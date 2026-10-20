---
title: Fontface — macOS folder access (Downloads prompt) learnings
type: note
project: 25-fontface
created: 2026-10-20
source: Purchases opt-in session (branch claude/purchases-optin in the Fontface repo)
---

# Fontface: macOS folder access learnings

- macOS guards Downloads, Desktop, Documents and iCloud Drive (TCC, its privacy controls). The first read, listing or watch of one makes the system ask "would like to access files in your Downloads folder". The read waits for the answer. A "no" comes back as EPERM.
- macOS remembers the answer per app identity. An ad-hoc signed build (no Developer ID) gets a new identity every build, so each new build asks again. That's why Sean saw the prompt "every time": watching was on, and he runs new builds often.
- Fix (2026-10-20): Purchases watching is opt-in. While it's off, Fontface never looks at a watched folder. The question appears only right after the user turns watching on. A choice saved before then was dropped once.
- To test the prompt again: `tccutil reset SystemPolicyDownloadsFolder design.snds.fontface`.
- A Developer ID signature would make the answer stick across updates. Worth doing before a public release.
