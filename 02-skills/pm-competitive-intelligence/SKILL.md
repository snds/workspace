---
name: pm-competitive-intelligence
description: >
  Win/loss analysis, competitive positioning, battlecard construction,
  market landscape assessment, and competitive strategy for enterprise
  SaaS. Use this skill whenever the conversation touches: analyzing why
  deals are won or lost, building competitive positioning, writing or
  updating a battlecard, assessing the competitive landscape, monitoring
  competitor signals, interpreting analyst reports (Gartner Magic Quadrant,
  Forrester Wave), or deciding whether to chase feature parity vs. invest
  in differentiation. Also trigger on: "competitive analysis", "win/loss",
  "battlecard", "competitive positioning", "feature parity", "Gartner",
  "Magic Quadrant", "Forrester Wave", "competitive intelligence", "competitor
  X", "how do we differentiate", "competitive landscape".
---

# PM Competitive Intelligence

Specialist skill for win/loss analysis, competitive positioning, and
battlecard construction. Part of the enterprise SaaS product management
skill network.

---

## Domain Boundary

This skill owns **how to understand and respond to competitive dynamics** —
analysis, positioning, and strategic response.

- **Building the features that differentiate** → `pm-roadmap-strategy`
- **Communicating competitive positioning to executives** → `pm-stakeholder-comms`
- **GTM and launch positioning** → `pm-enterprise-gtm`
- **Discovery to understand competitive dynamics from customers** → `pm-discovery-research`

---

## Win/Loss Analysis Methodology

Win/loss analysis is a research methodology, not a sales ops function. Most
organizations either skip it or do it badly (asking sales to explain wins and
losses without independent verification).

### Why Standard Win/Loss Analysis Fails

- **Sales rationalizes outcomes**: AEs attribute wins to product quality and
  relationships; losses to price and missing features. This is self-serving
  attribution, not analysis.
- **Recency bias**: Analysis happens immediately after close, before patterns
  emerge.
- **Selective memory**: The most emotionally vivid deal (the big loss) gets
  disproportionate attention.
- **Champion bias in customer interviews**: Customers who chose you will
  validate your product. Customers who didn't choose you will validate their
  decision to go elsewhere. Neither is the whole truth.

### A Rigorous Win/Loss Process

**Step 1: Structured sales rep interviews (internal)**

Interview the AE 1–2 weeks after deal close. Ask:
- "Walk me through the deal from the first meeting to the close."
- "At what point did you think you would win/lose? What changed?"
- "What did the prospect tell you about why they were leaning toward [competitor]?"
- "What objections came up that you couldn't answer?"
- "What capability did they ask for that we didn't have?"

What to listen for: specific moments, not general impressions.

**Step 2: Customer/prospect interviews (external)**

In wins: interview the champion 30–60 days after go-live (when they're past
the honeymoon phase). Ask what almost made them choose someone else.

In losses: interview the prospect 30–60 days after the decision. Time provides
candor — the decision is made, there's no upside to telling you what you want
to hear.

Questions that get honest answers:
- "Tell me about the evaluation process from your perspective."
- "What made [competitor] stand out in the evaluation?"
- "Was there a moment when the decision shifted? What happened?"
- "If you were advising a peer going through a similar decision, what would
  you tell them about the differences between [your product] and [competitor]?"

Questions that get rationalizations:
- "Did the price make the difference?" (Always yes; never the real story)
- "What feature were we missing?" (Produces a feature list, not the real reason)
- "Was it our product or our sales process?" (Forces a false binary)

**Step 3: Pattern analysis**

Run win/loss analysis quarterly, not deal-by-deal. Patterns only emerge in
aggregate. Minimum 10 data points per category before drawing conclusions.

Track by:
- Deal segment (SMB, mid-market, enterprise)
- Competitor faced
- Deal stage where the shift happened (discovery, demo, proof of concept, final eval)
- Stated reason vs. inferred reason

---

## Competitive Positioning Frameworks

### Competitive Matrix (Capability Comparison)

**What it is**: A side-by-side comparison of capabilities across you and
key competitors.

**What it's useful for**:
- Internal alignment on where you're strong and weak
- Identifying parity gaps that are costing deals
- Informing roadmap prioritization with competitive context

**Why it's dangerous if shared externally**:
- Reduces competitive differentiation to a feature checklist
- Positions you as the vendor trying to catch up (even if you're ahead)
- Invites prospects to score you on the competitor's terms

Use the matrix internally. Use the positioning statement externally.

### Positioning Statement

**Format**:
```
For [target customer] who [has problem],
[Product name] is [category]
that [key benefit].
Unlike [competitor],
[your product] [differentiator].
```

**Example**:
```
For enterprise fashion brands managing complex product development,
Centric PLM is a product lifecycle management platform
that accelerates time-to-market by connecting design, sourcing, and
production in a single workflow.
Unlike legacy PLM systems, Centric is built for the fashion-specific
workflow with out-of-the-box templates and a consumer-grade UI that
doesn't require months of configuration.
```

**Rules for a good positioning statement**:
- The problem must be real and specific — not "improving efficiency"
- The category should be familiar enough to frame context, narrow enough to
  signal expertise
- The differentiator must be real and defensible — not "best in class"
- One differentiator, not three. Multiple differentiators mean no differentiator.

### JTBD Lens for Competitive Analysis

Competitors aren't just direct alternatives. In any customer's decision:

1. **Direct competitors**: Other products that do the same job
2. **Adjacent alternatives**: Products in adjacent categories that could
   do the job with some configuration (spreadsheets, general-purpose tools)
3. **The incumbent workflow**: "Do nothing" or "do it the way we always have"
4. **Build internally**: Some enterprise companies will build it themselves
   if no vendor solution meets their needs

For most enterprise SaaS, the most common "competitor" in a deal is not
another vendor — it's the incumbent workflow and organizational inertia.
Position against that, not just against the named vendors.

---

## Feature Parity vs. Differentiation Strategy

### The Parity Trap

Chasing feature parity with competitors is a race to average. It is
strategically correct when you're meaningfully behind on table stakes that
are required to compete in deals. It is strategically wrong when you're
investing in capabilities just because a competitor has them.

**Indicators you're in the parity trap**:
- Roadmap is driven primarily by "Competitor X just shipped Y"
- Win/loss analysis primarily produces feature gap lists
- Product differentiation narrative keeps shifting
- Customer quotes about your product are "it's similar to X but [minor thing]"

**The alternative**: Differentiation requires an opinionated bet about what
your target customer values that competitors have under-invested in. This bet
must come from customer discovery, not from feature comparisons.

### When to Pursue Parity

Pursue parity when:
- The missing capability is a requirement (deal-qualifier, not deal-winner)
  — you can't get to a final evaluation without it
- Multiple win/loss interviews cite the same gap as the proximate cause of
  the loss (not just a factor)
- The capability is in the basic needs category (Kano) — its absence is felt,
  its presence is neutral

Don't pursue parity when:
- The competitor's version of the feature isn't actually used by customers
  (check this — "they have it" doesn't mean "customers value it")
- The capability is in a segment you're not targeting
- Building it would delay investments in genuine differentiation

---

## Battlecard Construction

### What PMs Own vs. What Product Marketing Owns

| PM Owns | Product Marketing Owns |
|---------|----------------------|
| Factual capability comparison | Final tone and voice |
| Win themes (what we win on when the evaluation is honest) | Sales-facing narrative and training |
| Objection handling (product-level) | Pricing/commercial objection handling |
| Competitive feature gap tracking | Analyst and external positioning |
| Customer evidence (quotes, case studies) | Legal review of competitive claims |

### Battlecard Structure

```
## Competing Against [Competitor Name]

### When we win
[2-3 specific scenarios where honest evaluations favor us. Not "when they
pick quality over price." Specific: "When the customer has more than 3
product categories and needs cross-category workflow management."]

### When they win
[Be honest. 2-3 scenarios where their product genuinely has an advantage.
Sales will trust a battlecard that acknowledges real weaknesses more than
one that pretends to be superior on everything.]

### Key differentiators (our strengths)
[3-5 specific capabilities or properties where we are genuinely ahead.
Include customer evidence.]

### Known gaps (handle proactively)
[2-3 capabilities where they are ahead. Frame honestly with a response:
"They have X; here's how we approach it and why our approach is better
for [target customer type]."]

### Objection handling
| Objection | Response |
|-----------|----------|
| "They have [feature] and you don't" | [Specific response] |
| "They're more established in our industry" | [Specific response] |
| "Your price is higher" | [Redirect to value framing] |

### Qualifying questions for AEs
[2-3 questions the AE can ask to surface the customer's priorities in a
way that favors our strengths. These should be discovery questions, not
leading questions.]

### Evidence
[Customer quotes and case studies that support the win themes.]
```

---

## Analyst Relations Relevance

Gartner Magic Quadrant and Forrester Wave reports are enterprise sales
instruments before they are product inputs.

### How They Affect Enterprise Sales

- Enterprise procurement and IT often use analyst reports to create
  shortlists. Not appearing in a report means not making shortlists.
- Placement in Leaders quadrant or Strong Performers category is a
  de-risking signal for buyers — "Gartner approved it" reduces their
  career risk.
- Customers use analyst reports to justify vendor selection to internal
  stakeholders who weren't in the evaluation.

### How Product Decisions Affect Analyst Perception

Analysts evaluate products on:
- **Vision** (roadmap direction, market strategy): PM's responsibility
- **Execution** (product completeness, customer satisfaction): delivery record
- **Completeness of offering** (does the product address the full market need?): coverage

**PM's input to analyst relations**:
- Roadmap briefings: analysts need to understand where the product is going,
  not just where it is
- Win/loss data: analysts ask about competitive dynamics directly
- Customer reference programs: who you can point to as successful customers
  is an analyst evaluation input

### What Not to Do

- Don't chase analyst criteria at the expense of customer problems. Analysts
  lag the market — building for analyst criteria means building for yesterday's
  market.
- Don't assume analyst placement drives all enterprise deals. Many enterprise
  buyers in specialized industries don't reference general-purpose analyst reports.

---

## Monitoring Competitive Landscape

### Signals Worth Tracking

| Signal | What It Suggests | How to Get It |
|--------|-----------------|---------------|
| Competitor job postings | Investment areas (hiring ML engineers = ML investment) | LinkedIn, job boards, automated alerts |
| Pricing page changes | Packaging strategy shifts, competitive pressure response | Web archive comparisons, manual monitoring |
| Product announcements | New capabilities, partnership announcements | Press releases, product blogs, release notes |
| Customer reviews | What customers like/dislike about competitor (and you) | G2, Gartner Peer Insights, Capterra |
| Acquisition activity | Strategic direction, market consolidation | Tech press, Crunchbase |
| Win/loss interview mentions | Real-world competitive dynamics in active deals | PM-led win/loss program |
| Sales team feedback | Competitive objections surfacing in deals | Regular competitive debrief with sales |

### Signals That Are Noise

- **Competitor conference presentations**: Marketing, not roadmap. Don't
  react to announcements; wait to see if they ship it.
- **Feature announcements without GA**: "Coming soon" is not a product
  capability. Don't update your roadmap for vaporware.
- **Social media and LinkedIn buzz**: Measures awareness, not adoption.
  A competitor's social momentum doesn't mean their customers are happy.

---

## Common Failure Modes

| Failure Mode | What Happens | How to Prevent |
|-------------|-------------|---------------|
| Conflating competitive feature requests with customer needs | PM builds features because "Competitor has them," not because customers are struggling without them | Cross-reference every competitive gap with win/loss evidence: does this gap actually cause losses? |
| Updating strategy on competitor moves | Roadmap becomes reactive; differentiation erodes | Anchor strategy to customer problems, not competitor features; evaluate competitive moves against your discovery, not at face value |
| Battlecard as product promise | Sales tells prospects features are on the roadmap; PM hasn't committed | "Roadmap direction" vs. "committed feature" must be clearly distinguished in all competitive materials |
| Trusting sales-only win/loss | All analysis comes from AE interviews; systematic biases compound | Supplement with customer/prospect interviews on a regular cadence |
| Feature-level competitive thinking | Comparing feature lists rather than understanding job-level competitive dynamics | Apply JTBD lens: what job are customers hiring us vs. the competitor to do? |

---

## Cross-Hub References

- **Discovery to understand competitive dynamics** → `pm-discovery-research`:
  JTBD force analysis surfaces why customers switch or stay; interview methodology
  for competitive discovery
- **Building a differentiated roadmap** → `pm-roadmap-strategy`: competitive
  intelligence feeds Kano categorization and RICE confidence inputs
- **Launch positioning** → `pm-enterprise-gtm`: battlecard positioning feeds
  directly into launch enablement
- **Executive communication on competitive strategy** → `pm-stakeholder-comms`:
  framing competitive recommendations for steering committee
