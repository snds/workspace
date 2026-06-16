---
tags: [centric, plm, codebase, java, dojo, react, migration, analysis]
created: 2026-04-28
updated: 2026-04-28
status: stable
confidence: high
sources: [07-projects/02-centricPLM/CLAUDE.md]
related_skills: [fw-dojo, lead-backend-engineer, lead-frontend-engineer]
related_projects: [02-centricPLM]
---

# Centric PLM Codebase — Confirmed Tech Stack and Structure

What's actually in the Centric 8 PLM codebase. This is based on direct analysis of the Bitbucket source, not inference. Confidence levels are indicated.

---

## Confirmed Technology Stack

| Layer | Technology | Confidence |
|-------|-----------|-----------|
| Backend runtime | Java 21 on WildFly (JBoss) | Confirmed |
| Backend framework | Spring Boot | Inferred |
| ORM | Hibernate/JPA | Inferred |
| Frontend (legacy) | Dojo Toolkit SPA | Confirmed |
| Frontend (modern) | React + TypeScript + MobX | Confirmed |
| Databases | Oracle, PostgreSQL, SQL Server, MongoDB | Confirmed |
| Messaging | Apache Kafka, RabbitMQ/ActiveMQ | Confirmed |
| Frontend build | Webpack (custom config) | Confirmed |
| Containers | Docker + Kubernetes | Confirmed |
| REST API | v2, JSON, Swagger docs | Confirmed |
| GraphQL API | PI-PublicGraphqlApi module | Confirmed |
| Build system | Gradle (Groovy DSL) | Confirmed |
| Workflow engine | Camunda BPM | Confirmed |
| Design system | @centricsoftware/design-system (React, Vite, Storybook) | Confirmed |

---

## The Dual-Frontend Problem

Centric PLM has two co-existing frontend technologies:

**Dojo Toolkit (legacy SPA):**
- AMD module system (define/require)
- Dijit widget library for UI components
- dgrid for data tables (the 90-table surface we audited)
- Tightly coupled widget lifecycle
- No modern build tooling assumptions

**React + TypeScript + MobX (modern):**
- Component-based
- MobX for state management (not Redux)
- The `@centricsoftware/design-system` package is React-based
- Built with Vite + Storybook for component development

**The migration context:** The design system work exists at this boundary. The goal is to eventually migrate off Dojo entirely. The `fw-dojo` skill has AMD→ESM migration tables, Dijit widget lifecycle docs, and dgrid→TanStack Table patterns specifically to support this.

---

## Analysis Project Structure

The codebase analysis project in `07-projects/02-centricPLM/` follows eight sequential phases:

1. **Systems Architecture** — 30,000-foot view of how modules connect
2. **Frameworks & Libraries** — dependency audit (what's used, versions, risks)
3. **Business Logic & Domain Model** — PLM domain entities and workflows
4. **Information Architecture** — how information is organized across the app
5. **User Experience** — UI inventory (the 90-table audit lives here)
6. **Back-end Architecture** — API surface mapping
7. **Security & Compliance** — auth, data handling, compliance surface
8. **Performance & Scalability** — bottlenecks, optimization opportunities

Findings go in `findings/` organized by phase number. The `c8-analysis/` and `design-system-analysis/` directories are **read-only reference copies** — never modify them.

---

## Key Domain Concepts

Centric PLM manages the lifecycle of physical products. The domain has these core concerns:
- **BOM (Bill of Materials)** — hierarchical structure of a product's components
- **Workflows/approvals** — multi-stage sign-off chains for product decisions
- **Supplier collaboration** — external-facing data sharing with supply chain partners
- **Quality and compliance** — regulatory requirements (especially for Food & Beverage vertical)
- **Spec management** — design specifications for garments, formulas, packaging

The data model has 20+ entities with complex relationships. The schema supports multiple database backends (Oracle, PostgreSQL, SQL Server) — this is a cross-DB portability requirement, not a microservices pattern.

---

## Storybook Reference

Internal Storybook for `@centricsoftware/design-system`:
- **URL:** `http://design-dev.centricsoftware.com`
- **Access:** Internal only, DNS-gated (not accessible outside Centric network)

---

## Important Constraint for Analysis Work

All output from analysis sessions must be written in **plain English with UX/design terminology**. Sean is the UX lead — not a developer. Technical concepts need a one-sentence explanation when they're unavoidable. Mermaid diagrams and structured tables are preferred over prose-heavy technical descriptions.
