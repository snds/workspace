"""`secretscan` — the hard gate before anything is ingested into a (public) workspace.

The workspace repo can be public and there is no upstream secret-scanner, so ANY content
pulled in from outside must be scanned first, and anything that looks like a credential is
**blocked from promotion** — it stays quarantined, never staged for tracking. Detection is
pattern-based (stdlib only): well-known key/token formats, private keys, JWTs, env-style
secret assignments (`block` severity), and public/WAN IPs (`review` severity).

Safe-by-default bias: a false positive over-quarantines a harmless note (annoying); a false
negative leaks a credential into a public repo (unacceptable). So the gate errs toward block.
Matches are redacted in findings — the scanner never echoes a full secret.
"""
from __future__ import annotations

import ipaddress
import re
from pathlib import Path

# (name, compiled regex, severity). `block` → never promote the file. `review` → surface,
# require a human decision. Group 0 (or a capture group, see _redact) is the sensitive span.
PATTERNS = [
    ("openai-key", re.compile(r"sk-(?:proj-)?[A-Za-z0-9_-]{20,}"), "block"),
    ("anthropic-key", re.compile(r"sk-ant-[A-Za-z0-9_-]{20,}"), "block"),
    ("aws-access-key-id", re.compile(r"\b(?:AKIA|ASIA)[0-9A-Z]{16}\b"), "block"),
    ("gcp-api-key", re.compile(r"\bAIza[0-9A-Za-z_-]{35}\b"), "block"),
    ("github-token", re.compile(r"\b(?:ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{36,}\b"), "block"),
    ("github-pat", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{40,}\b"), "block"),
    ("slack-token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{10,}\b"), "block"),
    ("stripe-key", re.compile(r"\b[sr]k_live_[A-Za-z0-9]{16,}\b"), "block"),
    ("google-oauth", re.compile(r"\bya29\.[A-Za-z0-9_-]{20,}"), "block"),
    ("twilio-key", re.compile(r"\bSK[0-9a-fA-F]{32}\b"), "block"),
    ("sendgrid-key", re.compile(r"\bSG\.[A-Za-z0-9_-]{22}\.[A-Za-z0-9_-]{43}\b"), "block"),
    ("private-key-block",
     re.compile(r"-----BEGIN (?:RSA |EC |DSA |OPENSSH |PGP )?PRIVATE KEY-----"), "block"),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.eyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}"), "block"),
    # env-style assignment: KEY = "longvalue" where KEY names a secret. Capture the VALUE.
    ("secret-assignment",
     re.compile(r"(?i)\b(?:api[_-]?key|secret|token|passwd|password|access[_-]?key|"
                r"client[_-]?secret|private[_-]?key|auth[_-]?token)\b\s*[:=]\s*"
                r"['\"]?([A-Za-z0-9/+_\-\.]{12,})['\"]?"), "block"),
]

_IPV4 = re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b")
# obvious non-secret placeholders that would otherwise trip `secret-assignment`
_PLACEHOLDER = re.compile(r"(?i)^(?:x{6,}|\.{3,}|<[^>]+>|your[_-].*|example|changeme|"
                          r"redacted|placeholder|todo|none|null|true|false|\d+)$")


def _redact(m: re.Match) -> str:
    span = m.group(m.lastindex) if m.lastindex else m.group(0)
    span = span.strip("'\"")
    if len(span) <= 8:
        return span[:2] + "…"
    return f"{span[:4]}…{span[-2:]} ({len(span)} chars)"


def _is_public_ip(s: str) -> bool:
    try:
        ip = ipaddress.ip_address(s)
    except ValueError:
        return False
    return (ip.version == 4 and not (ip.is_private or ip.is_loopback or ip.is_link_local
            or ip.is_multicast or ip.is_reserved or ip.is_unspecified))


def scan_text(text: str) -> list:
    """Return a list of findings: {kind, severity, line, redacted}."""
    findings = []
    lines = text.splitlines()
    for i, line in enumerate(lines, 1):
        for name, rx, sev in PATTERNS:
            for m in rx.finditer(line):
                if name == "secret-assignment":
                    val = (m.group(m.lastindex) or "").strip("'\"")
                    if _PLACEHOLDER.match(val):
                        continue  # obvious placeholder, not a real secret
                findings.append({"kind": name, "severity": sev, "line": i,
                                 "redacted": _redact(m)})
        for m in _IPV4.finditer(line):
            if _is_public_ip(m.group(0)):
                findings.append({"kind": "public-ip", "severity": "review", "line": i,
                                 "redacted": m.group(0)})
    return findings


# Only text-like files are scanned; binaries are treated as opaque and never promoted.
_TEXT_EXT = {".md", ".markdown", ".txt", ".rst", ".adoc", ".json", ".yml", ".yaml",
             ".toml", ".ini", ".cfg", ".conf", ".env", ".sh", ".py", ".js", ".ts",
             ".rb", ".go", ".java", ".xml", ".csv", ".log", ".properties", ".mdc", ""}
_MAX_BYTES = 2_000_000


def scan_file(path: Path) -> list:
    p = Path(path)
    if p.suffix.lower() not in _TEXT_EXT:
        return [{"kind": "binary", "severity": "review", "line": 0,
                 "redacted": "(binary/opaque — not scannable; won't be promoted)"}]
    try:
        if p.stat().st_size > _MAX_BYTES:
            return [{"kind": "oversize", "severity": "review", "line": 0,
                     "redacted": f"({p.stat().st_size} bytes — too large to scan safely)"}]
        return scan_text(p.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError):
        return [{"kind": "unreadable", "severity": "review", "line": 0,
                 "redacted": "(could not read as text — won't be promoted)"}]


def blocked(findings: list) -> bool:
    """True if any finding hard-blocks promotion (a credential-class hit)."""
    return any(f["severity"] == "block" for f in findings)


def summarize(findings: list) -> str:
    kinds = sorted({f["kind"] for f in findings})
    return ", ".join(kinds)
