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
      "fallback_note": "Frame extraction / transcode has no portable fallback — surface the install command and stop.",
      "powers": ["reference-video-review"]
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
- **agent-browser** — powers [[web-automation]]. The CLI ships its own usage docs (`agent-browser
  skills get core`); the workspace skill is the *when/why*, the CLI is the *how*.
- **ffmpeg / yt-dlp** — power [[reference-video-review]]. ffmpeg is the hard dependency (frames);
  yt-dlp is only needed to fetch remote video.
- **inference-belt** — powers [[ai-video-generation]]. Account + cost involved; always confirm with
  the user before spending a generation call.

## Adding a capability

1. Add an entry to the JSON block above (id, kind, provides, detect, install, fallback, powers).
2. Add `requires: [<id>]` to each skill that needs it (its name must appear in `powers`).
3. Document it under "Per-capability notes".
4. Run `python3 09-tools/build-registry.py && python3 09-tools/validate-capabilities.py`.
