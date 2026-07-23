"""Lifecycle + maintenance commands: lint, verify, session, sync, resolve, doctor."""
from __future__ import annotations

import os
import shutil
import sys
from pathlib import Path

from . import adapters, core, yamlio


# ------------------------------------------------------------------ doctor ---
def doctor() -> int:
    """Check the environment and tell the user exactly what to do next.

    Designed for the 'I ran it and nothing happened' moment: it explains where
    you are (generator vs. workspace) and the one command to run.
    """
    print("wsx doctor — checking your setup\n")
    print(f"  python3   : ✓ {sys.version.split()[0]}")
    git = shutil.which("git")
    if git:
        print(f"  git       : ✓ {git}")
        # A missing identity makes every `git commit` fail — silently, unless we say so.
        # This is the #1 reason a fresh workspace ends up with zero commits.
        import subprocess
        def _cfg(key):
            r = subprocess.run(["git", "config", "--get", key], text=True,
                               capture_output=True, check=False)
            return (r.stdout or "").strip()
        who, mail = _cfg("user.name"), _cfg("user.email")
        if who and mail:
            print(f"  git id    : ✓ {who} <{mail}>")
        else:
            print("  git id    : ⚠ not set — commits may fail, or be recorded under a")
            print("                guessed name. Set it once so your history is yours:")
            print('                git config --global user.name  "Your Name"')
            print('                git config --global user.email "you@example.com"')
    else:
        print("  git       : ✗ not found — install GitHub Desktop "
              "(https://github.com/apps/desktop) for sync + history")
    here = os.getcwd()
    print(f"  here      : {here}")
    root = core.find_workspace_root()
    if root:
        print(f"  workspace : ✓ {root}\n")
        print("  You're inside a workspace. Useful next:")
        print("    wsx verify            # check it's healthy")
        print("    wsx emit claude-code  # make it AI-ready")
    else:
        print("  workspace : — none here (this is the GENERATOR, not a workspace)\n")
        print("  The generator BUILDS a separate workspace folder. To create yours:")
        print('    wsx init ~/Documents/Projects/Workspace --name "Your Name"')
        print("  …or just open this folder in your AI assistant and say:")
        print('    "set up my workspace"')
    return 0


# -------------------------------------------------------------------- lint ---
def lint(root: Path) -> int:
    """Validate skills + manifest; report trigger overlaps. Returns problem count."""
    problems = 0
    trigger_owners: dict[str, list] = {}
    skills = list(core.iter_skills(root))
    man = core.load_manifest(root)
    recs = man.get("skills", {})

    for name, sk in skills:
        fm, body = core.parse_frontmatter(sk)
        if not fm.get("name"):
            print(f"  ✗ {name}: missing 'name' in front matter")
            problems += 1
        if not str(fm.get("description", "")).strip():
            print(f"  ✗ {name}: missing 'description' in front matter")
            problems += 1
        # un-enriched skeleton: the brain must replace the `_(…)_` writing prompts
        # (and drop the skeleton banner) before shipping. Pulled skills are exempt —
        # they arrive finished from a registry, not from our skeleton.
        if fm.get("source", "generated") == "generated":
            prompts = body.count("_(")
            if "skeleton —" in body or prompts:
                detail = f"{prompts} unfilled prompt(s)" if prompts else "skeleton banner still present"
                print(f"  ⚠ {name}: un-enriched skeleton — {detail}; "
                      "fill the body, then `wsx skill reindex`")
                problems += 1
        # composite skills must cite: if the manifest records references, the body
        # must carry the Sources block (the attribution the citations are for).
        rec = recs.get(name, {})
        if rec.get("references") and "wsx:sources" not in body and "Sources & further reading" not in body:
            print(f"  ⚠ {name}: composite skill has {len(rec['references'])} recorded "
                  "reference(s) but no Sources block — re-run `wsx resolve` to cite them")
            problems += 1
        for t in core.skill_triggers(fm):
            trigger_owners.setdefault(t, []).append(name)

    for trg, owners in sorted(trigger_owners.items()):
        if len(owners) > 1:
            print(f"  ⚠ trigger overlap: '{trg}' claimed by {', '.join(owners)} "
                  "— assign one canonical owner (see brain/resolver.md)")
            problems += 1

    # manifest sanity
    if man.get("schema_version") != "0.2":
        print(f"  ⚠ manifest schema_version is {man.get('schema_version')!r} (expected '0.2')")
        problems += 1

    if problems == 0:
        print(f"✓ lint clean — {len(skills)} skill(s), no trigger overlaps")
    else:
        print(f"lint found {problems} issue(s) across {len(skills)} skill(s)")
    return problems


# ------------------------------------------------------------------ verify ---
def verify(root: Path) -> int:
    """Dry-run: round-trip the profile and gather each emit target. Returns failure count."""
    fails = 0

    # 1. profile round-trips through the YAML subset
    prof = core.load_profile(root)
    try:
        reparsed = yamlio.loads(yamlio.dumps(prof))
        if reparsed != prof:
            print("  ✗ profile.yaml does not round-trip through the YAML subset")
            fails += 1
        else:
            print("  ✓ profile.yaml round-trips cleanly")
    except Exception as e:  # noqa: BLE001
        print(f"  ✗ profile.yaml failed to parse: {e}")
        fails += 1

    # 2. each adapter can gather without error (no files written)
    for target in ("claude-code", "agents-md", "cursor", "pack"):
        try:
            adapters.gather(root, prof)
            print(f"  ✓ {target}: ready to emit")
        except Exception as e:  # noqa: BLE001
            print(f"  ✗ {target}: gather failed — {e}")
            fails += 1

    # 3. required canonical files exist
    for rel in ("context/project-context.md", "context/session-log.md", "manifest.json"):
        if not (root / rel).exists():
            print(f"  ✗ missing canonical file: {rel}")
            fails += 1

    # 3a. SAFETY: never let a declared-but-unimplemented security property stand. A
    # person who sets encrypt:true may believe personal.md is encrypted at rest — it is
    # not; it is only gitignored. Say so loudly rather than imply a guarantee we don't keep.
    if prof.get("privacy", {}).get("encrypt"):
        print("  ⚠ privacy.encrypt is true, but wsx implements NO vault encryption.")
        print("    Gitignoring a file is not encryption. `context/personal.md` is excluded")
        print("    from git and from every emitted adapter, and that is all. For real")
        print("    at-rest protection use FileVault/BitLocker or an encrypted volume.")

    # 3b. Declared vs. actual transport: profile.transport.remote is just a recorded
    # string; only `wsx remote <url>` configures git. If they disagree the person thinks
    # their work is backed up when nothing can push.
    declared = str(prof.get("transport", {}).get("remote", "") or "").strip()
    if declared:
        r = core.git(root, "remote", "get-url", "origin", check=False, capture=True)
        actual = (r.stdout or "").strip()
        if not actual:
            print(f"  ⚠ profile declares a remote ({declared}) but git has none configured —")
            print(f"    nothing can sync. Wire it: wsx remote {declared}")
        elif actual != declared:
            print(f"  ⚠ remote mismatch — profile says {declared}, git says {actual}.")
            print(f"    Reconcile with: wsx remote {actual or declared}")

    # 4. pinned content still matches its pin — pulled skills (byte-identical, read-only)
    #    and any cached composite references. Both must stay verifiable/re-fetchable.
    man = core.load_manifest(root)
    pins = []  # (label, path, pin)
    for name, rec in man.get("skills", {}).items():
        if rec.get("pin"):
            pins.append((name, rec.get("path", ""), rec["pin"]))
        for ref in rec.get("references", []):
            if ref.get("pin") and ref.get("cached"):
                pins.append((f"{name}:ref", ref["cached"], ref["pin"]))
    ok = 0
    for label, rel, pin in pins:
        f = root / rel
        if not f.exists():
            print(f"  ✗ {label}: pinned content missing on disk ({rel})")
            fails += 1
        elif core.sha256_file(f) != pin:
            print(f"  ✗ {label}: on-disk content diverged from its pin — pinned content "
                  "must stay byte-identical (patch via overlay, or re-run `wsx resolve --update`)")
            fails += 1
        else:
            ok += 1
    if pins:
        print(f"  ✓ {ok}/{len(pins)} pinned item(s) (pulled skills + cached refs) match their pin")

    print("✓ verify passed" if fails == 0 else f"verify found {fails} failure(s)")
    return fails


# ------------------------------------------------------------- self-healing ---
def ensure_safe_git(root: Path) -> None:
    """Idempotently re-assert the safe multi-device git defaults, healing drift if a
    global config or another tool ever flipped them. Cheap; run before any sync."""
    try:
        cur = core.git(root, "config", "--local", "--get", "rebase.autoStash",
                       check=False, capture=True).stdout.strip()
        if cur != "false":
            core.git(root, "config", "--local", "rebase.autoStash", "false", check=False)
    except Exception:
        pass


# --------------------------------------------------------------- compaction ---
import re as _re


def compact(root: Path) -> int:
    """Fold context/sessions/*.md fragments into context/session-log.md, newest-first,
    idempotently (dedupe by the SessionID marker). Same conflict-free model the
    generator's own workspace uses: sessions write disjoint fragment files (no merge
    conflicts across devices/sessions), and this folds them into the readable log."""
    log_path = root / "context" / "session-log.md"
    frag_dir = root / "context" / "sessions"
    if not log_path.exists() or not frag_dir.is_dir():
        return 0
    log = log_path.read_text(encoding="utf-8")
    frags = sorted(p for p in frag_dir.glob("*.md") if p.name != "README.md")
    if not frags:
        # No fragments to fold, but still bound the log if it has grown large.
        n = _archive_old_blocks(log_path)
        if n:
            print(f"✓ compact: archived {n} old block(s) → session-log-archive.md (token-frugal).")
        return 0
    sid_re = _re.compile(r"^SessionID:\s*(\S+)", _re.MULTILINE)
    date_re = _re.compile(r"^Date:\s*(\d{4}-\d{2}-\d{2})", _re.MULTILINE)
    new, folded = [], 0
    for f in frags:
        text = f.read_text(encoding="utf-8").strip()
        if not text:
            f.unlink(); continue
        m = sid_re.search(text)
        marker = m.group(1) if m else text.splitlines()[0]
        if marker and marker in log:
            f.unlink(); folded += 1  # already folded elsewhere — drop the dup
        else:
            new.append((f, text, (date_re.search(text) or [None, "0000-00-00"])[1] if date_re.search(text) else "0000-00-00"))
    if new:
        new.sort(key=lambda t: (t[2], t[0].name), reverse=True)
        block = "\n\n".join(t[1] for t in new) + "\n\n"
        marker = "## Session Entries"
        idx = log.find(marker)
        if idx == -1:
            log = log.rstrip() + f"\n\n{marker}\n\n---\n\n" + block
        else:
            sep = log.find("\n---", idx)
            at = (log.find("\n", sep + 1) + 1) if sep != -1 else idx + len(marker) + 1
            log = log[:at] + "\n" + block + log[at:]
        log_path.write_text(log, encoding="utf-8")
        for f, _t, _d in new:
            f.unlink()
    archived = _archive_old_blocks(log_path)
    if new or folded or archived:
        msg = f"✓ compact: folded {len(new)} new, dropped {folded} already-folded fragment(s)."
        if archived:
            msg += f" Archived {archived} old block(s) → session-log-archive.md (token-frugal)."
        print(msg)
    return 0


# Token frugality: keep the LIVE session log small (~48 KB ≈ 12k tokens of the
# newest work); older blocks move to session-log-archive.md, read only on demand.
# Bounds the log's read cost at O(1) instead of O(sessions). Content-preserving.
_LIVE_BUDGET_BYTES = 48000


def _archive_old_blocks(log_path: Path) -> int:
    text = log_path.read_text(encoding="utf-8")
    marker = "## Session Entries"
    idx = text.find(marker)
    if idx == -1:
        return 0
    body_start = idx + len(marker)
    head, body = text[:body_start], text[body_start:]
    if len(body.encode("utf-8")) <= _LIVE_BUDGET_BYTES:
        return 0
    first = body.find("\n### ")
    if first == -1:
        return 0
    lead, blocks_text = body[:first], body[first:]
    blocks = [b for b in _re.split(r"(?=\n### )", blocks_text) if b.strip()]
    kept, kept_bytes, cut = [], 0, []
    for b in blocks:
        if not cut and kept_bytes + len(b.encode("utf-8")) <= _LIVE_BUDGET_BYTES:
            kept.append(b); kept_bytes += len(b.encode("utf-8"))
        else:
            cut.append(b)
    if not cut:
        return 0
    pointer = ("\n\n> _Older entries archived to [session-log-archive.md]"
               "(session-log-archive.md) to keep this file cheap to read. "
               "Ask to see it only if you need older history._\n")
    log_path.write_text(head + pointer + lead + "".join(kept), encoding="utf-8")
    arch = log_path.with_name("session-log-archive.md")
    prior = arch.read_text(encoding="utf-8") if arch.exists() else (
        "# Session Log — Archive\n\n_Older session blocks, moved out of session-log.md "
        "to keep the live log token-cheap. Newest archived first._\n\n## Session Entries\n")
    ai = prior.find(marker)
    if ai == -1:
        prior = prior.rstrip() + f"\n\n{marker}\n"; ai = prior.find(marker)
    at = ai + len(marker)
    arch.write_text(prior[:at] + "\n" + "".join(cut) + prior[at:], encoding="utf-8")
    return len(cut)


# ----------------------------------------------------------------- session ---
def session(root: Path, sub: str) -> int:
    if sub == "start":
        ensure_safe_git(root)  # self-heal safe git defaults each session
        compact(root)  # fold any pending fragments before the AI reads the log
        print(f"session started {core.now_stamp()} — context loaded from {root}")
        return 0
    if sub == "end":
        # Write a conflict-free FRAGMENT (not a direct append to the shared log), then
        # fold it. Disjoint files → no cross-device/session merge conflicts.
        sid = f"{core.today()}-{core.now_stamp().split()[1].replace(':', '')}"
        frag_dir = root / "context" / "sessions"
        frag_dir.mkdir(parents=True, exist_ok=True)
        frag = frag_dir / f"{sid}.md"
        frag.write_text(
            f"### {core.today()} — session\n\n"
            f"SessionID: {sid}\n"
            f"--- SESSION BLOCK ---\n"
            f"Date: {core.today()}\n"
            f"Stamp: {core.now_stamp()}\n"
            f"Summary: (your AI fills this in)\n"
            f"--- END BLOCK ---\n",
            encoding="utf-8",
        )
        compact(root)
        print(f"✓ session recorded as a fragment and folded into context/session-log.md")
        return 0
    if sub == "reconcile":
        print("note: reconcile merges Session Blocks from concurrent machines — "
              "not yet implemented (see SPEC). No changes made.")
        return 0
    raise SystemExit("error: session expects start|end|reconcile")


# -------------------------------------------------------------------- sync ---
def sync(root: Path) -> int:
    """Safe multi-device sync. Never rebases over a live editing session (a dirty
    tree defers, work stays local); integrates a moved remote by rebasing (the
    session log union-merges); retries the push. Non-lossy + idempotent."""
    ensure_safe_git(root)  # self-heal the safe defaults before touching the remote
    if not core.has_remote(root):
        print("note: no git remote configured — nothing to sync yet.")
        print("      run `wsx remote` for free hosting options (GitHub/GitLab/Codeberg),")
        print("      then `wsx remote <url>` to wire it.")
        return 0

    # Guard: never pull --rebase over uncommitted changes (autostash is off, so git
    # would refuse anyway — this is the friendly, explicit version).
    dirty = core.git(root, "status", "--porcelain", check=False, capture=True).stdout.strip()
    if dirty:
        print("⚠ uncommitted changes present — not pulling (won't rebase over live work).")
        print("  commit first (your AI does this at session end), then `wsx sync` again.")
        return 0

    print("syncing via git…")
    for _ in range(3):
        push = core.git(root, "push", check=False, capture=True)
        if push.returncode == 0:
            print("✓ synced (push)")
            return 0
        err = ((push.stderr or "") + (push.stdout or "")).lower()
        if not any(s in err for s in ("non-fast-forward", "fetch first", "rejected", "behind")):
            print(push.stderr.strip() or "✗ push failed")
            return 1
        # Remote moved — rebase our commits on top (autostash off; tree is clean).
        pull = core.git(root, "pull", "--rebase", check=False, capture=True)
        if pull.returncode != 0:
            core.git(root, "rebase", "--abort", check=False)
            print("✗ remote moved and the rebase hit a conflict in a structured file.")
            print("  your commits are safe locally. Ask your AI to `/reconcile`, then `wsx sync`.")
            return 1
    print("⚠ push still racing after retries; your commits are safe locally — try `wsx sync` again.")
    return 1


# ------------------------------------------------------------------ remote ---
_HOSTING = """where should this workspace live? (it's a git repo — pick a home so it
syncs across your machines and is backed up). Recommended, all free:

  • GitHub — a **private** repo (github.com/new → set Private). Most common; free
      private repos. Best if you already have an account.
  • GitLab (gitlab.com) — free private repos too; a good GitHub alternative.
  • Codeberg (codeberg.org) — free, community-run, no-tracking; nice for personal.
  • Local-only — no host at all; it just lives on this machine (you can add a
      remote later). Fine for a purely personal, single-machine setup.

Create an EMPTY repo (no README) on your chosen host, copy its URL, then run:
  wsx remote <url>        # e.g. wsx remote git@github.com:you/workspace.git
  wsx sync                # pushes your workspace up

Nothing is created for you — you own the account and the repo; wsx just wires it."""


def remote(root: Path, url: str = "") -> int:
    """Set (or show) the workspace's git remote, and record it in the profile.
    With no url, print the free-hosting recommendations."""
    if not url:
        if core.has_remote(root):
            r = core.git(root, "remote", "get-url", "origin", check=False, capture=True)
            print(f"remote 'origin' → {r.stdout.strip()}")
            print("change it with `wsx remote <url>`; push with `wsx sync`.")
        else:
            print(_HOSTING)
        return 0

    # add or update origin
    if core.has_remote(root):
        core.git(root, "remote", "set-url", "origin", url, check=False)
        verb = "updated"
    else:
        core.git(root, "remote", "add", "origin", url, check=False)
        verb = "set"

    # record intent in the profile so adapters/brain know where it lives
    prof = core.load_profile(root)
    prof.setdefault("transport", {})["type"] = "git"
    prof["transport"]["remote"] = url
    core.save_profile(root, prof)

    print(f"✓ remote 'origin' {verb} → {url}")
    print("  next: `wsx sync` to push your workspace up.")
    return 0


# resolve lives in resolver.py now (the mechanical half of the Resolver: fetch,
# pin, namespace, scaffold overlays, register). cli.cmd_resolve calls it directly.
