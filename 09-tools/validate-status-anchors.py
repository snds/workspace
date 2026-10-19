#!/usr/bin/env python3
"""
validate-status-anchors.py — every line item on a status page can be linked to.

A status page is an HTML page whose wrapper carries `data-status-page="<published URL>"`
(02-shared-references/artifact-standards.md, "Status pages"). Sean's rule (2026-10-19,
04-preferences/user-preferences.md, "Linked references"): when an agent mentions a tracked
item, it links to that item on the status page with an anchor, in a link that opens on his
Macs, the Windows PC and his iPhone. This gate checks the page side of that rule:

  - the published URL is an https link (a claude.ai artifact or a GitHub page);
  - every list item and table row has an id (lines inside an item's <details> are exempt);
  - ids are unique and use only letters, digits, `.`, `_`, `~` and `-` (the artifact host
    passes nothing else through to the page);
  - each of those items holds a link to itself, so Sean can copy it;
  - every `href="#…"` lands on an id that exists;
  - the page handles `hashchange`, so a link that arrives after load still lands;
  - (warning) ids that were in the committed page and are gone now: links to them land at
    the top of the page. Rename an item's text, never its id.

Usage:
  python3 09-tools/validate-status-anchors.py              # every tracked status page
  python3 09-tools/validate-status-anchors.py <file.html>  # just these
  python3 09-tools/validate-status-anchors.py --self-test
Exit: 0 clean (warnings allowed) · 1 errors.
"""

from __future__ import annotations

import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ID_OK = re.compile(r"^[A-Za-z0-9._~-]+$")
URL_OK = re.compile(r"^https://(claude\.ai/(artifact|code/artifact)/|github\.com/)\S+$")
VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


class Page(HTMLParser):
    """Collects ids, self-links and the items that must carry them."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, str | None]] = []  # (tag, id)
        self.ids: list[str] = []
        self.hrefs: list[str] = []
        self.items: list[tuple[str, str | None, int]] = []  # (tag, id, line)
        self.self_links: set[str] = set()
        self.status_url: str | None = None
        self.in_script = False
        self.script = ""

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "data-status-page" in a:
            self.status_url = a["data-status-page"] or ""
        sid = a.get("id")
        if sid is not None:
            self.ids.append(sid)
        href = a.get("href") or ""
        if tag == "a" and href.startswith("#") and len(href) > 1:
            target = href[1:]
            self.hrefs.append(target)
            if any(i == target for _, i in self.stack):
                self.self_links.add(target)
        if self.status_url is not None:
            in_details = any(t == "details" for t, _ in self.stack)
            if not in_details and (tag == "li" or (tag == "tr" and any(t == "tbody" for t, _ in self.stack))):
                self.items.append((tag, sid, self.getpos()[0]))
        if tag == "script":
            self.in_script = True
        if tag not in VOID:
            self.stack.append((tag, sid))

    def handle_endtag(self, tag):
        if tag == "script":
            self.in_script = False
        for k in range(len(self.stack) - 1, -1, -1):
            if self.stack[k][0] == tag:
                del self.stack[k:]
                break

    def handle_data(self, data):
        if self.in_script:
            self.script += data


def parse(text: str) -> Page:
    p = Page()
    p.feed(text)
    p.close()
    return p


def check(text: str, committed: str | None = None) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    p = parse(text)
    if p.status_url is None:
        return ["not a status page: no data-status-page attribute"], []
    if not URL_OK.match(p.status_url):
        errors.append(f"data-status-page is {p.status_url!r}: use the published https link "
                      "(a claude.ai artifact or a GitHub page) so the copied links open on any device")
    seen: set[str] = set()
    for sid in p.ids:
        if not ID_OK.match(sid):
            errors.append(f"id {sid!r}: use only letters, digits, '.', '_', '~' and '-'")
        if sid in seen:
            errors.append(f"id {sid!r} is used twice")
        seen.add(sid)
    for tag, sid, line in p.items:
        if not sid:
            errors.append(f"line {line}: a <{tag}> line item has no id")
        elif sid not in p.self_links:
            errors.append(f"line {line}: item #{sid} has no link to itself (a # or its number)")
    for target in sorted(set(p.hrefs) - seen):
        errors.append(f"href '#{target}' lands on no id")
    if "hashchange" not in p.script:
        errors.append("no hashchange handler: a link that arrives after the page loads won't scroll or highlight")
    if committed is not None:
        before = parse(committed)
        if before.status_url is not None:
            gone = sorted(set(before.ids) - seen)
            if gone:
                warnings.append("ids in the committed page and gone now (links to them land at the top): "
                                + ", ".join(gone[:12]) + (" …" if len(gone) > 12 else ""))
    return errors, warnings


def tracked_status_pages() -> list[Path]:
    out = subprocess.run(["git", "ls-files", "*.html"], cwd=ROOT, capture_output=True, text=True)
    pages = []
    for rel in out.stdout.splitlines():
        path = ROOT / rel
        try:
            if "data-status-page" in path.read_text(encoding="utf-8", errors="replace"):
                pages.append(path)
        except OSError:
            continue
    return pages


def committed_text(path: Path) -> str | None:
    rel = path.resolve().relative_to(ROOT).as_posix()
    out = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=ROOT, capture_output=True, text=True)
    return out.stdout if out.returncode == 0 else None


GOOD = """<div class="wrap" data-status-page="https://claude.ai/artifact/abc">
<ul><li id="ask-one"><b>One <a class="pin" href="#ask-one">#</a></b>
  <details><ul><li>a sub-point needs no id</li></ul></details></li></ul>
<table><tbody><tr id="track-a"><td>A <a href="#track-a">#</a></td></tr></tbody></table>
<p><a href="#ask-one">see one</a></p></div>
<script>addEventListener("hashchange", () => {});</script>"""

BAD = """<div data-status-page="file:///Users/me/page.html">
<ul><li>no id</li><li id="x y"><a href="#x y">#</a></li><li id="dup"><a href="#dup">#</a></li>
<li id="dup">again</li><li id="lonely">no self link</li></ul><a href="#nowhere">?</a></div>"""


def self_test() -> int:
    fails = []
    e, w = check(GOOD)
    if e or w:
        fails.append(f"good page: {e + w}")
    e, w = check(BAD)
    want = ["data-status-page is", "has no id", "'x y'", "used twice", "#lonely has no link",
            "'#nowhere' lands", "no hashchange"]
    for needle in want:
        if not any(needle in m for m in e):
            fails.append(f"bad page: no error containing {needle!r} in {e}")
    _, w = check(GOOD.replace('"ask-one"', '"ask-two"').replace("#ask-one", "#ask-two"), committed=GOOD)
    if not any("ask-one" in m for m in w):
        fails.append(f"a removed id isn't warned about: {w}")
    if check("<p>plain</p>")[0] != ["not a status page: no data-status-page attribute"]:
        fails.append("a page without the attribute isn't recognized as not a status page")
    for f in fails:
        print(f"✗ {f}")
    print(f"validate-status-anchors self-test: {'FAIL' if fails else 'ok'} ({len(want) + 3} cases)")
    return 1 if fails else 0


def main(argv: list[str]) -> int:
    if "--self-test" in argv:
        return self_test()
    paths = [Path(a) for a in argv if not a.startswith("-")] or tracked_status_pages()
    errors = 0
    for path in paths:
        text = path.read_text(encoding="utf-8")
        e, w = check(text, committed_text(path))
        rel = path.resolve().relative_to(ROOT).as_posix() if path.resolve().is_relative_to(ROOT) else str(path)
        for m in e:
            print(f"  ✗ {rel}: {m}")
        for m in w:
            print(f"  ! {rel}: {m}")
        errors += len(e)
    n = len(paths)
    print(f"status anchors: {'FAIL' if errors else 'ok'} — {n} status page(s), {errors} error(s)")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
