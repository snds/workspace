# Design Critique & Evaluation

Structured frameworks for evaluating design quality — from quick visual
reviews to formal heuristic evaluations — with actionable mitigation paths
for every issue identified. Load this spoke when reviewing a screen, flow,
component, or system for quality, consistency, and user-centricity.

This spoke connects visual design theory (the "why") to triage and governance
(the "what to do about it") through a structured evaluation layer.

---

## Table of Contents

1. Evaluation modes — choosing the right depth
2. Visual design review — the fast pass
3. Heuristic evaluation — the structured pass
4. Design system compliance review — the system pass
5. Design-to-code alignment — the handoff pass
6. Severity classification and mitigation
7. Critique output formats
8. Escalation to deep-dive audits

---

## 1. Evaluation Modes

Not every review requires the same depth. Match the evaluation mode to the
context and available time.

| Mode | When to use | Time investment | Output |
|---|---|---|---|
| Visual design review | Quick gut-check, async feedback, PR review | 10–15 min | Annotated notes, inline comments |
| Heuristic evaluation | Pre-launch review, redesign assessment, stakeholder presentation | 30–60 min | Structured findings with severity |
| DS compliance review | Component authoring, library QA, system audit | 45–90 min | Compliance matrix with gaps |
| Design-to-code check | Post-implementation, pre-release, regression | 30–60 min | Discrepancy report by dimension |

Select the mode based on what's being evaluated and the decision it needs to
inform. Multiple modes can run on the same artifact — a visual review catches
what feels wrong, a heuristic evaluation explains why, and a compliance review
identifies systemic gaps.

---

## 2. Visual Design Review — The Fast Pass

A rapid, perception-first evaluation. Uses the visual design theory principles
(see `visual-design-theory.md`) as the diagnostic lens. This is the review
a senior designer does instinctively — the goal is to make it structured and
repeatable.

### The seven-question scan

For any screen, component, or flow, ask these in order:

**1. Hierarchy** — Can I identify the primary, secondary, and tertiary content
within 3 seconds of looking? If everything competes for attention, hierarchy
has failed. Check: size contrast between levels, weight differentiation,
color/value contrast, whitespace distribution.

**2. Grouping** — Are related elements visually grouped? Are unrelated elements
visually separated? Check: proximity relationships (Gestalt proximity), shared
visual treatment (Gestalt similarity), container/boundary usage (Gestalt
common region). The most common failure: label-to-field spacing equals
field-to-field spacing, making the form read as a flat list instead of
grouped pairs.

**3. Alignment** — Do elements share consistent edges? Does the eye flow
smoothly or jump? Check: left-edge consistency across form labels and inputs,
horizontal alignment of action buttons, vertical rhythm across sections.
Misalignment by 1–2px is invisible to users but compounds across a screen
into a general feeling of "something is off."

**4. Contrast** — Can all text be read comfortably against its background?
Do interactive elements stand out from static content? Check: APCA Lc values
for all text/background pairs (Lc 75+ for body, Lc 60+ for UI text), visual
distinction between interactive and non-interactive elements, sufficient
differentiation between primary and secondary actions.

**5. Consistency** — Does this screen follow the same patterns as the rest
of the product? Check: component usage matches library (not detached or
overridden), spacing values align with the token scale, typography matches
the text style system, color usage matches semantic token intent.

**6. Density** — Is the information density appropriate for the context and
the user? Enterprise/data-heavy UIs can tolerate higher density, but every
element should still have breathing room. Check: no elements touching or
overlapping, minimum 8px between unrelated interactive targets, sufficient
padding inside containers, scrollable regions don't hide critical content
above the fold.

**7. Completeness** — Are all states represented? Check: empty states,
loading states, error states, edge cases (long text, missing images,
zero results, single item vs. many). The most commonly missing states:
empty state and error state. If a designer hasn't shown what happens when
there's no data, the developer will guess — and the guess will be wrong.

### Flagging issues

For each issue identified in the visual review:
- Name the principle violated (hierarchy, grouping, alignment, etc.)
- Describe what you see: "These two buttons compete because they're both
  high-contrast primary blue on the same row"
- Propose a specific fix, not just "fix the hierarchy": "Make the secondary
  action a ghost button to reduce its visual weight"

---

## 3. Heuristic Evaluation — The Structured Pass

A systematic inspection against established usability principles. Based on
Nielsen's 10 Usability Heuristics, adapted for modern design system context.

### The 10 heuristics (DS-adapted)

**H1. Visibility of system status**
Does the interface keep the user informed? Loading indicators, progress bars,
save confirmations, error feedback, state changes.
*DS lens:* Do components have a loading state? Does the system include a
toast/notification component for status feedback?

**H2. Match between system and the real world**
Does the interface use language and concepts familiar to the user? Icons that
match real-world metaphors, terminology from the user's domain, logical
information ordering.
*DS lens:* Does the icon library cover the domain's metaphors? Are labels
using user language or internal jargon?

**H3. User control and freedom**
Can users undo, redo, escape, and navigate freely? Back navigation, cancel
buttons, undo for destructive actions, clear paths out of modal flows.
*DS lens:* Do modal/dialog components have consistent close/cancel patterns?
Is there a standard undo pattern in the system?

**H4. Consistency and standards**
Does the interface follow platform conventions and internal patterns? Same
action looks the same everywhere. Same icon means the same thing.
*DS lens:* This is the core DS value proposition. Check: are components used
consistently? Are there detached or locally modified instances? Do similar
screens use the same patterns?

**H5. Error prevention**
Does the design prevent errors before they happen? Confirmation dialogs for
destructive actions, input validation as the user types, disabled states
when an action isn't available.
*DS lens:* Do form components include inline validation? Are destructive
action buttons visually distinct (semantic color: danger)?

**H6. Recognition rather than recall**
Can users see their options rather than remembering them? Visible navigation,
autocomplete, recently used items, contextual help.
*DS lens:* Does the system include search/filter components? Are breadcrumbs
available for deep navigation hierarchies?

**H7. Flexibility and efficiency of use**
Can experienced users work faster? Keyboard shortcuts, bulk actions, saved
preferences, customizable views.
*DS lens:* Do data table components support keyboard navigation, bulk select,
and customizable columns? Are there power-user affordances alongside
beginner-friendly defaults?

**H8. Aesthetic and minimalist design**
Does every element earn its place? No decorative clutter, no redundant labels,
no competing visual elements. Every piece of information competes with every
other piece — more elements = less attention per element.
*DS lens:* Are components minimal in their default state? Can optional
elements be hidden via boolean properties?

**H9. Help users recognize, diagnose, and recover from errors**
Are error messages specific, human-readable, and actionable? "Something went
wrong" is a failure. "Your password must be at least 8 characters" is useful.
*DS lens:* Do form components support error messages with specific content?
Is there a standard error message pattern (not just red text)?

**H10. Help and documentation**
Is contextual help available when needed? Tooltips, inline guidance, help
links, onboarding flows.
*DS lens:* Does the system include tooltip, popover, and contextual help
components? Are they used consistently at decision points?

### Conducting the evaluation

1. Define scope: which screens, flows, or components are being evaluated.
2. Walk through each screen against all 10 heuristics.
3. For each violation, document: which heuristic, what the issue is, severity
   (see section 6), and a screenshot or frame reference.
4. Compile findings. Deduplicate across screens (the same missing loading
   state across 5 screens is one systemic finding, not five).
5. Prioritize by severity and frequency.

---

## 4. Design System Compliance Review — The System Pass

Evaluates whether a design correctly uses the design system — the right
components, the right tokens, the right patterns.

### Compliance checklist

**Component usage:**
- [ ] All UI elements use library components (no detached instances, no
      locally built alternatives to existing components)
- [ ] Components are used at the correct variant (size, emphasis, state)
- [ ] No hidden layers manually toggled — boolean properties used instead
- [ ] Slots used for flexible content, not detach-and-customize
- [ ] Instance swap properties use preferred instances from the library

**Token compliance:**
- [ ] All colors reference semantic color variables (no hardcoded hex)
- [ ] All spacing uses spacing scale tokens (no arbitrary pixel values)
- [ ] All typography uses text styles or font-size variables (no raw values)
- [ ] All corner radii use radius tokens
- [ ] All shadows use effect styles with variable bindings

**Pattern compliance:**
- [ ] Layout follows the established grid/column system
- [ ] Form patterns match the system's form component architecture
- [ ] Navigation follows the system's nav component and hierarchy
- [ ] Data display uses the system's table/list/card patterns
- [ ] Responsive behavior follows documented breakpoint conventions

**State coverage:**
- [ ] All interactive elements show all required states (default, hover,
      focus, active, disabled where applicable)
- [ ] Empty states are designed, not left as blank containers
- [ ] Loading states are designed with skeleton or spinner patterns
- [ ] Error states are designed with the system's error pattern

**Accessibility baseline:**
- [ ] All text/background pairs meet APCA Lc 60+ (UI text) or Lc 75+ (body)
- [ ] Touch targets meet minimum 44×44px (mobile) or 32×32px (desktop)
- [ ] Focus indicators are visible on all interactive elements
- [ ] Color is not the only indicator of state (supplement with icon, text,
      or pattern)
- [ ] Heading hierarchy is semantic (H1 → H2 → H3, not skipped)

### Running Check Designs

Use Figma's Check Designs linter as an automated first pass before the manual
review. It catches hardcoded colors, spacing, and typography that should
reference variables. Address all Check Designs findings before starting the
manual compliance review — it eliminates the low-hanging fruit so the human
review can focus on judgment calls.

---

## 5. Design-to-Code Alignment — The Handoff Pass

Evaluates whether the implemented code matches the design specification.
For a comprehensive, tool-integrated version of this evaluation, use the
`design-to-code-check` skill from the design-system-ops pack if available.

### Quick alignment dimensions

**Dimension 1: Spacing and layout**
Compare padding, margins, gaps, and alignment between design and
implementation. Use browser DevTools overlay against the Figma spec.
Common failures: auto layout gap translated as margin instead of gap,
padding values rounded to non-token values, responsive breakpoint
behavior divergent.

**Dimension 2: Color and theming**
Compare all color values between design and implementation. Check that
semantic tokens are consumed (not hardcoded hex values that happen to
match today). Test dark mode / theme switching — this is where token
architecture failures surface.

**Dimension 3: Typography**
Compare font family, size, weight, line-height, letter-spacing. Check
that text styles are applied via the token system. Common failure: line-height
specified as a pixel value in code but as a multiplier in design — the
values match at one font size but diverge at others.

**Dimension 4: Interaction and behavior**
Compare interactive states (hover, focus, active, disabled), transitions,
animations, and keyboard behavior. This dimension is where design
specifications are most commonly incomplete — "the hover state" may be
defined visually but the transition duration and easing may not be.

**Dimension 5: Responsive behavior**
Compare behavior at each defined breakpoint. Check that the same components
are used across breakpoints (not rebuilt locally for mobile). Common failure:
desktop component replaced with a completely different mobile implementation
instead of the same component responding to viewport changes.

### Classifying discrepancies

Each discrepancy is one of two types:
- **Implementation error:** The developer built something different from
  what was specified. Fix is in the code.
- **Specification gap:** The design didn't define this behavior completely
  enough. Fix is in the design — document the missing spec, update the
  component documentation, and correct the implementation.

The distinction matters because specification gaps are systemic — they'll
recur on every future handoff unless the spec is improved.

---

## 6. Severity Classification and Mitigation

Every finding from any evaluation mode gets a severity rating and a specific
mitigation path. This uses the same severity framework as the triage system
in `ds-strategy.md`, adapted for design critique.

### Severity ratings

| Severity | Criteria | Mitigation timeline |
|---|---|---|
| 🔴 Critical | Breaks user outcomes. Accessibility failure (below WCAG AA / APCA Lc minimums). Users cannot complete the task. Data loss risk. | Fix before release. Block deployment. |
| 🟠 High | Significant usability problem. Users struggle or abandon task. Inconsistency that causes confusion. Missing critical state (error, empty). | Fix in current sprint. |
| 🟡 Medium | Suboptimal but functional. Minor inconsistency, non-ideal hierarchy, missing secondary state. Users succeed but experience is degraded. | Schedule in next sprint. Document in DDR if deferred. |
| ⚪ Low | Polish. Optical misalignment, minor spacing inconsistency, nice-to-have enhancement. Users unaffected. | Backlog. Address during related work. |

### Mitigation patterns

For each severity, a standard set of response actions:

**Critical:**
1. Document the issue with screenshot and principle violated.
2. Identify the root cause: missing component? Wrong token? Spec gap?
3. Implement the fix immediately.
4. If the fix requires a system change (new component, new token), create
   a DDR and escalate per `ds-strategy.md`.
5. Verify the fix in context (not just the component in isolation).

**High:**
1. Document with screenshot and principle.
2. Propose a specific fix (not "make it better" — "change the secondary
   CTA from filled to ghost variant to resolve hierarchy competition").
3. Add to current sprint backlog with the finding as acceptance criteria.
4. If the issue is systemic (appears across multiple screens), escalate
   to a DS compliance review.

**Medium:**
1. Document with screenshot and principle.
2. Propose a fix.
3. If the fix is a 5-minute change, do it now.
4. If it requires significant work, create a DDR documenting the issue,
   the proposed fix, and the deferral rationale.

**Low:**
1. Note it. Don't let it block progress.
2. Address when working on the same area for another reason.

---

## 7. Critique Output Formats

### Inline annotation (for async review)

For Figma-based reviews, use a standard annotation format:

```
[SEVERITY] [HEURISTIC or PRINCIPLE]
What: [Description of the issue]
Why: [Which principle is violated and why it matters]
Fix: [Specific proposed mitigation]
```

Example:
```
[🟠 HIGH] [H4: Consistency]
What: This data table uses a custom sort icon that doesn't match
the system's sort icon pattern used in every other table.
Why: Inconsistent iconography breaks recognition (H6) — users
must relearn the sort affordance on this screen.
Fix: Replace with the system DataTable sort icon component.
```

### Evaluation summary (for structured review)

Use for heuristic evaluations and compliance reviews:

```
## Design Evaluation — [Screen/Component/Flow name]
Date: YYYY-MM-DD
Evaluator: [name]
Mode: [Visual review / Heuristic evaluation / DS compliance / Design-to-code]

### Findings summary
🔴 Critical: [count]
🟠 High: [count]
🟡 Medium: [count]
⚪ Low: [count]

### Top findings
[Top 3–5 findings with the highest impact, each with severity, description,
and proposed mitigation]

### Full findings
[All findings in a table: ID, severity, principle/heuristic, description,
proposed fix, affected component/screen]

### Systemic observations
[Patterns that appear across multiple findings — e.g., "Loading states are
missing across 4 of 6 screens reviewed" — these are system-level gaps,
not individual screen issues]
```

---

## 8. Escalation to Deep-Dive Audits

The evaluation modes in this spoke are designed for regular design work.
When findings reveal systemic issues, escalate to a focused audit:

| Finding pattern | Escalate to | Notes |
|---|---|---|
| Multiple components with inconsistent APIs, naming, or structure | Component audit (design-system-ops) | Full 4-dimension inventory + dependency graph |
| Hardcoded values appearing despite tokens existing | Token audit (design-system-ops) | Token coverage and compliance scan |
| Variable collections with inconsistent naming or scoping | Figma variable audit (design-system-ops) | Collection structure and mode review |
| Naming conventions divergent across the library | Naming audit (design-system-ops) | System-wide naming consistency pass |
| Implementation doesn't match spec across multiple components | Design-to-code check (design-system-ops) | Structured 7-dimension discrepancy report |
| Design decisions undocumented, rationale lost | DDR process (ds-strategy.md) | Document and prevent future loss |

These deep-dive audit skills from the design-system-ops pack are available
in the Drive workspace at `02-skills/design-system-ops/skills/`. Load the
specific audit skill when escalating — this spoke provides the triage and
routing; the audit skills provide the depth.
