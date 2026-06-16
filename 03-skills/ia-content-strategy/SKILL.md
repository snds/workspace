---
name: ia-content-strategy
description: >
  Content types, content modeling, editorial workflows, and IA for
  content-managed systems. Part of the lead-information-architect skill network.
  Use this skill when the conversation touches: content strategy and IA
  alignment, content type design, content models and schemas (fields,
  attributes, relationships), structured vs. page-based content, editorial
  workflow design, content lifecycle (creation to archival), controlled
  vocabulary for content metadata, IA for CMS-driven products, or any question
  about how content is typed, structured, and governed in relation to navigation.
  Distinguished from ia-taxonomy-classification (the classification layer that
  organizes content) and be-data-modeling (the technical implementation of
  content schemas).
aliases: [ia-content-strategy]
tier: spoke
domain: design
hub: lead-information-architect
prerequisites: [lead-information-architect]
spec_version: "2.0"
---

# IA: Content Strategy

Specialist skill for content types, content modeling, and the intersection
of content strategy and information architecture. Part of the
`lead-information-architect` skill network.

---

## Domain Boundary

This skill owns **how content is typed, structured, and governed in relation
to IA**.

- **Classification layer that organizes content** → `ia-taxonomy-classification`
- **Technical implementation of content schemas** → `be-data-modeling`
- **Navigation structure that surfaces content** → `ia-navigation-systems`
- **Search across content types** → `ia-search-findability`

---

## Content Strategy and IA: The Relationship

Content strategy and IA are often designed in sequence — IA first, then content
strategy — or treated as separate disciplines that collaborate at the end.
Both approaches produce suboptimal results.

**The correct relationship**: Content strategy and IA must be designed together.

- **Content strategy** defines: what content exists, who creates it, what it's
  for, how long it lives, and how it's governed.
- **IA** defines: how that content is structured, labeled, classified, and navigated.

When these are designed separately, the result is either:
1. IA that can't be populated with the content that actually exists (structure
   without substance)
2. Content that has no coherent structural home (substance without structure)

**Design jointly**: Define content types and IA structure in parallel, with
each informing the other.

---

## Content Modeling

A **content model** defines the content types in a system, the attributes
(fields) of each type, and the relationships between types.

### What a Content Model Includes

**Content types**: Categories of content with shared structure and purpose.
Examples in a PLM-adjacent context:
- Style (primary product record)
- Colorway (variant of a Style)
- Supplier (entity record)
- Material (reference data)
- Sample (workflow artifact)
- Document (attachment)
- Announcement (editorial content)

**Attributes of each type**:
```
Style
├── title: string (required)
├── SKU: string (required, unique)
├── category: taxonomy reference (from ia-taxonomy-classification)
├── season: controlled vocabulary term
├── status: enumerated value (Draft | In Review | Approved | In Production | Archived)
├── created_by: user reference
├── created_at: datetime
├── updated_at: datetime
└── colorways: array of Colorway references
```

**Relationships between types**:
- Style `contains` Colorway (1:N, parent-child)
- Style `references` Material (M:N, associative)
- Style `has` Documents (1:N)
- Colorway `involves` Suppliers (M:N)

### The Content Model Statement

For each content type, write a scope statement:

> A **Style** is the primary product record. It represents a single design
> concept across all its color and size variations. It is created by a
> Designer, moves through an Approval Workflow, and is ultimately associated
> with production Materials and Suppliers.

This statement clarifies:
- What the type represents (conceptual scope)
- Who interacts with it (role implication for navigation)
- What lifecycle it has (state model)
- What it relates to (relationship model)

---

## Structured vs. Page-Based Content

This distinction is architectural and has direct IA consequences.

### Structured Content

Fields, schemas, and typed attributes. Each piece of information lives in
a named, typed field.

```json
{
  "title": "Spring Blouson Jacket",
  "sku": "WO-JKT-001",
  "category": "Outerwear > Jackets",
  "material": ["100% Nylon Shell", "80/20 Down Fill"],
  "status": "In Review"
}
```

**IA advantages**:
- Fields are individually queryable and filterable (enables faceted search)
- Metadata is machine-readable (enables classification, analytics, search)
- Content model is explicit — the schema documents itself
- Consistent structure across all instances of a type (navigation patterns
  apply uniformly)

### Page-Based Content

Rich text blobs. Untyped narrative content. HTML or markdown with implicit
structure only.

**IA disadvantages**:
- Cannot be filtered by field (faceted navigation is impossible)
- Metadata must be inferred or is absent (search is keyword-only)
- No consistent structure to build navigation patterns on
- Content strategy is invisible — there's no enforceable schema

**Enterprise guidance**: Enterprise systems should use structured content.
Every piece of information with business value should live in typed fields.
Rich text (notes, descriptions, comments) is acceptable as a field within
a structured record — not as the record itself.

**Failure mode**: CMS implementations where product pages, help articles,
and data records all live as generic "page" content type. The result is an
undifferentiated content mass that can't be navigated by type, filtered by
attribute, or managed by distinct workflows.

---

## Content Type Relationships and IA

The relationships between content types directly shape navigation patterns.

### Parent-Child (1:N)

One parent contains multiple children. Navigation pattern: detail panel,
tabs within a record, subordinate list view.

**Example**: Style contains Colorways. In the navigation model:
- Style page has a "Colorways" tab or section
- Colorways are navigated within the context of their parent Style
- Breadcrumb: Styles > [Style Name] > Colorways > [Colorway Name]

### Associative (M:N)

Items relate to each other without hierarchy. Navigation pattern: related
items section, cross-reference links, faceted filtering by related entity.

**Example**: Styles reference Materials. In the navigation model:
- Style page has a "Materials" related section
- Material page has a "Used in Styles" reverse reference
- Faceted search can filter Styles by Material

### Sequential (Process)

Items connect through a workflow or lifecycle. Navigation pattern: workflow
progress indicator, "next step" navigation, approval queue.

**Example**: Styles move through an Approval Workflow. In the navigation model:
- Workflow state is a top-level attribute (visible in list views)
- "My Approvals" queue surfaces items awaiting current user's action
- Transition actions (Submit, Approve, Reject) are contextual CTAs on the record

---

## Editorial Workflow Design

In content-managed enterprise systems, the editorial workflow is as important
as the public-facing navigation. Workflow design is an IA concern — it defines
how content is navigated by authors and approvers.

### Workflow States

Every content type that has a lifecycle needs explicit state design:

| State | Who can see it | Who can edit it | Navigation implications |
|---|---|---|---|
| Draft | Creator, Admins | Creator | Hidden from non-authors |
| In Review | Creator, Reviewers, Admins | Reviewers (review fields) | Appears in Reviewer queue |
| Approved | All authorized roles | Admins only | Appears in production navigation |
| Archived | Admins | Admins | Excluded from default views |

**Failure mode**: Treating workflow states as a backend concern and designing
the navigation only for the "published" state. Users who are content authors
spend most of their time in non-published states — and need well-designed
navigation for those states.

### Role-Based Editorial Navigation

Content authors, reviewers, and admins need different navigation structures:
- **Author**: Access to their own drafts; submit for review; track review status
- **Reviewer**: Review queue; approve/reject actions; see all submitted content
- **Admin**: Full editorial control; access to all states; workflow configuration

This is an instance of the broader multi-role IA challenge. Route to
`ia-enterprise-complexity` for the structural decision framework.

---

## Content Lifecycle

### The Phases

**Creation**: Content is authored in Draft state. The creation experience
is its own IA challenge — progressive disclosure of complex forms, sensible
defaults, validation feedback.

**Review**: Content moves through approval gates. Queue-based navigation
for reviewers. Status transparency for authors.

**Publication**: Content becomes visible to its intended audience. For some
systems this is a manual action; for others it's automatic on approval.

**Maintenance**: Published content must be findable, navigable, and updatable.
Over time, content may become stale, incorrect, or superseded.

**Archival/Retirement**: Content that is no longer relevant should be archived,
not deleted. Archived content should:
- Be excluded from default navigation and search results
- Remain accessible to users who have deep links or need historical reference
- Be clearly marked as archived when accessed
- Not be hard-deleted (audit trail and historical reference)

**Failure mode**: Systems with no archival mechanism. Content accumulates
indefinitely; search results fill with obsolete items; navigation paths lead
to outdated content. "Content rot" is an IA maintenance problem.

### Content Inventory and Audit

A content inventory catalogs all content in a system by type, status, age,
and owner. A content audit evaluates that content for quality, accuracy,
and IA alignment.

**IA uses of content inventory**:
- Identify content types that need better structural support
- Find orphaned content (no clear navigation path in)
- Identify navigation items with no supporting content ("empty" sections)
- Spot structural inconsistencies (the same type of content in multiple
  places with inconsistent organization)

---

## Controlled Vocabulary for Content Metadata

Every content type's metadata fields that accept category or tag values
should use a controlled vocabulary. Route to `ia-taxonomy-classification`
for vocabulary design.

**Key metadata fields for content findability**:
- **Category/type**: Which type of content is this? (From the content model)
- **Topic/tag**: What is it about? (From a controlled vocabulary)
- **Audience**: Who is it for? (Role or persona from a defined set)
- **Status**: What lifecycle state is it in?
- **Date**: When was it created/updated? (For recency-based findability)

**Failure mode**: Free-text tags without vocabulary control. Within 6 months,
the tag cloud is unusable for filtering — too many synonyms, spelling variants,
and unique-to-one-item tags.

---

## IA Implications of CMS Choice

When the product uses a CMS for content management, the CMS's content model
capabilities directly constrain and shape the IA.

**Flexible, schema-driven CMS** (Contentful, Sanity, Prismic): Supports
arbitrary content types with defined schemas. IA and content model can be
co-designed. Strong choice for complex enterprise content.

**Page-based CMS** (traditional WordPress, older CMS platforms): Content
is pages with rich text. Limited structured content support. IA is
constrained by what the CMS can store and query.

**Headless CMS**: Content model is separated from presentation. Maximum
flexibility for IA; the navigation and presentation layer is fully designed
without CMS constraints.

**The IA-first principle for CMS selection**: Define the content model and
IA requirements first, then evaluate which CMS can support them. Don't
inherit a CMS's content model limitations as IA constraints.

---

## Cross-Links

- **`ia-taxonomy-classification`**: Classification layer for content; controlled
  vocabulary for content metadata fields
- **`ia-navigation-systems`**: How content type structures become navigation
  patterns; parent-child relationships → breadcrumbs; workflow states → queue navigation
- **`ia-enterprise-complexity`**: Role-based editorial navigation; admin IA
  vs. end-user content navigation
- **`be-data-modeling`**: Content models directly map to database schemas;
  designed jointly, not in sequence
- **`ia-search-findability`**: Structured content enables faceted search;
  metadata fields become search facets

---

## References

- Halvorson & Rach, *Content Strategy for the Web* (2012)
- Ann Rockley & Charles Cooper, *Managing Enterprise Content* (2012)
- Sara Wachter-Boettcher, *Content Everywhere* (2012)
- Karen McGrane, *Content Strategy for Mobile* (2012)
- Brain Traffic, content strategy methodology

## Related
- hub → [[lead-information-architect]]
