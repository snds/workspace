---
title: Principles & Our Approach to AI
section: Introduction
source: https://courses.bradfrost.com/courses/take/ai-design-systems-course/lessons/72577755-principles-our-approach-to-ai
duration: ~13m25s
status: noted
as-of: 2026-09-10
---

# Principles & Our Approach to AI

The load-bearing intro lesson. They ask teams to adopt (or argue with) these as shared values before reaching for tools.

## The principles

| Principle | Their claim | Workspace analog |
|---|---|---|
| **Humanity** | Tech should elevate people, not replace them. Automate drudgery and means-to-an-end, not creative work. Honor talent and finite time. | Agents do the grind; Sean keeps taste, contracts, and calls. |
| **Safety** | Don't cause harm. Named: environmental cost, stolen training IP, baked-in bias, unknown externalities. | Threat-model-before-controls; don't treat a demo as consequence-free. |
| **Intentionality** | Autopilot is the failure mode. Deliberate choices at every step, not "whatever the model threw." | Context-is-king; no silent degradation. |
| **Responsibility** | Humans own the output. Guardrails, review, accountability. No shipping slop. | QA operating model + Proofboard. The agent does not get to declare done. |
| **Nuance** | Reject binary hype. Quote Melvin Kranzberg: technology is neither good nor bad, nor neutral. *Your* context picks the approach. | ds-advisor: pragmatic under constraints; name tradeoffs. |
| **Quality** | AI can emit a site in seconds. **"Is it good?" is the defining question of the era.** DS is how you get reliability and predictability at scale. Humans remain the taste-makers. | Last-Mile Craft + native visual eval. Quality is not "it compiled." |
| **Accessibility** | Two senses: (1) UI accessible to any person using the product; (2) **humans stay in the driver's seat** — control what goes into the model, and modify/extend/fix what comes out. | a11y as non-deferrable; human-oversight on agent workflows. |
| **Foundations** | **Stated as the crux of the whole course.** Marry generative expansion to sturdy org DS foundations. Connected foundations + feedback loops: product context strengthens the system, then ships back out. | Tokens, contracts, component schemas. An untransformed Figma dump is testimony, not a foundation. |
| **Context** | Without *persistent* context, AI is a goldfish. TJ's **context-based design system workflow**: each lifecycle stage inherits the previous; feedback loops also run backward. | This workspace. SESSION-STATE, skills, knowledge vault. Watch Chapter 3 Station 6. |
| **Collaboration** | Means of production got faster, so work can be omnidirectional across silos instead of one-way handoffs and naming-convention meetings. Translate across roles/languages. | Design/dev handoff; don't let MCP demos collapse back to designer-solo. |
| **Curiosity** | Curious *and* skeptical. Not "this is how we've always done it." Explorer mode; get comfortable being uncomfortable. | Learner domains stay learner; don't freeze the stack. |
| **Multiplicity** | There is not one right tool or workflow. Tools talk to each other. Org context + judgment pick the job's stack. | Portable-first; no vendor-privileged adapter. |
| **Practicality** | Hype demos are cheap. Start from where the org *is*. Tiered: dip a toe → advanced. Born from large-org work, not theory. | Pragmatic-over-perfect. |
| **Durability** | Landscape moves; foundations still matter. Operate in the current toolscape *and* build culture/process/architecture that outlasts a hype cycle. | Git-native workspace, contracts, token grain — the part that should survive Cursor/Claude/Figma MCP churn. |

## What they want you to do with this list

Argue it with your team. What hits, what's missing, what you care less about. Shared principles are how you navigate a fickle tool market.

## For Sean

This is the course's constitution. Later chapters are implementations. When a demo (Story UI, Figma Console MCP, generative UI) conflicts with **foundations / quality / driver's-seat accessibility**, the principle wins — they said so here.

Closest collision with existing doctrine: **Foundations + Context + Quality**. We already run that stack. The new object to steal is TJ's *context-based design system workflow* (inheritance across lifecycle stages + reverse feedback). Don't graduate it to `08-knowledge/` until Station 6 and the Eddie demos show the mechanism, not just the slogan.

Second collision: **Accessibility as process-control**, not only WCAG. That's the same idea as "the LLM boundary trap" (verification stops where an agent smooths the artifact). Keep humans able to patch outputs.
