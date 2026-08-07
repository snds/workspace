#!/usr/bin/env python3
"""
a11y_audit.py — structural accessibility audit with a runner-agnostic finding schema.

Usage:
    python3 scripts/a11y_audit.py --url https://example.com --config configs/default.yaml
    python3 scripts/a11y_audit.py --html-file ./dist/index.html --out ./a11y-out
    python3 scripts/a11y_audit.py --url https://example.com --runner pa11y --level aaa
    python3 scripts/a11y_audit.py --html-file page.html --runner manual --format json

What it does:
    1. Preflights the accessibility runners in preference order (axe-core CLI →
       pa11y → Lighthouse's accessibility category). A runner counts as present
       if its binary is on PATH or the package is already cached for
       `npx --no-install` — nothing is ever installed implicitly.
    2. Runs the first available runner and NORMALIZES its output into one schema:
       {id, severity, rule, selector, message, wcag} (+ source, help_url).
    3. If no runner is available (or --runner manual), emits the MANUAL_CHECKLIST
       — WCAG-oriented checks a human/agent must confirm by hand — plus, when the
       input is local HTML, stdlib static checks. Exits 2 to mark the run DEGRADED.

Exit codes:
    0  a runner ran; no findings at or above the configured fail_on severity
    1  a runner ran; findings at or above fail_on (the CI gate)
    2  DEGRADED — no runner available or --runner manual; results are a checklist
       plus heuristic static findings, not automated evidence
    3  usage / input error (missing file, unreadable config, unusable target)

Honest limits:
    - Automated rules find roughly 30-40% of real accessibility defects. Exit 0
      means "no machine-detectable violation," never "accessible."
    - The stdlib static checks parse the served HTML only. Anything a framework
      renders or mutates client-side is invisible to them; treat them as leads.
    - Severity is normalized into the /qa vocabulary (blocker/major/minor/nit),
      so a severity here is this toolkit's mapping, not the runner's own word.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
import urllib.request
from dataclasses import dataclass, field, asdict
from html.parser import HTMLParser
from pathlib import Path

SEVERITIES = ["blocker", "major", "minor", "nit"]
SEVERITY_RANK = {s: i for i, s in enumerate(SEVERITIES)}
LEVEL_ORDER = {"a": 0, "aa": 1, "aaa": 2}

DEFAULTS = {
    "level": "aa",
    "include_best_practices": True,
    "runner": {
        "prefer": ["axe", "pa11y", "lighthouse"],
        "timeout_seconds": 120,
        "npx_fallback": True,
        "extra_args": {"axe": [], "pa11y": [], "lighthouse": []},
    },
    "severity": {"fail_on": ["blocker", "major"]},
    "exclude": {"rules": [], "selectors": []},
    "degraded": {"static_checks": True, "fetch_url": False},
    "report": {"format": "markdown", "max_findings_per_rule": 5},
}


# ─── minimal YAML subset loader (stdlib-only) ─────────────────────────────────
# Handles exactly what the shipped configs use: comments, nested mappings by
# indent, `key: value` scalars, flow lists `[a, b]`, and block lists of scalars.
# It is not a general YAML parser; anything else raises so failures are loud.

def _scalar(raw: str):
    v = raw.strip()
    if len(v) >= 2 and v[0] in "\"'" and v[-1] == v[0]:
        return v[1:-1]
    low = v.lower()
    if low in ("true", "yes"):
        return True
    if low in ("false", "no"):
        return False
    if low in ("null", "~", ""):
        return None
    try:
        return int(v)
    except ValueError:
        pass
    try:
        return float(v)
    except ValueError:
        return v


def _flow_list(raw: str):
    inner = raw.strip()[1:-1].strip()
    return [_scalar(p) for p in inner.split(",") if p.strip()] if inner else []


def parse_yaml_subset(text: str) -> dict:
    root: dict = {}
    stack: list[tuple[int, dict]] = [(-1, root)]
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        raw = lines[i]
        i += 1
        stripped = raw.split("#", 1)[0].rstrip() if not raw.lstrip().startswith("#") else ""
        if not stripped.strip():
            continue
        indent = len(stripped) - len(stripped.lstrip())
        body = stripped.strip()
        if body.startswith("- "):
            raise ValueError(f"unexpected list item at top level: {body!r}")
        if ":" not in body:
            raise ValueError(f"cannot parse config line: {body!r}")
        key, _, rest = body.partition(":")
        key, rest = key.strip(), rest.strip()
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if rest.startswith("[") and rest.endswith("]"):
            parent[key] = _flow_list(rest)
            continue
        if rest == "":
            # block list or nested mapping — peek at the next content line
            j = i
            while j < len(lines) and not lines[j].split("#", 1)[0].strip():
                j += 1
            if j < len(lines) and lines[j].split("#", 1)[0].strip().startswith("- "):
                items = []
                while j < len(lines):
                    peek = lines[j].split("#", 1)[0]
                    if not peek.strip():
                        j += 1
                        continue
                    p_indent = len(peek) - len(peek.lstrip())
                    if p_indent <= indent or not peek.strip().startswith("- "):
                        break
                    items.append(_scalar(peek.strip()[2:]))
                    j += 1
                parent[key] = items
                i = j
            else:
                child: dict = {}
                parent[key] = child
                stack.append((indent, child))
            continue
        parent[key] = _scalar(rest)
    return root


def deep_merge(base: dict, override: dict) -> dict:
    out = dict(base)
    for k, v in (override or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = deep_merge(out[k], v)
        elif v is not None:
            out[k] = v
    return out


def load_config(path: str | None) -> dict:
    if not path:
        return json.loads(json.dumps(DEFAULTS))
    p = Path(path).expanduser()
    if not p.is_file():
        raise FileNotFoundError(f"config not found: {p}")
    return deep_merge(DEFAULTS, parse_yaml_subset(p.read_text(encoding="utf-8")))


# ─── finding schema ──────────────────────────────────────────────────────────

@dataclass
class Finding:
    """The one shape every runner is normalized into."""
    id: str                       # stable per-finding id: <rule>#<n>
    severity: str                 # blocker | major | minor | nit
    rule: str                     # runner rule identifier
    selector: str                 # CSS selector (or a locator hint)
    message: str                  # what is wrong, in one line
    wcag: list[str] = field(default_factory=list)   # e.g. ["1.4.3", "4.1.2"]
    source: str = ""              # axe | pa11y | lighthouse | static-html
    help_url: str = ""


def wcag_from_axe_tags(tags: list[str]) -> list[str]:
    """axe tags carry criteria as wcag143 / wcag2aa / wcag21aa — extract criteria."""
    out = []
    for t in tags or []:
        if t.startswith("wcag") and t[4:].isdigit() and len(t) >= 7:
            digits = t[4:]
            out.append(f"{digits[0]}.{digits[1]}.{digits[2:]}")
    return sorted(set(out))


def wcag_from_pa11y_code(code: str) -> list[str]:
    """pa11y codes look like WCAG2AA.Principle1.Guideline1_4.1_4_3.G18.Fail."""
    for part in (code or "").split("."):
        bits = part.split("_")
        if len(bits) == 3 and all(b.isdigit() for b in bits):
            return [".".join(bits)]
    return []


# ─── runner preflight ────────────────────────────────────────────────────────

RUNNER_PACKAGES = {"axe": "@axe-core/cli", "pa11y": "pa11y", "lighthouse": "lighthouse"}


def probe(argv: list[str], timeout: int) -> bool:
    try:
        r = subprocess.run(argv + ["--version"], capture_output=True, text=True, timeout=timeout)
        return r.returncode == 0
    except (OSError, subprocess.SubprocessError):
        return False


def resolve_runner(name: str, npx_fallback: bool, timeout: int = 30) -> list[str] | None:
    """Return the argv prefix for a runner, or None if it isn't available here."""
    if shutil.which(name):
        return [name]
    if npx_fallback and shutil.which("npx"):
        argv = ["npx", "--no-install", RUNNER_PACKAGES[name]]
        if probe(argv, timeout):
            return argv
    return None


def available_runners(cfg: dict) -> dict[str, list[str]]:
    rcfg = cfg["runner"]
    found = {}
    for name in rcfg["prefer"]:
        if name not in RUNNER_PACKAGES:
            continue
        argv = resolve_runner(name, bool(rcfg.get("npx_fallback", True)))
        if argv:
            found[name] = argv
    return found


# ─── runner invocation + normalization ───────────────────────────────────────

def axe_tags(level: str, best_practices: bool) -> list[str]:
    tags = ["wcag2a", "wcag21a"]
    if LEVEL_ORDER[level] >= 1:
        tags += ["wcag2aa", "wcag21aa", "wcag22aa"]
    if LEVEL_ORDER[level] >= 2:
        tags += ["wcag2aaa", "wcag21aaa"]
    if best_practices:
        tags.append("best-practice")
    return tags


def run_process(argv: list[str], timeout: int) -> tuple[int, str, str]:
    r = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout, r.stderr


AXE_IMPACT = {"critical": "blocker", "serious": "major", "moderate": "minor", "minor": "nit"}


def run_axe(argv: list[str], target: str, cfg: dict) -> list[Finding]:
    tags = ",".join(axe_tags(cfg["level"], bool(cfg["include_best_practices"])))
    timeout = int(cfg["runner"]["timeout_seconds"])
    cmd = argv + [target, "--stdout", "--tags", tags]
    cmd += [str(a) for a in (cfg["runner"].get("extra_args", {}).get("axe") or [])]
    code, out, err = run_process(cmd, timeout)
    if not out.strip():
        raise RuntimeError(f"axe produced no output (exit {code}): {err.strip()[:400]}")
    payload = json.loads(out)
    pages = payload if isinstance(payload, list) else [payload]
    findings: list[Finding] = []
    for page in pages:
        for v in page.get("violations", []):
            sev = AXE_IMPACT.get(v.get("impact") or "", "minor")
            wcag = wcag_from_axe_tags(v.get("tags", []))
            for n, node in enumerate(v.get("nodes", []) or [{}], start=1):
                target_sel = node.get("target") or []
                findings.append(Finding(
                    id=f"{v.get('id', 'axe-rule')}#{n}",
                    severity=sev,
                    rule=v.get("id", "axe-rule"),
                    selector=" ".join(target_sel) if isinstance(target_sel, list) else str(target_sel),
                    message=(v.get("help") or v.get("description") or "").strip(),
                    wcag=wcag,
                    source="axe",
                    help_url=v.get("helpUrl", ""),
                ))
    return findings


PA11Y_STANDARD = {"a": "WCAG2A", "aa": "WCAG2AA", "aaa": "WCAG2AAA"}
PA11Y_TYPE = {"error": "major", "warning": "minor", "notice": "nit"}


def run_pa11y(argv: list[str], target: str, cfg: dict) -> list[Finding]:
    timeout = int(cfg["runner"]["timeout_seconds"])
    cmd = argv + [target, "--reporter", "json",
                  "--standard", PA11Y_STANDARD[cfg["level"]],
                  "--timeout", str(timeout * 1000)]
    if cfg["include_best_practices"]:
        cmd += ["--include-warnings", "--include-notices"]
    cmd += [str(a) for a in (cfg["runner"].get("extra_args", {}).get("pa11y") or [])]
    code, out, err = run_process(cmd, timeout + 30)
    if not out.strip():
        raise RuntimeError(f"pa11y produced no output (exit {code}): {err.strip()[:400]}")
    issues = json.loads(out)
    findings: list[Finding] = []
    seen: dict[str, int] = {}
    for issue in issues:
        rule = issue.get("code", "pa11y-issue")
        seen[rule] = seen.get(rule, 0) + 1
        findings.append(Finding(
            id=f"{rule}#{seen[rule]}",
            severity=PA11Y_TYPE.get(issue.get("type", "error"), "major"),
            rule=rule,
            selector=issue.get("selector", ""),
            message=(issue.get("message") or "").strip(),
            wcag=wcag_from_pa11y_code(rule),
            source="pa11y",
        ))
    return findings


def run_lighthouse(argv: list[str], target: str, cfg: dict) -> list[Finding]:
    timeout = int(cfg["runner"]["timeout_seconds"])
    cmd = argv + [target, "--output=json", "--output-path=stdout", "--quiet",
                  "--only-categories=accessibility",
                  '--chrome-flags=--headless=new --no-sandbox']
    cmd += [str(a) for a in (cfg["runner"].get("extra_args", {}).get("lighthouse") or [])]
    code, out, err = run_process(cmd, timeout + 60)
    start = out.find("{")
    if start < 0:
        raise RuntimeError(f"lighthouse produced no JSON (exit {code}): {err.strip()[:400]}")
    report = json.loads(out[start:])
    audits = report.get("audits", {})
    refs = {r["id"]: r for r in report.get("categories", {})
            .get("accessibility", {}).get("auditRefs", []) if "id" in r}
    findings: list[Finding] = []
    for aid, audit in audits.items():
        score = audit.get("score")
        mode = audit.get("scoreDisplayMode")
        if mode in ("notApplicable", "informative") or score is None or score >= 1:
            continue
        weight = (refs.get(aid) or {}).get("weight", 0)
        sev = "blocker" if (score == 0 and weight >= 7) else ("major" if score == 0 else "minor")
        items = ((audit.get("details") or {}).get("items") or [])
        selectors = []
        for it in items:
            node = it.get("node") or {}
            if node.get("selector"):
                selectors.append(node["selector"])
        if not selectors:
            selectors = [""]
        for n, sel in enumerate(selectors, start=1):
            findings.append(Finding(
                id=f"{aid}#{n}",
                severity=sev,
                rule=aid,
                selector=sel,
                message=(audit.get("title") or "").strip(),
                wcag=[],
                source="lighthouse",
                help_url=f"https://web.dev/{aid}/",
            ))
    return findings


RUNNER_FUNCS = {"axe": run_axe, "pa11y": run_pa11y, "lighthouse": run_lighthouse}


# ─── degraded path: stdlib static HTML checks ────────────────────────────────

VOID_INPUTS = {"input", "select", "textarea"}
SKIP_INPUT_TYPES = {"hidden", "submit", "button", "reset", "image"}


class StaticChecker(HTMLParser):
    """Heuristic structural checks over served HTML. Leads, not verdicts."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.findings: list[Finding] = []
        self.ids: dict[str, int] = {}
        self.headings: list[int] = []
        self.label_depth = 0
        self.label_for: set[str] = set()
        self.unlabelled: list[tuple[str, str]] = []   # (selector, kind)
        self.open_interactive: list[dict] = []        # a/button awaiting text
        self.saw_html = False
        self.saw_main = False
        self.tables: list[str] = []
        self.table_stack: list[dict] = []
        self.hidden_stack: list[str] = []   # open tags that hide their subtree from AT
        self._counter = 0

    def _add(self, rule: str, severity: str, selector: str, message: str, wcag: list[str]):
        self._counter += 1
        self.findings.append(Finding(
            id=f"{rule}#{self._counter}", severity=severity, rule=rule,
            selector=selector, message=message, wcag=wcag, source="static-html",
        ))

    @staticmethod
    def _sel(tag: str, attrs: dict) -> str:
        sel = tag
        if attrs.get("id"):
            sel += f"#{attrs['id']}"
        elif attrs.get("class"):
            sel += "." + ".".join(attrs["class"].split()[:2])
        elif attrs.get("name"):
            sel += f"[name={attrs['name']}]"
        return sel

    def handle_starttag(self, tag, attrlist):
        attrs = {k.lower(): (v or "") for k, v in attrlist}
        sel = self._sel(tag, attrs)

        # Text inside an aria-hidden subtree contributes no accessible name.
        if attrs.get("aria-hidden", "").lower() == "true":
            self.hidden_stack.append(tag)

        if attrs.get("id"):
            self.ids[attrs["id"]] = self.ids.get(attrs["id"], 0) + 1

        if tag == "html":
            self.saw_html = True
            if not attrs.get("lang", "").strip():
                self._add("html-has-lang", "major", "html",
                          "<html> has no lang attribute, so assistive tech cannot pick a "
                          "pronunciation/voice for the page.", ["3.1.1"])
        if tag == "main":
            self.saw_main = True

        if tag == "meta" and attrs.get("name", "").lower() == "viewport":
            content = attrs.get("content", "").replace(" ", "").lower()
            blocked = "user-scalable=no" in content
            for part in content.split(","):
                if part.startswith("maximum-scale="):
                    try:
                        blocked = blocked or float(part.split("=", 1)[1]) < 2
                    except ValueError:
                        pass
            if blocked:
                self._add("meta-viewport", "major", "meta[name=viewport]",
                          "Viewport blocks or caps zoom (user-scalable=no / maximum-scale < 2), "
                          "which breaks magnification for low-vision users.", ["1.4.4"])

        if tag == "img":
            role = attrs.get("role", "").lower()
            if attrs.get("alt", "").strip() and not self.hidden_stack:
                for el in self.open_interactive:   # alt text names its ancestor link/button
                    el["text"] += attrs["alt"]
            if "alt" not in attrs and role not in ("presentation", "none"):
                self._add("image-alt", "major", sel,
                          "<img> has no alt attribute — screen readers fall back to the file name.",
                          ["1.1.1"])

        if tag == "iframe" and not (attrs.get("title") or attrs.get("aria-label")):
            self._add("frame-title", "major", sel,
                      "<iframe> has no title, so its purpose is unannounced in the frame list.",
                      ["4.1.2", "2.4.1"])

        if tag == "label":
            self.label_depth += 1
            if attrs.get("for"):
                self.label_for.add(attrs["for"])

        if tag in VOID_INPUTS:
            itype = attrs.get("type", "text").lower()
            if not (tag == "input" and itype in SKIP_INPUT_TYPES):
                labelled = bool(attrs.get("aria-label") or attrs.get("aria-labelledby")
                                or attrs.get("title")) or self.label_depth > 0
                if not labelled:
                    self.unlabelled.append((sel, attrs.get("id", "")))

        if tag in ("a", "button"):
            named = bool(attrs.get("aria-label") or attrs.get("aria-labelledby") or attrs.get("title"))
            self.open_interactive.append({"tag": tag, "sel": sel, "named": named, "text": ""})
            if tag == "a" and not attrs.get("href", "").strip() and "role" not in attrs:
                self._add("link-no-href", "minor", sel,
                          "<a> has no usable href (missing or empty), so it is not keyboard "
                          "focusable or announced as a link; use <button> for actions.",
                          ["4.1.2", "2.1.1"])

        if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
            self.headings.append(int(tag[1]))

        if tag == "table":
            self.table_stack.append({"sel": sel, "th": False, "caption": False})
        if tag == "th" and self.table_stack:
            self.table_stack[-1]["th"] = True
        if tag == "caption" and self.table_stack:
            self.table_stack[-1]["caption"] = True

        tabindex = attrs.get("tabindex", "")
        if tabindex.lstrip("+").isdigit() and int(tabindex) > 0:
            self._add("tabindex", "minor", sel,
                      f"Positive tabindex ({tabindex}) forces a focus order that diverges from "
                      "the DOM/visual order.", ["2.4.3"])

    def handle_endtag(self, tag):
        if self.hidden_stack and self.hidden_stack[-1] == tag:
            self.hidden_stack.pop()
        if tag == "label" and self.label_depth:
            self.label_depth -= 1
        if tag in ("a", "button"):
            for idx in range(len(self.open_interactive) - 1, -1, -1):
                if self.open_interactive[idx]["tag"] == tag:
                    el = self.open_interactive.pop(idx)
                    if not el["named"] and not el["text"].strip():
                        self._add(f"{tag}-name", "blocker", el["sel"],
                                  f"<{tag}> has no accessible name (no text, aria-label, or titled "
                                  "child) — it is announced as an unlabelled control.",
                                  ["4.1.2", "2.4.4"] if tag == "a" else ["4.1.2"])
                    break
        if tag == "table" and self.table_stack:
            t = self.table_stack.pop()
            if not t["th"]:
                self._add("th-has-data-cells", "minor", t["sel"],
                          "<table> has no <th> — if this is a data table, rows/columns have no "
                          "programmatic headers.", ["1.3.1"])

    def handle_data(self, data):
        if self.hidden_stack:
            return
        for el in self.open_interactive:
            el["text"] += data

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag in ("a", "button", "label", "table"):
            self.handle_endtag(tag)
        elif self.hidden_stack and self.hidden_stack[-1] == tag:
            self.hidden_stack.pop()

    def finish(self) -> list[Finding]:
        for sel, ident in self.unlabelled:
            if ident and ident in self.label_for:
                continue
            self._add("form-field-label", "blocker", sel,
                      "Form control has no associated label (no <label for>, wrapping <label>, "
                      "aria-label, or aria-labelledby).", ["1.3.1", "3.3.2", "4.1.2"])
        for ident, count in self.ids.items():
            if count > 1:
                self._add("duplicate-id", "minor", f"#{ident}",
                          f"id `{ident}` appears {count} times — label/ARIA references resolve to "
                          "the first match only.", ["4.1.1"])
        if self.headings:
            if 1 not in self.headings:
                self._add("page-has-heading-one", "minor", "body",
                          "No <h1> — the page has no top-level heading to orient heading navigation.",
                          ["1.3.1", "2.4.6"])
            prev = None
            for lvl in self.headings:
                if prev is not None and lvl > prev + 1:
                    self._add("heading-order", "minor", f"h{lvl}",
                              f"Heading level jumps h{prev} → h{lvl}, implying a section that "
                              "does not exist.", ["1.3.1"])
                prev = lvl
        if self.saw_html and not self.saw_main:
            self._add("landmark-one-main", "nit", "body",
                      "No <main> landmark — screen-reader users lose the 'skip to content' shortcut.",
                      ["1.3.1", "2.4.1"])
        return self.findings


def static_findings(html: str) -> list[Finding]:
    checker = StaticChecker()
    checker.feed(html)
    checker.close()
    return checker.finish()


# ─── degraded path: the manual checklist ─────────────────────────────────────

MANUAL_CHECKLIST = [
    {"id": "MC-01", "level": "a", "wcag": ["1.1.1"], "area": "text alternatives",
     "check": "Every informative image has alt text that conveys its purpose in context; decorative images are alt=\"\" or aria-hidden.",
     "how": "Read each alt aloud in place of the image — does the sentence still work?"},
    {"id": "MC-02", "level": "a", "wcag": ["1.3.1"], "area": "structure",
     "check": "Headings, lists, and tables are real semantic elements and the heading outline matches the visible hierarchy.",
     "how": "Walk the heading outline; a skipped or styling-only heading is a failure."},
    {"id": "MC-03", "level": "a", "wcag": ["1.3.2"], "area": "structure",
     "check": "DOM order matches the meaningful reading order (no CSS-reordered content that reads out of sequence).",
     "how": "Disable CSS and read the page top to bottom."},
    {"id": "MC-04", "level": "a", "wcag": ["2.1.1", "2.1.2"], "area": "keyboard",
     "check": "Every control is reachable and operable by keyboard alone, and focus can always leave (no traps).",
     "how": "Tab through the whole page and back with Shift+Tab; operate each control with Enter/Space/arrows."},
    {"id": "MC-05", "level": "a", "wcag": ["2.4.3"], "area": "keyboard",
     "check": "Focus order follows the visual order, including inside dialogs, menus, and after content changes.",
     "how": "Tab slowly and watch the focus ring travel; note any jump backwards or off-screen."},
    {"id": "MC-06", "level": "aa", "wcag": ["2.4.7", "2.4.11"], "area": "keyboard",
     "check": "The focus indicator is always visible, ≥ 3:1 against adjacent colors, and not clipped by overflow.",
     "how": "Check the indicator on every component type, including on dark surfaces and in the DS's own components."},
    {"id": "MC-07", "level": "a", "wcag": ["4.1.2"], "area": "names + roles",
     "check": "Every control exposes a correct accessible name and role, and its state (expanded/selected/checked/invalid) updates programmatically.",
     "how": "Inspect the accessibility tree for each control; the name should match its visible label."},
    {"id": "MC-08", "level": "a", "wcag": ["4.1.3", "3.3.1"], "area": "feedback",
     "check": "Async results, validation errors, and toasts are announced (live region or focus move) and errors identify the field and the fix.",
     "how": "Submit an invalid form with a screen reader running; confirm the error is spoken and reachable."},
    {"id": "MC-09", "level": "a", "wcag": ["3.2.1", "3.2.2"], "area": "predictability",
     "check": "Focus or input alone never triggers navigation, reordering, or an unannounced context change.",
     "how": "Tab into every select, tab, and combobox without activating it."},
    {"id": "MC-10", "level": "aa", "wcag": ["1.4.3", "1.4.11"], "area": "contrast",
     "check": "Text meets 4.5:1 (3:1 for large text) and meaningful non-text (borders, icons, chart series, focus rings) meets 3:1.",
     "how": "Measure with visual-qa-toolkit `qa_contrast` rather than eyeballing; include hover/disabled/dark-theme states."},
    {"id": "MC-11", "level": "a", "wcag": ["1.4.1"], "area": "color independence",
     "check": "No status, selection, required-field, or chart series is distinguished by color alone.",
     "how": "Measure with visual-qa-toolkit `qa_color_vision`; confirm an icon, label, pattern, or shape carries the same meaning."},
    {"id": "MC-12", "level": "aa", "wcag": ["1.4.10", "1.4.12"], "area": "reflow + spacing",
     "check": "Content reflows at a 320 CSS-px width with no 2-D scrolling, and survives the 1.4.12 text-spacing overrides without clipping.",
     "how": "Zoom to 400% at 1280px, then apply the WCAG text-spacing bookmarklet values."},
    {"id": "MC-13", "level": "aa", "wcag": ["2.5.8", "2.5.5"], "area": "targets",
     "check": "Interactive targets are ≥ 24×24 CSS px (44×44 on touch-primary surfaces) with adequate spacing.",
     "how": "Measure icon buttons, table row actions, close buttons, and dense inline links."},
    {"id": "MC-14", "level": "a", "wcag": ["2.3.1", "2.3.3"], "area": "motion",
     "check": "Nothing flashes more than 3×/second; large-region motion honors prefers-reduced-motion, and autoplay can be stopped.",
     "how": "Set the OS reduce-motion preference and re-run the interaction; see visual-qa-motion for the judgment lens."},
    {"id": "MC-15", "level": "aa", "wcag": ["1.2.2", "1.2.5"], "area": "media",
     "check": "Prerecorded video has accurate captions and audio description where visual information is not narrated.",
     "how": "Watch muted with captions only; then listen with the screen off."},
    {"id": "MC-16", "level": "aa", "wcag": ["3.3.3", "3.3.4"], "area": "forms",
     "check": "Errors are recoverable, destructive/legal/financial submissions are reversible or confirmed, and labels persist (no placeholder-as-label).",
     "how": "Fill the form incorrectly, then correct it without losing entered data."},
    {"id": "MC-17", "level": "aa", "wcag": ["2.4.1", "2.4.5"], "area": "navigation",
     "check": "A skip link or landmark structure allows bypassing repeated blocks, and more than one way exists to find a page.",
     "how": "Tab once from page load — the first stop should be a working skip link."},
    {"id": "MC-18", "level": "aaa", "wcag": ["1.4.6", "2.4.9", "3.1.5"], "area": "beyond AA",
     "check": "AAA targets where committed: 7:1 text contrast, link purpose from link text alone, lower-secondary reading level.",
     "how": "Only assert AAA when the project has declared it; otherwise record as an enhancement."},
    {"id": "MC-19", "level": "aa", "wcag": [], "area": "assistive-tech pass",
     "check": "One real AT pass per platform target (NVDA or JAWS on Windows, VoiceOver on macOS/iOS, TalkBack on Android) completing the primary task.",
     "how": "Task-based, not element-by-element: can the AT user finish the job? No automated rule substitutes for this."},
    {"id": "MC-20", "level": "aa", "wcag": [], "area": "zoom + OS settings",
     "check": "Works at 200% browser zoom, with OS large text, in forced-colors/high-contrast mode, and in dark theme.",
     "how": "Toggle each setting and re-run the primary task; forced-colors commonly erases custom focus rings and icon-only buttons."},
]


def checklist_for_level(level: str) -> list[dict]:
    cap = LEVEL_ORDER[level]
    return [c for c in MANUAL_CHECKLIST if LEVEL_ORDER[c["level"]] <= cap]


# ─── filtering + reporting ───────────────────────────────────────────────────

def apply_excludes(findings: list[Finding], cfg: dict) -> list[Finding]:
    rules = {str(r) for r in (cfg["exclude"].get("rules") or [])}
    selectors = [str(s) for s in (cfg["exclude"].get("selectors") or [])]
    kept = []
    for f in findings:
        if f.rule in rules:
            continue
        if any(s and s in f.selector for s in selectors):
            continue
        kept.append(f)
    return kept


def cap_per_rule(findings: list[Finding], limit: int) -> tuple[list[Finding], int]:
    if limit <= 0:
        return findings, 0
    seen: dict[str, int] = {}
    kept, dropped = [], 0
    for f in sorted(findings, key=lambda x: (SEVERITY_RANK.get(x.severity, 9), x.rule, x.selector)):
        seen[f.rule] = seen.get(f.rule, 0) + 1
        if seen[f.rule] <= limit:
            kept.append(f)
        else:
            dropped += 1
    return kept, dropped


def counts_by_severity(findings: list[Finding]) -> dict[str, int]:
    out = {s: 0 for s in SEVERITIES}
    for f in findings:
        out[f.severity] = out.get(f.severity, 0) + 1
    return out


def build_payload(target: str, mode: str, runner: str, cfg: dict,
                  findings: list[Finding], notes: list[str], dropped: int) -> dict:
    counts = counts_by_severity(findings)
    fail_on = [s for s in (cfg["severity"].get("fail_on") or []) if s in SEVERITY_RANK]
    gate = sum(counts.get(s, 0) for s in fail_on)
    payload = {
        "schema": "a11y-audit-toolkit/1.0",
        "target": target,
        "mode": mode,                       # measured | degraded
        "runner": runner,                   # axe | pa11y | lighthouse | manual
        "level": cfg["level"],
        "include_best_practices": bool(cfg["include_best_practices"]),
        "fail_on": fail_on,
        "counts": counts,
        "gating_findings": gate,
        "truncated_findings": dropped,
        "findings": [asdict(f) for f in findings],
        "notes": notes,
    }
    if mode == "degraded":
        payload["MANUAL_CHECKLIST"] = checklist_for_level(cfg["level"])
    return payload


def render_markdown(p: dict) -> str:
    method = (f"{p['runner']} (automated rules)" if p["mode"] == "measured"
              else "MANUAL_CHECKLIST + stdlib static HTML checks (no runner available)")
    lines = [
        f"## QA Report — {p['target']} · audit · lens:a11y · level:{p['level']}",
        f"Standard: WCAG 2.2 {p['level'].upper()}"
        + (" + best-practice rules" if p["include_best_practices"] else ""),
        f"Method:   {method}",
        "",
        "### Findings  (severity: blocker | major | minor | nit)",
    ]
    if not p["findings"]:
        lines.append("- none reported by this method")
    for f in p["findings"]:
        wcag = f" · WCAG {', '.join(f['wcag'])}" if f["wcag"] else ""
        sel = f["selector"] or "(no selector)"
        lines.append(f"- [{f['severity']}] {f['rule']} — {f['message']}")
        lines.append(f"  Evidence: `{sel}`{wcag} · source: {f['source']}")
    c = p["counts"]
    lines += [
        "",
        "### Summary",
        f"blocker {c['blocker']} · major {c['major']} · minor {c['minor']} · nit {c['nit']}"
        + (f"  ·  truncated: {p['truncated_findings']}" if p["truncated_findings"] else ""),
        f"Mode: {p['mode']}  ·  Gating severities: {', '.join(p['fail_on']) or 'none'}"
        f"  ·  Gating findings: {p['gating_findings']}",
    ]
    if p["notes"]:
        lines += ["", "Notes:"] + [f"- {n}" for n in p["notes"]]
    if p["mode"] == "degraded":
        lines += ["", "### MANUAL_CHECKLIST",
                  "No runner was available, so nothing above is automated evidence. Confirm each "
                  "item by hand and record the result; then re-run once a runner is installed."]
        for c_item in p["MANUAL_CHECKLIST"]:
            wcag = f" (WCAG {', '.join(c_item['wcag'])})" if c_item["wcag"] else ""
            lines.append(f"- [ ] **{c_item['id']}** · {c_item['area']}{wcag} — {c_item['check']}")
            lines.append(f"      How: {c_item['how']}")
    lines += ["", "### Next",
              "Automated rules cover roughly 30-40% of real defects. Route confirmed structural "
              "findings to `fe-accessibility` for implementation, contrast/color findings to "
              "`visual-qa-toolkit`, and judgment calls to `visual-qa-accessibility`."]
    return "\n".join(lines) + "\n"


# ─── main ────────────────────────────────────────────────────────────────────

def fetch_html(url: str, timeout: int) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "a11y-audit-toolkit/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:   # noqa: S310 - explicit opt-in flag
        charset = resp.headers.get_content_charset() or "utf-8"
        return resp.read().decode(charset, errors="replace")


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Structural accessibility audit; normalizes axe/pa11y/Lighthouse output, "
                    "degrades to a WCAG manual checklist.")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--url", help="URL to audit (runner drives a headless browser)")
    src.add_argument("--html-file", help="local HTML file to audit")
    ap.add_argument("--config", help="YAML config (see configs/default.yaml)")
    ap.add_argument("--runner", default="auto",
                    choices=["auto", "axe", "pa11y", "lighthouse", "manual"],
                    help="force a runner; `manual` skips detection and emits the checklist")
    ap.add_argument("--level", choices=["a", "aa", "aaa"], help="WCAG conformance target")
    ap.add_argument("--format", choices=["markdown", "json"], help="stdout format")
    ap.add_argument("--out", help="directory for a11y_report.md + a11y_report.json")
    ap.add_argument("--fetch-url", action="store_true",
                    help="in degraded mode, fetch --url over HTTP for static checks (pre-JS HTML only)")
    args = ap.parse_args()

    try:
        cfg = load_config(args.config)
    except (OSError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 3
    if args.level:
        cfg["level"] = args.level
    if args.format:
        cfg["report"]["format"] = args.format
    if args.fetch_url:
        cfg["degraded"]["fetch_url"] = True
    if cfg["level"] not in LEVEL_ORDER:
        print(f"error: level must be one of {sorted(LEVEL_ORDER)}", file=sys.stderr)
        return 3

    notes: list[str] = []
    if args.html_file:
        path = Path(args.html_file).expanduser().resolve()
        if not path.is_file():
            print(f"error: no such HTML file: {path}", file=sys.stderr)
            return 3
        target = path.as_uri()
        label = str(path)
        local_html = path.read_text(encoding="utf-8", errors="replace")
    else:
        target = label = args.url
        local_html = None

    # ── runner selection
    runners: dict[str, list[str]] = {}
    if args.runner != "manual":
        runners = available_runners(cfg)
        if args.runner != "auto":
            runners = {args.runner: runners[args.runner]} if args.runner in runners else {}

    findings: list[Finding] = []
    used = "manual"
    for name, argv in runners.items():
        try:
            findings = RUNNER_FUNCS[name](argv, target, cfg)
            used = name
            notes.append(f"Ran `{' '.join(argv)}` against {label}.")
            break
        except (OSError, ValueError, RuntimeError, subprocess.SubprocessError) as exc:
            notes.append(f"Runner `{name}` failed ({type(exc).__name__}: {exc}); falling through.")

    mode = "measured" if used != "manual" else "degraded"

    if mode == "degraded":
        if args.runner == "manual":
            head = "DEGRADED by request (--runner manual) — nothing below is automated evidence."
        elif runners:
            head = "DEGRADED: every available runner failed (see the failure notes below)."
        elif args.runner != "auto":
            head = (f"DEGRADED: requested runner `{args.runner}` is not installed here — "
                    f"install it with `npm i -g {RUNNER_PACKAGES[args.runner]}`.")
        else:
            head = ("DEGRADED: no accessibility runner available — install one with "
                    "`npm i -g @axe-core/cli` (preferred), `npm i -g pa11y`, or "
                    "`npm i -g lighthouse`.")
        notes.insert(0, head)
        if cfg["degraded"].get("static_checks", True):
            html = local_html
            if html is None and cfg["degraded"].get("fetch_url"):
                try:
                    html = fetch_html(target, int(cfg["runner"]["timeout_seconds"]))
                    notes.append("Fetched the URL over HTTP for static checks (pre-JavaScript HTML only).")
                except OSError as exc:
                    notes.append(f"Could not fetch {target} for static checks ({exc}).")
            if html is not None:
                findings = static_findings(html)
                notes.append("Static findings are heuristic and cover the served HTML only — "
                             "client-rendered content is not represented.")
            else:
                notes.append("No HTML available for static checks (pass --html-file, or --fetch-url "
                             "to retrieve the URL).")

    findings = apply_excludes(findings, cfg)
    findings, dropped = cap_per_rule(findings, int(cfg["report"].get("max_findings_per_rule", 5)))

    payload = build_payload(label, mode, used, cfg, findings, notes, dropped)
    markdown = render_markdown(payload)

    if args.out:
        out_dir = Path(args.out).expanduser()
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "a11y_report.json").write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        (out_dir / "a11y_report.md").write_text(markdown, encoding="utf-8")

    if cfg["report"].get("format") == "json":
        print(json.dumps(payload, indent=2, ensure_ascii=False))
    else:
        print(markdown, end="")

    if mode == "degraded":
        return 2
    return 1 if payload["gating_findings"] else 0


if __name__ == "__main__":
    sys.exit(main())
