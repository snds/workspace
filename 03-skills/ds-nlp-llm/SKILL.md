---
name: ds-nlp-llm
description: >
  NLP pipelines, text classification, embeddings, vector search, RAG architecture, LLM
  integration patterns, and evaluation for enterprise SaaS. Use this skill whenever the
  conversation touches: text classification, sentiment analysis, zero-shot classification,
  few-shot prompting, fine-tuning, BERT, sentence-transformers, embeddings, vector
  databases, semantic search, dense retrieval, sparse retrieval, BM25, hybrid search,
  RAG, retrieval-augmented generation, chunking strategy, RAGAS evaluation, LLM API
  integration, OpenAI, Anthropic, Cohere, prompt engineering at scale, prompt caching,
  structured output, JSON mode, function calling, LLM-as-judge, streaming responses,
  LLM fallback chains, PII detection, presidio, NER, spaCy, or any question about
  building NLP or LLM-powered features in an enterprise product at production scale.
  This skill covers NLP/LLM engineering — not general ML serving infrastructure
  (ds-ml-engineering), not LLM as a product management decision (pm-platform-api).
aliases: [ds-nlp-llm]
spec_version: "2.0"
---

# DS: NLP & LLM Engineering

Specialist lens for NLP pipelines and LLM integration in enterprise SaaS. Part of the
lead-data-scientist skill network.

---

## Domain Boundary

This skill owns **NLP pipeline engineering and LLM integration patterns**.

- **ML serving infrastructure** → `ds-ml-engineering` (also load for serving a fine-tuned model)
- **LLM capability as product strategy** → `pm-platform-api`
- **LLM API key management** → also engage `be-auth-patterns`
- **Streaming response handling in API design** → also engage `be-api-design`
- **Prompt/response semantic caching** → also engage `be-caching-performance`
- **Analytical NLP (topic modeling, sentiment on product data)** → `ds-product-analytics`

---

## Text Classification: Pipeline Selection

Start with the simplest option that meets the accuracy and cost requirements. Move right
only when you've validated the simpler approach is insufficient.

### Decision Matrix

| Approach | Best For | Accuracy | Cost/Call | Latency | Data Required |
|----------|----------|----------|-----------|---------|---------------|
| Zero-shot LLM | Prototyping, low volume, novel categories | Moderate | High | 500ms–2s | None |
| Few-shot prompting | Better accuracy with examples, still LLM-dependent | Good | High | 500ms–2s | 5–50 examples |
| Fine-tuned BERT-class | High volume, stable categories, cost-sensitive | Best | Very low | 10–50ms | 100–10K examples |
| Full LLM fine-tuning | Rarely justified for classification | Best | High infra cost | Fast after deploy | 10K+ examples |

**Enterprise decision point**: At what volume does zero-shot LLM become too expensive?
At $0.001/call (GPT-4o-mini class), 1M calls/month = $1K. At $0.01/call (GPT-4 class),
1M calls/month = $10K. Fine-tuning a DistilBERT or RoBERTa for $50–200 of GPU time and
running at <1ms CPU inference is often the right answer for classification at scale.

### Fine-Tuning a Classifier (BERT-class)

Pipeline steps:
1. Label schema definition: is the label exhaustive? Mutually exclusive? Multi-label?
2. Label quality: inter-annotator agreement (Cohen's kappa > 0.7 is the standard bar)
3. Train/validation/test split — stratified by class; do NOT shuffle time-ordered data if
   documents arrive in time-dependent batches
4. Baseline: logistic regression on TF-IDF vectors. If fine-tuned BERT doesn't beat this
   by a meaningful margin, the task may not benefit from deep features.
5. Fine-tune: `transformers` Trainer API or Lightning; learning rate ~2e-5 for BERT,
   ~1e-4 for smaller models; freeze early layers if labeled data is limited (<500 examples)
6. Calibration: `sklearn.calibration.CalibratedClassifierCV` or temperature scaling if
   confidence scores will be used downstream (probability outputs from softmax are not
   calibrated by default)
7. Evaluation: per-class precision/recall (overall accuracy is misleading for imbalanced
   classes); confusion matrix; error analysis on FN/FP examples

---

## Embedding Models and Vector Search

### Model Selection

| Model | Use Case | Dimensions | Notes |
|-------|----------|-----------|-------|
| `text-embedding-3-small` (OpenAI) | Cost-effective semantic search | 1536 (reducible) | Strong baseline; MRL allows dimension reduction |
| `text-embedding-3-large` (OpenAI) | High-accuracy retrieval | 3072 | Best OpenAI benchmark scores; 2x cost |
| `sentence-transformers/all-MiniLM-L6-v2` | On-prem, low latency | 384 | Fast, decent quality; good for high-volume CPU inference |
| `sentence-transformers/all-mpnet-base-v2` | On-prem, better quality | 768 | Better accuracy than MiniLM; moderate speed |
| `embed-english-v3.0` (Cohere) | RAG with reranking | 1024 | Pairs well with Cohere reranker |

**Domain specificity matters**: General embedding models perform poorly on domain-specific
terminology (legal, medical, PLM). Fine-tune embeddings with contrastive learning
(triplet loss, in-batch negatives) on domain pairs if baseline retrieval quality is poor.

### Dense vs. Sparse Retrieval

| Approach | Strength | Weakness |
|----------|----------|---------|
| Dense (embedding-based) | Semantic similarity, handles synonyms, paraphrases | Misses exact keyword matches; requires GPU for high-volume indexing |
| Sparse (BM25/TF-IDF) | Exact keyword match, proper nouns, product codes | No semantic understanding; fails on paraphrases |

**BM25 is still competitive** for search over structured text (product names, codes,
identifiers). Don't replace it with embeddings without measuring the accuracy change.

### Hybrid Search

Combines dense and sparse retrieval for the best of both.

**Reciprocal Rank Fusion (RRF)** is the standard approach:
```
RRF_score(d) = Σ 1 / (k + rank_i(d))
```
Where rank_i(d) is the rank of document d in retrieval system i, k=60 is standard.

Alternatively: use a cross-encoder reranker (Cohere Rerank, `cross-encoder/ms-marco-*`)
on the merged top-K candidates from both retrieval systems.

### Vector Database Selection

| Database | Type | Best For | Enterprise Considerations |
|----------|------|----------|--------------------------|
| pgvector | SQL-native (Postgres extension) | Existing Postgres stack, moderate scale (<10M vectors) | No operational overhead; ACID transactions with metadata; limited ANN performance at scale |
| Pinecone | Managed SaaS | Simplicity, fast time to prod | Vendor dependency; cost at scale; no SQL metadata joins |
| Weaviate | Self-hosted or managed | Hybrid search native, GraphQL API | Good multi-tenancy support; operational complexity |
| Qdrant | Self-hosted or managed | High performance, payload filtering | Rust-native; good filtering; strong for on-prem requirements |
| Chroma | Lightweight local | Development, small-scale | Not production-grade for high volume |

**Enterprise default**: Start with pgvector if you're already on Postgres. Migrate to a
purpose-built vector store only when you've hit a genuine scale or performance constraint,
not preemptively.

---

## RAG Architecture

### Chunking Strategy

Chunking determines retrieval quality at the retrieval stage — poor chunking cannot be
compensated by better retrieval.

| Strategy | Description | Use When |
|----------|-------------|---------|
| Fixed-size with overlap | Split every N tokens; overlap M tokens between chunks | Baseline; works for prose; fast to implement |
| Sentence-boundary | Split on sentence endings | Better for content where sentence = coherent unit |
| Semantic (embedding similarity) | Group sentences until embedding similarity drops below threshold | Best quality; slow to compute; requires validation |
| Document structure-aware | Split on headers, sections, logical units | Best for structured documents (docs, knowledge bases) |

Overlap guideline: 10–15% of chunk size. Too little overlap: context cuts across chunk
boundary and the relevant sentence is split. Too much overlap: retrieval returns near-
duplicate chunks with marginally different context.

**Parent-child chunking**: Index small chunks (for retrieval precision) but return the
larger parent chunk (for context completeness) to the generation step. Addresses the
precision-completeness tradeoff.

### Retrieval Quality Evaluation

Never skip retrieval evaluation before optimizing generation. Most RAG failures are
retrieval failures.

| Metric | Definition |
|--------|-----------|
| Recall@K | % of relevant documents appearing in top-K retrieved; measures coverage |
| Precision@K | % of top-K retrieved that are relevant; measures noise |
| MRR (Mean Reciprocal Rank) | Average of 1/rank for first relevant result; measures ranking quality |
| NDCG | Normalized Discounted Cumulative Gain; handles graded relevance |

Build a labeled retrieval evaluation set before tuning. Without a ground-truth set,
embedding/chunking/retrieval parameter changes are unjustified optimization.

### RAG Generation Patterns

Context window management:
- Fit K retrieved chunks within the model's context window with headroom for the
  question and output
- Rerank retrieved chunks before truncation to fill the window with highest-value context
- Long-context models (128K+ tokens) reduce the need for aggressive truncation but don't
  eliminate the need for retrieval evaluation

Faithfulness control:
- Prompt engineering: "Answer only based on the provided context. If the context doesn't
  contain the answer, say so."
- Citation tracking: structure prompt to extract which chunks the answer draws from;
  return citations to the user

### RAGAS Evaluation Framework

RAGAS evaluates RAG pipelines on four dimensions (all automated, using an LLM-as-judge):

| Metric | Measures |
|--------|---------|
| Faithfulness | Is the generated answer grounded in the retrieved context? |
| Answer Relevancy | Does the answer actually address the question? |
| Context Recall | Did retrieval capture all information needed to answer the question? |
| Context Precision | Are the retrieved chunks relevant, or is there noise? |

RAGAS requires: the question, the retrieved context, the generated answer, and (for
context recall) a ground-truth answer. Build a benchmark set and run RAGAS regression
on every pipeline change.

---

## Production LLM Patterns

### Streaming Responses

Use streaming for any user-facing LLM interaction with generation latency > ~2 seconds.
Streaming returns tokens incrementally (SSE or chunked HTTP response) so the user sees
partial output immediately.

Implementation:
- OpenAI: `stream=True` parameter; iterate over `response.choices[0].delta.content`
- Anthropic: `stream=True`; iterate over `MessageStreamEvent`
- Requires the serving layer to support streaming; route to `be-api-design`

### Prompt Caching

Prompt caching reduces cost for prompts with stable prefixes (system prompt, retrieved
context, few-shot examples).

- **Anthropic**: explicit `cache_control` breakpoints; caching charged at 10% of input token cost
- **OpenAI**: automatic caching for prompts > 1024 tokens; no explicit control
- Savings up to 90% on repeated stable prefixes in high-traffic applications

Design cached vs. non-cached sections: system prompt + knowledge base context = cache;
user-specific dynamic content = no cache.

### Fallback Chains

Production LLM applications should not depend on a single provider or model. Design a
fallback chain:

```
Primary: GPT-4o / Claude Sonnet
  → Fallback 1: GPT-4o-mini / Claude Haiku (cheaper, slightly lower quality)
    → Fallback 2: Rule-based or template response (no LLM dependency)
```

Trigger fallback on: rate limit errors, timeout, provider outage, or latency SLA breach.

### Rate Limiting and Retry

LLM API providers impose rate limits (TPM = tokens per minute, RPM = requests per minute).
Strategies:
- Exponential backoff with jitter (not linear retry — linear retry amplifies the spike)
- Token bucket or leaky bucket client-side rate limiter to stay within provider limits
- Request queuing for batch workloads; parallelism limited to TPM headroom
- Track per-user and per-tenant rate limits if exposing LLM functionality to end users

### Structured Output

For any LLM output that feeds downstream parsing or application logic, use structured
output — don't parse freeform prose:
- OpenAI: `response_format={"type": "json_schema", "json_schema": ...}` or function calling
- Anthropic: tool use with typed schema
- Benefit: guaranteed schema conformance; eliminates brittle regex parsing
- Anti-pattern: extracting JSON from freeform text with regex; breaks on any model
  output variation

---

## LLM Evaluation

### LLM-as-Judge

Use a stronger or same-tier LLM to evaluate outputs of a weaker model or pipeline.

Patterns:
- **Pairwise comparison**: "Which of these two responses better answers the question?"
  — reduces to A/B preference; good for ranking models
- **Rubric scoring**: "Score this response on faithfulness (1-5) with reasoning" — better
  for absolute quality measurement
- **Reference-based**: Compare to a gold-standard answer — requires ground truth labels

Calibration: LLM judges have known biases (length bias, position bias in pairwise).
Randomize answer order in pairwise comparisons; check for length correlation with score.

### Regression Suites for Prompt Changes

Any change to a production prompt should run against a regression suite before deployment:
- Curated set of 50–200 representative inputs with known good outputs or rubric scores
- Automated scoring (RAGAS, LLM-as-judge, or heuristic checks)
- Pass/fail threshold: new prompt must not regress on more than X% of cases
- Version control prompts (not in code comments — in a prompt registry or git-tracked
  config file)

---

## PII Handling

Enterprise SaaS data frequently contains PII. PII must not be sent to third-party LLM
APIs without explicit data processing agreements and customer consent.

Detection:
- `presidio` (Microsoft): entity recognition (name, email, SSN, credit card, etc.)
- `spaCy` NER: lighter-weight, customizable
- Pattern-based: regex for structured PII (email, phone, IP addresses)

Before sending to external API:
1. Detect PII entities in input
2. Redact or pseudonymize (replace with entity type placeholder: [PERSON], [EMAIL])
3. If context requires the original PII post-generation, maintain a redaction map for
   re-substitution
4. Log that PII was detected and redacted (for compliance audit trail)

Architectural option: on-premise or VPC-deployed model (Llama variants, Mistral) for
data that cannot leave the tenant's data perimeter.

---

## Common Failure Modes

| Failure | Mechanism | Prevention |
|---------|-----------|-----------|
| Hallucination in RAG | Model generates plausible but unsupported answer; retrieval missed relevant context | Faithfulness evaluation (RAGAS); citation forcing; retrieval quality checks |
| Retrieval precision collapse | Too many irrelevant chunks sent to generation step | Reranker; precision@K evaluation; narrower similarity threshold |
| Prompt injection | User input manipulates system prompt behavior | Input sanitization; separate user content from system instructions structurally |
| Classification at zero-shot breaks on edge cases | LLM doesn't generalize correctly to domain-specific categories | Labeled examples → few-shot or fine-tuning; targeted error analysis |
| Token budget overrun | Long retrieved context + long system prompt exceeds context window | Context budget planning; aggressive reranking before truncation |
| No regression testing on prompt changes | Prompt edit breaks production quality silently | Prompt versioning + automated regression suite |
| PII in LLM logs | Inputs logged for debugging contain customer PII | Scrub PII before any logging; audit log pipeline for PII leakage |

---

## Cross-Hub References

- For serving infrastructure → `be-service-architecture`
- For caching → `be-caching-performance`
- For API key management for third-party LLM services → `be-auth-patterns`
- For LLM as product capability → `pm-platform-api`
- For fine-tuned model deployment → `ds-ml-engineering`
