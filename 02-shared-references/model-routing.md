---
title: Model Routing Guide
spec_version: "1.0"
status: canonical
aliases: [model-routing, model-selection, agent-model-map]
related:
  - capability-registry
  - workspace-ontology
  - trigger-routes
---

# Model Routing Guide

**Single source of truth** for which model to use on which agent surface for which work context.
Every surface selects from its own native model roster first. Third-party models (e.g. Claude in
Cursor) are noted where available but are not the default. Each entry includes effort tier and
speed signal where known.

Load this file when: selecting a model for a new task; onboarding a new agent surface; a task
changes context mid-session (e.g. switching from spec writing to code generation).

---

## Surfaces

- [Ollama (local)](#ollama-local)
- [Claude (claude.ai / Claude Code / Claude Desktop)](#claude)
- [Cursor](#cursor)
- [Codex (OpenAI)](#codex-openai)

---

## Effort tiers (universal)

| Tier | Label | Use when |
|------|-------|----------|
| 1 | **Quick** | Fast lookups, single-turn drafts, yes/no decisions, refactors with clear spec |
| 2 | **Standard** | Most work: component specs, token architecture, code review, doc writing |
| 3 | **Deep** | Multi-step reasoning, ambiguous briefs, tradeoff analysis, hard debugging |
| 4 | **Extended** | Long-running agents, full audit passes, multi-file refactors, research sweeps |

---

## Ollama (local)

Native roster: open-weight models pulled locally. No API cost. Privacy-complete.
Hardware: M3 Max, 36 GB unified memory. Run `ollama ps` to verify GPU residency.

```json
{
  "surface": "ollama",
  "native_first": true,
  "hardware": "M3 Max · 36 GB unified memory · Metal GPU",
  "runtime_note": "Prefer -mlx tagged variants where available. Verify PROCESSOR=GPU via `ollama ps`.",
  "models": {
    "gemma4": {
      "tag": "ollama run gemma4",
      "size_gb": 7.7,
      "fit": "comfortable",
      "context_k": 256,
      "speed": "fast",
      "effort_tiers": [1, 2],
      "strengths": ["structured prose", "spec writing", "long-context review", "multimodal input"],
      "weak_at": ["complex multi-step code", "deep reasoning chains"]
    },
    "gemma4:27b": {
      "tag": "ollama run gemma4:27b",
      "size_gb": 18,
      "fit": "comfortable",
      "context_k": 256,
      "speed": "moderate",
      "effort_tiers": [2, 3],
      "strengths": ["documentation", "component anatomy", "design critique", "long-context audit"],
      "weak_at": ["bleeding-edge TypeScript patterns"]
    },
    "qwen3.5:27b": {
      "tag": "ollama run qwen3.5:27b",
      "size_gb": 20,
      "fit": "comfortable",
      "context_k": 256,
      "speed": "moderate",
      "effort_tiers": [2, 3],
      "strengths": ["React/TS/Vue code", "token pipeline scripts", "tone-sensitive comms", "instruction-following"],
      "weak_at": ["visual/creative direction"]
    },
    "qwen3.6:35b-moe": {
      "tag": "ollama run qwen3.6:35b",
      "size_gb": 22,
      "fit": "tight",
      "context_k": 256,
      "speed": "fast (MoE — only 3B active params)",
      "effort_tiers": [2, 3],
      "strengths": ["agentic coding", "Figma plugin TS", "FontTools scripting", "high quality-per-watt"],
      "weak_at": ["creative narrative"],
      "note": "Close other apps before loading. Best speed/quality ratio in the local roster."
    },
    "qwen3:32b": {
      "tag": "ollama run qwen3:32b",
      "size_gb": 20,
      "fit": "tight",
      "context_k": 128,
      "speed": "slow",
      "effort_tiers": [3, 4],
      "strengths": ["hard reasoning", "tradeoff analysis", "architecture decisions", "thinking mode on"],
      "weak_at": ["speed-sensitive tasks"],
      "note": "Enable thinking mode for tier-3/4 work. Best local reasoning ceiling. Close other apps."
    }
  }
}
```


### Ollama — Work context → model map

| Work context | Model | Effort | Notes |
|---|---|---|---|
| Quick drafts, fast lookups | `gemma4` (default) | 1 | Leave other apps open |
| Spec writing, component anatomy docs | `gemma4:27b` | 2 | Strong structured prose |
| Token system design, DS strategy | `qwen3:32b` | 3 | Thinking mode on |
| React/TS/Vue component code | `qwen3.5:27b` | 2 | Coding standout |
| Figma plugin TypeScript | `qwen3.6:35b-moe` | 2–3 | Fastest at code |
| FontTools / pipeline scripting | `qwen3:32b` | 3 | Thinking mode on |
| Architecture / tradeoff decisions | `qwen3:32b` | 3–4 | Thinking mode on |
| Long-context audit (multi-file review) | `gemma4:27b` | 2–3 | 256K context |
| Tone-sensitive comms (HR, stakeholder) | `qwen3.5:27b` | 2 | Best register control |
| Legion game design / creative writing | `gemma4:27b` or `qwen3.5:27b` | 2 | Try both; personal preference |
| Data table audit, large spec review | `gemma4:27b` | 2–3 | Long context wins here |

---

## Claude

Surfaces: claude.ai (web/mobile), Claude Desktop, Claude Code.
Native roster: Anthropic models. These are the primary models — use them first on this surface.

```json
{
  "surface": "claude",
  "native_first": true,
  "models": {
    "claude-sonnet-4-6": {
      "label": "Claude Sonnet 4.6",
      "tier": "standard",
      "speed": "fast",
      "effort_tiers": [1, 2, 3],
      "strengths": ["balanced quality/speed", "design system work", "spec writing", "code review", "most daily tasks"],
      "note": "Default for most work on this surface."
    },
    "claude-opus-4-6": {
      "label": "Claude Opus 4.6",
      "tier": "premium",
      "speed": "slower",
      "effort_tiers": [3, 4],
      "strengths": ["complex reasoning", "nuanced tradeoff analysis", "ambiguous briefs", "extended agent tasks"],
      "note": "Reserve for tier-3/4 tasks. Costs more — don't use for quick drafts."
    },
    "claude-sonnet-5": {
      "label": "Claude Sonnet 5",
      "tier": "standard-next",
      "speed": "fast",
      "effort_tiers": [1, 2, 3],
      "strengths": ["latest capabilities", "strong at code and reasoning"],
      "note": "Available via API. Use when latest model matters."
    },
    "claude-opus-5": {
      "label": "Claude Opus 5",
      "tier": "premium-next",
      "speed": "slower",
      "effort_tiers": [3, 4],
      "strengths": ["highest reasoning ceiling", "extended agentic tasks"],
      "note": "Available via API. Reserve for the hardest problems."
    }
  }
}
```


### Claude — Work context → model map

| Work context | Model | Effort | Notes |
|---|---|---|---|
| Quick drafts, lookups, refactors | Sonnet 4.6 | 1 | Default |
| Spec writing, component docs | Sonnet 4.6 | 2 | Strong structured output |
| Token system / DS strategy | Sonnet 4.6 or Opus 4.6 | 2–3 | Opus for ambiguous briefs |
| React/TS/Vue component code | Sonnet 4.6 | 2 | Reliable at this |
| Figma plugin TypeScript | Sonnet 4.6 | 2–3 | |
| Architecture / hard tradeoffs | Opus 4.6 | 3–4 | Extended thinking if available |
| Long-context audit | Sonnet 4.6 | 2–3 | Large context window |
| Tone-sensitive comms | Sonnet 4.6 | 2 | Good register control |
| Legion game design | Sonnet 4.6 | 2 | Loads full skill set via trigger |
| Extended agentic tasks (Claude Code) | Opus 4.6 or Opus 5 | 4 | Multi-file, long-running |
| Workspace bootstrap / skill loading | Sonnet 4.6 | 1 | Fast, low cost |

---

## Cursor

Native roster: Cursor's built-in models (GPT-4o, Grok, Gemini). Claude is available
but consumes the monthly stipend — prefer it only when Claude's specific strengths are
required and the task justifies the cost.

```json
{
  "surface": "cursor",
  "native_first": true,
  "stipend_note": "Claude in Cursor draws from a monthly token budget. Grok is the cost-efficient default for most coding tasks.",
  "models": {
    "grok-3": {
      "label": "Grok 3",
      "native": true,
      "speed": "fast",
      "effort_tiers": [1, 2, 3],
      "strengths": ["code generation", "refactoring", "inline edits", "TypeScript", "React"],
      "note": "Primary default for all coding work in Cursor. Cost-efficient."
    },
    "grok-3-mini": {
      "label": "Grok 3 Mini",
      "native": true,
      "speed": "very fast",
      "effort_tiers": [1],
      "strengths": ["quick completions", "autocomplete", "small refactors"],
      "note": "Use for high-frequency tab completions. Saves budget for harder tasks."
    },
    "gpt-4o": {
      "label": "GPT-4o",
      "native": true,
      "speed": "fast",
      "effort_tiers": [1, 2],
      "strengths": ["general coding", "balanced quality/speed"],
      "note": "Fallback when Grok underperforms on a specific pattern."
    },
    "claude-sonnet": {
      "label": "Claude Sonnet (via Cursor)",
      "native": false,
      "speed": "fast",
      "effort_tiers": [2, 3],
      "stipend_cost": "medium",
      "strengths": ["nuanced spec review", "DS strategy reasoning", "tone-sensitive output", "workspace-aware tasks"],
      "note": "Use when task requires Claude's specific strengths (reasoning, comms, DS work). Not for routine code gen."
    },
    "claude-opus": {
      "label": "Claude Opus (via Cursor)",
      "native": false,
      "speed": "slower",
      "effort_tiers": [3, 4],
      "stipend_cost": "high",
      "strengths": ["complex multi-file reasoning", "architecture decisions"],
      "note": "High stipend cost. Reserve for genuinely hard problems only."
    }
  }
}
```


### Cursor — Work context → model map

| Work context | Model | Effort | Stipend cost |
|---|---|---|---|
| Tab completion, autocomplete | Grok 3 Mini | 1 | None |
| Component code, inline refactors | Grok 3 | 1–2 | None |
| React/TS/Vue feature work | Grok 3 | 2 | None |
| Figma plugin TypeScript | Grok 3 | 2–3 | None |
| FontTools / pipeline scripts | Grok 3 | 2–3 | None |
| Multi-file refactor | Grok 3 | 3 | None |
| Spec writing in-editor | Grok 3 | 2 | None |
| DS strategy / token architecture | Claude Sonnet | 3 | Medium — justify first |
| Tone-sensitive comms drafted in editor | Claude Sonnet | 2 | Medium |
| Hard architecture decisions | Claude Opus | 4 | High — use sparingly |
| Workspace-aware reasoning | Claude Sonnet | 2–3 | Medium |

---

## Codex (OpenAI)

Surface: OpenAI Codex / o-series (CLI agent, API, or ChatGPT with code interpreter).
Native roster: o3, o4-mini, GPT-4o. These are the primary models on this surface.

```json
{
  "surface": "codex",
  "native_first": true,
  "models": {
    "o4-mini": {
      "label": "o4-mini",
      "speed": "fast",
      "effort_tiers": [1, 2, 3],
      "strengths": ["coding tasks", "TypeScript", "React", "cost-efficient reasoning", "agentic coding loops"],
      "note": "Default for most Codex work. Strong coding, fast, lower cost than o3."
    },
    "o3": {
      "label": "o3",
      "speed": "slower",
      "effort_tiers": [3, 4],
      "strengths": ["hard reasoning", "complex multi-step problems", "highest reasoning ceiling on this surface"],
      "note": "Reserve for tier-3/4 tasks. More expensive — don't use for routine coding."
    },
    "gpt-4o": {
      "label": "GPT-4o",
      "speed": "fast",
      "effort_tiers": [1, 2],
      "strengths": ["general tasks", "balanced quality/speed", "multimodal input"],
      "note": "Good fallback for non-reasoning-heavy tasks. Multimodal if you need vision."
    },
    "o3-mini": {
      "label": "o3-mini",
      "speed": "very fast",
      "effort_tiers": [1],
      "strengths": ["quick completions", "lightweight reasoning"],
      "note": "High-frequency use only. Not for complex multi-step work."
    }
  }
}
```

### Codex — Work context → model map

| Work context | Model | Effort | Notes |
|---|---|---|---|
| Quick completions, snippets | o3-mini | 1 | Cost-efficient |
| Component code, TypeScript | o4-mini | 1–2 | Default |
| React/Vue feature work | o4-mini | 2 | Strong coder |
| Figma plugin TypeScript | o4-mini | 2–3 | |
| FontTools / pipeline scripts | o4-mini | 2–3 | |
| Agentic coding loops | o4-mini | 3–4 | Good at multi-step loops |
| Hard reasoning, architecture | o3 | 3–4 | Reserve for genuinely hard problems |
| Multimodal input (screenshot → code) | GPT-4o | 2 | Vision capable |
| Multi-file refactor | o4-mini or o3 | 3 | o3 for ambiguous scope |


---

## Cross-surface routing cheatsheet

For any task, resolve in this order:
1. Which surface am I on?
2. What is the work context?
3. What effort tier does this task need?
4. Pick the native model for that tier — avoid non-native unless there's a specific reason.

| Work context | Ollama | Claude | Cursor | Codex |
|---|---|---|---|---|
| Quick draft / lookup | gemma4 | Sonnet 4.6 | Grok 3 Mini | o3-mini |
| Spec / doc writing | gemma4:27b | Sonnet 4.6 | Grok 3 | o4-mini |
| Component code | qwen3.5:27b | Sonnet 4.6 | Grok 3 | o4-mini |
| Figma plugin TS | qwen3.6:35b-moe | Sonnet 4.6 | Grok 3 | o4-mini |
| FontTools / pipelines | qwen3:32b | Sonnet 4.6 | Grok 3 | o4-mini |
| Token / DS strategy | qwen3:32b | Opus 4.6 | Claude Sonnet* | o3 |
| Architecture / tradeoffs | qwen3:32b | Opus 4.6 | Claude Opus* | o3 |
| Long-context audit | gemma4:27b | Sonnet 4.6 | Grok 3 | o4-mini |
| Tone-sensitive comms | qwen3.5:27b | Sonnet 4.6 | Claude Sonnet* | o4-mini |
| Agentic / multi-file | qwen3:32b | Opus 4.6 / Opus 5 | Grok 3 | o4-mini / o3 |
| Legion creative | gemma4:27b | Sonnet 4.6 | Grok 3 | GPT-4o |

*Cursor: Claude draws from monthly stipend — confirm task justifies cost before selecting.

---

## Agent loading instruction

Any agent entering this workspace should load this file when:
- The user says "pick the best model for this" or similar
- A task context switch occurs mid-session
- A new surface or tool is being initialized
- The bootstrap sequence reaches the model-selection step

This file does not auto-load at boot — it is demand-loaded when model selection is relevant.
Register it as a trigger route if model selection becomes a frequent session-start action.

## Related

- [[capability-registry]] — external tool dependencies by surface
- [[workspace-ontology]] — routing map for all workspace content
- [[trigger-routes]] — curated trigger → skill/reference load hints
- [[AGENTS]] — universal agent contract and surface adapter model

## Changelog

- 2026-09-03 v1.0 — Initial. Covers Ollama (local), Claude, Cursor, Codex.
  Authored by Claude Sonnet 4.6 / claude.ai / Voyager-2.local.
