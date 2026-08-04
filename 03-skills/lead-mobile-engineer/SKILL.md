---
name: lead-mobile-engineer
description: >-
  Staff-level mobile engineering hub for native and cross-platform app work. Routes to four
  spokes: iOS (Swift + SwiftUI), Android (Kotlin + Jetpack Compose), React Native + Expo, and
  stack-agnostic platform craft (native-vs-cross-platform choice, lifecycle, offline-first,
  mobile performance, permissions, store release). Use when the target is a phone or tablet app
  rather than a web surface: "build an iOS screen", "Compose state hoisting", "React Native
  navigation", "why does the app get killed in the background", "offline sync", "cold start is
  slow", "TestFlight", "Play staged rollout", "should this be native or React Native". Owns the
  mobile-specific engineering gates (device constraints, lifecycle survival, store review, real
  low-end device measurement) that web frontend practice does not cover. Not for web frontend
  (use lead-frontend-engineer), not for mobile visual design (use lead-ui-designer).
aliases: [lead-mobile-engineer, mobile-lead]
triggers: [mobile engineering, mobile app, ios app, android app, react native, expo, swiftui, jetpack compose, kotlin android, native vs cross-platform, app lifecycle, offline first, cold start, testflight, play console, store review, mobile performance, push notifications, deep linking]
tier: hub
domain: engineering
prerequisites: [eng-foundations]
defers_to: [framework-13, framework-14, framework-16, eng-foundations]
rigor_role: command-hub
spec_version: "2.2"
---

# Lead Mobile Engineer

**Hub skill** for mobile application engineering. The component model and much of the state
thinking transfer from web, which is why these spokes lived under the frontend hub for a while.
What does *not* transfer is the reason this hub exists: the device is constrained and interrupted,
the OS owns the lifecycle, the release path goes through someone else's review queue, and the
quality signals are physical (cold start, jank, memory pressure, battery, thermal throttling).

Engineering fundamentals come from [[eng-foundations]]. Web-runtime depth stays with
[[lead-frontend-engineer]], which remains the peer hub for anything that is genuinely a browser
concern. This hub owns the mobile application.

## Spoke network, load on demand

Load the one or two spokes the question needs. The hub carries enough to triage and route.

| Spoke | Owns | Load when |
|---|---|---|
| [[mobile-ios-swiftui]] | Swift, SwiftUI, Observation, Swift Concurrency and actors, Human Interface Guidelines, Xcode signing and TestFlight | Native iOS implementation or review, iOS-only behavior, App Store submission |
| [[mobile-android-kotlin]] | Idiomatic Kotlin, coroutines and Flow, Jetpack Compose, Clean Architecture / MVVM, Material 3, Gradle and Play | Native Android implementation or review, KMP shared code, Play release |
| [[mobile-react-native]] | React Native and Expo, JSI runtime, Expo Router / React Navigation, native modules, FlashList, EAS | Cross-platform build from a React mental model, RN performance, OTA updates |
| [[mobile-platform-craft]] | Native-vs-cross-platform decision, lifecycle and background limits, offline-first and sync, mobile performance budgets, permissions and privacy, store submission | Architecture decisions, platform-quality review, anything that holds regardless of stack |

Routing shortcuts:

- **"Should this be native or cross-platform"** → `mobile-platform-craft` first, then the chosen
  stack spoke. Never answer from stack preference.
- **Performance complaint** (slow start, jank, battery) → `mobile-platform-craft` for the budget
  and the measurement discipline, plus the stack spoke for the specific profiler.
- **Offline or sync behavior** → `mobile-platform-craft`, plus [[be-api-design]] for the sync
  contract and conflict semantics.
- **Accessibility** → the stack spoke for the platform API, plus [[a11y-motor-physical]] and
  [[a11y-visual]] for the bar.
- **Auth, token storage, biometrics, certificate pinning** → [[sec-authn-authz]] and
  [[lead-security-architect]]. Mobile clients are untrusted; secrets in the binary are public.
- **Design and visual decisions** → [[lead-ui-designer]] and [[uid-spatial-composition]]. Platform
  conventions (HIG, Material) are design decisions with engineering consequences, not either alone.

## Core principles

**The OS is in charge.** Your process is suspended, resumed, and killed on the OS's schedule.
State survival (saved state, process death, configuration change) is a design requirement, not an
edge case. Assume every background task is interrupted.

**The device is a budget.** Memory, battery, thermal headroom, and network are finite and shared.
A feature that works on the newest phone on office wifi is untested. Measure on real low-end
hardware, on a degraded network.

**Offline is a state, not an error.** Design the local store, the sync direction, and the conflict
rule before the first fetch. Retrofitting offline behavior onto an online-only architecture is a
rewrite.

**Release cadence is not yours.** Store review, staged rollout, and the fact that users run old
versions for months change how you version APIs and feature-flag behavior. The client you shipped
last year is still calling your API.

**Platform convention beats cross-platform consistency.** Users judge the app against the other
apps on their phone, not against your other platform build. Diverge where the platform diverges,
and use a shared abstraction only where behavior genuinely is shared.

## Execution protocol

1. **Resolve the context profile** and the target platforms before anything else. Personal-solo and
   employer repos have different commit and review rules.
2. **Decide the stack deliberately** if it is not already fixed: `mobile-platform-craft`, judged on
   fidelity needs, team skills, and how much of the surface is genuinely platform-specific. Record
   it as an ADR; this decision is expensive to reverse.
3. **Shape before building.** Screens and navigation graph, state ownership, the data and sync
   model, permissions required and when they are requested, and the offline behavior.
4. **Load the stack spoke** and implement, hoisting state, respecting the main-thread or main-actor
   boundary, and keeping heavy work off the UI thread.
5. **Handle the lifecycle explicitly.** Save and restore state across background, process death,
   and configuration change. Verify by killing the app, not by backgrounding it.
6. **Budget and measure performance** on a real low-end device: cold start, scroll frame time,
   memory ceiling, and battery over a realistic session.
7. **Verify accessibility on-device** with the platform screen reader (VoiceOver or TalkBack),
   Dynamic Type or font scaling, and dark mode.
8. **Ship through the store path**: signing, staged rollout, crash and ANR monitoring, and a
   rollback that acknowledges you cannot recall a shipped binary (feature flag or server-side kill
   switch, not a hopeful hotfix).

## Done-gates

Per [#14 Engineering Operating Model](../../01-frameworks/14-engineering-operating-model.md) and
[[eng]]'s verb gates, with the mobile-specific additions:

- **Lifecycle survival proven.** State restores correctly after background, process death, and
  configuration change or rotation. Tested by forcing it, not by assuming it.
- **Offline and flaky-network behavior defined and exercised.** No infinite spinner, no silent data
  loss, no duplicate write on retry.
- **Measured on real low-end hardware.** Cold start, jank, and memory numbers come from a device,
  not a simulator. State the device and the numbers.
- **Permissions requested in context and degrade gracefully** when denied or revoked later.
- **Accessibility verified with the platform screen reader** and at scaled font sizes.
- **Release path complete**: signing and provisioning valid, staged rollout configured, crash and
  ANR monitoring live, and a kill switch or flag for the failure you can no longer patch quickly.
- **Client-side trust boundary respected.** Authorization is verified server-side; the binary
  contains no secret that matters, per
  [#16 Security Operating Model](../../01-frameworks/16-security-operating-model.md).

## Absolute bans

- **Never treat the simulator as evidence** for performance, memory, or battery claims.
- **Never ship a secret in the app bundle.** API keys, signing material, and tokens in the binary
  or in a plist are extracted, not hidden.
- **Never ship without a server-side or flag-based kill switch** for a risky feature. Store review
  latency means a bad build is live for days.
- **Never enforce authorization only in the client.** The UI hiding a control is not access
  control.

## Defers-to

- Workspace doctrine wins: [#13 Domain Rigor Stack](../../01-frameworks/13-domain-rigor-stack.md),
  [#14 Engineering Operating Model](../../01-frameworks/14-engineering-operating-model.md),
  [#16 Security Operating Model](../../01-frameworks/16-security-operating-model.md), then
  [[eng-foundations]] and [[eng]].
- Plugin depth (technique only): platform and library plugins may supply current API mechanics;
  they do not relax the gates or bans above. See [[process-plugins]].

## Related
- foundation → [[eng-foundations]]
- spoke → [[mobile-android-kotlin]] · [[mobile-ios-swiftui]] · [[mobile-platform-craft]] · [[mobile-react-native]]
- peer ↔ [[lead-frontend-engineer]]
