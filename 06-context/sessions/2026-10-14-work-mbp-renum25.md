### 2026-10-14 — Fontface renumbered 24 → 25; its baton now syncs through git

SessionID: 2026-10-14-work-mbp-renum25
--- SESSION BLOCK ---
Date: 2026-10-14
Machine: Work MacBook Pro
Surface: Claude Code (desktop) · side session of the GitHub-route landing session
Agent: Claude Opus 5.5
Project(s): 25-fontface, 24-mailbird (index only)
Summary: Two projects held number 24. Mailbird (2026-10-13) was already on GitHub; Fontface
(2026-10-12) was older but had never been committed, because `.gitignore` had no allow-entry for
its folder. Sean chose: Mailbird keeps 24, Fontface moves to 25 (same rule as 22: whoever reaches
GitHub first keeps the number), and Fontface's baton is now tracked like 21–24. The folder was
untracked, so it moved with a plain `mv`, not `git mv`; Mailbird did not change at all.
Decisions: project numbers go to whoever reaches origin first (now applied twice: 22, 25).
Changed: 07-projects/25-fontface/{README,SESSION-STATE}.md (renamed from 24-fontface, now tracked),
.gitignore (allow-entry), _PROJECTS.md, 06-context/project-registry.md, 06-context/project-context.md.
Verification: no `24-fontface` references remain except the history note. validate-integrity went
from 3 errors (the untracked Fontface links) to 0. nightly rebuild wrote 0 files.
Incident: a sibling session's accidental `git reset --hard` at 07:37 PDT wiped the three index
edits. The Fontface files and .gitignore were restored by that session; the three index edits were
rebuilt from this session's transcript (the staged Fontface lines plus the 25 renumber). Nothing lost.
Pending: none for the renumber.
--- END BLOCK ---
