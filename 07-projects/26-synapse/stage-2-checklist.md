# What's left in Stage 2

_The Synapse app's Stage 2. Code and plan: `snds/synapse` (local checkout `/Users/sean.sands/Projects/synapse`). Baton: [SESSION-STATE.md](SESSION-STATE.md)._

Stage 2's goal is to see and manage the workspace without asking an agent ([plan](https://github.com/snds/synapse/blob/main/docs/stage-2/STAGE-2.md)). Everything is built except the parts that need signing or other hardware. This is what's left, in order. Sections 1–7 need you. Section 8 is what Claude builds without you. The exit tests (S1–S14) are in [STAGE-2.md](https://github.com/snds/synapse/blob/main/docs/stage-2/STAGE-2.md#exit-tests).

**Where it stands (2026-10-17):** the scorecard passes 9 of 13 automated tests on T1b (S3–S9, S13, S14). S2, S10, S11 and S12 wait for the steps below. S1 is your own tally.

## 1. Your UI feedback (item 1)

- [ ] **Open the app on sample data:**

  ```bash
  cd /Users/sean.sands/Projects/synapse/app && npm run dev
  ```

  Then open http://localhost:1430. For the desktop window on your live workspace, run `npm run tauri dev` instead.
- [ ] **Go through every screen, in light and dark:** Home, Projects, Health, Domains & skills, the Library (open a file, change a property, try a merge), the graph and its list, an impact review, Agent apps, Settings, and the ⌘K palette.
- [ ] **Decide the small type sizes.** Every screen passes APCA Bronze. APCA's Silver target flags 1,198 elements, almost all because Silver allows no text under 14px. The labels are 11–12px today: keep them, or raise them.
- [ ] **Pass:** your notes are written down, and Claude reworks the screens before anything else is built on them.

## 2. Keyboard and screen reader (S10)

The automated half passes: 0 serious findings on 14 screens in both themes, and 0 elements under APCA Bronze. Automated checks find about a third of real problems, so a person finishes it.

- [x] **Keyboard only, on every screen:** reach and use every control with Tab, the arrows, Return, Escape and ⌘K. Focus is always visible, and nothing traps it.
- [x] **Library:** open a file, edit it, save with ⌘S, settle a merge, and open and accept an impact review.
- [x] **Graph:** find a node and follow its edges from the inspector. The list version does everything the canvas does.
- [x] **VoiceOver (⌘F5):** each screen's heading is read; the selected row is announced as current; the editor's text can be read; dialogs are announced and close with Escape.
- [x] **Pass:** 0 serious issues. Claude fixes anything you find, and the scorecard marks S10 passed. **Done 2026-10-19:** Sean found zero issues; the scorecard reads it from `docs/stage-2/manual-checks.json`.

## 3. Obsidian round trip (S2)

The fight guard is built and tested. What's left is the live session the [watch-guard spike](https://github.com/snds/synapse/blob/main/spikes/watch-guard/RESULT.md) couldn't do: Obsidian open while the app writes. It runs on a test vault, never on your own.

- [x] **Claude makes the test vault** (a copy of T1b): done 2026-10-18, at `/Users/sean.sands/Projects/synapse-sandbox/s2-vault` (2,146 files, with the workspace's own `.obsidian` settings). Every file's hash is recorded.
- [ ] **Point the service at it.** Quit the service from its menu, then:

  ```bash
  cd /Users/sean.sands/Projects/synapse && python3 scripts/s2-roundtrip.py point /Users/sean.sands/Projects/synapse-sandbox/s2-vault
  ```

  Then start the app as usual; it starts the service on the test vault.
- [ ] **Open it in Obsidian** (Open folder as vault) with your usual Linter settings (lint on save on, lint on file change off).
- [ ] **With the app running:**
  - [ ] Type in a note in Obsidian while the app applies a fix to the same note. The app waits out the quiet period and never overwrites your typing.
  - [ ] Save a note in Obsidian (the Linter runs) that has a waiting fix in the app. The fix is drafted again or set aside, and nothing is lost.
  - [ ] Edit a note in the app's Library while it's open in Obsidian. Obsidian shows the change, and nothing is duplicated or reverted.
  - [ ] Undo one of the app's fixes in Obsidian, twice within a minute. The app sets the file aside and asks.
  - [ ] Rename a note in Obsidian. It keeps its ID (S6).
- [ ] **Compare,** naming each note you edited on purpose (one `--intended` per note):

  ```bash
  cd /Users/sean.sands/Projects/synapse && python3 scripts/s2-roundtrip.py compare /Users/sean.sands/Projects/synapse-sandbox/s2-vault --intended <path of a note you edited>
  ```

- [ ] **Put the service back on your workspace.** Quit it from its menu, then:

  ```bash
  cd /Users/sean.sands/Projects/synapse && python3 scripts/s2-roundtrip.py restore /Users/sean.sands/Projects/synapse-sandbox/s2-vault
  ```

  and start the app again.
- [ ] **Pass:** 0 files changed outside the intended edits (the compare above; the scorecard reads its result), and the app stops and asks rather than fight.

## 4. An Apple team (items 5, 14, 16)

The Mac unlock (Touch ID), native notifications and the app bundle all need the app signed by an Apple team.

- [ ] **Try the free route first:** Xcode → Settings → Accounts → add your Apple ID. That gives a free "Personal Team", which may be enough on your own Macs. Tell Claude the team ID (10 characters, shown under the team).
- [ ] **Otherwise:** the Apple Developer membership, which is still with Apple support.
- [ ] **Then Claude builds:**
  - the device key in the keychain, bound to your current Touch ID set, with your device password as the fallback;
  - locking when the screen locks or the Mac sleeps, plus the tray's Lock item and `sy lock`;
  - the service as a helper app inside the app;
  - native notifications, and Settings → Notifications.
- [ ] **Pass:** S14 with Touch ID. After the idle timeout, a screen lock or sleep, saved fixes can't be read until you unlock (scenario X8).

## 5. The Windows PC (items 14, 15)

Claude tells you before starting, because it needs the PC for a while.

- [ ] **Your YubiKey's firmware version:** Yubico Authenticator shows it, or `ykman info`. The recovery passkey needs 5.2 or later (D71).
- [ ] **D72's Hello spike:** a Windows Hello passkey with PRF, compared with the other Hello routes, using a platform passkey and the YubiKey.
- [ ] **Every exit test on the PC:** S2–S14. For S8, the catalog's verified Windows apps are found.
- [ ] **Then Claude ties in** the Windows Hello key provider.
- [ ] **Pass:** S11, Windows matches the Mac.

## 6. Signing and release (item 16, D94)

- [ ] **Decide how Windows builds are signed:** Microsoft's Artifact Signing (about $9.99 a month, open to individuals in the US, billed from the day the account exists), or a commercial certificate (about $150–300 a year).
- [ ] **Mac:** Developer ID signing and notarization. These need the paid membership (section 4).
- [ ] **The updater's signing key:** created once and kept outside the repo, in your password manager. Claude gives you the command when it's time.
- [ ] **Then Claude builds:** signed builds in CI, the updater (the service updates with the app), and the uninstaller.
- [ ] **Pass:** S12, a clean uninstall on both systems (no autostart entries, nothing left outside the data folder), and a signed release.

## 7. Two last checks

- [x] **S13 from another account.** With the service running, try its socket as the built-in `nobody` account (nothing is created):

  ```bash
  cd /Users/sean.sands/Projects/synapse && sudo -u nobody nc -U "/Users/sean.sands/Library/Application Support/design.snds.sy/run/service.sock"
  ```

  **Pass:** refused ("Permission denied"). **Done 2026-10-19** on the Personal MacBook Pro (as `/Users/snds/...`): refused, exit 1. `nc -v` printed no reason; `nobody` can't enter the home folder, and `run/` and the socket are owner-only. The scorecard reads it from `docs/stage-2/manual-checks.json`.
- [ ] **S1, daily use:** for two weeks, check status in the app instead of asking an agent. **Pass:** 10 of 10 working days, and a note of what's missing.

## 8. What Claude builds without you

- [x] **Health's tool buttons (item 7):** run doctor, the harness and the nightly rebuild through the tool runner, with their results as issues. Done 2026-10-18: Health → Tools.
- [x] **A skill page (item 8):** a skill's document beside its contract: triggers, edges, what governs it, and its check status. Done 2026-10-18: a skill's sheet → Open the page.
- [x] **Windows CI builds the desktop app too (item 15).** Done 2026-10-18: the `Desktop app (Windows)` job, whose unsigned build is kept a week as an artifact for the PC.
- [x] **An unsigned Mac app bundle** with the service inside as a helper app, so packaging, autostart from the bundle and the uninstall can be rehearsed before signing. Done 2026-10-18 ([mac-bundle.md](https://github.com/snds/synapse/blob/main/docs/stage-2/mac-bundle.md)), with `sy-service --uninstall` and the S12 check `scripts/leftovers.py`.
- [ ] **The updater's wiring,** everything but the key. Waits on a decision of yours: the repo is private, so its releases can't serve an updater. Where are updates published (a public releases repo, a Cloudflare bucket or Pages site)?
- [ ] **Docs:** this list, STAGE-2.md and the scorecard updated as each item closes.

## Outcome

Stage 2 is done when S1–S14 pass on your Mac and the Windows PC, the [security review](https://github.com/snds/synapse/blob/main/docs/stage-2/security-review.md) is updated, and there's a signed release. Then Stage 3: import, create, measure ([roadmap](https://github.com/snds/synapse/blob/main/docs/plan/07-roadmap.md#stage-3-import-create-measure)).
