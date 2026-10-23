---
name: fw-storybook
description: >
  Storybook component documentation, visual testing, and interaction testing for design
  systems. Use this skill whenever the conversation involves Storybook configuration,
  writing stories (CSF), visual regression testing, interaction testing, addon setup,
  Storybook for design system documentation, or publishing component showcases. Also
  trigger when discussing design/dev handoff documentation, component state matrices,
  or building a living style guide. If the user mentions "Storybook", "stories",
  "CSF", ".stories.tsx", "Chromatic", or component documentation tooling — use this
  skill.
pinned_version: "10.3.3"
pinned_date: "2026-03-26"
changelog_url: "https://github.com/storybookjs/storybook/releases"
aliases: [fw-storybook]
tier: spoke
domain: engineering
hub: lead-frontend-engineer
prerequisites: [lead-frontend-engineer]
spec_version: "2.0"
triggers: [component state matrices, storybook, stories.tsx, chromatic]
---

# Storybook — Framework Skill

## Version Check (run on every load)

1. Web search for `Storybook latest release`.
2. Compare against `pinned_version: 10.3.3`.
3. Flag if newer (v11 expected Spring 2026). Proceed.

---

## Core Concept

Storybook is an isolated development environment for UI components. For design systems,
it serves as: component documentation, visual regression baseline, interaction test
runner, and designer handoff reference.

---

## v10 Key Changes

- **ESM-only** distribution (breaking from v9)
- **29% smaller** install size
- **CSF Factories** (Preview) — new story authoring format, default in v11
- **Type-safe stories** with `satisfies Meta<typeof Component>`

---

## Story Authoring (CSF 3)

```tsx
// Button.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import { Button } from './Button';

const meta = {
  title: 'Components/Button',
  component: Button,
  tags: ['autodocs'],
  argTypes: {
    variant: {
      control: 'select',
      options: ['primary', 'secondary', 'ghost'],
    },
    size: { control: 'select', options: ['sm', 'md', 'lg'] },
    disabled: { control: 'boolean' },
  },
} satisfies Meta<typeof Button>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Primary: Story = {
  args: { variant: 'primary', children: 'Button' },
};

export const Secondary: Story = {
  args: { variant: 'secondary', children: 'Button' },
};

export const AllVariants: Story = {
  render: () => (
    <div style={{ display: 'flex', gap: 8 }}>
      <Button variant="primary">Primary</Button>
      <Button variant="secondary">Secondary</Button>
      <Button variant="ghost">Ghost</Button>
    </div>
  ),
};
```

---

## DS-Essential Addons

| Addon | Purpose |
|---|---|
| `@storybook/addon-docs` | Auto-generated docs from props/JSDoc |
| `@storybook/addon-a11y` | Axe accessibility audit per story |
| `@storybook/addon-interactions` | Interaction testing (play functions) |
| `@storybook/addon-viewport` | Responsive testing |
| `@storybook/addon-themes` | Theme switching (light/dark/brand) |
| `storybook-addon-designs` | Embed Figma frames alongside stories |

---

## Interaction Testing

```tsx
import { within, userEvent, expect } from '@storybook/test';

export const ClickTest: Story = {
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const button = canvas.getByRole('button');
    await userEvent.click(button);
    await expect(button).toHaveFocus();
  },
};
```

---

## Design System Documentation Pattern

```
Components/
├── Primitives/
│   ├── Button/
│   │   ├── Default.stories.tsx
│   │   ├── States.stories.tsx     (all states matrix)
│   │   └── Anatomy.mdx           (component anatomy doc)
│   ├── Input/
│   └── Badge/
├── Composites/
│   ├── InputGroup/
│   └── CardHeader/
├── Patterns/
│   ├── DataTable/
│   └── Modal/
└── Tokens/
    ├── Colors.stories.tsx         (swatch grid)
    ├── Typography.stories.tsx     (type scale)
    └── Spacing.stories.tsx        (spacing scale)
```

---

## Design-Engineer Integration

Spoke of `design-engineer`. Storybook is the documentation and testing layer:
- Pair with any framework skill (React, Vue, Angular, Svelte)
- Use `addon-designs` to link Figma frames
- Use `addon-a11y` for automated accessibility auditing
- Use interaction tests for behavioral contracts

## Related
- hub → [[lead-frontend-engineer]]
