---
name: pm-platform-api
description: >
  Platform versus product strategy, API as product, integration ecosystem
  design, extensibility patterns, and developer experience for enterprise
  SaaS. Use this skill whenever the conversation touches: deciding whether
  to build a platform vs. product capability, treating APIs as product
  decisions (versioning, deprecation, breaking changes), integration
  ecosystem strategy (native vs. iPaaS vs. partner SDK), webhooks and
  extensibility patterns, enterprise integration table stakes (SSO, SCIM,
  audit logs, data export), platform sequencing decisions, or developer
  experience as product quality. Also trigger on: "platform strategy",
  "API product", "API versioning", "deprecation policy", "webhooks",
  "integration ecosystem", "iPaaS", "Zapier", "Workato", "extensibility",
  "custom fields", "open API", "developer experience", "SSO", "SCIM",
  "audit log", "platformize", "platform vs. product".
aliases: [pm-platform-api]
spec_version: "2.0"
tier: spoke
domain: product
hub: lead-product-manager
prerequisites: [lead-product-manager]
---

# PM Platform & API

Specialist skill for platform strategy, API product decisions, integration
ecosystem, and enterprise extensibility. Part of the enterprise SaaS product
management skill network.

---

## Domain Boundary

This skill owns **the strategic and product decisions around platform
capabilities and integrations** — not the technical implementation.

- **API design execution and REST conventions** → `be-api-design`
- **Integration implementation patterns** → `be-integration-patterns`
- **Auth, SSO, SCIM implementation** → `be-auth-patterns`
- **Launch strategy for platform capabilities** → `pm-enterprise-gtm`
- **Roadmap sequencing of platform vs. feature work** → `pm-roadmap-strategy`

---

## Platform vs. Product: The Core Distinction

**A product** solves a specific problem for a specific user. Success is
measured by whether users accomplish the job.

**A platform** enables others (customers, partners, developers) to solve
their own problems on top of your foundation. Success is measured by whether
the ecosystem built on top is healthy.

The distinction matters for product decisions:

| Dimension | Product Lens | Platform Lens |
|-----------|-------------|---------------|
| Who is the customer? | The end user | The builder on top (developer, admin, partner) |
| What is the output? | Features and workflows | APIs, SDKs, hooks, extensibility |
| Success metric | Task completion, retention | API adoption, integration count, ecosystem health |
| Failure mode | Wrong features for users | Leaky abstractions that prevent builders from succeeding |
| Investment horizon | Quarter-to-quarter | Multi-year foundation |

### The Platformization Decision

**Platformizing is a sequencing decision, not just a technical one.** The
question is not "should we have a platform?" — it's "is now the right time
to invest in platform capabilities vs. continuing to build directly?"

Platform investment is justified when:
- Multiple product features or customer segments need the same underlying capability
- Customers need to integrate your product into their own workflows (true for
  most enterprise use cases)
- Partners or ISVs could multiply your distribution if given the right surface
- The current approach (one-off integrations, custom work) is not scaling

Platform investment is premature when:
- The core product problem isn't solved — building the platform before the
  product means building infrastructure for the wrong thing
- There's only one use case for the capability being platformized
- You're using "platform thinking" to avoid delivering customer value

**The platform trap**: Calling something a "platform strategy" to make an
engineering-heavy investment sound strategic. If there are no concrete use
cases for the platform that couldn't be served by direct features, it's
architecture, not strategy.

---

## API as Product

Every API design decision is a product decision. APIs are the user interface
for developers and integrations — the same design discipline applies.

### API Design Decisions That Are Product Decisions

**Versioning contract**: Will you support v1 indefinitely? What triggers a
major version? The versioning policy is a customer promise. Changing it
breaks trust. Define it before you ship v1, not after.

**Deprecation policy**: When and how will you retire old API versions?
Enterprise customers build integrations that are critical to their operations.
"We deprecated it with 30 days notice" is a product failure, not a
communication success. Industry standard is 12–24 months deprecation period
for enterprise APIs.

**Breaking change definition**: What constitutes a breaking change? Removing
a field is obvious. Changing a field's behavior is less obvious. Changing
a rate limit is often overlooked. Document this explicitly in your API
contract.

**Rate limits**: Not just a technical constraint — a product decision about
what use cases you're supporting. Limits that prevent legitimate customer
workflows are a product bug.

**Consistency over cleverness**: API design that is consistent (predictable
naming, predictable pagination, predictable error responses) is better than
clever design. Inconsistency compounds for every developer who builds on it.

### Failure Mode: The Internal API Trap

Many enterprise SaaS products have "APIs" that were built for internal use
(frontend-to-backend) and later exposed to customers. These APIs are usually:
- Poorly documented
- Inconsistently designed
- Not versioned
- Not treated as a product contract

The result: customers build integrations on top of internal APIs, then break
when you make internal changes. You're now supporting undocumented behavior
as a product commitment.

Prevention: Treat any API intended for external use as a product from the
start, with documentation, versioning, and a deprecation policy.

---

## Integration Ecosystem Strategy

### Build vs. Buy vs. Partner Decision Matrix

| Integration Approach | When to Choose | Trade-offs |
|---------------------|----------------|-----------|
| **Native integration** (built by your team) | Strategic partner where deep integration is a differentiator; high-traffic integration your customers demand | High investment; you own the maintenance; full control over quality |
| **iPaaS-powered** (Zapier, Workato, Boomi, Make) | Long tail of integrations; customers need flexibility to connect your product to their own stack | Faster to support many integrations; quality is variable; customer complexity shifts to them |
| **Partner-built SDK** | SI/GSI partners who build for specific verticals; ISVs who need deep embedding | Partner investment required; quality control is an ongoing concern; ecosystem management overhead |
| **Customer-built via open API** | Customers with engineering resources who have custom needs | Requires a well-documented, stable API; you support the API, not the customer's implementation |

The right answer is usually a combination: native integrations for the 5
strategic partners that represent 60% of customer demand, iPaaS for the long
tail, open API for customers with engineering resources.

### The Long Tail Problem

Enterprise customers have heterogeneous stacks. The top 5 integration requests
cover maybe 40% of accounts. The next 50 cover another 40%. You can't build
50 native integrations — that's why iPaaS connectors exist.

However: the quality of iPaaS integrations is uneven, and customer-built
integrations on iPaaS platforms often break. PM needs to own the connector
quality on major iPaaS platforms, even though the customer "builds" the flow.

---

## Extensibility Patterns

### Pattern Inventory

| Pattern | What It Enables | Enterprise Fit | When to Use |
|---------|----------------|----------------|-------------|
| **Webhooks** | Real-time event push to customer systems; automation, workflow triggers | High — most enterprise customers need event-driven integrations | When customers need to react to product events in their own systems |
| **Custom fields / objects** | Customer-specific data model extensions | Essential — every enterprise has unique data models | When different accounts have different data requirements |
| **Open API (REST/GraphQL)** | Full programmatic access to product data and actions | Essential for enterprise | When customers have engineering resources and custom integration needs |
| **Plugins / extensions** | Third parties extend the product UI or functionality | Advanced — requires developer ecosystem | When partners need to embed capabilities in the product |
| **Embedded mode** | Your product embeds within another product (iframe, SDK) | Specialized | When your product is a component in a larger workflow system |
| **Data export / warehouse sync** | Raw data access for analytics | Common requirement | When customers have data teams who need access to product data |

### Webhooks as a Product Capability

Webhooks are not a technical feature — they are the integration primitive
that makes your product a participant in the customer's workflow ecosystem.

**PM decisions around webhooks:**
- Which events warrant a webhook? (Every significant state change in the
  product is a candidate)
- Delivery guarantees: at-least-once vs. exactly-once; retry policy; failure handling
- Payload schema: versioned? Will you maintain backwards compatibility?
- Security: HMAC signature validation — required, not optional
- Developer experience: webhook testing tools, delivery logs, failure alerting

---

## Enterprise Integration Table Stakes

These are requirements, not features. An enterprise customer cannot fully
adopt your product without them. Missing any of these will cause deals to
stall or churn to spike.

### SSO (Single Sign-On)

**Why it's required**: Enterprise IT does not allow employees to create and
manage their own credentials in every SaaS tool. They need centralized
identity management.

**Minimum viable SSO for enterprise**:
- SAML 2.0 support (the enterprise standard; Okta, Azure AD, ADFS)
- OIDC support (modern standard; Google Workspace, newer IdPs)
- JIT (Just-In-Time) provisioning — users created on first SSO login
- Attribute mapping (IdP user attributes → product roles)

**Common PM failure**: Shipping "SSO support" as a binary capability without
addressing the multi-tenant complexity. Enterprise customers have multiple
IdP configurations across subsidiaries — your SSO needs to support multiple
configurations per account tier.

### SCIM (System for Cross-domain Identity Management)

**Why it's required**: IT needs to manage user lifecycle (onboarding,
offboarding, role changes) centrally, not per-application.

SCIM 2.0 required actions:
- User create (from IdP provisioning)
- User deactivate / deprovision (offboarding — this is the critical one;
  a former employee with active access is a security liability)
- Group sync (map IdP groups to product roles)
- Attribute push (keep user attributes in sync)

**PM anti-pattern**: Shipping SSO without SCIM. SSO handles login; SCIM
handles lifecycle. Enterprise IT needs both. A company that grows from 10
to 1000 users needs SCIM; manual deprovisioning doesn't scale.

### Audit Logs

**Why it's required**: Enterprise compliance requirements (SOC 2, ISO 27001,
internal audit functions) require evidence of who did what, when.

Audit log minimum requirements:
- Covers all user actions (data access, configuration changes, admin actions)
- Immutable (users can read but not modify or delete)
- Exportable (SIEM integration, CSV/JSON export)
- Configurable retention (typically 1–7 years)
- Searchable/filterable by actor, action type, timestamp, resource

**PM anti-pattern**: Building audit logs as a UI feature only. Enterprise
customers need the log data in their own SIEM systems. API access to audit
logs is as important as the UI.

### Data Export

**Why it's required**: Enterprises don't want to be locked in. They need to
be able to take their data with them, and they need to provide their data
teams with access.

Minimum:
- Complete data export (all customer data, not a subset)
- Machine-readable format (JSON/CSV, not PDF)
- Bulk export (not record-by-record)
- Automated/scheduled export option (for data warehouse sync)
- API-accessible (so customers can build their own pipelines)

---

## Platform Sequencing

### When to Build the Platform Layer

The classic sequencing mistake: building the platform before enough is
known about what products will be built on it. Premature platformization
produces infrastructure for the wrong abstraction.

**Platform sequencing rule**: Build at least two concrete products (features
or workflows) before extracting the shared layer into a platform capability.
This gives you real requirements, not speculative requirements.

**Signs you're ready to platformize**:
- Two or more product surfaces need the same capability and are solving it
  separately (duplication is the signal)
- Customers are asking to integrate and the current approach is custom work
- Engineering is spending more time on per-customer customization than on
  product development

**Signs you're platformizing prematurely**:
- The platform capability has one known use case
- The primary motivation is "this is cleaner architecture" rather than
  concrete customer or product demand
- Nobody has defined who the platform customer is

---

## Developer Experience as Product Quality

The quality of your developer experience IS the quality of your platform
product. Bad docs, inconsistent APIs, and poor error messages are product
bugs, not documentation bugs.

### DX Quality Checklist

**Documentation**:
- [ ] Getting started guide that works end-to-end in under 30 minutes
- [ ] API reference that is generated from the code (so it's always current)
- [ ] Real-world examples (not toy examples) for common use cases
- [ ] Error message documentation (what each error means and how to fix it)
- [ ] Changelog with breaking change notices clearly marked

**SDKs**:
- [ ] Officially supported SDKs for the top 2-3 languages used by your customers
- [ ] SDK is kept in sync with the API (version-matched)
- [ ] SDK is open source when possible (trust signal + community contribution)

**Sandbox environment**:
- [ ] Developers can test without affecting production data
- [ ] Sandbox is reset-able
- [ ] Test data is available out of the box

**Error messages**:
- [ ] Errors are specific ("field 'account_id' is required, was missing")
  not generic ("validation error")
- [ ] Errors include actionable guidance ("see docs.example.com/api/errors/E123")
- [ ] Rate limit responses include retry-after headers

---

## Cross-Hub References

- **API design execution** → `be-api-design`: when the API strategy is
  defined and needs to be implemented
- **Integration implementation** → `be-integration-patterns`: when the
  integration ecosystem strategy needs to be built out
- **SSO/SCIM auth implementation** → `be-auth-patterns`: PM defines the
  requirements; backend implements the protocols
- **AI/LLM capabilities as platform features** → `ds-nlp-llm`: when building
  AI capabilities that need to be exposed via API
- **Launch strategy for platform features** → `pm-enterprise-gtm`: table
  stakes checklist, launch readiness
- **Platform roadmap sequencing** → `pm-roadmap-strategy`: foundation-before-
  features logic, platform vs. feature portfolio tradeoffs

## Related
- hub → [[lead-product-manager]]
