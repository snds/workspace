# Design System Strategy & Governance

Reference for triage, audits, design decision records, context discovery,
stakeholder communication, and system-level governance. Load this spoke when
working on strategic DS decisions — not when building individual components.

---

## Table of Contents

1. Operating modes
2. Triage framework
3. Design Decision Record (DDR)
4. Context Discovery Protocol
5. Evidence standards
6. Output altitude
7. Figma page documentation structure

---

## 1. Operating Modes

Identify the mode from context. Multiple are often active simultaneously.

**Thinking partner** — Reason through the problem. Surface constraints, goals,
and unknowns. Offer options the user may not have considered. Flag risks. Ask
one clarifying question at a time if the problem is underspecified.

> Signals: open-ended problems, "I'm trying to figure out...", "Is this the
> right approach...", ambiguous or contested design decisions.

**Triage assistant** — Assess current state, classify issues by severity,
scope what's actionable now. Be explicit about what's being deferred and why.

> Signals: audit outputs, long issue lists, time/resource pressure, "I have
> too much to fix and not enough time."

**Artifact generator** — Produce structured outputs: DDRs, component specs,
Figma page documentation, rationale docs, strategy slide content, tabular data.

> Signals: "Document this", "Write this up", "I need something I can share
> or hand off."

---

## 2. Triage Framework

Apply this four-part lens when assessing a component, system area, or problem.

### 2a. Assess current state

Evaluate across four axes:
- **Structure**: Is the component anatomy complete, consistent, logically organized?
- **Tokens**: Are values hardcoded, aliased, or properly semantic (3-tier)?
- **Documentation**: Does usage context, business logic, and decision rationale exist?
- **Accessibility**: Are WCAG 2.1/2.2 AA minimums met? Are interactive patterns
  ARIA-compliant?

### 2b. Classify issues

| Severity | Criteria | Default action |
|---|---|---|
| Critical | Breaks user outcomes; accessibility failures; corrupts downstream system integrity | Fix now or escalate as blocker |
| High | Significant inconsistency; missing docs causing active misuse; semantic token debt | Schedule next cycle |
| Medium | Suboptimal but functional — naming issues, structural gaps, incomplete variants | Backlog with a DDR |
| Low | Polish, idealized restructuring, future-state improvements | Defer openly; document intent |

### 2c. Scope the now

Given actual time and resource constraints: what is the *minimum viable
improvement* that moves toward the goal without creating new debt? State
this explicitly, including what's being deferred.

### 2d. Document the decision

Every significant decision — especially deferred ones — gets a DDR.

---

## 3. Design Decision Record (DDR)

The canonical format for capturing design decisions. Draft in Claude,
finalize in Figma. Adapt length to complexity.

The metadata block is machine-readable by design — `Key: Value` format so
any future connector (Jira, Confluence, Airtable, MCP) can parse it.

```
## [Component or System Area] — [Short decision title]

--- METADATA ---
DDR-ID:          DS-[YYYY]-[###]
Date:            YYYY-MM-DD
Author:          [Name or role]
Status:          Draft | Active | Deferred | Superseded
Altitude:        Tactical | Strategic | Both
Severity:        Critical | High | Medium | Low
Component:       [Figma component name or system area]
Affected-Teams:  [Team names — comma-separated; TBD if unknown]
Jira-Ticket:     [Ticket ID or TBD]
Confluence-Page: [URL or TBD]
Figma-Frame:     [Frame URL or TBD]
Context-Quality: Confirmed | Inferred | Undocumented | Conflicted
--- END METADATA ---

### Context
What problem exists? Constraints — time, resources, org pressure, technical
debt, missing context, undefined business logic. Note source confidence.

### Decision
What are we doing right now, specifically?

### Rationale
Why this approach? Cite sources, precedents, standards. Connect to user
outcomes.

### Tradeoffs Accepted
What are we knowingly sacrificing or deprioritizing?

### Deferred / Backlog
What should happen in a future cycle? Be specific enough to act on later.
Include trigger conditions ("revisit when token system is refactored").

### References
External citations, related Figma frames, component links, prior DDRs.
```

**DDR-ID convention:** `DS-[year]-[zero-padded sequence]`. Per-project or
per-system. This ID is the stable cross-tool reference.

---

## 4. Context Discovery Protocol

When a component, pattern, or decision has unclear or missing context — which
is the default — run this protocol before proceeding.

### Step 1: Ask where to look

Ask one targeted question, not a list. Pick the most likely source:

- "Is there a Confluence page, Jira ticket, or Figma annotation for this?"
- "Who owns this component? A name or Slack handle is enough."
- "Is there a PR, commit message, or Storybook entry explaining intent?"
- "What does the component actually do in production?"

### Step 2: Evaluate what's found

Apply the Documentation Trust Matrix:

| Trust level | Criteria | Use it? |
|---|---|---|
| Confirmed | Matches current behavior; authored by owner; recent (<1 year) | Use as-is; cite it |
| Inferred | Partially matches; known stakeholder; somewhat dated | Use with caveat; note the gap |
| Suspect | Contradicts behavior; unknown author; stale; boilerplate | Cross-reference before using; flag conflict |
| Conflicted | Two sources contradict each other | Document the conflict; decide which to follow and note why |

Mark the DDR's `Context-Quality` with the *highest-doubt* level encountered.

### Step 3: Work with what exists

If no reliable documentation is found:

> "No confirmed documentation found. Decision is based on observed behavior,
> industry standards, and design system best practices. Original intent is
> unknown — see Deferred for recommended follow-up."

This is not a failure state. It is an honest baseline.

### Handling tribal knowledge

Tribal knowledge is valid input. It is not reliable documentation.
- Attribute it: "Per [name/role], the intent was..."
- Note recency: "Conveyed informally; no written record exists."
- Flag the risk: if the person leaves, this decision is unmoored.
- Capture it in the DDR immediately.

---

## 5. Evidence Standards

Cite proactively when a recommendation isn't obvious or overrides existing
patterns. Don't cite widely-accepted fundamentals unless challenged.

**Accessibility**
- WCAG 2.1/2.2: https://www.w3.org/TR/WCAG22/
- ARIA APG: https://www.w3.org/WAI/ARIA/apg/

**UX Research & Patterns**
- Nielsen Norman Group: https://www.nngroup.com/
- Baymard Institute: https://baymard.com/

**Component Pattern References**
- Material Design 3: https://m3.material.io/
- Carbon Design System: https://carbondesignsystem.com/
- Atlassian Design System: https://atlassian.design/
- Radix UI Primitives: https://www.radix-ui.com/primitives

**Token Architecture**
- W3C Design Tokens CG: https://design-tokens.github.io/community-group/format/
- Style Dictionary: https://amzn.github.io/style-dictionary/

**Figma**
- Figma Help Center: https://help.figma.com/
- Variables & Modes: https://help.figma.com/hc/en-us/articles/15339657135383
- Slots: https://help.figma.com/hc/en-us/articles/38231200344599

Lead with relevance: *why* this source supports *this* decision.

---

## 6. Output Altitude

Always be explicit about which altitude the current work operates at.

### Tactical (implementation)

Figma components, variables, styles, tokens, annotations, handoff specs,
component documentation pages, inline usage guidance.

Output formats: DDRs, component spec tables, anatomy descriptions, token
mapping tables, annotation copy, state/variant matrices.

### Strategic (direction)

System vision, principles, roadmaps, stakeholder communication, org alignment,
prioritization frameworks, cross-team guidance.

Output formats: structured slide content, FigJam frameworks, tabular data,
executive summaries, design principles docs.

---

## 7. Figma Page Documentation Structure

When producing documentation destined for a Figma page, structure for direct
transfer. Figma text uses size and weight for hierarchy, not markdown.

```
[Title] — [Component or Area]
Status: Draft | Review | Final    Date: YYYY-MM-DD    Altitude: Tactical | Strategic

─── Context ─────────────────────────────────────────────────────
[Problem statement and constraints — 2–4 sentences]

─── Decision / Guidance ─────────────────────────────────────────
[The actionable content]

─── Rationale ───────────────────────────────────────────────────
[The why — with citations where relevant]

─── Tradeoffs & Deferred ────────────────────────────────────────
[Honest accounting of what's not done and why]

─── References ──────────────────────────────────────────────────
[Related frames, external links, prior DDRs]
```
