---
name: visual-qa-usability
description: >
  Usability visual QA specialist. Use this skill for reviewing: task completion
  paths (can users accomplish goals with the design as shown), error prevention
  through visual design, learnability of interface patterns, efficiency of
  interaction flows, cognitive load assessment, visual feedback clarity (does
  the user know what happened?), form usability, input affordances, confirmation
  and undo patterns, progress visibility in multi-step tasks, discoverability
  of features, first-use experience quality, onboarding visual design, help
  and tooltip design, microcopy effectiveness in visual context, destructive
  action safeguards, data density vs. comprehension, and any evaluation of
  whether a visual design enables users to accomplish their goals without
  frustration, confusion, or error. Spoke of lead-visual-qa.
aliases: [visual-qa-usability]
tier: cross-cutting
domain: quality
hub: lead-visual-qa
spec_version: "2.0"
---

# Visual QA — Usability

Usability quality assurance specialist. Evaluates whether visual designs enable
users to accomplish their goals efficiently, without confusion, frustration, or
error. Applies the visual design lens to task-completion quality. Spoke of
`lead-visual-qa`.

---

## Domain Boundary

This skill owns the **task completion and efficiency evaluation lens**.

- **Component aesthetics, spacing, design systems** → `visual-qa-ui-design`
- **Navigation patterns, information architecture** → `visual-qa-ux-design`
- **WCAG compliance, color contrast, target sizing** → `visual-qa-accessibility`
- **Brand craft, typography quality** → `visual-qa-graphic-design`

Usability and UX QA are closely related. UX QA evaluates *how the experience is
structured*; usability QA evaluates *whether users can succeed within that structure*.
A well-organized flow that still produces errors is a usability failure.

### Measurement companion: `visual-qa-toolkit`

This spoke defines the task-completion evaluation lens. For dimensions that
can be measured rather than asserted, invoke `visual-qa-toolkit`:

| This skill evaluates | Toolkit script |
|---|---|
| State differentiation (is hover distinct enough from default to be a feedback signal) | `qa_state_comparison` — pairwise SSIM between state screenshots, flags critical pairs that are too similar |
| Destructive-vs-constructive action visual separation via color drift | `qa_color_extraction` + `qa_color_vision` — measure whether warning colors remain distinct, including under CVD |
| Visual-diff of success vs. error vs. loading state screenshots | `qa_visual_diff` — SSIM + pixel diff |

The most direct fit is `qa_state_comparison`: a common feedback-visibility failure
is a hover or active state that differs too subtly from default. This spoke's
checklist flags the concern qualitatively; the toolkit quantifies it
(SSIM > 0.98 between default and hover = user won't perceive the feedback).

The toolkit accepts paths (folder of state screenshots, config). It has no
built-in knowledge of specific projects. See `visual-qa-toolkit/SKILL.md` for
invocation details.

---

## Task Completion Path Analysis

### The "Can They Do It?" Test

For any primary task in the design, apply this sequence:

1. **Entry**: Is the starting point of the task visually obvious from the landing state?
2. **Path**: Can the user follow the correct sequence of actions using only visual cues?
3. **Completion**: Is the success state visually distinct and unmistakable?
4. **Recovery**: If the user makes a mistake, can they identify and correct it from the design alone?

Flag any step in this sequence where the answer is "only if you already know how."

### Action Discoverability

Features that users never find are features that don't exist. Evaluate:

| Discovery Level | Description | Usability Risk |
|-----------------|-------------|---------------|
| **Visible** | Action is shown in the primary UI, no interaction required | Low |
| **Disclosed** | Action appears after a common interaction (hover, expand, scroll) | Acceptable for secondary actions |
| **Hidden** | Action requires prior knowledge or non-obvious discovery path | High — flag for discoverability |
| **Invisible** | No visual cue the action exists | Critical — effectively removes the feature |

Right-click menus, swipe gestures, long-press targets, and keyboard-only actions
are Invisible-class unless supported by a visible affordance or common platform convention.

---

## Error Prevention

### Slips vs. Mistakes

| Error Type | Description | Visual Design Fix |
|------------|-------------|-----------------|
| **Slip** | User knew the right action but executed incorrectly (mis-tap, typo, wrong button) | Larger targets, spacing between destructive and constructive actions, undo |
| **Mistake** | User had the wrong mental model and intentionally chose wrong | Better labeling, progressive disclosure, contextual help |

### Destructive Action Safeguards

Visual design must make destructive actions harder to perform by accident:

- **Visual separation**: Destructive actions (delete, remove, clear) must be
  visually separated from constructive actions (save, submit, confirm)
- **Color and weight signal**: Destructive actions use a warning color (typically
  red) — but color alone is insufficient (see accessibility QA)
- **Confirmation step**: High-consequence destructive actions require a
  confirmation dialog with clear description of consequences
- **Asymmetric visual weight**: The "Cancel" option should be visually prominent
  relative to the destructive "Confirm Delete" — not treated as equal-weight

Evaluate: Is the destructive action visually contained, labeled clearly, and
difficult to reach accidentally? Or is it adjacent to safe actions and styled
with equal or greater prominence?

### Form Error Prevention

Forms are the most common source of user errors. Evaluate:

- **Inline format guidance**: Does the user know the expected format before making
  a mistake? (Phone: "10 digits, no dashes" visible in placeholder or label)
- **Real-time vs. post-submit validation**: Real-time validation should only fire
  after the user has left a field (onBlur), not during typing — mid-input red
  errors are anxious and counterproductive
- **Error state proximity**: Error messages must appear immediately adjacent to the
  field that caused them, not summarized only at the top of the form
- **Required field marking**: Required fields should be marked before submission, not
  only revealed as errors after a failed submission attempt
- **Input type affordance**: Date fields should look like date inputs; password
  fields should have visibility toggles; file uploads should have drag zone visual cues

---

## Cognitive Load

### Visual Noise

Every element on a screen consumes cognitive capacity. Evaluate:

- **Information priority**: Is everything on the screen necessary for the current
  task, or are secondary features competing for attention?
- **Decorative vs. functional**: Decorative elements (background patterns,
  gradients, illustrations) should never compete with the primary task affordance
- **Density calibration**: Is the information density appropriate for the context?
  (High-density dashboards for experts; low-density task flows for occasional users)

### Chunking

The human working memory holds ~4–7 items. Design should chunk information into
groups of ≤ 5 related items before creating hierarchy.

- Form sections with > 7 fields without visual grouping are overwhelming
- Navigation menus with > 7 items should use grouping, sub-navigation, or search
- Lists > ~10 items need pagination, filtering, or grouping to remain scannable

### Progressive Disclosure

Users should see what they need for the current step, not every option for the
entire workflow:

- Wizard/stepped forms that show all steps at once overwhelm users at the first step
- Settings panels that show advanced options at the same hierarchy as basic options
  create choice paralysis
- Feature panels that show rarely-used and frequently-used actions at equal weight
  train users to scan rather than act

---

## Feedback and System Status (Nielsen's #1 Heuristic)

Every action a user takes should produce visible feedback. Evaluate:

| Action | Expected Feedback | Failure |
|--------|-------------------|---------|
| Button click | Pressed/active state, then result or loading indicator | No visual response — user clicks twice |
| Form submit | Loading state, then success/error | Spinner appears but page never changes state |
| File upload | Progress indicator or confirmation | Upload completes silently — user unsure if it worked |
| Delete | Item removed with brief transition | Item disappears instantly — user unsure if they clicked |
| Search | Results update or "no results" state | Empty results state looks like loading state |
| Navigation | New screen appears or active state updates | Selection occurs but screen doesn't change — dead interaction |

Flag any interaction where the design as shown would leave the user uncertain
whether their action was registered.

### Loading State Quality

Loading states are often designed as afterthoughts. Evaluate:

- **Specificity**: Is the loading state specific to what's loading? (Skeleton screens
  that match the content layout > generic spinner)
- **Duration indication**: For longer operations (> 5 seconds), does the design
  include a progress indicator or time estimate?
- **Actionability**: Can the user navigate away, cancel, or continue using other
  parts of the interface while waiting?
- **Completion clarity**: When loading ends, is the transition to populated state
  clear? (Abrupt snap vs. fade in)

---

## Learnability and First Use

### Onboarding Visual Design

For a user seeing an interface for the first time:

- Is the primary action or purpose of the screen visually obvious without reading?
- Are novel interaction patterns taught at first encounter (tooltip, coach mark, animation)?
- Does the empty state for a new account give the user an actionable path (not just
  an illustration saying "nothing here yet")?

### Consistency and Predictability

- Do the same UI patterns behave the same way across the design?
- If a component has an interaction in one context, does it have the same interaction
  in all contexts?
- If similar actions are placed in different locations on different screens,
  users must re-learn them each time — flag inconsistent placement of recurring controls

---

## Microcopy Usability

Microcopy (button labels, tooltips, form hints, empty states, error messages) is
part of the visual design. Evaluate:

- **Button labels**: Are they specific ("Save changes" vs. "OK") and do they
  describe the outcome ("Submit application" vs. "Continue")?
- **Empty states**: Do they explain why the state is empty and what the user
  should do? Not just "No results found."
- **Error messages**: Do they explain what went wrong and how to fix it? Not
  just "An error occurred."
- **Confirmation dialogs**: Does the confirmation label match the action? ("Delete
  project" on the confirm button, not "Yes")
- **Placeholder text**: Does it describe the format/example, not the label? ("e.g.
  555-1234", not "Phone number" — which disappears when the user types)

---

## QA Checklist — Usability

**Task Completion:**
- [ ] Primary task entry point is visually obvious from the default state
- [ ] Task path is followable using only visual cues (no prior knowledge required)
- [ ] Success state is visually distinct and unmistakable
- [ ] Recovery path from errors is visible in the design

**Error Prevention:**
- [ ] Destructive actions are visually separated from constructive actions
- [ ] Destructive actions use warning color with additional non-color signaling
- [ ] High-consequence actions have a confirmation step
- [ ] Forms provide format guidance before submission (not only via error)
- [ ] Required fields are marked before the user attempts to submit

**Cognitive Load:**
- [ ] Information density is appropriate for context and user expertise
- [ ] Decorative elements are not competing with primary task affordances
- [ ] Forms and lists are chunked into groups of ≤ 5–7 items
- [ ] Advanced or rare options are visually subordinated to primary ones

**Feedback:**
- [ ] Every interactive action produces a visible response
- [ ] Loading states are specific to the loading content
- [ ] Success and error states are visually distinct from each other and from loading
- [ ] Long operations include progress or time-estimate signals

**Learnability:**
- [ ] Novel interaction patterns have visible affordances or teaching moments
- [ ] Empty states provide an actionable next step, not just a placeholder
- [ ] Recurring controls appear in consistent positions across screens
- [ ] Microcopy is specific, outcome-focused, and tells the user what to do

## Related
- hub → [[lead-visual-qa]]
