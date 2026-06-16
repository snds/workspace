---
name: ux-interaction-design
description: >
  Complex workflow design, form patterns, error state design, and interaction detail
  for enterprise SaaS. Use this skill when working on: multi-step forms and wizards,
  task decomposition and workflow mapping, save state design (auto-save vs. draft vs.
  explicit), undo/redo patterns, bulk editing interactions, inline validation vs.
  on-submit validation, dependent field logic (show/hide vs. enable/disable), error
  state taxonomy and error message writing, edge case inventory (empty, null, loading,
  error, partial states), micro-interactions and state change feedback, optimistic UI
  decisions, transition design, and any interaction pattern where the question is
  "what should happen when the user does X?" Also trigger on: "how should this form
  work", "what happens when the operation fails", "should I use a wizard or not",
  "how do I handle N selected items", "what's the feedback for this action", or any
  question about the detailed behavioral design of an interface.
aliases: [ux-interaction-design]
tier: spoke
domain: design
hub: lead-ux-designer
prerequisites: [lead-ux-designer]
spec_version: "2.0"
---

# UX — Interaction Design

Spoke skill in the `lead-ux-designer` network. Owns workflow design, form patterns,
error states, edge cases, and interaction detail for enterprise SaaS.

Does not own: navigation structure and IA (→ `ux-information-architecture`), loading
state design (→ `ux-performance-perception`), component variant coverage (→ `ux-design-systems`),
accessibility keyboard patterns (→ `ux-accessibility`). Those live in their respective spokes.
This spoke owns the behavioral logic of features once the user is inside a task or workflow.

---

## Workflow Design for Complex Enterprise Tasks

### Task analysis before wireframes

Complex enterprise workflows are not obvious from requirements. Before designing screens,
decompose the task:

1. **Atomic actions**: what are the indivisible actions the user takes? (select a value,
   enter text, attach a file, trigger a calculation)
2. **Decision points**: where does the workflow branch? What does the user decide, and
   what decides it for them?
3. **Required data**: what information must be present or entered before the next step
   is possible?
4. **Dependencies**: which fields or actions depend on the state of other fields or
   prior actions?
5. **Permissions**: which steps are gated by role? Which actions require approval?

This map is the design input. A wireframe produced without it is guessing.

### Progressive workflow

Present only what's needed for the current step. In a workflow with 40 fields, the
user completing Step 1 does not need to see Step 3's fields. This is not about hiding
complexity — it is about reducing the cognitive load of determining what's relevant now.

Progressive workflow is not the same as a wizard. A wizard forces a specific step
sequence. Progressive workflow can be non-linear: show the relevant fields for what
the user is currently doing, regardless of where in the sequence they are.

### Save state design

Each save model has different risk profiles and user expectations. Choose explicitly.

| Save Model | When to Use | Risk | User Expectation |
|------------|-------------|------|-----------------|
| **Auto-save** | Long-form content, draft-like workflows, frequent edits | User may not know state is saved; silent failures are invisible | "It always saves" — user becomes dependent |
| **Explicit save** | Actions with downstream consequences, workflows with approval steps, high-stakes data entry | User must remember to save; frustration if lost on navigation | "I control when it saves" |
| **Draft / Publish** | Content that has a live state and a staging state | Complexity in explaining draft vs. live; stale draft confusion | "I can edit without affecting what's live" |
| **Optimistic / Immediate** | Simple toggles, low-stakes changes, reversible actions | Error rollback must be designed; silent rollbacks confuse | "It happened immediately" |

Auto-save and explicit save are not interchangeable. Auto-save in a workflow where
partial records are invalid creates data quality problems. Explicit save in a 40-field
form is a risk if the user navigates away.

Hybrid: auto-save to draft, explicit publish. This is the correct model for workflows
where partial data is a real risk but "remember to save" is too high a burden.

### Undo/redo

Enterprise users make mistakes at scale. A user who bulk-selects 200 records and
applies the wrong change needs undo, not a confirmation dialog before every action.

Undo is often a better pattern than confirmation dialogs for reversible actions.
"Item deleted. Undo?" beats "Are you sure you want to delete this item? This cannot
be undone." (The "cannot be undone" caveat is the problem — if it truly cannot be
undone, either make it undoable or make the confirmation modal harder to dismiss.)

Undo implementation constraints: the backend must support an undo operation (or a
logical reversal). This is a `be-data-modeling` and `fe-state-management` conversation —
surface it early.

### Wizard patterns: when and when not

Use a wizard when:
- Steps are genuinely sequential (completing step N is a prerequisite for step N+1)
- Steps are irreversible (completing step N commits data that step N+1 depends on)
- The overall flow is bounded (4–7 steps, not 15)
- The user has enough information to complete each step without returning to previous steps

Do not use a wizard when:
- The sequence is artificial — the user could fill these fields in any order
- The user frequently needs to go back and change earlier answers
- The overall workflow is too long (>7 steps becomes "wizard fatigue")
- The data is co-dependent in complex ways (circular dependency between steps)

A wizard that the user constantly needs to navigate back through is not a wizard —
it's a multi-page form with bad navigation.

---

## Form Design for Enterprise Data Entry

### Input sizing signals meaning

Input width should correspond to the expected content length. A postal code field
should be narrow. A notes field should be wide. A phone number field should be medium.
Using full-width inputs for everything removes an important signal: when all inputs
look the same, the user has no visual cue about what scale of input is expected.

This is not just aesthetics — it affects completion rate. Users confronted with a
full-width field for a 5-character code often second-guess themselves.

### Field grouping

Related fields belong close together. Unrelated fields separated by space or dividers.
Section dividers with labels (not arbitrary horizontal rules) provide the structure
that lets users navigate a long form quickly.

Section labels should be nouns or noun phrases that describe the content, not action
verbs. "Product Details" yes. "Enter Product Details" no — the user knows they're
entering data.

### Inline validation vs. on-submit validation

| Validation Type | When to Use |
|----------------|-------------|
| **Inline / real-time** | Format validation (email syntax, phone number format, required field)  — validate on blur, not on every keystroke |
| **Inline / on-blur** | Field-level business rules that can be validated without submitting (character limits, date range checks) |
| **On-submit** | Cross-field validation (field A must be less than field B), server-side business rules, anything that requires a round-trip |

Never show inline errors on keypress — it triggers errors before the user has finished
typing and creates anxiety without actionable information. Validate on blur (when the
user leaves the field) for format errors. Validate on submit for everything else.

Always show both inline errors (adjacent to the field) and a summary at the top for
complex forms. Users who Tab through a form without looking at each field will miss
inline-only errors.

### Dependent fields: show/hide vs. enable/disable

| Pattern | Behavior | Pro | Con |
|---------|----------|-----|-----|
| **Show/Hide** | Dependent field only appears when the trigger condition is met | Cleaner UI; no disabled fields to explain | Causes layout shift; user can't see what's coming |
| **Enable/Disable** | Dependent field always visible, enabled only when condition is met | Stable layout; user can see what fields exist | Requires explaining why fields are disabled; more cognitive load |

Default to **enable/disable** when the dependent field is critical or the user needs
to see it exists before triggering it. Default to **show/hide** when the dependent
field is genuinely irrelevant and adds noise.

Never use show/hide for fields the user has already filled in — clearing a condition
should not silently wipe entered data.

### Multi-value inputs

Tags, chips, multi-select dropdowns — the interaction model must be explicit:
- How do you add a value? (type and press Enter, click from a dropdown, both)
- How do you remove a value? (X button, backspace to remove last item, click to deselect)
- What's the maximum? (if there is one, show it before the user hits it)
- What happens to duplicates? (block them? show a warning? allow them?)

Combobox multi-select (type to filter + click to add): requires the list to update
as the user types and the selected items to be clearly distinguished from unselected.
The selected items should remain visible whether they match the current filter or not.

### Bulk editing

When acting on N selected records:
1. Show a clear count of what's selected ("14 items selected")
2. Surface only the actions that apply to all selected items (not per-record actions)
3. For destructive bulk actions, confirm the scope explicitly ("Delete 14 items?")
4. Partial success handling: some operations will fail for some records — the UI
   must show what succeeded and what failed, not collapse to a single outcome

---

## Error State Design

### Error taxonomy

| Type | Cause | Recovery | Design Response |
|------|-------|----------|----------------|
| **Validation error** | User input doesn't meet constraints | User fixes it | Inline + summary; red field highlight + clear message |
| **Business rule error** | Input is valid format but violates a rule | User must understand the rule | Explain the rule in the error; don't just say "invalid" |
| **System error** | Unexpected server failure, network issue | Retry or contact support | Clear message; retry option; don't blame the user |
| **Permission error** | User doesn't have access | Contact admin or request access | Explain what's restricted and how to proceed |
| **Dependency error** | Operation can't complete because of a related record's state | Resolve the dependency first | Explain what needs to change and where |

### Error message writing

Every error message must answer three questions:
1. **What happened?** Be specific — "The SKU field already exists" not "Duplicate value"
2. **Why did it happen?** Explain the constraint — "SKU values must be unique within a product line"
3. **What should the user do?** Give a clear next action — "Change the SKU or deactivate the existing product with this SKU"

"This field is required" fails all three. It describes a result, not a cause, and
gives no action. "Required" as a label on the field already handles the constraint
communication — the error message needs to do more.

Anti-pattern: technical error messages exposed to end users. "500 Internal Server Error"
is not a user-facing message. "We couldn't save your changes. The server returned an
unexpected error. Please try again, or contact support if this continues." is.

### Partial success states

Bulk operations where some items fail are not binary success or failure. The UI must:
1. Confirm what succeeded (N of M items)
2. Identify what failed and why (list the failed items with error context)
3. Offer a recovery path (retry the failures, download a failure report, resolve each manually)

Never collapse a partial success to a failure state ("This operation failed") or
to a success state ("Done") when 20% of items silently failed.

---

## Micro-interactions and Feedback

### The 100ms rule

Every user action needs feedback within 100ms — even if the feedback is just a
loading indicator. Actions that appear to do nothing will be clicked again. Double-
submit protection is not sufficient if the user doesn't know the first submit was received.

Response time design:
- < 100ms: no feedback needed — feels instantaneous
- 100ms–1s: visual feedback on the trigger (button loading state, spinner in form)
- 1s–5s: inline progress indication; disable the trigger
- > 5s: full loading state or background job pattern

### Optimistic UI

Optimistic UI shows success before the server confirms. When to use it and when not to:

**Appropriate for:**
- Toggle actions (like, follow, bookmark) — low stakes, easily reversed
- Adding items to a list — failure is rare; rollback is visible and non-destructive
- Reordering — the user's intent is clear and the cost of reverting is low

**Not appropriate for:**
- Financial transactions — a false success followed by rollback destroys trust
- Deletions — users act on the assumption the deletion succeeded
- Actions with downstream side effects (sending an email, triggering a workflow)
- Any operation where the user will make other decisions based on the result

Optimistic UI without rollback design is incomplete. The error state of an optimistic
action must be explicitly designed: "Failed to save, click to retry" with the
previously-showing success state reverted.

### Transition design

Movement should convey relationship, not just decoration:
- **Slide**: navigation between hierarchical levels (drilling in or backing out)
- **Fade**: modal and dialog appear/disappear; content replacement that isn't spatial
- **Scale / expand**: popover, dropdown, tooltip — anchored to a trigger point
- **Progress**: step-by-step workflows; the animation direction should match the flow direction

Transitions should be perceptible but fast (150–300ms for most). Long transitions
punish repeat users. All transitions must have a `prefers-reduced-motion` fallback
(→ `ux-accessibility` for the reduced-motion design requirement).

---

## Edge Case Inventory

A feature design is incomplete without all five states documented:

| State | Description | Design requirement |
|-------|-------------|-------------------|
| **Empty** | No data exists yet | Explain what's empty, why, and how to populate it |
| **Null / blank** | Data exists but the value is absent | Distinguish from "zero" and "not applicable" — each needs a different visual treatment |
| **Loading** | Data is in flight | Match loading treatment to wait type (→ `ux-performance-perception`) |
| **Error** | Fetch failed or operation failed | Inline + actionable; don't surface technical details |
| **Partial** | Some data loaded, some failed or pending | Show what you have; indicate what's missing; allow retry |

The partial state is the most commonly missed. In enterprise apps with complex data
models, some fields may come from different API calls with different latencies. A
record that loads its metadata quickly but its computed fields slowly needs a partial
state design — not a single loading state that blocks everything.

---

## Cross-Links

- `ux-performance-perception` — loading state taxonomy; skeleton screen design; long-running operations
- `ux-information-architecture` — flow routing and navigation within workflows
- `ux-design-systems` — component behavior spec for interactive elements used in workflows
- `ux-accessibility` — keyboard interaction patterns; focus management in forms; error state accessibility
- `be-data-modeling` — form validation rules that reflect data model constraints; understanding what's feasible
- `be-api-design` — error response structures that must support inline error display
- `fe-state-management` — multi-step flow state; form dirty state tracking; optimistic UI feasibility

---

## References

- Baymard Institute — Form UX research: https://baymard.com/blog/form-design-best-practices
- Luke Wroblewski — Web Form Design (book)
- Nielsen Norman Group — Error message writing: https://www.nngroup.com/articles/error-message-guidelines/
- ARIA APG — Combobox, multiselect patterns: https://www.w3.org/WAI/ARIA/apg/patterns/

## Related
- hub → [[lead-ux-designer]]
