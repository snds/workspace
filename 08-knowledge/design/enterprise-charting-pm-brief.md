---
tags: [design-system, charts, product-management, briefing, plm]
created: 2026-09-10
updated: 2026-09-10
status: working
confidence: medium
audience: product-management
related: [enterprise-charting-and-dataviz]
trigger_words:
  - charting pm brief
  - charting for product
---

# Charts in the product — a plain briefing for product management (2026-09-10)

Research snapshot, not a committed roadmap. The first real build should be small. Product still needs to say which surface gets it first.

This is the product-management version of [[enterprise-charting-and-dataviz]]. That file keeps the design and engineering detail.

---

## In one paragraph

People need to *see* the shape of their data, not only scroll a grid. Sometimes a chart sits above a list and clicking it narrows the list. Sometimes a chart lives on a dashboard and is just there to explain how things are going. We already have a tiny “chart these cells” popup in the table. We should use **one free charting tool** for all of that, look like the rest of Centric, and when the data means good or bad, use the **same green and red** the rest of the product already uses. We will copy good ideas from IBM’s chart system. We will **not** install IBM’s chart software — it is heading toward end of life.

---

## What users are trying to do

**1. Understand a list faster, then work the list.**

Imagine a page of styles. Above the table is a simple bar chart: Approved, At risk, Blocked. The user clicks **Blocked**. The table now shows only blocked rows. A chip appears that says so. They can dismiss the chip and the table goes back. Clicking a slice of a stacked bar does the same kind of thing for that slice.

The chart is a filter you can see. It is not decoration.

**2. Check how the business is doing, without a table underneath.**

A home dashboard, a season recap, a supplier scorecard. The chart may not drive a grid on the same page. It still has to look like us, load honestly, and say when something is empty vs when something broke.

**3. Glance at a trend on a number card.**

A big number with a tiny spark of a line. No axes. No extra software. Click the card if they want more.

**4. Chart a handful of cells they just selected.**

Power users already get a small popup (bar, line, pie, scatter) from a table selection. Keep that. Do not build a second charting world just for the popup.

---

## What we recommend

**One charting tool, used everywhere we draw a real chart.**

The tool is Apache ECharts. It is free for companies. It can do simple popups and hard dashboards. It works for the React work in the design system and the Vue work in the main product. We wrap it so every chart looks like Centric, not like a demo from the internet.

The little table popup can use that same tool. Today it uses a smaller library because that was convenient, not because the free tool cannot draw a small chart. Two tools means two looks and twice the upkeep. We should not keep both once we commit.

**Tiny trends on number cards do not need that tool.** A short line in the card is enough.

**We copy IBM’s *ideas*, not IBM’s product.**

IBM Carbon Charts is one of the few design systems that took charts seriously: how color works, how a keyboard user reads a chart, how you can “view this as a table.” Their software version is in maintenance and is scheduled to end in 2027. Installing it, or forking it to keep it alive, would mean we own someone else’s aging product. If IBM deleted the repo tomorrow, our charts should still work.

**We will not pay for “advanced” chart features.**

Several popular tools look free until you need zoom, maps, or linked charts — then they want a license. We are not starting down that path.

---

## Color: when green means good

The rest of the product already has a meaning for color:

- Green = positive / success / on track
- Red = negative / failed / blocked
- Orange = warning / at risk
- Yellow = caution / watch
- Cyan (not brand blue) = info / draft / unknown
- Gray = no judgment

Charts must use **those same colors** when the data itself is a status. A bar for “Blocked” should be the same red as a Blocked pill. A line for “Approved” should not be a random purple from a rainbow.

**When the data is not a status, do not use those colors.**

A chart of styles **by mill** is just names. Painting Italy green because that mill had a good week tells a lie. Italy is a place, not a health score. Use a plain set of distinct colors that do not mean good or bad.

**Numbers need a “which way is good?” note.**

“Up” is not always green. Margin above plan: up is good. Defect rate above target: up is bad. If we do not know which way is good, we do not paint it as success and failure. We wait until the metric is defined.

Color is never the only clue. A label, an icon, or a pattern sits with the color so people who cannot tell red from green can still read the chart.

---

## What “done” looks like for a first release

Not twenty chart types. Two useful pieces plus the rules above:

1. A **status (or category) bar** on a list page. Click a bar, the table filters, a chip shows what you clicked.
2. A **time chart** that can filter a date or period the same way.
3. Tiny trend lines on the number cards we already have.
4. The table’s “chart my selection” popup, still there, eventually using the same tool.

If a click on a chart cannot show up as a chip the user can clear, that click is not finished.

---

## What we are asking product to decide

1. **Where does this land first?** The design-system work (React) or the main product (Vue)? That picks the first wrapper, not the tool.
2. **Who provides the rolled-up numbers for the widgets?** A chart on a page with tens of thousands of rows cannot draw every row in the browser. The widget shows totals. The table stays a filtered list. That needs an agreement with engineering, not a chart library.
3. **Are network pictures in scope?** Supplier maps and bill-of-materials trees are a different kind of drawing. Say so early if they are.
4. **Will a customer or legal review later require a vendor accessibility certificate?** If yes, that is a later exception with a written license path — not a quiet swap of tools.

---

## What we will not do

- Buy Highcharts, or any tool that hides the useful parts behind a paywall.
- Install IBM’s chart package, or fork it.
- Build twenty chart types before the click-to-filter behavior works.
- Let a chart use a private green that is not the product’s success green.
- Treat “the chart is pretty” as done if a keyboard or screen-reader user cannot get the same numbers.
