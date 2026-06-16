---
name: mobile-react-native
description: >
  React Native + Expo for cross-platform mobile from a web/React mental model — the
  bridge/JSI architecture, navigation (Expo Router/React Navigation), native modules,
  platform-specific code, lists/perf (FlashList), and the build/release pipeline (EAS).
  Use when building or reviewing a React Native or Expo app, or deciding RN vs. native.
  Triggers: react native, expo, EAS, react navigation, expo router, native module, JSI,
  Hermes, FlashList, mobile React.
aliases: [mobile-react-native]
triggers: [react native, expo, eas, react navigation, expo router, native module, jsi, hermes, flashlist, mobile react]
tier: spoke
hub: lead-frontend-engineer
domain: engineering
prerequisites: [lead-frontend-engineer]
surfaces: ["*"]
spec_version: "2.0"
---

# Mobile — React Native + Expo

For a web/React developer crossing into mobile. The component model transfers; the runtime, navigation,
and platform realities do not. Foundations (complexity, contracts, testing) come from [[eng-foundations]]
via [[lead-frontend-engineer]]; this spoke owns the RN-specific application.

## The runtime is not the browser
RN renders to *native* views via JSI (the modern replacement for the async bridge) on the Hermes engine —
no DOM, no CSS box model (it's a Flexbox subset), no web APIs. Mental shift: you're orchestrating native
UI from JS, not painting a document. Reach for **Expo** by default (managed workflow, OTA updates, EAS
build) unless you need a custom native toolchain.

## Navigation + platform divergence
Navigation is a first-class architectural choice (Expo Router's file-based routing, or React Navigation) —
not an afterthought like web routing. Respect platform conventions: iOS and Android differ in back-gesture,
headers, and transitions. Use `Platform.select` / `.ios.tsx`/`.android.tsx` for genuine divergence, not to
paper over a bad abstraction.

## Performance
The JS thread and the UI/native threads are separate — jank comes from blocking JS or over-bridging.
Virtualize long lists (**FlashList** over FlatList), memoize aggressively, move animations to the native
driver (Reanimated), and keep heavy work off the JS thread. Profile with the right tool per platform.

## Native modules + release
When JS can't reach a capability, write/native-bridge a module (or use a community one). Shipping is **EAS
Build/Submit** + store review + OTA updates for JS-only changes — a fundamentally different release cadence
than web deploys.

## Related
- hub → [[lead-frontend-engineer]]
- peer ↔ [[mobile-ios-swiftui]] · [[mobile-android-kotlin]] · [[mobile-platform-craft]]
