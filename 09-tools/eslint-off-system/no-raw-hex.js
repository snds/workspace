/**
 * off-system/no-raw-hex
 *
 * Ban color literals so agents must go through the product token table.
 * Allowlist token SSOTs in the product eslint.config.js (not here).
 */
const HEX = /#(?:[0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})\b/;
const FUNC = /\b(?:rgb|rgba|hsl|hsla|oklch|oklab|hwb)\s*\(/i;

function reportIfColorLiteral(context, node, value) {
  if (typeof value !== 'string') return;
  if (HEX.test(value) || FUNC.test(value)) {
    context.report({
      node,
      messageId: 'rawColor',
      data: { value: value.slice(0, 40) },
    });
  }
}

const rule = {
  meta: {
    type: 'problem',
    docs: {
      description:
        'Disallow raw color literals; author via design tokens (cssVar / TOKENS).',
    },
    schema: [],
    messages: {
      rawColor:
        'Off-system color literal {{value}}. Use a token id / cssVar / TOKENS[…].hex instead.',
    },
  },
  create(context) {
    return {
      Literal(node) {
        reportIfColorLiteral(context, node, node.value);
      },
      TemplateElement(node) {
        reportIfColorLiteral(context, node, node.value.cooked);
      },
    };
  },
};

export default rule;
