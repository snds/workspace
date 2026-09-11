// ─── Static design tokens ─────────────────────────────────────────────────────
// These are standard design system tokens not tied to a generated color system.

export interface StaticToken {
  id: string;
  name: string;
  /** Short form shown in the row (e.g. "16px", "400", "md") */
  shortValue: string;
  /** Full CSS value shown in expanded detail */
  fullValue: string;
  description?: string;
  /** Numeric form for visual previews (px for sizes, weight number, opacity float, etc.) */
  meta?: number;
}

// ─── Typography ───────────────────────────────────────────────────────────────

export const TYPOGRAPHY_TOKENS: Record<string, StaticToken[]> = {
  "Font Family": [
    {
      id: "font.family.sans",
      name: "font.family.sans",
      shortValue: "sans",
      fullValue: "system-ui, -apple-system, Inter, sans-serif",
      description: "Default sans-serif typeface",
    },
    {
      id: "font.family.mono",
      name: "font.family.mono",
      shortValue: "mono",
      fullValue: "JetBrains Mono, Fira Code, monospace",
      description: "Monospace typeface for code",
    },
    {
      id: "font.family.serif",
      name: "font.family.serif",
      shortValue: "serif",
      fullValue: "Georgia, Times New Roman, serif",
      description: "Serif typeface",
    },
  ],

  "Font Size": [
    { id: "font.size.xs",   name: "font.size.xs",   shortValue: "12px", fullValue: "0.75rem / 12px",   meta: 12 },
    { id: "font.size.sm",   name: "font.size.sm",   shortValue: "14px", fullValue: "0.875rem / 14px",  meta: 14 },
    { id: "font.size.base", name: "font.size.base", shortValue: "16px", fullValue: "1rem / 16px",      meta: 16 },
    { id: "font.size.lg",   name: "font.size.lg",   shortValue: "18px", fullValue: "1.125rem / 18px",  meta: 18 },
    { id: "font.size.xl",   name: "font.size.xl",   shortValue: "20px", fullValue: "1.25rem / 20px",   meta: 20 },
    { id: "font.size.2xl",  name: "font.size.2xl",  shortValue: "24px", fullValue: "1.5rem / 24px",    meta: 24 },
    { id: "font.size.3xl",  name: "font.size.3xl",  shortValue: "30px", fullValue: "1.875rem / 30px",  meta: 30 },
    { id: "font.size.4xl",  name: "font.size.4xl",  shortValue: "36px", fullValue: "2.25rem / 36px",   meta: 36 },
    { id: "font.size.5xl",  name: "font.size.5xl",  shortValue: "48px", fullValue: "3rem / 48px",      meta: 48 },
    { id: "font.size.6xl",  name: "font.size.6xl",  shortValue: "60px", fullValue: "3.75rem / 60px",   meta: 60 },
  ],

  "Font Weight": [
    { id: "font.weight.thin",      name: "font.weight.thin",      shortValue: "100", fullValue: "100", meta: 100 },
    { id: "font.weight.light",     name: "font.weight.light",     shortValue: "300", fullValue: "300", meta: 300 },
    { id: "font.weight.regular",   name: "font.weight.regular",   shortValue: "400", fullValue: "400", meta: 400 },
    { id: "font.weight.medium",    name: "font.weight.medium",    shortValue: "500", fullValue: "500", meta: 500 },
    { id: "font.weight.semibold",  name: "font.weight.semibold",  shortValue: "600", fullValue: "600", meta: 600 },
    { id: "font.weight.bold",      name: "font.weight.bold",      shortValue: "700", fullValue: "700", meta: 700 },
    { id: "font.weight.extrabold", name: "font.weight.extrabold", shortValue: "800", fullValue: "800", meta: 800 },
  ],

  "Line Height": [
    { id: "font.leading.none",    name: "font.leading.none",    shortValue: "1",     fullValue: "1",     meta: 1     },
    { id: "font.leading.tight",   name: "font.leading.tight",   shortValue: "1.25",  fullValue: "1.25",  meta: 1.25  },
    { id: "font.leading.snug",    name: "font.leading.snug",    shortValue: "1.375", fullValue: "1.375", meta: 1.375 },
    { id: "font.leading.normal",  name: "font.leading.normal",  shortValue: "1.5",   fullValue: "1.5",   meta: 1.5   },
    { id: "font.leading.relaxed", name: "font.leading.relaxed", shortValue: "1.625", fullValue: "1.625", meta: 1.625 },
    { id: "font.leading.loose",   name: "font.leading.loose",   shortValue: "2",     fullValue: "2",     meta: 2     },
  ],

  "Letter Spacing": [
    { id: "font.tracking.tighter", name: "font.tracking.tighter", shortValue: "-0.05em",  fullValue: "-0.05em",  meta: -0.05 },
    { id: "font.tracking.tight",   name: "font.tracking.tight",   shortValue: "-0.025em", fullValue: "-0.025em", meta: -0.025 },
    { id: "font.tracking.normal",  name: "font.tracking.normal",  shortValue: "0em",      fullValue: "0em",      meta: 0 },
    { id: "font.tracking.wide",    name: "font.tracking.wide",    shortValue: "0.025em",  fullValue: "0.025em",  meta: 0.025 },
    { id: "font.tracking.wider",   name: "font.tracking.wider",   shortValue: "0.05em",   fullValue: "0.05em",   meta: 0.05 },
    { id: "font.tracking.widest",  name: "font.tracking.widest",  shortValue: "0.1em",    fullValue: "0.1em",    meta: 0.1 },
  ],
};

// ─── Spacing ──────────────────────────────────────────────────────────────────

export const SPACING_TOKENS: StaticToken[] = [
  { id: "space.0",    name: "space.0",    shortValue: "0",   fullValue: "0px",               meta: 0   },
  { id: "space.1px",  name: "space.1px",  shortValue: "1px", fullValue: "1px",               meta: 1   },
  { id: "space.0.5",  name: "space.0.5",  shortValue: "2px", fullValue: "0.125rem / 2px",    meta: 2   },
  { id: "space.1",    name: "space.1",    shortValue: "4px", fullValue: "0.25rem / 4px",     meta: 4   },
  { id: "space.1.5",  name: "space.1.5",  shortValue: "6px", fullValue: "0.375rem / 6px",    meta: 6   },
  { id: "space.2",    name: "space.2",    shortValue: "8px", fullValue: "0.5rem / 8px",      meta: 8   },
  { id: "space.2.5",  name: "space.2.5",  shortValue: "10px", fullValue: "0.625rem / 10px",  meta: 10  },
  { id: "space.3",    name: "space.3",    shortValue: "12px", fullValue: "0.75rem / 12px",   meta: 12  },
  { id: "space.3.5",  name: "space.3.5",  shortValue: "14px", fullValue: "0.875rem / 14px",  meta: 14  },
  { id: "space.4",    name: "space.4",    shortValue: "16px", fullValue: "1rem / 16px",      meta: 16  },
  { id: "space.5",    name: "space.5",    shortValue: "20px", fullValue: "1.25rem / 20px",   meta: 20  },
  { id: "space.6",    name: "space.6",    shortValue: "24px", fullValue: "1.5rem / 24px",    meta: 24  },
  { id: "space.7",    name: "space.7",    shortValue: "28px", fullValue: "1.75rem / 28px",   meta: 28  },
  { id: "space.8",    name: "space.8",    shortValue: "32px", fullValue: "2rem / 32px",      meta: 32  },
  { id: "space.9",    name: "space.9",    shortValue: "36px", fullValue: "2.25rem / 36px",   meta: 36  },
  { id: "space.10",   name: "space.10",   shortValue: "40px", fullValue: "2.5rem / 40px",    meta: 40  },
  { id: "space.12",   name: "space.12",   shortValue: "48px", fullValue: "3rem / 48px",      meta: 48  },
  { id: "space.14",   name: "space.14",   shortValue: "56px", fullValue: "3.5rem / 56px",    meta: 56  },
  { id: "space.16",   name: "space.16",   shortValue: "64px", fullValue: "4rem / 64px",      meta: 64  },
  { id: "space.20",   name: "space.20",   shortValue: "80px", fullValue: "5rem / 80px",      meta: 80  },
  { id: "space.24",   name: "space.24",   shortValue: "96px", fullValue: "6rem / 96px",      meta: 96  },
  { id: "space.32",   name: "space.32",   shortValue: "128px", fullValue: "8rem / 128px",    meta: 128 },
];

// ─── Border ───────────────────────────────────────────────────────────────────

export const BORDER_TOKENS: Record<string, StaticToken[]> = {
  "Radius": [
    { id: "radius.none", name: "radius.none", shortValue: "0",      fullValue: "0px",    meta: 0    },
    { id: "radius.xs",   name: "radius.xs",   shortValue: "2px",    fullValue: "0.125rem / 2px",  meta: 2    },
    { id: "radius.sm",   name: "radius.sm",   shortValue: "4px",    fullValue: "0.25rem / 4px",   meta: 4    },
    { id: "radius.md",   name: "radius.md",   shortValue: "6px",    fullValue: "0.375rem / 6px",  meta: 6    },
    { id: "radius.lg",   name: "radius.lg",   shortValue: "8px",    fullValue: "0.5rem / 8px",    meta: 8    },
    { id: "radius.xl",   name: "radius.xl",   shortValue: "12px",   fullValue: "0.75rem / 12px",  meta: 12   },
    { id: "radius.2xl",  name: "radius.2xl",  shortValue: "16px",   fullValue: "1rem / 16px",     meta: 16   },
    { id: "radius.3xl",  name: "radius.3xl",  shortValue: "24px",   fullValue: "1.5rem / 24px",   meta: 24   },
    { id: "radius.full", name: "radius.full", shortValue: "9999px", fullValue: "9999px",           meta: 9999 },
  ],
  "Width": [
    { id: "border.width.none",     name: "border.width.none",     shortValue: "0",     fullValue: "0px",   meta: 0   },
    { id: "border.width.hairline", name: "border.width.hairline", shortValue: "0.5px", fullValue: "0.5px", meta: 0.5 },
    { id: "border.width.thin",     name: "border.width.thin",     shortValue: "1px",   fullValue: "1px",   meta: 1   },
    { id: "border.width.medium",   name: "border.width.medium",   shortValue: "2px",   fullValue: "2px",   meta: 2   },
    { id: "border.width.thick",    name: "border.width.thick",    shortValue: "4px",   fullValue: "4px",   meta: 4   },
    { id: "border.width.heavy",    name: "border.width.heavy",    shortValue: "8px",   fullValue: "8px",   meta: 8   },
  ],
};

// ─── Effects ──────────────────────────────────────────────────────────────────

export const EFFECT_TOKENS: Record<string, StaticToken[]> = {
  "Shadow": [
    { id: "shadow.none",  name: "shadow.none",  shortValue: "none",  fullValue: "none" },
    { id: "shadow.xs",    name: "shadow.xs",    shortValue: "xs",    fullValue: "0 1px 2px rgb(0 0 0 / 0.05)" },
    { id: "shadow.sm",    name: "shadow.sm",    shortValue: "sm",    fullValue: "0 1px 3px rgb(0 0 0 / 0.1), 0 1px 2px rgb(0 0 0 / 0.06)" },
    { id: "shadow.md",    name: "shadow.md",    shortValue: "md",    fullValue: "0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)" },
    { id: "shadow.lg",    name: "shadow.lg",    shortValue: "lg",    fullValue: "0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)" },
    { id: "shadow.xl",    name: "shadow.xl",    shortValue: "xl",    fullValue: "0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)" },
    { id: "shadow.2xl",   name: "shadow.2xl",   shortValue: "2xl",   fullValue: "0 25px 50px -12px rgb(0 0 0 / 0.25)" },
    { id: "shadow.inner", name: "shadow.inner", shortValue: "inner", fullValue: "inset 0 2px 4px 0 rgb(0 0 0 / 0.05)" },
  ],
  "Blur": [
    { id: "blur.none", name: "blur.none", shortValue: "0",    fullValue: "0px",  meta: 0  },
    { id: "blur.sm",   name: "blur.sm",   shortValue: "4px",  fullValue: "4px",  meta: 4  },
    { id: "blur.md",   name: "blur.md",   shortValue: "8px",  fullValue: "8px",  meta: 8  },
    { id: "blur.lg",   name: "blur.lg",   shortValue: "16px", fullValue: "16px", meta: 16 },
    { id: "blur.xl",   name: "blur.xl",   shortValue: "24px", fullValue: "24px", meta: 24 },
    { id: "blur.2xl",  name: "blur.2xl",  shortValue: "40px", fullValue: "40px", meta: 40 },
    { id: "blur.3xl",  name: "blur.3xl",  shortValue: "64px", fullValue: "64px", meta: 64 },
  ],
  "Opacity": [
    { id: "opacity.0",   name: "opacity.0",   shortValue: "0",    fullValue: "0",    meta: 0    },
    { id: "opacity.5",   name: "opacity.5",   shortValue: "5%",   fullValue: "0.05", meta: 0.05 },
    { id: "opacity.10",  name: "opacity.10",  shortValue: "10%",  fullValue: "0.1",  meta: 0.1  },
    { id: "opacity.20",  name: "opacity.20",  shortValue: "20%",  fullValue: "0.2",  meta: 0.2  },
    { id: "opacity.30",  name: "opacity.30",  shortValue: "30%",  fullValue: "0.3",  meta: 0.3  },
    { id: "opacity.40",  name: "opacity.40",  shortValue: "40%",  fullValue: "0.4",  meta: 0.4  },
    { id: "opacity.50",  name: "opacity.50",  shortValue: "50%",  fullValue: "0.5",  meta: 0.5  },
    { id: "opacity.60",  name: "opacity.60",  shortValue: "60%",  fullValue: "0.6",  meta: 0.6  },
    { id: "opacity.70",  name: "opacity.70",  shortValue: "70%",  fullValue: "0.7",  meta: 0.7  },
    { id: "opacity.80",  name: "opacity.80",  shortValue: "80%",  fullValue: "0.8",  meta: 0.8  },
    { id: "opacity.90",  name: "opacity.90",  shortValue: "90%",  fullValue: "0.9",  meta: 0.9  },
    { id: "opacity.100", name: "opacity.100", shortValue: "100%", fullValue: "1",    meta: 1    },
  ],
};
