---
name: mobile-android-kotlin
description: >
  Native Android with Kotlin + Jetpack Compose — idiomatic Kotlin (coroutines, null
  safety, flows), Compose declarative UI + state, Clean Architecture / MVVM, the activity/
  lifecycle model, Material 3, and the Gradle/Play build pipeline. Use when building or
  reviewing a native Android app or Kotlin Multiplatform shared code. Triggers: kotlin,
  android, jetpack compose, coroutines, flow, viewmodel, clean architecture, material 3,
  gradle, play store, KMP.
aliases: [mobile-android-kotlin]
triggers: [kotlin, android, jetpack compose, coroutines, kotlin flow, viewmodel, clean architecture, material 3, gradle, play store, kmp]
tier: spoke
hub: lead-frontend-engineer
domain: engineering
prerequisites: [lead-frontend-engineer]
surfaces: ["*"]
spec_version: "2.0"
---

# Mobile — Android (Kotlin + Jetpack Compose)

Native Android. Engineering fundamentals come from [[eng-foundations]]; this owns the Android application.
(Synthesized from idiomatic-Kotlin + Android-Clean-Architecture community practice.)

## Idiomatic Kotlin
Lean on the language: **null safety** (avoid `!!`; model absence with `?` and `?:`), **coroutines + Flow**
for async/streams (structured concurrency, scoped to lifecycle), data classes, sealed hierarchies for state,
and DSL builders. Idiomatic Kotlin is concise *and* safe — fighting the type system is a smell.

## Compose is declarative + state-hoisted
Jetpack Compose mirrors the React/SwiftUI model: UI = `@Composable` functions of state. **Hoist state**
(stateless composables + a state holder), drive UI from a `ViewModel` exposing `StateFlow`, and respect
recomposition (stable params, `remember`, keys). Material 3 is the default design language.

## Architecture
**Clean Architecture / MVVM** with clear layers (UI → domain → data), unidirectional data flow, and a
repository boundary. Kotlin Multiplatform (KMP) can share domain/data across Android + iOS when it pays off.
This is the application of [[eng-foundations]]'s contracts/abstraction principles on mobile.

## Lifecycle + ship
The activity/fragment + lifecycle-aware components model governs state survival (config changes, process
death — `SavedStateHandle`). Build with Gradle; ship via Play Console (app bundles, staged rollout).

## Related
- hub → [[lead-frontend-engineer]]
- peer ↔ [[mobile-react-native]] · [[mobile-ios-swiftui]] · [[mobile-platform-craft]]
