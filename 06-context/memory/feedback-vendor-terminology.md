---
type: feedback
description: "Vendor / vendored" is only for paid-for external services/work/content — never a synonym for "brought into the repo", and never for our own or open-source code
created: 2026-07-21
confidence: high
---

**"Vendor" / "vendored" is reserved for _paid-for_ external services, work, content, or context.
It is NOT a synonym for "copied into the repo", and it does not apply to our own bespoke code or to
open-source dependencies.**

Correct term by what the thing actually is:

- **Our own / shared / in-house code** moved between our repos (e.g. the generated colour palette) →
  **adopt · copy in · reuse · share · port · mirror**. Sean built these, with my help — attributing
  them to a "vendor" is factually wrong on two counts: not paid-for, and not external.
- **Open-source dependency** → **dependency · add · import · use**. Open source isn't paid, so its
  authors are not "vendors".
- **A local compatibility shim we write** → **shim · write · author**.
- **Actual paid vendor** (a SaaS we pay for, a paid contractor, licensed/paid data or assets) →
  *this* is the only correct use of "vendor / vendored".

**Domain caveat — don't over-correct:** in PLM / supply-chain context, "vendor" legitimately means a
**supplier** (a paid third party) — so "Vendor Portal", "vendor quotes", "VMS (Vendor Management
System)", "nominated vs vendor-sourced supplier" in the product/domain docs are **correct** and must
not be changed. The rule governs *my meta-descriptions of code, dependencies, and decisions*, not the
domain vocabulary.

**Why:** it's an attribution error, not a style nit — calling our work "vendored" credits an external
paid party for something we made. **How to apply:** before writing "vendor/vendored" about anything
technical, check: is it literally something we pay an external party for? If not, use adopt / copy in
/ reuse / dependency / shim. Corrected twice (the Base UI "vendor" tag on the alignment page, then the
"vendored" palette in Phase 1b) — reach for the accurate verb the first time.
