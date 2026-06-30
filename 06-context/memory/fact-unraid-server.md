---
type: fact
description: Sean's Unraid home server — how to reach it (LAN, key auth, sandbox) and what runs on it
created: 2026-06-25
confidence: high
---

Sean's Unraid home server. Durable connection knowledge, reusable for any work on the box (Docker
container audits, deploys, the planned dockers + app-settings review). The IP-disclosure rule that
governs what's safe to write here is [[feedback-infra-ip-disclosure]].

## The box
- **Reach it at:** `root@10.42.1.162` over SSH (:22). Internal/LAN IP only (RFC1918) — fine to record;
  renumberable at the router. This Mac is `10.42.1.156`.
- **OS / runtime:** Unraid 7.2.x, Docker 27.x.
- **Hardware:** AMD Threadripper PRO 3955WX (32 threads), ~62 GiB RAM, **NVIDIA RTX A2000 (CUDA)**.
  Large array (~124 TB), plenty free.
- **Shares (TRaSH "data" layout):** media under `/mnt/user/data/media`, downloads `/mnt/user/data/usenet`,
  app config `/mnt/user/appdata`.
- **Notable containers:** Plex (`plexinc/pms-docker`), Emby (`binhex/arch-emby`), Media Sentinel
  (`MediaSentinel`, web UI on :8484).

## Connecting — the gotchas (these cost real time to rediscover)
1. **The Bash sandbox blocks LAN (10.x).** Every ssh/curl/rsync to the box needs
   `dangerouslyDisableSandbox: true` on the Bash call. Internet (npm/pip/web) works without it — only
   private LAN IPs are blocked. Symptom if forgotten: "Connection refused / port 22 unreachable" even
   though the host is up.
2. **Key auth via the ssh-agent.** The authorized key is `~/.ssh/id_ed25519` (fingerprint
   `SHA256:7PHrTHxkKGNKRBzrKsloEo3pxo7tnojKV9oqHGzBIL0` — derived from the *public* key, safe to record).
   It's **passphrase-protected**, so for non-interactive use it must be loaded into the agent: Sean runs
   `ssh-add --apple-use-keychain ~/.ssh/id_ed25519` once (persists via the macOS keychain). If ssh says
   `Permission denied (publickey… no identity pubkey loaded)`, the agent is empty — ask Sean to ssh-add.
   (Claude never handles the passphrase itself.)
3. **Unraid key-persistence quirk.** `/root` is a RAM fs — appending to `/root/.ssh/authorized_keys` is
   ignored by sshd and does NOT persist. Authorized keys live in the **Unraid GUI → Settings → Users →
   root → "SSH authorized keys."** Add new keys there, not via the file.
4. **Connect:** `ssh -o BatchMode=yes -o StrictHostKeyChecking=accept-new root@10.42.1.162 …`. For
   multi-line remote work, pipe a quoted heredoc (`ssh … 'bash -s' <<'REMOTE' … REMOTE`); for paths with
   spaces, prefer `curl -G --data-urlencode`.

Media Sentinel's own deploy loop (rsync → `install-unraid.sh` → :8484) lives in that project's repo
(`~/Projects/MediaSentinel`), not here — this note is the reusable server/connection knowledge.
