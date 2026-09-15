### 2026-09-15 — A8 live validation: real MCP output corrected the probe twice

SessionID: 2026-09-15-work-mbp-figma-probe-live
--- SESSION BLOCK ---
Date: 2026-09-15
Machine: Work MacBook Pro (main, going forward)
Surface: Claude Code (Mac desktop app)
Agent: Claude Opus 5
Project(s): 19-workspace-brain

Summary: Closed the gap left by the A8 fragment earlier today — Sean supplied a node URL and
`figma-bind-probe.py` was fed real MCP output for the first time. It ran end to end and
corrected the capture contract in two places that fixtures could never have caught.

(1) `get_metadata` returns `<frame …><symbol …/></frame>`: types are element TAGS and there
is NO paint attribute at all. The original R3-from-metadata path required a node to be
"painted", so it could never fire on real output — and a self-test asserted it worked, using
an invented `type="RECTANGLE" fill="#fff"` shape Figma does not emit. R3 now judges a raw
shape by tree position: top-level chrome fails, the same shape inside an instance is that
component's own internals (icon vectors) and is left alone.

(2) `get_variable_defs` returns a MIXED map — token paths, `var(--x)` references, and bare
property names whose values are the resolved literals of UNBOUND properties. That third kind
is precisely what R2 exists to refuse and it is visible nowhere else; the probe was not
reading the map for R2 at all. Before the fix it would have reported "R1 and R3 verified, 0
violations" on a component carrying eight unbound properties — a false pass, the worst
outcome for a prove-gate. A follow-on fragility surfaced while fixing it: "a token has a
slash" would have flagged doctrine's own hyphenated spellings (`space-0`, `radius-none`,
`border-width-0`), so the discriminator is now "a token has a separator", pinned in both
directions by self-test.

Findings on the live node: R1 clean — no `Color/*` primitives anywhere, which is the evidence
that the hard gate does not over-fire on real production work. R3 clean — every child is a
variant symbol. R2 found eight unbound properties spanning height, padding, gap, radius,
focus-ring radius, font size, line height and weight: exactly the families the Density
standing rule names, on a control, while tokens for those families exist in the same file.
Reported to Sean in session; the capture stayed in the scratchpad.

Also corrected a rule I had written wrong earlier in the day: I justified scratchpad-only
captures as wall 3 ("employer content must not be committed here"). Wall 3 is
one-directional — nothing personal into employer repos — and employer design data is tracked
in this vault by design (CDS file key, token names and hex values already live across
02-centricPLM, 09-figma-repo-sync-plugin, project-context-detail and the log archive). Fixed
in the probe docstring, its --emit-template help, figma hub step 7, the close-out SKIP text,
the decision memo and the report. A wrong rule written into a skill surface gets followed
later, so it was worth the pass.

Generalisable lesson, recorded in [[decision-capture-and-assess-split]]: a detector built
only against fixtures of your own design tests your imagination, not the tool.

22 harness gates green, 43/43 negative fixtures, ruff clean.

Report: `07-projects/19-workspace-brain/reports/figma-bind-probe_v1.0_2026-09-15.md`
--- END BLOCK ---
