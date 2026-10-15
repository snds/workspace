---
title: Unicron
type: project
status: Active
triggers: [unicron, shared design system, dsa, design system analytics, pattern candidate, pattern detection, ds ratchet]
frameworks: [component-pattern, design-systems-ai, qa-operating-model, engineering-operating-model, domain-rigor-stack]
related_projects: [24-mailbird, 26-synapse, 28-lockdown]
---

# Unicron (29-unicron)

_Working name. No trademark check yet._

The one shared design system for Mailbird, Synapse, and Lockdown (Lockdown D14). Mailbird's stack is the base: React 19, Vite 8, Tailwind v4, shadcn/ui (Base UI, Nova), Material Symbols, three-tier tokens. Synapse rebuilds onto it; Lockdown starts from it.

Its sibling is **DSA**, the design-system analytics library: pattern-candidate detection, adoption and correct-use metrics, and a CI ratchet. DSA is where every design-system detection, analysis, and analytics piece lives, so other systems (including an employer system later) can consume it as a dependency without the tool ever holding their data.

- **Status:** scaffolding started 2026-10-15.
- **Context profile:** `personal-solo`. Both repos are **public**.
- **Repos:** `~/Projects/unicron` (`snds/unicron`) and `~/Projects/dsa` (`snds/dsa`).
- **This folder:** baton and pointers only. Docs live in the repos.
- **Baton:** [[07-projects/29-unicron/SESSION-STATE|SESSION-STATE]].

## Standing rules that apply

- [[decision-pattern-candidate-detection]] — every design system runs the detector; DSA is the reference implementation.
- [[decision-pattern-uniqueness]] — how a candidate is judged (pattern, variant, snowflake).
- Framework 09 §7 and §7a — composition model and the pattern catalog.
- Token doctrine: three tiers (global → semantic → component), [[token-architecture]].

## Walls

- No employer names, tokens, paths, data, or code in either repo. The rule crosses the wall; the data never does.
- The employer's own analytics plan stays machine-local on the Work MBP (see 12-MCS). DSA is a clean-room build from the vault's vendor-neutral knowledge.
