---
name: fw-angular
description: >
  Angular framework patterns for design system implementation — standalone components,
  signals, content projection, directive-based theming, and cross-framework component
  alignment. Use this skill whenever the conversation involves Angular components in
  a design system context, Angular standalone component architecture, signal-based
  reactivity, ng-content projection, Angular-specific token consumption, or ensuring
  parity between Angular and React/Vue DS implementations. If the user mentions
  "Angular", "@angular/*", "ng-content", "signals", or is working on a DS targeting
  Angular — use this skill.
pinned_version: "21"
pinned_date: "2026-03-26"
changelog_url: "https://github.com/angular/angular/releases"
aliases: [fw-angular]
tier: spoke
domain: engineering
hub: lead-frontend-engineer
prerequisites: [lead-frontend-engineer]
spec_version: "2.0"
---

# Angular — Framework Skill

## Version Check (run on every load)

1. Web search for `Angular latest release`.
2. Compare against `pinned_version: 21`.
3. Flag if newer. Proceed with current knowledge.

---

## DS-Relevant Angular Patterns

### Standalone component (v21+ default)

```typescript
@Component({
  selector: 'ds-button',
  standalone: true,
  imports: [CommonModule],
  template: `
    <button
      [class]="computedClasses()"
      [disabled]="disabled()">
      <ng-content />
    </button>
  `,
  styles: [`
    :host { display: inline-flex; }
    .btn { /* token-driven styles */ }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ButtonComponent {
  variant = input<'primary' | 'secondary' | 'ghost'>('primary');
  size = input<'sm' | 'md' | 'lg'>('md');
  disabled = input<boolean>(false);

  computedClasses = computed(() =>
    `btn btn--${this.variant()} btn--${this.size()}`
  );
}
```

### Signal-based reactivity (Angular 17+)

Signals replace RxJS for simple state in DS components:

```typescript
// Component-local state
const count = signal(0);
const doubled = computed(() => count() * 2);

// Theme injection
const theme = inject(DS_THEME_TOKEN);
const primaryColor = computed(() => theme().colors.primary);
```

### Content projection = Figma slots

```typescript
// Single slot
<ng-content />

// Named slots
<ng-content select="[slot=header]" />
<ng-content select="[slot=footer]" />

// Usage
<ds-card>
  <div slot="header">Card Title</div>
  <p>Body content</p>
  <div slot="footer">Actions</div>
</ds-card>
```

### Token consumption

```typescript
// Injection token for theme
export const DS_THEME_TOKEN = new InjectionToken<Theme>('ds-theme');

// Provider at app root
providers: [
  { provide: DS_THEME_TOKEN, useValue: defaultTheme },
]

// CSS custom properties (preferred)
:host {
  --button-bg: var(--color-primary);
  --button-text: var(--color-on-primary);
}
```

---

## React ↔ Angular Parity Mapping

| React | Angular | Notes |
|---|---|---|
| `props` | `input()` signals | v17+ signal inputs |
| `children` | `<ng-content />` | Default projection |
| Named slots | `<ng-content select="...">` | Attribute selectors |
| `useState` | `signal()` | |
| `useEffect` | `effect()` | |
| `useContext` | `inject()` + `InjectionToken` | |
| `forwardRef` | `viewChild()` signal | |
| `className` | `[class]` / `[ngClass]` | |
| Composition | Directives + host bindings | |

---

## Design-Engineer Integration

Spoke of `design-engineer`. Angular DS components should:
1. Use standalone components (no NgModules for DS primitives)
2. Prefer signals over RxJS for component-local state
3. Use CSS custom properties for tokens (not TypeScript theme objects)
4. Use OnPush change detection universally
5. Test a11y with cdk/a11y utilities

## Related
- hub → [[lead-frontend-engineer]]
