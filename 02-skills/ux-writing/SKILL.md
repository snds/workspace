---
name: ux-writing
description: >
  Microcopy and content design for enterprise SaaS interfaces. Staff/principal IC
  level. Use this skill when working on: error message architecture and writing,
  empty state copy strategy, label design at the writing level, voice and tone
  operationalization, plain language standards, content style guide construction,
  notification and alert copy, and writing for data-dense interfaces. Also trigger
  on: "what should this error say", "how do I write this empty state", "is this
  label right", "how should we write validation messages", "what's our tone guide",
  "how do I write for this alert type", or any question about the words in a UI.
hub: lead-ux-designer
aliases: [ux-writing]
tier: spoke
domain: design
prerequisites: [lead-ux-designer]
spec_version: "2.0"
---

# UX — Writing

Spoke skill in the `lead-ux-designer` network. Owns microcopy, content design,
error message writing, empty state strategy, label design, voice and tone, and
plain language standards for enterprise SaaS.

Does not own: the interaction pattern that error messages appear in (→ `ux-interaction-design`),
accessibility requirements for error message placement and ARIA (→ `ux-accessibility`),
the information architecture of label hierarchies (→ `ux-information-architecture`),
or data table column header layout decisions (→ `lead-information-designer`). This spoke
owns the words. The pattern that contains them lives in the relevant interaction spoke.

---

## Error Message Architecture

### The 3-part anatomy

Every error message must answer three questions in sequence:

1. **What went wrong** — a specific, non-technical description of the failure
2. **Why it went wrong** — the constraint or rule that was violated
3. **How to fix it** — a concrete next action the user can take

This is a contract, not a formula. If all three parts are already clear from context,
you can compress. But you cannot skip a part without replacing it with something that
does the same work in context.

### Common failure patterns

| Anti-pattern | Why it fails | Replacement |
|---|---|---|
| "Something went wrong" | Violates all three parts. Gives no information and no path forward. | "We couldn't save your changes. The server returned an unexpected error. Try again, or contact support if this continues." |
| "Invalid input" | Describes a result, not a cause. The user already knows the input was rejected. | "SKU must be 6–12 characters and cannot contain spaces." |
| "Error 500" | Technical — appropriate for a developer console, not a user interface. | "We ran into a server problem and couldn't complete that action. Try again in a moment." |
| "This field is required" | The field's required indicator already communicates the constraint. The error must do more. | "Product name is required to continue. Enter a name before saving." |
| "Please try again" | Gives an action without explaining the problem. Users don't know if trying again will change anything. | "Your session expired. Sign in again to continue where you left off." |

### Validation timing

| Timing | Use For | Do Not Use For |
|---|---|---|
| **On blur** | Format errors (email syntax, phone format, date format), character limit violations | Business rule violations that require a round-trip |
| **On submit** | Cross-field validation, server-side business rules, anything that requires backend evaluation | Format errors already catchable on blur — delaying them creates unnecessary friction |
| **On keystroke** | Essentially never for errors — keystroke validation triggers errors before the user finishes typing | Counters and remaining-character indicators are fine on keystroke; error states are not |

Never show error states while the user is actively typing in a field. The user has not
declared intent yet.

### Form-level vs. field-level error placement

**Field-level errors** (adjacent to the field, below the input or label) handle:
- Single-field validation failures
- Format errors
- Business rule violations scoped to one field

**Form-level summary** (above the form or at the top of a section) handles:
- Multiple simultaneous errors — the user needs to know the scope before scrolling to fix
- Cross-field dependency errors where the error doesn't belong to either field alone
- Server-side errors that affect the whole submission

Always provide both when there are multiple errors. A user who tabs through a form
without looking at each field will miss inline-only errors. The summary counts and
links to each field error — it does not repeat the full message.

### Recovery path design

When an error message is not sufficient on its own, the UI must also change:

- **Field highlight**: Red border (or equivalent semantic indicator) must appear on
  every field with an error — not just the first. Users scan visually before reading.
- **Scroll to error**: On submit with inline errors below the fold, auto-scroll to the
  first error. Don't leave the user wondering why the form didn't advance.
- **Disabled submit state messaging**: If a submit button is disabled due to validation
  state, tell the user why — don't just gray out the button with no explanation.
- **Persistent errors**: Errors that require external resolution (e.g., "An admin must
  grant you permission to create products") must persist — not auto-dismiss — until the
  condition changes or the user dismisses manually.

---

## Empty State Copy Strategy

### The four empty state types

Each type has a different job. Copy that works for first-use fails for no-results.

| Type | What it is | Copy goal |
|---|---|---|
| **First use** | The feature has never been used; no data exists yet | Marketing — communicate value, create desire to start, make the first action feel easy |
| **No data** | The user has used the feature but there is genuinely nothing here right now | Orient — explain the absence, indicate whether to wait or act |
| **No results** | A search or filter returned nothing | Navigation recovery — help the user adjust their search or filter |
| **Error** | Data should be here but couldn't load | Trust repair — acknowledge the failure, take responsibility, offer a recovery path |

### What every empty state must include

1. **What's missing** — name the thing that isn't there ("No products", "No results for 'fleece jacket'")
2. **Why it's missing** — the cause, not just the state ("You haven't created any products yet" vs. "No products match your filters")
3. **What to do next** — a concrete action or instruction, not a vague reassurance

The most common failure is conflating these types. An error empty state that uses
first-use copy ("Get started by adding your first product!") is a trust problem — the
user knows something broke, and cheerful onboarding language makes it worse.

### CTA copy in empty states

**Imperative verb + noun** is the standard CTA pattern: "Add product", "Create collection",
"Start import". This is appropriate when the action is obvious and the user has clear
intent.

Imperative CTAs patronize when:
- The user already knows how to use the feature and is in a no-results state (they
  searched for something and found nothing — they don't need to "Add" anything)
- The empty state is caused by a filter or search — the right action is to clear the
  filter, not create new content
- The user doesn't have permission to create content — offering a "Create" CTA to a
  read-only user is false affordance

For no-results empty states: prioritize "Clear filters" or "Try a different search"
over any create-new CTA. For error states: prioritize "Try again" or "Contact support"
over any positive action.

---

## Label Design at the Writing Level

### Label as taxonomy vs. label as microcopy

**Label as taxonomy** (IA layer): "What category does this concept belong to? Where
does this sit in the information hierarchy?" This is an information architecture
decision about classification.

**Label as microcopy** (UX writing layer): "What word or phrase communicates this
concept most accurately and efficiently to the user doing this task right now?"
These are distinct problems. A label can be taxonomically correct and still be poor
microcopy. "Product Configuration Attributes" is accurate IA; "Product settings" is
better microcopy for the same concept in an end-user context.

### Verb-noun consistency in action labels

Action labels must use consistent verb-noun patterns across the product. Pick a
pattern and apply it without exception:

- **Verb then noun**: "Save draft", "Delete product", "Export report"
- **Noun then verb**: rare; avoid unless the component pattern demands it

Mixing "Draft Save" with "Save Report" in the same product is not a style preference
disagreement — it is a cognitive load problem. The user must re-parse the label
structure each time.

### Icon + label vs. icon-only

**Always label when:**
- The icon is not universally understood (most icons are not)
- The action has significant consequences (delete, publish, submit)
- The user is in a context where cognitive load is already high
- The product serves users across language and culture backgrounds (icon meaning is not universal)

**Icon-only is permissible when:**
- Space is the genuine constraint (mobile, dense toolbar, data table row actions)
- The icon is paired with a visible tooltip that is always accessible
- The icon is one of a small set of universally understood symbols (close X, search magnifier, home)
- The icon-only use is consistent with a pattern the user has been trained on elsewhere in the product

Icon-only without tooltip is never acceptable — it fails WCAG and removes meaning
from users with unfamiliar conventions.

### Destructive action labeling

Use **"Delete"** for permanent removal. Use **"Remove"** for reversible disassociation.
Use **"Archive"** for soft deletion with recovery. These are not synonyms — they carry
different expectations about recoverability.

"Delete" is better than "Remove" for permanent actions because it is semantically
heavier. Users who click "Delete" have been warned by the word itself. "Remove" reads
as reversible; when the action is permanent, that misalignment destroys trust.

### Confirmation dialog copy — the label-as-contract principle

A confirmation dialog label is a contract with the user: it describes the exact
action that will happen if they confirm. The confirm button label must:

1. **Mirror the triggering action** — if the user clicked "Delete product", the confirm
   button says "Delete product", not "OK" or "Confirm"
2. **Be specific about scope** — "Delete 14 products" not "Delete" when bulk actions are involved
3. **Not use double negatives** — "Don't cancel" as a confirm button is a UX crime
4. **Place destructive confirm on the right, cancel on the left** — this is the
   platform-consistent pattern; inverting it to trick users into cancelling is
   manipulative design

The cancel button label should always be "Cancel" — not "Go back", "No thanks", or
"Keep product". "Cancel" is unambiguous and lets the user exit the dialog without
having to parse intent.

---

## Voice and Tone at the System Level

### The spectrum

Enterprise SaaS sits at a specific position on each axis:

| Axis | Consumer | Enterprise SaaS | Government/Regulated |
|---|---|---|---|
| Formal ↔ Informal | Informal | Moderately formal | Formal |
| Technical ↔ Plain | Plain | Domain-specific plain | Highly precise |
| Assertive ↔ Tentative | Assertive | Confident but not condescending | Measured |

"Moderately formal" means: professional, direct, clear — not stiff or legalistic, but
not casual or playful. It treats the user as a competent professional. It does not
use slang, exclamation points in functional copy, or emoji in transactional messages.

### Consistency across states

The product voice must be recognizable in success, error, warning, and empty states.
A product that is warm and clear in success notifications but cold and technical in
error messages has a voice inconsistency — users notice it as something being off,
even if they can't name it.

Test: read one success message and one error message aloud. Do they sound like the
same person? If not, one of them is wrong.

### When tone shifts are appropriate

Tone shifts (not voice shifts) are appropriate:

- **Data loss warning**: tone is more serious, more direct, less warm. This is not the
  moment for brand personality. "Deleting this product cannot be undone. All variants,
  images, and pricing data will be permanently removed." Not: "Heads up — this is
  permanent! 👋"
- **Feature discovery / onboarding**: tone can be slightly warmer and more inviting —
  this is the closest enterprise SaaS gets to consumer UX writing
- **Error messages for system failures (not user errors)**: tone shifts to empathetic
  and apologetic — take responsibility, don't be defensive

Voice is the constant (who you are). Tone is the variable (how you sound in context).

### Brand voice operationalized as microcopy guidelines

Brand voice documents that describe personality in adjectives ("bold, human, precise")
are not actionable for writers or designers. Operationalize them:

| Adjective | What it means in UI copy | What it rules out |
|---|---|---|
| "Human" | Write as if a smart colleague is explaining something | Passive voice, system-speak ("The operation was unable to be completed") |
| "Precise" | Name the exact thing, not a category | "Something went wrong", vague CTAs like "Learn more" without context |
| "Confident" | Don't hedge unnecessarily | "You may want to consider...", excessive qualifiers |

---

## Plain Language Standards

### Flesch-Kincaid targets

- **Broad enterprise audience (end users)**: Grade 8 or below
- **Admin/configuration surfaces**: Grade 10 or below — these users are technically
  sophisticated, but plain language still reduces error
- **Developer documentation or API surfaces**: No grade level restriction — precision
  over simplicity when the audience is technical

Flesch-Kincaid Grade 8 ≈ 8th-grade reading level ≈ sentences averaging 15 words,
words averaging 1.5 syllables. This is not "dumbing down" — it is reducing parse
time under cognitive load.

### Active voice enforcement

Active voice: "The system deleted the record" → passive; "We deleted the record" or
"The record was deleted on [date]" → context-dependent.

The rule: **prefer active voice when there is a meaningful actor**. In UI copy, the
actor is usually "you" (the user) or "we" (the system). Name the actor.

Exception: when the actor is genuinely irrelevant or unknown (audit log entries, for
example), passive voice is appropriate. "Record updated by [user]" is better than
forcing active voice awkwardly.

### Sentence length

- Instructional copy (tooltips, helper text, onboarding): ≤20 words per sentence
- Error messages: ≤25 words for the full message (across all three parts)
- Alert body copy: ≤30 words

Longer sentences are not prohibited — they are a cost. Every word above the limit
adds parse time for a user who is already doing something else.

### Concrete nouns vs. abstract system terminology

| Abstract | Concrete |
|---|---|
| "Entity" | "Product", "Order", "User" — name the actual thing |
| "Record" | "Product record" or just "product" |
| "Configuration" | "Settings" for end users; "Configuration" is acceptable for admin surfaces |
| "Instance" | Name the specific thing the instance represents |

When technical terms are the right choice: when the user is technical (developer, data
admin) and the technical term is more precise than the plain equivalent. "API key" is
correct terminology — "access password" is misleading plain language. Don't substitute
inaccuracy for clarity.

### Testing with non-expert readers

At-risk copy: error messages, onboarding steps, any copy involving a workflow the
user hasn't done before. Testing standard:

1. Show the copy to someone unfamiliar with the feature
2. Ask: "What would you do next?" If they can't answer, the copy failed
3. Ask: "What do you think happened?" If they mis-attribute the cause, the copy failed

This is not a research study — it is a 10-minute desk test. Run it before shipping any
high-stakes microcopy.

---

## Content Style Guide Construction

### Structure

A functional content style guide has five sections:

1. **Voice and tone** — the operating personality and how it shifts by state
2. **Vocabulary** — preferred terms, avoided terms, and why
3. **Grammar and mechanics** — the decisions every writer has to make and the answer
4. **Formatting** — capitalization, punctuation, numbers, dates, file sizes
5. **Component-specific rules** — what goes in a toast vs. a dialog vs. a tooltip

A style guide without a vocabulary list and grammar section is an inspiration document,
not an operational guide.

### Vocabulary list

For every product-specific term, document:
- **Preferred term** (use this)
- **Avoid terms** (don't use these)
- **Why** (the reason, so writers can extrapolate to new cases)

Example entry:
> **Delete** — Use for permanent removal of a record or object. Avoid: "Remove" (implies
> reversibility), "Erase", "Purge" (too technical). Why: "Delete" carries the correct
> expectation of permanence. "Remove" is reserved for reversible disassociation (removing
> a tag from a product, removing a user from a team).

### Capitalization

**Sentence case** for UI labels, buttons, navigation, column headers, and section headings.
**Title Case** for proper product names only.

Why sentence case wins in dense UI:
- Reduces visual noise — fewer capitals means labels are faster to scan
- Eliminates ambiguous decisions ("should 'product details' be title case or not?")
- Matches user expectations set by major platforms (Google, Microsoft, Apple all use
  sentence case in dense UI contexts)

The one exception: acronyms and initialisms always capitalize by convention (SKU, PLM,
API, UPC).

### Punctuation in UI

| Context | Rule |
|---|---|
| Button labels | No period |
| Nav labels | No period |
| Column headers | No period |
| Tooltip copy (single sentence) | No period |
| Tooltip copy (multiple sentences) | Period on all sentences |
| Error messages | Period on each sentence |
| Helper text (body copy) | Period if a complete sentence |
| Confirmation dialog body | Period — it is a complete sentence |

When in doubt: labels don't take periods; sentences do. The test is whether the text
is a label (noun phrase or imperative verb) or a sentence (subject + predicate).

### Numbers, dates, and file sizes

| Type | Format | Rationale |
|---|---|---|
| Numbers < 10 in body copy | Spell out ("three products") | Standard editorial convention |
| Numbers ≥ 10 | Numerals ("14 products") | Faster to scan |
| Numbers in data tables | Always numerals, right-aligned | Alignment enables comparison |
| Dates (US audience) | Month DD, YYYY ("April 28, 2026") or ISO 8601 for technical contexts (2026-04-28) | Unambiguous regardless of locale |
| Dates (international) | ISO 8601 (2026-04-28) | Avoids MM/DD vs DD/MM ambiguity |
| File sizes | Decimal SI (KB, MB, GB) — 1 KB = 1,000 bytes | Consistent with how OS and browsers display them |

---

## Notification and Alert Copy

### The four alert types

Each type has structural requirements. Violating them breaks user expectations.

**Info alerts**
- Purpose: contextual information that is useful but not urgent
- Structure: statement of fact or context; optional action if there is something to do
- Tone: neutral, informational
- Example: "This product is included in 3 active promotions. Changes to pricing may affect
  those promotions."

**Success alerts**
- Purpose: confirmation that a user-initiated action completed
- Structure: past-tense confirmation of the completed action; optional next step
- Tone: brief, confirmatory — not celebratory
- Example: "Product saved." or "14 products exported." Not: "Great job! Your product has
  been successfully saved! 🎉"
- Rule: success is the expected outcome — don't over-celebrate the expected

**Warning alerts**
- Purpose: a condition exists that may cause a problem; user can act before the problem occurs
- Structure: present-tense statement of the condition + consequence if unaddressed
- Tone: serious but not alarming — a warning is not an error
- Example: "This product's inventory is below the reorder threshold. Orders may be delayed
  if stock runs out."

**Error alerts**
- Purpose: an action failed or a system problem requires attention
- Structure: 3-part anatomy (what failed + why + how to fix it)
- Tone: direct, apologetic for system errors, instructional for user errors
- Example: "We couldn't process the export. The file exceeded the 50MB limit. Split the
  export into smaller batches or reduce the date range."

### Toast duration vs. persistent messages

| Condition | Treatment |
|---|---|
| Success (user-initiated action, reversible or low-stakes) | Toast — 4–6 seconds, auto-dismiss |
| Info (contextual, non-urgent) | Toast — 5–8 seconds, or persistent if the info is needed while the user continues working |
| Warning (requires user attention before continuing) | Persistent — do not auto-dismiss; the user must acknowledge or act |
| Error (action failed) | Persistent — do not auto-dismiss; user must act to resolve or dismiss |

Auto-dismissing an error is a UX error. The user may miss it and not understand why
their action didn't work. The 4-second toast for errors is a common pattern borrowed
from consumer UX that doesn't apply to enterprise workflows where the user's attention
is elsewhere.

---

## Writing for Data-Dense Interfaces

### How density changes microcopy decisions

Dense interfaces (data tables, configuration grids, dashboards) have fundamentally
different copy constraints than conversational or form-heavy interfaces:

- **Character budgets are real**: a 30-character column header will truncate at most viewport widths
- **Labels are scanned, not read**: users look for the pattern, not the full phrase
- **Context is carried by the structure**: the table communicates relationships that
  copy in isolation cannot

The implication: copy in dense interfaces must be shorter, must carry more meaning
per character, and cannot rely on surrounding prose to provide context.

### Column headers at character limits

Target character limits by column type:

| Column type | Target | Hard max |
|---|---|---|
| Status (enum value) | 6–8 chars | 10 chars |
| Count / quantity | 5–8 chars | 12 chars |
| Date / timestamp | 8–12 chars | 16 chars |
| Name / label | 8–16 chars | 20 chars |
| Description | 10–20 chars | 28 chars |

When a column header must exceed these limits, use abbreviation with a full-label
tooltip on the header — not truncation. "Min. Order Qty." is better than
"Minimum Order Quantity" truncated to "Minimum Order Q...".

### Truncation strategy

Truncation in a dense interface is a labeling problem. When text truncates, the
truncated version must preserve:

1. **The identifying information** — the part of the label that distinguishes this
   item from others. Truncating at the end risks cutting the distinguishing suffix.
   For file names, product codes, and structured identifiers: consider middle truncation
   ("ProductCode...001") over end truncation ("ProductCode-...")
2. **The user's ability to scan** — truncated column values that all look the same at
   the truncation point are invisible in a table

Always provide the full value on hover via tooltip when truncation is applied.

### Tooltip copy

A tooltip is the full label, not a supplement to it. The tooltip must:
- State the full label or value without relying on context from the truncated text
- Be a complete, standalone description — not "See full name" (that's not the name)
- For action tooltips on icon-only buttons: include the keyboard shortcut if one exists
  ("Delete selected (Del)")

Tooltip copy is not a place for extra explanation that didn't fit in the UI. If
something requires explanation beyond the label, that explanation belongs in helper text
or documentation — not a tooltip that disappears after 2 seconds.

---

## Cross-Links

- `ux-interaction-design` — error state interaction patterns, inline vs. summary error placement, validation timing
- `ux-accessibility` — plain language as cognitive accessibility; error message ARIA requirements; tooltip as accessible label
- `ux-information-architecture` — label strategy as IA taxonomy decision; navigation label design
- `lead-information-designer` — data table column header design and labeling in dense information layouts

---

## References

- Plain Language Action and Information Network — Federal plain language guidelines: https://www.plainlanguage.gov/
- Flesch-Kincaid readability test — background: https://en.wikipedia.org/wiki/Flesch%E2%80%93Kincaid_readability_tests
- Nielsen Norman Group — Error message writing: https://www.nngroup.com/articles/error-message-guidelines/
- Nielsen Norman Group — Empty state design: https://www.nngroup.com/articles/empty-state-ux/
- Microsoft Writing Style Guide: https://learn.microsoft.com/en-us/style-guide/welcome/
- Google Material Design — Writing: https://m3.material.io/foundations/content-design/overview
- Torrey Podmajersky — Strategic Writing for UX (book)
- Janice Redish — Letting Go of the Words (book)
