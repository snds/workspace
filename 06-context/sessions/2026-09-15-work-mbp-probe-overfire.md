### 2026-09-15 — A8 over-fire test: a second node rebuilt the R2 discriminator

SessionID: 2026-09-15-work-mbp-probe-overfire
--- SESSION BLOCK ---
Date: 2026-09-15
Machine: Work MacBook Pro (main, going forward)
Surface: Claude Code (Mac desktop app)
Agent: Claude Opus 5
Project(s): 19-workspace-brain

Summary: Sean asked for a second node specifically to check whether R2 over-fires. It did,
immediately, and the fix is the more valuable half of A8.

The separator-based discriminator flagged `foreground` — a real single-word semantic token,
sitting among `surface/popover` and `chrome/border/subtle` with a `var(--sem-muted-foreground)`
CSS twin. Flagging it would have told a designer to bind something already bound.

Three attempts, each failing on live data the previous one had not seen: "a token has a
slash" flagged doctrine's own `space-0` / `radius-none` / `border-width-0`; "a token has a
separator" flagged `foreground`; the rule that holds is **"the key names a Figma/CSS
property"**. Token names are unbounded and system-specific; property names are a closed,
stable set. Keying on the open set was the error, and the tell was in the first node all
along — it was full of bound fills and produced no colour-valued bare key, because unbound
values only ever surface under a property name.

After the rebuild: node 2 reports 1 hit (was 2), node 1 still reports 8 (unchanged).
Precision up, detection unweakened.

R3 also gained live vocabulary: real trees use `symbol` / `instance` / `slot` / `frame` /
`text`, and a `slot` nested inside an instance must not reset instance context or every icon
vector in a composed overlay would be flagged. Pinned by self-test.

Open, stated: both nodes report a raw variable-font weight axis (`wght`) at different values
while named weight tokens exist in the file. Consistent and probably genuine — if Figma
merely echoed a resolved axis, node 2's would match its bound weight token, and it does not.
Not rounded up to certain.

Generalised into [[decision-capture-and-assess-split]]: when writing a discriminator,
enumerate the closed set, never the open one.

CONCURRENCY NOTE: a Cursor session (Grok 4.6) landed `@shadcn/lint` work in this same tree
mid-session — new routes, knowledge-hints, `_INDEX`, `09-tools/shadcn-lint/`, and a baton
rewrite. Its `shadcn-lint-service` routing fixture is currently RED and `trigger-routes.md`
has drift; both belong to that in-flight work, not to this. This commit deliberately contains
only the probe files, so their work is left untouched in the tree for them to finish. I
corrected one stale line in their baton rewrite (it still said the probe had only seen
synthetic fixtures).
--- END BLOCK ---
