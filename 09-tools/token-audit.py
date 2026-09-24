#!/usr/bin/env python3
"""token-audit — mechanical gate for a three-tier design token system.

Encodes the checkable rules from the Subatomic course synthesis ([[design-token-architecture]],
project 23) so any agent can audit a token source instead of eyeballing it:

  tiers      tier 1 = raw values (definitions) · tier 2 = aliases that give values jobs
             (semantic) · tier 3 = rare component / category / special-case overrides
  aliases    every `{ref}` resolves, no cycles, no upward references (1→2, 2→3)
  budget     tier 3 is a privilege: warn when it grows past a share of the system
  naming     legibility over succinctness (no cryptic abbreviations), one size vocabulary,
             one case/separator convention, tier-2 colour properties from a fixed bucket set
  themes     every ROOT theme exposes the same tier-2 + tier-3 API (components depend on it); skinny
             child themes (dark / sub-brand / campaign) are checked with --parent/--override instead
  parity     Figma vs code token names match once the sanctioned divergences are removed
             (code-only prefix, Figma's named `default`, code-only animation/z-index/breakpoint,
             Figma-only viewport)
  css        component CSS/SCSS consumes tier 2/3 only — no raw colour literals (hex, functional,
             named), no tier-1 vars (tier-1 spacing and z-index are exempt), no stray typography
             literals (use composites), no hard-coded spacing/radius/shadow/motion/z-index; a stylesheet
             that paints a knockout background also uses knockout content (same component)
  outputs    every platform output (CSS/SCSS/JSON) built from one source exposes the same names
  override   a child theme (dark / sub-brand / campaign) only overrides names its parent has, and only
             allowed categories (dark: colour + shadow; sub-brand / campaign: colour, font-family, radius)
  contrast   tier-2 content-on-background pairs meet WCAG 4.5:1 in every theme (a11y is not deferrable);
             translucent text is composited over its background; unparseable colours are reported (TA024)

Input: DTCG (`$value`/`$type`) or Style Dictionary (`value`, `{a.b.value}` refs) JSON, nested groups;
files or directories (build/dist/node_modules skipped inside the directory given; a directory with no
token JSON is bad input). Tier resolution, first match wins, judged only on the part of the path you
pointed at (a directory argument's own name + below; for a file, a `tier-N` folder anywhere in the path
typed, else its immediate parent): a `tier-1|2|3`
directory (structure = tier) · a `core/` directory → 1 · `--config` `tier_prefixes` (dotted token-name
prefixes) · inference (raw value → 1; alias under a category root → 2; alias under anything else,
e.g. `button.*` → 3). Rule ids TA001–TA024 (TA010 unassigned); errors: TA001–005, TA013, TA021, TA023.

Usage:
  python3 09-tools/token-audit.py tokens/**/*.json
  python3 09-tools/token-audit.py core/ strawberry/                 # one theme + shared core, by directory
  python3 09-tools/token-audit.py --themes strawberry/ chocolate/ vanilla/
  python3 09-tools/token-audit.py --parity figma-export.json code-tokens.json
  python3 09-tools/token-audit.py tokens.json --css src/components --prefix ds
  python3 09-tools/token-audit.py --outputs dist/tokens.css dist/_tokens.scss dist/tokens.json
  python3 09-tools/token-audit.py --parent chocolate/ --override dark-chocolate/ --kind dark
  python3 09-tools/token-audit.py core/ --themes strawberry/ chocolate/ --contrast
  python3 09-tools/token-audit.py --config token-audit.config.json tokens.json --json
  python3 09-tools/token-audit.py --self-test

Exit: 0 clean (warnings allowed) · 1 errors (or warnings with --strict) · 2 bad input (unreadable or
invalid JSON, non-object root, empty directory, --override without --parent).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

REF_RE = re.compile(r"\{([^{}]+)\}")
CSS_VAR_RE = re.compile(r"var\(\s*--([a-zA-Z0-9_-]+)")
# Sass variables, optionally module-namespaced (`$ds-x`, `tokens.$ds-x`).
SCSS_VAR_RE = re.compile(r"(?<![\w$-])(?:[A-Za-z_][\w-]*\.)?\$([A-Za-z_][\w-]*)")
# `(?<![\w-])` so getters such as `theme-color(…)` / `mat-color(…)` / `ds-color(…)` are token reads, not literals.
CSS_COLOR_LITERAL_RE = re.compile(r"#[0-9a-fA-F]{3,8}\b|(?<![\w-])(?:rgba?|hsla?|oklch|oklab|lab|lch|hwb|color)\(")
CSS_NAMED_COLORS = (
    "aliceblue antiquewhite aqua aquamarine azure beige bisque black blanchedalmond blue blueviolet brown "
    "burlywood cadetblue chartreuse chocolate coral cornflowerblue cornsilk crimson cyan darkblue darkcyan "
    "darkgoldenrod darkgray darkgreen darkgrey darkkhaki darkmagenta darkolivegreen darkorange darkorchid "
    "darkred darksalmon darkseagreen darkslateblue darkslategray darkslategrey darkturquoise darkviolet "
    "deeppink deepskyblue dimgray dimgrey dodgerblue firebrick floralwhite forestgreen fuchsia gainsboro "
    "ghostwhite gold goldenrod gray green greenyellow grey honeydew hotpink indianred indigo ivory khaki "
    "lavender lavenderblush lawngreen lemonchiffon lightblue lightcoral lightcyan lightgoldenrodyellow "
    "lightgray lightgreen lightgrey lightpink lightsalmon lightseagreen lightskyblue lightslategray "
    "lightslategrey lightsteelblue lightyellow lime limegreen linen magenta maroon mediumaquamarine "
    "mediumblue mediumorchid mediumpurple mediumseagreen mediumslateblue mediumspringgreen "
    "mediumturquoise mediumvioletred midnightblue mintcream mistyrose moccasin navajowhite navy oldlace "
    "olive olivedrab orange orangered orchid palegoldenrod palegreen paleturquoise palevioletred "
    "papayawhip peachpuff peru pink plum powderblue purple rebeccapurple red rosybrown royalblue "
    "saddlebrown salmon sandybrown seagreen seashell sienna silver skyblue slateblue slategray slategrey "
    "snow springgreen steelblue tan teal thistle tomato turquoise violet wheat white whitesmoke yellow "
    "yellowgreen"
).split()
# Word-bounded so `var(--ds-color-red)` / `$white` never match; applied to colour-bearing properties only.
CSS_NAMED_COLOR_RE = re.compile(
    r"(?<![\w$@#.-])(?:" + "|".join(sorted(CSS_NAMED_COLORS, key=len, reverse=True)) + r")(?![\w-])", re.I)
COLOR_PROPS_RE = re.compile(
    r"^(?:color|background(?:-color|-image)?|border(?:-[a-z]+)*|outline(?:-color)?|fill|stroke|"
    r"(?:box|text)-shadow|text-decoration(?:-color)?|caret-color|accent-color|column-rule(?:-color)?)$")
# A declaration ends at `;` or just before the block's closing `}` (last declaration, minified CSS).
CSS_DECL_RE = re.compile(r"([a-zA-Z-]+)\s*:\s*([^;{}]+?)\s*(?:;|(?=\}))")
KO_BACKGROUND_RE = re.compile(r"background(?:-\w+)*-knockout")
KO_CONTENT_RE = re.compile(r"content(?:-\w+)*-knockout")
# Typography comes from composite bundles; a literal on one of these in component CSS is a stray.
TYPOGRAPHY_PROPS = {"font-size", "font-weight", "font-family", "line-height", "letter-spacing"}
CSS_KEYWORDS = {"inherit", "initial", "unset", "revert", "normal", "1", "0"}  # line-height:1 trims text boxes
# Non-colour visual decisions that must come from tokens in component CSS (course ch6: "no literal values").
DIMENSION_PROPS = {
    "padding", "padding-top", "padding-right", "padding-bottom", "padding-left", "padding-inline",
    "padding-block", "margin", "margin-top", "margin-right", "margin-bottom", "margin-left",
    "margin-inline", "margin-block", "gap", "row-gap", "column-gap", "border-radius", "border-width",
    "box-shadow", "transition", "transition-duration", "transition-delay", "animation",
    "animation-duration", "animation-delay", "z-index",
}
# Signed dimension/time literals, or a bare integer (z-index) — zero is stripped before this runs.
LITERAL_DIMENSION_RE = re.compile(r"(?<![\w-])-?(?:\d*\.?\d+)(?:px|rem|em|ms|s)\b|^\s*-?\d+\s*$")

# Roots that name a token *category* — an alias living directly under one of these is tier 2.
CATEGORY_ROOTS = {
    "color", "colour", "typography", "font", "font-family", "font-size", "font-weight",
    "line-height", "letter-spacing", "text-transform", "spacing", "space", "size", "sizing",
    "border", "border-width", "border-radius", "radius", "shadow", "box-shadow", "elevation",
    "animation", "motion", "duration", "easing", "opacity", "z-index", "zindex", "layer",
    "breakpoint", "viewport", "media",
}
# Segments that identify a tier or namespace rather than meaning; stripped before analysis.
TIER_WORDS = {
    "1": {"core", "primitive", "primitives", "definition", "definitions", "base", "global", "ref", "reference"},
    "2": {"theme", "semantic", "semantics", "alias", "sys", "system"},
    "3": {"component", "components", "comp", "override", "overrides"},
}
COLOR_PROPERTY_BUCKETS = {"background", "content", "border"}
COLOR_PROPERTY_OPTIONAL = {"text", "icon"}  # sanctioned split of `content` — opt-in (costs maintenance)

# Cryptic abbreviations → the spelled-out word the course's "legibility over succinctness" wants.
DEFAULT_ABBREVIATIONS = {
    "bg": "background", "fg": "foreground", "clr": "color", "col": "color", "txt": "text",
    "btn": "button", "brd": "border", "bdr": "border", "rad": "radius", "sz": "size",
    "fs": "font-size", "fw": "font-weight", "lh": "line-height", "ls": "letter-spacing",
    "ff": "font-family", "sp": "spacing", "pad": "padding", "mrg": "margin", "dur": "duration",
    "anim": "animation", "shdw": "shadow", "elev": "elevation", "pri": "primary",
    "sec": "secondary", "hl": "highlight", "dis": "disabled", "hvr": "hover", "foc": "focus",
    "inv": "inverse", "neu": "neutral", "tbl": "table", "nav": None, "img": None,
}
# Size vocabularies that must not be mixed within one system.
SIZE_SYNONYMS = [
    ("xs", "extra-small"), ("sm", "small"), ("md", "medium"), ("lg", "large"),
    ("xl", "extra-large"),
]
# Sanctioned parity divergences (course ch3 "naming parity: critical but impossible").
CODE_ONLY_ROOTS = {"animation", "motion", "duration", "easing", "z-index", "zindex", "layer", "breakpoint", "media"}
FIGMA_ONLY_ROOTS = {"viewport"}
ERROR_RULES = {"TA001", "TA002", "TA003", "TA004", "TA005", "TA013", "TA021", "TA023"}
# Child themes (course ch8): dark mode overrides colour + shadow only; sub-brands cosmetic categories only.
OVERRIDE_ALLOW = {
    "dark": {"color", "colour", "shadow", "box-shadow", "elevation"},
    "sub-brand": {"color", "colour", "font-family", "border-radius", "radius", "typography.font-family"},
}
OVERRIDE_ALLOW["campaign"] = OVERRIDE_ALLOW["sub-brand"]  # campaigns are cosmetic partial overrides too (ch8)
# Tier-2 content-on-background pairs checked for WCAG contrast when both exist (config `contrast_pairs` extends).
DEFAULT_CONTRAST_PAIRS = [
    ("color.content.default", "color.background.default"),
    ("color.content.subtle", "color.background.default"),
    ("color.content.knockout", "color.background.knockout"),  # knockout content pairs with knockout bg (ch6),
    # not with `background-brand` — brand backgrounds are often pale tints carrying default content.
    ("color.content.brand", "color.background.default"),
]


class BadInput(Exception):
    """Unreadable or structurally invalid input → exit 2, never mistaken for 'findings' (exit 1)."""


def norm_ref(ref: str) -> str:
    """`{a.b.value}` / `{a.b.$value}` (Style Dictionary) → `a.b`."""
    ref = ref.strip()
    for suf in (".$value", ".value"):
        if ref.endswith(suf):
            return ref[: -len(suf)]
    return ref


@dataclass
class Token:
    path: tuple[str, ...]
    value: object
    type: str | None
    source: str
    tier: str = "?"
    tier_path: str = ""  # the part of the path the user pointed at; tier directories are judged here only

    @property
    def name(self) -> str:
        return ".".join(self.path)

    def refs(self) -> list[str]:
        out: list[str] = []

        def walk(v: object) -> None:
            if isinstance(v, str):
                out.extend(norm_ref(m) for m in REF_RE.findall(v))
            elif isinstance(v, dict):
                for x in v.values():
                    walk(x)
            elif isinstance(v, list):
                for x in v:
                    walk(x)

        walk(self.value)
        return out

    def is_alias(self) -> bool:
        return bool(self.refs())


@dataclass
class Finding:
    rule: str
    token: str
    message: str
    source: str = ""

    @property
    def level(self) -> str:
        return "error" if self.rule in ERROR_RULES else "warn"


@dataclass
class Config:
    prefix: str = ""
    tier_prefixes: dict[str, list[str]] = field(default_factory=dict)  # {"1": ["core"], ...}
    tier3_max_share: float = 0.25
    tier3_may_alias_tier1: bool = True  # the course allows it; stricter systems may forbid
    abbreviations: dict[str, str | None] = field(default_factory=lambda: dict(DEFAULT_ABBREVIATIONS))
    allow_abbreviations: set[str] = field(default_factory=set)
    color_buckets: set[str] = field(default_factory=lambda: set(COLOR_PROPERTY_BUCKETS))
    require_type: bool = False
    contrast_pairs: list[tuple[str, str]] = field(default_factory=lambda: list(DEFAULT_CONTRAST_PAIRS))
    contrast_min: float = 4.5

    @classmethod
    def load(cls, path: str | None) -> "Config":
        cfg = cls()
        if not path:
            return cfg
        try:
            raw = json.loads(Path(path).read_text())
        except (OSError, ValueError) as e:
            raise BadInput(f"cannot read config {path}: {e}") from e
        if not isinstance(raw, dict):
            raise BadInput(f"{path}: config root must be a JSON object")
        try:
            cfg.prefix = str(raw.get("prefix", cfg.prefix))
            cfg.tier_prefixes = {str(k): [str(x) for x in v] for k, v in raw.get("tier_prefixes", {}).items()}
            cfg.tier3_max_share = float(raw.get("tier3_max_share", cfg.tier3_max_share))
            cfg.tier3_may_alias_tier1 = bool(raw.get("tier3_may_alias_tier1", cfg.tier3_may_alias_tier1))
            cfg.abbreviations.update(dict(raw.get("abbreviations", {})))
            cfg.allow_abbreviations = {str(x) for x in raw.get("allow_abbreviations", [])}
            cfg.color_buckets = {str(x) for x in raw.get("color_buckets", sorted(cfg.color_buckets))}
            cfg.require_type = bool(raw.get("require_type", cfg.require_type))
            pairs = [tuple(x) for x in raw.get("contrast_pairs", [])]
            if any(len(x) != 2 or not all(isinstance(y, str) for y in x) for x in pairs):
                raise ValueError("contrast_pairs must be a list of [fg, bg] token names")
            cfg.contrast_pairs += pairs  # type: ignore[arg-type]
            cfg.contrast_min = float(raw.get("contrast_min", cfg.contrast_min))
        except (TypeError, ValueError, AttributeError) as e:
            raise BadInput(f"{path}: invalid config value — {e}") from e
        return cfg


# ---------------------------------------------------------------- loading


def flatten(data: dict, source: str, path: tuple[str, ...] = (), inherited_type: str | None = None,
            tier_path: str = "") -> list[Token]:
    tokens: list[Token] = []
    group_type = data.get("$type", inherited_type) if isinstance(data, dict) else inherited_type
    for key, node in data.items():
        if key.startswith("$") or not isinstance(node, dict):
            continue
        if "$value" in node or "value" in node:
            val = node.get("$value", node.get("value"))
            tokens.append(Token(path + (key,), val, node.get("$type", node.get("type", group_type)), source,
                                tier_path=tier_path or source))
        else:
            tokens.extend(flatten(node, source, path + (key,), group_type, tier_path))
    return tokens


SKIP_DIRS = {"node_modules", "build", "dist", ".git", "__MACOSX"}
TIER_DIR_RE = re.compile(r"(?:^|[/\\])tier[-_ ]?([123])\b", re.I)


def expand(paths: list[str]) -> list[tuple[str, str]]:
    """(file, tier_path) pairs. Directories → their token JSON; build/vendored dirs are skipped *inside* the
    directory given (an ancestor named build/ does not hide everything). tier_path keeps only what the
    user pointed at — the directory argument's own name + below, or a file's immediate parent — so an
    unrelated ancestor such as `packages/core/…` cannot force a tier."""
    out: list[tuple[str, str]] = []
    for p in paths:
        pp = Path(p)
        if pp.is_dir():
            found = [f for f in sorted(pp.rglob("*.json"))
                     if not SKIP_DIRS & set(f.relative_to(pp).parts[:-1])
                     and not f.name.startswith(("package", "tsconfig", "."))]
            if not found:
                raise BadInput(f"{p}: directory contains no token JSON")
            # The directory's own name + the path below it; files are not resolve()d (symlinks may point anywhere).
            out.extend((str(f), f"{pp.resolve().name}/{f.relative_to(pp).as_posix()}") for f in found)
        elif TIER_DIR_RE.search(pp.parent.as_posix()):
            out.append((p, pp.as_posix()))  # an explicit tier-N folder anywhere in the typed path counts
        else:
            out.append((p, f"{pp.parent.name}/{pp.name}"))  # only an immediate `core/` parent counts
    return out


def load_tokens(paths: list[str]) -> list[Token]:
    out: list[Token] = []
    for p, tier_path in expand(paths):
        try:
            data = json.loads(Path(p).read_text())
        except (OSError, ValueError) as e:
            raise BadInput(f"cannot read {p}: {e}") from e
        if not isinstance(data, dict):
            raise BadInput(f"{p}: token root must be a JSON object")
        out.extend(flatten(data, p, tier_path=tier_path))
    return out


def meaning_segments(path: tuple[str, ...], cfg: Config) -> list[str]:
    """Path segments minus namespace prefix and tier words, split on - and _ for naming checks."""
    segs = [s.lower() for s in path]
    if cfg.prefix and segs and segs[0] == cfg.prefix.lower():
        segs = segs[1:]
    tier_words = set().union(*TIER_WORDS.values())
    while segs and segs[0] in tier_words:
        segs = segs[1:]
    return segs


def assign_tiers(tokens: list[Token], cfg: Config) -> None:
    for t in tokens:
        segs = [s.lower() for s in t.path]
        if cfg.prefix and segs and segs[0] == cfg.prefix.lower():
            segs = segs[1:]
        tier = None
        # Structure = tier (course ch4): a `tier-1|2|3` directory in the source path is authoritative;
        # a `core/` directory without one holds shared tier-1 definitions.
        m = TIER_DIR_RE.search(t.tier_path)
        if m:
            tier = m.group(1)
        elif re.search(r"(?:^|[/\\])core[/\\]", t.tier_path) or t.tier_path.startswith("core/"):
            tier = "1"
        for tier_id, prefixes in ({} if tier else cfg.tier_prefixes).items():
            if any(".".join(segs).startswith(p.lower().rstrip(".") ) for p in prefixes):
                tier = tier_id
                break
        if tier is None and segs:
            for tier_id, words in TIER_WORDS.items():
                if segs[0] in words:
                    tier = tier_id
                    break
        if tier is None:
            if not t.is_alias():
                tier = "1"
            else:
                root = meaning_segments(t.path, cfg)[:1]
                tier = "2" if root and root[0] in CATEGORY_ROOTS else "3"
        t.tier = tier


# ---------------------------------------------------------------- checks


def check_aliases(tokens: list[Token], cfg: Config) -> list[Finding]:
    by_name = {t.name: t for t in tokens}
    findings: list[Finding] = []
    for t in tokens:
        for ref in t.refs():
            target = by_name.get(ref)
            if target is None:
                findings.append(Finding("TA001", t.name, f"alias {{{ref}}} does not resolve", t.source))
                continue
            if t.tier == "1":
                findings.append(Finding("TA003", t.name, f"tier-1 definition aliases {{{ref}}}; definitions hold raw values", t.source))
            elif t.tier == "2" and target.tier == "3":
                findings.append(Finding("TA005", t.name, f"tier-2 token points up to tier-3 {{{ref}}}", t.source))
            elif t.tier == "3" and target.tier == "1" and not cfg.tier3_may_alias_tier1:
                findings.append(Finding("TA005", t.name, f"tier-3 token aliases tier-1 {{{ref}}}; this system requires tier 2", t.source))
        if t.tier in {"2", "3"} and not t.is_alias():
            findings.append(Finding("TA004", t.name, f"tier-{t.tier} token holds a raw value; tiers 2–3 must alias a definition (course ch2/ch8)", t.source))
        if cfg.require_type and not t.type:
            findings.append(Finding("TA012", t.name, "missing $type", t.source))

    # cycles
    graph = {t.name: [r for r in t.refs() if r in by_name] for t in tokens}
    state: dict[str, int] = {}
    reported: set[frozenset[str]] = set()

    def dfs(n: str, stack: list[str]) -> None:
        state[n] = 1
        stack.append(n)
        for m in graph.get(n, []):
            if state.get(m) == 1:
                cyc = stack[stack.index(m):]
                key = frozenset(cyc)
                if key not in reported:
                    reported.add(key)
                    findings.append(Finding("TA002", n, "alias cycle: " + " → ".join(cyc + [m]), by_name[n].source))
            elif state.get(m) is None:
                dfs(m, stack)
        stack.pop()
        state[n] = 2

    for n in graph:
        if state.get(n) is None:
            dfs(n, [])
    return findings


def check_budget(tokens: list[Token], cfg: Config) -> list[Finding]:
    if not tokens:
        return []
    t3 = [t for t in tokens if t.tier == "3"]
    share = len(t3) / len(tokens)
    if share > cfg.tier3_max_share:
        return [Finding(
            "TA006", "(system)",
            f"tier-3 share {share:.0%} ({len(t3)}/{len(tokens)}) exceeds {cfg.tier3_max_share:.0%}; "
            "component tokens should earn their place (heavily variable components, component "
            "categories, special cases) — move the rest to tier 2",
        )]
    return []


def check_naming(tokens: list[Token], cfg: Config) -> list[Finding]:
    findings: list[Finding] = []
    size_forms: dict[tuple[str, str], dict[str, list[str]]] = {}
    styles: dict[str, list[str]] = {}
    for t in tokens:
        segs = meaning_segments(t.path, cfg)
        words = [w for s in segs for w in re.split(r"[-_]", s) if w]
        for w in words:
            if w in cfg.abbreviations and cfg.abbreviations[w] and w not in cfg.allow_abbreviations:
                findings.append(Finding("TA007", t.name, f"abbreviation `{w}` — spell it out (`{cfg.abbreviations[w]}`)", t.source))
            for pair in SIZE_SYNONYMS:
                if w in pair:
                    size_forms.setdefault(pair, {}).setdefault(w, []).append(t.name)
        for s in t.path:
            style = "camel" if re.search(r"[a-z][A-Z]", s) else "snake" if "_" in s else "kebab" if "-" in s else None
            if style:
                styles.setdefault(style, []).append(t.name)
        if t.tier == "2" and segs and segs[0] in {"color", "colour"} and len(segs) > 1:
            prop = segs[1]
            allowed = cfg.color_buckets | COLOR_PROPERTY_OPTIONAL
            if prop not in allowed:
                findings.append(Finding(
                    "TA009", t.name,
                    f"tier-2 colour property `{prop}` is not a bucket ({', '.join(sorted(cfg.color_buckets))}); "
                    "order is category → property → variant → state",
                    t.source,
                ))
    for pair, forms in size_forms.items():
        if len(forms) > 1:
            eg = "; ".join(f"`{w}` e.g. {names[0]}" for w, names in forms.items())
            findings.append(Finding("TA008", "(system)", f"mixed size vocabulary {pair}: {eg} — pick one"))
    if len(styles) > 1:
        eg = "; ".join(f"{k} e.g. {v[0]}" for k, v in styles.items())
        findings.append(Finding("TA011", "(system)", f"mixed segment casing/separators: {eg}"))
    return findings


def check_themes(theme_paths: list[str], cfg: Config) -> list[Finding]:
    apis: dict[str, set[str]] = {}
    for p in theme_paths:
        toks = load_tokens([p])  # a theme may be one file or a directory of tier files
        assign_tiers(toks, cfg)
        apis[p] = {".".join(meaning_segments(t.path, cfg)) for t in toks if t.tier in {"2", "3"}}
    union = set().union(*apis.values()) if apis else set()
    findings: list[Finding] = []
    for p, api in apis.items():
        for missing in sorted(union - api):
            findings.append(Finding("TA013", missing, "theme does not define this tier-2/3 token other themes expose", p))
    return findings


def normalize_for_parity(t: Token, cfg: Config) -> str | None:
    segs = meaning_segments(t.path, cfg)
    if not segs:
        return None
    while len(segs) > 1 and segs[-1] == "default":  # Figma cannot have unnamed defaults
        segs = segs[:-1]
    return "-".join(re.sub(r"[_\s]+", "-", s) for s in segs)


def check_parity(figma_path: str, code_path: str, cfg: Config) -> list[Finding]:
    fig = load_tokens([figma_path])
    code = load_tokens([code_path])
    exempt = CODE_ONLY_ROOTS | FIGMA_ONLY_ROOTS

    def names(tokens: list[Token]) -> set[str]:
        # Exempt by the first *meaning segment* — the hyphen-joined name would split `z-index` and would
        # wrongly exempt components such as `media-card` or `layer-panel`.
        return {n for t in tokens
                if (n := normalize_for_parity(t, cfg)) and meaning_segments(t.path, cfg)[0] not in exempt}

    fig_names, code_names = names(fig), names(code)
    # Vocabulary: [[cross-surface-token-parity]] (MATCH / ALIGNED / DEVIATE / FIGMA-ONLY). Names that survive
    # normalisation are MATCH-or-ALIGNED by construction (prefix, named `default` = ALIGNED); code-only
    # categories are excluded by design, so only true one-sided gaps are reported.
    findings = [Finding("TA014", n, "FIGMA-ONLY (gap): in Figma, not in code", figma_path) for n in sorted(fig_names - code_names)]
    findings += [Finding("TA014", n, "CODE-ONLY (gap): in code, not in Figma", code_path) for n in sorted(code_names - fig_names)]
    return findings


def check_css(css_paths: list[str], tokens: list[Token], cfg: Config) -> list[Finding]:
    tier1_vars = set()
    for t in tokens:
        # Tier-1 spacing (on the grid) and z-index (a ramp) are consumed directly (course ch3/ch4);
        # colour/type/radius/shadow/motion are not.
        if t.tier == "1" and meaning_segments(t.path, cfg)[:1] not in (["spacing"], ["space"], ["z-index"], ["zindex"]):
            base = "-".join(t.path)
            tier1_vars.add(base.lower())
            if cfg.prefix:
                tier1_vars.add(f"{cfg.prefix}-{base}".lower())
    files: list[Path] = []
    for p in css_paths:
        pp = Path(p)
        if pp.is_dir():
            # Specimen/docs tooling (.storybook, docs) renders raw values on purpose; build output isn't source.
            files.extend(f for f in sorted(pp.rglob("*.css")) + sorted(pp.rglob("*.scss"))
                         if not any(part.startswith(".") or part in SKIP_DIRS | {"docs"} for part in f.relative_to(pp).parts[:-1]))
        else:
            files.append(pp)
    findings: list[Finding] = []
    for f in files:
        try:
            text = f.read_text(errors="replace")
        except OSError as e:
            raise BadInput(f"cannot read {f}: {e}") from e
        text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
        if f.suffix in (".scss", ".sass"):
            # Sass line comments; the lookbehind keeps `url(//cdn…)`, `http://` and quoted `//` intact.
            text = re.sub(r"(\"(?:\\.|[^\"\\\n])*\"|'(?:\\.|[^'\\\n])*'|url\([^)]*\))|//[^\n]*",
                          lambda m: m.group(1) or "", text)
        for prop, value in CSS_DECL_RE.findall(text):
            if prop.startswith("--"):
                continue  # token definitions themselves are allowed to hold values
            value = value.strip()
            uses_token = "var(" in value or bool(SCSS_VAR_RE.search(value))
            if prop in TYPOGRAPHY_PROPS and not uses_token and value not in CSS_KEYWORDS:
                findings.append(Finding("TA017", f"{f}:{prop}", f"stray typography literal `{value}` — use a composite (mixin/class) or a tier-3 typography token", str(f)))
            # urls, strings and Sass map lookups (`map-get($m, red)`) carry names, not colours
            plain = re.sub(r"url\([^)]*\)|\"[^\"]*\"|'[^']*'|\b(?:map-get|map\.get)\([^)]*\)", "", value)
            if CSS_COLOR_LITERAL_RE.search(value) or (COLOR_PROPS_RE.match(prop) and CSS_NAMED_COLOR_RE.search(plain)):
                findings.append(Finding("TA015", f"{f}:{prop}", f"raw colour literal `{value}` in component CSS — consume a tier-2/3 token", str(f)))
            for sigil, var in [("--", v) for v in CSS_VAR_RE.findall(value)] + [("$", v) for v in SCSS_VAR_RE.findall(value)]:
                if var.lower() in tier1_vars:
                    findings.append(Finding("TA016", f"{f}:{prop}", f"component consumes tier-1 definition `{sigil}{var}` — give it a job (tier 2) first", str(f)))
            bare = SCSS_VAR_RE.sub("", re.sub(r"var\([^)]*\)", "", value))
            bare = re.sub(r"(?<![\w.-])-?0(?:\.0+)?(?:px|rem|em|ms|s)?\b", "", bare)  # zero needs no token
            if prop in DIMENSION_PROPS and LITERAL_DIMENSION_RE.search(bare):
                findings.append(Finding("TA020", f"{f}:{prop}", f"hard-coded `{value}` — spacing/radius/shadow/motion/z-index come from tokens", str(f)))
        findings += knockout_findings(text, str(f))
    return findings


def knockout_findings(text: str, source: str) -> list[Finding]:
    """Knockout surfaces carry knockout content on the SAME COMPONENT (course ch6). Judged per stylesheet:
    component CSS commonly paints the knockout background on a container and sets knockout content on
    its own children elsewhere in the file (`.x--inverted &` context rules, icon fills, nav links) — a
    per-rule check misfires on that correct pattern (calibrated on the course demo, 2026-09-24). Only
    background properties count as a knockout *background* (a knockout token used as an SVG `fill` is
    not one)."""
    bg_rules: list[str] = []
    decls = list(CSS_DECL_RE.finditer(text))
    stack: list[str] = []
    di = 0
    for i, ch in enumerate(text + "\0"):
        while di < len(decls) and decls[di].start() <= i:  # attribute each declaration to its innermost selector
            prop, value = decls[di].group(1), decls[di].group(2)
            names = [v.lower() for v in CSS_VAR_RE.findall(value) + SCSS_VAR_RE.findall(value)]
            if prop.startswith("background") and any(KO_BACKGROUND_RE.search(v) for v in names):
                bg_rules.append(stack[-1] if stack else "(root)")
            di += 1
        if ch == "{":
            start = max(text.rfind(c, 0, i) for c in "{};") + 1
            stack.append(" ".join(text[start:i].split()))
        elif ch == "}" and stack:
            stack.pop()
    used = [v.lower() for v in CSS_VAR_RE.findall(text) + SCSS_VAR_RE.findall(text)]
    if bg_rules and not any(KO_CONTENT_RE.search(v) for v in used):
        return [Finding("TA018", f"{source}:{bg_rules[0]}",
                        f"knockout background on {len(bg_rules)} rule(s) but no knockout content colour anywhere in "
                        "this component's stylesheet", source)]
    return []


def output_names(path: Path) -> set[str]:
    """Token names a build output exposes, normalised (case, separators, `--`/`$` sigils) for cross-format comparison."""
    try:
        text = path.read_text(errors="replace")
        data = json.loads(text) if path.suffix == ".json" else None
    except (OSError, ValueError) as e:
        raise BadInput(f"cannot read {path}: {e}") from e
    if path.suffix == ".json":
        names: set[str] = set()

        def walk(node: object, trail: tuple[str, ...]) -> None:
            if isinstance(node, dict) and not any(k in node for k in ("$value", "value")):
                for k, v in node.items():
                    if not k.startswith("$"):
                        walk(v, trail + (k,))
            else:
                names.add("-".join(trail))

        walk(data, ())
    elif path.suffix == ".scss":
        names = set(re.findall(r"^\s*\$([\w-]+)\s*:", text, flags=re.M))
    else:
        names = set(re.findall(r"--([\w-]+)\s*:", text))
    return {re.sub(r"[^a-z0-9]", "", n.lower()) for n in names if n}


def check_outputs(paths: list[str]) -> list[Finding]:
    """Every platform output built from one source must expose the same token set (course ch6)."""
    sets = {p: output_names(Path(p)) for p in paths}
    union = set().union(*sets.values()) if sets else set()
    findings = []
    for p, names in sets.items():
        missing = sorted(union - names)
        if missing:
            findings.append(Finding("TA019", p, f"output lacks {len(missing)} token(s) other outputs expose, e.g. {', '.join(missing[:5])}", p))
    return findings


def check_override(parent_paths: list[str], child_paths: list[str], kind: str, cfg: Config) -> list[Finding]:
    """Child theme (dark / sub-brand / campaign) may only override existing parent names, in allowed categories."""
    parent = {".".join(meaning_segments(t.path, cfg)): t.value for t in load_tokens(parent_paths)}
    allow = OVERRIDE_ALLOW.get(kind)
    findings: list[Finding] = []
    for t in load_tokens(child_paths):
        name = ".".join(meaning_segments(t.path, cfg))
        if name not in parent:
            findings.append(Finding("TA021", name, f"{kind} override defines a token its parent theme does not have", t.source))
        elif parent[name] == t.value:
            continue  # a full-copy child (Figma-mode style) re-declares unchanged values; only changes are overrides
        segs = name.split(".")
        cat = segs[0] if segs else ""
        # Tier-3 names lead with the component (`link.color.content…`), so the category may sit anywhere.
        if allow is not None and not (set(segs) & allow) and not (
                "typography" in segs and "font-family" in segs and "font-family" in allow):
            findings.append(Finding("TA022", name, f"{kind} theme overrides category `{cat}`; allowed: {', '.join(sorted(allow))}", t.source))
    return findings


def _alpha(raw: str | None, pct: str | None) -> float:
    if raw is None:
        return 1.0
    return max(0.0, min(1.0, float(raw) / (100 if pct else 1)))


def parse_color(v: object) -> tuple[float, float, float, float] | None:
    """sRGB (r, g, b, alpha) in 0..1 from hex (3/4/6/8), rgb[a](), hsl[a]() or a DTCG colour object;
    None when the value is not a colour this tool can evaluate (named colours, other spaces)."""
    if isinstance(v, dict):  # DTCG 2025 colour object
        if isinstance(v.get("hex"), str) and v.get("colorSpace", "srgb") == "srgb" and "components" not in v:
            return parse_color(v["hex"])
        comps = v.get("components")
        if v.get("colorSpace", "srgb") == "srgb" and isinstance(comps, list) and len(comps) >= 3 \
                and all(isinstance(c, (int, float)) for c in comps[:3]):
            a = v.get("alpha", 1)
            return (float(comps[0]), float(comps[1]), float(comps[2]), float(a) if isinstance(a, (int, float)) else 1.0)
        return None
    if not isinstance(v, str):
        return None
    v = v.strip()
    m = re.fullmatch(r"#([0-9a-fA-F]{3,4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})", v)
    if m:
        h = m.group(1)
        if len(h) in (3, 4):
            h = "".join(c * 2 for c in h)
        a = int(h[6:8], 16) / 255 if len(h) == 8 else 1.0
        return (int(h[0:2], 16) / 255, int(h[2:4], 16) / 255, int(h[4:6], 16) / 255, a)
    num = r"(\d*\.?\d+)"
    m = re.fullmatch(rf"rgba?\(\s*{num}(%?)[\s,]+{num}(%?)[\s,]+{num}(%?)\s*(?:[,/]\s*{num}(%?))?\s*\)", v)
    if m:
        g = m.groups()
        ch = [float(g[i]) / (100 if g[i + 1] else 255) for i in (0, 2, 4)]
        return (ch[0], ch[1], ch[2], _alpha(g[6], g[7]))
    m = re.fullmatch(rf"hsla?\(\s*{num}(?:deg)?[\s,]+{num}%[\s,]+{num}%\s*(?:[,/]\s*{num}(%?))?\s*\)", v)
    if m:
        h, s_, lum = float(m.group(1)) % 360 / 360, float(m.group(2)) / 100, float(m.group(3)) / 100
        import colorsys
        r, g_, b = colorsys.hls_to_rgb(h, lum, s_)
        return (r, g_, b, _alpha(m.group(4), m.group(5)))
    return None


def _luminance(rgb: tuple[float, float, float]) -> float:
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast_ratio(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    la, lb = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def resolve(tokens: list[Token], cfg: Config) -> dict[str, object]:
    """Meaning-name → resolved raw value. Refs follow full token paths only — the same rule TA001 uses,
    so a ref the alias check calls broken never silently resolves here (unresolvable → None)."""
    by_full = {t.name: t for t in tokens}
    by_meaning = {".".join(meaning_segments(t.path, cfg)): t for t in tokens}
    out: dict[str, object] = {}
    for key, t in by_meaning.items():
        seen, cur = set(), t
        while cur is not None and isinstance(cur.value, str) and REF_RE.fullmatch(cur.value.strip()) and cur.name not in seen:
            seen.add(cur.name)
            cur = by_full.get(norm_ref(REF_RE.fullmatch(cur.value.strip()).group(1)))
        out[key] = None if cur is None or cur.name in seen else cur.value
    return out


def check_contrast(tokens: list[Token], cfg: Config, label: str = "") -> list[Finding]:
    """Tier-2 content-on-background pairs meet WCAG AA (4.5:1 default) in this theme (course ch8; a11y is not deferrable)."""
    values = resolve(tokens, cfg)
    where = f" in {label}" if label else ""
    findings: list[Finding] = []
    for fg, bg in cfg.contrast_pairs:
        if fg not in values or bg not in values:
            continue  # pair absent in this system
        if values[fg] is None or values[bg] is None:
            # --themes mode never runs the alias check on theme files, so this must not pass silently.
            findings.append(Finding("TA024", f"{fg} on {bg}", f"contrast unverifiable: alias does not resolve{where}", label))
            continue
        a, b = parse_color(values[fg]), parse_color(values[bg])
        if a is None or b is None or b[3] < 1:
            why = "translucent background (depends on what is beneath)" if b is not None and b[3] < 1 else "unsupported colour value"
            findings.append(Finding("TA024", f"{fg} on {bg}", f"contrast unverifiable: {why}{where}", label))
            continue
        # Translucent text is seen composited over its background.
        fg_rgb = tuple(a[3] * a[i] + (1 - a[3]) * b[i] for i in range(3))
        r = contrast_ratio(fg_rgb, b[:3])  # type: ignore[arg-type]
        if r < cfg.contrast_min:
            findings.append(Finding("TA023", f"{fg} on {bg}", f"contrast {r:.2f}:1 < {cfg.contrast_min}:1{where}", label))
    return findings


# ---------------------------------------------------------------- driver


def audit(paths: list[str], cfg: Config, themes: list[str] | None = None,
          parity: list[str] | None = None, css: list[str] | None = None,
          outputs: list[str] | None = None, override: tuple[list[str], list[str], str] | None = None,
          contrast: bool = False) -> tuple[list[Finding], dict]:
    tokens = load_tokens(paths) if paths else []
    assign_tiers(tokens, cfg)
    findings: list[Finding] = []
    findings += check_aliases(tokens, cfg)
    findings += check_budget(tokens, cfg)
    findings += check_naming(tokens, cfg)
    extra: dict = {}
    if themes:
        findings += check_themes(themes, cfg)
        extra["themes"] = {t: len(load_tokens([t])) for t in themes}
    if parity:
        findings += check_parity(parity[0], parity[1], cfg)
    if css:
        findings += check_css(css, tokens, cfg)
    if outputs:
        findings += check_outputs(outputs)
    if override:
        findings += check_override(*override, cfg)
    if contrast:
        if themes:
            for th in themes:
                findings += check_contrast(load_tokens((paths or []) + [th]), cfg, th)
        elif tokens:
            findings += check_contrast(tokens, cfg)
    counts = {tier: sum(1 for t in tokens if t.tier == tier) for tier in ("1", "2", "3")}
    return findings, {"tokens": len(tokens), "tiers": counts, **extra}


def report(findings: list[Finding], stats: dict, as_json: bool) -> None:
    if as_json:
        print(json.dumps({
            "stats": stats,
            "findings": [{"rule": f.rule, "level": f.level, "token": f.token, "message": f.message, "source": f.source} for f in findings],
        }, indent=2))
        return
    t = stats.get("tiers", {})
    print(f"token-audit: {stats.get('tokens', 0)} tokens · tier1 {t.get('1', 0)} · tier2 {t.get('2', 0)} · tier3 {t.get('3', 0)}")
    if stats.get("themes"):
        print("  themes: " + " · ".join(f"{k} {v}" for k, v in stats["themes"].items()))
    for f in sorted(findings, key=lambda x: (x.level != "error", x.rule, x.token)):
        print(f"  {f.level.upper():5} {f.rule} {f.token}: {f.message}")
    errs = sum(f.level == "error" for f in findings)
    print(f"{errs} error(s), {len(findings) - errs} warning(s)")


def self_test() -> int:
    import tempfile

    good = {
        "color": {
            "green": {"500": {"$value": "#00704a", "$type": "color"}},
            "neutral": {"0": {"$value": "#ffffff", "$type": "color"}, "900": {"$value": "#111111", "$type": "color"}},
        },
        "spacing": {"8": {"$value": "8px", "$type": "dimension"}},
        "theme": {
            "color": {
                "background": {"brand": {"$value": "{color.green.500}"}, "default": {"$value": "{color.neutral.0}"}},
                "content": {"default": {"$value": "{color.neutral.900}"}, "knockout": {"$value": "{color.neutral.0}"}},
                "border": {"default": {"$value": "{color.neutral.900}"}},
            },
        },
        "button": {"background": {"$value": "{theme.color.background.brand}"}},
    }
    bad = {
        "core": {"pink": {"$value": "{core.magenta}"}, "magenta": {"$value": "{core.pink}"}},
        "theme": {"color": {"bg": {"brand": {"$value": "#e20074"}}, "fill": {"lg": {"$value": "{core.nope}"}}},
                  "spacing": {"large": {"$value": "{core.pink}"}, "section-break": {"$value": "{core.pink}"}}},
        "btn": {"primaryBg": {"$value": "{core.pink}"}},
        "card": {"x": {"$value": "{core.pink}"}}, "chip": {"x": {"$value": "{core.pink}"}},
    }
    cfg = Config()
    failures: list[str] = []
    with tempfile.TemporaryDirectory() as d:
        g, b = Path(d, "good.json"), Path(d, "bad.json")
        g.write_text(json.dumps(good))
        b.write_text(json.dumps(bad))
        f_good, stats = audit([str(g)], cfg)
        if f_good:
            failures.append("clean fixture produced findings: " + "; ".join(f"{f.rule} {f.token}" for f in f_good))
        if stats["tiers"] != {"1": 4, "2": 5, "3": 1}:
            failures.append(f"tier inference wrong on clean fixture: {stats['tiers']}")
        f_bad, _ = audit([str(b)], cfg)
        rules = {f.rule for f in f_bad}
        for want in ("TA001", "TA002", "TA003", "TA004", "TA006", "TA007", "TA008", "TA009", "TA011"):
            if want not in rules:
                failures.append(f"violation fixture missed {want}")
        # themes: brand-b lacks one semantic token
        a, bb = Path(d, "a.json"), Path(d, "b.json")
        a.write_text(json.dumps(good))
        good_b = json.loads(json.dumps(good))
        del good_b["theme"]["color"]["border"]
        bb.write_text(json.dumps(good_b))
        f_th, _ = audit([], cfg, themes=[str(a), str(bb)])
        if not any(f.rule == "TA013" and f.token == "color.border.default" for f in f_th):
            failures.append("theme API drift not detected")
        # parity: code has ds- prefix + animation (sanctioned); Figma has named defaults + viewport
        fig = {"color": {"background": {"default": {"$value": "#fff"}}}, "viewport": {"mobile": {"$value": 375}},
               "typography": {"display": {"default": {"$value": "x"}}}}
        code = {"ds": {"color": {"background": {"default": {"value": "#fff"}}}, "typography": {"display": {"value": "x"}},
                       "animation": {"fade": {"value": "200ms"}}, "spacing": {"8": {"value": "8px"}}}}
        fp, cp = Path(d, "fig.json"), Path(d, "code.json")
        fp.write_text(json.dumps(fig))
        cp.write_text(json.dumps(code))
        f_par, _ = audit([], Config(prefix="ds"), parity=[str(fp), str(cp)])
        par = {(f.token, f.message) for f in f_par}
        if par != {("spacing-8", "CODE-ONLY (gap): in code, not in Figma")}:
            failures.append(f"parity normalization wrong: {sorted(par)}")
        # css: raw literal + tier-1 var flagged; tier-2 var allowed
        css = Path(d, "button.css")
        css.write_text(".b{background:var(--color-green-500);color:#fff;border-color:var(--theme-color-border-default);"
                       "padding:var(--spacing-8);font-size:14px;line-height:1;font-weight:var(--theme-button-font-weight);--local:#000;}"
                       ".k{background:var(--theme-color-background-knockout);border-radius:6px;margin:0;gap:calc(var(--spacing-8) * 2);"
                       "transition:opacity 0s var(--theme-animation-ease);}")
        f_css, _ = audit([str(g)], cfg, css=[str(css)])
        css_rules = sorted(f.rule for f in f_css)
        if css_rules != ["TA015", "TA016", "TA017", "TA018", "TA020"]:
            failures.append(f"css scan wrong: {css_rules}")
        # outputs: scss lacks one token the css + json expose
        o_css, o_scss, o_json = Path(d, "t.css"), Path(d, "_t.scss"), Path(d, "t.json")
        o_css.write_text(":root{--ds-color-brand:#f0f;--ds-spacing-8:8px;}")
        o_scss.write_text("$ds-color-brand: #f0f;\n")
        o_json.write_text(json.dumps({"ds": {"color": {"brand": {"value": "#f0f"}}, "spacing": {"8": {"value": "8px"}}}}))
        f_out, _ = audit([], cfg, outputs=[str(o_css), str(o_scss), str(o_json)])
        if [(f.rule, Path(f.token).name) for f in f_out] != [("TA019", "_t.scss")]:
            failures.append(f"output drift wrong: {[(f.rule, f.token) for f in f_out]}")
        # override: dark child may change colour/shadow names the parent has — not spacing, not new names
        par, kid = Path(d, "parent.json"), Path(d, "dark.json")
        par.write_text(json.dumps(good))
        kid.write_text(json.dumps({"theme": {"color": {"background": {"default": {"$value": "{color.neutral.900}"}}},
                                             "spacing": {"page": {"$value": "{spacing.8}"}}}}))
        f_ov, _ = audit([], cfg, override=([str(par)], [str(kid)], "dark"))
        if sorted(f.rule for f in f_ov) != ["TA021", "TA022"]:
            failures.append(f"override check wrong: {[(f.rule, f.token) for f in f_ov]}")
        # contrast: good fixture passes (#111 on #fff); a pale brand pair fails
        f_c, _ = audit([str(g)], cfg, contrast=True)
        if f_c:
            failures.append(f"contrast false positive: {[(f.token, f.message) for f in f_c]}")
        pale = json.loads(json.dumps(good))
        pale["color"]["neutral"]["900"]["$value"] = "#cccccc"
        pp = Path(d, "pale.json")
        pp.write_text(json.dumps(pale))
        f_c2, _ = audit([str(pp)], cfg, contrast=True)
        if not any(f.rule == "TA023" and f.token.startswith("color.content.default") for f in f_c2):
            failures.append("contrast failure not detected")
        # ---- regressions from the 2026-09-24 adversarial review (one case per confirmed finding) ----
        def css_rules_for(name: str, text: str, toks: list[str] | None = None, c: Config = cfg) -> list[str]:
            fpath = Path(d, name)
            fpath.write_text(text)
            return sorted(f.rule for f in audit(toks or [str(g)], c, css=[str(fpath)])[0] if f.rule.startswith("TA0") and f.source == str(fpath))

        # parity exempts by meaning segment: z-index is sanctioned; media-/layer- components are real gaps
        fp2, cp2 = Path(d, "fig2.json"), Path(d, "code2.json")
        fp2.write_text(json.dumps({"color": {"background": {"default": {"$value": "#fff"}}}}))
        cp2.write_text(json.dumps({"color": {"background": {"default": {"value": "#fff"}}},
                                   "z-index": {"modal": {"value": 500}},
                                   "media-card": {"color": {"background": {"value": "{color.background.default}"}}},
                                   "layer-panel": {"color": {"border": {"value": "{color.background.default}"}}}}))
        got = sorted(f.token for f in audit([], cfg, parity=[str(fp2), str(cp2)])[0])
        if got != ["layer-panel-color-border", "media-card-color-background"]:
            failures.append(f"parity exemption wrong: {got}")
        # declarations without a trailing semicolon (last in block, minified)
        if css_rules_for("nosemi.css", ".x{color:#f00}.y{padding:12px}") != ["TA015", "TA020"]:
            failures.append("declaration without trailing ';' not scanned")
        # knockout pairing is per component stylesheet: content on children elsewhere in the file passes;
        # a knockout token used as a `fill` is not a background; a stylesheet with no knockout content fails
        ko = ("--theme-color-background-knockout", "--theme-color-content-knockout")
        paired = (f".hdr--inverted{{background:var(--theme-color-background-brand-knockout);}}"
                  f".nav{{.hdr--inverted &{{color:var({ko[1]});}}}}"
                  f".logo{{.hdr--inverted &{{fill:var({ko[0]});}}}}")
        unpaired = (f".promo{{background:var({ko[0]});.title{{font-weight:var(--x);}}"
                    f"@media (min-width: 40em){{padding:var(--spacing-8);}}}}")
        fill_only = f".icon{{fill:var({ko[0]});}}"
        got = [css_rules_for(n, t) for n, t in (("paired.scss", paired), ("unpaired.scss", unpaired), ("fill.scss", fill_only))]
        if got != [[], ["TA018"], []]:
            failures.append(f"knockout pairing wrong: {got}")
        # negative dimensions, animation shorthand and bare z-index integers are literals; zero is not
        if css_rules_for("dims.css", ".a{margin-top:-8px;animation:spin 2s;z-index:5;margin:-0px;}") != ["TA020", "TA020", "TA020"]:
            failures.append("negative / animation / z-index literals not flagged")
        # Sass: // comments ignored, $token counts as token use, tier-1 $vars caught
        sass = "// .x { color: #f00; }\n.a{font-size:$ds-theme-body-size;color:$ds-color-neutral-900;}"
        if css_rules_for("v.scss", sass, c=Config(prefix="ds")) != ["TA016"]:
            failures.append("sass comments / variables handled wrong")
        # named colours in colour properties only; urls, strings and token names are not colours
        named = (".a{color:white;}.b{background:url(red.png);}.c{color:var(--ds-color-red);}"
                 ".d{font-family:\"Navy Sans\";}.e{transition:color 0s;}")
        # `white` is a colour (TA015); the quoted "Navy Sans" is not — it is only a stray font literal (TA017)
        if css_rules_for("named.css", named) != ["TA015", "TA017"]:
            failures.append("named-colour detection wrong")
        # Style Dictionary `{a.b.value}` refs resolve
        sd = Path(d, "sd.json")
        sd.write_text(json.dumps({"color": {"base": {"value": "#fff"}, "font": {"value": "{color.base.value}"}}}))
        if any(f.rule == "TA001" for f in audit([str(sd)], cfg)[0]):
            failures.append("Style Dictionary .value ref reported unresolved")
        # an ancestor named build/ must not hide a directory's tokens; an empty directory is bad input
        bdir = Path(d, "build", "tokens")
        bdir.mkdir(parents=True)
        (bdir / "t.json").write_text(json.dumps(good))
        if audit([str(bdir)], cfg)[1]["tokens"] != 10:
            failures.append("directory under a build/ ancestor loaded no tokens")
        Path(d, "empty").mkdir()
        # an unrelated `core` ancestor must not force tier 1
        cdir = Path(d, "packages", "core", "tokens")
        cdir.mkdir(parents=True)
        (cdir / "tokens.json").write_text(json.dumps(good))
        for arg in (str(cdir / "tokens.json"), str(cdir)):
            fs, st = audit([arg], cfg)
            if any(f.rule == "TA003" for f in fs) or st["tiers"] != {"1": 4, "2": 5, "3": 1}:
                failures.append(f"core ancestor forced tier 1 for {Path(arg).name}: {st['tiers']}")
        core_dir = Path(d, "core")
        core_dir.mkdir()
        (core_dir / "c.json").write_text(json.dumps({"brand": {"$value": "{x.y}"}}))
        if audit([str(core_dir)], cfg)[1]["tiers"]["1"] != 1:
            failures.append("core/ directory argument no longer tier 1")
        # contrast: translucent text composited, DTCG colour objects parsed, unparseable reported
        def contrast_rules(fg: object) -> list[str]:
            t = json.loads(json.dumps(good))
            t["color"]["neutral"]["900"]["$value"] = fg
            cp_ = Path(d, "c.json")
            cp_.write_text(json.dumps(t))
            return sorted({f.rule for f in audit([str(cp_)], cfg, contrast=True)[0] if f.rule in ("TA023", "TA024")})
        for fg, want in (("rgba(17, 17, 17, 0.2)", ["TA023"]), ("#11111133", ["TA023"]),
                         ({"colorSpace": "srgb", "components": [0.8, 0.8, 0.8]}, ["TA023"]),
                         ("hsl(0, 0%, 7%)", []), ("hsl(0 0% 85%)", ["TA023"]), ("black", ["TA024"])):
            got = contrast_rules(fg)
            if got != want:
                failures.append(f"contrast for {fg!r}: {got} != {want}")
        # a meaning-name ref is broken for TA001 AND unresolved for contrast (no silent resolution)
        mn = json.loads(json.dumps(good))
        mn["theme"]["color"]["content"]["default"]["$value"] = "{color.background.default}"
        mp = Path(d, "mn.json")
        mp.write_text(json.dumps(mn))
        fs = audit([str(mp)], cfg, contrast=True)[0]
        if not any(f.rule == "TA001" for f in fs) or any(f.rule == "TA023" for f in fs):
            failures.append("meaning-name ref: alias and contrast checks disagree")
        # same-named theme files keep distinct stats
        t1, t2 = Path(d, "ta", "tokens.json"), Path(d, "tb", "tokens.json")
        for tp in (t1, t2):
            tp.parent.mkdir()
            tp.write_text(json.dumps(good))
        if len(audit([], cfg, themes=[str(t1), str(t2)])[1]["themes"]) != 2:
            failures.append("same-named theme files collapsed in stats")
        # campaign overrides are cosmetic like sub-brands
        if not any(f.rule == "TA022" for f in audit([], cfg, override=([str(par)], [str(kid)], "campaign"))[0]):
            failures.append("campaign override categories unchecked")
        # bad input exits 2, never 1; --override needs --parent
        badj = Path(d, "bad-input.json")
        badj.write_text("{not json")
        arr = Path(d, "arr.json")
        arr.write_text("[1, 2]")
        import contextlib
        import io
        # verification round (2026-09-24): getters are not literals; typed tier-N folders count; broken
        # aliases in theme contrast are reported; strings/urls survive `//` stripping; malformed numbers
        # and bad config values are handled; map keys named like colours are not colours
        getters = (".x{color:theme-color(primary);background:mat-color($p, 500);border-color:ds-color(border);}"
                   ".y{color:map-get($brand, red);background:url(\"//cdn.example.com/a.png\");padding:var(--spacing-8);}")
        if css_rules_for("getters.scss", getters) != []:
            failures.append(f"getter / map / url false positive: {css_rules_for('getters.scss', getters)}")
        nested_t2 = Path(d, "typed", "tier-2", "color", "x.json")
        nested_t2.parent.mkdir(parents=True)
        nested_t2.write_text(json.dumps({"color": {"background": {"default": {"$value": "#fff"}}}}))
        if not any(f.rule == "TA004" for f in audit([str(nested_t2)], cfg)[0]):
            failures.append("file below a typed tier-2 folder lost its tier")
        core_t, theme_t = Path(d, "tcore.json"), Path(d, "tlight.json")
        core_t.write_text(json.dumps({"core": {"white": {"$value": "#fff"}, "grey": {"$value": "#777"}}}))
        theme_t.write_text(json.dumps({"theme": {"color": {"content": {"default": {"$value": "{color.grey}"}},
                                                           "background": {"default": {"$value": "{core.white}"}}}}}))
        if not any(f.rule == "TA024" for f in audit([str(core_t)], cfg, themes=[str(theme_t)], contrast=True)[0]):
            failures.append("broken alias in a theme passed contrast silently")
        if contrast_rules("rgb(1.2.3, 0, 0)") != ["TA024"]:
            failures.append("malformed rgb() not reported as unverifiable")
        bad_cfg = Path(d, "badcfg.json")
        for cfg_text in ('{"tier3_max_share": "abc"}', '{"contrast_pairs": 5}', '{"tier_prefixes": ["core"]}'):
            bad_cfg.write_text(cfg_text)
            with contextlib.redirect_stderr(io.StringIO()):
                if main(["--config", str(bad_cfg), str(g)]) != 2:
                    failures.append(f"bad config {cfg_text} did not exit 2")

        for argv in ([str(badj)], [str(arr)], [str(Path(d, "empty"))], ["--override", str(kid)]):
            with contextlib.redirect_stderr(io.StringIO()):
                try:
                    rc = main(argv)
                except SystemExit as e:
                    rc = e.code
            if rc != 2:
                failures.append(f"bad input {argv[-1]} exited {rc}, expected 2")
    if failures:
        for x in failures:
            print("self-test FAIL:", x, file=sys.stderr)
        return 1
    print("OK token-audit self-test")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", help="token JSON files (DTCG or Style Dictionary)")
    ap.add_argument("--config", help="JSON config: prefix, tier_prefixes (dotted token-name prefixes; used only when the path has no tier-N/core directory), tier3_max_share, tier3_may_alias_tier1, abbreviations, allow_abbreviations, color_buckets, require_type, contrast_pairs (list of [fg, bg]; extends the defaults), contrast_min (WCAG ratio, default 4.5)")
    ap.add_argument("--prefix", help="global code namespace (e.g. ds) — stripped before analysis")
    ap.add_argument("--themes", nargs="+", help="ROOT theme files/dirs that must expose the same tier-2/3 API (skinny child themes → --parent/--override)")
    ap.add_argument("--parity", nargs=2, metavar=("FIGMA_JSON", "CODE_JSON"))
    ap.add_argument("--css", nargs="+", help="component CSS/SCSS files or dirs to scan for raw values / tier-1 use")
    ap.add_argument("--outputs", nargs="+", help="built platform outputs (.css/.scss/.json) that must expose the same token set")
    ap.add_argument("--override", nargs="+", metavar="PATH", help="child theme files/dirs to check against --parent")
    ap.add_argument("--parent", nargs="+", metavar="PATH", help="parent theme files/dirs for --override")
    ap.add_argument("--kind", choices=["dark", "sub-brand", "campaign"], default="dark", help="override kind (category allowlist)")
    ap.add_argument("--contrast", action="store_true", help="WCAG contrast of tier-2 content/background pairs (per --themes theme, with positional paths as shared core)")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--strict", action="store_true", help="warnings fail too")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args(argv)
    if a.self_test:
        return self_test()
    if bool(a.override) != bool(a.parent):
        ap.error("--override and --parent must be given together")  # exits 2
    if not (a.paths or a.themes or a.parity or a.outputs or a.css or a.override):
        ap.print_usage(sys.stderr)
        return 2
    try:
        cfg = Config.load(a.config)
        if a.prefix:
            cfg.prefix = a.prefix
        override = (a.parent, a.override, a.kind) if a.override else None
        findings, stats = audit(a.paths, cfg, themes=a.themes, parity=a.parity, css=a.css, outputs=a.outputs,
                                override=override, contrast=a.contrast)
    except BadInput as e:
        print(f"token-audit: {e}", file=sys.stderr)
        return 2
    report(findings, stats, a.json)
    if any(f.level == "error" for f in findings) or (a.strict and findings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
