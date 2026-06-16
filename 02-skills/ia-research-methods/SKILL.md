---
name: ia-research-methods
description: >
  Card sorting, tree testing, first-click testing, IA heuristic evaluation,
  and quantitative IA validation protocols. Part of the lead-information-architect
  skill network. Use this skill when the conversation touches: card sort design
  and analysis (open, closed, hybrid), tree testing methodology and metrics,
  first-click testing protocols, IA heuristic evaluation criteria, participant
  recruitment for IA studies, analysis methods (similarity matrix, dendrogram,
  standardization grid), quantitative navigation validation through analytics, or
  any question about how to validate or evaluate an information architecture.
  Distinguished from ia-mental-models (the insights that drive IA decisions)
  and ux-research-synthesis (broader UX research synthesis methods).
---

# IA: Research Methods

Specialist skill for IA validation and evaluation methods. Part of the
`lead-information-architect` skill network.

---

## Domain Boundary

This skill owns **how IA decisions are validated and evaluated**.

- **The insights these methods produce** → `ia-mental-models`
- **Broader UX research synthesis** → `ux-research-synthesis`
- **Product analytics as IA validation** → `ds-product-analytics`
- **JTBD and generative user research** → `pm-discovery-research`

---

## Method Overview

IA research methods fall into two categories:

**Generative methods** (discover what structure should be):
- Open card sort
- Mental model interviews (see `ia-mental-models`)
- User interviews with task focus

**Evaluative methods** (validate that structure works):
- Closed card sort
- Tree testing
- First-click testing
- IA heuristic evaluation
- Quantitative analytics

Use generative methods early — before IA structure is committed. Use evaluative
methods mid-cycle to validate proposals and post-launch to monitor quality.

---

## Card Sorting

Card sorting asks participants to organize items into groups. It is the
primary method for discovering and validating IA groupings.

### Open Card Sort

**What it is**: Participants receive a set of cards (items, topics, features)
and create their own category labels and groupings.

**What it reveals**:
- How users naturally group related items (validates or challenges proposed groupings)
- What users call categories (vocabulary for labels)
- Which items users are uncertain how to categorize (edge cases, cross-cutting concerns)
- How many categories feel natural (informs top-level nav breadth)

**Best for**: Generative IA work. Before you have a proposed structure.
When you want to discover, not validate.

**Participant count**: 15–30 participants for open sorts. Beyond 30, new
grouping patterns rarely emerge. 15 is the minimum for statistically
meaningful similarity matrix analysis.

**Tooling**: Optimal Workshop (OptimalSort), Maze, UserZoom, UXtweak, or
in-person with physical index cards.

**Procedure**:
1. Select 30–100 items to sort (card count matters: <20 limits insight,
   >100 creates participant fatigue)
2. Write each item as a short, unambiguous phrase
3. Instruct participants to group items in a way that makes sense to them,
   then name each group
4. Collect and analyze without influencing grouping

**Failure modes**:
- Cards that are ambiguous or jargon-heavy bias toward expert users' groupings
- Too few cards (<20) produces uninformative results
- Too many cards (>100) causes participant fatigue and rushed sorting
- Pre-seeded category labels bias toward the designer's model (that's a
  closed sort — use it deliberately, not accidentally)

### Closed Card Sort

**What it is**: Participants receive pre-labeled categories and must sort
items into those categories.

**What it reveals**:
- Whether proposed categories are understood correctly
- Whether items are placed in the category the designer intended
- Which categories are ambiguous (high variance in what users place there)
- Which items don't fit clearly into any category

**Best for**: Evaluative IA work. When you have a proposed structure and
want to test it before committing.

**Participant count**: 20–50 participants. More participants are needed than
in an open sort because you're looking for statistical patterns (agreement
rates) rather than generative patterns.

**Procedure**:
1. Define the proposed categories (these become the sort targets)
2. Select the items to sort
3. Instruct participants to sort items into the provided categories; allow
   "doesn't fit" as an option for items that genuinely don't belong
4. Track agreement rates per item per category

**Analysis**: For each item, what percentage of participants placed it in
each category? Items with >70% agreement are well-placed. Items with <50%
agreement for their intended category need reconsideration.

### Hybrid Card Sort

**What it is**: Participants sort into predefined categories (closed) but
can also create new categories if needed (open).

**Best for**: When you have a partially validated structure but want to
catch items that don't fit and categories that are missing.

**Trade-off**: Combines the strengths of both methods. Adds complexity to
analysis (you have both agreement data and new-category data to reconcile).

---

## Card Sort Analysis Methods

### Similarity Matrix

A matrix showing, for each pair of items, what percentage of participants
placed them in the same group. High-agreement pairs belong together.
Low-agreement pairs may not.

**Reading the matrix**:
- Values near 100%: Items are strongly associated in users' mental models
- Values near 0%: Items are not associated
- Values around 50%: Ambiguous — participants are split on the relationship

**Use**: Identify clusters of strongly associated items. These clusters are
candidate IA groupings. Items with low similarity to any cluster are potential
stand-alone items or cross-cutting concerns.

### Dendrogram (Hierarchical Clustering)

A tree diagram derived from the similarity matrix. Shows the sequence in
which item clusters merge as you lower the agreement threshold.

**Reading the dendrogram**:
- Items that merge at high similarity (near the right side) are strongly
  associated — they're almost always grouped together
- Items that merge late (near the root) are only loosely associated

**Use**: Choose a cut point on the dendrogram to produce a proposed navigation
structure. Higher cut points → more, smaller groups (deeper IA).
Lower cut points → fewer, larger groups (shallower IA).

### Standardization Grid

A matrix showing each participant × each category, indicating which items
each participant assigned to each category. Useful for seeing outlier
participants or identifying if a few participants are skewing the results.

---

## Tree Testing

Tree testing validates a proposed navigation hierarchy using only text labels
and structure — no visual design, no chrome.

### What It Tests

Whether users can find specific items using only the navigation tree.
Because there is no visual design, results reflect pure structural and
labeling quality — not visual cues.

**What it reveals**:
- Whether navigation labels are clear enough to guide users to the right section
- Whether items are in the right location in the hierarchy
- Which hierarchy levels cause users to lose confidence
- Whether users take direct paths or indirect paths (hesitation points)

### Key Metrics

**Success rate**: What percentage of participants found the correct item?
>80% success is target. <60% indicates a significant structural or labeling problem.

**Directness**: What percentage of participants found the item without backtracking?
A user who found the correct item after multiple wrong turns technically "succeeded"
but experienced a confusing IA. Directness separates lucky success from easy success.

**First-click accuracy**: On the first click from the tree root, what
percentage of users clicked the correct top-level section?

**Time on task**: How long did it take to find the item? Longer times (even
with success) indicate hesitation and uncertainty.

### Protocol

**Writing tree test tasks**: Tasks should be realistic and specific.
"Find where to add a new colorway to an existing style" — not
"Find the colorways feature."

Avoid using the exact navigation label in the task (this creates a
word-matching exercise, not a navigation test). If the nav item is
"Colorways", write the task as "add a new color variant to a style" —
not "find Colorways."

**Participant count**: 50–100 for quantitative statistical validity.
Remote unmoderated is standard (Optimal Workshop Treejack, UserZoom, Maze).

**Task count**: 10–20 tasks per study. More tasks increase fatigue; prioritize
the highest-stakes navigation paths.

**Tree depth**: Test the full tree, not just the top level. Include enough
depth for participants to navigate meaningfully.

### Analysis

Sort tasks by success rate. Lowest success rates identify the highest-priority
structural problems.

For low-success tasks, analyze the first click distribution. If users are
splitting between two sections, the two sections have overlapping scope in
the user's mental model.

Examine backtracking paths. Where do users back up after a wrong turn?
These are the hesitation points — the decisions that aren't clear.

**Failure modes**:
- Tree testing with only top-level navigation (not deep enough to reveal
  hierarchy problems)
- Tasks that use the exact words from the navigation labels (word matching,
  not IA testing)
- Too few participants (<30) for statistical significance
- Testing navigation in isolation from the real UI context (results may not
  transfer to the full-interface experience)

---

## First-Click Testing

First-click testing measures where users click first when given a specific
task and shown a UI (wireframe, mockup, or live product).

### The Research Foundation

Jared Spool and Bob Bailey's research (2001) found that **the first click
predicts task completion with >80% accuracy**. Users who click correctly
on the first click complete the task 87% of the time. Users who click
incorrectly on the first click complete the task only 46% of the time.

**The implication**: Getting the first click right is the most important
single IA decision for any given task. Testing first-click patterns is
highly efficient — it identifies the most consequential IA failures quickly.

### What It Tests

- Are navigation labels clear enough that users choose correctly on the first click?
- Is the correct navigation item visually prominent enough?
- Are competing navigation items confusingly similar?
- Does the page structure direct users toward the correct action?

### Protocol

**Stimulus**: Screenshot or live prototype of the interface. Can be a
navigation-only view or the full interface.

**Task**: Specific, realistic task. "You want to check the status of a
sample that was sent to the supplier last week. Where would you click first?"

**Measure**: Where users click (x,y coordinate or element click). Time
to first click (hesitation indicator).

**Analysis**: Clickmap showing the distribution of first clicks. High
concentration on the correct element → clear label. Distributed clicks →
ambiguous or competing labels.

**Sample size**: 20–50 participants for a clear click distribution.

**Failure modes**:
- Tasks that include the navigation label text (word matching)
- UI with poor contrast or visual hierarchy (visual failures dominate over
  IA failures in the results)
- Showing only the navigation without page context (navigation is always
  experienced in context)

---

## IA Heuristic Evaluation

A structured expert review of an IA against established quality criteria.
Faster than user testing; useful for identifying obvious problems before
running participant studies.

### Heuristic Checklist

**1. Findability**
- Can users reach primary task areas within 2 clicks?
- Are high-frequency tasks accessible from the most-used pages?
- Does search work as a fallback for navigation failures?

**2. Labeling clarity**
- Are navigation labels in user task language (not system/org language)?
- Are labels specific enough to set correct expectations?
- Are labels mutually exclusive? (Do users know which label their item
  belongs under without having to guess?)

**3. Hierarchy integrity**
- Is hierarchy depth proportional to task frequency? (Frequent tasks should
  be shallow; rare tasks can be deep)
- Is the hierarchy consistent? (Items at the same level are genuinely peers)
- Is hierarchy depth ≤4 levels for primary user paths?

**4. Conceptual model consistency**
- Does the IA reflect a consistent conceptual model throughout?
- Is the same concept always accessed through the same navigation path?
- Do labels reflect the same vocabulary throughout (no synonyms for the
  same concept in different navigation levels)?

**5. Wayfinding support**
- Does every page have clear identity (title, section indicator)?
- Are active navigation states visually unambiguous at all levels?
- Do breadcrumbs accurately reflect location (not history)?

**6. Discoverability**
- Can users learn the product's capability set from navigation alone?
- Are new features surfaced to users who haven't specifically sought them?
- Do empty states lead users to adjacent capabilities?

**Scoring**: Rate each criterion on a 1–5 scale per major navigation section.
Aggregate scores identify the weakest areas for research prioritization.

---

## Quantitative IA Validation

User-facing analytics validate IA decisions at scale, with real user behavior.

### Navigation Path Analysis

What paths do users actually take to reach key pages?

**Setup**: Use analytics events to track navigation interactions (not just
page views). Track: which nav item was clicked, from which page, resulting
in which page.

**Analysis**: For each key destination page, what percentage of users arrived
via:
- The expected navigation path?
- Search?
- Direct link?
- Unexpected paths (suggests the navigation is not the obvious path)?

**If <50% of users reach a page via navigation**: The navigation path is
failing; users are compensating with search or deep links.

### Search Query Analysis

What do users search for? Analyzed against what exists in navigation.

**Queries matching navigation labels**: If users search for "Colorways" and
there's a "Colorways" link in navigation — the navigation is failing label
comprehension or visibility.

**Zero-result queries**: Explicit vocabulary failures. What terms are users
searching that return nothing? These are candidates for controlled vocabulary
expansion.

**Search-then-abandon rate**: High abandon rate (search → no click) indicates
results are irrelevant or result design fails.

### Exit Page Analysis

Pages where users leave the product entirely.

**Expected exits**: Login page (session end), task completion confirmation
pages.

**Unexpected exits**: If users consistently exit from a specific workflow
page or section, that section has an IA or experience failure that's causing
users to give up.

Route to `ds-product-analytics` for instrumentation setup.

---

## Multi-Role Research Design

For enterprise systems with multiple user roles, IA research requires
deliberate role-stratified design.

**Separate studies per role** (preferred for roles with >40% task set divergence):
- Run separate card sorts and tree tests per role
- Compare results cross-role to identify structural tensions
- Design role-specific navigation based on role-specific research

**Composite studies with role analysis** (appropriate for roles with <40%
task set divergence):
- Run a single study; collect role as a demographic variable
- Segment analysis by role
- Identify where role-based differences are significant vs. negligible

**Failure mode**: Running composite studies for divergent roles, then
averaging the results. The average of two different mental models is a
third, incorrect mental model that serves neither role.

---

## Cross-Links

- **`ia-mental-models`**: Card sort and interview findings feed mental model
  mapping; the research produces the insights the modeling synthesizes
- **`ia-taxonomy-classification`**: Card sort results drive controlled vocabulary
  and taxonomy design
- **`ia-navigation-systems`**: Tree testing validates proposed navigation
  structures from `ia-navigation-systems`
- **`ia-enterprise-complexity`**: Multi-role research design for systems with
  multiple user roles
- **`ds-product-analytics`**: Quantitative IA validation through behavioral analytics
- **`ds-experimentation`**: A/B testing navigation changes; statistical significance
  for navigation experiments

---

## References

- Donna Spencer, *Card Sorting: Designing Usable Categories* (2009)
- Optimal Workshop, Treejack methodology documentation
- Jared Spool & Bob Bailey, "First Click Testing" (CHI 2001)
- Steve Krug, *Don't Make Me Think* — navigation clarity heuristics
- Nielsen Norman Group, tree testing and card sorting research reports
