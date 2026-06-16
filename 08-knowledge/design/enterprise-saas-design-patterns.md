---
tags: [enterprise-saas, plm, patterns, design-systems, components, layouts]
created: 2026-05-12
updated: 2026-05-12
status: stable
confidence: high
sources:
  - "Mobbin audit (Stream A — 20 PLM-critical patterns + 6 deep re-audits)"
  - "Mobbin audit (Stream C — 8 AI-forward patterns)"
  - "Synthesis pass 2026-05-12"
related_skills: [ds-advisor, design-engineer, workspace-bootstrap]
related_projects: [02-centricPLM, 10-centric-UX-research, 17-data-table]
trigger_words:
  - enterprise saas
  - PLM layout
  - data table
  - record detail
  - record header
  - bulk edit
  - saved view
  - filter chip
  - side panel
  - drawer
  - approval workflow
  - audit trail
  - activity feed
  - csv import
  - permissions
  - rbac
  - inbox
  - notifications
  - cell anatomy
  - status pill
  - lifecycle
  - diff view
  - version history
  - record comparison
  - merge records
  - tree table
  - BOM
  - centric layout
  - ai suggestion
  - ai summary
  - provenance
---

# Enterprise SaaS Design Patterns — Operational Reference

> **Load this when building anything enterprise-SaaS-shaped.** Composing a
> Centric PLM screen, a B2B web layout, a record-shaped detail page, a
> data-table surface, or an AI-augmented UI. This entry is the operational
> distillation of the 2026-05-12 Mobbin audit — it tells you which patterns to
> reach for, which primitives compose them, and which discipline to apply.
>
> The synthesis (long-form) lives at
> `04-artifacts/active/enterprise-saas-pattern-synthesis_v0.1_2026-05-12.md`.
> The audit sources are next to it.

---

## The first move: identify the surface shape

Before reaching for any pattern, classify the surface you're building. This
single decision determines 80% of the pattern selection.

```
Is the surface...
├─ A list/table of records?          → Tier 2 patterns (A1+A2+A11+A12+A4)
├─ A single record's detail page?    → Tier 1+3 (A6+A15+A10/A13+A8)
├─ A workflow / approval flow?       → Tier 3 (A7+A14+A10)
├─ A data input flow?                → Tier 2 (A17 or A16)
├─ An inbox / notification surface?  → Tier 3 (A20 + A10 stream)
├─ An admin / RBAC surface?          → Tier 4 (A19)
├─ A comparison / merge view?        → Tier 4 (A9)
└─ Anything AI-augmented?            → Stream C primitives + surface-specific tier
```

If the surface doesn't fit one of these shapes cleanly, it's probably a
**composition** of two or three. That's normal for enterprise SaaS — most real
screens combine a record-detail + an embedded list + a drawer for related
records, etc.

---

## The cross-pattern primitive spine

**The 15 primitives below underlie all 28 audit patterns.** Build these first;
the patterns are configurations of these primitives.

### Stream A — structural spine (8 primitives)

| Primitive | One-line use | Pattern occurrences |
|---|---|---|
| **`StatusPill`** | Tokenized state badge with per-vertical color set. | A1, A3, A6, A7, A14 |
| **`Drawer`** | Right-side panel (preview / action / listing / chat / canvas), 3 sizes. | A3, A6, A8, A13, A15, A20 |
| **`TypedFieldEditor`** | Per-type editor: text / number / date / select / multi-select / reference / boolean / image / file. **Same primitive serves cells, form fields, and import targets.** | A3, A16, A17, C1 |
| **`ActivityItem`** | avatar + actor + verb + object-chip + timestamp + optional inline diff. | A10, A14, A20 |
| **`RelationChip`** | Typed-link selector + record reference + remove. Hover triggers Drawer preview. | A6, A10, A12, A13 |
| **`Stepper`** | 3 layouts: numbered pill / vertical left-rail / inline-section. State: complete / current / locked / future. | A7, A16, A17 |
| **`PropertiesRail`** | Right-rail of typed key-value rows. Same primitive in record header, drawer detail, inbox detail. | A6, A15, A20 |
| **`KeyboardShortcutMenu`** | Right-click context menu where every action carries a single-letter shortcut. **The productivity multiplier.** | A20, propagate to A4, A11, B1 |

### Stream C — AI-provenance spine (7 primitives, treat as checklist)

| Primitive | When to use |
|---|---|
| **`ConfidenceIndicator`** | When AI produces a variant. Numeric % when computable, visual pip ladder otherwise. |
| **`AnchoredToSourceSpan`** | When AI makes a factual claim about a record. **Hover-traceable to evidence.** Default for regulated PLM. |
| **`GeneratedVsVerifiedState`** | When AI fills a typed cell or field. Three sub-states: `generated.unverified / accepted / stale`. Tokens. |
| **`InsufficientInputAcknowledgment`** | AI declines to invent when input is empty / corrupt / off-topic. Better blank than wrong. |
| **`MistakeCaveat`** | Standing uncertainty disclaimer. Quiet but present at every AI write surface. |
| **`DestructiveWriteGate`** | Non-bypassable confirmation when AI overwrites prior user content. |
| **`CreditCostTransparency`** | Surface AI compute cost where the user triggers it (header pill, per-node accounting). |

---

## "When you need to build X" — pattern routing

### Building a list of records

→ **Patterns:** A1 density toggle (Vanta 3-radio) + A2 column manager (Neon dropdown
default / Whop modal at >30 fields / Salesforce split-pane when ordering matters)
+ A11 view switcher with layout radio (Table / Kanban / Tree / Calendar) + A12
sectioned filter chip builder (Apollo) + A4 selection-conditional action bar
(Apollo highlighted-primary).
→ **Primitives:** `TypedFieldEditor` in display mode + `StatusPill` per row + `KeyboardShortcutMenu` for bulk actions.
→ **First decision:** flat / hierarchical / kanban-shaped data? → A11 layout pick.
→ **Density default:** `density.regular`. Always expose the toggle in the toolbar; never bury in settings.
→ **Empty state:** functional, not decorative. Template / import CTAs (per B3).

### Building a record detail page

→ **Patterns:** A6 record header (title + status pill + breadcrumb + paginated
nav + metadata rail) + A10 activity feed OR A13 related-records sections
(or tabs over both) + A8 version-history rail + A15 drawer for relation preview.
→ **Primitives:** `RecordHeader` composite + `PropertiesRail` (right-rail) + `RelationChip` (chips on hover → drawer preview) + `Drawer` (right-side, 3 sizes).
→ **First decision:** rail content is metadata (A6) or activity (A10)? Often both → tabs.
→ **Inline status:** put status on the header AND inline next to relevant fields (ElevenLabs Call Status pattern). Status appears in 2-3 places in a record; that's OK.

### Building a workflow / approval surface

→ **Patterns:** A7 lifecycle (StatusPill + Stepper + PipelineLane based on
metaphor fit) + A14 Asana action-triad approval drawer (Approve / Changes
requested / Reject) + A10 activity feed of approval events.
→ **Primitives:** `StatusPill` + `Stepper` + `ActivityItem`.
→ **First decision:** action-triad shape (Asana) or stage-shape (Rox pipeline / Lightfield kanban)?
→ **Privacy banner:** explicit visibility statement on approval drawers ("Visible to collaborators and people with access to parent task"). PLM regulated workflows require this.
→ **Inline comment thread + Leave-approval CTA:** approval is a conversation, not a button-press.

### Building a data input flow

→ **Bulk-shaped (CSV):** A17 import wizard. Use Clay's split-pane (file controls
+ mapping + preview live data) + Rox's Auto-map shortcut + AutoSend's
mapped/unmapped counter + Copy.ai's explicit column-exclusion with Undo.
**Validation step (5 must-haves):** error visualization (red cells + tooltip)
+ error resolution drawer (HubSpot Ways-to-fix-this-error options) +
**partial-import CTA always available** (7shifts `Import N/M`) + tabbed
valid/error split (Fresha) + filter `Show only rows with errors` toggle (Remote).
+ **Compliance gate** (AutoSend permission checkboxes) for regulated bulk.
→ **Single-record-shaped:** A16 multi-step form. Pick layout per step interdependence:
left-rail (ElevenLabs sequential-deep), top-stepper (Whop bounded modal),
inline-section (AutoSend in-page), checklist-cards (Origin non-sequential).
→ **Primitives shared:** `TypedFieldEditor` + `Stepper` + cell-anatomy validation states.
→ **Schema convention:** Zod on the code side; mirror its types in the typed-field token set.

### Building an inbox / notification surface

→ **Pattern:** A20 Linear model. Action triad header (Delete / Snooze /
Unsubscribe) + snooze menu (`An hour / Until tomorrow / Until next week / A
month / Custom`) + keyboard-first context menu (every action with single-letter
shortcut: U mark unread / H snooze / S status / A assignee / P priority / L
labels / D set due date) + master-detail with full thread inline + self-reminders
flow back through inbox + bulk actions (`Mark all as read ⌥U / Delete all`).
→ **Primitives:** `ActivityItem` as inbox row + `PropertiesRail` in detail + `KeyboardShortcutMenu` + `Drawer` (master-detail).
→ **First decision:** channel-tabbed (Dialpad: Approvals / Comments / Mentions / Changes / System) or single-stream (Linear-style)? **PLM needs channel-tabbed.**
→ **Empty state:** Todoist celebration ("Nice work! You're all caught up.") — small but real adoption lever.

### Building a comparison / merge surface

→ **Compare (no merge intent):** A9 Chatbase model. N-column with each column a record card, sync toggle to drive shared inputs, add-instance CTA.
→ **Merge (dedupe / dual-master conflict):** A9 Salesforce model. Two-column with **per-attribute radio "Use as principal"**, empty-value placeholders shown explicitly (`[empty]`), Back/Next step pagination.
→ **Primitives shared:** `RecordHeader` per column + aligned rows for attribute comparison.
→ **First decision:** compare or merge? Different primitives, related vocabulary.

### Building an admin / RBAC surface

→ **Patterns:** A19. Role-CRUD (OpenAI Platform: name + Preset/Custom pill +
description + Assignments/Permissions) + descriptive-role picker (Jira: each
role explains what it grants in the dropdown) + grant matrix (Mixpanel:
user × project × role table) + scoped-role (Gusto: condition + scope + role-type).
+ Integrated admin overview (Whop: members + 2FA toggle + audit log inline).
→ **Primitives:** `StatusPill` (role type) + `TypedFieldEditor` (member rows) + `PropertiesRail` (per-user detail).
→ **First decision:** role-centric (define roles, assign users) or user-centric (assign per user)? Pick one default; document the other as power-user view.

### Building an AI-augmented surface

→ **Gate first:** which Stream C provenance primitives apply?
- AI fills cells/fields → `GeneratedVsVerifiedState` token + `ConfidenceIndicator`.
- AI overwrites prior content → `DestructiveWriteGate` always.
- AI makes factual claims → `AnchoredToSourceSpan` (Maze model, default for PLM).
- AI metered → `CreditCostTransparency` (Fireflies pill).
- AI write surface → `MistakeCaveat` (quiet but present).
- AI received insufficient input → `InsufficientInputAcknowledgment` (Manus model).

→ **Patterns by task:**
- Per-row AI columns → C1 (Clay Up-to-date ✓ + X variant-pick).
- AI chat about a record → C2 (Fireflies suggestion chips + credit transparency).
- AI document drafting → C3 (WRITER categorized suggestions + Asana destructive gate).
- AI workflow config → C4 (Asana NL → generated rule canvas). Defer — emerging.
- AI record summary → **C8 (Maze anchored-to-source) — highest PLM-leverage pattern.**

→ **PLM default:** prefer anchored-to-source over confidence-percentage. Regulated industries care less about "78% confidence" and more about "this claim points to this verifiable evidence."

---

## Token vocabulary implied by the pattern set

The audit established a tokenized primitive set. These tokens should land in
Centric DS:

### Density tokens

```
density.dense      → row-height: 32px, vertical-padding: 4px, inline-font: -1
density.regular    → row-height: 44px, vertical-padding: 8px, inline-font: 0   (default)
density.comfortable → row-height: 60px, vertical-padding: 16px, inline-font: 0
```

Calibrate against Centric's existing token scale; the values above are illustrative.

### Status state vocabulary

```
status.draft / pending / in-review / approved / released / rejected / obsolete
+ per-vertical extensions:
  fashion: line-locked, costed, sample-approved, bulk-go
  food: formula-approved, label-locked, lab-pending
  engineering: spec-locked, eco-pending, released-revision
```

Each state carries a color token + icon + label. Per-vertical color choice can
override base; semantic stays consistent.

### Cell state matrix (A3 + C1 unified)

```
read / hover / focus / editing / error / dirty / locked / computed
+ AI states (C1):
  generated.unverified  (newly produced, awaiting confirmation)
  generated.accepted    (user reviewed and confirmed)
  generated.stale       (source data changed; needs regeneration)
```

These are **outer-state-envelope tokens** — the cell type's affordance (caret
for select, calendar for date, etc.) sits inside the envelope; the envelope's
visual treatment is consistent regardless of cell type.

### Drawer size tokens

```
drawer.preview   → ~360px   (relation hover, quick inspect)
drawer.standard  → ~480px   (record detail, edit)
drawer.wide      → ~720px   (multi-section, AI chat, canvas)
```

### Stepper state tokens

```
stepper.complete / current / locked / future
```

---

## Provenance discipline for AI features

Apply this checklist to **every AI surface** before shipping:

```
[ ] Generated content has a visible provenance signal (state token, badge,
    or anchored-to-source link).
[ ] Confidence is surfaced when computable (numeric ± or visual ladder).
[ ] Destructive writes (overwriting prior content) require explicit confirmation.
[ ] AI surfaces show a quiet "AI can make mistakes" caveat at the write point.
[ ] When the AI receives insufficient / corrupt input, it acknowledges rather
    than invents.
[ ] Compute / credit cost is transparent where the user triggers AI.
[ ] AI-generated claims about regulated records are hover-traceable to a source
    span (preferred over confidence-percentage alone for PLM).
[ ] AI-generated cells are visually distinct from human-entered values, even at
    a glance.
```

For PLM specifically:
- **Compliance language**: never let AI ship without a `MistakeCaveat` and an `AnchoredToSourceSpan` to the original source (audit doc, supplier test, formulation entry).
- **BOM cost figures**: AI summary should never invent numbers. If a cost can't be derived from the BOM, return `InsufficientInputAcknowledgment` rather than estimate.
- **Approval recommendations**: AI suggestions for approval routing are advisory; the action triad (Approve / Changes / Reject) remains human. AI can pre-fill the comment field; never the action.

---

## Pattern catalog (28 entries) — compact reference

### Stream A — Section A (PLM-critical, 20 patterns)

- **A1 Data table density** — Vanta 3-radio toolbar control. → density tokens.
- **A2 Column management** — Neon dropdown (default) / Whop modal (>30 fields) / Salesforce split-pane (ordering). Distinguish schema-level vs view-level.
- **A3 Cell anatomy + state matrix** — Clay typed cells + Neon date presets + Canva named-preset select. Type-aware + state-aware. The cell-state vocabulary is foundational.
- **A4 Bulk selection + action bar** — Apollo contextual-bar with highlighted-primary. Defaults appear on selection, contextual to selected rows.
- **A5 Tree / BOM navigation** — Origin canonical tree-table (chevron in first cell + indent guide line + per-column aggregation). Group-by-row is a sibling primitive.
- **A6 Record detail header** — ElevenLabs title + branch pill + breadcrumb + paginated nav + right metadata rail. Inline status on fields.
- **A7 Lifecycle / state** — StatusPill primitive + Stepper (bounded sequential) + PipelineLane (kanban + stage admin). Three sub-primitives.
- **A8 Change set / diff** — ElevenLabs/Neon side-by-side + Google AI Studio multi-file + Hume/GitBook version-history rail. `LineDiff` primitive is shared.
- **A9 Comparison + merge** — Chatbase compare (N-column + sync) OR Salesforce merge (per-attribute radio). **Two distinct primitives.**
- **A10 Audit trail + activity feed** — Todoist chip-embedded narrative + Aboard structured wide-table. Same event stream, two surfaces.
- **A11 Saved views** — Apollo full-config drawer (View name + Layout radio + Group by + Fields + Filters + Visibility/sharing). Notion Mail template gallery for onboarding.
- **A12 Filter chips** — Apollo sectioned builder (typed chip groups by section). Shop chip-strip + sidebar for high-dimension cases. Mixed-control panel for non-chippable.
- **A13 Relations / linked records** — Jira inline `relates to` chip + Salesforce section-tabbed related-records mini-tables. Fibery is the schema-level editor.
- **A14 Approval workflows** — Asana drawer with **Approve / Changes requested / Reject** action triad + visibility banner + comment thread + Leave-approval CTA. Three sub-primitives.
- **A15 Drawer / side panel** — Three sizes × three shapes (preview / action / listing). Linear master-detail is canonical.
- **A16 Multi-step form** — Four layouts: ElevenLabs left-rail (sequential deep) / Whop top-stepper (bounded modal) / AutoSend inline-section / Origin checklist-cards (non-sequential). Reuses typed-field primitive set.
- **A17 CSV import wizard** — Clay split-pane preview + Rox auto-map + AutoSend counters + Copy.ai column-exclusion. Plus validation step (7shifts/Fresha/HubSpot/Remote — 5 must-haves, see "data input flow" routing).
- **A18 Background jobs** — Four foreground-progress modes (full-page status / multi-item counter / segmented bar / spinner-with-destination). **Task-center / queued-jobs-list pattern not in Mobbin — Section D follow-up.**
- **A19 Permissions / RBAC** — OpenAI Platform role-CRUD + Jira descriptive-role picker + Mixpanel grant matrix + Gusto scoped-role + Whop integrated admin. Five primitives.
- **A20 Notifications / inbox** — Linear model (the canonical work-inbox). Action triad + snooze menu + keyboard-first context menu + master-detail + self-reminders + bulk actions.

### Stream C — AI-forward (8 patterns)

- **C1 Inline AI in cells** — Clay row-level Up-to-date ✓ + X multi-variant with confidence + Notion Mail track-changes-style. → `GeneratedVsVerifiedState` token added to A3.
- **C2 AI side-panel chat with record context** — Fireflies smart-suggestion chips + "Consumes AI credits" + references list + thumbs-up/down. → Drawer + PropertiesRail reuse.
- **C3 Generated-then-edited documents** — WRITER inline-rewrite menu + categorized suggestions panel + Asana destructive-write modal + Gamma asset-generation with style controls. → DestructiveWriteGate.
- **C4 NL workflow config** — Asana NL prompt → generated rule canvas (visible) + Ask-for-changes input. **Emerging — re-audit 2027-Q3.**
- **C5 Embedded canvases in records** — Clay workflow canvas + Deputy field-palette + Sana AI multi-source context picker + Runway sketch tools. Emerging.
- **C6 Voice input / dictation** — Base44 inline mic in input + ElevenLabs upload-or-record + history rail. Low PLM priority but fashion-floor reality.
- **C7 Diff-and-merge for AI** — X variant-pick (current state of the art) + OpenAI version-switch consequence. True merge not yet canonical — watch.
- **C8 Per-record AI summary** — **Maze anchored-to-source span (the standard for regulated PLM)** + Fireflies references + Manus insufficient-input acknowledgment + Rox "Command can make mistakes" caveat. **Highest PLM-leverage AI pattern.**

---

## Anti-patterns

Watch-fors that surfaced during the audit:

- **Density buried in settings menus.** Vanta puts it in a toolbar settings popover next to columns. Density is a frequent-retune control, not a configuration buried two levels deep.
- **Bulk actions in a permanent toolbar.** QuickBooks's persistent "Batch actions" dropdown is harder to discover than Apollo's selection-conditional contextual bar. The toolbar that appears *on selection* with primary action highlighted is the right default.
- **Multi-step bulk wizards as the only bulk pattern.** Jira's 4-step wizard is appropriate for mass operations with preview/validation. Wrong default for single-action bulk (delete, change status).
- **Modal-record-detail pattern** (Deputy custom-field modal). Legacy enterprise; avoid for new records. Drawer (A15) handles peek-without-navigation correctly.
- **Approval as a single button.** Asana's action triad (Approve / Changes / Reject) is necessary — single-button approval forces ambiguity into the comment field.
- **Pricing-tier patterns repurposed for record comparison.** Aligned rows work, but the marketing context bleeds into B2B-record UX. Use Chatbase's instance-comparison shape instead; reuse only the mechanic.
- **AI confidence percentages alone for regulated claims.** "78% confident" doesn't help an auditor; anchored-to-source-span does. Default to spans for PLM.
- **AI write without a destructive-write gate.** Asana's "Replace existing content?" should be the default any time AI is about to overwrite prior content.
- **AI invents when input is empty.** Manus's "this recording appears to be a test" pattern is the discipline — better to acknowledge than to fabricate.
- **Tag-chip-heavy rows defeat density tokens.** When every row carries 3-5 pill chips, perceived row height ≈ 2× the CSS row-height. Chip-cells have their own density tax that the density token can't fully control. Account for this in the cell-anatomy spec.
- **AI workflow builders without a visible generated rule.** If the AI translates NL to a workflow, *show the rule* (Asana's pattern). Don't ask the user to trust an invisible translation.
- **Inbox without keyboard shortcuts.** Linear's productivity edge is single-letter shortcuts for every action. PLM tables operate at scale where keyboard is essential.

---

## Cross-references

### Audit source (this entry's foundation)
- `04-artifacts/active/enterprise-saas-pattern-taxonomy_v0.1_2026-05-12.md` — original taxonomy
- `04-artifacts/active/enterprise-saas-pattern-audit_section-a_v0.1_2026-05-12.md` — Stream A audit (20 patterns + 6 deep re-audits)
- `04-artifacts/active/enterprise-saas-pattern-audit_ai-forward_v0.1_2026-05-12.md` — Stream C audit (8 patterns)
- `04-artifacts/active/enterprise-saas-pattern-synthesis_v0.1_2026-05-12.md` — synthesis (impact-ranked, primitives consolidated, cross-stream tensions resolved)

### Skills
- `02-skills/ds-advisor/SKILL.md` — strategic / triage / governance lens
- `02-skills/design-engineer/SKILL.md` — component / code / primitive lens
- `02-skills/figma-canvas-designer/SKILL.md` — when laying out screens in Figma

### Frameworks
- `00-frameworks/02-ui-ux-operational-framework.md` — sits above this entry
- `00-frameworks/05-last-mile-craft-framework.md` — finishing discipline applies to every pattern shipped
- `00-frameworks/06-qa-operating-model.md` — target-user lens for verifying the patterns work in context

### Knowledge entries that pre-date this one
- `08-knowledge/design/centric-plm-design-system.md` — Centric DS strategy, token architecture, Ark UI decision
- `08-knowledge/design/centric-plm-frontend-stack.md` — DataTable API surface + framework-specific quirks
- `08-knowledge/cross-domain/figma-source-audit-patterns.md` — adjacent audit method

### Pending pattern-specific entries
See the synthesis "Graduation queue" — 28 entries pending. Graduate one-by-one
as Centric work creates demand. Don't pre-author; let demand drive depth.

---

## How to use this when generating layouts

1. **Identify surface shape** from the decision tree at the top.
2. **Compose primitives first.** Decide which 4-6 primitives apply, then which
   patterns configure them.
3. **Reach for tokens, not pixels.** Density, status, cell-state, drawer-size,
   stepper-state vocabulary above.
4. **Apply provenance discipline** if AI is involved (checklist).
5. **Cross-check the anti-patterns** before declaring the layout done.
6. **For Centric specifically**, layer the vertical context (Fashion / Food /
   Engineering) on top of the base vocabulary — status color extensions, role
   names, BOM-specific tree behavior.

If a brief mentions specific surface words ("data table", "record detail",
"bulk edit", "approval", "audit log", "inbox"), this entry should auto-surface
via the knowledge-index trigger and become the spine of the response.
