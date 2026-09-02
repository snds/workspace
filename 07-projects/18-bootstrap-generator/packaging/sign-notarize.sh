#!/usr/bin/env bash
# Sign + notarize + staple the macOS app so it opens with NO Gatekeeper prompt.
# Run this AFTER make-macos-app.sh, once you have an Apple Developer ID.
#
# Nothing secret is stored in this repo. You provide credentials at runtime via
# environment variables (or a keychain profile). Example:
#
#   export WSX_SIGN_ID="Developer ID Application: Your Name (TEAMID)"
#   export WSX_APPLE_ID="you@icloud.com"
#   export WSX_TEAM_ID="TEAMID"
#   export WSX_APP_PW="xxxx-xxxx-xxxx-xxxx"   # app-specific password (appleid.apple.com)
#   bash packaging/sign-notarize.sh
#
# See packaging/macos-notarization.md for the full walkthrough.
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP="$ROOT/dist/WSX Generator.app"
ZIP="$ROOT/dist/WSX-Generator-notarize.zip"

: "${WSX_SIGN_ID:?set WSX_SIGN_ID to your 'Developer ID Application: … (TEAMID)'}"
[ -d "$APP" ] || { echo "✗ $APP not found — run make-macos-app.sh first."; exit 1; }

echo "1/4 codesign (deep, hardened runtime)…"
codesign --force --deep --options runtime --timestamp \
  --sign "$WSX_SIGN_ID" "$APP"
codesign --verify --deep --strict --verbose=2 "$APP"

echo "2/4 zip for notarization…"
rm -f "$ZIP"
/usr/bin/ditto -c -k --keepParent "$APP" "$ZIP"

echo "3/4 notarytool submit (waits for Apple)…"
if [ -n "${WSX_KEYCHAIN_PROFILE:-}" ]; then
  xcrun notarytool submit "$ZIP" --keychain-profile "$WSX_KEYCHAIN_PROFILE" --wait
else
  : "${WSX_APPLE_ID:?set WSX_APPLE_ID}"; : "${WSX_TEAM_ID:?set WSX_TEAM_ID}"; : "${WSX_APP_PW:?set WSX_APP_PW}"
  xcrun notarytool submit "$ZIP" \
    --apple-id "$WSX_APPLE_ID" --team-id "$WSX_TEAM_ID" --password "$WSX_APP_PW" --wait
fi

echo "4/4 staple the ticket to the app…"
xcrun stapler staple "$APP"
xcrun stapler validate "$APP"

echo "✓ signed + notarized: $APP"
echo "  Ship it (zip the .app): ditto -c -k --keepParent \"$APP\" dist/wsx-generator-macos-signed.zip"
echo "  It now opens with a normal double-click — no 'unidentified developer' prompt."
