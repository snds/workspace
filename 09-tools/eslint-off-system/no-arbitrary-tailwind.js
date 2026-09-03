/**
 * off-system/no-arbitrary-tailwind
 *
 * Ban Tailwind arbitrary-value utilities in className strings
 * (bg-[#fff], p-[17px], w-[123px], text-[14px], …).
 * No-op for repos that do not use Tailwind; still useful as a future gate.
 */
const ARBITRARY =
  /(?:^|\s)(?:!)?-?(?:[a-z0-9/-]+)?(?:sm:|md:|lg:|xl:|2xl:|dark:|hover:|focus:|active:)*(?:[a-z]+(?:-[a-z0-9]+)*)-\[[^\]]+\]/;

function checkClassString(context, node, value) {
  if (typeof value !== 'string') return;
  if (ARBITRARY.test(value)) {
    context.report({
      node,
      messageId: 'arbitrary',
      data: { value: value.trim().slice(0, 60) },
    });
  }
}

const rule = {
  meta: {
    type: 'problem',
    docs: {
      description:
        'Disallow Tailwind arbitrary values in className; use tokenized utilities.',
    },
    schema: [],
    messages: {
      arbitrary:
        'Off-system Tailwind arbitrary class in {{value}}. Use a design decision token / utility.',
    },
  },
  create(context) {
    return {
      JSXAttribute(node) {
        if (node.name?.name !== 'className' && node.name?.name !== 'class') return;
        const v = node.value;
        if (!v) return;
        if (v.type === 'Literal') checkClassString(context, v, v.value);
        if (v.type === 'JSXExpressionContainer' && v.expression?.type === 'Literal') {
          checkClassString(context, v.expression, v.expression.value);
        }
        if (
          v.type === 'JSXExpressionContainer' &&
          v.expression?.type === 'TemplateLiteral'
        ) {
          for (const q of v.expression.quasis) {
            checkClassString(context, q, q.value.cooked);
          }
        }
      },
    };
  },
};

export default rule;
