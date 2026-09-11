import type { DesignToken } from '@/types/tokens';

/** Omni's internal design tokens — used for the tool's own UI */
export const OMNI_TOKENS: Record<string, DesignToken> = {
  // Surface hierarchy (dark theme)
  'omni.surface.0': { $value: '#09090b', $type: 'color', $description: 'Deepest surface' },
  'omni.surface.1': { $value: '#111113', $type: 'color', $description: 'Panel backgrounds' },
  'omni.surface.2': { $value: '#1a1a1f', $type: 'color', $description: 'Cards and elevated surfaces' },
  'omni.surface.3': { $value: '#232329', $type: 'color', $description: 'Interactive surface hover' },
  'omni.surface.4': { $value: '#2b2b33', $type: 'color', $description: 'Active/pressed surface' },

  // Text
  'omni.text.primary': { $value: '#ededef', $type: 'color' },
  'omni.text.secondary': { $value: '#a0a0ab', $type: 'color' },
  'omni.text.muted': { $value: '#63636e', $type: 'color' },

  // Border
  'omni.border.default': { $value: '#2b2b33', $type: 'color' },
  'omni.border.subtle': { $value: '#1f1f28', $type: 'color' },
  'omni.border.focus': { $value: '#7c3aed', $type: 'color' },

  // Accent (violet)
  'omni.accent.default': { $value: '#7c3aed', $type: 'color' },
  'omni.accent.hover': { $value: '#6d28d9', $type: 'color' },
  'omni.accent.foreground': { $value: '#ffffff', $type: 'color' },

  // Status colors
  'omni.status.success': { $value: '#22c55e', $type: 'color' },
  'omni.status.warning': { $value: '#f59e0b', $type: 'color' },
  'omni.status.error': { $value: '#ef4444', $type: 'color' },
  'omni.status.info': { $value: '#3b82f6', $type: 'color' },

  // Spacing
  'omni.spacing.xs': { $value: '4px', $type: 'dimension' },
  'omni.spacing.sm': { $value: '8px', $type: 'dimension' },
  'omni.spacing.md': { $value: '12px', $type: 'dimension' },
  'omni.spacing.lg': { $value: '16px', $type: 'dimension' },
  'omni.spacing.xl': { $value: '24px', $type: 'dimension' },

  // Border radius
  'omni.radius.sm': { $value: '4px', $type: 'dimension' },
  'omni.radius.md': { $value: '6px', $type: 'dimension' },
  'omni.radius.lg': { $value: '8px', $type: 'dimension' },
  'omni.radius.full': { $value: '9999px', $type: 'dimension' },
};

/** Convert OMNI_TOKENS to CSS custom properties */
export function omniTokensToCSS(): string {
  const lines: string[] = [];
  for (const [path, token] of Object.entries(OMNI_TOKENS)) {
    if (token.$type === 'color' || token.$type === 'dimension') {
      const varName = `--${path.replace(/\./g, '-')}`;
      lines.push(`  ${varName}: ${token.$value};`);
    }
  }
  return `:root {\n${lines.join('\n')}\n}`;
}
