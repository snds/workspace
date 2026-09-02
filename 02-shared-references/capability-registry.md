---
title: Capability Registry
spec_version: "1.0"
status: canonical
aliases: [capability-registry, capabilities]
---

# Capability Registry

The **single source of truth** for external tool dependencies (MCP servers and CLIs) that
skills can require. A skill declares `requires: [<capability-id>]` in its frontmatter; the
details of how to **detect**, **install**, and **fall back** live here — never duplicated into
the skill. See [[skill-frontmatter]] → "Capability requirements" for the field, and [[AGENTS]] +
[[08-workspace-contribution-framework]] → "Capability preflight" for the runtime protocol.

The fenced `json` block below is canonical and machine-read by `09-tools/validate-capabilities.py`.
The prose under each heading is the human mirror — keep them in sync (the validator checks that
every id in the JSON is documented and that `powers` + `route` targets are real skills).

```json
{
  "spec_version": "1.0",
  "capabilities": {
    "figma-mcp": {
      "kind": "mcp",
      "provides": "Figma Dev Mode access — read the current selection, variables/tokens, screenshots, and code-connect mappings.",
      "detect": { "method": "mcp-tool-present", "match": "mcp__*figma*__*" },
      "install": {
        "claude-code": "Enable Figma Desktop → Preferences → Enable Dev Mode MCP Server, then `claude mcp add` the local server; or `claude mcp add --transport http figma <url> --scope user`.",
        "cursor": "Cursor → Settings → MCP → add the Figma Dev Mode MCP server.",
        "generic": "Run the Figma Dev Mode MCP server and connect your MCP client to it."
      },
      "fallback": "degrade",
      "fallback_note": "Proceed without live Figma data: ask the user to paste the frame/spec or export assets, and work from those instead of the canvas.",
      "powers": ["figma-canvas-designer", "figma-design-to-code", "figma-code-connect", "figma-design-specs", "figma-diagramming", "figma-mcp-tool-usage", "figma-source-audit"]
    },
    "blender-mcp": {
      "kind": "mcp",
      "provides": "Drive Blender headlessly — author/sim geometry, bake density to VDB/3D-texture, render viewport/thumbnails — for hero 3D/VFX assets that procedural generation can't art-direct.",
      "detect": { "method": "mcp-tool-present", "match": "mcp__*Blender*__*" },
      "install": {
        "claude-code": "Run Blender with the MCP add-on (ahujasid/blender-mcp) enabled + connected, then `claude mcp add` it (see 08-knowledge/cross-domain/skill-ecosystem-and-mcp-servers).",
        "generic": "Install the Blender MCP add-on (ahujasid/blender-mcp), enable it in Blender, and connect your MCP client."
      },
      "fallback": "degrade",
      "fallback_note": "No Blender → use procedural generation (fBm/curl noise) for the volume/asset, or ask the user to supply a baked VDB/3D-texture. Procedural is the default path anyway, so this degrades cleanly.",
      "powers": ["vfx-volumetrics"]
    },
    "linear-mcp": {
      "kind": "mcp",
      "provides": "Read and write a Linear workspace — list/create issues, move statuses, apply labels, and comment. The transport for the Open Agent Engine queue, ledger, and receipts.",
      "detect": { "method": "mcp-tool-present", "match": "mcp__*linear*__*" },
      "install": {
        "claude-code": "One server per lane, user-scoped so the runner works from any directory: `claude mcp add --transport sse linear-<lane> https://mcp.linear.app/sse --scope user`, then `/mcp` to complete OAuth. Multiple Linear workspaces need SEPARATE auth contexts — Linear scopes one MCP connection to one workspace, so run each through `mcp-remote` with its own config dir: `MCP_REMOTE_CONFIG_DIR=~/.mcp-auth/linear-<lane> npx mcp-remote https://mcp.linear.app/mcp`.",
        "cursor": "User-scope `~/.cursor/mcp.json` (the doctor reads this file, not the marketplace Linear plugin). Name the server `linear-personal` and run it through mcp-remote so tokens land in the lane auth dir. Native SSE (`https://mcp.linear.app/sse`) OAuths into Cursor's store and still reports `not-authed`. Work MBP also adds `linear-c8` with its own dir; Voyager-2.local must not. Template: `00-bootstrap/templates/cursor-mcp.json.example`. Reload MCP, then complete OAuth as `hello@snds.design` (never the Centric Google account).",
        "generic": "Point any MCP client at https://mcp.linear.app/mcp (or /mcp/readonly for read-only reach) and complete the OAuth flow with the account that should read and update agent issues. One connection binds to one workspace.",
        "no-mcp": "No MCP on this surface: use the HTTP transport instead — POST https://api.linear.app/graphql with header `Authorization: <LINEAR_API_KEY from the environment>`. Equivalent capability, one extra credential to manage. See [[open-agent-engine]] → Transport."
      },
      "fallback": "degrade",
      "fallback_note": "MCP is the preferred transport, not a requirement. The engine needs only four operations (query / create / update issue, read+update comment by id), so degrade to the HTTP transport: POST https://api.linear.app/graphql with an API key READ FROM THE ENVIRONMENT (LINEAR_API_KEY). Never accept a key pasted into the conversation and never write one into a workspace file. If no key is present in the environment, say so and stop — do not ask for one. Final floor: the loop is runnable by hand in the tracker's web UI, so a surface with neither transport still has a path. Tell the user which transport is in use; a receipt written over HTTP is identical to one written over MCP.",
      "powers": ["open-agent-engine"]
    },
    "agent-browser": {
      "kind": "cli",
      "provides": "Chromium browser automation over CDP — accessibility-tree snapshots, clicks/typing, scraping JS-heavy pages.",
      "detect": { "method": "shell", "probe": "command -v agent-browser" },
      "install": { "any": "npm i -g agent-browser && agent-browser install" },
      "fallback": "degrade",
      "fallback_note": "For static pages, fall back to WebFetch/WebSearch. Interactive or JS-rendered sites (login flows, infinite scroll, SPA dashboards) genuinely need the CLI — tell the user and stop if those are required.",
      "powers": ["web-automation"]
    },
    "ffmpeg": {
      "kind": "cli",
      "provides": "Audio/video decode, frame extraction, transcode, and trimming.",
      "detect": { "method": "shell", "probe": "command -v ffmpeg" },
      "install": {
        "macos": "brew install ffmpeg",
        "linux": "sudo apt-get install -y ffmpeg",
        "windows": "winget install Gyan.FFmpeg"
      },
      "fallback": "block",
      "fallback_note": "Frame extraction / transcode has no portable fallback — surface the install command and stop. For visual-prove-engine specifically, only the `vqa motion --video` input path needs it; a pre-extracted `--frames` directory works without ffmpeg.",
      "powers": ["reference-video-review", "render-qa-toolkit", "visual-prove-engine"]
    },
    "python-imaging": {
      "kind": "cli",
      "provides": "NumPy + Pillow in the active python3 — array math and PNG decode/encode, the substrate for deterministic pixel measurement.",
      "detect": { "method": "shell", "probe": "python3 -c 'import numpy, PIL'" },
      "install": {
        "any": "python3 -m pip install numpy Pillow",
        "macos": "python3 -m pip install numpy Pillow",
        "linux": "python3 -m pip install numpy Pillow",
        "windows": "python3 -m pip install numpy Pillow"
      },
      "fallback": "block",
      "fallback_note": "Pixel measurement cannot be reproduced by narrative inspection — that substitution is the exact failure the engine exists to prevent. Surface the install command and stop; never emit an unmeasured verdict as if measured.",
      "powers": ["visual-prove-engine"]
    },
    "nvidia-flip": {
      "kind": "cli",
      "provides": "NVIDIA FLIP (flip_evaluator) — viewing-distance-aware HVS error maps for render-vs-reference.",
      "detect": { "method": "shell", "probe": "python3 -c 'import flip_evaluator'" },
      "install": { "any": "python3 -m pip install flip-evaluator" },
      "fallback": "degrade",
      "fallback_note": "vqa compare / flip_region fall back to flip-lite (CSF + HyAB + edges) and record backend: flip-lite. Never silent. SSIM+Δe remain. Do not treat flip-lite as nvidia-flip.",
      "powers": ["visual-prove-engine"]
    },
    "dreamsim": {
      "kind": "cli",
      "provides": "DreamSim mid-level perceptual distance (torch) for Spirit / novel-view / same-object questions.",
      "detect": { "method": "shell", "probe": "python3 -c 'import dreamsim, torch'" },
      "install": { "any": "python3 -m pip install dreamsim torch" },
      "fallback": "degrade",
      "fallback_note": "dreamsim_region skips if the cue is optional, else errors. Never a Literal gutter substitute. Foreground-biased: matching heroes can hide chrome diffs.",
      "powers": ["visual-prove-engine"]
    },
    "gltf-validator": {
      "kind": "cli",
      "provides": "Khronos glTF-Validator CLI for Error-level mesh/asset audit.",
      "detect": { "method": "shell", "probe": "command -v gltf-validator" },
      "install": {
        "any": "npm i -g gltf-validator",
        "macos": "npm i -g gltf-validator",
        "linux": "npm i -g gltf-validator"
      },
      "fallback": "degrade",
      "fallback_note": "vqa mesh uses the engine's stdlib glTF parser (NaN accessors, buffer overruns, illegal types) and still fail-closes on Error. Official validator is preferred when present.",
      "powers": ["visual-prove-engine"]
    },
    "tesseract": {
      "kind": "cli",
      "provides": "Tesseract OCR (CLI or pytesseract) for measuring currently attested strings.",
      "detect": { "method": "shell", "probe": "command -v tesseract" },
      "install": {
        "macos": "brew install tesseract",
        "linux": "sudo apt-get install -y tesseract-ocr",
        "windows": "winget install UB-Mannheim.TesseractOCR"
      },
      "fallback": "degrade",
      "fallback_note": "ocr_text skips if optional, else errors. Never silently pass a title/string cue. Keep attest for identity until OCR is actually run.",
      "powers": ["visual-prove-engine"]
    },
    "geometric-foundation-model": {
      "kind": "cli",
      "provides": "VGGT or DUSt3R for multi-view geometric consistency (pose/pointmap) on pinned orbits.",
      "detect": { "method": "shell", "probe": "python3 -c 'import vggt'" },
      "install": { "any": "python3 -m pip install vggt  # or the DUSt3R environment documented upstream" },
      "fallback": "degrade",
      "fallback_note": "vqa geometry still requires >=2 views and measures pairwise phase-correlation. A single still is never a 3D pass. Missing VGGT is recorded; do not invent a reconstructed mesh.",
      "powers": ["visual-prove-engine"]
    },
    "yt-dlp": {
      "kind": "cli",
      "provides": "Download video/audio from URLs for local reference review.",
      "detect": { "method": "shell", "probe": "command -v yt-dlp" },
      "install": {
        "macos": "brew install yt-dlp",
        "linux": "pipx install yt-dlp  # or: sudo apt-get install -y yt-dlp",
        "windows": "winget install yt-dlp.yt-dlp"
      },
      "fallback": "degrade",
      "fallback_note": "Only needed to fetch a remote video. If the user supplies a local file, ffmpeg alone suffices — skip yt-dlp.",
      "powers": ["reference-video-review"]
    },
    "inference-belt": {
      "kind": "cli",
      "provides": "inference.sh `belt` CLI — run 40+ hosted text/image-to-video generation models (Veo, Seedance, Wan, etc.).",
      "detect": { "method": "shell", "probe": "command -v belt" },
      "install": { "any": "Install the inference.sh CLI (https://inference.sh), then authenticate: `belt login`." },
      "fallback": "block",
      "fallback_note": "Hosted generation needs the belt CLI + an authenticated account — no local fallback. Surface the install + login steps and stop.",
      "powers": ["ai-video-generation"]
    },
    "axe-cli": {
      "kind": "cli",
      "provides": "Deque axe-core accessibility engine over a headless browser — structural WCAG violations (roles, labels, names, landmarks, order) with rule ids, impact, WCAG tags, and CSS selectors.",
      "detect": { "method": "shell", "probe": "command -v axe || npx --no-install @axe-core/cli --version" },
      "install": {
        "any": "npm i -g @axe-core/cli   # or run per-invocation: npx @axe-core/cli <url>",
        "macos": "npm i -g @axe-core/cli",
        "linux": "npm i -g @axe-core/cli",
        "windows": "npm i -g @axe-core/cli"
      },
      "fallback": "degrade",
      "fallback_note": "No axe → try pa11y, then Lighthouse's accessibility category. With no runner at all, a11y-audit-toolkit emits its MANUAL_CHECKLIST (exit 2, degraded) plus stdlib static HTML checks; findings are then human-confirmed, never reported as automated evidence.",
      "powers": ["a11y-audit-toolkit"]
    },
    "pa11y": {
      "kind": "cli",
      "provides": "pa11y accessibility runner (HTML_CodeSniffer or axe engine) — WCAG 2.x issue codes per success criterion, with selector and context, plus JSON/CI reporters.",
      "detect": { "method": "shell", "probe": "command -v pa11y || npx --no-install pa11y --version" },
      "install": {
        "any": "npm i -g pa11y   # or per-invocation: npx pa11y <url>"
      },
      "fallback": "degrade",
      "fallback_note": "Second-choice runner behind axe — its WCAG-code output is useful for conformance reporting. Absent, a11y-audit-toolkit falls through to Lighthouse, then the MANUAL_CHECKLIST degraded path.",
      "powers": ["a11y-audit-toolkit"]
    },
    "lighthouse": {
      "kind": "cli",
      "provides": "Google Lighthouse — lab audit of a URL producing a JSON report: performance metrics (LCP, TBT, CLS, SI, FCP), category scores, resource-size details, and an accessibility category backed by axe-core.",
      "detect": { "method": "shell", "probe": "command -v lighthouse || npx --no-install lighthouse --version" },
      "install": {
        "any": "npm i -g lighthouse   # CI: npm i -D @lhci/cli && npx lhci autorun"
      },
      "fallback": "degrade",
      "fallback_note": "No Lighthouse → fe-perf-harness can still assert budgets against any Lighthouse-shaped JSON produced elsewhere (LHCI runner, PageSpeed Insights API export, a hosted CI step); with no report at all it reports INCONCLUSIVE (exit 2) rather than passing. For a11y-audit-toolkit it is the third-choice runner behind axe and pa11y.",
      "powers": ["a11y-audit-toolkit", "fe-perf-harness"]
    },
    "gitleaks": {
      "kind": "cli",
      "provides": "Secret scanning over a working tree, staged changes, or full git history — provider-format and entropy rules producing findings with file, line, commit, rule id, and the matched secret's fingerprint.",
      "detect": { "method": "shell", "probe": "command -v gitleaks" },
      "install": {
        "macos": "brew install gitleaks",
        "linux": "brew install gitleaks   # or download the release binary from github.com/gitleaks/gitleaks/releases",
        "windows": "winget install gitleaks.gitleaks"
      },
      "fallback": "degrade",
      "fallback_note": "Without gitleaks, scan the diff for the high-confidence provider formats you can name (AWS key ids, private-key headers, `Bearer` literals, connection strings with inline passwords) and say the check was pattern-based. A history-wide entropy scan is not reproducible by hand, so the claim 'no secrets in history' must not be made — report the secret-scan gate as DEGRADED and name the install command.",
      "powers": ["sec-supply-chain"]
    },
    "syft": {
      "kind": "cli",
      "provides": "SBOM generation (CycloneDX or SPDX) from a built artifact — container image, directory, or archive — enumerating components with versions, licenses, and purls.",
      "detect": { "method": "shell", "probe": "command -v syft" },
      "install": {
        "macos": "brew install syft",
        "linux": "brew install syft   # or: curl -sSfL https://get.anchore.io/syft | sh -s -- -b /usr/local/bin",
        "windows": "winget install Anchore.Syft"
      },
      "fallback": "block",
      "fallback_note": "An SBOM re-read from the manifest can differ from what actually shipped, which defeats its purpose, so there is no acceptable substitute. Surface the install command and stop rather than producing a manifest-derived list and calling it an SBOM.",
      "powers": ["sec-supply-chain"]
    },
    "semgrep": {
      "kind": "cli",
      "provides": "Static analysis over source with pattern rules — injection, unsafe deserialization, missing authorization, hardcoded credentials, and framework-specific security rules, reported per finding with rule id, severity, and file/line.",
      "detect": { "method": "shell", "probe": "command -v semgrep" },
      "install": {
        "macos": "brew install semgrep",
        "linux": "pipx install semgrep   # or: python3 -m pip install semgrep",
        "windows": "pipx install semgrep"
      },
      "fallback": "degrade",
      "fallback_note": "Without semgrep there is no automated SAST path, so the `audit` verb cannot claim one. Fall back to the per-class review checklist in sec-appsec-owasp, read the enforcement point in the diff by hand, and label the result `critique` (judgment) rather than `audit` (measurement) per framework 13.",
      "powers": ["sec-appsec-owasp"]
    },
    "aio-cli": {
      "kind": "cli",
      "provides": "Adobe I/O CLI (`aio`) — Developer Console project/workspace/API management, App Builder init, action deploy/invoke, and Runtime logs.",
      "detect": { "method": "shell", "probe": "command -v aio" },
      "install": {
        "any": "npm install -g @adobe/aio-cli   # then: aio login",
        "macos": "npm install -g @adobe/aio-cli",
        "linux": "npm install -g @adobe/aio-cli",
        "windows": "npm install -g @adobe/aio-cli"
      },
      "fallback": "block",
      "fallback_note": "Every Console, init, deploy, and log path on App Builder runs through the CLI — there is no portable substitute. Surface the install + `aio login` steps and stop rather than hand-editing generated config or clicking through the Developer Console UI.",
      "powers": ["adobe-app-builder"]
    }
  }
}
```

## Detection methods

- **`mcp-tool-present`** — surface-agnostic: inspect *your own available tool list* (including
  tools reachable via tool-search/deferred loading) for a tool name matching the `match` glob.
  If one exists, the MCP is installed **and enabled** on this surface. This is how an agent on
  Claude Code, Cursor, or any MCP client checks for an MCP server without shelling out.
- **`shell`** — run the `probe` (a `command -v <bin>` test); exit 0 = present. For CLIs.
- **`env`** — (reserved) check an environment variable / credential is set.

## Fallback semantics

- **`degrade`** — proceed with reduced capability, following `fallback_note`. Tell the user what's
  degraded; don't pretend the tool ran.
- **`block`** — stop the tool-dependent step, surface the install command for the current surface,
  and ask the user to install (or proceed with an explicit manual alternative they provide).
- **`route`** — hand off to the named `fallback_skill` (a workspace skill that achieves the goal
  another way). Requires a `fallback_skill` id that resolves in the skill registry.

## Per-capability notes

- **figma-mcp** — powers the Figma Dev Mode workflow spokes: [[figma-canvas-designer]] (author on canvas),
  [[figma-design-to-code]] (design→code), [[figma-code-connect]] (component→snippet mapping),
  [[figma-design-specs]] (design→spec/PRD), [[figma-diagramming]] (Mermaid→FigJam),
  [[figma-mcp-tool-usage]] (tool selection/params), [[figma-source-audit]] (audit a library via `use_figma`).
  Already present on most Claude surfaces; degrade cleanly to paste-the-spec/export-assets when absent. The
  Figma *plugin* API spokes ([[figma-plugin-dev]], `figma-component-generation`, `figma-variable-creation`,
  etc.) run **inside Figma** and do **not** depend on this MCP — so they carry no `requires`.
- **blender-mcp** — powers [[vfx-volumetrics]] (bake hero nebula/volume assets). Optional by design: the
  procedural path is the default, so absence degrades to fBm/curl-noise generation. The many *generic*
  Blender mentions across `3d-*` / `imaging-*` skills are theory/reference (Blender as an industry DCC),
  not MCP-driving, and correctly carry no `requires`.
- **linear-mcp** — powers [[open-agent-engine]] (the queue, ledger, and receipts). **One connection = one
  Linear workspace:** per Linear's docs, "reconnecting alone does not switch the workspace within an existing
  auth session, [so] each workspace needs its own separate authentication context." That constraint is the
  feature — it makes Open Agent Engine's lane isolation structural rather than a discipline, so a runner
  authed to one lane physically cannot read another. Register user-scoped (not project-scoped) so the runner
  fires from any directory, including repos outside this workspace. A read-only endpoint
  (`/mcp/readonly`) and a `read`-only OAuth scope exist when a lane should observe without write reach.
  **`degrade`, not `block`, because MCP is a preferred transport rather than a hard dependency** — the
  engine needs four operations, and the GraphQL endpoint provides the same four to any agent with a shell
  or HTTP. The tradeoff is a credential: MCP's OAuth keeps the key out of the agent entirely, whereas the
  HTTP path needs `LINEAR_API_KEY` in the environment. Prefer MCP wherever it exists; never manufacture a
  key to avoid an install. The portability floor below both is a human running the loop in the web UI.
- **agent-browser** — powers [[web-automation]]. The CLI ships its own usage docs (`agent-browser
  skills get core`); the workspace skill is the *when/why*, the CLI is the *how*.
- **ffmpeg / yt-dlp** — power [[reference-video-review]] and [[render-qa-toolkit]] (`qa_video_extract`),
  plus [[visual-prove-engine]]'s `vqa motion --video` decode path. ffmpeg is the hard dependency
  (frames); yt-dlp is only needed to fetch remote video (reference-video-review). render-qa-toolkit
  expects a local file for extract; visual-prove-engine accepts a pre-extracted `--frames` directory
  as the no-ffmpeg path.
- **python-imaging** — powers [[visual-prove-engine]] (all probes, perception, comparison, motion,
  calibration). Blocks rather than degrades: a "measured" verdict produced without measurement is the
  self-attestation failure mode the engine replaces, so absence stops the step and surfaces
  `python3 -m pip install numpy Pillow`. SciPy/OpenCV are optional accelerators detected at runtime
  by `vqa doctor`, never required.
- **nvidia-flip** — powers [[visual-prove-engine]] `flip_region` / `vqa compare`. Degrades to flip-lite
  (numpy CSF + HyAB + edges) with an explicit `backend` field. Absence is never silent.
- **dreamsim** — powers [[visual-prove-engine]] `dreamsim_region` (Spirit / NVS). Degrades: optional cues
  skip, required cues error. Not a Literal gutter metric; foreground-biased.
- **gltf-validator** — powers [[visual-prove-engine]] `vqa mesh`. Degrades to the stdlib parser, which
  still fail-closes on NaN accessors and illegal glTF. Official validator is preferred.
- **tesseract** — powers [[visual-prove-engine]] `ocr_text`. Degrades: optional skip / required error.
  Attested strings stay attested until OCR actually runs.
- **geometric-foundation-model** — powers [[visual-prove-engine]] `vqa geometry`. Degrades to
  phase-correlation across ≥2 pinned views. A single still is not a 3D pass.
- **inference-belt** — powers [[ai-video-generation]]. Account + cost involved; always confirm with
  the user before spending a generation call.
- **axe-cli / pa11y / lighthouse** — the accessibility + performance measurement runners. `axe-cli`,
  `pa11y`, and `lighthouse` power [[a11y-audit-toolkit]], which tries them **in that preference order**
  and normalizes whichever one is present into a single finding schema; `lighthouse` additionally powers
  [[fe-perf-harness]] (Core Web Vitals / budget assertion). All three are Node CLIs, so the probe accepts
  either a global binary or a cached `npx --no-install` package — the toolkit shells out to `npx` only when
  the package is already available locally, never triggering a silent install. All degrade rather than
  block: a11y work falls through axe → pa11y → Lighthouse → MANUAL_CHECKLIST (exit 2), and budget work
  falls back to asserting against a Lighthouse-shaped JSON report produced elsewhere.
- **gitleaks / syft / semgrep** — the security measurement path behind the `audit` verb in
  [[lead-security-architect]] and the stage-3 scan gate in [[16-security-operating-model]]. `gitleaks`
  (secret scan) and `syft` (SBOM) power [[sec-supply-chain]]; `semgrep` (SAST) powers
  [[sec-appsec-owasp]]. Their fallbacks differ deliberately, because what an absent tool costs differs:
  `gitleaks` degrades to a named-pattern scan of the diff and the gate reports DEGRADED, since a
  history-wide entropy scan cannot honestly be reproduced by hand; `semgrep` degrades to the per-class
  review checklist and the result must be labelled `critique` rather than `audit`; `syft` **blocks**,
  because an SBOM re-derived from the manifest can differ from what shipped and a wrong SBOM is worse
  than a missing one. All three are surface-independent binaries, so the same probe works on any
  machine, and none of them may be reported as having run when it did not.
- **aio-cli** — powers [[adobe-app-builder]]. Node CLI, installed globally; `aio login` is a
  separate step and its session expires, so an authentication failure is not a missing install.
  Blocks rather than degrades: without it there is no way to reach the Developer Console,
  initialize a project, deploy actions, or read Runtime logs. The `appbuilder-*` plugin skills
  assume the latest CLI, which is what exposes the non-interactive Console commands.

## Adding a capability

1. Add an entry to the JSON block above (id, kind, provides, detect, install, fallback, powers).
2. Add `requires: [<id>]` to each skill that needs it (its name must appear in `powers`).
3. Document it under "Per-capability notes".
4. Run `python3 09-tools/build-registry.py && python3 09-tools/validate-capabilities.py`.
