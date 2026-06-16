---
name: ux-performance-perception
description: >
  Perceived performance UX design — loading states, skeleton screens, optimistic UI,
  latency design, and the UX of waiting. Use this skill when working on: loading state
  design for any feature, skeleton screen layout, deciding when to use optimistic UI,
  designing for slow API responses, long-running background operations (exports, batch
  jobs, report generation), progress indication for multi-step processes, timeout UX,
  perceived performance instrumentation, and any question about what to show users
  while they wait. Also trigger on: "what loading state should I use", "how do I design
  the skeleton", "when can I use optimistic UI", "the API is slow — how do I handle that",
  "how do I communicate that this is taking a long time", "what's the UX for a background
  job", or any question about the designed experience between user action and data display.
  This skill understands that performance perception is a joint design/engineering problem
  and names the backend and frontend constraints that affect perceived performance decisions.
---

# UX — Performance Perception

Spoke skill in the `lead-ux-designer` network. Owns the design of the time between
user action and data availability: loading states, skeleton screens, optimistic UI,
progress indication, and latency design.

Does not own: actual performance engineering (→ `fe-performance`, `be-caching-performance`),
frontend implementation of loading states (→ `fe-api-integration`). This spoke owns
the design decisions about what to show, when, and why — the implementation lives
in the FE and BE spokes.

---

## The Psychology of Waiting

The same objective wait time can feel fast or slow depending on how it is designed.
Perceived performance is a design output, not a technical measurement.

### Doherty Threshold and response time models

Jacob Nielsen's response time models (1993, still accurate):

| Response time | User perception | Required feedback |
|--------------|-----------------|------------------|
| < 0.1s (100ms) | Instantaneous — no feedback needed | None |
| 0.1–1.0s | User notices the delay | Visual acknowledgment — button loading state |
| 1–10s | User's train of thought is interrupted | Progress indication + disable the trigger |
| > 10s | User will do something else | Background job pattern; notification on completion |

The Doherty Threshold (400ms) is the point at which response speed is noticed as
a distinct improvement. Below 400ms, users experience the system as "fast." Above
400ms, the system needs to communicate that something is happening.

### Uncertainty is more uncomfortable than known delay

A 5-second wait with a progress bar that shows "Step 2 of 4" feels shorter than a
3-second wait with a spinner. The reason is uncertainty: a spinner communicates "I
don't know how long this will take." A progress indicator communicates "I know how
long this will take, and you can see how far along we are."

Design implication: whenever backend processing time is somewhat predictable, prefer
an estimated duration or step count over a generic spinner. Even a rough estimate
("This usually takes 15–30 seconds") reduces perceived wait time.

### Occupied time feels shorter

Users who have something to look at while waiting perceive the wait as shorter.
Skeleton screens work partly because of this principle — they give the user a
preview of the coming content, which occupies attention and creates anticipation.

A blank white screen with a spinner in the center is the worst-performing loading
experience. Not because it's ugly, but because it provides nothing to look at.

---

## Loading State Taxonomy

Never use a single spinner for all loading scenarios. Each loading category has
different user context, different appropriate treatment, and different behavioral
implications.

### Category 1: Initial load (no data yet rendered)

**User context**: the user has navigated to a page or opened a view. No content has
appeared yet.

**Design treatment**: skeleton screen. The skeleton should mirror the layout of the
content it precedes — same column widths, same element positions, same approximate
proportions. Not a generic grey block.

**Do not**: show a blank page then flash to content (causes jarring layout shift).
Show a spinner centered in a blank page for initial loads > 500ms.

### Category 2: Background refresh (stale data showing)

**User context**: the user is looking at data. The system is checking for updates
in the background.

**Design treatment**: a subtle indicator that doesn't disrupt the current view.
Options: a "last updated N minutes ago" timestamp that pulses or updates; a small
refresh indicator in the header; a "new data available" banner that appears when
fresh data is ready (so the user can choose when to refresh).

**Do not**: re-render a full skeleton screen every time background data refreshes.
This would constantly interrupt the user's reading of the current data.

### Category 3: User-triggered load (button press, filter apply, form submit)

**User context**: the user has taken an explicit action and is waiting for the result.

**Design treatment**: loading state on the trigger element (button spinner, input
loading indicator). Disable the trigger to prevent double-submit. Show inline feedback
near the trigger, not a full-page loading state.

**Important**: the loading state must be on or immediately adjacent to the trigger.
A user who clicks "Apply Filter" needs to see that the filter is being applied — not
a spinner at the top of the page that may be off-screen.

### Category 4: Optimistic update (near-instant expected)

**User context**: the user has taken an action where success is overwhelmingly likely
and failure is rare and reversible.

**Design treatment**: no loading state. Show the result immediately. If the operation
fails, roll back and show an error.

**Constraint**: optimistic updates require an error rollback state. If the design
doesn't include the rollback, the optimistic pattern is incomplete.

### Category 5: Long operation (> 5 seconds)

**User context**: the user has triggered a process that the system cannot complete
quickly — report generation, bulk export, data import, calculation jobs.

**Design treatment**: background job pattern. Do not block the UI. Offer one of:
- Progress bar with step count or percentage
- "Processing in background" state with a notification when complete
- Email notification when complete (for operations > 2 minutes)
- Estimated completion time where computable

The user must be able to continue using the product during a long operation. A modal
spinner that blocks the entire UI for 30 seconds is not a loading state — it is
an app freeze.

---

## Skeleton Screen Design

Skeleton screens are the primary loading state for initial page loads in enterprise SaaS.
A well-designed skeleton reduces perceived wait time and prevents layout shift.

### Mirror the actual content layout

The skeleton must have the same structural proportions as the content it precedes.
If the page has a two-column layout with a primary content area (70%) and a sidebar
(30%), the skeleton has the same proportions. If the table has 6 columns with
specific widths, the skeleton shows 6 column-width blocks.

A generic skeleton (three grey horizontal bars) fails because it bears no resemblance
to the actual content. The user's perception of waiting is partly managed by seeing
the shape of the expected content.

### Animation: pulse or shimmer

Skeleton blocks should animate to signal "loading" — not because animation is nice,
but because a static grey block is ambiguous. A static skeleton might look like a
component rendered in error state. The animation makes the loading state unambiguous.

- **Pulse**: the block fades between two grey tones. Subtler. Lower motion impact.
  Appropriate for dense tables and complex layouts.
- **Shimmer**: a highlight moves across the block left-to-right. More visually prominent.
  Appropriate for card-heavy layouts and simpler pages.

Both must have a `prefers-reduced-motion` fallback — use a static skeleton when
the user has reduced motion enabled (→ `ux-accessibility`).

### Skeleton scope

Above-the-fold content only. Below-the-fold elements can load progressively —
the skeleton only needs to cover what the user sees immediately. Skeletonizing
100 rows of an off-screen table wastes rendering resources and can increase
actual page load time.

For tables: show column headers (which are often available before row data) with
skeleton rows. The column headers with defined widths give the user the structural
context; the row skeletons communicate that row data is loading.

Number of skeleton rows: show enough to fill the visible viewport. If the table is
typically paginated at 25 rows but the viewport shows 10, skeleton 10 rows. Do not
skeleton 25 rows when only 10 are visible — the extra rows are off-screen and waste
rendering time.

### Known metadata population

If metadata is available before the full data load (e.g., the user is navigating
to a record and the record title is in the navigation path), populate it in the
skeleton. A skeleton that shows "Product: WIDGET-001" in the page header is more
informative than an anonymous grey block.

This requires coordination with the FE to understand what metadata is available
at navigation time vs. after the data fetch.

---

## Optimistic UI Design

Optimistic UI is a perceived performance technique where the UI reflects the expected
success state before the server confirms. Done correctly, it eliminates visible latency
for common actions. Done incorrectly, it creates confusing error states.

### When optimistic UI is appropriate

| Criterion | Required | Notes |
|-----------|----------|-------|
| Low error rate | Yes | The action must succeed reliably (>99%). If failure is common, optimistic UI creates constant disappointment. |
| Reversible / non-destructive | Yes | The action can be rolled back without side effects. Add to list: yes. Delete: no. |
| No downstream side effects | Yes | The action does not trigger something the user cannot undo (email send, webhook, financial transaction). |
| Server response is the same as the expected result | Yes | If the server might return a modified version of what was submitted, optimistic state will be wrong. |

### Rollback design

Every optimistic update must have an explicit error rollback state:
1. Show the optimistic success state immediately
2. If the server returns an error: revert the UI to pre-action state + show an
   inline error ("Couldn't save — tap to retry")
3. The rollback must be visible and contextual — not a toast notification that
   the user might miss while looking elsewhere

### Undo as an alternative to confirmation

"Item deleted. Undo?" is a better pattern than "Are you sure you want to delete?" for
reversible actions.

Why: confirmation dialogs interrupt the workflow, require cognitive engagement for a
decision the user has already made, and add friction for expert users who perform the
action frequently. Undo allows the action to complete immediately while preserving
recoverability.

Constraints: undo requires a time window (typically 5–10 seconds on the snackbar),
a backend undo operation, and a clear visual treatment. If the backend cannot undo
the action reliably, the confirmation dialog is the correct pattern.

---

## Perceived Performance Techniques

These are design patterns that reduce perceived (not actual) latency.

### Prioritized rendering

Render above-the-fold content first. Defer off-screen content. This requires
FE implementation coordination (→ `fe-performance`) but the decision about what
is "above the fold" and therefore priority is a design decision.

For dashboards: render the primary KPI row first. Secondary charts can load
progressively. Below-the-fold widgets can load independently after the critical
content is shown.

### Content-aware placeholders

When navigating to a record, use known metadata (e.g., record title from navigation
path, last-known values from a previous load) to pre-populate the page before the
full data fetch completes. This creates the illusion of instant navigation.

Requires coordination with `fe-api-integration` to understand what data is available
at navigation time (client cache, URL params) vs. requiring a fetch.

### Hover prefetch

Preload target page data when the user hovers a navigation link or table row.
The user's hover time (typically 200–400ms before click) can be used to initiate
the data fetch, so by the time they click, the data is partially loaded.

This is a FE implementation detail but it requires the design to define hover
targets explicitly — and the product analytics to confirm that the hover-to-click
pattern exists in the user population.

### Stale-while-revalidate pattern

Render cached data immediately on navigation, then revalidate in the background
and update if the data has changed. The user sees content instantly; the data
is refreshed transparently.

Design requirement: the UI must communicate when it is showing stale data (a
"Last updated N minutes ago" indicator) and when it has refreshed (subtle
transition, not a jarring re-render).

---

## Latency Design for Enterprise Features

### Long-running operations: background job pattern

Operations that take > 10 seconds should not block the UI. The background job
pattern: the user triggers the operation, the UI confirms the operation is running,
the user can continue working, a notification appears when the operation completes.

Required design elements:
1. **Trigger confirmation**: "Your export has started. You'll be notified when it's ready."
2. **Status check**: a way to see running operations (a jobs/tasks list, a notification bell)
3. **Completion notification**: in-app notification + (for long operations) email
4. **Failure state**: operation failed — what went wrong, what to do
5. **Result delivery**: how the user gets the output (download link, record update, email)

### Step indicator for multi-step backend processes

When a long operation has known steps (import → validate → process → complete),
show the current step. This converts "I don't know when this ends" to "I'm at step
2 of 4." Step indicators dramatically reduce perceived wait time for structured operations.

Step indicator requirements:
- Show current step clearly distinguished from completed and upcoming steps
- Show step labels that describe what's happening ("Validating records," not "Step 2")
- For steps with known sub-operations, optionally show progress within the step
- Show estimated time remaining if computable

### Timeout design

If an operation exceeds the expected duration:
1. Surface a message: "This is taking longer than expected"
2. Continue showing progress — don't abandon the operation
3. Offer options: "Wait" or "Cancel" (if cancellation is technically supported)
4. At a defined hard timeout: show a failure state with a retry option and a support path

The timeout threshold and the messaging must be coordinated with backend (`be-caching-performance`)
to set realistic expectations. A timeout message that fires at 3 seconds when the operation
always takes 8 seconds is worse than no timeout message.

---

## Cross-Links

- `fe-performance` — rendering optimizations; lazy loading; code splitting
- `fe-api-integration` — loading state implementation; request/response state management
- `be-caching-performance` — what the backend can provide: response streaming, partial data, TTFB
- `ds-product-analytics` — measuring perceived performance: rage clicks, time-to-interactive, task abandonment rates
- `ux-interaction-design` — optimistic UI as an interaction pattern; undo vs. confirmation decisions
- `ux-design-systems` — skeleton screen as a design system component; loading state token design

---

## References

- Nielsen Norman Group — Response times: https://www.nngroup.com/articles/response-times-3-important-limits/
- Google Web Vitals — LCP, INP, CLS: https://web.dev/vitals/
- Luke Wroblewski — Mobile First (progressive loading patterns)
- Cloudflare — Stale-while-revalidate: https://developers.cloudflare.com/cache/concepts/cache-control/
