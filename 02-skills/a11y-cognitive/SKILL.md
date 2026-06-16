---
name: a11y-cognitive
description: >
  Cognitive load, ADHD, dyslexia, anxiety-reducing design, memory constraints, and
  reading disabilities. Spoke skill in the lead-accessibility-architect network. Use
  this skill whenever the conversation touches: cognitive accessibility, cognitive load,
  extraneous load, ADHD, attention deficit, attention, focus, impulsivity, working
  memory, dyslexia, reading disability, reading difficulty, literacy, plain language,
  reading level, Flesch-Kincaid, anxiety design, stress design, error recovery,
  destructive actions, undo, confirmation dialogs, progressive disclosure, recognition
  over recall, consistency, predictability, multi-step tasks, task complexity, mental
  model, information density, WCAG 3.1.5 Reading Level, WCAG 3.3 Input Assistance,
  error messages, help text, instructions, memory load, sustained attention, cognitive
  fatigue, TBI, traumatic brain injury, dementia, Alzheimer's, intellectual disability,
  executive function, planning, task initiation, time awareness, timeout warnings.
aliases: [a11y-cognitive]
tier: cross-cutting
domain: accessibility
hub: lead-accessibility-architect
spec_version: "2.0"
---

# a11y-cognitive

Specialist lens for cognitive accessibility: cognitive load reduction, ADHD and
dyslexia design, anxiety-reducing patterns, and plain language. Part of the
`lead-accessibility-architect` skill network.

---

## Domain Boundary

This skill owns **cognitive and learning disability design** — load reduction, reading
accommodation, anxiety patterns, and error design.

- **Autism spectrum and sensory processing** → `a11y-neurodiversity` (overlaps here; route to neurodiversity for sensory/ASD-specific depth)
- **Information architecture for cognitive accessibility** → `lead-information-architect`/`ia-mental-models`
- **Interaction complexity reduction** → `ux-interaction-design`
- **Legal standards** → `a11y-legal-compliance`

---

## Cognitive Impairment Breadth

"Cognitive disability" covers an extremely wide range of conditions with very
different design implications:

| Condition | Key Design Impact |
|----------|-----------------|
| ADHD | Attention, impulsivity, working memory, time perception |
| Dyslexia | Reading decoding, letter/word recognition, fatigue |
| Other reading disabilities | Comprehension, phonological processing |
| Intellectual disability | Simplified language, visual support, reduced complexity |
| Traumatic brain injury (TBI) | Variable; often memory, processing speed, fatigue |
| Dementia / Alzheimer's | Memory, orientation, familiar patterns critical |
| Anxiety disorders | Stress-triggered avoidance, fear of making mistakes |
| Depression | Reduced motivation, decision fatigue, difficulty initiating tasks |
| Executive function disorders | Task planning, switching, initiation, time management |

~15–20% of adults have some form of reading difficulty. ADHD affects ~5–7% of adults.
These are not edge cases — they are a significant portion of any product's user base.

---

## Cognitive Load Theory

Sweller's Cognitive Load Theory (CLT) provides the design framework for managing
how much mental effort a user must expend.

### Three Types of Cognitive Load

**Intrinsic load** — the inherent complexity of the task itself. A tax form is
genuinely complex. This load cannot be designed away, only supported.

**Extraneous load** — complexity introduced by poor design. Confusing labels,
inconsistent patterns, cluttered layouts, unclear error messages, and unnecessary
steps all add extraneous load. This is the designer's responsibility to eliminate.

**Germane load** — cognitive effort spent building a mental model and learning.
Good design supports this (familiar patterns, consistent metaphors, progressive
disclosure); poor design impedes it (too many exceptions, contradictory behavior).

**Design directive**: Minimize extraneous load mercilessly. Enterprise software is
particularly prone to accumulating extraneous load — features layered over features,
inconsistent interaction patterns, redundant navigation, and forms with unexplained
requirements. Every point of extraneous load is a design failure.

### Measuring Extraneous Load

Extraneous load is hard to measure directly but has proxy indicators:
- Users cannot explain what an interface element does
- Error rates are high in predictable, repeatable locations
- Users abandon tasks at a specific step
- Support tickets cluster around the same interactions
- Testing shows users re-reading labels multiple times before acting

---

## ADHD Design

ADHD is characterized by difficulty regulating attention, impulsivity, and variable
executive function. It affects ~5–7% of adults — more than color blindness.

### Attention and Distraction

Users with ADHD have difficulty sustaining attention on tasks that require
prolonged focus, particularly when competing stimuli are present.

**Design responses**:
- Minimize ambient animation, auto-playing content, and decorative motion (see also
  `a11y-neurodiversity` for vestibular overlap)
- Reduce visual noise: consolidate related information, use clear visual hierarchy,
  eliminate decorative complexity that doesn't contribute to function
- Notification design: frequent, interruptive notifications pull ADHD users away from
  the current task more severely than neurotypical users; allow fine-grained notification
  control
- Progress indication: clear visual progress (step indicators, progress bars) helps
  users who lose their place; makes it easy to re-orient after attention breaks

### Impulsivity and Error Recovery

Impulsivity means ADHD users activate controls before fully evaluating consequences.
Design for accidental activations:
- **Undo patterns**: wherever technically feasible, make actions reversible; "Undo
  send" is a famous example that benefits ADHD users primarily
- **Confirmation for destructive actions**: "Delete this project?" with explicit
  confirmation prevents catastrophic irreversible errors
- **Non-destructive default actions**: the most prominently placed, easiest-to-reach
  action should be safe; destructive actions should require additional steps
- **Forgiveness over prevention**: prevention mechanisms (disabled states, complex
  confirmation flows) create friction for all users; forgiveness (undo, recovery) is
  more usable overall

### Working Memory

ADHD impairs working memory — the short-term buffer for information being actively
used. Design for low working memory:
- Show relevant information persistently; do not expect users to remember content
  from previous steps
- In multi-step flows, show a summary of entered data on the final confirmation screen
- Error messages on form validation should appear adjacent to the field with the error;
  do not require the user to remember which field had which error after a page-level
  error summary
- Labels and instructions should be visible on the screen where they are needed, not
  only in a prior step or tooltip

### Time Perception

ADHD significantly impairs time perception — users may not realize how much time has
passed during a task session.
- Timeout warnings must be explicit and provide sufficient advance notice (WCAG 2.2.1
  Timing Adjustable: users must be able to extend time limits unless the time limit
  is essential)
- Session timeout modals should warn at a generous threshold (5-10 minutes before
  expiry, not 60 seconds)
- Progress indicators help users gauge how much more effort remains

---

## Dyslexia Design

Dyslexia is a reading disability that affects the phonological processing of written
text. It does not affect intelligence. ~15–20% of the population has some level of
reading difficulty; dyslexia is the most common cause.

Users with dyslexia may:
- Read letter by letter rather than recognizing whole word shapes
- Confuse similar letters (b/d, p/q, n/u) and words
- Experience visual stress (letters appearing to move or blur on high-contrast white
  backgrounds)
- Fatigue significantly faster when reading dense text
- Benefit from more time on tasks but not from simplified content

### Typography Recommendations for Dyslexia

| Property | Recommendation | Rationale |
|----------|---------------|-----------|
| Font | Clear letterform differentiation (b/d/p/q distinct) | Reduces letter confusion |
| Font weight | Regular to medium (avoid light weights for body text) | Light weights reduce letterform clarity |
| Line height | 1.5× or greater | Reduces line crowding; helps visual tracking |
| Letter spacing | Slightly wider than default (+5–10%) | Reduces letter-level crowding |
| Word spacing | Default or slightly wider | Helps word boundary recognition |
| Line length | 45–75 characters (short-medium) | Reduces line tracking difficulty |
| Alignment | Left-aligned, ragged right | Justified text creates variable word spacing that impairs tracking |
| Emphasis | Bold, not italic | Italic changes letterform shapes; bold preserves them |
| Color | Off-white or cream background rather than pure white (for those with visual stress) | Reduces glare |

**Note on "dyslexia fonts"** (Dyslexie, OpenDyslexic): The evidence for their
efficacy is mixed and not conclusive. Standard fonts with clear letterform differentiation
(many sans-serif fonts perform well) are a safer design choice. The typography parameters
above have stronger evidence than font-specific choices.

### Accommodating Reading Difficulty

- Chunk long text: short paragraphs (3-5 sentences), clear subheadings, bullet points
  where appropriate
- Front-load key information: users who lose their place benefit from key information
  appearing early in a section
- Visual supports: icons paired with text labels, illustrations supporting instructions
- Interactive glossaries or definitions for technical terms (hover/tap to define)
- Avoid text in images — cannot be reflowed, resized, or read aloud by AT

---

## Memory Constraints and Recognition Over Recall

A fundamental HCI principle with particular importance for cognitive accessibility:
designs requiring **recall** (retrieving information from memory) are harder than
designs supporting **recognition** (identifying the correct option from visible choices).

| Recall (harder) | Recognition (easier) |
|----------------|---------------------|
| Command-line interface | GUI menu |
| "Enter the product code" | Dropdown of products |
| "Enter your PIN" | "Select the image you chose" |
| Remembering step 2 requirements during step 4 | Showing step 2 data in the step 4 confirmation |

**Design for cognitive accessibility**:
- Show relevant data persistently when it's needed for a decision
- Use dropdowns, autocomplete, and pickers rather than free text where possible
- Provide summary screens in multi-step flows
- Show confirmation of user-entered data before destructive/irreversible submission

### Consistent Patterns

Every inconsistency forces the user to re-learn and expend cognitive effort. Users
with cognitive disabilities have less tolerance for exceptions:

- Consistent navigation placement — if primary navigation is at the top, it should
  always be at the top
- Consistent interaction patterns — if tapping a card navigates to a detail view
  in one context, it must not perform a different action in a similar context
- Consistent terminology — using "Delete", "Remove", and "Dismiss" interchangeably
  for the same action forces users to evaluate whether they're the same
- Consistent feedback — success, error, and loading states should look and behave the
  same way across the product

---

## Anxiety-Reducing Design

Anxiety disorders affect ~18% of the US adult population in any given year. Design
patterns that cause distress to anxious users often cause friction for all users.

### Principles

**Predictability**: Unexpected changes, surprises, and unknown consequences increase
anxiety. The user should always know what will happen before they trigger an action.
- Action labels should describe the outcome: "Delete account permanently" not just "Delete"
- Hover/focus tooltips should explain non-obvious actions before activation
- Inline confirmation for actions with significant consequences

**Reversibility**: Fear of making irreversible mistakes is a significant anxiety trigger.
Make as many actions reversible as possible:
- Soft delete (move to trash/archive) before permanent deletion
- Explicit, prominent undo/undo trail
- "We'll email you a summary" confirmations for high-stakes form submissions

**Clear, calm error messages**: Error states are high-anxiety moments. Error messages
must:
- Explain what went wrong (not "An error occurred" — say what failed)
- Avoid accusatory or alarming language ("You made an error" → "Check this field")
- Tell the user exactly how to recover
- Not imply the user is stupid or at fault
- Use calm visual design (red is appropriate for emphasis, but avoid alarming icon
  choices or flashing for non-emergency errors)

**Timeout warnings**: Session timeouts are panic-inducing for anxious users who have
spent time filling out a form. WCAG 2.2.1 requires users be able to extend time limits;
good design gives generous advance warning (5-10 minutes) and a simple, low-stress
extension mechanism.

---

## Plain Language

**WCAG 3.1.5 Reading Level** (AAA): Supplementary content or a lower-complexity version
should be available if body text exceeds a Grade 9 reading level.

For general consumer products, target Grade 6-8. For expert/professional tools, Grade
10-12 is acceptable, but jargon should always be defined or accompanied by context.

### Plain Language Guidelines

| Principle | Example |
|-----------|---------|
| Simple vocabulary | "Use" not "utilize"; "end" not "terminate" |
| Short sentences | 15-20 words maximum for key instructions |
| Active voice | "You can save your progress" not "Progress can be saved" |
| Concrete language | "Click the blue Save button" not "Activate the persistence control" |
| No idioms | Idioms fail for non-native speakers and literal readers |
| Define first use | Acronyms spelled out on first occurrence: "Application Programming Interface (API)" |
| Front-load instructions | The critical action comes first, conditions/exceptions after |

### Error Message Language

Errors are high-cognitive-load moments. The user is already stressed.

**Bad**: "Invalid input. Please check form fields and resubmit."
**Good**: "Your password must be at least 8 characters. The one you entered is 5 characters."

**Bad**: "Server error 500. Contact administrator."
**Good**: "We couldn't save your changes. Please try again. If this keeps happening, contact support."

The format: what went wrong + why + what to do to fix it.

---

## Working Memory Constraints and Miller's Law

George Miller's 1956 paper "The Magical Number Seven, Plus or Minus Two" established
that most people can hold approximately 7 items in short-term memory. Subsequent
research (Cowan, 2001) revised the effective working memory capacity to approximately
**4 chunks** — not 7 — when accounting for how meaning is grouped.

Cognitive impairments, high stress, and task fatigue reduce working memory capacity
further. The design implication: assume users can hold 3-4 items in working memory
at any given time, not 7. For users with cognitive disabilities, assume 2-3.

### Chunking

Chunking is the process of grouping related information into meaningful units. A
10-digit phone number (6045551212) is hard to hold; broken into chunks (604-555-1212)
it becomes 3 units. Design applications:

- Group form fields by logical section (Contact info / Shipping / Payment — 3 chunks,
  not 10 fields)
- Group navigation into 5-7 categories maximum per level
- Break long content lists into paginated or sectioned groups
- Use visual grouping (cards, sections, dividers) to make chunks explicit

### Implications for Form Design

A single-page form with 15 fields requires users to hold the overall task goal in
working memory while simultaneously processing each field's requirement. For users
with limited working memory:

- Show one section at a time in stepped forms
- Repeat relevant context at each step ("You're completing checkout for: [order summary]")
- Do not ask users to remember information from prior steps without showing it again
- Autocomplete wherever possible (SC 1.3.5 Identify Input Purpose)

---

## WCAG COGA — Cognitive and Learning Disabilities Success Criteria

WCAG 2.2 includes four new success criteria specifically from the W3C Cognitive
and Learning Disabilities (COGA) Task Force. These represent a significant expansion
of cognitive accessibility in the formal standard.

### SC 3.2.6 Consistent Help (AA)

If a help mechanism (human contact, chat, phone, FAQ link, automated tool) appears
across multiple pages, it must appear in the **same relative position** across those pages.

- A chat widget that floats bottom-right on the home page must float bottom-right on
  every page, not be embedded in the footer on product pages
- If a "Contact support" link exists in the top navigation, it must be in the top
  navigation on all pages
- This prevents users with cognitive impairments from needing to re-locate help
  every time they switch pages

### SC 3.3.7 Redundant Entry (A)

Information already entered in the **current session** must not be required again unless:
- Re-entry is essential to the function (e.g., confirm password field)
- The information has become invalid (session expired, data changed)

Implementations: shipping/billing "same as" checkbox; pre-filling fields from
earlier steps; displaying previously entered values for confirmation rather than
requiring re-entry.

### SC 3.3.8 Accessible Authentication (Minimum) — AA

Cognitive function tests must not be required to complete authentication unless an
alternative authentication method is available. Cognitive function tests include:
- CAPTCHAs (transcribing distorted text, selecting images, solving puzzles)
- Memorization (remembering a custom code, security question answers)
- Transcription of one-time passcodes from SMS without copy-paste support

**Compliant alternatives**: email magic links, passkeys/WebAuthn, OAuth (Sign in
with Google/Apple), biometric authentication. These remove the cognitive test entirely.

**Exception**: An image-recognition CAPTCHA where the user must identify objects
they chose (not memorized) is explicitly exempted from 3.3.8 — this is object
recognition, not a cognitive test in the COGA sense.

### SC 3.3.9 Accessible Authentication (Enhanced) — AAA

Like 3.3.8 but removes even the object recognition and personal content exceptions.
Authentication must require no cognitive function test whatsoever.

---

## Executive Function Support

Executive function includes: task initiation, planning, sequential organization,
time management, task switching, and working toward a goal. Executive function
difficulties are associated with ADHD, TBI, autism, depression, and many other conditions.

### Design Responses

- **Show the whole plan upfront**: Multi-step forms and flows should show the
  complete list of steps before the user begins (progress indicator, step counter)
- **Save and return**: Allow users to save partial progress and complete tasks
  across multiple sessions; don't force single-session completion of long tasks
- **Chunked tasks**: Break complex tasks into manageable pieces with clear
  completion markers; each chunk should feel like an achievable unit
- **Time estimation**: "This takes about 5 minutes" and "You'll need your account
  number and last 4 digits of your SSN" reduces cognitive load by allowing preparation
- **Task history and recovery**: Show recently started, incomplete tasks prominently;
  allow easy resumption

---

## Quality Checklist

- [ ] Error messages explain what went wrong and exactly how to fix it
- [ ] Destructive actions require explicit confirmation
- [ ] Reversible actions (undo, soft-delete) provided wherever technically feasible
- [ ] Multi-step flows show all steps upfront and allow save-and-return
- [ ] Information needed for later steps is shown persistently, not recalled from memory
- [ ] All instruction text available before and during relevant interaction (not only before)
- [ ] Recognition preferred over recall throughout
- [ ] Consistent interaction patterns across similar components
- [ ] Consistent terminology for the same concept across the product
- [ ] Ambient animation minimized; no looping animations in main content areas
- [ ] Notification volume is controllable
- [ ] Session timeout provides generous advance warning and easy extension
- [ ] Body text at appropriate reading level for the target audience
- [ ] Jargon defined on first use; acronyms expanded
- [ ] Error language is calm, non-accusatory, and recovery-focused
- [ ] Complex flows broken into appropriately-sized chunks with visible progress

---

## Cross-Links

| Skill | Relationship |
|-------|-------------|
| `a11y-neurodiversity` | Executive function and ADHD overlap; route to neurodiversity for sensory processing, ASD, and vestibular depth |
| `a11y-legal-compliance` | WCAG 3.2.6, 3.3.7, 3.3.8, 3.3.9 COGA success criteria; legal requirements for plain language (3.1.5) |
| `a11y-assistive-tech` | ARIA live regions and focus management for error recovery announcements |
| `lead-ux-designer` / `ux-interaction-design` | Cognitive load is the primary constraint on acceptable interaction complexity |
| `infod-dashboard-patterns` | Cognitive load is the primary enemy of accessible dashboard design; progressive disclosure architecture |
| `lead-accessibility-architect` | Hub — routes to this spoke for cognitive load, reading disabilities, ADHD, dyslexia, anxiety design, and plain language |
