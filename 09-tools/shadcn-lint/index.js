import noTierLeakage from "./no-tier-leakage.js";

/** @type {import("eslint").ESLint.Plugin} */
const plugin = {
  meta: {
    name: "eslint-plugin-ds-lint",
    version: "1.0.0",
  },
  rules: {
    "no-tier-leakage": noTierLeakage,
  },
};

export default plugin;
