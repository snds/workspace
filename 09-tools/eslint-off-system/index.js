import noRawHex from './no-raw-hex.js';
import noArbitraryTailwind from './no-arbitrary-tailwind.js';

/** @type {import('eslint').ESLint.Plugin} */
const plugin = {
  meta: {
    name: 'eslint-plugin-off-system',
    version: '1.0.0',
  },
  rules: {
    'no-raw-hex': noRawHex,
    'no-arbitrary-tailwind': noArbitraryTailwind,
  },
};

export default plugin;
