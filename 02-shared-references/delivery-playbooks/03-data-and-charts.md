---
title: Data & Charts — takeaway first, chart second
status: canonical
date: 2026-07-09
tags: [data, charts, dataviz, delivery]
---

# Data and charts — takeaway first, chart second

Fires when the deliverable is data, results, metrics, or comparisons. The craft standard
(form, color, marks, interaction) lives in the **`dataviz` skill** — load it before writing
the first line of chart code. This playbook adds the audience layer on top.

---

## Audience rules (on top of the dataviz standard)

- **The title states the takeaway,** not the topic. "Blocked sources never reached the queue"
  beats "Queue ingress by source category." A chart whose conclusion must be derived by the
  reader fails the forward test ([[01-audience-contract]]).
- **Annotate the reading, not the data.** One plain-english callout on the feature that
  matters ("this spike is the outage on June 3rd") does more than a second axis.
- **Plain-english axis labels and units.** "Articles per day," not "ingress_count."
- **The caveats-at-the-top rule applies** ([[01-audience-contract]]): sample size, time
  window, what was excluded — stated on or beside the chart, not buried in an appendix.
- Tables are for looking up values; charts are for seeing a shape. If the reader needs exact
  numbers, deliver both — chart for the story, table for the reference.

## Format

- Per [[artifact-standards]]: self-contained, versioned, double-click to open. `.xlsx` for
  tabular data a non-developer will work with; never raw JSON/CSV as the final deliverable.
- Judge rendered output at native resolution per [[10-perception-integrity]] before calling
  it clean.

## Pre-delivery checklist

0. Context profile resolved and cited? ([[00-context-profiles]] — always first)
1. `dataviz` skill loaded before the chart was built?
2. Title = takeaway? Annotations = reading, not decoration?
3. Caveats visible at the top altitude?
4. Would the number-free version (the shape alone) still tell the right story?
