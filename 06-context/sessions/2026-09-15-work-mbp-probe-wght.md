### 2026-09-15 — A8 third node: R2's premise demonstrated, `wght` settled as a true positive

SessionID: 2026-09-15-work-mbp-probe-wght
--- SESSION BLOCK ---
Date: 2026-09-15
Machine: Work MacBook Pro (main, going forward)
Surface: Claude Code (Mac desktop app)
Agent: Claude Opus 5
Project(s): 19-workspace-brain

Summary: Third live node, probed to settle whether the raw variable-font weight axis (`wght`)
was a true positive or an artifact of Figma echoing a resolved axis. Settled: true positive,
and the same data proves R2's underlying premise.

The decisive evidence is a natural experiment, not an argument. A 15px focus-ring radius
appears in node 1 as the BARE property `radiusRing: 15`, with no focus-ring token anywhere in
that node's map; it appears in node 3 as the TOKEN `focus-ring-radius/md: 15`, with no bare
key. One concept, one value, two nodes — bare where unbound, token where bound. If bare keys
were echoes of bound properties, node 3 would show both; it shows one. So a bare key can be
trusted to mean unbound, which is the assumption R2 rests on and had not previously been
tested.

Applied to `wght`: node 1 reports 400 while its only weight token is `font-weight/medium: 500`;
node 2 reports 461 against tokens 500 and 600. Neither value exists as a token in its own map,
so neither can be an echo. Node 3 reports 400 alongside `font-weight/normal: 400`, which is
coincidence — 400 is Regular. Likely cause worth naming: the `ligature/*` entries show this
file uses variable ICON fonts, which carry their own `wght` axis; `var(--icon-size)` is bound
and the icon weight axis is not, which also explains node 2's otherwise odd 461.

Also confirmed on node 3: the rebuilt property-name discriminator holds — `foreground` passes,
and the Figma-only construction tokens (`Day/top-left` and siblings, sanctioned by doctrine
rule 0) pass as tokens. No metadata was supplied for this node and the probe correctly
reported `verified: R1, R2` only, declining to claim R3 rather than implying a clean tree.

Three nodes now: node 1 eight R2 hits, node 2 one, node 3 five. R1 clean on all three — the
hard gate has not over-fired once on real production work.

CONCURRENCY: the Cursor `@shadcn/lint` work is still in-flight and uncommitted in this tree,
with its routing fixture red and `trigger-routes.md` drifted. This commit again contains only
the probe files.
--- END BLOCK ---
