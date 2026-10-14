# Figma AI Agent — Phase 1

An AI-powered design agent embedded directly in Figma. Talk to Claude, it acts on the scene graph.

## Quick start (no terminal needed)

The `dist/` folder is pre-built. You can load the plugin immediately:

1. Open Figma Desktop
2. Menu → Plugins → Development → Import plugin from manifest…
3. Select the `manifest.json` file in this folder
4. The plugin opens — go to **Settings** (gear icon) and add your Anthropic API key
5. Start designing

---

## What Phase 1 can do

- **Create**: frames, text, shapes, components, pages, groups
- **Modify**: fills, strokes, auto layout, resize, move, rename, opacity, corner radius, visibility, layer order
- **Read**: page context, selection details, node properties, find nodes, list pages
- **Navigate**: go to page, scroll to node
- **Selection context**: automatically injects the currently selected node(s) into every prompt — Claude always knows what you're pointing at

## How to use

1. Select something in Figma (optional — gives Claude context about what you're working with)
2. Type a prompt: *"Create a card component 320×200 with a white background and 16px corner radius"*
3. Watch Claude plan and execute tool calls in the chat
4. The **Context** tab shows live selection properties
5. The **Log** tab records every tool call with full input/output

## Settings

| Setting | Notes |
|---------|-------|
| Anthropic API Key | Required. Stored in Figma clientStorage (local only, never synced). |
| Figma PAT | Optional in Phase 1. Required for cross-file context in Phase 3+. |
| Model | Claude Sonnet 4.5 recommended. Haiku for fast/cheap iteration. |
| Max tokens | 4096 default. Increase for complex multi-step tasks. |
| Auto-context | On by default. Injects selection into every message. |

## Keyboard shortcuts

- **⌘↵** (or **Ctrl+↵**) — Send prompt
- Click any tool call card to expand input/output details

## Rebuild from source

```bash
npm install
npm run build        # One-time build
npm run watch        # Watch mode for development
```

Requires Node.js 18+.

## Phase roadmap

| Phase | Status | What it adds |
|-------|--------|-------------|
| **1 — Core Agent Loop** | ✅ This build | Agent loop, 26 tools, selection context, chat UI |
| 2 — Library Intelligence | Planned | Library index, component import, variable binding, DS-first enforcement |
| 3 — Screenshot & Vision | Planned | screenshot-to-design, cross-file REST reads |
| 4 — Claude Chat Relay | Planned | Prompt from Claude.ai → executes in Figma |

## File structure

```
figma-ai-agent/
  manifest.json         Plugin manifest
  package.json
  build.js              esbuild build script
  dist/
    code.js             Compiled plugin sandbox (load this)
    ui.html             Plugin panel UI
  src/
    code.ts             Plugin sandbox entry point
    ui.html             Chat UI source
    types.ts            Shared TypeScript interfaces
    context.ts          Selection serializer
    tools/
      read.ts           Read tools
      create.ts         Create tools
      modify.ts         Modify tools
      navigation.ts     Navigation tools
```
