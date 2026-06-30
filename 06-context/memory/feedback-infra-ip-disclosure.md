---
type: feedback
description: Documenting Sean's infrastructure — internal/LAN IPs are fine to record, external/WAN IP never
created: 2026-06-25
confidence: high
---

When recording anything about Sean's home/network infrastructure: **internal / LAN IPs (the `10.42.x.x`
RFC1918 range) are fine to document.** They're only meaningful inside the LAN, aren't reachable from
outside, and Sean can renumber them at the router at will.

**The real attack surface is the external / public (WAN) IP — never record, infer, log, or expose it, and
don't ask for it unless there's a concrete, approved need.** It is deliberately undocumented anywhere.

**Why:** An internal IP leaks nothing exploitable to anyone who isn't already on the LAN; the external IP
is what an attacker would actually use. Sean flagged this directly after I over-weighted the internal IP
as a risk (briefly wanting to gitignore a note over it) and under-named the external one.

**How to apply:** Treat LAN IPs, the SSH key *fingerprint* (derived from the public key), hardware specs,
and share layout as routine to note — including in the public `snds/workspace` repo. Keep the external IP,
and any real secrets (passwords, API keys, tokens), out of all notes, and out of public repos especially.
Related: [[fact-unraid-server]].
