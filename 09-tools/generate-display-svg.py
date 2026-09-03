#!/usr/bin/env python3
"""
generate-display-svg.py — emit a live display-graphic SVG from a JSON grammar.

Stdlib-only. Production path for HUD / schematic / instrument stills:
legal primitives become real SVG geometry and real <text>. Flattened
raster cutouts are refused.

This is not a raster generator and not a project catalog. Tokens and
layout come from the scene file. A Literal pack (LCARS or other) still
owns measured values; this tool only emits what the scene names.

Usage:
  python3 09-tools/generate-display-svg.py --check 09-tools/fixtures/display-scene.hud-example.json
  python3 09-tools/generate-display-svg.py --emit 09-tools/fixtures/display-scene.hud-example.json -o /tmp/hud.svg
  python3 09-tools/generate-display-svg.py --schema
  python3 09-tools/generate-display-svg.py --self-test
"""
from __future__ import annotations

import argparse
import json
import math
import re
import sys
import tempfile
from pathlib import Path
from typing import Any
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
FIXTURE = ROOT / "09-tools" / "fixtures" / "display-scene.hud-example.json"
TOOL_VERSION = "1.0"

LEGAL_KINDS = (
    "elbow",
    "bar",
    "pill",
    "rect",
    "sweep",
    "rail",
    "label",
    "circle",
)
FORBIDDEN_KINDS = frozenset(
    {
        "image",
        "img",
        "bitmap",
        "raster",
        "use",
        "foreignobject",
        "foreignObject",
        "picture",
        "cutout",
        "plate",
    }
)
FORBIDDEN_KEYS = frozenset(
    {
        "href",
        "src",
        "srcset",
        "assetsrc",
        "assetsrcset",
        "xlink:href",
        "xlinkhref",
        "foreignobject",
        "image",
        "raster",
        "cutout",
        "plate",
    }
)
RASTER_SUFFIX = re.compile(r"\.(png|jpe?g|webp|gif|tif{1,2}|bmp)(\b|$)", re.I)
HEX = re.compile(r"^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")


class SceneError(ValueError):
    """A scene that must not be emitted."""


def _as_float(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise SceneError(f"{field} must be a number")
    return float(value)


def _as_str(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise SceneError(f"{field} must be a non-empty string")
    return value


def walk_forbidden(node: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(node, dict):
        for key, val in node.items():
            low = str(key).lower().replace("_", "")
            here = f"{path}.{key}"
            if low in FORBIDDEN_KEYS:
                errors.append(f"{here}: forbidden key `{key}` (live geometry only)")
            errors.extend(walk_forbidden(val, here))
    elif isinstance(node, list):
        for i, val in enumerate(node):
            errors.extend(walk_forbidden(val, f"{path}[{i}]"))
    elif isinstance(node, str) and RASTER_SUFFIX.search(node):
        errors.append(f"{path}: raster path `{node}` is not a construction primitive")
    return errors


def resolve_fill(raw: Any, tokens: dict[str, str], field: str) -> str:
    if raw is None:
        raise SceneError(f"{field} needs a fill (token name or #hex)")
    if not isinstance(raw, str):
        raise SceneError(f"{field} fill must be a string")
    name = raw.strip()
    if name in tokens:
        return tokens[name]
    if HEX.match(name):
        return name
    raise SceneError(f"{field}: unknown fill `{raw}` (not a token and not #hex)")


def validate_scene(scene: dict[str, Any]) -> list[str]:
    errors = walk_forbidden(scene)
    if not isinstance(scene, dict):
        return ["scene must be a JSON object"]

    for req in ("width", "height", "elements"):
        if req not in scene:
            errors.append(f"missing `{req}`")
    if errors and not isinstance(scene.get("elements"), list):
        return errors

    try:
        w = _as_float(scene.get("width"), "width")
        h = _as_float(scene.get("height"), "height")
        if w <= 0 or h <= 0:
            errors.append("width and height must be > 0")
    except SceneError as exc:
        errors.append(str(exc))

    tokens = scene.get("tokens") or {}
    if tokens is None:
        tokens = {}
    if not isinstance(tokens, dict):
        errors.append("`tokens` must be an object")
        tokens = {}
    for name, val in tokens.items():
        if not isinstance(name, str) or not isinstance(val, str) or not HEX.match(val):
            errors.append(f"token `{name}` must map to a #hex color")

    bg = scene.get("background")
    if bg is not None:
        try:
            resolve_fill(bg, tokens, "background")
        except SceneError as exc:
            errors.append(str(exc))

    elements = scene.get("elements")
    if not isinstance(elements, list) or not elements:
        errors.append("`elements` must be a non-empty array")
        return errors

    seen: set[str] = set()
    for i, el in enumerate(elements):
        prefix = f"elements[{i}]"
        if not isinstance(el, dict):
            errors.append(f"{prefix} must be an object")
            continue
        try:
            eid = _as_str(el.get("id"), f"{prefix}.id")
        except SceneError as exc:
            errors.append(str(exc))
            continue
        if eid in seen:
            errors.append(f"{prefix}.id `{eid}` is duplicated")
        seen.add(eid)

        kind = el.get("kind")
        if not isinstance(kind, str):
            errors.append(f"{prefix}.kind is required")
            continue
        if kind in FORBIDDEN_KINDS:
            errors.append(
                f"{prefix}: kind `{kind}` is a cutout/raster path — emit live primitives"
            )
            continue
        if kind not in LEGAL_KINDS:
            errors.append(
                f"{prefix}: illegal kind `{kind}` (legal: {', '.join(LEGAL_KINDS)})"
            )
            continue

        try:
            _check_element_geometry(el, tokens, prefix)
        except SceneError as exc:
            errors.append(str(exc))

    return errors


def _box(el: dict[str, Any], prefix: str) -> tuple[float, float, float, float]:
    x = _as_float(el.get("x"), f"{prefix}.x")
    y = _as_float(el.get("y"), f"{prefix}.y")
    w = _as_float(el.get("width"), f"{prefix}.width")
    h = _as_float(el.get("height"), f"{prefix}.height")
    if w <= 0 or h <= 0:
        raise SceneError(f"{prefix}: width and height must be > 0")
    return x, y, w, h


def _check_element_geometry(el: dict[str, Any], tokens: dict[str, str], prefix: str) -> None:
    kind = el["kind"]
    if kind != "label":
        resolve_fill(el.get("fill"), tokens, f"{prefix}.fill")
    else:
        resolve_fill(el.get("fill"), tokens, f"{prefix}.fill")
        _as_str(el.get("text"), f"{prefix}.text")
        _as_float(el.get("x"), f"{prefix}.x")
        _as_float(el.get("y"), f"{prefix}.y")
        size = el.get("size", 16)
        _as_float(size, f"{prefix}.size")
        if float(size) <= 0:
            raise SceneError(f"{prefix}.size must be > 0")
        return

    if kind == "circle":
        _as_float(el.get("cx", el.get("x")), f"{prefix}.cx")
        _as_float(el.get("cy", el.get("y")), f"{prefix}.cy")
        r = _as_float(el.get("r", el.get("radius")), f"{prefix}.r")
        if r <= 0:
            raise SceneError(f"{prefix}.r must be > 0")
        return

    if kind == "sweep":
        _as_float(el.get("cx"), f"{prefix}.cx")
        _as_float(el.get("cy"), f"{prefix}.cy")
        r = _as_float(el.get("r"), f"{prefix}.r")
        t = _as_float(el.get("thickness"), f"{prefix}.thickness")
        _as_float(el.get("start"), f"{prefix}.start")
        sweep = _as_float(el.get("sweep"), f"{prefix}.sweep")
        if r <= 0 or t <= 0 or t >= r:
            raise SceneError(f"{prefix}: r > thickness > 0")
        if sweep == 0:
            raise SceneError(f"{prefix}.sweep must be non-zero")
        return

    if kind == "rail" and "height" not in el:
        if "thickness" not in el:
            raise SceneError(f"{prefix}: rail needs height or thickness")
        el = {**el, "height": el["thickness"]}
    x, y, w, h = _box(el, prefix)
    if kind == "elbow":
        t = _as_float(el.get("thickness"), f"{prefix}.thickness")
        if t <= 0 or t >= w or t >= h:
            raise SceneError(f"{prefix}: thickness must be > 0 and < width/height")
        corner = el.get("corner", "tl")
        if corner not in {"tl", "tr", "bl", "br"}:
            raise SceneError(f"{prefix}.corner must be tl|tr|bl|br")
        if "radius" in el:
            _as_float(el["radius"], f"{prefix}.radius")
    elif kind == "rail" and "height" not in el and "thickness" in el:
        pass


def elbow_d(x: float, y: float, w: float, h: float, t: float, corner: str, radius: float) -> str:
    r = min(max(radius, 0.0), t, w - t, h - t)
    if corner == "tl":
        # Clockwise from the top of the outer radius.
        if r <= 0:
            return (
                f"M{x},{y} H{x + w} V{y + t} H{x + t} V{y + h} H{x} Z"
            )
        return (
            f"M{x + r},{y} H{x + w} V{y + t} H{x + t} V{y + h} H{x} "
            f"V{y + r} A{r},{r} 0 0 1 {x + r},{y} Z"
        )
    if corner == "tr":
        if r <= 0:
            return (
                f"M{x},{y} H{x + w} V{y + h} H{x + w - t} V{y + t} H{x} Z"
            )
        return (
            f"M{x},{y} H{x + w - r} A{r},{r} 0 0 1 {x + w},{y + r} "
            f"V{y + h} H{x + w - t} V{y + t} H{x} Z"
        )
    if corner == "bl":
        if r <= 0:
            return (
                f"M{x},{y} H{x + t} V{y + h - t} H{x + w} V{y + h} H{x} Z"
            )
        return (
            f"M{x},{y} H{x + t} V{y + h - t} H{x + w} V{y + h} "
            f"H{x + r} A{r},{r} 0 0 1 {x},{y + h - r} Z"
        )
    # br
    if r <= 0:
        return (
            f"M{x},{y + h - t} H{x + w - t} V{y} H{x + w} V{y + h} H{x} Z"
        )
    return (
        f"M{x},{y + h - t} H{x + w - t} V{y} H{x + w} V{y + h - r} "
        f"A{r},{r} 0 0 1 {x + w - r},{y + h} H{x} Z"
    )


def polar(cx: float, cy: float, r: float, deg: float) -> tuple[float, float]:
    rad = math.radians(deg)
    return cx + r * math.cos(rad), cy + r * math.sin(rad)


def sweep_d(cx: float, cy: float, r: float, t: float, start: float, sweep: float) -> str:
    inner = r - t
    end = start + sweep
    large = 1 if abs(sweep) > 180 else 0
    sweep_flag = 1 if sweep > 0 else 0
    inv = 0 if sweep_flag else 1
    ox1, oy1 = polar(cx, cy, r, start)
    ox2, oy2 = polar(cx, cy, r, end)
    ix2, iy2 = polar(cx, cy, inner, end)
    ix1, iy1 = polar(cx, cy, inner, start)
    return (
        f"M{ox1:.3f},{oy1:.3f} "
        f"A{r:.3f},{r:.3f} 0 {large} {sweep_flag} {ox2:.3f},{oy2:.3f} "
        f"L{ix2:.3f},{iy2:.3f} "
        f"A{inner:.3f},{inner:.3f} 0 {large} {inv} {ix1:.3f},{iy1:.3f} Z"
    )


def xml_attr(value: str) -> str:
    return escape(value, {'"': "&quot;"})


def attr_map(pairs: list[tuple[str, str]]) -> str:
    return "".join(f' {k}="{xml_attr(v)}"' for k, v in pairs if v is not None)


def emit_element(el: dict[str, Any], tokens: dict[str, str]) -> str:
    kind = el["kind"]
    eid = el["id"]
    fill = resolve_fill(el.get("fill"), tokens, f"{eid}.fill")
    opacity = el.get("opacity")
    extra: list[tuple[str, str]] = [("id", eid), ("fill", fill)]
    if opacity is not None:
        extra.append(("opacity", f"{float(opacity):g}"))
    if el.get("role"):
        extra.append(("data-role", str(el["role"])))

    if kind == "label":
        size = float(el.get("size", 16))
        weight = str(el.get("weight", 700))
        family = str(el.get("family", "sans-serif"))
        anchor = str(el.get("anchor", "start"))
        extra.extend(
            [
                ("x", f"{float(el['x']):g}"),
                ("y", f"{float(el['y']):g}"),
                ("font-size", f"{size:g}"),
                ("font-weight", weight),
                ("font-family", family),
                ("text-anchor", anchor),
            ]
        )
        text = escape(str(el["text"]))
        return f"    <text{attr_map(extra)}>{text}</text>"

    if kind == "circle":
        cx = float(el.get("cx", el.get("x")))
        cy = float(el.get("cy", el.get("y")))
        r = float(el.get("r", el.get("radius")))
        extra.extend([("cx", f"{cx:g}"), ("cy", f"{cy:g}"), ("r", f"{r:g}")])
        return f"    <circle{attr_map(extra)}/>"

    if kind == "sweep":
        d = sweep_d(
            float(el["cx"]),
            float(el["cy"]),
            float(el["r"]),
            float(el["thickness"]),
            float(el["start"]),
            float(el["sweep"]),
        )
        extra.append(("d", d))
        return f"    <path{attr_map(extra)}/>"

    x, y, w, h = float(el["x"]), float(el["y"]), float(el["width"]), float(el["height"])
    if kind == "elbow":
        t = float(el["thickness"])
        radius = float(el.get("radius", t))
        d = elbow_d(x, y, w, h, t, str(el.get("corner", "tl")), radius)
        extra.append(("d", d))
        return f"    <path{attr_map(extra)}/>"

    if kind == "rail":
        h = float(el.get("height", el.get("thickness", 16)))
    rx = 0.0
    if kind == "pill":
        rx = min(w, h) / 2.0
    elif kind in {"bar", "rail", "rect"}:
        rx = float(el.get("rx", 0))
    extra.extend(
        [
            ("x", f"{x:g}"),
            ("y", f"{y:g}"),
            ("width", f"{w:g}"),
            ("height", f"{h:g}"),
        ]
    )
    if rx:
        extra.extend([("rx", f"{rx:g}"), ("ry", f"{rx:g}")])
    return f"    <rect{attr_map(extra)}/>"


FORBIDDEN_SVG = re.compile(
    r"<(image|foreignObject|use)\b|xlink:href=|href=\"(?!#)",
    re.I,
)


def emit_svg(scene: dict[str, Any]) -> str:
    errors = validate_scene(scene)
    if errors:
        raise SceneError("\n".join(errors))

    tokens = {k: str(v) for k, v in (scene.get("tokens") or {}).items()}
    width = float(scene["width"])
    height = float(scene["height"])
    vb = scene.get("viewBox") or f"0 0 {width:g} {height:g}"
    title = str(scene.get("title") or scene.get("id") or "display scene")
    bg = scene.get("background")
    bg_fill = resolve_fill(bg, tokens, "background") if bg is not None else None

    parts = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:g}" '
            f'height="{height:g}" viewBox="{escape(str(vb))}" role="img" '
            f'aria-labelledby="scene-title" data-generator="generate-display-svg/{TOOL_VERSION}">'
        ),
        f"  <title id=\"scene-title\">{escape(title)}</title>",
    ]
    if bg_fill:
        parts.append(
            f'  <rect id="background" x="0" y="0" width="{width:g}" '
            f'height="{height:g}" fill="{escape(bg_fill)}"/>'
        )

    open_group: str | None = None
    for el in scene["elements"]:
        group = el.get("group")
        group_id = str(group) if group else None
        if group_id != open_group:
            if open_group:
                parts.append("  </g>")
            if group_id:
                parts.append(f'  <g id="{xml_attr(group_id)}">')
            open_group = group_id
        line = emit_element(el, tokens)
        parts.append(line if group_id else "  " + line.strip())
    if open_group:
        parts.append("  </g>")
    parts.append("</svg>")
    svg = "\n".join(parts) + "\n"
    if FORBIDDEN_SVG.search(svg):
        raise SceneError("emitter produced a forbidden raster/external node")
    return svg


SCHEMA: dict[str, Any] = {
    "$schema": "https://json-schema.org/draft/2020-12/schema",
    "title": "Display scene grammar",
    "type": "object",
    "required": ["width", "height", "elements"],
    "additionalProperties": True,
    "properties": {
        "id": {"type": "string"},
        "title": {"type": "string"},
        "width": {"type": "number", "exclusiveMinimum": 0},
        "height": {"type": "number", "exclusiveMinimum": 0},
        "viewBox": {"type": "string"},
        "background": {"type": "string"},
        "tokens": {
            "type": "object",
            "additionalProperties": {"type": "string", "pattern": "^#([0-9A-Fa-f]{3}|[0-9A-Fa-f]{6}|[0-9A-Fa-f]{8})$"},
        },
        "elements": {
            "type": "array",
            "minItems": 1,
            "items": {
                "type": "object",
                "required": ["id", "kind", "fill"],
                "properties": {
                    "id": {"type": "string"},
                    "kind": {"enum": list(LEGAL_KINDS)},
                    "fill": {"type": "string"},
                    "group": {"type": "string"},
                    "role": {"type": "string"},
                    "x": {"type": "number"},
                    "y": {"type": "number"},
                    "width": {"type": "number"},
                    "height": {"type": "number"},
                    "thickness": {"type": "number"},
                    "corner": {"enum": ["tl", "tr", "bl", "br"]},
                    "radius": {"type": "number"},
                    "rx": {"type": "number"},
                    "cx": {"type": "number"},
                    "cy": {"type": "number"},
                    "r": {"type": "number"},
                    "start": {"type": "number"},
                    "sweep": {"type": "number"},
                    "text": {"type": "string"},
                    "size": {"type": "number"},
                    "weight": {},
                    "family": {"type": "string"},
                    "anchor": {"enum": ["start", "middle", "end"]},
                    "opacity": {"type": "number"},
                },
            },
        },
    },
}


def load_scene(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise SceneError(f"{path}: invalid JSON ({exc})") from exc
    if not isinstance(data, dict):
        raise SceneError(f"{path}: scene must be a JSON object")
    return data


def refuse_raster_fixture() -> dict[str, Any]:
    return {
        "width": 100,
        "height": 100,
        "elements": [
            {
                "id": "plate",
                "kind": "image",
                "fill": "#000",
                "src": "northstar.png",
            }
        ],
    }


def self_test() -> int:
    errors: list[str] = []
    if not FIXTURE.is_file():
        errors.append(f"missing fixture {FIXTURE}")
    else:
        scene = load_scene(FIXTURE)
        check = validate_scene(scene)
        if check:
            errors.append("example fixture failed --check:\n  " + "\n  ".join(check))
        else:
            svg = emit_svg(scene)
            if "<text" not in svg:
                errors.append("example emit has no <text>")
            if "<path" not in svg:
                errors.append("example emit has no <path> (expected an elbow)")
            if FORBIDDEN_SVG.search(svg):
                errors.append("example emit contains a forbidden node")
            if 'kind="image"' in svg or "<image" in svg:
                errors.append("example emit contains an image")
            with tempfile.NamedTemporaryFile("w", suffix=".svg", delete=False) as tmp:
                tmp.write(svg)
                out = Path(tmp.name)
            if out.stat().st_size < 200:
                errors.append("example emit is too small")
            out.unlink(missing_ok=True)

    refuse_errs = validate_scene(refuse_raster_fixture())
    if not refuse_errs:
        errors.append("raster cutout fixture was accepted (must refuse)")
    elif not any("cutout" in e or "raster" in e or "kind" in e for e in refuse_errs):
        errors.append("raster refusal did not name the cutout/raster reason")

    if errors:
        print("✗ generate-display-svg self-test failed", file=sys.stderr)
        for e in errors:
            print(f"  {e}", file=sys.stderr)
        return 1
    print("✓ generate-display-svg self-test passed")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__.split("Usage:", 1)[0].strip())
    src = p.add_mutually_exclusive_group()
    src.add_argument("--check", metavar="SCENE.json", help="validate a scene; emit nothing")
    src.add_argument("--emit", metavar="SCENE.json", help="validate and write SVG")
    src.add_argument("--schema", action="store_true", help="print the scene JSON schema")
    src.add_argument("--self-test", action="store_true", help="run fixture + refuse checks")
    p.add_argument("-o", "--output", help="SVG path for --emit (default: stdout)")
    args = p.parse_args(argv)

    if args.self_test:
        return self_test()
    if args.schema:
        json.dump(SCHEMA, sys.stdout, indent=2)
        sys.stdout.write("\n")
        return 0
    if not args.check and not args.emit:
        p.print_help()
        return 2

    path = Path(args.check or args.emit)
    if not path.is_file():
        print(f"✗ scene not found: {path}", file=sys.stderr)
        return 2
    try:
        scene = load_scene(path)
    except SceneError as exc:
        print(f"✗ {exc}", file=sys.stderr)
        return 2

    errs = validate_scene(scene)
    if errs:
        print(f"✗ {path}: {len(errs)} problem(s)", file=sys.stderr)
        for e in errs:
            print(f"  {e}", file=sys.stderr)
        return 2
    if args.check:
        print(f"✓ {path}: {len(scene['elements'])} live primitives")
        return 0

    try:
        svg = emit_svg(scene)
    except SceneError as exc:
        print(f"✗ emit failed:\n{exc}", file=sys.stderr)
        return 2
    if args.output:
        out = Path(args.output)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(svg, encoding="utf-8")
        print(f"✓ wrote {out} ({len(svg)} bytes)")
        return 0
    sys.stdout.write(svg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
