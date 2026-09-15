/**
 * ds-lint/no-tier-leakage
 *
 * Ban Radix step utilities, Tailwind shade aliases, CDS compat classes
 * (`bg-cds-blue-500`), and raw black/white. Sibling of @shadcn/lint — not a
 * replacement. Spec: ./tier-leakage.json (shared with probe.py).
 *
 * Walks ternaries, `&&` / `||`, object/array literals, and class builders
 * (`cn`, `cva`, …). CDS writes `error ? "border-cds-red-500" : "border-border"`
 * and `cva({ variants: { danger: "bg-cds-red-500" } })`.
 */
import { readFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const spec = JSON.parse(
  readFileSync(join(dirname(fileURLToPath(import.meta.url)), "tier-leakage.json"), "utf8"),
);

const BUILDERS = new Set([
  "cn",
  "cx",
  "clsx",
  "twMerge",
  "twJoin",
  "classNames",
  "cva",
  "tv",
]);

function alt(values) {
  return [...values].sort((a, b) => b.length - a.length).join("|");
}

function leakPattern(spec) {
  const prefixes = alt(spec.prefixes);
  const hues = alt(spec.hues);
  const steps = alt(spec.steps);
  const literals = alt(spec.literal_palette);
  const compat = alt(spec.compat_prefixes || ["cds"]);
  const families = [...spec.hues, ...(spec.compat_extra_families || ["black"])];
  const compatHues = alt(families);
  return `^(?:${prefixes})-(?:(?:${hues})A?-(?:${steps})|(?:${literals})|(?:${compat})-(?:${compatHues})A?-(?:${steps}))$`;
}

const LEAK_RE = new RegExp(leakPattern(spec));

function utilityStem(token) {
  let value = token.trim();
  if (!value) return "";
  if (value.startsWith("!")) value = value.slice(1);
  if (value.includes(":")) value = value.slice(value.lastIndexOf(":") + 1);
  if (value.startsWith("!")) value = value.slice(1);
  const slash = value.indexOf("/");
  if (slash !== -1) value = value.slice(0, slash);
  return value;
}

function leaksIn(value) {
  if (typeof value !== "string") return [];
  return value.split(/\s+/).filter((raw) => {
    const stem = utilityStem(raw);
    return stem && LEAK_RE.test(stem);
  });
}

function reportLeaks(context, node, value) {
  for (const cls of leaksIn(value)) {
    context.report({
      node,
      messageId: "tierLeak",
      data: { cls },
    });
  }
}

function calleeName(node) {
  if (!node) return "";
  if (node.type === "Identifier") return node.name;
  if (node.type === "MemberExpression") return calleeName(node.property);
  return "";
}

function isBuilder(node) {
  return node?.type === "CallExpression" && BUILDERS.has(calleeName(node.callee));
}

function walk(context, node, seen) {
  if (!node || typeof node !== "object") return;
  if (seen.has(node)) return;
  seen.add(node);
  if (node.type === "Literal" && typeof node.value === "string") {
    reportLeaks(context, node, node.value);
  }
  if (node.type === "TemplateLiteral") {
    for (const quasi of node.quasis) {
      reportLeaks(context, quasi, quasi.value.cooked);
    }
  }
  for (const key of Object.keys(node)) {
    if (key === "parent") continue;
    const value = node[key];
    if (Array.isArray(value)) {
      for (const child of value) walk(context, child, seen);
    } else if (value && typeof value === "object" && typeof value.type === "string") {
      walk(context, value, seen);
    }
  }
}

const rule = {
  meta: {
    type: "problem",
    docs: {
      description:
        "Disallow primitive hue-step and shade-alias Tailwind utilities; author via semantic tokens.",
    },
    schema: [],
    messages: {
      tierLeak:
        'Tier leak: "{{cls}}" is a primitive, shade alias, or cds-* compat class. Use a semantic token (bg-primary, text-muted-foreground, bg-destructive). Map hue steps only in CSS token files.',
    },
  },
  create(context) {
    return {
      JSXAttribute(node) {
        const attr = node.name?.name;
        if (attr !== "className" && attr !== "class") return;
        const v = node.value;
        if (!v) return;
        if (v.type === "Literal") {
          reportLeaks(context, v, v.value);
          return;
        }
        if (v.type !== "JSXExpressionContainer" || !v.expression) return;
        if (isBuilder(v.expression)) return;
        walk(context, v.expression, new Set());
      },
      CallExpression(node) {
        if (!isBuilder(node)) return;
        const seen = new Set();
        for (const arg of node.arguments) walk(context, arg, seen);
      },
    };
  },
};

export default rule;
