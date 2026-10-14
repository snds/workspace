#!/usr/bin/env python3
"""Render the Synapse plan set (plan/*.md) into one self-contained HTML page.

Usage: python3 build-plan-html.py <plan_dir> <out_html>

Stdlib only. Supports the markdown subset the plan uses: headings, paragraphs,
nested lists, task boxes, pipe tables, fenced code, mermaid fences, horizontal
rules, inline code, bold, italics and links. Links between plan files become
in-page anchors. Edit the markdown and re-run; never edit the HTML by hand.
"""
import html
import os
import re
import sys
from pathlib import Path

ORDER = [
    # (path relative to plan/, nav label, section number, nav group)
    ("00-big-picture.md", "Big picture", "00", "Plan"),
    ("01-workspace-model.md", "Workspace model", "01", "Plan"),
    ("02-architecture.md", "Architecture", "02", "Plan"),
    ("03-app-experience.md", "App experience", "03", "Plan"),
    ("04-generator-and-importer.md", "Create and import", "04", "Plan"),
    ("05-measurement.md", "Measurement", "05", "Plan"),
    ("06-security.md", "Security", "06", "Plan"),
    ("07-roadmap.md", "Roadmap", "07", "Plan"),
    ("08-commercial-path.md", "Commercial path", "08", "Plan"),
    ("decisions.md", "Decision log", "—", "Plan"),
    ("access/00-overview.md", "Overview", "A0", "Personas & access module"),
    ("access/01-systems.md", "Systems", "A1", "Personas & access module"),
    ("access/02-integrations.md", "Integrations", "A2", "Personas & access module"),
    ("access/03-how-it-works.md", "How it works", "A3", "Personas & access module"),
    ("access/04-security.md", "Security", "A4", "Personas & access module"),
    ("access/05-vaultwarden.md", "Vaultwarden", "A5", "Personas & access module"),
    ("access/06-phases.md", "Phases", "A6", "Personas & access module"),
]
IDS = {path: "d" + re.sub(r"[^a-z0-9]", "", num.lower()) if num != "—" else "dlog" for path, _, num, _ in ORDER}

LIST_RE = re.compile(r"^(\s*)([-*]|\d+\.)(\s+)(.*)$")


def doc_id(doc):
    return IDS[doc]


def slug(text):
    t = text.strip().lower()
    t = re.sub(r"[^\w\s-]", "", t)
    return re.sub(r"\s", "-", t)


def indent(line):
    return len(line) - len(line.lstrip(" "))


def resolve(href, doc):
    if href.startswith(("http://", "https://")):
        return href
    if href.startswith("#"):
        return f"#{doc_id(doc)}-{href[1:]}"
    path, _, frag = href.partition("#")
    target = os.path.normpath(os.path.join(os.path.dirname(doc), path)).replace(os.sep, "/")
    if target in IDS:
        return f"#{IDS[target]}-{frag}" if frag else f"#{IDS[target]}"
    return None


def inline(text, doc):
    codes = []

    def keep(m):
        codes.append("<code>" + html.escape(m.group(1)) + "</code>")
        return f"\x00{len(codes) - 1}\x00"

    text = re.sub(r"`([^`]+)`", keep, text)
    text = html.escape(text, quote=False)

    def link(m):
        label, href = m.group(1), m.group(2)
        url = resolve(href, doc)
        if url is None:
            return label
        return f'<a href="{html.escape(url, quote=True)}">{label}</a>'

    text = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", link, text)
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", text)
    text = re.sub(r"(?<![\w])_(?!\s)(.+?)(?<!\s)_(?![\w])", r"<em>\1</em>", text)
    return re.sub(r"\x00(\d+)\x00", lambda m: codes[int(m.group(1))], text)


def split_row(line):
    line = line.strip()
    if line.startswith("|"):
        line = line[1:]
    if line.endswith("|"):
        line = line[:-1]
    return [c.strip() for c in line.split("|")]


def starts_block(line):
    return (
        line.startswith("```")
        or re.match(r"^#{1,4}\s", line)
        or re.match(r"^-{3,}\s*$", line)
        or LIST_RE.match(line)
        or line.lstrip().startswith("|")
    )


def parse_list(lines, i):
    first = LIST_RE.match(lines[i])
    base = len(first.group(1))
    ordered = first.group(2).endswith(".")
    items, loose = [], False
    n = len(lines)
    while i < n:
        m = LIST_RE.match(lines[i])
        if not m or len(m.group(1)) != base or m.group(2).endswith(".") != ordered:
            break
        content_indent = base + len(m.group(2)) + len(m.group(3))
        body, item_loose = [m.group(4)], False
        i += 1
        while i < n:
            line = lines[i]
            if not line.strip():
                k = i
                while k < n and not lines[k].strip():
                    k += 1
                if k < n and indent(lines[k]) >= content_indent:
                    body.extend([""] * (k - i))
                    i, item_loose = k, True
                    continue
                break
            if indent(line) >= content_indent:
                body.append(line[content_indent:])
                i += 1
                continue
            if indent(line) > base and not LIST_RE.match(line):
                body.append(line.strip())
                i += 1
                continue
            break
        items.append((body, item_loose))
        k = i
        while k < n and not lines[k].strip():
            k += 1
        if k > i and k < n:
            m2 = LIST_RE.match(lines[k])
            if m2 and len(m2.group(1)) == base and m2.group(2).endswith(".") == ordered:
                loose, i = True, k
    return items, ordered, loose, i


def render(lines, doc, tight=False):
    out, i, n = [], 0, len(lines)
    while i < n:
        line = lines[i]
        if not line.strip():
            i += 1
            continue
        fence = re.match(r"^```(\w*)\s*$", line)
        if fence:
            lang, j, buf = fence.group(1), i + 1, []
            while j < n and not lines[j].startswith("```"):
                buf.append(lines[j])
                j += 1
            body = html.escape("\n".join(buf))
            if lang == "mermaid":
                out.append(f'<figure class="diagram"><pre class="mermaid">{body}</pre></figure>')
            else:
                out.append(f'<div class="code" tabindex="0"><pre><code>{body}</code></pre></div>')
            i = j + 1
            continue
        head = re.match(r"^(#{1,4})\s+(.*)$", line)
        if head:
            level = len(head.group(1))
            text = head.group(2).strip()
            if level == 1:
                i += 1
                continue  # the doc title is rendered by the section header
            hid = f"{doc_id(doc)}-{slug(text)}"
            tag = f"h{level + 1}"
            out.append(f'<{tag} id="{hid}">{inline(text, doc)}</{tag}>')
            i += 1
            continue
        if re.match(r"^-{3,}\s*$", line):
            out.append("<hr>")
            i += 1
            continue
        if line.lstrip().startswith("|") and i + 1 < n and re.match(r"^\s*\|[\s:|-]+\|\s*$", lines[i + 1]):
            header = split_row(line)
            rows, j = [], i + 2
            while j < n and lines[j].lstrip().startswith("|"):
                rows.append(split_row(lines[j]))
                j += 1
            th = "".join(f'<th scope="col">{inline(c, doc)}</th>' for c in header)
            body = "".join(
                "<tr>" + "".join(f"<td>{inline(c, doc)}</td>" for c in r) + "</tr>" for r in rows
            )
            out.append(
                f'<div class="table-wrap" tabindex="0"><table><thead><tr>{th}</tr></thead>'
                f"<tbody>{body}</tbody></table></div>"
            )
            i = j
            continue
        if LIST_RE.match(line):
            items, ordered, loose, i = parse_list(lines, i)
            tag = "ol" if ordered else "ul"
            lis = []
            for body, item_loose in items:
                cls = ""
                if body and body[0].startswith("[ ] "):
                    body = [body[0][4:]] + body[1:]
                    cls = ' class="task"'
                inner = render(body, doc, tight=not (loose or item_loose))
                lis.append(f"<li{cls}>{inner}</li>")
            start = ""
            if ordered:
                num = int(LIST_RE.match(line).group(2)[:-1])
                start = f' start="{num}"' if num != 1 else ""
            out.append(f"<{tag}{start}>{''.join(lis)}</{tag}>")
            continue
        para = [line.strip()]
        i += 1
        while i < n and lines[i].strip() and not starts_block(lines[i]):
            para.append(lines[i].strip())
            i += 1
        raw = " ".join(para)
        text = inline(raw, doc)
        if tight:
            out.append(text)
        elif raw.startswith("**TL;DR:**"):
            out.append(f'<p class="tldr">{text}</p>')
        else:
            out.append(f"<p>{text}</p>")
    return "".join(out)


def strip_frontmatter(text):
    if text.startswith("---\n"):
        end = text.find("\n---\n", 4)
        if end != -1:
            return text[end + 5:]
    return text


def build(plan_dir, out_path):
    sections, groups = [], {}
    for path, short, num, group in ORDER:
        src = strip_frontmatter((plan_dir / path).read_text(encoding="utf-8"))
        lines = src.splitlines()
        title = next((l[2:].strip() for l in lines if l.startswith("# ")), short)
        title = re.sub(r"^(Synapse|Personas & access)\s+—\s+", "", title)
        did = doc_id(path)
        groups.setdefault(group, []).append(
            f'<li><a href="#{did}"><span class="num">{num}</span>{html.escape(short)}</a></li>'
        )
        kicker = '<span class="kicker">Personas &amp; access module</span>' if path.startswith("access/") else ""
        sections.append(
            f'<section class="doc" id="{did}" aria-labelledby="{did}-title">'
            f'<header class="doc-head"><span class="doc-num">{num}</span>'
            f'<div>{kicker}<h2 id="{did}-title">{inline(title, path)}</h2></div></header>'
            f"{render(lines, path)}</section>"
        )
    nav = "".join(
        f'<h2>{html.escape(g)}</h2><ol>{"".join(items)}</ol>' for g, items in groups.items()
    )
    page = TEMPLATE.replace("{{NAV}}", nav).replace("{{SECTIONS}}", "".join(sections))
    out_path.write_text(page, encoding="utf-8")


TEMPLATE = """<title>Synapse Plan</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wdth,wght@87,600;87,700&family=IBM+Plex+Mono:wght@400;500&family=IBM+Plex+Sans:ital,wght@0,400;0,500;0,600;1,400&display=swap">
<style>
/* Layout: a sticky contents rail beside one reading column (~70ch); tables, code and diagrams may run the full column width and scroll inside their own box. */
:root {
  --bg: #f6f7f9;
  --surface: #ffffff;
  --fg: #18202b;
  --muted: #566273;
  --rule: #d9dee5;
  --accent: #1d5c86;
  --accent-soft: #e6eef5;
  --signal: #9a5b00;
  --code-bg: #eef1f5;
  --display: "Archivo", "Arial Narrow", "Helvetica Neue", Arial, sans-serif;
  --body: "IBM Plex Sans", -apple-system, "Segoe UI", Roboto, sans-serif;
  --mono: "IBM Plex Mono", ui-monospace, "SF Mono", Menlo, monospace;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme="light"]) {
    --bg: #11161d; --surface: #171e27; --fg: #e4e9ef; --muted: #9aa6b5; --rule: #2a3440;
    --accent: #7db4dc; --accent-soft: #1b2b3d; --signal: #e0a54a; --code-bg: #1c242e;
    color-scheme: dark;
  }
}
:root[data-theme="dark"] {
  --bg: #11161d; --surface: #171e27; --fg: #e4e9ef; --muted: #9aa6b5; --rule: #2a3440;
  --accent: #7db4dc; --accent-soft: #1b2b3d; --signal: #e0a54a; --code-bg: #1c242e;
  color-scheme: dark;
}
html { scroll-behavior: smooth; scroll-padding-top: 16px; }
body { background: var(--bg); color: var(--fg); font-family: var(--body); font-size: 16px; line-height: 1.62; }
.page { max-width: 1200px; margin: 0 auto; padding-inline: 20px; padding-block: 36px 72px; display: grid; grid-template-columns: 220px minmax(0, 1fr); gap: 0 44px; }
.masthead { grid-column: 1 / -1; display: grid; gap: 12px; padding-bottom: 26px; margin-bottom: 8px; border-bottom: 2px solid var(--fg); }
.meta { font-family: var(--mono); font-size: 12.5px; letter-spacing: .05em; text-transform: uppercase; color: var(--muted); display: flex; flex-wrap: wrap; gap: 6px 16px; }
.meta .status { color: var(--signal); font-weight: 500; }
h1 { font-family: var(--display); font-weight: 700; font-stretch: 87%; font-size: clamp(38px, 7vw, 58px); line-height: 1; letter-spacing: -.01em; margin: 0; }
.lede { font-size: 19px; line-height: 1.5; max-width: 62ch; margin: 0; text-wrap: pretty; }
.facts { display: flex; flex-wrap: wrap; gap: 8px 22px; margin: 4px 0 0; padding: 0; list-style: none; font-size: 14px; color: var(--muted); }
.facts b { font-family: var(--mono); font-weight: 500; font-size: 11.5px; letter-spacing: .06em; text-transform: uppercase; color: var(--accent); margin-right: 6px; }
nav.toc { position: sticky; top: 16px; align-self: start; padding-top: 22px; }
nav.toc h2 { font-family: var(--mono); font-size: 11.5px; font-weight: 500; letter-spacing: .08em; text-transform: uppercase; color: var(--muted); margin: 18px 0 8px; }
nav.toc h2:first-child { margin-top: 0; }
.kicker { display: block; font-family: var(--mono); font-size: 11.5px; letter-spacing: .06em; text-transform: uppercase; color: var(--signal); margin-bottom: 4px; }
nav.toc ol { list-style: none; margin: 0; padding: 0; display: grid; gap: 2px; }
nav.toc a { display: flex; gap: 10px; align-items: baseline; padding: 5px 8px; border-radius: 4px; color: var(--fg); text-decoration: none; font-size: 14.5px; }
nav.toc a:hover { background: var(--accent-soft); }
nav.toc .num { font-family: var(--mono); font-size: 12px; color: var(--accent); min-width: 1.6em; }
main { min-width: 0; }
.doc { padding-block: 30px 18px; border-bottom: 1px solid var(--rule); }
.doc-head { display: flex; align-items: baseline; gap: 14px; margin-bottom: 14px; }
.doc-num { font-family: var(--display); font-weight: 700; font-stretch: 87%; font-size: 34px; line-height: 1; color: var(--accent); }
.doc h2 { font-family: var(--display); font-weight: 700; font-stretch: 87%; font-size: 34px; line-height: 1.08; margin: 0; text-wrap: balance; }
.doc h3 { font-family: var(--display); font-weight: 600; font-stretch: 87%; font-size: 23px; line-height: 1.2; margin: 34px 0 10px; text-wrap: balance; }
.doc h4 { font-family: var(--body); font-weight: 600; font-size: 17px; margin: 24px 0 8px; }
.doc h5 { font-family: var(--body); font-weight: 600; font-size: 15px; margin: 18px 0 6px; color: var(--muted); }
.doc p, .doc ul, .doc ol { max-width: 70ch; margin: 0 0 12px; }
.doc ul, .doc ol { padding-left: 1.3em; }
.doc li { margin: 4px 0; }
.doc li > ul, .doc li > ol { margin: 6px 0 4px; }
.doc li > p { margin: 0 0 6px; }
.doc li::marker { color: var(--muted); }
.doc li.task { list-style: none; position: relative; }
.doc li.task::before { content: ""; position: absolute; left: -1.3em; top: .38em; width: .85em; height: .85em; border: 1.5px solid var(--muted); border-radius: 3px; }
.tldr { border-left: 3px solid var(--accent); background: var(--surface); padding: 12px 16px; border-radius: 0 6px 6px 0; font-size: 16.5px; }
strong { font-weight: 600; }
code { font-family: var(--mono); font-size: .86em; background: var(--code-bg); padding: 1px 5px; border-radius: 3px; overflow-wrap: anywhere; }
a { color: var(--accent); text-underline-offset: 2px; }
a:focus-visible, [tabindex]:focus-visible { outline: 2px solid var(--accent); outline-offset: 2px; border-radius: 3px; }
hr { border: 0; border-top: 1px dashed var(--rule); margin: 26px 0; }
.code { overflow-x: auto; background: var(--code-bg); border: 1px solid var(--rule); border-radius: 6px; margin: 0 0 14px; }
.code pre { margin: 0; padding: 14px 16px; font-family: var(--mono); font-size: 13px; line-height: 1.6; }
.code code { background: none; padding: 0; font-size: inherit; overflow-wrap: normal; }
.diagram { margin: 6px 0 18px; padding: 16px; background: var(--surface); border: 1px solid var(--rule); border-radius: 6px; overflow-x: auto; }
.diagram pre { margin: 0; font-family: var(--mono); font-size: 12px; white-space: pre; }
.table-wrap { overflow-x: auto; border: 1px solid var(--rule); border-radius: 6px; background: var(--surface); margin: 4px 0 16px; }
table { border-collapse: collapse; width: 100%; min-width: 620px; font-size: 14.5px; line-height: 1.45; }
th, td { text-align: left; vertical-align: top; padding: 9px 12px; border-bottom: 1px solid var(--rule); }
tr:last-child td { border-bottom: 0; }
thead th { font-family: var(--mono); font-weight: 500; font-size: 11.5px; letter-spacing: .06em; text-transform: uppercase; color: var(--muted); background: var(--code-bg); }
td:first-child { font-weight: 500; }
footer { grid-column: 2; padding-top: 22px; font-family: var(--mono); font-size: 12.5px; color: var(--muted); }
@media (max-width: 860px) {
  .page { grid-template-columns: minmax(0, 1fr); }
  nav.toc { position: static; padding-top: 14px; }
  nav.toc ol { display: flex; gap: 6px; overflow-x: auto; padding-bottom: 6px; }
  nav.toc h2 { margin: 10px 0 6px; }
  nav.toc a { white-space: nowrap; border: 1px solid var(--rule); background: var(--surface); }
  footer { grid-column: 1; }
  .lede { font-size: 17px; }
  .doc h2, .doc-num { font-size: 28px; }
}
@media (prefers-reduced-motion: reduce) { html { scroll-behavior: auto; } }
</style>

<div class="page">
  <header class="masthead">
    <div class="meta"><span>Plan set v2.0</span><span class="status">Draft for review</span><span>2026-10-14</span><span>Sean Sands</span></div>
    <h1>Synapse</h1>
    <p class="lede">A desktop app and tray service for Mac and Windows that makes an AI workspace visible and manageable. It reads and writes the same plain files agents and Obsidian use. It runs its checks without an agent, creates and imports workspaces with measured results, and keeps each persona's accounts and tools apart.</p>
    <ul class="facts">
      <li><b>Platforms</b>macOS and Windows</li>
      <li><b>Source of truth</b>plain files in git</li>
      <li><b>Stack</b>Rust and Tauri 2</li>
      <li><b>North star</b>your workspace</li>
      <li><b>Stages</b>0–6 personal, 7 if commercial</li>
    </ul>
  </header>
  <nav class="toc" aria-label="Plan documents">
    {{NAV}}
  </nav>
  <main>{{SECTIONS}}</main>
  <footer>Generated from 07-projects/26-synapse/plan/ by tools/build-plan-html.py. Edit the markdown, then rebuild.</footer>
</div>
"""

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    build(Path(sys.argv[1]), Path(sys.argv[2]))
