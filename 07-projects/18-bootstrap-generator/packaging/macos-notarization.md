# macOS notarization — the frictionless double-click path (optional, ~$99/yr)

The free zips (`package.py`) already work for a non-technical user via **Path A**
(open the folder in an AI app → "set up my workspace") and, without an AI app, via
right-click → Open on `start.command`. This guide is only for when you want a
**clean, no-prompt double-click** — which on macOS requires an Apple Developer ID
and notarization. Nothing here changes the free path; it adds a signed `.app`.

Everything is scripted (`make-macos-app.sh`, `sign-notarize.sh`) so adding the cert
later is drop-in — no rework of the generator or the zips.

## One-time setup

1. **Enroll** in the Apple Developer Program — https://developer.apple.com/programs/
   ($99/year). Personal enrollment is fine.
2. In **Xcode → Settings → Accounts**, add your Apple ID, then **Manage
   Certificates → +  → Developer ID Application**. This creates the
   `Developer ID Application: Your Name (TEAMID)` signing identity in your keychain.
   (Xcode command-line tools are enough if you prefer; the cert must be a
   *Developer ID Application*, not a Mac App Store cert.)
3. Create an **app-specific password** at https://appleid.apple.com → Sign-In &
   Security → App-Specific Passwords (for `notarytool`).
4. Find your **Team ID**: `xcrun notarytool --help` referencing, or Apple Developer →
   Membership. It's the 10-char code in the cert name.

Optional but nicer — store credentials once in the keychain and skip env vars:

```
xcrun notarytool store-credentials WSX_NOTARY \
  --apple-id "you@icloud.com" --team-id "TEAMID" --password "xxxx-xxxx-xxxx-xxxx"
export WSX_KEYCHAIN_PROFILE=WSX_NOTARY
```

## Each release (three commands)

```
bash packaging/make-macos-app.sh          # builds dist/WSX Generator.app (unsigned)

export WSX_SIGN_ID="Developer ID Application: Your Name (TEAMID)"
export WSX_KEYCHAIN_PROFILE=WSX_NOTARY     # or set WSX_APPLE_ID/WSX_TEAM_ID/WSX_APP_PW
bash packaging/sign-notarize.sh           # codesign → notarytool → staple

ditto -c -k --keepParent "dist/WSX Generator.app" dist/wsx-generator-macos-signed.zip
```

Ship `wsx-generator-macos-signed.zip` instead of `wsx-generator-macos.zip` for the
frictionless path. Windows/Linux are unaffected (no notarization needed).

## What each step does

- **codesign --options runtime --timestamp** — signs the bundle with your Developer
  ID and enables the hardened runtime + a secure timestamp (both required by
  notarization).
- **notarytool submit --wait** — uploads to Apple's notary service; Apple scans it
  and returns "Accepted" (usually < 5 min).
- **stapler staple** — attaches the notarization ticket to the app so it verifies
  offline. After this, a normal double-click just works — no "unidentified
  developer" dialog.

## Caveats / honest notes

- The app here launches Terminal to run `launch.py` (so the prompts are visible).
  A signed *script-based* app notarizes fine; if Apple ever tightens script-app
  rules, the fallback is to embed a tiny compiled launcher — but that's not needed
  today.
- Notarization must be redone for **each build** you distribute (the ticket is
  per-binary). The three commands above are the whole loop.
- The cert renews yearly ($99). If it lapses, already-notarized/stapled builds keep
  working; you just can't sign new ones until you renew.
- **Never commit** your app-specific password or `.p12` cert exports. This repo only
  ever reads them from env/keychain at runtime.
