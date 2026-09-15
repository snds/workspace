#!/usr/bin/env python3
"""Per-surface routing trajectories — does each surface actually DELIVER the context?

`evaluate-skill-routing.py` proves a matcher routes correctly, but it carries its own
copy of the matcher, so it can be green while every real surface is wrong. This runs
each surface's **actual entry point** — the command the tool itself invokes — and asserts
what lands in the model's context.

The failure it exists to prevent, measured 2026-09-15: six of the 48 routing fixtures
delivered a different file set on Claude Code than on Cursor. Same vault, same utterance.
Cursor had no Layer-1 lexical fallback; the Claude hook deduped a knowledge hint away when
the same trigger had already produced a curated hit. Both surfaces were wrong, in opposite
directions, and nothing could see it because nothing ran both.

Surfaces:
  claude-code   .claude/hooks/dispatcher.py user-prompt   (stdin JSON, CLAUDE_PROJECT_DIR)
  cursor        09-tools/cursor-prompt-route.py           (beforeSubmitPrompt, stdin JSON)
  shell-agent   09-tools/skill-loadset.py --json          (any agent with a shell, no hook:
                                                           Gemini CLI, Warp, Aider, codex,
                                                           a generic MCP client)
  hookless      no executable path at all (ChatGPT / Grok / Perplexity web). Its trajectory
                is whatever the adapter FILE tells the model to do, so the adapters are
                asserted statically — see check_hookless_adapters().

Assertions per case: `expect_paths`, `forbid_paths`, `expect_header`, `expect_empty`, and
`parity` — the hook surfaces must deliver an identical set of workspace paths, because they
now run one matcher and any divergence means that unification regressed.

Usage:
  python3 09-tools/evaluate-surface-trajectories.py           # run corpus
  python3 09-tools/evaluate-surface-trajectories.py --check   # CI gate
  python3 09-tools/evaluate-surface-trajectories.py --utterance "…"   # ad-hoc, all surfaces
  python3 09-tools/evaluate-surface-trajectories.py --json
  python3 09-tools/evaluate-surface-trajectories.py --self-test

Exit: 0 pass · 1 a trajectory failed · 2 could not run.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
CORPUS = ROOT / "02-shared-references" / "surface-trajectory-cases.jsonl"
DISPATCHER = ROOT / ".claude" / "hooks" / "dispatcher.py"

# Workspace-relative path inside a delivered payload.
PATH_RE = re.compile(r"\b(?:0\d-[\w./-]+\.(?:md|py)|llms\.txt)")
# Surfaces that run the shared matcher and therefore MUST agree.
PARITY_SURFACES = ("claude-code", "cursor")

# Every hookless adapter must name the workspace entry points itself — that file is the
# only thing reaching the model when no hook exists.
HOOKLESS_ADAPTERS = [
    "PERPLEXITY.md",
    "GEMINI.md",
    "WARP.md",
    "CONVENTIONS.md",
    "00-bootstrap/adapters/web-session.md",
]
HOOKLESS_MUST_NAME = ["AGENTS.md"]


# ------------------------------------------------------------------ surface delivery

def _run(cmd: list[str], stdin: str = "") -> subprocess.CompletedProcess:
    env = dict(os.environ, CLAUDE_PROJECT_DIR=str(ROOT))
    return subprocess.run(
        cmd, input=stdin, capture_output=True, text=True, cwd=str(ROOT), env=env, timeout=60
    )


def deliver_claude_code(utterance: str) -> str:
    if not DISPATCHER.exists():
        return ""
    proc = _run([sys.executable, str(DISPATCHER), "user-prompt"],
                json.dumps({"prompt": utterance}))
    if not proc.stdout.strip():
        return ""
    try:
        return json.loads(proc.stdout).get("hookSpecificOutput", {}).get("additionalContext", "")
    except json.JSONDecodeError:
        return ""


def deliver_cursor(utterance: str) -> str:
    proc = _run([sys.executable, str(TOOLS / "cursor-prompt-route.py")],
                json.dumps({"prompt": utterance}))
    try:
        return (json.loads(proc.stdout or "{}") or {}).get("additional_context", "")
    except json.JSONDecodeError:
        return ""


def deliver_shell_agent(utterance: str) -> str:
    """The contract tells any shell-capable agent to run this. Its paths ARE the delivery."""
    proc = _run([sys.executable, str(TOOLS / "skill-loadset.py"), "--json", utterance])
    try:
        data = json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        return ""
    return "\n".join([*data.get("paths", []), data.get("close_out", "")])


SURFACES = {
    "claude-code": deliver_claude_code,
    "cursor": deliver_cursor,
    "shell-agent": deliver_shell_agent,
}


# ------------------------------------------------------------------------ assertions

def _paths(payload: str) -> set[str]:
    return set(PATH_RE.findall(payload))


def evaluate_case(case: dict) -> list[str]:
    wanted = case.get("surfaces") or list(PARITY_SURFACES)
    if wanted == "*":
        wanted = list(SURFACES)
    fails: list[str] = []
    delivered: dict[str, str] = {}

    for surface in wanted:
        fn = SURFACES.get(surface)
        if fn is None:
            fails.append(f"{case['id']}: unknown surface '{surface}'")
            continue
        payload = fn(case["utterance"])
        delivered[surface] = payload

        if case.get("expect_empty") and payload.strip():
            fails.append(f"{case['id']} [{surface}]: expected no injection, got {len(payload)} chars")
        for want in case.get("expect_paths", []):
            if want not in payload:
                fails.append(f"{case['id']} [{surface}]: missing {want}")
        for nope in case.get("forbid_paths", []):
            if nope in payload:
                fails.append(f"{case['id']} [{surface}]: delivered forbidden {nope}")
        header = case.get("expect_header")
        if header and not payload.startswith(header):
            got = payload.splitlines()[0] if payload.strip() else "(nothing)"
            fails.append(f"{case['id']} [{surface}]: header '{got}' != '{header}'")

    if case.get("parity"):
        pair = [s for s in PARITY_SURFACES if s in delivered]
        if len(pair) == len(PARITY_SURFACES):
            sets = {s: _paths(delivered[s]) for s in pair}
            base = sets[pair[0]]
            for other in pair[1:]:
                diff = base ^ sets[other]
                if diff:
                    fails.append(
                        f"{case['id']}: SURFACE DIVERGENCE {pair[0]} vs {other} — "
                        f"{sorted(diff)} (one matcher means one delivery)"
                    )
    return fails


def check_one_matcher() -> list[str]:
    """Structural guard: the Claude hook must delegate, not fork the matcher again.

    Parity fixtures catch drift only for utterances in the corpus. This catches the
    shape that produced the drift — a second implementation — for every utterance.
    """
    if not DISPATCHER.exists():
        return []
    text = DISPATCHER.read_text(encoding="utf-8", errors="replace")
    start = text.find("def handle_user_prompt")
    if start == -1:
        return ["dispatcher.py has no handle_user_prompt"]
    body = text[start:start + 3000]
    fails = []
    if "prompt_route" not in body:
        fails.append("dispatcher.handle_user_prompt does not delegate to prompt_route — "
                     "a second matcher is how the surfaces drifted apart (2026-09-15)")
    for forked in ("_registry_trigger_hits(", "TIER_CAPS["):
        if forked in body:
            fails.append(f"dispatcher.handle_user_prompt re-implements `{forked}` — "
                         f"the matcher lives in 09-tools/prompt_route.py")
    return fails


def check_hookless_adapters() -> list[str]:
    """A surface with no hook gets only what its adapter file says. Assert it says it."""
    fails = []
    for rel in HOOKLESS_ADAPTERS:
        path = ROOT / rel
        if not path.exists():
            fails.append(f"hookless adapter missing: {rel}")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for token in HOOKLESS_MUST_NAME:
            if token not in text:
                fails.append(f"{rel}: never names {token} — a hookless agent has no other way in")
    return fails


# ----------------------------------------------------------------------- self-test

def self_test() -> int:
    """Prove the assertions can fail. A trajectory suite that only passes proves nothing."""
    failures = []

    def expect(name, cond):
        if not cond:
            failures.append(name)

    expect("paths() extracts a skill path",
           _paths("load 03-skills/qa/SKILL.md now") == {"03-skills/qa/SKILL.md"})
    expect("paths() ignores prose", _paths("nothing pathlike here") == set())

    real = {"id": "t", "utterance": "figma component variants",
            "surfaces": ["cursor"], "expect_paths": ["03-skills/figma/SKILL.md"]}
    expect("a satisfied expectation passes", not evaluate_case(real))

    missing = dict(real, expect_paths=["03-skills/definitely-not-a-skill/SKILL.md"])
    expect("a missing path fails", evaluate_case(missing))

    forbidden = dict(real, expect_paths=[], forbid_paths=["03-skills/figma/SKILL.md"])
    expect("a forbidden path fails", evaluate_case(forbidden))

    wrong_header = dict(real, expect_paths=[], expect_header="# Definitely Not The Header")
    expect("a wrong header fails", evaluate_case(wrong_header))

    expect("expect_empty fails on a firing utterance",
           evaluate_case(dict(real, expect_paths=[], expect_empty=True)))

    expect("unknown surface is an error",
           evaluate_case({"id": "t", "utterance": "x", "surfaces": ["nope"]}))

    # Parity is the centerpiece, so prove it fails on a planted divergence rather than
    # trusting that today's surfaces happen to agree.
    saved = dict(SURFACES)
    try:
        SURFACES["claude-code"] = lambda _u: "load 03-skills/qa/SKILL.md"
        SURFACES["cursor"] = lambda _u: "load 03-skills/qa/SKILL.md"
        expect("parity passes when both surfaces deliver the same set",
               not evaluate_case({"id": "p", "utterance": "x", "parity": True}))
        SURFACES["cursor"] = lambda _u: "load 03-skills/qa/SKILL.md and 08-knowledge/design/extra.md"
        planted = evaluate_case({"id": "p", "utterance": "x", "parity": True})
        expect("parity fails on a planted divergence", planted)
        expect("the divergence message names the offending path",
               any("extra.md" in f for f in planted))
    finally:
        SURFACES.clear()
        SURFACES.update(saved)

    expect("one-matcher guard passes on the live dispatcher", not check_one_matcher())
    expect("hookless adapter check passes on the live adapters", not check_hookless_adapters())

    for name in failures:
        print(f"  ✗ {name}")
    if failures:
        print(f"FAIL surface-trajectories self-test — {len(failures)} assertion(s)")
        return 1
    print("OK surface-trajectories self-test")
    return 0


# ---------------------------------------------------------------------------- main

def load_corpus() -> list[dict]:
    if not CORPUS.exists():
        return []
    return [json.loads(line) for line in CORPUS.read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.lstrip().startswith("//")]


def show_utterance(utterance: str) -> None:
    for surface, fn in SURFACES.items():
        payload = fn(utterance)
        print(f"\n### {surface} — {len(_paths(payload))} path(s)")
        print(payload.strip() or "(no injection)")
    sets = {s: _paths(SURFACES[s](utterance)) for s in PARITY_SURFACES}
    diff = sets[PARITY_SURFACES[0]] ^ sets[PARITY_SURFACES[1]]
    print(f"\nparity({' vs '.join(PARITY_SURFACES)}): "
          + ("OK" if not diff else f"DIVERGENT {sorted(diff)}"))


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="CI gate: exit 1 on any failure")
    ap.add_argument("--json", action="store_true", help="machine-readable report")
    ap.add_argument("--utterance", help="show what every surface delivers for one utterance")
    ap.add_argument("--self-test", action="store_true", help="prove the assertions can fail")
    args = ap.parse_args()

    if args.self_test:
        return self_test()
    if args.utterance:
        show_utterance(args.utterance)
        return 0

    cases = load_corpus()
    if not cases:
        print(f"surface-trajectories: no corpus at {CORPUS.relative_to(ROOT)}", file=sys.stderr)
        return 2

    failures: list[str] = []
    for case in cases:
        failures.extend(evaluate_case(case))
    structural = check_one_matcher() + check_hookless_adapters()
    failures.extend(structural)

    if args.json:
        print(json.dumps({"cases": len(cases), "failures": failures}, indent=2))
    else:
        for f in failures:
            print(f"  ✗ {f}")
        surfaces = ", ".join(SURFACES)
        if failures:
            print(f"FAIL {len(failures)} trajectory failure(s) over {len(cases)} case(s) "
                  f"[{surfaces}] + hookless adapters")
        else:
            print(f"OK {len(cases)} trajectory case(s) across {surfaces} + hookless adapters; "
                  f"hook surfaces in parity")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
