### 2026-10-13 — Walls: one GitHub route for every surface; file edits are their own class

SessionID: 2026-10-14-work-mbp-ghroute
--- SESSION BLOCK ---
Date: 2026-10-13 (landed 2026-10-14)
Machine: Work MacBook Pro
Surface: Claude Code (desktop) · session cb042892-48fa-4e0e-864c-1fec1fe4e8fd
Agent: Claude Opus 5.5
Project(s): 19-workspace-brain (walls)
Summary: Sean was blocked switching GitHub accounts, fighting the gates, and unable to comment,
open issues or merge. Diagnosis: six stacked gate layers. Claude's gh knew only `snds`; gh cannot
verify TLS or read the keychain inside Claude Code's sandbox; P31 denied plain file edits on an
employer default branch; the auto-mode profile named ~/fontface as the only trusted repo; and
GitHub never lets Sean approve his own PRs, which Claude opens as him. Built (Sean chose "Build all
four", merge after a GitHub rule change): 09-tools/gh_route.py (pinned) routes every GitHub login by
repo owner for git (bin/git-credential-ws) and gh (bin/gh, linked as ~/.local/bin/gh); overlay v6;
the lanes include carries the route and sends routed owners' SSH forms over HTTPS; file writes are
class `edit` (never branch-checked); commit and push on default stay denied. Merged origin/main and
pushed main (7 stuck local commits went up).
Decisions: decision-claude-employer-surface amendment 2026-10-13. The employer insteadOf lives only in
the lanes include, not the tracked overlay (H25 employer-substance). No admin-override merges.
Changed: 09-tools/{gh_route,git_lanes,wall_guard,profile_resolve,pr-desk,test-validators}.py,
00-bootstrap/doctor/{pin_lib,installers,render_shims}.py, 00-bootstrap/dist/{gh,git-credential-ws,
claude-overlay.env,git/lanes/ws-lanes.inc}, devices.json, surfaces.json, action-policy.json (+fixture),
fixtures (wall_guard, git_lanes, identity), .gitignore, the decision note.
Verification: pin checks 7/7 (profile_resolve 406/406 outside the sandbox), installers 72/72,
git_lanes 67/67, render_shims 67/67, affected test-validators classes green, ruff clean,
employer-substance clean. Harness red only on pre-existing items (evidence-grades census from the
mechanization review) and sandbox-environment timeouts (nightly 74/74 outside the sandbox).
Pending: Sean runs --install-pin, --install-git-hooks, --install-claude-overlay (in that order) and
starts a fresh session; updates the auto-mode profile and /sandbox (gh, git) himself; changes GitHub
rules on the two merge-list repos. Then ^pc-09 and ^pc-50 can close after one real Centric push.
Incident: a stray `git reset` during landing unstaged other sessions' work on main; restored exactly
from the landing stash's index tree (no content lost). Two projects share number 24 (mailbird, fontface).
--- END BLOCK ---
