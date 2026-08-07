---
name: adobe-app-builder
description: >-
  Adobe App Builder hub — serverless extensions on Adobe I/O Runtime for Experience Cloud (AEM,
  Commerce, Assets, Analytics): Developer Console project/workspace/API bootstrap, `aio app init`
  templates, Runtime actions (webhooks, event providers, journaling consumers, Asset Compute
  workers), App Builder SDKs (State, Files, Events), and the deploy/CI path across Stage and
  Production workspaces. Use when the work targets App Builder or the aio CLI: "scaffold an App
  Builder app", "add a Runtime action", "aio app deploy", "AEM UI extension", "Adobe I/O Events
  webhook", "App Builder CI pipeline", "why is my action returning 502". The workspace owns when
  to reach for App Builder, the engineering done-gates, and the bans; the installed adobe-skills
  plugin owns the CLI mechanics and templates. Not for Adobe *design* tooling, not for general
  serverless architecture (use lead-backend-engineer), and not for Figma work.
aliases: [adobe-app-builder, app-builder, aio]
triggers: [adobe app builder, app builder, aio cli, aio app init, aio app deploy, adobe i/o runtime, runtime action, adobe developer console, experience cloud extension, aem ui extension, asset compute worker, adobe i/o events, api mesh, adobe io state, adobe io files]
tier: hub
domain: engineering
prerequisites: [eng-foundations]
requires: [aio-cli]
defers_to: [framework-13, framework-14, framework-16, eng-foundations]
rigor_role: command-hub
spec_version: "2.2"
---

# Adobe App Builder

Adobe's extensibility platform: serverless actions on Adobe I/O Runtime plus an optional SPA,
deployed per Developer Console **workspace**, wired to Experience Cloud products through API
subscriptions and I/O Events. Practically, it is a constrained serverless stack with Adobe's
identity model (IMS), Adobe's limits, and Adobe's release surface.

This is a **thin hub**. Depth lives in the installed Cursor plugin `adobe-skills/app-builder`,
which holds the CLI invocations, action templates, and troubleshooting trees. The workspace owns
the decision to use App Builder at all, the engineering gates the work must clear, and the bans.
Engineering fundamentals (contracts, idempotency, caching, testing, failure design) come from
[[eng-foundations]]; nothing about serverless suspends them.

> **Tool dependency, preflight first.** Requires the `aio-cli` capability
> ([[capability-registry]]). If the CLI is absent, install it (`npm install -g @adobe/aio-cli`)
> rather than working around it: every Console, init, deploy, and log path runs through it. See
> [[AGENTS]] → "Capability preflight".

## Routing (plugin skills hold the mechanics)

| Need | Plugin skill |
|---|---|
| Create the Console project/workspace, subscribe APIs, pick a template, run `aio app init` | `appbuilder-project-init` |
| Author, deploy, invoke, and debug Runtime actions; State/Files/Events SDK patterns | `appbuilder-action-scaffolder` |
| Build the SPA / Experience Cloud shell UI, React Spectrum surface, extension registration | `appbuilder-ui-scaffolder` |
| Unit and integration tests for actions and UI | `appbuilder-testing` |
| End-to-end tests against a deployed workspace | `appbuilder-e2e-testing` |
| CI/CD, workspace promotion, secrets in the pipeline | `appbuilder-cicd-pipeline` |

Workspace skills that pair with it: [[be-api-design]] for the action's public contract,
[[be-integration-patterns]] for event and webhook semantics, [[devops-ci-cd]] and
[[devops-release-engineering]] for the pipeline, [[sec-authn-authz]] for IMS token handling, and
[[fe-component-architecture]] if the SPA is more than a thin shell.

## When to use App Builder

- The work must run **inside** the Experience Cloud shell, or extend AEM / Commerce / Assets with
  a UI extension or a custom rendition.
- The integration is event-driven off Adobe I/O Events and benefits from Adobe-hosted identity,
  journaling, and delivery.
- The team wants no infrastructure of its own for a small-to-medium integration surface.

## When NOT to use it

- The service is **not** Adobe-facing. A general API or worker belongs on the platform the team
  already operates: route to [[lead-backend-engineer]] and [[lead-devops-engineer]].
- The workload is long-running, stateful, high-throughput, or latency-critical. Runtime actions
  are short-lived with payload and duration limits; fighting them is a platform mismatch, not an
  optimization problem.
- The problem is design tooling or Figma automation. That is the [[figma]] hub.

## Execution protocol

1. **Resolve the context profile** first (`02-shared-references/delivery-playbooks/00-context-profiles.md`).
   Adobe work is usually employer-context: branch and PR, no self-merge, no direct push.
2. **Shape before scaffolding.** Name the extension point, the events consumed and emitted, the
   action contract (inputs, outputs, error taxonomy, idempotency), and the data that must persist.
   Record it as an ADR when the choice is expensive to reverse. This is `/eng shape` with an Adobe
   target, so [[eng]]'s gates apply.
3. **Preflight the CLI and the Console state** (org, project, workspace, API subscriptions) before
   any init or deploy step.
4. **Load the matching plugin skill** for the mechanics, then scaffold or implement.
5. **Wire config correctly**: secrets as workspace-scoped environment/config values, never in
   source, never in action default params committed to the repo. Stage and Production are separate
   workspaces with separate credentials.
6. **Test at the right layer**: unit tests on action logic, integration tests on the SDK and event
   boundary, end-to-end only for the flows a customer actually performs.
7. **Deploy through the pipeline**, Stage before Production, and verify with logs
   (`aio app logs`) plus the action's own structured output.
8. **Hand off**: the release/rollback plan and monitoring to [[devops-release-engineering]];
   durable platform lessons to `08-knowledge/engineering/`.

## Done-gates

Per [#14 Engineering Operating Model](../../01-frameworks/14-engineering-operating-model.md), and
inheriting [[eng]]'s verb gates:

- **Contract named.** Every web action has documented inputs, response shape, status codes, and
  error taxonomy. Web actions are internet-reachable by default; the contract includes who may
  call it.
- **Idempotency stated.** Event consumers and webhook receivers get retried by the platform. Each
  handler is either idempotent or explicitly documented as unsafe to retry, with the mitigation.
- **Limits acknowledged.** Duration, memory, payload, and concurrency limits are named for the
  action, with the behavior at the limit (large-payload redirect, sequence split, queue) chosen on
  purpose rather than discovered in production.
- **Auth verified at the boundary.** IMS token validation and authorization happen in the action,
  not in the SPA. See [#16 Security Operating Model](../../01-frameworks/16-security-operating-model.md)
  and [[sec-authn-authz]].
- **Observability sufficient.** Structured logging with an activation-correlatable id, and an
  alert on the failure mode you just described.
- **Rollback path.** A prior deployment can be restored, or the irreversible step is named in the
  ship plan.

## Absolute bans

- **Never commit credentials.** No client secrets, private keys, IMS tokens, or technical-account
  JSON in the repo, in `ext.config.yaml`, or in committed default params. Secrets are workspace
  config or pipeline secrets.
- **Never ship a `require-adobe-auth: false` web action without its own authorization check.** An
  unauthenticated web action is a public endpoint on your tenant.
- **Never deploy straight to Production to test.** Stage exists; using Production as the first
  integration environment is how customer data becomes the test fixture.
- **Never let the plugin's fast path skip the gates above.** Scaffolding speed is the plugin's
  contribution; the contract, auth, and rollback gates are the workspace's, and they win (see
  [#13 Domain Rigor Stack](../../01-frameworks/13-domain-rigor-stack.md) and [[process-plugins]]).

## Defers-to

- Workspace doctrine wins: [#13 Domain Rigor Stack](../../01-frameworks/13-domain-rigor-stack.md),
  [#14 Engineering Operating Model](../../01-frameworks/14-engineering-operating-model.md),
  [#16 Security Operating Model](../../01-frameworks/16-security-operating-model.md), then
  [[eng-foundations]] and [[eng]].
- Plugin depth (technique only): `adobe-skills/app-builder` (`appbuilder-*` skills) for CLI
  commands, templates, and troubleshooting. Do not restate those mechanics here; they change with
  the CLI.

## Related
- foundation → [[eng-foundations]]
