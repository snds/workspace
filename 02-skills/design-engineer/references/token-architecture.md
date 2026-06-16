# Token Architecture Reference

> **Status:** Stub — expand as token work progresses.

## Contents

### 3-Tier Token Model

```
Global (Primitives)
  Raw values. Color ramps, spacing scale, type scale, radius scale.
  No semantic meaning. Never consumed directly by components.
  Figma: Primitives collection, zero modes.

Semantic (Aliases)
  Purpose-driven names. color.background.primary, spacing.inline.md.
  Maps to different primitives per mode (Light/Dark, Brand A/B).
  Figma: Semantic collection, modes for themes.

Component (Scoped)
  Component-specific overrides. button.padding.x, input.border.color.
  References semantic tokens. Modes for density (Default/Compact).
  Figma: Component collection (optional — only for complex components).
```

### DTCG Format (W3C Design Tokens Community Group)

Standard JSON format for token interchange:

```json
{
  "color": {
    "action": {
      "primary": {
        "$value": "{color.blue.600}",
        "$type": "color",
        "$description": "Primary action background"
      }
    }
  }
}
```

Reference: https://design-tokens.github.io/community-group/format/

### Style Dictionary Integration

Transform tokens from DTCG format into platform outputs:
- CSS custom properties
- iOS Swift/SwiftUI constants
- Android XML resources
- Figma variable JSON (via Figma Variables REST API or plugin)

### Figma Variable Structure

Map collections to tiers:
- Collection "Primitives" → Global tier
- Collection "Semantic" → Semantic tier (modes: Light, Dark)
- Collection "Component/[name]" → Component tier (modes: Default, Compact)

Scoping rules: see `figma-authoring.md` section 2.

### Token Naming Convention

```
{category}.{property}.{variant}.{state}

Examples:
  color.background.primary
  color.text.on-action
  spacing.inline.md
  radius.component.button
  font.size.body.default
  border.width.thin
```

- Use dot notation consistently.
- `on-` prefix for colors designed to sit on a specific background.
- Size scale: xs, sm, md, lg, xl (avoid numbered scales like 100/200/300
  at the semantic tier — numbers belong at the primitive tier).
