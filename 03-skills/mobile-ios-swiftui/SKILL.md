---
name: mobile-ios-swiftui
description: >
  Native iOS with Swift + SwiftUI — declarative UI, state management (@State/@Observable/
  bindings), the app/scene lifecycle, Swift concurrency (async/await, actors), Human
  Interface Guidelines, and the Xcode build/sign/TestFlight pipeline. Use when building or
  reviewing a native iOS app, or implementing iOS-specific behavior. Triggers: swift,
  swiftui, ios, xcode, observable, async await, actor, human interface guidelines,
  testflight, app store, UIKit.
aliases: [mobile-ios-swiftui]
triggers: [swift, swiftui, ios, xcode, observable macro, observableobject, async await, actor, human interface guidelines, testflight, app store, uikit]
tier: spoke
hub: lead-frontend-engineer
domain: engineering
prerequisites: [lead-frontend-engineer]
surfaces: ["*"]
spec_version: "2.0"
---

# Mobile — iOS (Swift + SwiftUI)

Native iOS. Component thinking transfers from web; the language, layout, and platform contract are Apple's.
Engineering fundamentals come from [[eng-foundations]]; this owns the iOS application.

## SwiftUI is declarative + state-driven
UI is a function of state, like React — but state is explicit and typed: `@State` (local), `@Binding`
(two-way), `@Observable`/`@Environment` (shared, the modern Observation framework replacing
ObservableObject). Layout is stacks + modifiers, not Flexbox. Think in value types (structs) and a single
source of truth for each piece of state.

## Concurrency is structured
Swift Concurrency (`async/await`, `Task`, **actors** for data-race safety, `@MainActor` for UI) is the
modern model — not GCD callbacks. Respect the main-actor boundary; isolate mutable shared state in actors.

## The platform contract
Follow the **Human Interface Guidelines** — iOS users expect native navigation, gestures, Dynamic Type,
dark mode, and accessibility (VoiceOver) as defaults, not extras (ties to [[a11y-assistive-tech]]). The
app/scene lifecycle, background modes, and permissions are OS-governed.

## Build + ship
Xcode project/workspace, signing + provisioning profiles, **TestFlight** for beta, App Store review. The
signing/provisioning model is the usual first-week wall — understand certificates, identifiers, profiles.

## Related
- hub → [[lead-frontend-engineer]]
- peer ↔ [[mobile-react-native]] · [[mobile-android-kotlin]] · [[mobile-platform-craft]]
