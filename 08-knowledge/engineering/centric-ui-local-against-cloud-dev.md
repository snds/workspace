---
tags: [knowledge-vault, engineering, centric-ui, cloud-dev, debugging]
created: 2026-07-20
updated: 2026-07-20
---

# Running centric-ui locally against the cloud dev backend

Hard-won from a full diagnostic loop on 2026-07-20. Running the `centric-ui` FE on a laptop against the
**cloud dev** backend (instead of the `centric-service` Docker Compose stack) is a *nominally supported
but effectively untrodden* path — the docs describe it, and it does not work as described. Three separate
traps, each of which fails in a way that points at the wrong layer.

**No secrets in this entry** — per [[feedback-infra-ip-disclosure]], API keys/tokens stay out of all
notes. Values live only in the gitignored `.env.local`.

---

## The single most useful diagnostic rule

`docs/system-architecture.md` §5 documents the backend's validation order:

```
1. x-api-key    → 401
2. tenant auth  → 403
3. Bearer       → passed through
```

**A 401 from a centric-ui backend call means the API key. Always.** Not the Keycloak token, not the
tenant. This inverts the intuition — "401 Unauthorized" reads like a login problem, and the response body
compounds it by naming the *path*:

```json
{ "status": 401, "message": "Unauthorized API path: /schema-registry-service/v1/schema" }
```

That message means *"this api-key is not authorized for this path"*, **not** "this path is wrong". Chasing
the path (proxy rewrites, prefix stripping) is a dead end — see trap 2. A 403 would be the tenant.

**Symptom shape:** the app loads and authenticates fine; the sidebar collapses to just "Home" and the
dashboard stat tiles vanish, because both derive from backend calls (`record-service` `NavMenuItem` →
sidebar; `schema-registry-service` schema list → tiles). Mock-backed widgets keep rendering
(`VITE_DASHBOARD_USE_MOCK_*` default `true`), so the page looks *half* alive, which reads like a data-sync
problem rather than an auth one. It is not a tenant-sync problem.

---

## Trap 1 — the documented API key is the LOCAL-COMPOSE key

`docs/local-setup.md` instructs: *"Set the API key (required for backend requests) — the key is in
`.env.cloud.example`"*, and `.env.cloud.example` carries a hardcoded value under a
`# Cloud dev backend configuration` header. **That value is the local Docker-stack key.** Cloud dev uses a
different one, and following the docs exactly produces the 401 above.

**Where to get the right one:** `VITE_*` vars are build-time inlined by Vite, so the *deployed* app's
bundle carries the correct key and sends it on every request. Read it from the deployed site's own
DevTools → Network → any `/record-service/` or `/schema-registry-service/` request → Request Headers →
`x-api-key`. Self-service, no BE ticket needed. Put it only in `.env.local` (gitignored). Grab
`x-cpes-service-name` at the same time if the service identity also differs.

Both bad values in `.env.cloud.example` date from the original `setup CI/CD` commit (2026-03-06) and have
never been revisited.

## Trap 2 — the dev proxy table is only half cloud-capable

In dev, `app/lib/resolveServiceBaseUrl.ts` **hard-returns `""` whenever `import.meta.env.DEV`**. So under
`npm run dev` every `VITE_*_BASE_URL` is ignored, all BE traffic goes same-origin, and the **Vite proxy
table in `vite.config.ts` is the only thing deciding where requests land.** Setting cloud URLs in
`.env.local` does nothing on its own — a genuinely non-obvious inversion.

That table has two helpers: `localServiceProxy(port)` (hardcoded localhost) and
`cloudOrLocalServiceProxy(cloudBaseUrl, port)` (cloud when the env var is set, else the local port). As of
2026-07-20 the cloud-capable one is applied only to `document-service` and `flavour-provisioning` — the
latter added with the helper itself in #160 (2026-07-10) for that feature alone. **`record-service`,
`schema-registry-service` and `workflow-service` remain localhost-only**, so cloud dev is structurally
impossible for the three services that matter most until they are converted. Swapping them to
`cloudOrLocalServiceProxy` is non-breaking — each still falls back to its compose port when the env var is
unset.

**Path shape is NOT the problem** (worth recording, because it looks like it is): production's
`server.mjs` proxies these same routes with **no `pathRewrite`** — only `/keycloak-admin` rewrites. The
service-name prefix is part of the spec path and is expected upstream. A dev proxy that forwards
`/record-service/v1/...` unchanged already matches production.

## Trap 3 — Keycloak redirect URI: three values, none agreeing

The cloud VMS realm's `react` client accepts **only `http://localhost:3000/*`**. Meanwhile
`vite.config.ts` defaults the dev server to **8082**, and `.env.cloud.example` hardcodes **5173**. All
three disagree; the example file's value works nowhere.

Probe the realm directly rather than guessing — an unauthenticated GET to the authorization endpoint
returns the `Invalid parameter: redirect_uri` page for a rejected URI and a login page for an accepted
one, so candidates can be tested in seconds without credentials:

```
{keycloak}/realms/VMS/protocol/openid-connect/auth?client_id=react&response_type=code&scope=openid&redirect_uri={urlencoded}
```

`localhost` only — `127.0.0.1` is rejected even on the accepted port (PKCE is origin-specific, and
`app/config/keycloak.ts` normalises `127.0.0.1` → `localhost` for exactly this reason). Leave
`VITE_KEYCLOAK_REDIRECT_URI` **unset** so it derives from the browser origin, and run the dev server on
the accepted port: `PORT=3000 npm run dev -- --port 3000` (`scripts/run-dev.mjs` passes argv through to
`react-router dev`; `PORT` additionally steers its port-cleanup step).

---

## Known-unreachable

`workflow-service` has **no cloud dev hostname** — `workflow-service.internal.app.dev.centricsoftware.io`
does not resolve (curl exit/HTTP 000, versus 401 for the services that do exist). It is not a config
problem and cannot be fixed locally; BE must expose it or supply the real host. Until then workflow
features fail against cloud dev while everything else works. **Test hostnames before adopting them** —
401 means the host exists and is auth-gated; 000 means no such host.

## Unauthenticated probing has a hard limit

Ingress rejects tokenless requests *before* path routing, so every candidate path returns a bare 401 with
an empty body. Path shapes cannot be discriminated by curl from a laptop. The distinguishing message only
appears **with** a valid token — i.e. from the browser's Network tab. When curl stops discriminating,
switch to the authenticated browser rather than inferring from status codes alone.

## Related

- [[centric-vms-frontend-stack]] — other centric-ui/ds-docs stack quirks
- [[feedback-credential-scoping]] — which git/GitHub identity to use on the Centric laptop
- [[feedback-infra-ip-disclosure]] — why no key values appear in this entry
