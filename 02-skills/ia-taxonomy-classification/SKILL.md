---
name: ia-taxonomy-classification
description: >
  Classification systems, faceted taxonomy, ontologies, controlled vocabularies,
  and taxonomy governance. Part of the lead-information-architect skill network.
  Use this skill when the conversation touches: classification theory, faceted
  navigation, controlled vocabularies, thesaurus design, ontology construction,
  polyhierarchy, term selection and labeling, taxonomy governance, enterprise
  knowledge organization, or any question about how information should be
  classified and labeled. Distinguished from ia-navigation-systems (how taxonomy
  is navigated) and ia-mental-models (how taxonomy aligns to user expectations).
aliases: [ia-taxonomy-classification]
tier: spoke
domain: design
hub: lead-information-architect
prerequisites: [lead-information-architect]
spec_version: "2.0"
---

# IA: Taxonomy & Classification

Specialist skill for classification systems, ontologies, controlled
vocabularies, and taxonomy design. Part of the `lead-information-architect`
skill network.

---

## Domain Boundary

This skill owns **how information is classified and labeled**.

- **How classification is navigated** → `ia-navigation-systems`
- **How users' mental models align to classification** → `ia-mental-models`
- **How classification is implemented in databases** → `be-data-modeling`
- **How users discover their language for classification** → `ia-research-methods` (card sorting), `pm-discovery-research`

---

## The Classification Lineage

Understanding modern digital taxonomy requires knowing where it came from.

### Aristotle's Category Theory (c. 350 BCE)

Aristotle proposed that every thing could be placed in a single hierarchical
category defined by genus (broader type) and differentia (distinguishing
quality). This **monohierarchical** model shaped Western information
organization for two millennia: one thing, one place, one path.

**The limitation**: Reality is polyhierarchical. A "red wool scarf" is
simultaneously a clothing item, a fashion accessory, a wool product, and a
red item. Forcing it into one branch destroys three classification pathways.

### Dewey Decimal System (1876)

Melvil Dewey's classification system is monohierarchical at scale — every
book has exactly one call number, one location on the shelf. The system
works for physical objects (a book can only be in one place) but reveals
the fundamental limitation of monohierarchy for digital information:
**the user must know which branch to look under**.

**The core failure mode of monohierarchy**: Users who approach the
taxonomy from a different mental model than the classifier used cannot
find what they need, even when it exists.

### S.R. Ranganathan and Faceted Classification (1933)

Ranganathan's PMEST framework (Personality, Matter, Energy, Space, Time)
proposed that every concept could be described by multiple independent
facets simultaneously. A book on "cotton textile manufacturing in India
during the 19th century" has:
- **Personality**: textile
- **Matter**: cotton
- **Energy**: manufacturing
- **Space**: India
- **Time**: 19th century

Any of these facets could be the primary access point depending on the
user's need. **Faceted classification was the theoretical foundation for
faceted navigation in modern UIs.**

### Modern Faceted Navigation

Contemporary e-commerce and enterprise search UIs are direct implementations
of Ranganathan's theory. A PLM product catalog uses facets — category, brand,
material, color, size, status — that are independent, combinable, and
hierarchical. The user applies multiple facets simultaneously to narrow from
thousands of items to the specific item they need.

---

## Core Concepts

### Taxonomy

A **taxonomy** is a hierarchical classification system: broader categories
contain narrower subcategories in a tree structure.

```
Apparel
├── Tops
│   ├── T-Shirts
│   ├── Blouses
│   └── Sweaters
├── Bottoms
│   ├── Pants
│   └── Skirts
└── Outerwear
    ├── Jackets
    └── Coats
```

**Properties**: Hierarchical, typically monohierarchical in traditional
implementations, every item belongs to exactly one node.

**Use when**: Users think about information in a consistent hierarchical
way, tasks are aligned to the hierarchy, the domain has stable categories.

**Failure mode**: Forcing polyhierarchical information into a monohierarchical
taxonomy. Users who approach from a different mental model branch fail to find
what they need.

### Thesaurus

A **thesaurus** (in information science, not the synonym-finder) describes
**semantic relationships** between terms:

| Relationship | Abbreviation | Meaning | Example |
|---|---|---|---|
| Broader term | BT | Parent concept | Apparel BT Clothing |
| Narrower term | NT | Child concept | T-Shirt NT Apparel |
| Related term | RT | Associated but not hierarchical | Scarf RT Hat |
| Use for | UF | Preferred term / synonym redirect | Jumper UF Sweater |
| Use | USE | Non-preferred term points to preferred | Sweater USE Jumper |

**Thesaurus relationships** solve the synonym problem in controlled vocabularies
and power semantic search expansion. If a user searches "jumper" in a UK-market
system, the thesaurus knows to also surface "sweater" results.

### Ontology

An **ontology** is a formal representation of concepts, their properties, and
the relationships between them. More expressive than a taxonomy or thesaurus:

- **Classes**: Types of things (Product, Material, Supplier, Region)
- **Properties**: Attributes of classes (Product has a color, weight, SKU)
- **Relationships**: Named connections between classes (Product `manufacturedBy`
  Supplier; Product `composedOf` Material)
- **Constraints**: Rules about valid values and relationships

**OWL/RDF** are the standard formal languages for ontologies. In practice,
most enterprise systems implement a "lightweight ontology" — a data model with
named relationships — rather than a formal OWL ontology.

**PLM application**: A PLM ontology defines that a Style contains Colorways,
which contain Sizes, which have Prices, which vary by Market — and that a
Material has a Composition (% fibers), a Supplier, and a Compliance Status.
This is the product knowledge graph.

**Failure mode**: Building a taxonomy when you actually need an ontology.
If the relationships between concepts are as important as the concepts
themselves (and in PLM they always are), a flat hierarchy won't serve.

### Controlled Vocabulary

A **controlled vocabulary** is a standardized, curated list of terms used to
describe and classify content. It prevents **synonym explosion** — the problem
where the same concept is described with dozens of different terms, making
search and filtering unreliable.

Examples:
- A tag taxonomy where users can enter free-form tags → uncontrolled: "t-shirt",
  "tshirt", "tee", "T-Shirt", "T shirt" are five entries for one concept
- The same system with a controlled vocabulary → users select from a validated
  list; all five terms map to the canonical "T-Shirt"

**Components**:
- **Preferred terms**: The canonical form used in the system
- **Synonyms/entry terms**: Alternative terms that redirect to preferred terms
- **Scope notes**: Definitions that clarify when a term applies
- **Hierarchical relationships** (if the vocabulary is also a taxonomy)

### Folksonomy

A **folksonomy** is a user-generated tagging system with no controlled vocabulary.
Users apply their own tags freely.

**Strengths**: Reflects current user language; grows with usage; surfaces
long-tail terms the official vocabulary missed.

**Weaknesses**: Synonym explosion; inconsistent granularity; no governance;
non-canonical terms accumulate indefinitely.

**Best practice**: Use folksonomies to *discover* user language (analyze tag
clouds and tag co-occurrence for vocabulary insights), then migrate the
high-value terms into a controlled vocabulary.

---

## Faceted Classification

### The Mechanics

Faceted classification applies multiple, orthogonal classification dimensions
simultaneously. Each facet is:

- **Independent**: Facets don't imply each other
- **Combinable**: Any combination of facets is valid
- **Hierarchical** (optionally): Each facet can itself have hierarchical depth

A product can be classified by `category: Tops`, `material: Cotton`,
`color: Blue`, `brand: Brand A`, and `size: M` simultaneously. Each
dimension is a facet.

### Designing Facets

**The PMEST test**: Apply Ranganathan's framework to identify candidate facets.
Not every dimension maps to every PMEST slot — use it as a prompt, not a
prescription.

**Selection criteria for a facet**:
1. Users actually filter/search by this dimension (validate with search analytics)
2. The dimension has enough cardinality to be useful (>3 values, typically)
3. The dimension is mutually exclusive within itself (a product has one color
   family, or a clearly defined set of colors)
4. The dimension doesn't replicate another facet (if "category" and "type"
   mean the same thing, consolidate)

**Failure mode**: Facet explosion — adding every possible attribute as a facet.
Users face a wall of filters; cognitive load destroys usability. Start with
5–8 primary facets. Add secondary facets only if analytics show demand.

### Facet Hierarchies

Facets can themselves be hierarchical:

```
Category (facet)
├── Apparel
│   ├── Tops
│   └── Bottoms
└── Accessories
    ├── Bags
    └── Scarves
```

This enables "roll-up" — showing counts at the parent level before the user
drills into a subcategory. Essential for enterprise catalogs with deep
hierarchical product structures.

---

## Polyhierarchy

A concept belonging to multiple parent categories simultaneously.

```
Wool Scarf
├── parent: Accessories > Scarves
└── parent: Materials > Wool Products
```

**The challenge**: Navigation assumes a single location. "You are here" breaks
when an item has multiple valid locations. Breadcrumbs become ambiguous.

**Solution approaches**:
1. **Faceted navigation** (preferred): Abandon the single-hierarchy model
   entirely. Items don't "live" anywhere; they're retrieved by facet combination.
2. **Primary/secondary categorization**: One canonical location (primary);
   additional cross-references (secondary). Breadcrumbs use primary only.
3. **Multiple entry points**: The item appears in multiple places in the
   hierarchy but links to a single canonical page.

**Failure mode**: Implementing polyhierarchy in a navigation system designed
for monohierarchy. Results in duplicate entries, broken breadcrumbs, and user
confusion about canonical location.

---

## Term Selection and Labeling

### User Language vs. Expert Language

Users navigate by their mental model vocabulary, not the organization's
internal language. The gap between user language and system language is one
of the most common IA failure modes.

| System language | User language |
|---|---|
| "Material Master" | "Fabrics" / "Materials" |
| "Style Record" | "Product" / "Style" |
| "Bill of Materials" | "Recipe" / "Components" |
| "Purchase Order" | "Order" / "PO" |

**Research method**: Use card sorting with user-written labels (not
pre-labeled cards) to discover actual user vocabulary. Route to
`ia-research-methods` for the protocol.

**The IKEA effect**: Users prefer their own words. When users write their own
labels for categories in an open card sort, they feel more confident
navigating a system built with those labels. This is not mere preference —
comprehension and task completion rates measurably improve.

### Testing Label Comprehension

Before committing to navigation labels, test comprehension:

1. **Label comprehension test**: Show the label; ask users what they expect
   to find there. If >20% of responses don't match intent, the label fails.
2. **Card sort closed validation**: Give users items; ask them to sort into
   labeled categories. High disagreement on a category signals a label problem.
3. **Tree test first-click**: In a tree test, which label do users click first?
   If the correct label isn't first-clicked by >60%, it's insufficiently clear.

### Avoiding Jargon in Navigation

Enterprise systems are especially prone to insider jargon in navigation:
- Acronyms: "PLM", "PIM", "MDM", "BOM" — meaningful to admins, opaque to end users
- Internal team names: "The Supply Chain Hub" — only meaningful to people who
  know the org structure
- System names: "Centric 8" as a navigation label

**Guideline**: If a new employee couldn't interpret a navigation label on
their first day, it's failing discoverability.

---

## Taxonomy Governance

### Why Governance Matters

A taxonomy without governance degrades. Terms proliferate without consolidation,
preferred terms are bypassed, new concepts are added without fitting the
existing structure, deprecated terms persist. Over 2–3 years without governance,
a well-designed controlled vocabulary becomes a synonym swamp.

### Governance Components

**Term authority**: Who can add, modify, or deprecate terms? (Usually: IA
owner or information management team, with input from domain experts and users)

**Term proposal process**:
1. New term proposed (by content author, user, product team)
2. Check for existing preferred term or synonym
3. If new: define scope, assign hierarchy position, add synonyms/redirects
4. Review by authority
5. Publish with implementation date

**Deprecation process**:
1. Term identified as obsolete or superseded
2. Map all existing uses to replacement term
3. Mark as deprecated (retain as entry term pointing to preferred term)
4. Remove from active vocabulary after migration period

**Version control**: Taxonomy changes should be versioned. Enterprise systems
often have content tagged with old taxonomy terms; version control enables
migration planning.

### Enterprise Taxonomy Lifecycle

**Phase 1 — Generative**: Initial taxonomy created from user research and
domain analysis. Route to `ia-research-methods` and `ia-mental-models`.

**Phase 2 — Operational**: Taxonomy in use; governance handles routine
additions and minor restructuring.

**Phase 3 — Decay**: Without governance, terms proliferate, synonyms multiply,
the hierarchy becomes inconsistent. Symptoms: duplicate category entries,
user-reported "can't find it" errors, search analytics showing long-tail
variants of controlled terms.

**Phase 4 — Restructure or reset**: Major taxonomy revision required; often
triggered by product pivots, acquisitions, or accumulated governance debt.

---

## Cross-Links

- **`ia-navigation-systems`**: How taxonomy structures become navigation patterns;
  faceted classification → faceted navigation UI patterns
- **`ia-mental-models`**: Aligning taxonomy to user mental models before
  formalizing classification structure
- **`ia-research-methods`**: Card sorting to discover user vocabulary and
  validate proposed taxonomy groupings
- **`be-data-modeling`**: Hierarchical taxonomies require specific DB patterns:
  adjacency list (simple, but expensive tree traversal), nested set model
  (fast reads, expensive writes), closure table (most flexible, highest storage)
- **`pm-discovery-research`**: Discovering user language before building
  controlled vocabularies

---

## References

- S.R. Ranganathan, *Prolegomena to Library Classification* (1937)
- Elaine Svenonius, *The Intellectual Foundation of Information Organization* (2000)
- ANSI/NISO Z39.19, *Guidelines for the Construction, Format, and Management of Monolingual Controlled Vocabularies*
- Tom Gruber, "A translation approach to portable ontology specifications" (1993)
- OWL 2 Web Ontology Language (W3C)

## Related
- hub → [[lead-information-architect]]
