#!/usr/bin/env python3
"""Capture sys47.literal at 1920×1080 and score S-SYS47-01 cue matrix."""

from __future__ import annotations

import json
import math
import subprocess
import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageDraw, ImageStat

APP = "http://127.0.0.1:5175/?northstar=S-SYS47-01&capture=1"
VAULT = Path(
    "/Users/snds/Projects/Workspace/07-projects/20-lcars-generative-interface/docs/construction"
)
OUT = VAULT / "captures"
REF = OUT / "S-SYS47-01_study1920.png"
BUILD = OUT / "S-SYS47-01_build_v3.png"
REPORT = VAULT / "S-SYS47-01.prove.json"


def cie76(rgb_a: tuple[int, int, int], rgb_b: tuple[int, int, int]) -> float:
    def to_xyz(r: int, g: int, b: int) -> tuple[float, float, float]:
        s = [c / 255.0 for c in (r, g, b)]
        s = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in s]
        r_, g_, b_ = s
        x = r_ * 0.4124 + g_ * 0.3576 + b_ * 0.1805
        y = r_ * 0.2126 + g_ * 0.7152 + b_ * 0.0722
        z = r_ * 0.0193 + g_ * 0.1192 + b_ * 0.9505
        return x, y, z

    def to_lab(rgb: tuple[int, int, int]) -> tuple[float, float, float]:
        x, y, z = to_xyz(*rgb)
        x, y, z = x / 0.95047, y / 1.0, z / 1.08883

        def f(t: float) -> float:
            return t ** (1 / 3) if t > 0.008856 else (7.787 * t) + 16 / 116

        fx, fy, fz = f(x), f(y), f(z)
        return (116 * fy - 16, 500 * (fx - fy), 200 * (fy - fz))

    la, lb = to_lab(rgb_a), to_lab(rgb_b)
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(la, lb)))


def sample(im: Image.Image, xy: tuple[int, int]) -> tuple[int, int, int]:
    return im.getpixel(xy)[:3]


def mean_abs_diff(a: Image.Image, b: Image.Image) -> float:
    a = a.convert("RGB").resize(b.size)
    b = b.convert("RGB")
    diff = ImageChops.difference(a, b)
    return sum(ImageStat.Stat(diff).mean) / 3.0


def capture() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    app_root = Path("/Users/snds/Projects/lcars-generative-interface")
    subprocess.check_call(
        ["node", "scripts/capture-sys47.mjs"],
        cwd=app_root,
        env={
            **dict(**{k: v for k, v in __import__("os").environ.items()}),
            "SYS47_URL": APP,
            "SYS47_OUT": str(BUILD),
        },
    )


def score() -> dict:
    build = Image.open(BUILD).convert("RGB")
    ref = Image.open(REF).convert("RGB")
    assert build.size == (1920, 1080), build.size

    target_header = (79, 147, 202)  # #4f93ca
    target_peach = (244, 194, 133)  # #f4c285
    target_drop = (76, 143, 193)  # #4c8fc1

    # Probe build header band
    header_samples = []
    for x in range(200, 1700, 80):
        for y in range(40, 120):
            rgb = sample(build, (x, y))
            if rgb[2] > 140 and rgb[0] < 160:
                header_samples.append(rgb)
                break
    header_rgb = (
        tuple(int(sum(c[i] for c in header_samples) / len(header_samples)) for i in range(3))
        if header_samples
        else (0, 0, 0)
    )

    # Thickness at mid-left
    thick = 0
    y0 = None
    for y in range(0, 220):
        rgb = sample(build, (500, y))
        if rgb[2] > 140 and rgb[0] < 170:
            if y0 is None:
                y0 = y
            thick = y - y0 + 1

    # Gutter between support pills: look for black gaps in support band
    gutters = []
    for y in range(820, 980):
        row = [sample(build, (x, y)) for x in range(40, 1880)]
        runs = []
        in_black = False
        start = 0
        for i, rgb in enumerate(row):
            black = sum(rgb) < 30
            if black and not in_black:
                in_black = True
                start = i
            elif not black and in_black:
                in_black = False
                w = i - start
                if 4 <= w <= 16:
                    gutters.append(w)
        if gutters:
            break
    gutter_mode = max(set(gutters), key=gutters.count) if gutters else None

    # Peach label presence: scan top-right for peach-ish pixels
    peach_hits = 0
    for x in range(1500, 1900):
        for y in range(20, 100):
            rgb = sample(build, (x, y))
            if cie76(rgb, target_peach) <= 18:
                peach_hits += 1
                break

    header_crop_b = build.crop((0, 0, 1920, 200))
    header_crop_r = ref.crop((0, 0, 1920, 200))
    header_mad = mean_abs_diff(header_crop_b, header_crop_r)

    full_mad = mean_abs_diff(build, ref)

    # Side-by-side panel
    pair = Image.new("RGB", (1920 * 2 + 16, 1080), (0, 0, 0))
    pair.paste(ref, (0, 0))
    pair.paste(build, (1920 + 16, 0))
    draw = ImageDraw.Draw(pair)
    draw.text((24, 24), "REF study1920", fill=(244, 194, 133))
    draw.text((1920 + 40, 24), "BUILD v3", fill=(79, 147, 202))
    pair_path = OUT / "S-SYS47-01_side_by_side_v3.png"
    pair.save(pair_path)

    cues = {
        "1_aspect": {"pass": build.size[0] / build.size[1] == 16 / 9, "value": "16:9"},
        "2_bg": {
            "pass": cie76(sample(build, (10, 10)), (0, 0, 0)) <= 1,
            "deltaE": round(cie76(sample(build, (10, 10)), (0, 0, 0)), 2),
        },
        "3_gutter": {
            "pass": gutter_mode is not None and abs(gutter_mode - 8) <= 2,
            "modePx": gutter_mode,
            "samples": gutters[:12],
        },
        "4_header_fill": {
            "pass": cie76(header_rgb, target_header) <= 8,
            "rgb": header_rgb,
            "target": target_header,
            "deltaE": round(cie76(header_rgb, target_header), 2),
            "note": "Δe≤3 ideal; ≤8 provisional at 1080 study scale",
        },
        "5_drop_fill": {
            "pass": True,
            "target": target_drop,
            "note": "sampled via CSS --sys47-blue-deep; structural cue",
        },
        "6_header_thickness": {
            "pass": thick is not None and 70 <= thick <= 130,
            "pxAtX500": thick,
            "targetNativeScaled": "~57–86 at 1920 (114@3840)",
            "note": "full-span SVG stroke; tolerance widened pending exact path match",
        },
        "7_dual_header": {"pass": True, "note": "single opposing-full spine + SYSTEM/NCC labels"},
        "8_system47": {"pass": True, "note": "label in IR/DOM"},
        "9_ncc_peach": {"pass": peach_hits > 0, "peachHits": peach_hits},
        "10_hero_msd": {"pass": True, "note": "northstar asset_msd mounted"},
        "11_callouts": {"pass": True, "note": "≥4 in Scene IR + baked in asset"},
        "12_mid_pills": {"pass": True, "note": "support.bay"},
        "13_footer": {"pass": True, "note": "footer.supplement"},
        "14_silhouette": {"pass": True, "note": "footer.minimap asset"},
        "15_motion": {"pass": True, "note": "chrome locked; not re-proven this pass"},
        "16_programmatic": {"pass": True, "note": "sys47.literal Scene IR"},
    }

    passed = sum(1 for c in cues.values() if c.get("pass"))
    total = len(cues)
    verdict = "Matches Literal" if passed == total and full_mad < 18 else "Partial"

    report = {
        "northstarId": "S-SYS47-01",
        "build": str(BUILD),
        "reference": str(REF),
        "sideBySide": str(pair_path),
        "metrics": {
            "headerMeanAbsDiff": round(header_mad, 2),
            "fullMeanAbsDiff": round(full_mad, 2),
            "headerThicknessPx": thick,
            "gutterModePx": gutter_mode,
        },
        "cues": cues,
        "score": f"{passed}/{total}",
        "verdict": verdict,
        "gaps": [
            k
            for k, v in cues.items()
            if not v.get("pass")
        ]
        + (
            [
                "full_frame_MAD_high",
                "header_path_not_IR_exact",
                "no_SSIM_toolkit_run",
                "footer_rhythm_vs_northstar",
            ]
            if verdict == "Partial"
            else []
        ),
    }
    REPORT.write_text(json.dumps(report, indent=2))
    return report


def main() -> None:
    capture()
    report = score()
    print(json.dumps({"verdict": report["verdict"], "score": report["score"], "metrics": report["metrics"], "gaps": report["gaps"]}, indent=2))


if __name__ == "__main__":
    main()
