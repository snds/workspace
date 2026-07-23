#!/usr/bin/env bash
# Build a minimal, double-clickable macOS .app bundle around launch.py.
#
# This produces dist/WSX Generator.app. UNSIGNED as built here — run
# sign-notarize.sh afterward (once you have an Apple Developer ID) to make it
# open cleanly with no Gatekeeper prompt. Until signed, it still needs the
# right-click -> Open workaround, same as start.command.
#
# Usage:  bash packaging/make-macos-app.sh
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP="$ROOT/dist/WSX Generator.app"
BUNDLE_ID="design.snds.wsx-generator"   # change to your reverse-DNS id

rm -rf "$APP"
mkdir -p "$APP/Contents/MacOS" "$APP/Contents/Resources/payload"

# 1) Copy the generator payload into Resources (reuse package.py's notion of the
#    tree by copying the tool + launcher; excludes are best-effort here).
for item in generator brain .claude launch.py README.md VALIDATION.md; do
  cp -R "$ROOT/$item" "$APP/Contents/Resources/payload/"
done
find "$APP/Contents/Resources/payload" -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true
find "$APP/Contents/Resources/payload" -name '.DS_Store' -delete 2>/dev/null || true

# 2) Info.plist
cat > "$APP/Contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>CFBundleName</key><string>WSX Generator</string>
  <key>CFBundleDisplayName</key><string>WSX Generator</string>
  <key>CFBundleIdentifier</key><string>${BUNDLE_ID}</string>
  <key>CFBundleVersion</key><string>0.2</string>
  <key>CFBundleShortVersionString</key><string>0.2</string>
  <key>CFBundlePackageType</key><string>APPL</string>
  <key>CFBundleExecutable</key><string>wsx-generator</string>
  <key>LSMinimumSystemVersion</key><string>10.13</string>
</dict></plist>
PLIST

# 3) The bundle executable: opens Terminal on launch.py so the user sees the prompts.
cat > "$APP/Contents/MacOS/wsx-generator" <<'RUN'
#!/bin/bash
DIR="$(cd "$(dirname "$0")/../Resources/payload" && pwd)"
# Launch in Terminal so the interactive prompts are visible.
osascript <<OSA
tell application "Terminal"
  activate
  do script "python3 " & quoted form of "$DIR/launch.py"
end tell
OSA
RUN
chmod +x "$APP/Contents/MacOS/wsx-generator"

echo "✓ built: $APP"
echo "  Unsigned. Next: bash packaging/sign-notarize.sh  (needs your Apple Developer ID)."
