# Artifact Standards — Naming, Versioning & Delivery

Shared reference for all skills. Applies to every file, document, archive, or
runnable artifact produced or received in any session — regardless of type or domain.

---

## 1. The Core Problem This Solves

Artifacts get lost. Versions get overwritten. "The one from last Tuesday" becomes
unrecoverable. A script that worked once can't be re-run because the person who
received it doesn't know how. These standards exist to prevent all three failure modes.

---

## 2. Naming Convention

Every artifact gets a structured filename on creation. Never use untitled, generic,
or date-only names. The convention:

```
[context]_[descriptor]_v[version]_[YYYY-MM-DD].[ext]
```

| Segment | Rules | Examples |
|---|---|---|
| `context` | Project, system, or component area. Lowercase, hyphenated. | `ds-audit`, `centric-plm`, `data-table` |
| `descriptor` | What this artifact *is*. Lowercase, hyphenated. | `component-spec`, `triage-report`, `token-map`, `launcher` |
| `v[version]` | See versioning rules below. | `v1.0`, `v1.2`, `v2.0` |
| `[YYYY-MM-DD]` | Date of this version. ISO 8601 — no exceptions. | `2025-06-14` |
| `[ext]` | Accurate file extension. Never `.txt` for structured content. | `.html`, `.zip`, `.md`, `.fig`, `.xlsx` |

**Full examples:**
```
ds-audit_triage-report_v1.0_2025-06-14.md
centric-plm_data-table-spec_v2.1_2025-07-03.html
token-migration_mapping-reference_v1.0_2025-06-20.xlsx
data-table_inline-edit-launcher_v1.0_2025-06-14.zip
```

### Naming rules
- No spaces anywhere. Hyphens within segments, underscores between segments.
- If the user supplies a name or renames something mid-session, adopt it immediately
  and apply the convention around it — don't override their intent.
- If a file arrives without a compliant name, note the suggested rename but don't
  block on it.

---

## 3. Versioning

Use semantic-style two-part versioning: `v[major].[minor]`

| Change type | Version bump | Example |
|---|---|---|
| First delivery of a new artifact | `v1.0` | — |
| Iteration, refinement, correction, or addition | Minor: `v1.0 → v1.1` | Fixed a label, added a section |
| Structural change, scope change, breaking revision | Major: `v1.x → v2.0` | Rebuilt from different assumptions; schema changed |
| Superseded by a completely new approach | New artifact, new name | Don't force v3.0 on something that's actually a different thing |

**Never silently overwrite.** If a file is being revised, the prior version is
retained by incrementing. The current version is always the highest number.

### Version register

For any session producing more than two artifacts, maintain a version register
in the conversation or as a companion `.md` file:

```
## Version Register — [Project/Context] — [Session Date]

| Artifact | Version | Date | Status | Notes |
|---|---|---|---|---|
| ds-audit_triage-report | v1.0 | 2025-06-14 | Superseded | Initial draft |
| ds-audit_triage-report | v1.1 | 2025-06-14 | Superseded | Added severity column |
| ds-audit_triage-report | v2.0 | 2025-06-15 | Current | Restructured after scope change |
```

The register is itself a versioned artifact:
```
[context]_version-register_v[n].[n]_[YYYY-MM-DD].md
```

---

## 4. Non-Developer Output Standards

Every delivered artifact must be immediately usable by someone with no terminal
access, no development environment, and no prior context. Apply this by default.

### HTML artifacts
- Single self-contained `.html` file. All CSS and JS inline — no external
  dependencies that could break or require a server.
- Should open correctly by double-clicking in Finder (macOS) or Explorer (Windows).
- If the content requires dynamic data loading (JSON, CSV), bundle the data inline
  as a JavaScript variable inside the HTML file.

### Documents (specs, reports, decision records)
- Prefer `.html` for rich formatting that opens in any browser.
- Use `.md` when the destination is a developer tool (GitHub, Confluence) or when
  the user will paste into Figma.
- Use `.pdf` for anything intended for stakeholders, executives, or external sharing.
- Use `.docx` or `.pptx` when the user needs an editable Office-format file.
- Never deliver raw JSON or YAML as a final output — wrap it in HTML or `.md`
  with context.

### Data artifacts
- `.xlsx` for anything tabular intended for non-developer review or Airtable import.
- `.csv` as an additional export when machine ingestion is likely (MCP connectors, etc.).
- Always include a header row. Column names should be human-readable, not camelCase.

---

## 5. Runnable Code — Encapsulated Delivery

When an artifact requires a server, runtime, or terminal to execute, it must be
delivered as a self-contained, double-click-to-run package. Never deliver a bare
script and assume the recipient can run it.

### Default platform: macOS
Unless specified otherwise, all runnable packages target macOS first.
If another platform is requested, deliver for that platform *in addition* to macOS —
not instead of it.

### Package structure

```
[context]_[descriptor]_v[version]_[YYYY-MM-DD]/
├── start.command          ← macOS launcher (double-click to run)
├── start.bat              ← Windows launcher (included by default)
├── README.html            ← Plain-English instructions, opens in browser
├── [app files]            ← The actual content
└── [context]_[descriptor]_v[version]_[YYYY-MM-DD].zip   ← Deliverable archive
```

The `.zip` is the deliverable. Its name matches the folder inside it.

### macOS launcher (`start.command`)

```bash
#!/bin/bash
# Move to the directory containing this script
cd "$(dirname "$0")"

# Check for Python 3
if ! command -v python3 &> /dev/null; then
  osascript -e 'display alert "Python 3 Required" message "Please install Python 3 from https://www.python.org/downloads/ and try again."'
  exit 1
fi

# Start server and open browser
PORT=8765
python3 -m http.server $PORT &
SERVER_PID=$!
sleep 1
open "http://localhost:$PORT"

# Wait — quit server when window closes (trap Ctrl+C or terminal close)
echo "Server running at http://localhost:$PORT"
echo "Press Ctrl+C to stop."
trap "kill $SERVER_PID" EXIT
wait $SERVER_PID
```

After creating `start.command`, always set executable permission in the same step:
```bash
chmod +x start.command
```

### Windows launcher (`start.bat`)

```bat
@echo off
cd /d "%~dp0"
where python >nul 2>nul
if %errorlevel% neq 0 (
  echo Python not found. Please install from https://www.python.org/downloads/
  pause
  exit /b 1
)
start "" "http://localhost:8765"
python -m http.server 8765
pause
```

### README.html (always included)

The README must answer three questions in plain language with no assumed knowledge:
1. What is this? (one sentence)
2. How do I open it? (numbered steps — max 4)
3. What do I do if it doesn't work? (one fallback, one contact)

Do not include technical terminology in the README unless it is unavoidable, and
define it inline when used.

### When Python is not a valid assumption

If the runnable artifact has no dependency on a dynamic server (pure HTML/JS/CSS),
skip the server launcher and deliver the HTML directly in the zip alongside the README.
The `start.command` pattern is for artifacts that genuinely require a local server
(e.g., fetching local JSON files, running a Node/Python backend).

For pure front-end artifacts: no launcher needed — just `index.html` + `README.html`.

---

## 6. Figma Artifact Naming

Figma pages, frames, and components follow the same versioning logic but use
Figma-native conventions (spaces allowed, title case).

| Figma element | Convention | Example |
|---|---|---|
| Page | `[Area] — v[n].[n] [YYYY-MM-DD]` | `Data Table Spec — v1.2 2025-06-14` |
| Section/frame | `[Descriptor] — [Status]` | `Inline Edit States — In Review` |
| Archived page | Prefix with `[ARCHIVE]` | `[ARCHIVE] Token Map — v1.0` |
| Draft page | Prefix with `[WIP]` | `[WIP] Component Audit` |

Never delete a Figma page that contains a finalized version. Archive it.

---

## 7. Receiving User-Supplied Artifacts

When the user supplies a file:
1. Note the filename as received.
2. Suggest a compliant name if it doesn't follow the convention — but ask before
   renaming anything they'll need to find again.
3. If it's a new version of something already in context, identify which version it
   supersedes and update the version register.
4. Apply Documentation Trust Matrix (see `ds-advisor` skill) to any content that
   will inform a decision.

---

## 8. Session Handoff

At the end of any session that produced artifacts, output a brief handoff block:

```
## Session Artifacts — [Date]

| File | Version | Format | Status |
|---|---|---|---|
| [filename] | v[n].[n] | [ext] | Delivered / In progress |

Next session: [what needs to happen — specific enough to act on without re-reading
the entire conversation]
```

This is the minimum needed to resume without losing context.
