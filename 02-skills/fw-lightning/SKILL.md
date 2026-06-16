---
name: fw-lightning
description: >
  Salesforce Lightning Design System (SLDS) — design tokens, component blueprints,
  agentic UI patterns, and enterprise design language. Use this skill whenever the
  conversation involves Lightning Design System, SLDS tokens, SLDS component blueprints,
  Lightning Web Components (LWC), or analyzing/referencing SLDS as a design system
  exemplar. Also trigger when discussing agentic design patterns (SLDS 2), Salesforce
  platform UI, or when the target stack uses Lightning. If the user mentions "SLDS",
  "Lightning", "Salesforce design system", or "LWC" — use this skill.
pinned_version: "SLDS 2 (2.29.0)"
pinned_date: "2026-03-26"
changelog_url: "https://www.lightningdesignsystem.com/release-notes/"
aliases: [fw-lightning]
tier: spoke
domain: engineering
hub: lead-frontend-engineer
prerequisites: [lead-frontend-engineer]
spec_version: "2.0"
---

# Salesforce Lightning Design System — Framework Skill

## Version Check (run on every load)

1. Web search for `Salesforce Lightning Design System latest release`.
2. Compare against `pinned_version: SLDS 2 (2.29.0)`.
3. Flag if newer. Proceed with current knowledge.

---

## Architecture

SLDS provides CSS-only component blueprints (HTML/CSS patterns) and design tokens.
Implementation happens via Lightning Web Components (LWC) on the Salesforce platform
or via the blueprint CSS in any context.

### SLDS 2 (Winter '26 GA)

Major redesign introducing:
- **Dark mode** — first-class support
- **Agentic design patterns** — UI for AI agents (Agentforce)
- **Updated component blueprints** — refreshed visual language
- **New token architecture** — refined semantic tokens

### Token structure

```
Global:     --slds-g-color-brand-base-50
Semantic:   --slds-c-button-color-background
Component:  Scoped via component blueprints
```

SLDS tokens use a `--slds-` prefix and follow a verbose but explicit naming convention:
`--slds-{scope}-{category}-{property}-{variant}-{state}`

### Key patterns worth studying

| Pattern | Why it's notable |
|---|---|
| **Blueprint model** | CSS-only component specs — framework-agnostic by design |
| **Density tokens** | Compact/comfortable/spacious modes via token swapping |
| **Agentic UI** | Patterns for AI agent interaction surfaces (SLDS 2) |
| **Expression design** | Icon + illustration system for empty states and guidance |
| **Activity Timeline** | Vertical timeline pattern for record history |

### Lightning Web Components (LWC)

LWC uses web standards (Shadow DOM, custom elements, ES modules):

```javascript
import { LightningElement, api } from 'lwc';

export default class DsButton extends LightningElement {
  @api variant = 'primary';
  @api label;
}
```

---

## Design-Engineer Integration

Spoke of `design-engineer`. SLDS is a reference exemplar for:
- Token naming conventions (verbose but unambiguous)
- Blueprint-first (CSS-only) component specification
- Density/mode switching via tokens
- Agentic/AI UI patterns (emerging, SLDS 2)
