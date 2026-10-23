# Memory — Index

Durable, **non-project** facts about Sean's world and the working relationship. Loaded at session start.
One line per memory. For when/how/why to write here, see [[08-workspace-contribution-framework]]
(Memory protocol); for what belongs here vs. knowledge / context / preferences, see the routing map in
[[workspace-ontology]].

Types: `fact` (durable non-project truths) · `feedback` (accumulated working guidance) ·
`reference` (external pointers) · `decision` (why a structural choice was made).
New entry: copy `_template.md`, fill it in, add a line below.

## Entries

- [[fact-workspace-repos]] — `fact` · the two workspace repos; `snds/workspace` is canonical going forward.
- [[fact-centric-ui-api-key-vs-gh-pat]] — `fact` · cloud API 401s need `VITE_API_KEY` + matching `VITE_SERVICE_NAME`, not a GH PAT (PAT is for ghcr.io).
- [[fact-machine-layer-installs]] — `fact` · per-machine install state of the bootstrap-v2 hooks/doctor layer (Personal MBP ✅ 2026-07-09; Work MBP mostly done 2026-10-14, launchd open; Windows `Enterprise` back in use, not installed).
- [[fact-intent-app]] — `fact` · Intent.app + intentd 0.9.12 on Personal MBP; `git.autoCommit` false; secrets stay off-git.
- [[fact-claude-code-sandbox-limits]] — `fact` · Claude Code's Bash sandbox on the Work MBP blocks `api.github.com` (so `gh` says "token invalid" while git works), denies `ps`, and slows git (xcrun cache); run slow harness gates outside it; the wall guard refuses PATH-swapped git and `GH_CONFIG_DIR=` overrides.
- [[fact-work-mbp-desktop-onedrive-backup]] — `fact` · on the Work MBP the Desktop is backed up to the employer's OneDrive by policy; a personal file there is expected, not a separation slip (2026-10-18).
- [[fact-unraid-server]] — `fact` · Sean's Unraid home server: how to reach it (LAN / key / sandbox) + what runs on it.
- [[fact-github-actions-billing]] — `fact` · `snds` has a payment method and an Actions budget since 2026-10-19; private-repo CI runs past the free 2,000 minutes, up to the budget; cadence per [[github-actions-private-repo-minutes]].
- [[feedback-infra-ip-disclosure]] — `feedback` · internal/LAN IPs OK to record; external/WAN IP never (the real attack surface).
- [[feedback-credential-scoping]] — `feedback` · identity (2026-10-06): every surface, Claude included, is device-based (Work MBP → Centric unless expressly overridden; Personal MBP → `snds`); conduct follows the repo remote; personal identity never on employer repos; credentials follow the repo owner through `gh_route.py` (`bin/gh`, `bin/git-credential-ws`; 2026-10-13), and no surface switches accounts by hand.
- [[feedback-visual-qa-evidence-in-prs]] — `feedback` · every visual PR (tokens/primitives/spacing/layout/colour) commits its A/B before/after/heatmap evidence into the PR and embeds a board; the reviewer judges in the PR, not by pulling the branch. Proofboard for visual work.
- [[feedback-cross-surface-token-aligned]] — `feedback` · Figma↔code token compare: prefer MATCH when refs align; use **ALIGNED** (not DEVIATE) when intent + visual match but surface form cannot (e.g. `radius/full` vs `rounded-full`); never say “no parity” when intent is shared. Canonical: [[cross-surface-token-parity]].
- [[feedback-vendor-terminology]] — `feedback` · "vendor/vendored" has two OK senses (commercial supplier + engineering: external code copied into our tree); prefer "vendored" for that engineering case; still never call *our* bespoke code vendored (copy-in/port/reuse); PLM-domain "vendor = supplier" stays. Paid-only ban struck 2026-07-30.
- [[reference-saas-plm-knowledge-discovery]] — `reference` · Centric's cross-role SaaS PLM knowledge base (`saas-plm-analysis/knowledge-discovery`); local path, its AGENTS.md/INDEX.md navigation contract, and how it relates to this workspace.
- [[decision-portable-workspace-refactor]] — `decision` · why the workspace became portable, git-native, LLM-agnostic.
- [[decision-externalize-everything-to-workspace]] — `decision` · standing directive: all durable content lives in the workspace (or the platform Projects dir), never in an agent's private memory; encoded as an AGENTS.md Core rule for cross-surface reach.
- [[decision-externals]] — `decision` · other people's repos/packages enter only as pinned externals (`09-tools/externals.py`): code in projects_root, tracked wiring from `externals.json`, reviewed plans; REA is the first; Synapse drives the same tool (2026-10-19).
- [[decision-vendor-surface-artifacts]] — `decision` · vendor Canvas/Artifact/HTML panels are not durable; write through to the vault (or emit a copy-ready path on web); Cursor `.canvas.tsx` is dual-home (2026-09-11).
- [[decision-component-pattern-framework-system]] — `decision` · why the 5-layer component & pattern context system was built (framework #09 + skill + MCP + DESIGN.md + AGENTS binding) and where its outputs live.
- [[decision-frost-ds-ai-operating-model]] — `decision` · framework #18 + `ai-design-systems` spoke: Frost/Southleft DS×AI as L1 (#18) beside #09 (2026-09-11).
- [[decision-gdrive-numbered-taxonomy]] — `decision` · My Drive top level is `01-Documents`…`12-Adult` + `99-Review`, ordered by irreplaceability; `00` reserved for Sean; moves-only, dupes staged not deleted; executed + verified 2026-10-13 (artifacts in `Projects/files-reorg`).
- [[decision-pattern-uniqueness]] — `decision` · jobs you can tell apart without domain nouns are different patterns; a parent component's usage is not a new pattern (2026-09-14).
- [[decision-pattern-candidate-detection]] — `decision` · every design system runs a detector that finds compositions repeating 3+ times across 2+ hosts and suggests them as pattern candidates; one library, one schema, reused by the DS analytics tool (2026-10-15).
- [[decision-visual-first-documentation]] — `decision` · a definition without a picture is unfinished; live components or a labeled schematic, never a text dump (2026-09-14). Method: [[visual-first-documentation]].
- [[decision-plan-ahead-order-of-operations]] — `decision` · print numbered order + first later-breaker before executing multi-step / dual-repo work; overlay ≠ Pages `main` (2026-09-11).
- [[decision-visual-qa-interrupt]] — `decision` · mint missing QA detectors and push; page Sean only if self-critique is failing or mint still cannot hit the bar (2026-09-11).
- [[decision-tool-native-adapters]] — `decision` · Thin native-filename adapters so Gemini/Copilot/Warp/Aider/Windsurf/web LLMs have a first-file path into AGENTS.md (2026-09-11).
- [[decision-workspace-automation-first-wave]] — `decision` · A1/A2/A3/A6/A7 scripts are wired into Layer 0, close-out, adapters, and CI (2026-09-11).
- [[decision-session-status-card]] — `decision` · every surface emits `session-status.py` (notices + all projects + pending); not Claude-only (2026-09-11).
- [[decision-self-improving-workspace]] — `decision` · per-session correct/heal/improve for the whole vault; P0 mechanical heals no longer wait on /optimize (2026-09-11).
- [[decision-cursor-prompt-route-hook]] — `decision` · Cursor `beforeSubmitPrompt` + shared `prompt_route.py` so employer-repo sessions load workspace doctrine (2026-09-09).
- [[decision-proto-is-design-sandbox]] — `decision` · saas-plm-prototype is the design sandbox — never strip screens because centric-ui has an equivalent (2026-08-12).
- [[feedback-expand-acronyms]] — `feedback` · expand acronyms on first use; Sean is a designer peer, not a developer audience.
- [[decision-bootstrap-v2-guarantee]] — `decision` · the workspace handshake is guaranteed by deterministic harness layers (hooks + beacon + audit + launchd doctor), not model discretion; ritual token is frozen ABI.
- [[decision-commercial-data-licensing]] — `decision` · default to commercially-licensable data/asset sources for all projects; non-commercial sources (e.g. Gaia DR3) only when uniquely needed — isolate, mark, reconcile later.
- [[decision-defer-dense-vault-retrieval]] — `decision` · defer embedding/dense Layer-2 vault retrieval until `vault-retrieve.py --eval` shows paraphrase gaps lexical cannot fix (13/13 green 2026-08-05).
- [[decision-intent-coordination-standard]] — `decision` · multi-agent work uses a living spec + `intent-run.py`; Intent.app is optional GUI.
- [[decision-apca-primary-wcag-fallback]] — `decision` · contrast by APCA first everywhere, WCAG 2.x the fallback and the conformance floor; automated gates on APCA Bronze via apca-check; apca-w3 license limits.
- [[decision-memory-tiers]] — `decision` · context in three tiers: current (read every session), recent (when asked about lately), long-term (queried with `project-recall.py`, never assumed empty); batons split by month past 12 KB with a linked `history/README.md` (2026-10-18)
- [[decision-research-network]] — `decision` · research in any field gets framework #19 + `lead-research` + field spokes + a retro into the workspace; supersedes dc-research's "no research hub"; #04 tiers stay the only confidence language; user research stays on `ux-research-synthesis` (2026-10-22)
- [[decision-design-skill-architecture]] — `decision` · one home per design subspecialty: `ds` is the only design-system hub, `ds-component-spec` (was `ux-design-systems`) under it, `design-engineer` a lens, UX duplicates of IA/dataviz/a11y folded into their specialist hubs; hubs declare `area:`; index in `skill-areas.md` (2026-10-22)
- [[decision-skill-prefixes]] — `decision` · one prefix, one domain: `ds-` always design system, data science is `dsci-`; the template for any future prefix collision (2026-10-22)
- [[decision-routing-every-domain]] — `decision` · every domain: every spoke has its own triggers (from its description's asks), every hub with spokes declares an `area`, no everyday-word triggers; measured by `sy routing test`; hub-prose-only spokes 129 → 0 (2026-10-23)
- [[decision-capture-and-assess-split]] — `decision` · MCP-gated checks split at the tool boundary: the agent captures, `figma-bind-probe.py` judges; the capture stays a labelled SKIP and exit 2 is not a pass.
- [[decision-figma-construction-gates]] — `decision` · `skillNames` does not enforce; wrap is not an exemption; hug versus a bound slot versus a literal height; leftover variants / section hug / `Docs ·` vs `Deprecated ·` (R8); per-component `--capture` is mandatory (2026-09-28).
- [[decision-indexes-are-queried-not-read]] — `decision` · every index gets a retrieval CLI (`artifact-find.py`, `skill-loadset.py`, knowledge-hints) and the token budget drops with it, so reverting to a whole-file read fails CI.
- [[decision-lint-narrow-or-not-at-all]] — `decision` · automation-layer lints stay narrow (ruff E9/F/I; evidence grades need a legend + named detector); a check that reports non-defects gets routed around.
- [[decision-shadcn-lint-independent-service]] — `decision` · `@shadcn/lint` is a product-repo DS lint service, independent of vault validators and eslint-off-system; token-tier overlay lives beside it.
- [[decision-no-unattended-runner]] — `decision` · not building the unattended Open Engine runner; the safety gate stays because /schedule, CronCreate and headless runs can reach that path anyway.
- [[decision-llm-inclusive-harness]] — `decision` · every harness change is LLM- and device-inclusive: one tool-neutral mechanism + thin surface shims + per-surface coverage rows (min Claude Code, Claude Chat, Cursor, Codex); repos keyed by remote, resolved per device (2026-09-22).
- [[decision-plain-language-is-standing]] — `decision` · plain language is a standing beacon sentence injected on every surface and every folder; the full rule stays in user preferences; employer repos do not carry a copy (2026-10-06).
- [[decision-claude-employer-surface]] — `decision` · Claude is an employer-approved surface (2026-10-06): Centric repos run under `centric-engineering` on the Work MBP; IR1 and the Claude transport block retired; personal-content, conduct and credential walls unchanged; the Claude login account is not an identity key.
- [[decision-project-intent-in-repo]] — `decision` · project intent lives in each project's repo (platform Projects dir), the vault points at it; centric-ui inherits saas-plm-prototype's intent (2026-09-22).
- [[decision-public-residual-detail]] — `decision` · gap detail follows the repo's visibility: in this public vault a known gap is written at class level with a stable ID; recipes and machine posture stay held, code and fixtures stay public (F-14, 2026-09-23).
- [[decision-one-matcher-per-workspace]] — `decision` · one Layer-0 matcher (`prompt_route.py`); every surface delegates and `evaluate-surface-trajectories.py` proves each real entry point delivers the same context.
- [[decision-reachability-is-a-detector]] — `decision` · validators prove files are well-formed; `workspace-harness.py` proves an agent can reach them and prices the traversal — reachability + token budget are CI detectors now.
- [[decision-vgpu-default-web-3d]] — `decision` · new web 3D/shader/GPU work defaults to vgpu (vgpu.sh); existing Three trees stay on the adapter; DCC unchanged.
- [[relational-context]] — `feedback` · the working-relationship texture, in the agent's voice, carried across sessions (lives at `../relational-context.md`).
