# ADR-001 — Measured System47 fills on Literal surface

Date: 2026-08-09  
Status: accepted for `surfaceId: sys47.literal` only

## Context

Constitution tokens (`frame.bluegrey` `#C8D0E0`, etc.) were tuned for APCA bodyLabel floors. Native probes on S-SYS47-01 give header blue `#4f93ca` and related samples that differ substantially (Δe ≫ 3).

## Decision

On the Literal northstar surface `sys47.literal`, CSS variables `--sys47-*` take visual authority from measured IR fills. Global `TOKENS` remain for generative recipes and a11y-governed surfaces.

## Consequences

- Cue matrix color checks use IR samples, not constitution defaults.
- Do not retune global tokens to System47 without a separate a11y pass.
- When SVG-tracing the MSD, keep fills aligned to IR probes.
