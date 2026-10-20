---
title: Fontface — see-through window (translucent sidebar) learnings
type: note
project: 25-fontface
created: 2026-10-20
source: Translucency session (branch claude/translucency in the Fontface repo, commit 0a99b61)
---

# Fontface: see-through window learnings

- Tauri 2.12.1 and later always allow a see-through window on macOS. The `macos-private-api` feature and `macOSPrivateApi` config flag are now no-ops; Fontface sets both anyway so they agree.
- Tauri's window effects (`set_effects`) put the OS blur under the web view: macOS uses an NSVisualEffectView (the "Sidebar" material is what native sidebars use), Windows 11 uses Mica. Tauri swallows failures, so the app must decide itself whether an effect will work (e.g. Windows build 22000 or later for Mica).
- The page then decides where the blur shows: anything with a transparent background shows it. Fontface keeps one token (`--sidebar` under `data-translucent` on <html>) so only the sidebars go see-through and content stays solid.
- macOS can switch see-through on and off live. Windows and Linux can only make a window see-through when it's created, so Fontface creates that window in code there (`"create": false` in the platform config) and a later "on" waits for the next launch.
- Windows 10's only blur (Acrylic) lags while dragging or resizing, per Tauri's own notes, so Fontface offers nothing there. Linux has no standard blur; plain see-through is off by default.
- macOS's Reduce transparency: `NSWorkspace.accessibilityDisplayShouldReduceTransparency`, with `NSWorkspaceAccessibilityDisplayOptionsDidChangeNotification` on NSWorkspace's own notification center for live changes. Windows: `HKCU\Software\Microsoft\Windows\CurrentVersion\Themes\Personalize\EnableTransparency` (0 = off).
- In WebKit, an unknown media query reads back as "not all" from `matchMedia(...).media`. That's how the page tells whether `prefers-reduced-transparency` is supported before trusting it.
- Contrast is the real constraint. Fontface's faint grey text (oklch 0.556) is only 4.7:1 on solid white, so any see-through tint over a dark desktop pushes it under WCAG AA (a 30% sidebar tint gave about 2.6:1). The fix: heavier tints (sidebar 45% light / 60% dark, content 92%) plus a stronger faint-text color only where the desktop shows through. A selected row's highlight is the weakest spot, because it shifts the background toward the text.
- Turn contrast into a test, not a judgment call: src/translucency.test.ts reads the tints from index.css and checks faint text at 4.5:1 and main text at 7:1 against a cautious worst-case backdrop (material #999 light / #737373 dark; raw black or white on Linux). Grey oklch(L 0 0) makes this easy: linear sRGB is L³, and the browser blends in encoded sRGB.
- Keep overlapping layers solid (the Table's sticky header and pinned columns). Two translucent layers on top of each other leave a ghost of the text underneath.
- Not seen live yet: how the tints look, plus rounded corners and shadow on the see-through window, need Sean's eyes.
