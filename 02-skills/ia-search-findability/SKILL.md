---
name: ia-search-findability
description: >
  Search UX, faceted search, autocomplete, search result design, and findability.
  Part of the lead-information-architect skill network. Use this skill when the
  conversation touches: findability vs. discoverability, search behavior patterns,
  query construction and autocomplete, faceted search UX, filter design (left
  panel, chips, zero-result states), search result anatomy and ranking, zero-results
  handling, search analytics as IA validation, or any question about how users
  find things through search interfaces. Distinguished from ia-navigation-systems
  (navigation as the structural findability mechanism) and ia-taxonomy-classification
  (the vocabulary and structure search operates on).
aliases: [ia-search-findability]
tier: spoke
domain: design
hub: lead-information-architect
prerequisites: [lead-information-architect]
spec_version: "2.0"
---

# IA: Search & Findability

Specialist skill for search UX, findability design, and search as an IA
validation mechanism. Part of the `lead-information-architect` skill network.

---

## Domain Boundary

This skill owns **how users find things through search interfaces**.

- **Navigation as the structural findability mechanism** → `ia-navigation-systems`
- **The vocabulary and structure search operates on** → `ia-taxonomy-classification`
- **Quantitative IA validation through analytics** → `ds-product-analytics`
- **Mental model alignment (why users search what they search)** → `ia-mental-models`

---

## Findability vs. Discoverability

These are distinct problems requiring different design solutions. Conflating
them produces interfaces that solve neither well.

### Findability

**Definition**: Can users find something they know exists?

**The user's state**: "I know there's a thing called X. I want to get to X."

**Design solutions**: Clear labeling, consistent navigation structure, search
with strong known-item retrieval, deep links, direct URL access.

**Failure indicators**: Users use search for things that are prominently linked
in navigation. Search queries are verbatim navigation label text. "I couldn't
find it" feedback about items that exist and are linked.

### Discoverability

**Definition**: Can users find something they don't know exists?

**The user's state**: "I don't know what's possible. I'm exploring."

**Design solutions**: Contextual navigation (related items, "you might also
need"), progressive disclosure of capabilities, empty state design that
surfaces adjacent functions, browsable category structures, feature spotlights.

**Failure indicators**: Users don't use features that would serve them because
they never encountered them during normal use. New users can't learn the
product's capability set from navigation alone. Power users discover features
by accident years after they were shipped.

**The enterprise discoverability problem**: Enterprise products especially
suffer from low discoverability. Large feature sets, role-based permission
filtering (hides features from users who might benefit from knowing they exist),
and workflow-focused navigation (optimized for efficiency, not exploration)
all suppress discoverability. Deliberate discoverability design is required.

---

## Search Behavior Patterns

Users approach search in fundamentally different modes. A search UX that
handles only one mode fails the rest.

### Known-Item Search

**Behavior**: User types a specific thing they know exists. High precision
in the query. Quick scan of top results.

**UX requirements**: Fast results, exact match first, result title and
metadata that confirm "this is the one", deep link from result to item.

**Failure mode**: Relevance ranking that buries exact matches below
"related" results. Users who are 100% sure what they want don't want to
evaluate 10 results — they want the one item immediately.

### Exploratory Search

**Behavior**: User is browsing to understand what exists. Vague queries,
multiple sessions, refinement over time.

**UX requirements**: Strong faceted filtering, browsable result sets,
clear metadata in results, recommendations, related items.

**Failure mode**: Search optimized only for known-item retrieval — fast
exact match, no browsing support. Users doing exploratory work get a
results list with no way to narrow or explore.

### Re-finding

**Behavior**: User is searching for something they found before. Often
relies on memory fragments ("that report about Q3 from last month").

**UX requirements**: Recency signals in results, recently accessed items
surfaced first (personalization), ability to filter by date, personal
collections or bookmarks.

**Failure mode**: Pure relevance ranking with no recency weighting.
Re-finding queries often use imprecise vocabulary — the user doesn't
remember the exact title — so semantic matching and recency signals matter.

### Serendipitous Discovery

**Behavior**: User finds something useful while searching for something else.

**UX requirements**: Rich result snippets, "related to your search" sections,
breadcrumb context in results (shows where in the IA the result lives).

**Failure mode**: Minimal result metadata. If results are just a title and
a link, there's nothing for the user to "catch" while scanning.

---

## Query Construction

### How Users Actually Search

Users don't write ideal queries. Understanding actual behavior shapes how
search must compensate:

- **Short queries**: 2–3 words is the median query length. Users do not write
  full sentences unless the interface invites it.
- **Natural language**: Users increasingly use natural language ("show me
  products with late samples") — search must parse intent, not just tokenize.
- **Misspellings**: Every search system should handle common misspellings for
  its domain vocabulary. "Colorway" vs. "colour way" vs. "color-way" are all
  the same concept.
- **Keyword fragments**: "blue scarf wool" rather than "blue wool scarf" — word
  order should not affect results in a well-designed system.
- **Synonym variance**: Users use different words for the same concept, especially
  across markets and roles. "Jumper" (UK) vs. "Sweater" (US); "SKU" vs. "product
  variant" vs. "item".

### Compensating for Poor Queries

**Fuzzy matching**: Return results even when the query doesn't exactly match.
Levenshtein distance for typo correction; phonetic matching for soundalike errors.

**Spell correction**: Detect and correct misspellings. Display "Showing results
for [corrected term]" with an option to search the original term.

**Synonym expansion**: When a user searches "jumper", also return results
tagged "sweater". Powered by a thesaurus or controlled vocabulary.
Route to `ia-taxonomy-classification` for vocabulary design.

**Query parsing**: Identify the intent structure in the query. "Blue wool
scarves under $50" is a multi-facet query — the search should parse color
(blue), material (wool), category (scarves), and price constraint (<$50)
from natural language.

---

## Autocomplete and Type-Ahead

### Purpose

Autocomplete serves two functions:
1. **Efficiency**: Reduces the keystrokes required to express a complete query
2. **Vocabulary training**: Shows users what the system understands, creating
   an implicit controlled vocabulary effect (users learn to use terms the
   system recognizes)

### Design Requirements

**Suggestion sources**:
- Top queries that start with the typed prefix (popularity-weighted)
- Matching items (results preview, not just query suggestions)
- Recent searches (personalized, improves re-finding)
- Category/facet suggestions ("in Styles", "in Materials")

**Handling empty states during typing**: Show helpful placeholder content —
popular searches, recent searches, or search tips — not a blank panel.

**Error handling**: If the user's partial input matches nothing, don't show
an empty autocomplete panel — either hide it or show a "no suggestions yet"
state that resolves as the user types more.

**Keyboard navigation**: Autocomplete must be fully keyboard-navigable.
Arrow keys to select, Enter to accept, Escape to dismiss. This is both
an accessibility requirement and a power-user efficiency feature.

**Failure modes**:
- Autocomplete that shows stale or low-quality suggestions (outdated query
  logs; suggestions that don't reflect current content)
- Autocomplete that breaks on spaces (mid-query typing should work)
- Autocomplete results that take the user to a wrong destination

---

## Faceted Search UX

### Filter Placement

**Left-panel filter sidebar** (desktop default):
- Permanent visibility keeps filters in the user's working memory
- Users can see active filter state at all times
- Supports iterative refinement (change one filter, see results update)

**Modal/drawer filter** (mobile default):
- Necessary on narrow viewports
- User must commit to opening the filter panel — adds friction
- Show applied filter count on the trigger button ("Filters (3)")
  so users know filters are active without opening the drawer

**Inline filters** (within results list):
- Quick filter chips above results; good for a small number of primary filters
- Works well on mobile for 3–5 key filters
- Not suitable for complex multi-value facets

### Applied Filter Visualization

Users who can't see their active filters can't debug their own search state.

**Chip/tag pattern**: Each active filter value appears as a chip with a remove
(×) action. Required for faceted search.

**"Clear all" control**: Always provide a way to remove all filters at once.
Don't hide this behind the filter panel.

**Result count feedback**: "Showing 47 results for [query] filtered by
[Material: Cotton] [Color: Blue]". The count and active filter visualization
together tell the user their search state.

**Empty results from filtering**: Distinguish between "nothing matches your
query" and "your filters narrowed to zero results":
- Query zero results: suggest related queries, offer to broaden search
- Filter zero results: show which filter caused the zero, offer to remove it,
  show how many results would be returned without that filter

**Failure mode**: Active filters that aren't visible. User applies three
filters, navigates away, returns, and has no idea their search is filtered.
Persistent filter state must be visibly indicated.

### Filter Hierarchy and Organization

**Primary vs. secondary filters**: Lead with the most reducing filters
(category, status). Secondary filters (color, size, material) can be
collapsed by default with an expand control.

**Filter value ordering**:
- Alphabetical: good for long lists where users scan for specific values
- By count (most results first): good for exploratory filtering where users
  want to understand what's available
- By custom order: good for status/stage values that have natural sequence
  (Draft → Review → Approved → Published)

**Showing item counts per filter value**: Indicating how many results each
value produces ("Cotton (47)") helps users predict the result of clicking
and reduces the frustration of filtering to zero results.

---

## Search Result Design

### Result Anatomy

Every result should include, in roughly this priority order:
1. **Title**: The item's primary identifier, linked to the item
2. **Category/type indicator**: What kind of thing is this? (Especially
   important in mixed-type search results)
3. **Key metadata**: The 2–3 attributes most relevant to the query context
4. **Snippet/description**: Contextual excerpt showing where the query term
   appears (highlighted)
5. **Breadcrumb path**: Where in the IA this item lives — helps users
   evaluate relevance and navigate to the section if they need more

**Adaptation by result type**: A document result looks different from a
product record result. Use distinct result card templates per content type.

### Result Ranking

Users trust the ranking of results. The first 3 results receive
disproportionate attention and clicks.

**Ranking signals** (in rough priority order for enterprise):
1. **Exact match** on primary fields (title, SKU, ID) — always rank first
2. **Relevance score** on text content
3. **Recency** — recently modified/created items are often what the user wants
4. **Popularity** — frequently accessed items are likely relevant
5. **Personalization** — items the user has accessed before

**Surfacing ranking rationale**: In high-stakes search (medical, legal, financial,
enterprise workflow), users benefit from understanding why a result ranks
where it does. "Exact title match", "matches your recent activity", or
result scores help users calibrate trust in ranking.

### Zero Results

Zero results is not a dead end — it's a design state.

**Required elements**:
1. Clearly show what was searched (query echo) — confirm the system understood the input
2. Spell check / "did you mean" suggestion if applicable
3. Related searches or suggested categories
4. Option to broaden (remove filters, try fewer keywords)
5. Contact/support path if this is an important search context

**What not to do**:
- Show a blank page with "No results found"
- Remove the search bar from the zero-results view
- Give no path forward

---

## Search as IA Validation

Search analytics are one of the most valuable IA quality metrics. What users
search for reveals what the navigation is failing to deliver.

### Key Analytics

**Top queries**: If users are searching for things that are prominent in the
navigation, the navigation labels are failing comprehension. Users search
when they can't find through navigation.

**Zero-result query analysis**: These are explicit vocabulary failures —
the user used a term the system doesn't know. Mine these for controlled
vocabulary additions, synonym mappings, and content gaps.

**Search-then-abandon rate**: User searched → got results → left without
clicking. Indicates results were irrelevant or the result design was insufficient
to identify the right item.

**Navigation-vs-search ratio by section**: If a specific section has a
dramatically high search rate relative to page views, the local navigation
for that section is failing. Search is compensating for IA.

Route to `ds-product-analytics` for quantitative tracking setup.

---

## Cross-Links

- **`ia-taxonomy-classification`**: The controlled vocabulary and structure
  search operates on; synonym expansion powered by thesaurus relationships
- **`ia-navigation-systems`**: Search as supplemental navigation; navigation
  analytics complement search analytics
- **`ia-mental-models`**: Why users search the terms they do — their mental
  model vocabulary drives query construction
- **`ds-product-analytics`**: Search analytics as IA quality metrics; query
  analysis, zero-result rates, click-through patterns
- **`ia-research-methods`**: Quantitative validation of IA through analytics
  (complements tree testing and card sorting)

---

## References

- Udi Manber & Gene Myers, "Suffix Arrays" (1993) — text retrieval algorithms
- Jacob Nielsen, "Search: Visible and Simple" (2001)
- Marcia Bates, "The Design of Browsing and Berrypicking Techniques for the Online Search Interface" (1989)
- Peter Morville, *Ambient Findability* (2005)
- Karen Markey Drabenstott, faceted search research
