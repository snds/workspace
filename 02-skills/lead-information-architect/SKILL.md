---
name: lead-information-architect
description: >
  Staff/Principal IC information architect. Full IA discipline depth covering
  taxonomy theory, classification science, wayfinding theory, findability
  research, mental model mapping, content strategy, and enterprise-scale IA
  complexity. Hub skill for a network of 7 specialist spokes. Trigger on:
  information architecture, IA, navigation design, navigation structure,
  taxonomy, classification, ontology, controlled vocabulary, wayfinding,
  findability, search UX, mental models, content strategy, content modeling,
  card sorting, tree testing, sitemap, IA audit, site structure, app structure,
  label design, navigation labels, enterprise navigation, multi-role navigation.
aliases: [lead-information-architect]
tier: hub
domain: design
spec_version: "2.0"
---

# Lead Information Architect

**Hub skill** for the IA discipline skill network. Routes to 7 specialist spoke
skills based on topic. This skill provides foundational IA principles and
routing logic; spokes carry domain-specific depth.

---

## Routing Protocol

### This hub vs. adjacent skills

| Question type | Route to |
|---|---|
| Deep taxonomy, ontology, classification theory | `ia-taxonomy-classification` (this network) |
| Navigation patterns, wayfinding, label design | `ia-navigation-systems` (this network) |
| Search UX, faceted search, findability | `ia-search-findability` (this network) |
| Mental model mapping, conceptual design | `ia-mental-models` (this network) |
| Content types, content modeling, CMS IA | `ia-content-strategy` (this network) |
| Multi-role IA, admin/end-user split, suite navigation | `ia-enterprise-complexity` (this network) |
| Card sorting, tree testing, first-click testing | `ia-research-methods` (this network) |
| Practical UX-oriented IA implementation (not deep theory) | `lead-ux-designer` → `ux-information-architecture` |
| User research methods more broadly (interviews, JTBD, synthesis) | `pm-discovery-research` |
| Visual expression of navigation | `lead-ui-designer` → `uid-spatial-composition` |
| Navigation interaction patterns (transitions, hover states) | `lead-ux-designer` → `ux-interaction-design` |
| Database schema for taxonomy hierarchies | `be-data-modeling` |
| Quantitative navigation validation, search analytics | `ds-product-analytics` |

**The boundary**: `ux-information-architecture` is a practical implementation
reference — appropriate for IA decisions made during UX design sprints.
`lead-information-architect` carries the full discipline depth: theoretical
lineage, named frameworks, failure mode analysis, and the research methods
to validate IA decisions. When the UX spoke hits its limits, it defers here.

---

## Spoke Network — Load On-Demand

**Do not load all spokes eagerly.** Load only the 1–2 spokes relevant to the
current question. The hub contains enough context to triage and route.

### Spoke Manifest

| Skill | Domain | Trigger When |
|---|---|---|
| `ia-taxonomy-classification` | Classification systems, faceted taxonomy, ontologies, controlled vocabularies, taxonomy governance | Designing category systems, faceted navigation, term lists, ontology design, PLM product categorization, vocabulary governance |
| `ia-navigation-systems` | Navigation patterns, wayfinding, Kevin Lynch theory, signage theory, digital nav design | Navigation pattern selection, wayfinding design, label strategy, breadcrumb design, mega menu vs sidebar decisions |
| `ia-search-findability` | Search UX, faceted search, autocomplete, result design, findability vs discoverability | Search interface design, filter UX, autocomplete, zero-results states, search analytics |
| `ia-mental-models` | User conceptual models, mental model mapping, conceptual design, gulf theory | Aligning IA to user expectations, Indi Young mental model research, conceptual model definition before nav design |
| `ia-content-strategy` | Content types, content modeling, editorial workflows, IA for CMS | Defining content types, structured content schemas, editorial workflow design, content lifecycle |
| `ia-enterprise-complexity` | Multi-role IA, multi-product suites, admin vs end user, scaling navigation | Role-based navigation decisions, app-suite umbrella nav, admin IA, when navigation breaks at scale |
| `ia-research-methods` | Card sorting, tree testing, first-click testing, IA heuristic evaluation | Validating IA proposals, running card sorts, tree testing protocols, IA quality metrics |

### Spoke Loading Protocol

**Step 1**: Match the user's question to the Spoke Manifest above. Identify
the 1–2 directly relevant spokes (rarely 3).

Common routing patterns:

- **Designing a new navigation structure**: `ia-navigation-systems` + `ia-taxonomy-classification`
- **Multi-role enterprise IA**: `ia-enterprise-complexity` + `ia-navigation-systems`
- **Validating an IA with research**: `ia-research-methods` + `ia-mental-models`
- **Search and findability**: `ia-search-findability` (+ `ia-taxonomy-classification` if vocabulary is the issue)
- **CMS or content-driven IA**: `ia-content-strategy` + `ia-taxonomy-classification`
- **Why users can't find things**: `ia-mental-models` + `ia-search-findability`
- **IA for a new product from scratch**: Start with `ia-mental-models`, then `ia-taxonomy-classification`, then `ia-navigation-systems`

**Step 2**: Load the spoke from:
```
[workspace root]/02-skills/[skill-name]/SKILL.md
```

**Step 3**: If the conversation shifts to a different domain mid-session,
load that spoke then — not preemptively.

**Never load all 7 spokes at once.** A typical IA question needs 1–2 spokes.

---

## Core Principles

### 1. IA is the structure of shared understanding

IA makes the organization's model of information match the users' mental model.
When these models diverge, the product fails — users search instead of navigate,
they abandon tasks, they call support. Every IA decision is a hypothesis about
what users expect to find where.

### 2. Structure before visual design

A beautiful interface built on a broken IA fails. A navigation bar with the
wrong labels — however well-designed visually — produces findability failures
that no amount of visual polish can fix. IA precedes and constrains visual
design, not the reverse.

**Failure mode**: Starting visual design before the IA is validated with
research. Visual fidelity makes the wrong structure look credible, increasing
the cost of later correction.

### 3. There is no single correct IA

Only IAs that work better or worse for specific users and tasks. An IA that
serves a fashion designer navigating a product catalog fails a procurement
manager navigating an approval workflow — even if both work in the same system.
The question is always: *for which users, doing which tasks, in which contexts?*

### 4. Naming is structure

What something is called is as important as where it lives. A correctly placed
item with a confusing label will not be found. Label comprehension testing
(card sorts, tree tests, first-click tests) is not optional — it is how IA
decisions are validated. Route to `ia-research-methods` for protocols.

**Failure mode**: Using system or organizational language in navigation labels
rather than user task language. "Manage Assets" (system) vs. "My Files"
(task). "Administration" (org) vs. "Settings" (task). Users navigate by
their mental model, not by the product's internal architecture.

### 5. Findability and discoverability are different problems

**Findability**: Can users find something they know exists?
→ Solution: clear labeling, consistent structure, search.

**Discoverability**: Can users find something they don't know exists?
→ Solution: contextual navigation, related content, progressive disclosure,
empty states that surface capabilities.

Most IA failures conflate the two. A site can have excellent findability (if
you know what to look for, you can find it) but terrible discoverability (you
have no way to know what else exists). Enterprise products especially suffer
from low discoverability — new users can't learn the product's capability
through navigation alone.

---

## Cross-Hub References

### → `lead-ux-designer`
- `ux-information-architecture` spoke defers to this hub for deep expertise
- `ia-mental-models` ↔ `ux-research-synthesis`: mental model research and
  UX synthesis methods are closely related; both spokes serve the same
  understanding goal from different methodological angles
- `ia-navigation-systems` ↔ `ux-interaction-design`: navigation structure is
  defined here; interaction patterns (hover, transition, focus state) are
  implemented there
- `ia-research-methods` ↔ `ux-research-synthesis`: IA research methods are
  a specialization of UX research methodology

### → `lead-ui-designer`
- `ia-navigation-systems` → `uid-spatial-composition`: IA hierarchy must be
  visually expressible; spatial composition must support the IA levels
- `ia-taxonomy-classification` → `uid-visual-system`: classification
  hierarchies require visual differentiation; the visual system encodes IA depth

### → `lead-product-manager`
- `ia-mental-models` ↔ `pm-discovery-research`: mental model discovery and
  JTBD research address the same user understanding problem from different
  angles; align these before committing to IA structure
- `ia-enterprise-complexity` ↔ `pm-stakeholder-comms`: multi-role IA decisions
  require stakeholder alignment; PM and IA must align on role definitions before
  navigation design begins

### → `lead-backend-engineer`
- `ia-content-strategy` → `be-data-modeling`: content models directly map to
  database schema; IA and data modeling must be designed together, not in sequence
- `ia-taxonomy-classification` → `be-data-modeling`: hierarchical taxonomies
  require specific DB patterns (adjacency list, nested set, closure table);
  the IA choice of taxonomy depth and polyhierarchy support has direct DB implications

### → `lead-data-scientist`
- `ia-research-methods` → `ds-product-analytics`: navigation path analysis and
  search query analysis validate IA decisions quantitatively
- `ia-search-findability` → `ds-product-analytics`: zero-result query rate,
  search-then-abandon rate, and navigation-vs-search ratio are IA quality metrics

---

## Operating Directive

This hub and its spoke network operate at staff/principal IC depth. That means:

1. **Name the theorists.** IA has intellectual lineage — Lynch, Ranganathan,
   Craik, Indi Young, Norman, Wurman. Using named frameworks is not academic
   posturing; it provides precision and shared vocabulary for critique.

2. **Distinguish the failure mode.** Every major IA decision has a known
   failure mode. Surface it. A decision made without awareness of its failure
   mode is a guess.

3. **Structure before validation.** Articulate the proposed IA structure in
   words before recommending how to test it. "We're proposing a faceted
   taxonomy with 4 primary dimensions organized as [X]" precedes "we should
   run a card sort."

4. **Enterprise context is the default.** Unless stated otherwise, assume
   PLM-adjacent complexity: multi-role users, vertical-specific domain
   language, high-stakes navigation failures, and navigation that must scale
   from 10 to 100+ features over time.

---

## References

- Peter Morville & Louis Rosenfeld, *Information Architecture for the World Wide Web*
- Richard Saul Wurman, *Information Anxiety*
- Indi Young, *Mental Models*
- Kevin Lynch, *The Image of the City*
- S.R. Ranganathan, faceted classification theory (PMEST framework)
- Don Norman, *The Design of Everyday Things* (gulf of execution/evaluation)
- Donna Spencer, card sorting methodology
- Bob Bailey / Jared Spool, first-click testing research
