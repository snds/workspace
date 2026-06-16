---
name: mobile-platform-craft
description: >
  Cross-cutting mobile craft that applies whatever the stack (React Native, iOS, Android,
  Flutter) — the native-vs-cross-platform decision, app lifecycle + background limits,
  offline-first + sync, mobile performance (startup, memory, battery, jank), navigation
  patterns, permissions + privacy, and store submission. Use for mobile architecture
  decisions and platform-quality reviews. Triggers: native vs cross-platform, flutter,
  offline first, app lifecycle, mobile performance, battery, push notifications,
  permissions, deep linking, app store submission.
aliases: [mobile-platform-craft]
triggers: [native vs cross-platform, flutter, offline first, app lifecycle, mobile performance, battery, push notifications, permissions, deep linking, app store submission]
tier: spoke
hub: lead-frontend-engineer
domain: engineering
prerequisites: [lead-frontend-engineer]
governed_by: [a11y-motor-physical]
surfaces: ["*"]
spec_version: "2.0"
---

# Mobile — Platform Craft (stack-agnostic)

The mobile realities that hold whether you ship React Native, native iOS/Android, or Flutter. The
stack-specific spokes own *how*; this owns the cross-cutting *what + when*.

## Native vs. cross-platform — decide deliberately
- **Native** (Swift/Kotlin): best fidelity, platform APIs day-one, two codebases.
- **React Native / Flutter / KMP**: one codebase, faster shared iteration, occasional native escape hatches.
Decide by team skills, fidelity needs, and how much is genuinely platform-specific. Don't cross-platform a
deeply-native experience or native-build a content app.

## The device is constrained + interrupted
Unlike web: limited memory (the OS kills backgrounded apps), **battery** is a budget, network is flaky, and
the app is constantly suspended/resumed. Design **offline-first** (local store + sync + conflict handling),
handle the **lifecycle** (save state on background; assume process death), and treat connectivity as optional.

## Performance is felt physically
Cold-start time, scroll jank, memory pressure, and battery drain are the quality signals. Budget startup,
virtualize lists, lazy-load, cache images, and measure on *real low-end devices*, not just the simulator.
Pairs with [[fe-performance]] (perception) and [[sci-numerical-methods]] only where heavy compute is involved.

## Platform contract + ship
Respect per-OS navigation/gesture conventions and accessibility ([[a11y-motor-physical]], [[a11y-visual]]).
Permissions are privacy-gated and revocable — request in context, degrade gracefully. Shipping means store
review (Apple/Google), versioning, staged rollout, and crash/ANR monitoring.

## Related
- hub → [[lead-frontend-engineer]]
- governed-by → [[a11y-motor-physical]]
- peer ↔ [[mobile-react-native]] · [[mobile-ios-swiftui]] · [[mobile-android-kotlin]]
