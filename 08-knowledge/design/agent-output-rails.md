---
tags: [design-systems, agents, evals, lint, qa, verification, knowledge-vault]
created: 2026-09-03
updated: 2026-09-03
status: working
confidence: medium
sources:
  - "PJ Onori — How well do agents use your design system? (sanity.io/engineering/design-system-evals, 2026-08-26)"
  - "sanity-labs/design-system-agent-tester (open-source harness; Claude-only, WIP)"
  - "Workspace DSDS constitution + visual-prove-engine + llm-safe-design-system-expressiveness (2026-09)"
related_skills: [visual-prove-engine, visual-reference-replication, ds-source-watch, ds-advisor, design-engineer, a11y-audit-toolkit]
related_projects: [19-workspace-brain, 20-lcars-generative-interface]
domain_agnostic: true
relations:
  builds-on:
    - "[[measured-visual-verdicts]]"
    - "[[agentic-error-correction-foundations]]"
    - "[[llm-safe-design-system-expressiveness]]"
    - "[[agentic-ds-context-model]]"
  relates-to:
    - "[[dsds-constitution]]"
    - "[[component-contracts-and-schemas]]"
---

# For future agent

- **TL;DR:** Steal Onori's isolation law, pack recipes (chunks), and product-repo lint. Do not clone his n-agent tester. Capture and prove live in [[visual-prove-engine]], not in a project script.
- **Key claims:**
  - *Timeless:* extra rails (chunks, lint autofix, MCP wizards, extra skills) can hide that the docs or catalog failed. Measure with assistance off.
  - *Timeless:* agent feedback reports symptoms. Humans name the cause. Same-model critique is not a prove-gate.
  - *Timeless:* more docs plateau. Better structured docs (DSDS) beat volume. Pack recipes beat a prop-walking wizard.
  - *Dated 2026-08:* Sanity UI numbers (Haiku/Sonnet/Opus n=30, AILF +34) are his system, his prompts, Claude-only. Do not treat them as transferable scores.
  - *Pointer:* lint that makes off-system values inexpressible lives in the **product repo**. The vault owns the law, not the ESLint config.
- **As of:** 2026-09 · **Status:** current
- **Audience:** `for: agent`

# Agent-output rails

Testimony: Onori's Sanity evals post. This note keeps the transferable method. It does not adopt Sanity UI, the tester, or a `chunk` kind in the workspace DSDS constitution.

## What the workspace already had

| Layer | Job |
|---|---|
| DSDS constitution | Docs as data. Meaning, not values |
| [[llm-safe-design-system-expressiveness]] | Off-system values must be inexpressible. CI is the contract |
| [[visual-prove-engine]] | Pixels are the critic. Compile success is not quality |
| [[agentic-error-correction-foundations]] | Independent measurement. Agent narrative is polish |

The miss was the **loop**, not the schema. Structured docs landed without a workspace-generic way to capture a URL into a provenanced PNG, and without an isolation stamp when assistance was on.

## Laws (travel with every coded surface)

1. **Isolation.** When the claim is "the docs / catalog / pack are enough," run the prove with chunks, lint autofix, MCP wizards, and extra skills **off**. Record `assistance: off` on the capture (`vqa capture --assistance off`) and `_provenance.assistance: "off"` on the cuespec. Assistance on is allowed for shipping. It is not allowed as the score for the docs.
2. **Recipes stay in the pack.** A chunk is a pasteable legal composition (when/why/how + code). It is not a new workspace DSDS kind until the spec ships one. LCARS `src/catalog/` and `generate-display-svg.py` are the existing form. Other packs get their own catalog. The method is shared; the primitives are not.
3. **Lint in the repo agents write.** Hex, arbitrary utilities, and off-token layout fail in that repo's CI. Do not add a vault ESLint that pretends to know every product grammar. Shared rule source: `09-tools/eslint-off-system/`. First product: LCARS `npm run lint`. Shared rule source: `09-tools/eslint-off-system/`. First product: LCARS `npm run lint`.
4. **Quality proxies are complementary.** axe / inline-style / responsive counts ([[a11y-audit-toolkit]]) sit beside pixel cues. They do not replace `vqa prove`. Eyeball remains testimony.
5. **Do not clone the tester.** `sanity-labs/design-system-agent-tester` is Claude-only, paid per run, and scores do not transfer. The workspace equivalent is: capture → prove → score --enforce. n-agent same-prompt sweeps stay a human-asked experiment.

## Capture is workspace-owned

```
python3 03-skills/visual-prove-engine/vqa.py capture URL -o build.png --viewport 1920x1080 --dpr 2 --assistance off
python3 03-skills/visual-prove-engine/vqa.py prove build.png CUESPEC.json
```

Pack wrappers may pass URL and output path. They must not reimplement the manifest. `inspect-*.mjs` that dump pack DOM may stay in the pack.

## Refuse

- A per-project `prove_*.py` with `pass: True` literals (the engine exists because those lied)
- Agent-authored continuous docs as a flywheel (Onori measured the plateau)
- A prop-walking wizard MCP as the primary rail (agents bail)
- Importing another system's tokens because an eval table looked good

## Triggers

`assistance off`, `ds evals`, `agent tester`, `docs flywheel`, `design system chunks`, `onori evals`, `vqa capture`

## Related

- [[measured-visual-verdicts]] · [[llm-safe-design-system-expressiveness]] · [[agentic-ds-context-model]]
- [[visual-prove-engine]] · [[visual-reference-replication]] · [[ds-source-watch]]
