# React Component Patterns Reference

> **Status:** Stub — expand as React DS component work progresses.

## Contents

### DS-Grade React Component Structure

```
ComponentName/
├── ComponentName.tsx       # Component implementation
├── ComponentName.types.ts  # TypeScript prop types + exports
├── ComponentName.styles.ts # Token-consuming styles (CSS modules or styled)
├── ComponentName.test.tsx  # Unit + accessibility tests
├── ComponentName.stories.tsx # Storybook stories
├── index.ts               # Public API barrel export
└── README.md              # Usage docs (for complex components)
```

### Prop Design Principles

- Props are the public API. Treat additions as features and removals as
  breaking changes.
- Prefer composition (`children`, render props, named slot props) over
  configuration (long lists of boolean props).
- Map Figma properties → React props 1:1 where feasible:
  - Figma boolean property → `boolean` prop
  - Figma text property → `string` prop
  - Figma instance swap → `ReactNode` prop or component prop
  - Figma slot → `children` or named `ReactNode` prop
  - Figma variant axis → union type prop (`size: 'sm' | 'md' | 'lg'`)

### Token Consumption

Components consume tokens via CSS custom properties or a theme object.
Never import primitive-tier values directly.

```tsx
// WRONG — bypasses semantic layer
import { blue600 } from '@tokens/primitives';
const style = { background: blue600 };

// CORRECT — consumes semantic token
const style = { background: 'var(--color-action-primary)' };

// ALSO CORRECT — via theme object
const theme = useTheme();
const style = { background: theme.color.action.primary };
```

### Accessibility as Structure

Accessibility is built into the component, not added later:
- Use semantic HTML elements (`button`, `input`, `dialog`, `nav`).
- Add ARIA attributes where semantic HTML is insufficient.
- Implement keyboard navigation per WAI-ARIA APG patterns.
- Manage focus: trap in modals, restore on close, announce to screen readers.
- Test with axe-core in unit tests and Storybook a11y addon.

### Controlled vs. Uncontrolled

Support both patterns for stateful components:

```tsx
interface InputProps {
  value?: string;          // Controlled
  defaultValue?: string;   // Uncontrolled
  onChange?: (value: string) => void;
}
```

### Forwarding Refs

All DS components should forward refs for composition:

```tsx
const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  (props, ref) => {
    return <button ref={ref} {...props} />;
  }
);
```

### Testing Checklist

- [ ] Renders without error
- [ ] All prop combinations render correctly
- [ ] Keyboard navigation works per APG pattern
- [ ] axe-core reports no violations
- [ ] Focus management works (modals, dropdowns)
- [ ] Responsive behavior at breakpoints
- [ ] Token/theme switching renders correctly
