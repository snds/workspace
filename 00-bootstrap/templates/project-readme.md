---
title: <% tp.file.folder() %>
type: project
status: Planning
lifecycle: discover
triggers: []
frameworks: [aesthetic-lens, ui-ux-operational, collaboration-critique, research-evidence, last-mile-craft]
created: <% tp.date.now("YYYY-MM-DD") %>
---

# <% tp.file.folder() %>

## Summary
One-line description of the project.

## Status
Planning / Active / Paused / Archived

## Project intent
<!-- Vault-only project (no repo): the same grammar as PROJECT.md (00-bootstrap/templates/project-intent.md; 02-shared-references/intent-spec.md), with `lifecycle:` in this README's frontmatter. At most 40 lines. When a repo appears, move this block into the repo's PROJECT.md and leave one line here: `Project intent: <owner>/<repo>:PROJECT.md`. Lint: python3 09-tools/intent-run.py lint --all -->

### Problem & audience

[HUMAN: the problem in one or two sentences, and who has it.]

### Knowns & unknowns

| claim | label | tier | evidence | decision rule |
|---|---|---|---|---|
| [HUMAN: a claim this project rests on] | unknown | T5 | [HUMAN: what would count as evidence] | [HUMAN: what we do if it says yes, and if it says no] |

### Out of scope & later

[HUMAN: what this project will not do now, and what waits for later.]

## Trigger words
<!-- Words that route Claude's attention to this project. Edit .claude/hooks/dispatcher.py TRIGGER_WORDS to wire them up. -->
- 

## Frameworks active
- [[01-frameworks/01-aesthetic-lens]]
- [[01-frameworks/02-ui-ux-operational-framework]]
- [[01-frameworks/03-collaboration-and-critique-framework]]
- [[01-frameworks/04-research-and-evidence-framework]]
- [[01-frameworks/05-last-mile-craft-framework]]

## Links
- [[SESSION-STATE]] — operational state
- [[06-context/project-context|Project context]] — ecosystem registration

## Notes folder
See `notes/` for freeform captures.
