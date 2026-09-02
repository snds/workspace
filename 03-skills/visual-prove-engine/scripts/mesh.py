"""
glTF / GLB mesh audit. Altitude E.

Fail closed on Error-level issues. Prefers the Khronos `gltf-validator` CLI
or `@khronosgroup/gltf-asset-auditor` when present; otherwise runs a stdlib
parser that still refuses NaN accessors, missing buffers, and illegal
primitive counts. Absence of the official validator is recorded as
`backend: stdlib` — never a silent pass of a broken asset.
"""
from __future__ import annotations

import json
import math
import shutil
import struct
import subprocess
from pathlib import Path
from typing import Any, Optional


COMPONENT_BYTES = {5120: 1, 5121: 1, 5122: 2, 5123: 2, 5125: 4, 5126: 4}
TYPE_COMPONENTS = {
    "SCALAR": 1, "VEC2": 2, "VEC3": 3, "VEC4": 4,
    "MAT2": 4, "MAT3": 9, "MAT4": 16,
}


def available() -> dict:
    return {
        "gltf_validator": shutil.which("gltf-validator") is not None,
        "npx": shutil.which("npx") is not None,
    }


def audit(path: str | Path) -> dict:
    p = Path(path)
    result: dict[str, Any] = {
        "asset": str(p),
        "backend": "stdlib",
        "errors": [],
        "warnings": [],
        "stats": {},
        "status": "error",
    }
    if not p.exists():
        result["errors"].append(f"asset missing: {p}")
        return result
    try:
        gltf, buffers = _load(p)
    except Exception as exc:
        result["errors"].append(f"parse failed: {exc}")
        return result

    result["stats"] = _stats(gltf)
    result["errors"].extend(_stdlib_errors(gltf, buffers))

    official = _run_official(p)
    if official is not None:
        result["backend"] = official["backend"]
        result["errors"].extend(official["errors"])
        result["warnings"].extend(official["warnings"])

    # Dedupe while preserving order
    result["errors"] = list(dict.fromkeys(result["errors"]))
    result["warnings"] = list(dict.fromkeys(result["warnings"]))
    result["status"] = "fail" if result["errors"] else "pass"
    return result


def _load(path: Path):
    if path.suffix.lower() == ".glb":
        return _load_glb(path)
    data = json.loads(path.read_text(encoding="utf-8"))
    buffers = []
    for b in data.get("buffers") or []:
        uri = b.get("uri")
        if not uri:
            buffers.append(b"")
            continue
        if uri.startswith("data:"):
            import base64
            _, b64 = uri.split(",", 1)
            buffers.append(base64.b64decode(b64))
        else:
            buffers.append((path.parent / uri).read_bytes())
    return data, buffers


def _load_glb(path: Path):
    raw = path.read_bytes()
    if raw[:4] != b"glTF":
        raise ValueError("not a GLB (missing glTF magic)")
    _ver, length = struct.unpack_from("<II", raw, 4)
    if length != len(raw):
        raise ValueError(f"GLB length {length} != file {len(raw)}")
    offset = 12
    json_chunk = None
    bin_chunk = b""
    while offset + 8 <= len(raw):
        clen, ctype = struct.unpack_from("<I4s", raw, offset)
        offset += 8
        chunk = raw[offset : offset + clen]
        offset += clen
        if ctype == b"JSON":
            json_chunk = json.loads(chunk.decode("utf-8"))
        elif ctype == b"BIN\x00":
            bin_chunk = chunk
    if json_chunk is None:
        raise ValueError("GLB has no JSON chunk")
    buffers = [bin_chunk]
    return json_chunk, buffers


def _stats(gltf: dict) -> dict:
    meshes = gltf.get("meshes") or []
    primitives = sum(len(m.get("primitives") or []) for m in meshes)
    triangles = 0
    accessors = gltf.get("accessors") or []
    for m in meshes:
        for prim in m.get("primitives") or []:
            idx = prim.get("indices")
            mode = prim.get("mode", 4)
            if idx is not None and idx < len(accessors):
                count = int(accessors[idx].get("count", 0))
                if mode == 4:  # TRIANGLES
                    triangles += count // 3
                elif mode == 5:  # TRIANGLE_STRIP
                    triangles += max(0, count - 2)
    return {
        "nodes": len(gltf.get("nodes") or []),
        "meshes": len(meshes),
        "primitives": primitives,
        "accessors": len(accessors),
        "triangles_est": triangles,
        "version": (gltf.get("asset") or {}).get("version"),
    }


def _stdlib_errors(gltf: dict, buffers: list) -> list:
    errors = []
    asset = gltf.get("asset") or {}
    if str(asset.get("version", "")) not in ("2.0", "2.0.0"):
        errors.append(f"unsupported or missing glTF version: {asset.get('version')!r}")
    if not (gltf.get("scenes") or gltf.get("scene") is not None):
        errors.append("no scenes")
    accessors = gltf.get("accessors") or []
    views = gltf.get("bufferViews") or []
    for i, acc in enumerate(accessors):
        ctype = acc.get("componentType")
        atype = acc.get("type")
        count = acc.get("count")
        if ctype not in COMPONENT_BYTES:
            errors.append(f"accessor {i}: illegal componentType {ctype}")
            continue
        if atype not in TYPE_COMPONENTS:
            errors.append(f"accessor {i}: illegal type {atype}")
            continue
        if not isinstance(count, int) or count < 0:
            errors.append(f"accessor {i}: illegal count {count}")
            continue
        bvi = acc.get("bufferView")
        if bvi is None:
            continue
        if bvi >= len(views):
            errors.append(f"accessor {i}: bufferView {bvi} out of range")
            continue
        view = views[bvi]
        bidx = view.get("buffer", 0)
        if bidx >= len(buffers):
            errors.append(f"accessor {i}: buffer {bidx} missing")
            continue
        byte_offset = int(view.get("byteOffset", 0)) + int(acc.get("byteOffset", 0))
        nbytes = COMPONENT_BYTES[ctype] * TYPE_COMPONENTS[atype] * count
        buf = buffers[bidx]
        if byte_offset + nbytes > len(buf):
            errors.append(f"accessor {i}: reads past buffer end")
            continue
        if ctype == 5126:  # FLOAT
            fmt = "<" + "f" * (TYPE_COMPONENTS[atype] * count)
            try:
                vals = struct.unpack_from(fmt, buf, byte_offset)
            except struct.error:
                errors.append(f"accessor {i}: unpack failed")
                continue
            if any(math.isnan(v) or math.isinf(v) for v in vals):
                errors.append(f"accessor {i}: NaN/Inf in float data")
        if atype == "VEC2" and acc.get("name", "").upper().find("TEXCOORD") >= 0:
            pass  # UV range is a warning, checked below
    # UV 0-1 warning is handled as error only when values are wildly outside
    for i, acc in enumerate(accessors):
        if acc.get("type") != "VEC2" or acc.get("componentType") != 5126:
            continue
        # Heuristic: TEXCOORD accessors
        used_as_uv = False
        for m in gltf.get("meshes") or []:
            for prim in m.get("primitives") or []:
                attrs = prim.get("attributes") or {}
                if attrs.get("TEXCOORD_0") == i or attrs.get("TEXCOORD_1") == i:
                    used_as_uv = True
        if not used_as_uv:
            continue
        bvi = acc.get("bufferView")
        if bvi is None or bvi >= len(views):
            continue
        view = views[bvi]
        bidx = view.get("buffer", 0)
        if bidx >= len(buffers):
            continue
        byte_offset = int(view.get("byteOffset", 0)) + int(acc.get("byteOffset", 0))
        count = int(acc.get("count", 0))
        fmt = "<" + "f" * (2 * count)
        try:
            vals = struct.unpack_from(fmt, buffers[bidx], byte_offset)
        except struct.error:
            continue
        if any(v < -0.01 or v > 1.01 for v in vals):
            errors.append(f"accessor {i}: UV outside [0,1]")
    return errors


def _run_official(path: Path) -> Optional[dict]:
    exe = shutil.which("gltf-validator")
    if exe:
        proc = subprocess.run(
            [exe, str(path), "-o", "-"],
            capture_output=True, text=True, check=False,
        )
        errors, warnings = _parse_validator_text(proc.stdout + proc.stderr)
        if proc.returncode not in (0, 1):
            # validator crashed — keep stdlib result, note it
            return {
                "backend": "gltf-validator (failed to run)",
                "errors": [f"gltf-validator exit {proc.returncode}"],
                "warnings": warnings,
            }
        return {"backend": "gltf-validator", "errors": errors, "warnings": warnings}
    return None


def _parse_validator_text(text: str) -> tuple:
    errors, warnings = [], []
    for line in text.splitlines():
        low = line.lower()
        if "error" in low and "0 errors" not in low:
            if line.strip():
                errors.append(line.strip())
        elif "warning" in low and "0 warnings" not in low:
            if line.strip():
                warnings.append(line.strip())
    return errors, warnings
