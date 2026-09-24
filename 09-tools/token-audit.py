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
  themes     every theme exposes the same tier-2 + tier-3 API (components depend on it)
  parity     Figma vs code token names match once the sanctioned divergences are removed
             (code-only prefix, Figma's named `default`, code-only animation/z-index/breakpoint,
             Figma-only viewport)
  css        component CSS consumes tier 2/3 only — no raw colour literals, no tier-1 vars
             (tier-1 spacing is exempt), no stray typography literals (use composites), no
             hard-coded spacing/radius/shadow/motion/z-index, knockout bg ⇒ knockout content
  outputs    every platform output (CSS/SCSS/JSON) built from one source exposes the same names
  override   a child theme (dark / sub-brand / campaign) only overrides names its parent has, and only
             allowed categories (dark: colour + shadow; sub-brand: colour, font-family, radius)
  contrast   tier-2 content-on-background pairs meet WCAG 4.5:1 in every theme (a11y is not deferrable)

Input: DTCG (`$value`/`$type`) or Style Dictionary (`value`) JSON, nested groups; files or directories
(build/dist/node_modules skipped). Tier resolution, first match wins: a `tier-1|2|3` directory in the
file path (structure = tier) · a `core/` directory → 1 · `--config` `tier_prefixes` · inference (raw
value → 1; alias under a category root → 2; alias under anything else, e.g. `button.*` → 3).

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

Exit: 0 clean (warnings allowed) · 1 errors (or warnings with --strict) · 2 bad input.
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
CSS_COLOR_LITERAL_RE = re.compile(r"#[0-9a-fA-F]{3,8}\b|\b(?:rgba?|hsla?|oklch|oklab|lab|lch)\(")
CSS_DECL_RE = re.compile(r"([a-zA-Z-]+)\s*:\s*([^;{}]+);")
# Typography comes from composite bundles; a literal on one of these in component CSS is a stray.
TYPOGRAPHY_PROPS = {"font-size", "font-weight", "font-family", "line-height", "letter-spacing"}
CSS_KEYWORDS = {"inherit", "initial", "unset", "revert", "normal", "1", "0"}  # line-height:1 trims text boxes
# Non-colour visual decisions that must come from tokens in component CSS (course ch6: "no literal values").
DIMENSION_PROPS = {
    "padding", "padding-top", "padding-right", "padding-bottom", "padding-left", "padding-inline",
    "padding-block", "margin", "margin-top", "margin-right", "margin-bottom", "margin-left",
    "margin-inline", "margin-block", "gap", "row-gap", "column-gap", "border-radius", "border-width",
    "box-shadow", "transition", "transition-duration", "animation-duration", "z-index",
}
LITERAL_DIMENSION_RE = re.compile(r"(?<![\w-])(?:\d*\.?\d+)(?:px|rem|em|ms|s)\b|^\s*\d{2,}\s*$")
CSS_RULE_RE = re.compile(r"([^{}]+)\{([^{}]*)\}")

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
# Tier-2 content-on-background pairs checked for WCAG contrast when both exist (config `contrast_pairs` extends).
DEFAULT_CONTRAST_PAIRS = [
    ("color.content.default", "color.background.default"),
    ("color.content.subtle", "color.background.default"),
    ("color.content.knockout", "color.background.knockout"),  # knockout content pairs with knockout bg (ch6),
    # not with `background-brand` — brand backgrounds are often pale tints carrying default content.
    ("color.content.brand", "color.background.default"),
]


@dataclass
class Token:
    path: tuple[str, ...]
    value: object
    type: str | None
    source: str
    tier: str = "?"

    @property
    def name(self) -> str:
        return ".".join(self.path)

    def refs(self) -> list[str]:
        out: list[str] = []

        def walk(v: object) -> None:
            if isinstance(v, str):
                out.extend(m.strip() for m in REF_RE.findall(v))
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
        raw = json.loads(Path(path).read_text())
        cfg.prefix = raw.get("prefix", cfg.prefix)
        cfg.tier_prefixes = {str(k): list(v) for k, v in raw.get("tier_prefixes", {}).items()}
        cfg.tier3_max_share = float(raw.get("tier3_max_share", cfg.tier3_max_share))
        cfg.tier3_may_alias_tier1 = bool(raw.get("tier3_may_alias_tier1", cfg.tier3_may_alias_tier1))
        cfg.abbreviations.update(raw.get("abbreviations", {}))
        cfg.allow_abbreviations = set(raw.get("allow_abbreviations", []))
        cfg.color_buckets = set(raw.get("color_buckets", sorted(cfg.color_buckets)))
        cfg.require_type = bool(raw.get("require_type", cfg.require_type))
        cfg.contrast_pairs += [tuple(x) for x in raw.get("contrast_pairs", [])]
        cfg.contrast_min = float(raw.get("contrast_min", cfg.contrast_min))
        return cfg


# ---------------------------------------------------------------- loading


def flatten(data: dict, source: str, path: tuple[str, ...] = (), inherited_type: str | None = None) -> list[Token]:
    tokens: list[Token] = []
    group_type = data.get("$type", inherited_type) if isinstance(data, dict) else inherited_type
    for key, node in data.items():
        if key.startswith("$") or not isinstance(node, dict):
            continue
        if "$value" in node or "value" in node:
            val = node.get("$value", node.get("value"))
            tokens.append(Token(path + (key,), val, node.get("$type", node.get("type", group_type)), source))
        else:
            tokens.extend(flatten(node, source, path + (key,), group_type))
    return tokens


SKIP_DIRS = {"node_modules", "build", "dist", ".git", "__MACOSX"}
TIER_DIR_RE = re.compile(r"(?:^|[/\\])tier[-_ ]?([123])\b", re.I)


def expand(paths: list[str]) -> list[str]:
    """Files as given; directories → their token JSON (build output and vendored dirs skipped)."""
    out: list[str] = []
    for p in paths:
        pp = Path(p)
        if pp.is_dir():
            out.extend(str(f) for f in sorted(pp.rglob("*.json"))
                       if not SKIP_DIRS & set(f.parts) and not f.name.startswith(("package", "tsconfig", ".")))
        else:
            out.append(p)
    return out


def load_tokens(paths: list[str]) -> list[Token]:
    out: list[Token] = []
    for p in expand(paths):
        try:
            data = json.loads(Path(p).read_text())
        except (OSError, json.JSONDecodeError) as e:
            raise SystemExit(f"token-audit: cannot read {p}: {e}")
        out.extend(flatten(data, p))
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
        m = TIER_DIR_RE.search(t.source)
        if m:
            tier = m.group(1)
        elif re.search(r"(?:^|[/\\])core[/\\]", t.source):
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
    fig_names = {n for t in fig if (n := normalize_for_parity(t, cfg)) and t.path[0].lower() not in FIGMA_ONLY_ROOTS}
    code_names = {n for t in code if (n := normalize_for_parity(t, cfg))}
    code_names = {n for n in code_names if n.split("-")[0] not in CODE_ONLY_ROOTS | FIGMA_ONLY_ROOTS}
    fig_names = {n for n in fig_names if n.split("-")[0] not in CODE_ONLY_ROOTS | FIGMA_ONLY_ROOTS}
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
        text = f.read_text(errors="replace")
        text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
        for prop, value in CSS_DECL_RE.findall(text):
            if prop.startswith("--"):
                continue  # token definitions themselves are allowed to hold values
            if prop in TYPOGRAPHY_PROPS and "var(" not in value and value.strip() not in CSS_KEYWORDS:
                findings.append(Finding("TA017", f"{f}:{prop}", f"stray typography literal `{value.strip()}` — use a composite (mixin/class) or a tier-3 typography token", str(f)))
            if CSS_COLOR_LITERAL_RE.search(value):
                findings.append(Finding("TA015", f"{f}:{prop}", f"raw colour literal `{value.strip()}` in component CSS — consume a tier-2/3 token", str(f)))
            for var in CSS_VAR_RE.findall(value):
                if var.lower() in tier1_vars:
                    findings.append(Finding("TA016", f"{f}:{prop}", f"component consumes tier-1 definition `--{var}` — give it a job (tier 2) first", str(f)))
            bare = re.sub(r"var\([^)]*\)", "", value)
            bare = re.sub(r"(?<![\w.-])0(?:\.0+)?(?:px|rem|em|ms|s)?\b", "", bare)  # zero needs no token
            if prop in DIMENSION_PROPS and LITERAL_DIMENSION_RE.search(bare):
                findings.append(Finding("TA020", f"{f}:{prop}", f"hard-coded `{value.strip()}` — spacing/radius/shadow/motion/z-index come from tokens", str(f)))
        # Knockout backgrounds and knockout content travel together (course ch6).
        for selector, body in CSS_RULE_RE.findall(text):
            uses = [v.lower() for v in CSS_VAR_RE.findall(body)]
            if any("background-knockout" in v for v in uses) and not any("content-knockout" in v for v in uses):
                sel = re.split(r"[;}]", selector)[-1].strip()
                findings.append(Finding("TA018", f"{f}:{sel}", "knockout background without a knockout content colour in the same rule", str(f)))
    return findings


def output_names(path: Path) -> set[str]:
    """Token names a build output exposes, normalised (case, separators, `--`/`$` sigils) for cross-format comparison."""
    text = path.read_text(errors="replace")
    if path.suffix == ".json":
        data = json.loads(text)
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


def _hex_rgb(v: object) -> tuple[float, float, float] | None:
    if not isinstance(v, str):
        return None
    v = v.strip()
    m = re.fullmatch(r"#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})(?:[0-9a-fA-F]{2})?", v)
    if m:
        h = m.group(1)
        h = "".join(c * 2 for c in h) if len(h) == 3 else h
        return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))  # type: ignore[return-value]
    m = re.fullmatch(r"rgba?\(\s*(\d+)[ ,]+(\d+)[ ,]+(\d+).*\)", v)
    if m:
        return tuple(int(x) / 255 for x in m.groups())  # type: ignore[return-value]
    return None


def _luminance(rgb: tuple[float, float, float]) -> float:
    lin = [c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]


def contrast_ratio(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    la, lb = sorted((_luminance(a), _luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def resolve(tokens: list[Token], cfg: Config) -> dict[str, object]:
    """Meaning-name → resolved raw value (alias chains followed; unresolvable → None)."""
    by_full = {t.name: t for t in tokens}
    by_meaning = {".".join(meaning_segments(t.path, cfg)): t for t in tokens}
    out: dict[str, object] = {}
    for key, t in by_meaning.items():
        seen, cur = set(), t
        while cur is not None and isinstance(cur.value, str) and REF_RE.fullmatch(cur.value.strip()) and cur.name not in seen:
            seen.add(cur.name)
            ref = REF_RE.fullmatch(cur.value.strip()).group(1)
            cur = by_full.get(ref) or by_meaning.get(".".join(meaning_segments(tuple(ref.split(".")), cfg)))
        out[key] = None if cur is None else cur.value
    return out


def check_contrast(tokens: list[Token], cfg: Config, label: str = "") -> list[Finding]:
    """Tier-2 content-on-background pairs meet WCAG AA (4.5:1 default) in this theme (course ch8; a11y is not deferrable)."""
    values = resolve(tokens, cfg)
    findings: list[Finding] = []
    for fg, bg in cfg.contrast_pairs:
        a, b = _hex_rgb(values.get(fg)), _hex_rgb(values.get(bg))
        if a is None or b is None:
            continue
        r = contrast_ratio(a, b)
        if r < cfg.contrast_min:
            findings.append(Finding("TA023", f"{fg} on {bg}", f"contrast {r:.2f}:1 < {cfg.contrast_min}:1{(' in ' + label) if label else ''}", label))
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
        extra["themes"] = {Path(t).name: len(load_tokens([t])) for t in themes}
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
                findings += check_contrast(load_tokens((paths or []) + [th]), cfg, Path(th).name)
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
    if failures:
        for x in failures:
            print("self-test FAIL:", x, file=sys.stderr)
        return 1
    print("OK token-audit self-test")
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0], formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("paths", nargs="*", help="token JSON files (DTCG or Style Dictionary)")
    ap.add_argument("--config", help="JSON config: prefix, tier_prefixes, tier3_max_share, tier3_may_alias_tier1, abbreviations, allow_abbreviations, color_buckets, require_type")
    ap.add_argument("--prefix", help="global code namespace (e.g. ds) — stripped before analysis")
    ap.add_argument("--themes", nargs="+", help="theme files that must expose the same tier-2/3 API")
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
    if not (a.paths or a.themes or a.parity or a.outputs or a.css or a.override):
        ap.print_usage(sys.stderr)
        return 2
    cfg = Config.load(a.config)
    if a.prefix:
        cfg.prefix = a.prefix
    override = (a.parent, a.override, a.kind) if a.override and a.parent else None
    findings, stats = audit(a.paths, cfg, themes=a.themes, parity=a.parity, css=a.css, outputs=a.outputs,
                            override=override, contrast=a.contrast)
    report(findings, stats, a.json)
    if any(f.level == "error" for f in findings) or (a.strict and findings):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
