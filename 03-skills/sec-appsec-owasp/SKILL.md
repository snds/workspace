---
name: sec-appsec-owasp
description: >
  Application security against the exploit classes that actually ship in enterprise B2B
  SaaS. Owns the class-to-control map: validate at the boundary and encode at the sink,
  injection, XSS and CSP, CSRF and CORS, SSRF through webhooks and renderers, unsafe
  deserialization, file upload and archive handling, multi-tenant leakage paths that
  scanners cannot see, unbounded work, and the secure SDLC wiring that decides which
  check runs at which stage. Includes a diff-review checklist of greppable danger signals
  and the triage rules for scanner findings. Use when handling untrusted input, rendering
  user content, fetching a user-supplied URL, accepting uploads, or hardening an app.
  Triggers: owasp, injection, sql injection, xss, csrf, ssrf, input validation, output
  encoding, content security policy, sanitization, secure sdlc, deserialization, file
  upload, path traversal, xxe, sast, dast.
aliases: [sec-appsec-owasp]
triggers: [owasp, injection, sql injection, xss, csrf, ssrf, input validation, output encoding, content security policy, sanitization, secure sdlc, deserialization, file upload, path traversal, xxe, sast, dast, csv injection]
tier: cross-cutting
hub: lead-security-architect
prerequisites: [lead-security-architect]
related: [be-security-posture, be-api-design, fe-api-integration, sec-threat-modeling, sec-authn-authz, sec-supply-chain]
domain: security
surfaces: ["*"]
defers_to: [framework-16]
rigor_role: load-chain
spec_version: "2.2"
---

# Security: Application Security

Almost every exploit class in this spoke reduces to one of five confusions: data treated as code,
data treated as identity, a boundary treated as trusted, a default treated as safe, or work treated
as bounded. Learn the five and the individual acronyms stop being a list to memorize.

This spoke owns the **class-to-control map** and the **SDLC wiring**: which control eliminates a
class rather than merely reducing it, and which check at which stage proves the control is present.
It covers the build half of stage 2 and the scanning of stage 3 in [[16-security-operating-model]].

Governed by [[lead-security-architect]]. Backend code-level treatment with language-specific examples,
security headers, and rate-limit algorithms lives in [[be-security-posture]]; client-side integration
patterns live in [[fe-api-integration]]; access control is owned entirely by [[sec-authn-authz]] and is
not re-derived here.

---

## The five root causes

| Root cause | What goes wrong | Classes it produces | The control that eliminates it |
|---|---|---|---|
| Data treated as code | User input is parsed by an interpreter as instructions | SQL and NoSQL injection, command injection, template injection, XSS, prompt injection | Separate the channel: parameterized APIs, context-correct encoding at the sink |
| Data treated as identity | A value the client controls is used as a claim | Broken access control, IDOR, tenant leakage, forged webhooks | Derive identity from a verified credential ([[sec-authn-authz]]) |
| A boundary treated as trusted | Internal, partner, or "our own client" data is accepted unchecked | SSRF, deserialization, mass assignment, second-order injection | Validate at every boundary crossing, including internal ones |
| A default treated as safe | Framework or platform defaults are permissive | Misconfiguration, verbose errors, open storage, permissive CORS, debug endpoints | Explicit deny-first configuration, checked in code review and by scan |
| Work treated as bounded | An input controls how much work the server does | Denial of service, cost amplification, decompression and regex bombs | Caps on every dimension: size, depth, page, time, concurrency |

Use these as the review lens. When someone reports a finding, name the root cause before you name the
fix, because the same root cause almost always appears more than once in the same codebase.

---

## Validate at the boundary, encode at the sink

Two separate obligations that are commonly collapsed into one, which is why sanitize-on-input keeps
failing.

**Validate at the boundary.** Parse the request into a typed structure before any business logic
runs. Allowlist rather than blocklist: enumerate the shapes you accept and reject everything else.
Reject unknown fields instead of ignoring them, which closes mass assignment. Bound every numeric and
every collection. Validation answers "is this a well-formed request?" and nothing more.

**Encode at the sink.** Escaping depends entirely on where the value is going, and the boundary does
not know. Encoding at input time produces double-encoded data, breaks legitimate content, and still
misses the sink that needed a different encoder.

| Sink | Correct control | Common mistake |
|---|---|---|
| HTML text | Framework auto-escaping | Bypassing it with a raw-HTML escape hatch |
| HTML attribute | Attribute-context encoding, quoted attributes | Unquoted attribute interpolation |
| JavaScript context | Serialize as JSON data, never build code | Interpolating a value into an inline script |
| URL or query parameter | URL encoding, plus scheme allowlist | Accepting `javascript:` or `data:` in a link |
| CSS | Avoid dynamic CSS values entirely | Interpolating into `style` |
| SQL and NoSQL | Parameter binding, typed query builders | String concatenation, or a raw escape hatch on a "safe" value |
| Shell | Do not use a shell; exec with an argument array | Building a command string |
| LDAP, XPath, and other query languages | Library-provided escaping or parameterization | Manual quoting |
| Server-side template | Pass values as context data, never into the template source | Rendering a user-supplied template |
| Log line | Structured fields, newline and control-character stripping | Concatenating user text into a log message |
| Spreadsheet export | Prefix formula-leading characters, or quote the cell | Writing raw cell values, which yields formula injection in the customer's spreadsheet |
| File download | Sanitized filename, explicit `Content-Type`, `Content-Disposition: attachment` | Reflecting a user-supplied filename or content type |

The spreadsheet row deserves attention in B2B products specifically: exports are a core feature, the
victim is your customer's finance or operations user, and no browser control protects them.

---

## Cross-site scripting and CSP

Three delivery paths, one root cause. Stored XSS enters through persisted content, reflected XSS
through a parameter echoed into the response, and DOM XSS entirely in the browser through a sink like
`innerHTML` or a framework escape hatch.

The fix ladder, in order:

1. **Let the framework escape.** Modern templating is safe by default. The vulnerability is
   essentially always in the place where a developer deliberately turned it off.
2. **Sanitize rich content with an allowlist library at render time.** Any product with a comment,
   description, or notes field will eventually need this. Never write your own sanitizer, and never
   sanitize with a regex.
3. **Treat SVG, HTML email templates, and Markdown as executable.** SVG uploads are a stored XSS
   vector unless served from a separate origin with a restrictive content type. Markdown renderers
   allow raw HTML unless configured otherwise.
4. **Serve user-uploaded files from a distinct origin.** Same-origin uploads mean any file that
   renders as HTML inherits your session.
5. **Add a Content-Security-Policy as defense in depth**, not as the primary control. Nonce-based
   `script-src`, no `unsafe-inline` for scripts, `frame-ancestors` set, and a report endpoint. Roll it
   out in report-only mode first and read the reports; header construction detail lives in
   [[be-security-posture]].

Prompt injection belongs in this family for any product with an LLM feature. Model output is
untrusted input: never render it as raw HTML, never pass it to a shell or a query, and never let it
select a privileged tool call without a policy check. The confused-deputy shape is identical to
classic injection, so the control shape is identical too.

---

## CSRF, CORS, and browser state

**CSRF applies whenever the browser attaches credentials automatically**, which means cookie-based
sessions. Controls: `SameSite=Lax` or `Strict` on session cookies as the baseline, plus a
synchronizer or double-submit token on state-changing requests, plus a check that state changes never
ride on `GET`.

**Bearer-token APIs are largely immune**, because the browser does not attach an `Authorization`
header on its own. The trap is a hybrid: a cookie-authenticated API that also accepts a bearer token,
or a cookie-based session that a fetch call uses with `credentials: 'include'`. Hybrids reintroduce
CSRF quietly, so name the authentication mechanism per route and know which routes need the token.

**CORS is not authorization.** A permissive CORS policy does not create a vulnerability by itself,
and a restrictive one does not protect an endpoint from a non-browser client. Still get it right:
never reflect the `Origin` header, never combine a wildcard origin with credentials, and keep an
explicit allowlist. Then remember that `curl` ignores all of it, so the endpoint's own authorization
is what actually protects the data.

---

## Server-side request forgery

SSRF matters more in enterprise B2B SaaS than in consumer products, because the feature list is full
of legitimate reasons to fetch a URL the customer supplies.

Trigger surfaces to inventory in your own product:

- Outbound webhooks, where the customer chooses the destination.
- URL-based imports, integrations configured by URL, and OAuth or SAML metadata endpoints.
- Server-side renderers: PDF generation, screenshot and preview services, HTML-to-document
  converters, and headless browsers.
- Image proxies, avatar fetchers, and link unfurlers.
- LLM tool use, retrieval over customer-supplied sources, and plugin-style extensions.

Controls, layered because any single one has bypasses:

1. **Allowlist by destination** where the product allows it. Customer-configured webhooks usually do
   not, so the remaining controls carry the weight.
2. **Resolve, then validate, then connect to the resolved address.** Validating a hostname and then
   handing the URL to an HTTP client re-resolves the name and loses the check.
3. **Block link-local, loopback, private, and metadata ranges** on the resolved address, for every
   redirect hop, and refuse to follow redirects across a scheme or into a blocked range.
4. **Give outbound fetches their own network identity**: a dedicated egress proxy or a subnet with no
   route to internal services and no instance credentials attached.
5. **Cap the response**: size, time, redirect count, and content type. An unbounded fetch is also a
   denial-of-service primitive.
6. **Never echo the response body verbatim** to the caller. Blind SSRF is far less useful to an
   attacker than one that returns content.

Cloud metadata specifics are covered in [[be-security-posture]].

---

## Deserialization, uploads, and archives

An under-reviewed surface in products that accept customer files, which is most of them.

- **Never deserialize untrusted data into arbitrary types.** Language-native serialization formats
  that can instantiate classes are remote code execution primitives. Use a data-only format and parse
  into a declared schema.
- **Disable external entity resolution in XML parsers.** XXE turns a document upload into file read
  and SSRF. Any product still accepting XML for imports or SAML needs this verified explicitly.
- **Determine type by content, not by claim.** Check magic bytes, do not trust the extension or the
  supplied content type, and re-encode images rather than passing originals through.
- **Bound decompression.** Enforce a limit on the uncompressed size and the entry count of any
  archive before extracting it, and reject entries whose normalized path escapes the destination or
  that are symlinks.
- **Generate storage paths yourself.** Never build a filesystem or object-store path from a
  user-supplied name. Store the original name as metadata only.
- **Scan and quarantine** where the file is later shared with other users, because your product may
  otherwise become a malware distribution channel between your customer's employees.

---

## Multi-tenant leakage paths that scanners cannot see

Automated tools reason about a single request. These classes live between requests, which is why they
survive a clean scan and appear in a customer's penetration test.

| Path | The leak | The check |
|---|---|---|
| Cache | A key omits tenant or principal, so one tenant serves another's cached response | Two-tenant test on the same logical key, at every cache layer including the CDN |
| Search index | Documents from multiple tenants share an index with no enforced filter | Query as tenant A with terms that only match tenant B content |
| Background jobs and queues | A job is enqueued with a payload but loses the caller's scope on execution | Assert the worker re-derives scope, and test a job whose payload names another tenant |
| Exports and reports | A long-running export resolves references after the fact, without re-checking scope | Request an export referencing a foreign id and require failure |
| Webhook delivery | An event is fanned out to subscribers across tenants, or contains fields the recipient may not see | Assert payload contents and destination are both tenant-scoped |
| Email and notifications | Templates render fields from a joined query broader than the recipient's rights | Review the template's data source, not just the template |
| Error responses and stack traces | Messages disclose identifiers, schema, or another tenant's values | Assert production error bodies are generic and structured |
| Analytics and telemetry | Events carry customer content into a third-party tool with a different access model | Review the event schema for content fields, not just identifiers |
| AI features | Retrieval or context assembly pulls documents without the caller's scope | Two-tenant retrieval test, and assert the scope is applied in the retrieval query |

The enforcement point for all of these belongs to [[sec-authn-authz]]. What this spoke owns is the
inventory: knowing that these nine paths exist and must each be checked, because the feature that
introduces them rarely looks like an access-control change.

---

## Unbounded work

Availability failures in SaaS are usually accidental self-inflicted amplification rather than a
volumetric attack.

- Cap page size and total offset. Reject rather than silently clamping, so clients notice.
- Cap query depth and complexity for GraphQL, and cap the count of expensive nested fields.
- Cap request body size, upload size, field length, and array length at the boundary.
- Cap concurrency per tenant, so one customer's batch job cannot consume the pool.
- Move expensive operations (exports, reports, bulk imports) to async jobs with a queue and a quota,
  not a synchronous request with a long timeout.
- Avoid catastrophic backtracking in regular expressions applied to user input, and time-bound any
  regex that must be dynamic.
- Rate limit by principal first, then by tenant, then by address. Algorithm selection lives in
  [[be-security-posture]] and the API surface detail in [[be-api-design]].

---

## Secure SDLC wiring

Stage 3 of [[16-security-operating-model]] requires scanning with triage. Wiring matters more than
tool choice: a check at the wrong stage is either noise or too late.

| Stage | Check | Catches | Misses |
|---|---|---|---|
| Design | Threat model ([[sec-threat-modeling]]) | Missing controls, wrong trust assumptions, whole-class omissions | Implementation defects |
| Pre-commit | Secret scan, formatter, lint rules for dangerous APIs | Committed credentials, known-bad calls | Anything requiring context |
| Pull request | Human review against the model, targeted SAST on the diff | Missing enforcement points, unsafe sinks, misuse of an escape hatch | Runtime and configuration issues |
| CI | Full SAST, dependency and container scan ([[sec-supply-chain]]) | Known vulnerable code patterns and dependencies | Access control, business logic, chained weaknesses |
| Pre-release | DAST against an authenticated deployment, configuration and header audit | Misconfiguration, missing headers, exposed endpoints | Logic flaws requiring domain knowledge |
| Runtime | Auth anomaly and denial signals, integrity checks, error-rate alerting | Exploitation in progress | Nothing that is never exercised |

What tools genuinely cannot find: broken access control, tenant isolation gaps, business-logic abuse,
and chained weaknesses. Those need the model, the review, and the two-tenant tests. Never let a green
pipeline stand in for them.

**Triage rules.** Every finding gets exactly one disposition, and there is no fourth option:

- **Fix**, with the change in this release for high and critical on the changed surface.
- **Waive**, with an owner, a stated reason, and an expiry date. An expired waiver fails the build.
- **False positive**, with a suppression scoped to the specific line or rule, never a global disable.

CI mechanics and gating configuration belong to [[devops-ci-cd]]; the policy above belongs here.

---

## Diff review checklist

A reviewer's grep list. Each pattern is legitimate somewhere, and each deserves an explicit sentence
in the pull request explaining why it is safe here.

- Raw or string-built queries, and ORM raw escape hatches.
- Any raw-HTML render path or framework escaping bypass.
- Dynamic code execution, dynamic template compilation, or a shell invocation with a string command.
- An outbound fetch whose URL derives from a request, and any redirect-following client.
- Deserialization of a request body into a language-native object graph, and XML parsing.
- File writes or reads whose path includes request data.
- Verification disabled: TLS verification off, signature checks skipped, algorithm unpinned.
- Wildcard or reflected CORS, permissive cookie flags, missing `SameSite`.
- A new route, resolver, job, or export that reaches data, checked against the enforcement point.
- Type-checker or linter suppressions near an authorization or validation call.
- New environment variables, feature flags, or config defaults that are permissive when unset.
- Debug, health, or metrics endpoints added without authentication.

---

## Done-gates

Before application-security work is ready for review:

- Every new or changed input is **validated at the boundary** with an allowlist schema that rejects
  unknown fields, and the caps are explicit.
- Every new sink uses the **correct encoder for its context**, and any escaping bypass is justified in
  the pull request.
- New fetch, upload, deserialization, or export paths have their **class-specific controls** in place,
  named in the review.
- The **multi-tenant leakage inventory** was walked for the paths this change touches, with a test for
  each that applies.
- Scanners for the changed surface **pass or have dispositioned findings** with owners and expiries.
- Production **error responses are generic**, and logs contain no credential or payload material.
- At least one **detection signal** exists for the new risk class, satisfying stage 4.
- Anything accepted rather than fixed is in the **accepted-risk register** with an expiry.

---

## Absolute bans

- Building a query, command, path, or template by concatenating request data.
- Sanitizing on input and calling the sink safe.
- Writing your own HTML sanitizer, escaping routine, or signature verification.
- Disabling TLS verification, signature checks, or a scanner to make something pass.
- Following redirects into private address space on a user-supplied fetch.
- Extracting an archive without size, count, and path checks.
- Serving user-uploaded content from your application origin.
- Returning stack traces, SQL text, or internal identifiers in a production error body.
- Treating a clean scan as evidence that access control and tenant isolation are correct.

---

## Defers-to

- **Framework [[16-security-operating-model]] wins** on pipeline order, done-gates, and bans.
- **Code-level depth defers to [[be-security-posture]]** (language examples, headers, rate limiting)
  and to [[fe-api-integration]] on the client side. Access control defers entirely to
  [[sec-authn-authz]]; pipeline and dependency controls to [[sec-supply-chain]].
- **The Cursor `review-security` plugin detects; this spoke decides.** Its findings enter the triage
  table above. A finding it cannot produce, such as a tenant-isolation gap, is still your obligation,
  so never treat its clean pass as a done-gate.

## Related
- hub → [[lead-security-architect]]
- governs → [[be-api-design]] · [[fe-api-integration]]
- peer ↔ [[sec-threat-modeling]] · [[sec-authn-authz]] · [[sec-supply-chain]]
