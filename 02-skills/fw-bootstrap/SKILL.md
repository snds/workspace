---
name: fw-bootstrap
description: >
  Bootstrap CSS framework — utility classes, Sass variables, component library, and
  theming for design systems. Use this skill whenever the conversation involves Bootstrap
  components, Bootstrap utility API, Sass variable customization, Bootstrap grid system,
  or analyzing/referencing Bootstrap as a design system foundation. Also trigger when
  migrating from Bootstrap to another system, extracting patterns from Bootstrap-based
  projects, or when the target stack uses Bootstrap. If the user mentions "Bootstrap",
  "BS5", "bootstrap.css", "bootstrap-sass", or Bootstrap component names — use this
  skill.
pinned_version: "5.3.8"
pinned_date: "2026-03-26"
changelog_url: "https://github.com/twbs/bootstrap/releases"
aliases: [fw-bootstrap]
tier: spoke
domain: engineering
hub: lead-frontend-engineer
prerequisites: [lead-frontend-engineer]
spec_version: "2.0"
---

# Bootstrap — Framework Skill

## Version Check (run on every load)

1. Web search for `Bootstrap latest release`.
2. Compare against `pinned_version: 5.3.8`.
3. Flag if newer. Proceed.

---

## Architecture

Bootstrap is a CSS framework with optional JavaScript for interactive components.
It uses Sass for customization and ships with a comprehensive utility API.

### Customization via Sass variables

```scss
// Override before importing Bootstrap
$primary: #0d6efd;
$font-family-base: "Inter", sans-serif;
$spacer: 1rem;
$border-radius: 0.375rem;
$enable-dark-mode: true;

@import "bootstrap/scss/bootstrap";
```

### CSS custom properties (v5.3+)

Bootstrap 5.3 added CSS custom properties for runtime theming:

```css
:root {
  --bs-primary: #0d6efd;
  --bs-primary-rgb: 13, 110, 253;
  --bs-body-font-family: "Inter", sans-serif;
  --bs-body-bg: #fff;
  --bs-body-color: #212529;
}

[data-bs-theme="dark"] {
  --bs-body-bg: #212529;
  --bs-body-color: #dee2e6;
}
```

### Utility API

Bootstrap's utility API generates utility classes from a config map:

```scss
$utilities: (
  "opacity": (
    property: opacity,
    values: (0: 0, 25: .25, 50: .5, 75: .75, 100: 1),
    responsive: true,
  ),
);
```

### Grid system

12-column flexbox grid with 6 responsive breakpoints:

| Breakpoint | Prefix | Min width |
|---|---|---|
| Extra small | (none) | 0 |
| Small | `sm` | 576px |
| Medium | `md` | 768px |
| Large | `lg` | 992px |
| Extra large | `xl` | 1200px |
| XXL | `xxl` | 1400px |

### Key patterns worth studying

| Pattern | Why it's notable |
|---|---|
| **Utility API** | Configurable utility generation — inspired Tailwind's approach |
| **Color modes** | data-bs-theme attribute for dark mode (v5.3+) |
| **Component JS** | Minimal JS with data attributes — no framework dependency |
| **Sass architecture** | Well-organized variable → mixin → component layering |

---

## Design-Engineer Integration

Spoke of `design-engineer`. Bootstrap is relevant as:
- Migration source (many enterprise apps started with Bootstrap)
- Reference for utility API design
- Sass variable architecture exemplar
- When the target stack requires Bootstrap compatibility

## Related
- hub → [[lead-frontend-engineer]]
