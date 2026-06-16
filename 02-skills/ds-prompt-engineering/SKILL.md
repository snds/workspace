---
name: ds-prompt-engineering
description: >
  Prompt engineering as a production discipline for LLM systems. Staff/principal IC level.
  Use this skill whenever the conversation touches: system prompt architecture, prompt
  versioning, few-shot example design, dynamic few-shot retrieval, output format contracts,
  JSON schema enforcement, structured output, Instructor, Outlines, guidance-ai, prompt
  A/B testing, evaluation harness design, golden datasets, LLM-as-judge for prompt eval,
  prompt regression, ROUGE, BERTScore, chain-of-thought prompting, zero-shot CoT, ReAct
  pattern, self-consistency sampling, Tree of Thought, token budget optimization, prompt
  caching (Anthropic, OpenAI), model routing, batch inference, RAG prompt design, context
  window management, citation prompts, agentic prompt patterns, tool-calling prompt design,
  multi-agent orchestration prompts, reflection prompts, or any question about designing
  prompts that hold up in production at scale.
  This skill covers prompt engineering craft — not NLP/LLM pipeline architecture
  (ds-nlp-llm), not LLM as a product decision (pm-platform-api).
hub: lead-data-scientist
aliases: [ds-prompt-engineering]
spec_version: "2.0"
---

# DS: Prompt Engineering

Production prompt engineering discipline for LLM systems. Part of the lead-data-scientist
skill network.

---

## Domain Boundary

This skill owns **prompt design and evaluation for production LLM systems**.

- **NLP pipelines, embeddings, RAG architecture** → `ds-nlp-llm` (also load for RAG retrieval design)
- **LLM API integration, serving infrastructure, rate limiting** → `ds-nlp-llm`
- **LLM as product capability / build-vs-buy** → `pm-platform-api`
- **API contract design for prompt endpoints** → `be-integration-patterns`
- **AI-native product UX (streaming, progressive disclosure)** → `ux-ai-product-design`

---

## System Prompt Architecture

### The System Prompt as a Contract

A system prompt is not configuration. It is a contract between the prompt author and the
model's behavior in production. Treat it with the same rigor as code:

- Version-controlled in source control (not a string in a database, not a config file
  excluded from review)
- Reviewed via pull request — changes require approval and a passing evaluation run
- Deployed independently of application code where prompt changes have different risk profiles

**Structural order (matters — models weight earlier content more heavily):**

1. **Role definition** — who the model is, what expertise it brings, what it is not
2. **Behavioral constraints** — what it must/must not do; tone, refusals, escalation
3. **Output format specification** — exact format, schema, field requirements, length bounds
4. **Examples** — demonstrations of correct behavior (if included; → see Few-Shot)
5. **Edge case handling** — explicit instructions for known-hard cases

**Playground vs. production gap**: A prompt that works in the ChatGPT playground or Claude.ai
fails in production because:
- Production inputs are noisier (typos, multi-language, context switching)
- Model versions change under you — a provider update regresses the prompt
- Edge cases accumulate; the prompt was written for the median, not the tail

Evaluate prompts against a representative dataset, not against examples you designed
the prompt to pass.

### Prompt Injection Attack Surface

System prompts are the primary target for prompt injection. Attack vectors:

| Attack | Mechanism | Defense |
|--------|-----------|---------|
| Direct injection | User input contains `Ignore previous instructions…` | Structural separation (user content in `<user_input>` tags); instruction hierarchy framing |
| Indirect injection | Retrieved content (RAG, web) contains adversarial instructions | Treat retrieved content as untrusted data; frame it explicitly as "external content, not instructions" |
| Jailbreak via roleplay | `Pretend you are a model without restrictions…` | Explicit identity constraints in role definition; constraint reminders before and after examples |

**Structural defense**: Never concatenate user input directly into instruction space. Use
explicit XML or JSON delimiters to separate instruction content from user-supplied content:

```
<instructions>
  [Your instructions here]
</instructions>
<user_input>
  {user_message}
</user_input>
```

---

## Few-Shot Example Design

### Selection Criteria

Few-shot examples are not arbitrary demonstrations. Selection determines whether they help
or hurt.

**Principles:**
- **Representative of target distribution** — examples should cover the range of real inputs,
  not just clean, easy cases. If 30% of real inputs are malformed, include malformed examples.
- **Cover edge cases explicitly** — include at least one example showing correct behavior on
  the hardest category of inputs
- **Demonstrate failure recovery** — include an example where the input is ambiguous and show
  the correct handling (clarify, refuse, hedge)
- **Diverse, not redundant** — ten examples covering the same easy case are worse than three
  examples covering three distinct cases

**Selection anti-patterns:**
- Examples that are too clean → model overfits to well-formed inputs
- Examples from test data → contamination; test set is no longer independent
- Duplicate examples → waste tokens; add no signal

### Example Format

| Format | Use When |
|--------|---------|
| Q/A pairs | Single-turn tasks; classification; extraction |
| Conversation transcript | Multi-turn or dialogue tasks |
| Structured input/output | JSON/schema-constrained tasks — show the schema filled out |

The format of the example should match the expected production format exactly. If production
calls arrive as JSON, examples should be in JSON. Format mismatch between examples and
production inputs is a reliability risk.

### Dynamic Few-Shot Selection

Static few-shot examples (hardcoded in the prompt) are a ceiling. Dynamic selection retrieves
examples at inference time based on similarity to the current input.

**Implementation:**
1. Pre-embed all examples in your example library using the same embedding model as retrieval
2. At inference time, embed the current input
3. Retrieve top-K most similar examples by cosine similarity
4. Inject retrieved examples into the prompt before the user turn

**When to use**: Tasks with high input diversity (many distinct categories); when a static
pool of examples can't cover all categories without exceeding the context window.

**Diminishing returns**: Studies show diminishing returns beyond 4–8 examples for most
classification and extraction tasks. For generation tasks, more examples help longer but
subject to context window pressure. Measure accuracy vs. example count on your eval set
before adding more.

---

## Output Format Contracts

### JSON Schema Enforcement

For any output that feeds downstream application logic, enforce structure at the API level —
not by parsing the model's freeform text.

| Tool | Mechanism | Notes |
|------|-----------|-------|
| OpenAI Function Calling | `tools` parameter with JSON schema; model fills arguments | Guaranteed schema conformance since `strict: true` |
| OpenAI `response_format` | `{"type": "json_schema", "json_schema": ...}` with `strict: true` | Direct structured output without function framing |
| Anthropic Tool Use | Tool definition with input schema; model returns tool call | Same guarantees as OpenAI function calling |
| Instructor (Python) | Pydantic model → prompt injection + response validation + retry | Works across providers; validation via Pydantic v2 |
| Outlines | Token-level constrained decoding (open-source/local models) | Guarantees schema at generation time, not just validation |
| guidance-ai | Grammar-constrained generation; interleaved control flow | Most powerful for complex constrained generation; higher complexity |

**When structured output is the default**: Any time the output drives business logic,
databases, downstream APIs, or UI rendering. Freeform text output is acceptable only when
the output is purely human-readable with no further programmatic use.

**Anti-pattern**: Using regex to extract JSON from freeform output. This is brittle and
fails on any output format variation. If the model can output structured JSON natively,
use that path.

### Streaming Structured Data

Streaming + structured output creates a tension: JSON is only valid when complete, but
streaming delivers partial tokens.

Solutions:
- **Token-by-token streaming + accumulate**: Buffer all tokens, parse the complete JSON on
  completion. Works for structured output; the UX benefit of streaming is eliminated unless
  you progressively render completed fields.
- **Field-level streaming**: Structure output so human-readable fields come first (rendered
  progressively), metadata/IDs come last (parsed after complete).
- **Partial object parsing**: `Instructor` supports `Partial[MyModel]` streaming — renders
  whatever fields have completed so far.

### Output Validation as a Production Requirement

LLM output must be validated before being consumed by application logic. Even with schema
enforcement, validate:
- Required fields are present and non-null
- Enum fields contain only allowed values
- Numeric fields fall within expected ranges
- Text fields meet length constraints

Validation failures should trigger a retry (with or without a modified prompt) rather than
passing bad data downstream. Log all validation failures — they are a signal that the prompt
is failing to produce compliant output on real inputs.

---

## Prompt Versioning and Evaluation

### A/B Testing Prompts

Treat prompt changes as feature releases:
- Controlled rollout: serve the new prompt to X% of traffic
- Hold out a comparison cohort on the existing prompt for the same time window
- Define the primary metric before the test (quality score, task completion rate, error
  rate, user satisfaction) — do not choose the metric after seeing results
- Statistical significance before declaring a winner — same rules as product A/B tests

**Metric hierarchy**: Human eval > LLM-as-judge > automated metric (ROUGE, BERTScore).
Use automated metrics for regression detection (fast, cheap), human eval for shipping
decisions.

### Evaluation Harness Design

**Golden dataset construction:**
- 50–300 examples minimum (more for high-stakes applications)
- Stratified across input categories — do not allow easy cases to dominate
- Labeled with: input, expected output, evaluation rubric or reference
- Built from real production inputs (not synthetic) once production data is available
- Maintained: add examples when new failure modes appear; never delete examples

**Evaluation metrics by task type:**

| Task | Primary Metric | Secondary |
|------|---------------|-----------|
| Classification | F1 per class, macro-F1 | Confusion matrix |
| Extraction | Exact match, token-level F1 | Precision/recall per field |
| Summarization | ROUGE-L, BERTScore | LLM-as-judge faithfulness |
| Generation (open-ended) | LLM-as-judge (rubric scoring) | Human eval |
| RAG answers | RAGAS faithfulness + relevancy | Citation accuracy |

**LLM-as-judge calibration**: Biases include length preference (longer = better), position
bias in pairwise (first option preferred), and self-preference (model prefers its own style).
Mitigations: randomize pairwise order, use rubric scoring over pairwise when possible,
cross-validate with human eval on a sample.

### Prompt Regression as a Deployment Risk

Model provider updates (API model updates, fine-tune refreshes) can silently break prompts
that previously worked. Defense:

1. **Lock model versions in production** — never use `gpt-4-latest`; pin to
   `gpt-4o-2024-08-06` or equivalent dated version
2. **Run eval suite on every model version upgrade** before routing traffic
3. **Monitor production quality metrics continuously** — LLM-as-judge on a sample of live
   traffic; alert on degradation
4. **Prompt registry with rollback** — store versioned prompts in a registry (git-tracked
   file, database row with version column); rollback is a config change, not a code deploy

---

## Chain-of-Thought and Reasoning Patterns

### Zero-Shot CoT

Appending "Let's think step by step" or "Think through this carefully before answering"
to a prompt.

**When it helps**: Multi-step arithmetic, logical reasoning, structured analysis tasks.
**When it's noise**: Simple classification, extraction, lookup tasks. CoT adds latency
and tokens without improving a task that requires no reasoning.

**Implementation**: Put the CoT instruction at the end of the user turn, after the
question. Instruct the model to output reasoning in `<thinking>` tags and the final
answer separately — this lets you parse structured output while preserving reasoning.

### ReAct (Reasoning + Acting)

Alternating reasoning steps ("Thought: …") and action steps ("Action: search(…)") in an
agentic loop. Enables the model to plan, observe tool results, and revise.

**When to use**: Any agentic task where the model needs to take sequential tool calls
based on intermediate results. ReAct is the standard pattern for tool-using agents.

**Implementation requirements**:
- Clear format definitions for Thought/Action/Observation steps (the model must output
  parseable action syntax)
- Termination conditions (max steps, success signal)
- Error handling in the Observation step (what the model sees when a tool call fails)

### Self-Consistency Sampling

Generate N independent completions for the same prompt; take the majority answer.

**When to use**: High-stakes reasoning tasks where accuracy matters more than cost.
Math, code generation, factual questions with deterministic answers.
**Cost**: N× inference cost. Use temperature > 0 to get diverse samples. N=5–10 is typical.
**Limitation**: Only useful when answers aggregate cleanly (majority vote). Does not apply
to open-ended generation.

### Tree of Thought

Generates and evaluates multiple reasoning branches rather than a single chain. More
powerful than self-consistency for complex planning and search tasks.

**When to use**: Creative planning, multi-constraint problem solving, tasks where the
right path is not obvious from a linear chain. Rare in production — high cost and
complexity.
**Implementation**: Requires orchestration code to prompt for branch generation,
pruning/evaluation, and expansion. Not a single prompt pattern.

---

## Cost and Latency Optimization

### Token Budget Management

System prompt tokens are paid on every request. Compress without losing behavior:

- Remove redundant instructions that repeat the same constraint in different words
- Use examples to convey format requirements rather than prose descriptions of format
- Move low-frequency edge case handling to a retrieval system (fetch the relevant
  instruction at runtime) rather than including it in the base system prompt
- Measure: run the compressed prompt against the eval suite before shipping; if quality
  holds, ship

**Target**: System prompt under 1,000 tokens for high-volume applications where cost matters.
Below 512 tokens for extremely high-volume (>10M requests/month).

### Prompt Caching

Prompt caching dramatically reduces cost for prompts with stable prefixes (system prompt,
knowledge base context, static few-shot examples).

| Provider | Mechanism | Cache Threshold | Cost |
|----------|-----------|----------------|------|
| Anthropic | Explicit `cache_control` breakpoints in the message | 1,024 tokens minimum | 10% of input token cost for cache reads |
| OpenAI | Automatic caching; no explicit control | 1,024 tokens minimum | 50% of input token cost for cache reads |

**Maximizing cache hit rate**:
- Put the stable content (system prompt, retrieved knowledge base) at the beginning of
  the prompt
- Put dynamic content (user message, session context) at the end
- The longest stable prefix that fits the cache window gets cached — don't intersperse
  dynamic content through the stable section

**Expected savings**: Up to 80–90% reduction in input token cost for high-traffic
applications with a stable system prompt and a cache hit rate above 80%.

### Model Routing

Not every request needs the most capable (and expensive) model.

**Routing patterns:**

| Pattern | Mechanism | When to Use |
|---------|-----------|------------|
| Complexity routing | Classify query complexity; route simple → small model, complex → large | High-volume apps with a known mix of simple and complex queries |
| Intent classification | Fast classifier (small model or rule-based) determines intent; route to specialist | Multi-intent apps where different query types need different prompts |
| Quality cascade | Small model attempts first; if confidence below threshold, escalate to large model | When most queries are simple; rare escalation is acceptable |

**Small model options** (fast, cheap, good for routing/classification): GPT-4o-mini,
Claude Haiku, Gemini Flash, Mistral Small.

### Batch Inference

For offline tasks (nightly processing, bulk enrichment, report generation), batch inference
avoids real-time latency requirements and enables cost optimization:
- **Anthropic Batch API**: 50% discount on input/output tokens; results returned
  within 24 hours
- **OpenAI Batch API**: 50% discount; 24-hour turnaround
- Use for: dataset enrichment, content classification at scale, embedding generation,
  bulk document processing

---

## RAG Prompt Design

### The Retrieval-Augmented Prompt Structure

Standard RAG prompt structure:

```
[System: role + behavioral constraints + output format]

Retrieved Context:
<context>
[Chunk 1 — with source label if citations required]
[Chunk 2]
...
</context>

User Question: {user_query}

Instructions: Answer based only on the provided context. If the context doesn't contain
the answer, state that explicitly. Do not use prior knowledge.
```

**Context placement**: Retrieved context before the user question. Models attend more
reliably to content that precedes the question than content that follows it.

### Context Window Management

| Parameter | Guidance |
|-----------|---------|
| Number of chunks | Start with K=5; measure recall@K on eval set; increase only if recall is failing |
| Chunk order | Highest-relevance chunks first and last (lost-in-the-middle effect — models attend less to middle of context) |
| Token budget | Leave at least 20% of context window for system prompt + question + output headroom |
| Reranking | Always rerank retrieved chunks before truncation; don't truncate based only on retrieval score |

**Lost-in-the-middle**: Research shows LLMs attend most reliably to context at the
beginning and end of the context window. If you must fit many chunks, put the highest-
relevance chunks at positions 1 and K (first and last).

### Citation and Grounding Prompts

For applications where the model must be traceable to source material:

```
For each claim in your answer, cite the source chunk using [Source N] notation.
Only make claims that are directly supported by the provided context.
If you cannot find support for a claim in the context, omit the claim rather than
citing knowledge not present in the retrieved documents.
```

**Validation**: After generation, verify that cited chunks actually contain the claimed
information. This can be automated with a secondary LLM-as-judge pass.

### Handling Contradictions

When retrieved context contradicts the model's internal knowledge or other retrieved chunks:

- Instruct the model explicitly: "If retrieved sources contradict each other, present both
  perspectives and note the disagreement rather than resolving it silently."
- For high-stakes applications, flag contradiction as a quality signal and route to
  human review rather than allowing the model to arbitrate.

---

## Agentic Prompt Patterns

### Tool/Function Calling Prompt Design

System prompt requirements for tool-using agents:
- List available tools with: name, description, when to use, when NOT to use, argument
  schema, and expected output format
- Define the action selection policy: "If the query can be answered from context alone,
  do not call a tool. Only call a tool when retrieval or computation is required."
- Define the tool call format explicitly if the API doesn't enforce it (for non-native
  function-calling models)

**Common failures**:
- Model calls tools unnecessarily (hallucinating that a tool call is needed) — add explicit
  "don't call unless necessary" instructions and a cost signal
- Model calls tools with malformed arguments — add examples of correct tool calls with
  properly typed arguments

### Multi-Agent Orchestration Prompts

**Router → Specialist pattern:**

Router system prompt: defines all available specialists, routing criteria (what each
specialist handles), and output format for the routing decision.

Specialist system prompt: scoped to one domain; does not need awareness of other specialists.
Clean interface boundaries prevent routing leakage between specialisms.

**Orchestrator system prompt** (for an orchestrator managing multiple agents):
- Define the task decomposition logic
- Define handoff format (how the orchestrator packages context for a specialist)
- Define aggregation logic (how specialist outputs are combined)
- Define stopping conditions and error recovery

### Reflection Prompts

Asking the model to critique its own output before finalizing it.

**Pattern**:
```
[Generate response]
Now review your response above. Check:
- Does it directly answer the question?
- Is every claim supported by the provided context?
- Is the format correct?
Revise and output the corrected version.
```

**When useful**: Long-form generation where quality matters more than latency; factual
tasks where self-correction catches known error types.
**Cost**: 2× inference cost. Measure quality improvement against cost before defaulting
to it.

### Error Recovery in Agentic Loops

Agentic tasks fail mid-loop. Prompts must handle:
- Tool call failure (API error, timeout): "If a tool call fails, retry once with the
  same arguments. If it fails again, attempt an alternative approach or report the
  failure."
- Unexpected tool output format: "If the tool output is not in the expected format,
  extract the relevant information as best you can and note the format discrepancy."
- Stuck loops (model repeats the same action): Detect via loop counter; inject "You
  have tried this approach N times. Try a different approach."

---

## Common Failure Modes

| Failure | Mechanism | Prevention |
|---------|-----------|-----------|
| Prompt regression on model update | Provider updates model weights silently | Pin model versions; run eval suite on upgrade |
| Instruction-following collapse on complex prompts | Too many competing constraints in one prompt | Prioritize constraints; simplify; split into sequential prompts |
| Example contamination | Test examples appear in the few-shot pool | Strict train/test split for example library |
| Cache miss from dynamic content in stable section | Dynamic tokens inserted mid-prompt break cache prefix | Move all dynamic content to end; keep stable section contiguous |
| Format non-compliance on edge inputs | System prompt format spec not robust enough | Add explicit examples of edge-case formatting; use schema enforcement |
| Prompt injection via retrieved content | RAG context contains adversarial instructions | Frame retrieved content as data, not instructions; use XML delimiters |
| Over-reliance on CoT for simple tasks | Adds latency/cost with no quality gain | Measure CoT vs. no-CoT on eval set; default off for simple tasks |

---

## Cross-Hub References

- For NLP pipelines, embeddings, and RAG architecture → `ds-nlp-llm`
- For LLM as product feature / API strategy → `pm-platform-api`
- For API design for prompt endpoints → `be-integration-patterns`
- For AI-native product UX patterns → `ux-ai-product-design`
- For caching infrastructure → `be-caching-performance`
