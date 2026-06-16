---
name: material-symbols-suite
description: Material Symbols Icon Automation Suite patterns and architecture. Use when building multi-part automation tools with shared configuration, debugging multi-component systems, or creating user-friendly tooling for non-developers. Covers shared config, folder structure, and debugging workflows.
aliases: [material-symbols-suite]
spec_version: "2.0"
tier: spoke
domain: design
hub: material-symbols-project
prerequisites: [material-symbols-project]
---

# Material Symbols Suite Patterns

---

## Epistemic Standards

This skill operates under shared epistemic principles. When beginning non-trivial
work, load and apply: `shared/epistemic-standards.md`

Core obligations: surface assumptions before acting on them; verify sources are
recent *and* relevant (standards version frequently); name rejected alternatives;
distinguish user framing from evidence; make uncertainty explicit.

---

## Artifact Standards

This skill follows shared artifact naming, versioning, and delivery conventions.
Load when producing or receiving any file: `shared/artifact-standards.md`

Core obligations: name every artifact with context_descriptor_vN.N_YYYY-MM-DD.ext;
never silently overwrite — increment the version; deliver runnable code as a
double-click zip (macOS default, other platforms additive); all outputs must be
immediately usable without a terminal.

---

## Shared Configuration

Central `config.json` at project root, consumed by all components:

```json
{
  "variable_axes": {
    "optical_size": { "values": [14, 16, 20, 24, 48], "default": 24 },
    "fill": { "values": [0, 1], "default": 0 }
  },
  "export_settings": {
    "coordinate_system": { "viewBox": "0 -960 960 960" }
  },
  "figma_settings": {
    "component_set": { "fixed_width": 154, "padding": 16 },
    "category_frame": { "fixed_width": 1200, "category_spacing": 104 }
  }
}
```

Load with defaults + override pattern:

```python
import json
from pathlib import Path

DEFAULT_CONFIG = { ... }

def load_config():
    config_path = Path(__file__).parent.parent / 'config.json'
    if config_path.exists():
        with open(config_path) as f:
            return {**DEFAULT_CONFIG, **json.load(f)}
    return DEFAULT_CONFIG
```

## Folder Structure

```
project-root/
├── config.json           # Shared configuration
├── output/
│   ├── svgs/            # Part 1 output → Part 3 input
│   │   └── home_opsz24_FILL0.svg
│   └── metadata/
│       └── icons_metadata.json  # Part 2 output → Part 3 input
├── svg-exporter/        # Part 1
├── metadata-scraper/    # Part 2
└── figma-plugin/        # Part 3
```

## Metadata JSON Format

```json
[
  {
    "name": "home",
    "categories": ["Home"],
    "tags": ["house", "building", "residence"],
    "version": 1
  }
]
```

## Debugging Workflow

### Systematic Approach

1. **Isolate** - Test each component independently
2. **Log comprehensively** - Capture state at each step
3. **Iterate with versions** - v1, v1.1, v2 with clear changelogs
4. **Test fixes independently** - One change per iteration

### Debug vs Production Pattern

Every script/plugin has two versions:

```
exporter.py        # Production (clean output)
exporter_debug.py  # Debug (verbose logging)
```

Or use runtime flag:

```python
DEBUG = '--debug' in sys.argv or os.environ.get('DEBUG')
```

### Error Reporting

Skip problematic items with detailed logs, don't fail entire process:

```python
skipped = []
for icon in icons:
    try:
        process(icon)
    except Exception as e:
        skipped.append({'name': icon, 'error': str(e)})
        log.warning(f"Skipped {icon}: {e}")

# Report at end
log.info(f"Processed: {len(icons) - len(skipped)}")
log.info(f"Skipped: {len(skipped)}")
for item in skipped:
    log.debug(f"  {item['name']}: {item['error']}")
```

## Non-Developer User Focus

### GUI Interfaces

Provide tkinter GUI with sensible defaults. All options visible, not hidden.

### Launcher Scripts

Platform-specific scripts that handle environment:
- `SETUP.bat` (Windows)
- `SETUP.sh` (Mac/Linux)

Include clear error messages and "press Enter to exit" for visibility.

### Documentation Hierarchy

```
START_HERE.md          # 2-minute orientation
GETTING_STARTED.md     # 15-minute complete walkthrough
README.md              # Technical overview
TROUBLESHOOTING.md     # Common issues by symptom
```

## Change Detection

Content-based hash stored in component descriptions:

```python
import hashlib

def compute_hash(svg_content):
    return hashlib.md5(svg_content.encode()).hexdigest()[:6]

# Store in description
description = f"home, house, building [hash:{hash_value}]"
```

Compare on import to detect actual changes vs. metadata-only changes.

## Continuation Prompts

For long debugging sessions, provide structured continuation:

```markdown
## Current Status - v{X}

### Fixes Applied
1. ✅ Issue resolved
2. ✅ Another fix

### Remaining Issues
1. ❌ Still broken

### Files Changed
- `path/to/file.py` - Description

### Next Steps
Continue from v{X} with [specific context]
```

## Related
- hub → [[material-symbols-project]]
