---
tags: [engineering, reliability, observability, error-handling, caching]
created: 2026-07-22
updated: 2026-07-22
status: stable
confidence: high
sources: [session-log 2026-07-22 (MediaSentinel 9.12 WLIIA re-process), MediaSentinel commits 3fad24e / b70e27b]
related_projects: [MediaSentinel]
---

# Silent degradation in fenced / advisory layers

A "fenced" layer is one deliberately built so its failure never breaks the pipeline: it
degrades to `None` / absent / a default and the deterministic path continues. Good design —
judgment should be advisory. But the **fence erases the distinction between "genuinely nothing"
and "the mechanism failed."** When those two collapse to the same value, a broken or
misconfigured layer looks identical to a healthy layer with nothing to report, and no error
surfaces anywhere. Found this pattern **three times in one MediaSentinel session**; treat it as
a family, not three coincidences.

## The three instances (all same shape)

1. **Swallowed timeout = no data.** `TranscriptStore._post_asr` caught `OSError` → `return
   None`. Sized for a 3.5-min cold open (900s timeout); when the window went full-episode a
   long whisper call could exceed 900s, and the timeout was indistinguishable from "this file
   has no transcript." A whole overnight batch could have come back quietly incomplete. Fix:
   raise the ceiling **and** make the ceiling a named constant that documents why it's high.

2. **Swallowed exception = no result.** The judgment client did `except Exception: return
   None` for every SDK error. Correct for the advisory contract, but it made **credit
   exhaustion identical to "no guest found"** — a mid-run balance wipe produced 94 silent
   `None`s while the queue reported 0 failures and the report looked healthy. Fix (commit
   3fad24e): classify the error (billing / auth / rate_limit / transient / other), count it on
   the client, and shout ONCE per fatal class to stderr. Still returns `None`; the degradation
   is just no longer invisible.

3. **Cache key omits a governing parameter = stale hit.** The transcript cache keyed on
   `(path, size, mtime)` — not the transcription window. Changing `COLD_OPEN_S=210` →
   full-episode without wiping `/config/transcripts` would silently keep the short transcripts
   (the file is unchanged, so the key matches). Compounding subtlety: the same key is shared by
   the window-independent sidecar/embedded paths, so **encoding the window into the key would be
   wrong for those sources.** The right lever was an explicit wipe on window change, not a key
   change. Any cache whose value depends on a parameter outside its key is a silent-staleness
   trap.

Adjacent, same root: the **progress counter lied**. The reconcile queue reported `437/438
done` while the expensive Opus vision pass hadn't started — the counter tracked feature
extraction, not the vision phase that carried ~all the wall-time and API spend. A monitor
keyed on queue-IDLE would have declared victory with a fifth of the work pending. Fix: key
completion on the real output signal (identity-file count climbing to N), not the queue state.

## Rules of thumb

- **A fenced layer needs a side channel for *why* it degraded** — a counter, a `last_error`, a
  one-time stderr line. Return `None` for control flow; record the cause for humans. The
  advisory contract and observability are not in tension.
- **`except Exception: return None` is a smell in any layer that spends money or time.** At
  minimum, classify fatal (auth/billing/quota) vs per-item before collapsing.
- **A timeout swallowed into "no data" is a silent-failure generator.** Size timeouts to the
  real workload, name the constant, and if possible distinguish timeout from empty.
- **If a cache value depends on a parameter, that parameter is in the key — or the cache is a
  staleness trap.** If it can't be in the key (shared with param-independent sources), the
  invalidation must be explicit and documented at the definition site.
- **Never trust a progress counter you didn't verify measures the expensive phase.** Monitor
  the real output artifact, and make your completion predicate emit on failure/stall too —
  silence must never read as success.

## The tell

When reviewing: grep for `return None`, `return default`, bare `except`, and `pass` in any
layer described as "graceful," "advisory," "best-effort," or "degrades." For each, ask: *if the
mechanism were completely broken right now, what would this return — and would anyone know?* If
the answer is "the same value, and no," that's the bug before it happens.
