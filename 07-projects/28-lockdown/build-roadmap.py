#!/usr/bin/env python3
"""
build-roadmap.py — Lockdown's status page, generated from the repo's own records.

Writes 07-projects/28-lockdown/roadmap.html from the snds/lockdown checkout:
  - docs/plan/feature-status.json  the v1 checklist (one line per feature, id = feature id)
  - docs/plan/decisions.md         every decision whose status says "flagged for Sean" or
                                   "audit item" (one line per decision, id = d<number>)
  - README.md                      the build-slice table (one line per slice, id = slice-<n>)
plus the asks and next steps kept in ASKS and NEXT below.

Every line item has a permanent id and a link to itself, as the status-page standard asks
(02-shared-references/artifact-standards.md, "Status pages"; checked by
09-tools/validate-status-anchors.py). Ids never change: rename an item's words, not its id.

Usage:
  python3 07-projects/28-lockdown/build-roadmap.py [--repo <lockdown checkout>]
The checkout defaults to $LOCKDOWN_REPO, then ~/Projects/lockdown.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import subprocess
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE / "roadmap.html"
PAGE_URL = "https://claude.ai/artifact/662Gqj3VZUFpjSnvsfgEqp"
DASHBOARD = "https://claude.ai/artifact/9gVWpq3tPqx83JZDjBtk4a"
GH = "https://github.com/snds/lockdown"

# What only Sean can do. Each keeps its id for good; mark it done instead of deleting it.
ASKS = [
    {
        "id": "ask-review-flagged",
        "title": "Say yes, no or change to the decisions marked “Needs your yes”",
        "line": "{flagged} decisions change something you would see or use. Silence means accepted.",
        "more": [
            ("What it is", "Each one is a choice a builder made that you would notice: a default, a new switch, a "
             "wording, a limit. The reason it was flagged is under each line in "
             "<a href=\"#decisions\">Decisions</a>."),
            ("Why it matters", "They are all built and merged. A no means a change, and changes get harder once "
             "people use the app."),
            ("What you do", "Read the list. Reply with the number and yes, no or what to change, for example "
             "“D307: off by default”. Anything you don't mention stays as built."),
        ],
    },
    {
        "id": "ask-family-pricing",
        "title": "Decide family-plan pricing",
        "line": "The household vault and organizer are built; plans and billing wait on the price.",
        "more": [
            ("What it is", "The <a href=\"#family-plan\">family plan</a> row: who pays, how much, and how many "
             "people a plan covers."),
            ("What you do", "Give a price and a seat count, or say there is no paid plan in v1. Either unblocks "
             "the row."),
        ],
    },
    {
        "id": "ask-signing-certificates",
        "title": "Get signing certificates for macOS and Windows",
        "line": "Releases are unsigned until these exist; the signing steps are written and wait for them.",
        "more": [
            ("What it is", "An Apple Developer ID (part of the Apple Developer Program, $99 a year) for signing "
             "and notarising the Mac app, and a Windows code-signing certificate or Microsoft's signing service."),
            ("Why it matters", "Unsigned apps show warnings on install, and the app and browser connector fall "
             "back to the path-and-hash check instead of the code-signature check "
             "(<a href=\"#ipc-peer-auth\">peer authentication</a>)."),
            ("What you do", "Enrol, then add the certificates as repository secrets. The secret names are in "
             "<a href=\"" + GH + "/blob/main/docs/plan/24-release.md\">docs/plan/24-release.md</a>."),
        ],
    },
    {
        "id": "ask-store-accounts",
        "title": "Open the browser-store accounts",
        "line": "The extension's store packages are built; submitting them needs your accounts.",
        "more": [
            ("What it is", "A Chrome Web Store developer account ($5, once), a Firefox Add-ons account and a "
             "Microsoft Edge Add-ons account (both free)."),
            ("What you do", "Open the accounts. Claude prepares the listings; you press submit. This is the last "
             "part of <a href=\"#extension-coverage\">extension coverage</a> apart from Safari."),
        ],
    },
    {
        "id": "ask-first-release",
        "title": "Tag the first release when you're ready",
        "line": "A v* tag builds every package and a draft release that you publish by hand.",
        "more": [
            ("What it is", "The release workflow runs only on a tag. It makes the packages, SBOMs, checksums and "
             "build provenance, and leaves a draft on GitHub (<a href=\"#signed-releases\">signed releases</a>)."),
            ("What you do", "Say when. It works best after the signing certificates and an outside review."),
        ],
    },
    {
        "id": "ask-outside-review",
        "title": "Commission an outside security review",
        "line": "{audit} decisions are marked audit items: security choices a reviewer should check before release.",
        "more": [
            ("What it is", "An independent review of the cryptography and protocols, chiefly the post-quantum "
             "signatures, Lockdown's own age and TLS code, and the peer checks. The audit items are listed in "
             "<a href=\"#decisions\">Decisions</a>; the formal model is the "
             "<a href=\"#malicious-server-resistance\">malicious-server resistance</a> row."),
            ("What it costs", "Money and a few weeks of a reviewer's time; quotes vary by firm."),
            ("What you do", "Choose a reviewer or say to wait. Claude prepares the scope from the audit items."),
        ],
    },
    {
        "id": "ask-identity-crate",
        "title": "Allow work in the shared identity crate",
        "line": "Two gaps live in snds/ecosystem-identity, which Mailbird and Synapse also use.",
        "more": [
            ("What it is", "A Windows variant of the crate's peer type (<a href=\"#ipc-peer-auth\">peer "
             "authentication</a>) and locking its own key types out of swap (<a href=\"#memory-hygiene\">memory "
             "hygiene</a>)."),
            ("Why it's yours", "A change there ships to all three apps, so it needs your go-ahead."),
            ("What you do", "Say yes and Claude opens a PR in that repo with the change and its tests."),
        ],
    },
    {
        "id": "ask-remove-bins",
        "title": "Remove an empty folder on the cloud machine",
        "line": "A builder made /bins by mistake; the safety check stopped the agent from removing it.",
        "more": [
            ("What you do", "If that cloud session is still open, run <code>rmdir /bins</code>. If it has been "
             "reclaimed, there is nothing to do."),
        ],
    },
]

# What Claude can build without Sean, if he wants it.
NEXT = [
    {"id": "next-pq-status-line", "title": "A post-quantum status line in Security",
     "line": "Shows whether this account's vaults are signed with both keys yet (D346, flagged)."},
    {"id": "next-shared-vault-pq", "title": "Post-quantum signatures on shared vaults",
     "line": "Shared vaults and single-item shares still sign with Ed25519 only (D343)."},
    {"id": "next-cxf-file-bytes", "title": "File contents through CXF, once CXP is final",
     "line": "Waits on the exchange protocol leaving draft; Lockdown backups already carry files."},
]

STATUS = {
    "done": ("done", "Done"),
    "partial": ("part", "Partial"),
    "not-started": ("open", "Not started"),
    "n/a-yet": ("na", "Not code"),
}
SURF = {"core": "Core", "desktop": "Desktop", "cli": "CLI", "extension": "Extension", "web": "Web vault",
        "server": "Server"}


def esc(s: str) -> str:
    return html.escape(s, quote=True)


def md(s: str) -> str:
    """Just enough Markdown for decision and slice text: code, bold, links."""
    parts = re.split(r"(`[^`]*`)", s)
    out = []
    for p in parts:
        if p.startswith("`") and p.endswith("`") and len(p) > 1:
            out.append("<code>" + esc(p[1:-1]) + "</code>")
            continue
        t = esc(p)
        t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)

        def link(m: re.Match) -> str:
            text, href = m.group(1), html.unescape(m.group(2))
            if not href.startswith("http"):
                href = f"{GH}/blob/main/{href.lstrip('./')}"
            return f'<a href="{esc(href)}">{text}</a>'

        t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, t)
        out.append(t)
    return "".join(out)


def pin(id_: str, label: str) -> str:
    return f'<a class="pin" href="#{id_}" aria-label="Copy a link to {esc(label)}">#</a>'


def flag_reason(status: str) -> str:
    """Why a decision was flagged, as its status gives it: "(…)" after the flag, or the clause before it."""
    paren = re.search(r"flagged for Sean\*{0,2}\s*\(([^()]*(?:\([^()]*\)[^()]*)*)\)", status, re.I)
    after = re.search(r"flagged for Sean\*{0,2}\s*:\s*(.+)$", status, re.I)
    if paren:
        why = paren.group(1)
    elif after:
        why = after.group(1)
    else:
        before = re.split(r":?\s*\*{0,2}flagged for Sean", status, flags=re.I)[0]
        why = before.split(";")[-1].strip(" :")
        if re.fullmatch(r"(proposed|accepted by default under d38|audit item)", why, re.I):
            why = ""
    why = why.strip()
    return why[:1].upper() + why[1:] if why else ""


def decisions(repo: Path) -> list[dict]:
    rows = []
    for line in (repo / "docs/plan/decisions.md").read_text().splitlines():
        m = re.match(r"^\| (D(\d+)) \|", line)
        if not m:
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        status = cells[-1]
        low = status.lower()
        flagged, audit = "flagged" in low, "audit" in low
        if not (flagged or audit):
            continue
        text = next((c for c in cells[1:-1] if c.startswith("**")), cells[-2])
        head = re.match(r"\*\*(.+?)\*\*\s*(.*)", text)
        title, rest = (head.group(1), head.group(2)) if head else (text, "")
        rows.append({"id": m.group(1).lower(), "num": m.group(1), "title": title, "rest": rest,
                     "status": status, "why": flag_reason(status) if flagged else "",
                     "flagged": flagged, "audit": audit})
    return rows


def slices(repo: Path) -> list[dict]:
    out = []
    for line in (repo / "README.md").read_text().splitlines():
        m = re.match(r"^\| \*\*(\d+) · (.+?)\*\* ✅ \| (.+) \|$", line)
        if m:
            out.append({"id": f"slice-{m.group(1)}", "n": m.group(1), "name": m.group(2), "text": m.group(3)})
    return out


def build(repo: Path) -> str:
    fs = json.loads((repo / "docs/plan/feature-status.json").read_text())
    feats = fs["features"]
    counts = Counter(f["status"] for f in feats)
    total = len(feats)
    decs = decisions(repo)
    sl = slices(repo)
    n_flag = sum(d["flagged"] for d in decs)
    n_audit = sum(d["audit"] for d in decs)
    n_dec = sum(1 for l in (repo / "docs/plan/decisions.md").read_text().splitlines() if re.match(r"^\| D\d+ ", l))
    head = subprocess.run(["git", "-C", str(repo), "log", "-1", "--format=%h %cs"], capture_output=True,
                          text=True).stdout.split()
    sha, day = (head + ["", ""])[:2]

    def stat(n: int, label: str, small: str = "") -> str:
        sm = f" <small>{small}</small>" if small else ""
        return f'<div class="stat"><b>{n}{sm}</b><span>{label}</span></div>'

    bar = "".join(
        f'<i style="width:{100 * counts[k] / total:.2f}%;background:var(--{v[0]})" title="{v[1]}: {counts[k]}"></i>'
        for k, v in STATUS.items())

    o = []
    o.append(f'<div class="wrap" data-status-page="{PAGE_URL}">')
    o.append("<header>")
    o.append("<h1>Lockdown Roadmap</h1>")
    o.append(f'<p class="answer"><strong>{counts["done"]} of {total} v1 features are done</strong> for desktop '
             f'and web, across {len(sl)} build slices and {n_dec} decisions. No release yet. What is left mostly '
             f'needs you: <a href="#asks">{len(ASKS)} things only you can do</a>, starting with '
             f'<a href="#ask-review-flagged">{n_flag} decisions waiting on your yes</a>.</p>')
    o.append('<div class="stats">' + stat(counts["done"], "Done", f"/ {total}") + stat(counts["partial"], "Partial")
             + stat(counts["not-started"], "Not started") + stat(counts["n/a-yet"], "Not code (audits, a licence call)")
             + "</div>")
    o.append(f'<div class="bar" role="img" aria-label="{counts["done"]} done, {counts["partial"]} partial, '
             f'{counts["not-started"]} not started, {counts["n/a-yet"]} not code">{bar}</div>')
    o.append('<div class="legend">' + "".join(
        f'<span><i class="dot" style="background:var(--{v[0]})"></i>{v[1]} {counts[k]}</span>'
        for k, v in STATUS.items()) + "</div>")
    o.append(f'<p class="lede">Native mobile apps and OS-level integration (system autofill, passkey '
             f'providers) are deferred by decision D122, so most not-started lines are those. The charts live on '
             f'the <a href="{DASHBOARD}">v1 status dashboard</a>.</p>')
    o.append("</header>")

    # Asks
    o.append('<section id="asks"><h2>Waiting on you</h2><ul class="asks">')
    for a in ASKS:
        line = a["line"].format(flagged=n_flag, audit=n_audit)
        more = "".join(f"<p><b>{esc(k)}.</b> {v}</p>" for k, v in a["more"])
        o.append(f'<li id="{a["id"]}"><span class="kind">You</span><b>{esc(a["title"])} {pin(a["id"], a["title"])}</b>'
                 f'<span>{esc(line)}</span><details class="more"><summary>What this means</summary>'
                 f'<div class="more-body">{more}</div></details></li>')
    o.append("</ul></section>")

    # Next
    o.append('<section id="next"><h2>Claude can build next</h2><p class="lede">Say the word and these start; '
             'none needs anything from you.</p><ul class="asks claude">')
    for n in NEXT:
        o.append(f'<li id="{n["id"]}"><span class="kind">Claude</span><b>{esc(n["title"])} {pin(n["id"], n["title"])}</b>'
                 f'<span>{esc(n["line"])}</span></li>')
    o.append("</ul></section>")

    # Features
    o.append('<section id="features"><h2>The v1 checklist</h2><p class="lede">Every feature committed to v1, '
             'with where it works today and what is left. A line is done only when it is complete for desktop and '
             'web; deferred mobile and OS-level parts are named in its note.</p>')
    cats: dict[str, list] = {}
    for f in feats:
        cats.setdefault(f["category"], []).append(f)
    for cat, items in cats.items():
        c = Counter(f["status"] for f in items)
        o.append(f'<div class="card"><h3>{esc(cat)} <span class="count">{c["done"]} of {len(items)} done</span></h3>'
                 '<ul class="steps">')
        for f in items:
            cls, label = STATUS[f["status"]]
            where = ", ".join(SURF.get(s, s) for s in f["surfaces"]) or "Nowhere yet"
            tags = f'<span class="chip">{esc(where)}</span>'
            if f.get("deferred"):
                tags += f' <span class="chip quiet">Deferred: {"mobile" if f["deferred"] == "mobile" else "OS-level"}</span>'
            o.append(f'<li id="{f["id"]}"><span class="mark {cls}" aria-hidden="true"></span>'
                     f'<span><b>{esc(f["name"])}</b> {pin(f["id"], f["name"])}'
                     f'<span class="note">{esc(f["left"])}</span><span class="tags">{tags}</span></span>'
                     f'<span class="who {cls}">{label}</span></li>')
        o.append("</ul></div>")
    o.append("</section>")

    # Decisions
    o.append(f'<section id="decisions"><h2>Decisions</h2><p class="lede">The {n_flag} marked '
             f'<span class="tag you">Needs your yes</span> change something you would see; silence means accepted. '
             f'The {n_audit} marked <span class="tag audit">Audit item</span> are security choices for an outside '
             f'reviewer. The full log is <a href="{GH}/blob/main/docs/plan/decisions.md">decisions.md</a>.</p>'
             '<div class="card"><ul class="steps decisions">')
    for d in decs:
        tags = ""
        if d["flagged"]:
            tags += '<span class="tag you">Needs your yes</span>'
        if d["audit"]:
            tags += '<span class="tag audit">Audit item</span>'
        why = f'<p><b>Why it was flagged.</b> {md(d["why"])}</p>' if d["why"] else ""
        rest = f"<p>{md(d['rest'])}</p>" if d["rest"] else ""
        o.append(f'<li id="{d["id"]}"><span class="num">{d["num"]}</span>'
                 f'<span><b>{md(d["title"])}</b> {pin(d["id"], d["num"])}<span class="tags">{tags}</span>'
                 f'<details class="more"><summary>What this means</summary><div class="more-body">{why}{rest}'
                 f'<p class="note">Status: {md(d["status"])}</p></div></details></span></li>')
    o.append("</ul></div></section>")

    # Slices
    o.append('<section id="slices"><h2>Built so far</h2><div class="card"><ul class="steps">')
    for s in sl:
        o.append(f'<li id="{s["id"]}"><span class="num">{s["n"]}</span><span><b>{esc(s["name"])}</b> '
                 f'{pin(s["id"], "slice " + s["n"])}<span class="note">{md(s["text"])}</span></span>'
                 f'<span class="who done">Done</span></li>')
    o.append("</ul></div></section>")

    o.append(f'<footer><span>Built from snds/lockdown at <code>{esc(sha)}</code> ({esc(day)}): '
             'docs/plan/feature-status.json, docs/plan/decisions.md and the README\'s slice table, by '
             '07-projects/28-lockdown/build-roadmap.py in the workspace.</span>'
             '<span>Every line has its own link: tap its # to copy it. The link opens this page at that line, on a '
             'Mac, the Windows PC or a phone.</span></footer>')
    o.append("</div>")
    o.append('<div class="toast" role="status" aria-live="polite" hidden></div>')
    return HEAD + "\n".join(o) + SCRIPT


HEAD = """<title>Lockdown Roadmap</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap">
<style>
/* Layout: one reading column. The answer and the numbers, what waits on Sean, what Claude can build next,
   the v1 checklist by category, the decisions that need a yes or an audit, then the slices built.
   Same family as the Synapse and Mailbird roadmaps, with Lockdown's green-teal accent. */
:root {
  --bg: oklch(0.985 0.003 175);
  --surface: oklch(1 0 0);
  --fg: oklch(0.2 0.012 190);
  --muted: oklch(0.49 0.014 190);
  --line: oklch(0.91 0.007 180);
  --accent: oklch(0.5 0.1 175);
  --done: oklch(0.53 0.13 155);
  --part: oklch(0.62 0.14 70);
  --open: oklch(0.6 0.012 190);
  --na: oklch(0.7 0.02 280);
  --audit: oklch(0.52 0.12 290);
  --chip: oklch(0.955 0.007 180);
  --font-body: "IBM Plex Sans", system-ui, -apple-system, "Segoe UI", sans-serif;
  --font-mono: "IBM Plex Mono", ui-monospace, "SF Mono", Menlo, monospace;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: oklch(0.17 0.009 190); --surface: oklch(0.21 0.01 190); --fg: oklch(0.95 0.004 180); --muted: oklch(0.71 0.012 180);
    --line: oklch(0.31 0.011 190); --accent: oklch(0.76 0.1 175);
    --done: oklch(0.75 0.13 155); --part: oklch(0.8 0.13 75); --open: oklch(0.6 0.01 190); --na: oklch(0.68 0.04 280);
    --audit: oklch(0.76 0.1 290); --chip: oklch(0.26 0.011 190);
    color-scheme: dark;
  }
}
:root[data-theme="dark"] {
  --bg: oklch(0.17 0.009 190); --surface: oklch(0.21 0.01 190); --fg: oklch(0.95 0.004 180); --muted: oklch(0.71 0.012 180);
  --line: oklch(0.31 0.011 190); --accent: oklch(0.76 0.1 175);
  --done: oklch(0.75 0.13 155); --part: oklch(0.8 0.13 75); --open: oklch(0.6 0.01 190); --na: oklch(0.68 0.04 280);
  --audit: oklch(0.76 0.1 290); --chip: oklch(0.26 0.011 190);
  color-scheme: dark;
}
* { box-sizing: border-box; }
body { background: var(--bg); color: var(--fg); font: 15px/1.55 var(--font-body); }
.wrap { max-width: 54rem; margin: 0 auto; padding-block: 40px 64px; padding-left: max(16px, env(safe-area-inset-left, 0px)); padding-right: max(16px, env(safe-area-inset-right, 0px)); display: flex; flex-direction: column; gap: 40px; }
h1, h2, h3 { text-wrap: balance; margin: 0; }
h1 { font-size: 2rem; font-weight: 700; letter-spacing: -0.02em; }
h2 { font-size: 1.25rem; font-weight: 600; }
h3 { font-size: 0.8rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: var(--muted); display: flex; justify-content: space-between; gap: 12px; }
h3 .count { letter-spacing: 0; text-transform: none; font-weight: 500; font-family: var(--font-mono); }
p { margin: 0; }
code, .mono { font-family: var(--font-mono); font-variant-numeric: tabular-nums; }
code { font-size: 0.85em; background: var(--chip); padding: 1px 5px; border-radius: 4px; overflow-wrap: anywhere; }
.lede { color: var(--muted); max-width: 64ch; }
header { display: flex; flex-direction: column; gap: 12px; }
.answer { font-size: 1.125rem; max-width: 64ch; }
.answer strong { font-weight: 600; }
.stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(9.5rem, 1fr)); gap: 1px; background: var(--line); border: 1px solid var(--line); border-radius: 10px; overflow: hidden; }
.stat { background: var(--surface); padding: 14px 16px; display: flex; flex-direction: column; gap: 2px; }
.stat b { font: 600 1.6rem/1.1 var(--font-mono); font-variant-numeric: tabular-nums; }
.stat b small { font-size: 1rem; color: var(--muted); font-weight: 500; }
.stat span { color: var(--muted); font-size: 0.85rem; }
.bar { display: flex; height: 8px; border-radius: 4px; overflow: hidden; background: var(--chip); }
.bar i { display: block; }
.legend { display: flex; flex-wrap: wrap; gap: 16px; font-size: 0.85rem; color: var(--muted); }
.legend span { display: inline-flex; align-items: center; gap: 6px; }
.dot { width: 10px; height: 10px; border-radius: 50%; flex: none; display: inline-block; }
section { display: flex; flex-direction: column; gap: 14px; }
.card { background: var(--surface); border: 1px solid var(--line); border-radius: 10px; padding: 4px 14px; }
.card h3 { padding: 10px 0 2px; }
ul.steps { list-style: none; margin: 0; padding: 0; }
ul.steps li { display: grid; grid-template-columns: 18px minmax(0, 1fr) auto; gap: 10px; align-items: baseline; padding: 8px 0; border-bottom: 1px solid var(--line); font-size: 0.92rem; }
ul.steps li:last-child { border-bottom: 0; }
ul.steps li > span { min-width: 0; }
ul.steps.decisions li, #slices ul.steps li { grid-template-columns: 3.2rem minmax(0, 1fr) auto; }
ul.steps.decisions li { grid-template-columns: 3.2rem minmax(0, 1fr); }
.num { font: 600 0.78rem var(--font-mono); color: var(--muted); }
.mark { width: 14px; height: 14px; border-radius: 4px; display: inline-grid; place-items: center; transform: translateY(2px); }
.mark.done { background: var(--done); }
.mark.part { background: linear-gradient(90deg, var(--part) 50%, transparent 50%); border: 1.5px solid var(--part); }
.mark.open { border: 1.5px solid var(--open); }
.mark.na { border: 1.5px dashed var(--na); }
.who { font: 400 0.75rem var(--font-mono); color: var(--muted); white-space: nowrap; }
.who.done { color: var(--done); }
.who.part { color: var(--part); }
.note { display: block; color: var(--muted); font-size: 0.85rem; }
.tags { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 4px; }
.chip { font: 500 0.72rem var(--font-mono); padding: 1px 8px; border-radius: 999px; background: var(--chip); color: var(--fg); }
.chip.quiet { color: var(--muted); }
.tag { font: 500 0.72rem var(--font-mono); padding: 1px 8px; border-radius: 999px; white-space: nowrap; border: 1px solid currentColor; }
.tag.you { color: var(--part); }
.tag.audit { color: var(--audit); }
ul.asks { list-style: none; margin: 0; padding: 0; display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 24rem), 1fr)); gap: 10px; align-items: start; }
ul.asks li { display: flex; flex-direction: column; gap: 3px; padding: 12px 14px; border-left: 3px solid var(--part); background: var(--surface); border-radius: 0 8px 8px 0; min-width: 0; }
ul.asks li b { font-weight: 600; }
ul.asks li > span { color: var(--muted); font-size: 0.9rem; }
ul.asks li .kind { font: 500 0.72rem var(--font-mono); letter-spacing: 0.04em; text-transform: uppercase; color: var(--part); }
ul.asks.claude li { border-left-color: var(--accent); }
ul.asks.claude li .kind { color: var(--accent); }
footer { color: var(--muted); font-size: 0.85rem; border-top: 1px solid var(--line); padding-top: 16px; display: flex; flex-direction: column; gap: 4px; }

/* Every line item has a permanent id. Its # copies a link to it; arriving on #id scrolls to the item,
   highlights it and opens its details. */
[id] { scroll-margin-block: 24px; }
a { color: var(--accent); }
:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; border-radius: 4px; }
.pin { font: 500 0.8rem var(--font-mono); color: var(--muted); text-decoration: none; padding: 0 3px; opacity: 0.75; }
.pin:hover, .pin:focus-visible { color: var(--accent); opacity: 1; }
.is-target { outline: 2px solid var(--accent); outline-offset: 2px; background: color-mix(in oklch, var(--accent) 9%, var(--surface)); border-radius: 8px; }
ul.steps li.is-target { outline-offset: -1px; padding-inline: 6px; }
@media (prefers-reduced-motion: no-preference) { .is-target { transition: background-color 0.4s; } }
details.more { margin-top: 4px; }
details.more summary { cursor: pointer; color: var(--accent); font-size: 0.85rem; width: fit-content; }
.more-body { display: flex; flex-direction: column; gap: 8px; padding-top: 8px; font-size: 0.9rem; max-width: 64ch; color: var(--fg); }
.more-body b { font-weight: 600; }
.toast { position: fixed; left: 50%; transform: translateX(-50%); bottom: calc(16px + env(safe-area-inset-bottom, 0px)); max-width: calc(100% - 32px); background: var(--fg); color: var(--bg); padding: 8px 14px; border-radius: 8px; font-size: 0.85rem; overflow-wrap: anywhere; user-select: text; z-index: 10; }
@media (max-width: 30rem) {
  ul.steps li { grid-template-columns: 18px minmax(0, 1fr); }
  ul.steps li .who { grid-column: 2; }
  ul.steps.decisions li, #slices ul.steps li { grid-template-columns: 2.6rem minmax(0, 1fr); }
}
</style>
"""

SCRIPT = """
<script>
(() => {
  const page = document.querySelector("[data-status-page]")?.dataset.statusPage || "";
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const toast = document.querySelector(".toast");
  let timer;
  const say = (text, ms) => {
    toast.textContent = text; toast.hidden = false;
    clearTimeout(timer); timer = setTimeout(() => { toast.hidden = true; }, ms);
  };
  const show = (id, smooth) => {
    const el = id && document.getElementById(id);
    if (!el) return;
    document.querySelectorAll(".is-target").forEach(e => e.classList.remove("is-target"));
    el.classList.add("is-target");
    el.querySelectorAll("details").forEach(d => { d.open = true; });
    el.scrollIntoView({ block: "center", behavior: smooth && !reduce ? "smooth" : "auto" });
    if (!el.hasAttribute("tabindex")) el.setAttribute("tabindex", "-1");
    el.focus({ preventScroll: true });
  };
  const fromHash = smooth => show(decodeURIComponent(location.hash.slice(1)), smooth);
  addEventListener("hashchange", () => fromHash(true));
  fromHash(false);
  // Web fonts can move things after the first scroll; settle on the item again.
  document.fonts?.ready.then(() => fromHash(false));
  document.addEventListener("click", async e => {
    const a = e.target.closest("a.pin");
    if (!a) return;
    e.preventDefault();
    const id = a.getAttribute("href").slice(1);
    show(id, true);
    try { history.replaceState(null, "", "#" + id); } catch (_) {}
    const link = page + "#" + id;
    try { await navigator.clipboard.writeText(link); say("Link copied: " + link, 2500); }
    catch (_) { say("Copy this link: " + link, 8000); }
  });
})();
</script>
"""


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=os.environ.get("LOCKDOWN_REPO", str(Path.home() / "Projects/lockdown")))
    args = ap.parse_args()
    OUT.write_text(build(Path(args.repo)))
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
