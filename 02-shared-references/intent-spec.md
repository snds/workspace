---
title: Living intent spec
spec_version: "1.0"
status: canonical
---

# Living intent spec

The coordination artifact for [[17-intent-coordination-operating-model]]. Copy
[00-bootstrap/templates/intent-spec.md](../00-bootstrap/templates/intent-spec.md) into the
**owning** project or repo (`docs/INTENT.md` or `docs/INTENT-<wave>.md`). Do not put the body
in a Linear issue ([[open-agent-engine]] stays pointer-shaped).

The spec is **living**: agents update checklist status, wave notes, and the changelog when
reality changes. Designed intent (outcome + northstar) changes only with Sean's approval.

## Required sections

1. **Outcome** — what should exist, and where (no use of *done* / *complete* as the definition).
2. **Context profile** + **lane** (if movement is tracked).
3. **Northstar** — Figma, `NORTHSTAR.md`, contract, or quoted user intent. Pointers, not a paste of the whole file.
4. **Fidelity / acceptance checklist** — checkable items; name the measurement (`vqa prove`, test command, validator, review).
5. **Task graph** — id, role (`coordinator` / `implementor` / `verifier`), `depends_on`, isolation, specialist skill.
6. **Waves** — what may run in parallel; what is held.
7. **Evidence** — per task, what the verifier will read. Author chat is never sufficient for consequential work.
8. **Open decisions / blocked-on**
9. **Changelog** — date, who, what changed in the plan.

## Filename and placement

| Work lives in… | Spec lives in… |
|---|---|
| `07-projects/<id>/` | that folder, usually `docs/INTENT.md` |
| An external git repo | that repo (never copy employer substance into this vault) |
| Workspace-brain itself | `07-projects/19-workspace-brain/docs/` |

Live handoff **points at** the spec; it does not duplicate it.

## Related

- L1: [[17-intent-coordination-operating-model]]
- L2: [[intent-coordination]]
- Verifier: [[mission-fit]] · [[06-qa-operating-model]]
- Movement: [[open-agent-engine]]
