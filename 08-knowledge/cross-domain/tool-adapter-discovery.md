---
tags: [workspace, harness, adapters, AGENTS.md, Copilot, Gemini, Warp]
created: 2026-09-11
updated: 2026-09-11
status: working
confidence: high
sources: [https://agents.md/, AGENTS.md, 00-bootstrap/SURFACES.md]
related_skills: [harness-map, workspace-bootstrap, self-improve]
related_projects: [19-workspace-brain]
relations:
  builds-on: ["[[agent-load-miss-review]]", "[[workspace-infrastructure]]"]
  relates-to: ["[[cursor-employer-repo-skill-routing]]"]
---

# Tool-native adapter discovery

## For future agent

- **TL;DR:** `AGENTS.md` is the contract. Many tools still auto-load a *different* filename first (`GEMINI.md`, `.github/copilot-instructions.md`, `WARP.md`, Windsurf rules, Aider `CONVENTIONS.md`). Those files are **thin pointers** (read AGENTS.md, lookup `load_chains`, close-out). Never symlink the full contract onto those names — some tools concatenate every instruction file they find. Never add `.cursorrules` / `.windsurfrules` / `.clinerules`: several IDEs first-match those and then skip `AGENTS.md`.
- **As of:** 2026-09-11 · **Status:** current
- **Audience:** `for: agent`

## What actually auto-loads (2026)

| Tool | Native file | What we ship |
|---|---|---|
| Codex, Cursor, Copilot coding agent, Jules, Amp, many others | `AGENTS.md` | Canonical contract |
| Claude Code | `CLAUDE.md` (`@AGENTS.md` import) | Existing adapter + import |
| Cursor (always-on) | `.cursor/rules/brain.mdc` | Existing |
| Gemini CLI | `GEMINI.md`; optional `context.fileName` | Thin `GEMINI.md` + `.gemini/settings.json` → `AGENTS.md` |
| GitHub Copilot Chat (VS Code) | `.github/copilot-instructions.md` | Thin pointer |
| Warp | `WARP.md` | Thin pointer |
| Aider | `CONVENTIONS.md` + `.aider.conf.yml` `read:` | Thin root `CONVENTIONS.md` (PR conventions stay in `.github/CONVENTIONS.md`) |
| Windsurf Cascade | `.windsurf/rules/` | Thin always-on rule. **No** `.windsurfrules` |
| Perplexity with files | `PERPLEXITY.md` | Existing thin adapter |
| ChatGPT / Grok.com / Perplexity without FS | nothing | Paste `00-bootstrap/adapters/web-session.md` + BEACON |

## Rules for a new adapter

Onboard from `00-bootstrap/adapters/_ADAPTER-TEMPLATE.md`. Allowlist the filename in `.gitignore`. Keep it under the validator cap. Must mention `AGENTS.md` and `close-out`. Do not duplicate folder semantics or write-quality gates.

Injection (Cursor/Claude hooks) is still not compliance. A web LLM that never receives the paste pack cannot follow the vault.
