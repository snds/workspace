---
name: ux-ai-product-design
description: >
  UX design for AI/LLM-powered product features in enterprise SaaS. Staff/principal
  IC level. Use this skill when working on: designing for probabilistic AI outputs,
  human-in-the-loop interaction patterns, AI disclosure requirements, streaming
  response UX, AI error state taxonomy, trust calibration, prompt exposure in
  enterprise UI, and AI feature discovery and onboarding. Also trigger on: "how do
  I show AI confidence", "when should AI auto-apply vs. ask", "what do I show while
  the model is thinking", "how do I disclose that this is AI-generated", "how do I
  design the thumbs up/down feedback", "how do I handle AI errors", or any question
  about designing a feature where the output is produced by a model rather than
  deterministic logic.
hub: lead-ux-designer
aliases: [ux-ai-product-design]
tier: spoke
domain: design
prerequisites: [lead-ux-designer]
spec_version: "2.0"
---

# UX — AI Product Design

Spoke skill in the `lead-ux-designer` network. Owns UX design for AI/LLM-powered
features in enterprise SaaS — probabilistic output design, human-in-the-loop patterns,
disclosure, streaming UX, AI error states, trust calibration, and prompt surface design.

Does not own: the ML/NLP model selection or evaluation (→ `ds-nlp-llm`), the frontend
state management for streaming responses (→ `fe-state-management`), or platform-level
API design for AI endpoints (→ `pm-platform-api`). This spoke owns the design layer
between the model output and the user.

---

## Designing for Probabilistic Outputs

### The fundamental difference

Deterministic systems return the same output for the same input every time. AI systems
return outputs that vary in content, confidence, and correctness. This is not a defect
to design around — it is a property to design for.

The UX failure mode for probabilistic outputs: presenting AI output with the same visual
treatment as deterministic system output. When an AI-suggested product description looks
identical to a manually entered one, the user has no signal that this content requires
review. Accuracy expectations from deterministic interfaces will be applied to
probabilistic content — and they will be wrong.

### Confidence visualization patterns

**Probability bars (use with caution)**

Numeric probability displays ("87% confident") are appropriate only when:
- The user population is analytically sophisticated and understands probability
- The probabilities are well-calibrated (a model that says 87% confident is wrong 13%
  of the time — not a model that arbitrarily outputs numbers near 90%)
- The precision is meaningful — don't display "87.3%" when the model's calibration
  doesn't support that precision

Probability bars fail when users treat them as authoritative precision or when the
values cluster in a narrow range (everything between 72–94% looks the same on a bar).

**Classification labels with confidence ranges**

Better for most enterprise use cases: categorize confidence into 3–4 bands and label
them in plain language:

| Confidence level | Label | Visual treatment |
|---|---|---|
| High (model-specific threshold) | "High confidence" or no label | Normal presentation |
| Medium | "Review suggested" | Subtle visual indicator (dashed border, review badge) |
| Low | "Needs review" | Prominent indicator; may disable auto-apply |

The threshold between bands is a product decision made in coordination with the model
team — it should be calibrated against actual model accuracy at each confidence level.

**"AI suggests" framing**

Label AI output distinctly from user-entered or system-calculated data:
- "AI suggested: Fleece Jacket — Winter Collection" vs. displaying it as if the user typed it
- The label communicates: this came from a model, not from a human or a calculation
- This framing reduces over-trust without requiring confidence scores

Don't apply "AI suggests" framing to every piece of content in a product. Reserve it for
content where the AI's output is a draft that requires human confirmation, not for content
that has already been reviewed and accepted.

---

## Human-in-the-Loop Interaction Design

### The escalation ladder

AI automation exists on a spectrum. Each level has specific UX requirements.

| Level | Description | When appropriate | UX requirement |
|---|---|---|---|
| **Fully automated** | AI acts without user knowledge or input | Actions that are low-stakes, reversible, and high-confidence | Audit trail; always reversible; disclosed in settings |
| **Automated with notification** | AI acts and tells the user afterward | Actions that are medium-stakes or require user awareness | Clear notification with what happened; undo within a time window |
| **Suggested with accept/reject** | AI proposes; user confirms | High-stakes actions, any action that affects data the user is responsible for, medium-confidence outputs | Visible suggestion; explicit accept and reject controls; context on why |
| **User-initiated with AI assist** | User triggers AI explicitly; AI responds | Tasks where user wants control over when AI is involved; very high-stakes | Clear trigger; no auto-application; user modifies output before committing |

The ladder is not a quality ranking — "fully automated" is not better than "user-initiated."
The appropriate level depends on stakes, reversibility, user expertise, and model confidence.

### Signaling which mode is active

When a feature can operate at multiple levels (e.g., configurable by admin), the UI must
always make the current mode visible. A user who doesn't know whether AI is auto-applying
or just suggesting cannot make informed decisions.

Mode indicator placement:
- In settings/admin surfaces: persistent label showing current mode
- In the working interface: contextual indicator near AI-affected content
- On first encounter after a mode change: notification or dismissible banner

### When to require human confirmation

Require explicit human confirmation when:
- The action affects records the user did not initiate (AI acting on records created by others)
- The action is irreversible or costly to reverse (delete, publish, send)
- The model confidence is below a configured threshold
- Regulatory requirements mandate human decision-making (see Disclosure section)
- The action has downstream effects the user may not anticipate

Do not require confirmation for every AI action — confirmation fatigue leads to users
approving without reading (the "click OK" problem). Reserve confirmations for cases where
the user's review meaningfully reduces error.

---

## AI Disclosure Requirements

### Regulatory context

**GDPR Recital 71**: When automated processing (including AI) is used to make decisions
that significantly affect individuals, those individuals have the right to obtain human
intervention, express their point of view, and contest the decision. Enterprise SaaS
serving EU users must design for this right.

**EU AI Act Article 50**: Requires transparency when AI systems interact directly with
natural persons — specifically, disclosing that the user is interacting with an AI
system (not a human), and disclosing AI-generated content in defined contexts.

**What this means for UI design**: AI-assisted decisions must be disclosed. "Disclosed"
means the user can reasonably understand that an AI was involved. Hiding AI involvement
in a system that makes significant decisions is a legal and ethical problem.

### What to disclose, where, and how

| Disclosure type | Where | How |
|---|---|---|
| AI involvement in a specific suggestion | Adjacent to the suggestion | Inline label ("AI suggested") |
| AI involvement in a decision | In the decision record or audit trail | "Generated by AI on [date]" in record metadata |
| AI system used in a feature | Feature settings or information section | Disclosure text; link to more information |
| AI limitations and error rates | When user first uses the feature | Onboarding disclosure; persistent link to limitations page |

**Inline label vs. modal disclosure**:
- **Inline label**: for per-instance disclosure ("AI suggested this value") — always visible without interaction
- **Modal/disclosure panel**: for system-level disclosure (what AI system, what data it uses, limitations) — accessible but not blocking

Don't put system-level disclosure in a modal that blocks every use. Put it in a
persistent, findable location and link to it from inline labels.

### The "explain this" affordance

When AI makes a suggestion, users often need to understand why. Design for this:
- "Why did AI suggest this?" link or icon adjacent to AI-generated content
- The explanation should be in plain language, not model internals
- For rule-based AI: show the rule ("This field was suggested based on the product category you selected")
- For LLM-based AI: show the input context that informed the output ("Based on the product name and description")
- The explanation does not need to expose model weights or internals — it needs to tell the user what information the model used

---

## Streaming Response UX

### Streaming delivery modes

| Mode | Description | UX implication |
|---|---|---|
| **Character-by-character** | Output appears one character at a time | Creates "typewriter" effect; smooth but CPU-intensive at scale |
| **Chunk streaming** | Output arrives in token batches | Small visual "jumps" as chunks arrive; acceptable if chunks are small |
| **Result-when-ready** | Output appears complete when generation finishes | No streaming effect; suitable for short, fast generations |

Character-by-character and chunk streaming are appropriate when:
- Generation takes more than 2 seconds (users need feedback that the system is working)
- The content is long enough to benefit from reading-while-generating
- The completion time is variable and unpredictable

Result-when-ready is appropriate when:
- Generation is consistently fast (under 1–2 seconds)
- The output is short (a label, a classification, a score)
- The streaming effect would feel artificial for the content type

### Skeleton vs. progressive disclosure for AI-generated content

**Skeleton loading**: appropriate when the layout and size of the AI output is predictable.
Show placeholders that match the approximate shape of the output (a 2-line text skeleton
for a product description, a 3-column card skeleton for a generated report section).

**Progressive disclosure**: appropriate when the content arrives in structural chunks
(heading, then paragraphs, then table). Render each structural element as it arrives.

**Blank-to-streaming**: avoid a blank space that suddenly fills with streaming text.
Always show a "Generating..." indicator or skeleton before the first token arrives.

### When to show thinking/loading states

- **Under 1 second**: no loading state needed; result-when-ready is appropriate
- **1–3 seconds**: button loading state + inline "Generating..." indicator near the output area
- **3–10 seconds**: progress indicator with an estimate ("Usually takes 5–10 seconds")
- **10+ seconds**: persistent progress state; offer cancellation; consider background job pattern

For very long generations (report generation, bulk AI operations): use background job
pattern with notification on completion rather than blocking the user in a waiting state.

### Cancellation affordance

Any generation that takes more than 3 seconds must have a visible cancel control. Users
who change their mind after triggering a generation should not have to wait for completion.

Cancellation design requirements:
- Cancel button must be visible and accessible throughout the generation
- On cancel: stop generation, show partial output if useful, or discard if partial output
  is worse than none
- Cancel is not an error — don't show an error state for a user-initiated cancellation

---

## AI Error States

### Taxonomy of AI failure modes

AI systems fail in ways deterministic systems don't. Each failure mode has a distinct
design response.

| Failure mode | What it means | What to show |
|---|---|---|
| **Model unavailable** | The AI service is down or unreachable | System error message; offer to retry or fall back to non-AI path |
| **Context limit exceeded** | Input was too long for the model | Explain the limit in plain terms; offer to shorten input or split the task |
| **Content filtered** | Output was blocked by content policy | Acknowledge without revealing filter details; offer alternative approach |
| **Low-confidence output** | Model completed but confidence is below threshold | Show output with confidence indicator; require human review before applying |
| **Hallucination risk** | Structured output doesn't match expected schema or contains suspicious values | Surface anomalies for review; don't silently apply output that fails validation |
| **Timeout** | Generation took too long and was stopped | Partial output options; retry; background processing alternative |

### The "I don't know" affordance

For AI features where the model may lack sufficient context to make a reliable suggestion,
design an explicit "I don't have enough information" state — not a low-confidence suggestion,
but a direct statement that the AI cannot make a useful suggestion for this case.

This state reduces over-trust: a model that sometimes says "I can't suggest this reliably"
signals that its other suggestions are trustworthy. A model that always produces output,
even when it shouldn't, trains users to not trust any of it.

What this looks like in UI:
- "AI couldn't suggest a value for this field. The product category may be too specific
  for the current training data."
- Not a failure message — a contextually appropriate non-answer

---

## Trust Calibration

### The two failure modes

**Over-trust**: the user accepts AI output without review. Consequences: errors propagate,
user attributes AI mistakes to their own, trust collapses when errors are discovered.

**Under-trust**: the user never uses AI features. Consequence: the feature investment is
wasted; users do work manually that the AI would do faster and comparably well.

Both are design problems. The goal is calibrated trust: users trust AI output in proportion
to its actual reliability.

### How UI design influences trust

Design choices that increase trust (appropriate if model is reliable):
- Consistent labeling of AI content (users learn to recognize what AI produces)
- Transparency about inputs and reasoning
- Visible track record (e.g., "AI was correct in 94% of similar cases")
- Easy editing of AI output (signals AI is a draft, not a decision)

Design choices that decrease trust (appropriate if model is unreliable or stakes are high):
- Prominent "review required" indicators
- Required confirmation before applying AI suggestions
- Easy rejection/override with zero friction

Design choices that accidentally miscalibrate trust:
- Hiding the AI label after first-use acceptance (out-of-sight, out-of-mind → over-trust)
- Making rejection so frictionless that users never engage with AI output → under-trust
- Using identical visual weight for high-confidence and low-confidence suggestions → over-trust

### Audit trails and provenance

When users need to understand what input produced what output:
- Log the context (inputs) used to generate AI output along with the output itself
- For AI-assisted decisions: the audit trail must include "AI suggested [X] based on [inputs] on [date]"
- This is a backend requirement that must be surfaced at the design layer — flag it to
  engineering early (→ `fe-state-management`, `be-api-design`)

### Feedback mechanisms

**Explicit feedback** (thumbs up/down, rating):
- Appropriate when the feedback is visible to the user and they understand it improves the model
- Place feedback controls adjacent to AI output — not buried in a menu
- Don't ask for feedback on every interaction; ask when it's meaningful (low-confidence outputs, first uses, unusual suggestions)

**Implicit feedback** (editing AI output):
- When a user edits AI output, that edit is signal. Design for its capture.
- "You edited this field — was the AI suggestion unhelpful?" — opt-in capture after edit
- This is a `be-api-design` + ML pipeline concern; surface it in design requirements

---

## Prompt Exposure in Enterprise UI

### When to show the prompt

Show the prompt to users when:
- The prompt is user-editable (the user's prompt is the primary input to the feature)
- Transparency about what was sent to the model is required by policy or regulation
- The user needs to understand why the output is what it is (prompt as explanation)

Hide the prompt when:
- The prompt is a system construct that wraps user-supplied data (showing it adds noise without value)
- The prompt contains system instructions the user should not modify
- The prompt includes sensitive context (other users' data, system configuration)

### Prompt templates as reusable configurations

In enterprise SaaS, users often perform the same AI-assisted task repeatedly with slight
variations. Prompt templates solve this:
- Template = saved prompt with variable slots ("Generate a product description for [product name] in [tone] voice")
- Templates are configured by admins and available to end users
- Template management is an admin surface; template use is an end-user surface

Design requirements for template-based prompts:
- Variable slots must be clearly marked and editable (a form, not a text editor)
- Templates must be nameable and searchable at scale (enterprise teams will accumulate many)
- Template outputs should still be labeled as AI-generated

### Conversational UI vs. form-based AI input

**Conversational UI** (chat, free-text prompt box) is appropriate for:
- Open-ended tasks where the user's intent is variable and hard to specify in advance
- Tasks that require clarification or follow-up (multi-turn by nature)
- Exploratory tasks where the user doesn't know exactly what they want

**Form-based AI input** is appropriate for:
- Structured tasks with predictable inputs (generate a product description: name, category, tone)
- Enterprise workflows where consistent outputs are more valuable than flexible inputs
- Cases where users are not comfortable with prompt engineering

For most enterprise SaaS: form-based input with optional free-text override is the better
default. Conversational UI creates a "blank page problem" for users who don't know how to
prompt effectively.

---

## AI Feature Discovery and Onboarding

### The trust bootstrapping problem

AI features face a trust bootstrapping problem that other features don't: users can't
trust AI outputs until they've seen enough of them to calibrate, but they won't use the
feature enough to calibrate if they don't trust it.

Design strategies:
- **Show, don't tell**: surface AI suggestions passively before asking the user to act on them
  ("Here's what AI would have suggested for the last 3 products you entered")
- **Low-stakes first use**: introduce the feature in the lowest-stakes context first
  (a suggestion in a non-critical field, not the primary product identifier)
- **Progressive capability disclosure**: start with the most reliable, most obvious use
  case — not the most impressive one

### The "AI suggested this" badge

The disclosure badge on AI-generated content serves two audiences simultaneously:
- **Trust-building**: for users who are learning to calibrate — the badge makes AI
  involvement visible and creates a mental model of what AI produces well
- **Trust-inducing anxiety**: for users who are skeptical — the badge highlights that
  the content is uncertain rather than established

Design for both:
- Badge must be visible but not alarming — use a neutral indicator, not a warning icon
- Badge should link to an explanation or feedback mechanism
- Allow users to dismiss or hide badges after they've calibrated (some users will want
  to "graduate" out of seeing constant AI labels)

### Progressive disclosure of AI capability

Don't surface all AI features at once. Sequence:

1. **Passive discovery**: AI suggestions appear in context without requiring the user to invoke them
2. **Active first use**: user explicitly tries the feature on a safe task
3. **Expanded use**: user adopts the feature in their regular workflow
4. **Configuration**: user or admin customizes behavior (thresholds, templates, automation level)

Onboarding that front-loads all AI capabilities with a feature tour is less effective than
letting users encounter features at the moment they're relevant.

---

## Cross-Links

- `ux-interaction-design` — human-in-the-loop confirmation patterns; error state interaction design
- `ds-nlp-llm` — model capability and limitation constraints that directly affect what UX is feasible
- `pm-platform-api` — AI feature API surface design; disclosure requirements at the platform level
- `ux-accessibility` — AI output and cognitive accessibility; plain language for AI-generated content
- `fe-state-management` — streaming state management; optimistic UI for AI suggestions; undo after AI auto-apply

---

## References

- EU AI Act, Article 50 — Transparency obligations: https://artificialintelligenceact.eu/article/50/
- GDPR Recital 71 — Automated decision-making: https://gdpr-info.eu/recitals/no-71/
- Nielsen Norman Group — AI UX: https://www.nngroup.com/topic/artificial-intelligence/
- Google PAIR Explorables — People + AI Research: https://pair.withgoogle.com/explorables/
- IBM Design for AI — Guidelines: https://www.ibm.com/design/ai/
- Ethan Mollick — Co-Intelligence (on human-AI collaboration norms)
- Ben Shneiderman — Human-Centered AI (book)
