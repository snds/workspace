#!/usr/bin/env python3
"""
vqa.py — visual prove engine CLI.

Subcommands:
  doctor          — report available deps and what degrades without them
  verify-capture  — validate a capture PNG against its *.capture.json manifest
  perceive        — pixel-derived region inventory + shape grammar + ledger flags
  prove           — run a declarative cuespec against a build capture
  compare         — reference vs build(s): registration, SSIM, FLIP, delta-E, ranking
  motion          — frame-sequence smoothness/stutter/flicker/easing + tracks/photon
  interact        — verify declared action-effects between state captures
  mesh            — glTF/GLB audit (fail closed on Error)
  geometry        — geometric consistency across >=2 pinned views
  judge           — cross-model VLM Spirit/Intent protocol (never Literal)
  score           — append a prove result to an improvement-loop ledger
  calibrate       — self-test: planted defects + clean fixtures, FP/FN report

Exit codes: 0 ok · 1 failed verdict / regression / calibration miss · 2 usage error.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SKILL_DIR))

from scripts import _core, calibrate, compare, geometry, interact, judge, mesh, motion, perceive, prove, trajectory  # noqa: E402


def _print(payload: dict) -> None:
    print(json.dumps(payload, indent=2))


def cmd_doctor(_args) -> int:
    report = _core.deps_report()
    _print(report)
    return 0


def cmd_verify_capture(args) -> int:
    result = _core.verify_capture(args.image, args.manifest)
    _print(result)
    return 0 if result["status"] == "verified" else 1


def cmd_perceive(args) -> int:
    img = _core.load_image(args.image)
    bg = _core.hex_to_rgb(args.background) if args.background else None
    payload = perceive.perceive(img, background=bg)
    out = Path(args.output) if args.output else None
    if out:
        stem = Path(args.image).stem
        _core.write_json(payload, out / f"{stem}.perceive.json")
        annotated = perceive.annotate(img, payload, out / f"{stem}.perceive.png")
        payload["artifacts"] = [str(out / f"{stem}.perceive.json"), str(annotated)]
    _print(payload if args.full else {
        k: payload[k] for k in
        ("image", "size", "background", "region_count", "gutters", "palette", "ledger_flags", *(
            ("artifacts",) if "artifacts" in payload else ()))
    })
    return 0


def cmd_prove(args) -> int:
    payload = prove.run_prove(args.build, args.cuespec, out_dir=args.output,
                              manifest_path=args.manifest)
    summary = payload["summary"]
    _print({"summary": summary, "capture": payload["capture"]["status"],
            **({"artifacts": payload["artifacts"]} if "artifacts" in payload else {})})
    if summary["verdict"] == "fail":
        return 1
    if args.strict and summary["verdict"] != "matches":
        return 1
    return 0


def cmd_compare(args) -> int:
    payload = compare.compare_rank(args.reference, args.builds, out_dir=args.output)
    _print({"reference": payload["reference"], "ranking": payload["ranking"]})
    return 0


def cmd_motion(args) -> int:
    spec = json.loads(Path(args.spec).read_text(encoding="utf-8")) if args.spec else {}
    payload = motion.analyze_motion(
        frames_dir=args.frames, video=args.video, spec=spec,
        out_dir=args.output, timestamps=args.timestamps,
    )
    _print(payload)
    failing = [v for v in payload["verdicts"] if v["status"] == "fail"]
    return 1 if failing else 0


def cmd_interact(args) -> int:
    payload = interact.run_interact(args.spec, out_dir=args.output)
    _print(payload)
    return 0 if payload["verdict"] == "pass" else 1


def cmd_mesh(args) -> int:
    payload = mesh.audit(args.asset)
    _print(payload)
    return 0 if payload["status"] == "pass" else 1


def cmd_geometry(args) -> int:
    payload = geometry.consistency(args.views, min_peak=args.min_peak, min_ssim=args.min_ssim)
    _print(payload)
    if payload["status"] == "error":
        return 2
    return 0 if payload["status"] == "pass" else 1


def cmd_judge(args) -> int:
    payload = judge.run_judge(args.spec, out_dir=args.output)
    _print(payload)
    if payload["verdict"] in ("yes",):
        return 0
    if payload["verdict"] in ("no", "split", "discarded"):
        return 1
    return 2


def cmd_score(args) -> int:
    result = trajectory.record_score(
        args.ledger, getattr(args, "from"), note=args.note or "",
        enforce=args.enforce, stall_limit=args.stall_limit,
    )
    _print(result)
    return 1 if result["enforce_fail"] else 0


def cmd_calibrate(args) -> int:
    report = calibrate.run_calibration(out_dir=args.output, keep_images=args.keep_images)
    _print({
        "verdict": report["verdict"],
        "cases": f"{report['cases_ok']}/{report['cases_total']}",
        "per_detector": report["per_detector"],
        "misses": report["misses"],
        "out_dir": report["out_dir"],
    })
    return 0 if report["verdict"] == "calibrated" else 1


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="vqa", description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="cmd", required=True)

    sub.add_parser("doctor", help="dependency and degradation report")

    p = sub.add_parser("verify-capture", help="validate capture manifest")
    p.add_argument("image")
    p.add_argument("--manifest")

    p = sub.add_parser("perceive", help="pixel-derived structure inventory")
    p.add_argument("image")
    p.add_argument("--background", help="known background hex, e.g. '#000000'")
    p.add_argument("--output", help="write perceive.json + annotated png here")
    p.add_argument("--full", action="store_true", help="print full region list")

    p = sub.add_parser("prove", help="run a cuespec against a build capture")
    p.add_argument("build")
    p.add_argument("cuespec")
    p.add_argument("--output", help="write prove.json + prove.md here")
    p.add_argument("--manifest", help="explicit capture manifest path")
    p.add_argument("--strict", action="store_true",
                   help="exit 1 unless verdict is matches")

    p = sub.add_parser("compare", help="rank builds against a reference")
    p.add_argument("reference")
    p.add_argument("builds", nargs="+")
    p.add_argument("--output", help="write heatmaps/side-by-sides/rank json here")

    p = sub.add_parser("motion", help="analyze a frame sequence or video")
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("--frames", help="directory of ordered PNG frames")
    src.add_argument("--video", help="video file (requires ffmpeg)")
    p.add_argument("--spec", help="motionspec JSON with budgets")
    p.add_argument("--timestamps", help="frame-timestamp manifest JSON for vsync jank")
    p.add_argument("--output")

    p = sub.add_parser("interact", help="verify declared action-effects")
    p.add_argument("spec")
    p.add_argument("--output")

    p = sub.add_parser("mesh", help="audit a glTF/GLB asset (fail closed on Error)")
    p.add_argument("asset")

    p = sub.add_parser("geometry", help="geometric consistency across pinned views")
    p.add_argument("views", nargs="+", help=">=2 image paths (orbit or stereo)")
    p.add_argument("--min-peak", type=float, default=0.08)
    p.add_argument("--min-ssim", type=float, default=0.25)

    p = sub.add_parser("judge", help="cross-model VLM Spirit/Intent protocol")
    p.add_argument("spec")
    p.add_argument("--output")

    p = sub.add_parser("score", help="append a prove run to an improvement ledger")
    p.add_argument("--ledger", required=True)
    p.add_argument("--from", dest="from", required=True, help="prove.json path")
    p.add_argument("--note")
    p.add_argument("--enforce", action="store_true",
                   help="exit 1 on regression or coverage drop (loop gate)")
    p.add_argument("--stall-limit", type=int, default=3)

    p = sub.add_parser("calibrate", help="self-test with planted defects")
    p.add_argument("--output", help="keep fixtures + report here (default: temp dir)")
    p.add_argument("--keep-images", action="store_true")

    args = parser.parse_args(argv)
    handlers = {
        "doctor": cmd_doctor,
        "verify-capture": cmd_verify_capture,
        "perceive": cmd_perceive,
        "prove": cmd_prove,
        "compare": cmd_compare,
        "motion": cmd_motion,
        "interact": cmd_interact,
        "mesh": cmd_mesh,
        "geometry": cmd_geometry,
        "judge": cmd_judge,
        "score": cmd_score,
        "calibrate": cmd_calibrate,
    }
    return handlers[args.cmd](args)


if __name__ == "__main__":
    sys.exit(main())
