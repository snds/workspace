---
type: fact
description: Cloud "Unauthorized API path" on centric-ui needs VITE_API_KEY + matching VITE_SERVICE_NAME — not a GitHub PAT
created: 2026-09-17
confidence: high
---

**`VITE_API_KEY` / `VITE_SERVICE_NAME` in centric-ui `.env.local` are the service gateway identity**
(`x-api-key` + `x-cpes-service-name`). Wrong or local-compose values against cloud hosts yield
`401 Unauthorized API path: /record-service/…`.

- **Not a GitHub PAT.** A real `ghp_…` does not clear that error.
- **GitHub Actions secret named `VITE_API_KEY`** stores the *cloud API key value* for CI — still not a PAT.
- **Get the pair from:** team vault, DevTools on a working cloud UI (Network → `/record-service/` headers), or BE.
- **Local compose** often uses `cpes-dummy` / `DUMMY-123` (or similar); that pair is wrong for cloud.
- **GH PAT is a different job:** `docker login ghcr.io` with `read:packages` to pull backend images (`docs/local-setup.md`).
- Cloud Keycloak `react` client expects **`http://localhost:3000`**; local default UI port is **8082**.

Sources: centric-ui README / `.env.local` comments / 2026-08-11 session with BE auth confusion.
