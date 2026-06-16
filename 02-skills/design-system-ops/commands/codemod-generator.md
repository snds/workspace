---
description: Generate a migration codemod with tests and rollback plan
allowed-tools: Read, Write, Grep, Glob, Bash(find:*), Bash(node:*)
---

Run the codemod-generator skill to produce a migration codemod.

Load the codemod-generator skill from /Users/sean.sands/Library/CloudStorage/GoogleDrive-hello@snds.design/My Drive/Claude Workspace/02-skills/design-system-ops/skills/codemod-generator/SKILL.md and follow its complete workflow.

The user should provide the migration context as an argument: $ARGUMENTS

Before starting, read the reference material specified in the skill's frontmatter from /Users/sean.sands/Library/CloudStorage/GoogleDrive-hello@snds.design/My Drive/Claude Workspace/02-skills/design-system-ops/skills/codemod-generator/references/.

Produce the full codemod package including: jscodeshift transform, test cases, migration runner script, MIGRATION.md, and ROLLBACK.md.
