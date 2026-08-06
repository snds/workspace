---
type: feedback
description: "Vendor / vendored" has two legitimate senses — commercial supplier, and engineering (copy external code into the repo). Do not ban the engineering sense. Still never call our own bespoke code "vendored".
created: 2026-07-21
updated: 2026-07-30
confidence: high
---

**Two legitimate senses of "vendor / vendored" — both OK. The old "paid-for only" ban is
struck (2026-07-30).**

Sean had reserved the word for commercial suppliers because that was the only sense he knew.
Engineering English also uses **to vendor / vendored / vendoring** for: take *external* code,
copy it into *our* tree, and treat that snapshot as ours to ship (instead of depending on it only
as a live package). That sense is standard (e.g. checking a library into `vendor/`, or keeping a
byte-identical copy of `@centric/data-table` in the SaaS PLM prototype). Prefer it over euphemisms
like "byte-identical package copy" when that is what you mean. It is **not** an AI/LLM-ism.

| What the thing is | Correct term |
|---|---|
| External code (OSS or internal package from another team) copied into our tree | **vendored · vendoring · vendor in** |
| Extra constraint that the copy must match upstream for a clean re-sync | **vendored + byte-identical / frozen / syncable** (policy on top of vendoring) |
| Live package we depend on without copying | **dependency · import · package** |
| Our own / shared / in-house code moved between *our* repos (palette we authored, `wsx` CLI we wrote) | **adopt · copy in · reuse · share · port · mirror** — **not** "vendored" (nothing external) |
| Local compatibility layer we write | **shim · write · author** |
| Paid SaaS / contractor / licensed asset | **vendor** (commercial sense) |
| PLM / supply-chain product copy | **vendor = supplier** ("Vendor Portal", "vendor quotes", VMS) — domain vocabulary, leave alone |

**Still wrong (the attribution concern that sparked the original rule stays):** calling *our* bespoke
work "vendored" credits an external party for something we made. The third historical correction
(`vendor_cli()` naming the bootstrap-generator's own CLI) was right for that reason — accurate
framing is **copied-in / self-contained copy of our CLI**, not "vendored CLI".

**How to apply:** before writing "vendored", ask only: *is this external code sitting in our tree?*
If yes → vendored. If it is ours → copy in / port / reuse. If it is a live dependency → dependency.
If it is a paid commercial party or a PLM supplier → vendor (noun). Do not reach for a workaround
word because the engineering sense "feels odd".

**History:** corrected three times under the old paid-only ban (Base UI tag; Phase 1b palette;
`wsx` `vendor_cli()`, 2026-07-23). Ban retired 2026-07-30 after Sean confirmed the engineering
sense was unfamiliar, not wrong — `check-terminology.py`'s `vendor-as-verb` rule retired with it.
