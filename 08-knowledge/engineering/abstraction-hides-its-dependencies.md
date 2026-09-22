---
tags: [engineering, design-systems, dependencies, encapsulation, bundle]
created: 2026-09-21
updated: 2026-09-21
status: validated
confidence: high
sources:
  - "Parnas, On the Criteria To Be Used in Decomposing Systems into Modules (1972) — hide decisions likely to change"
  - "npm peerDependencies: a peer is a shared singleton the consumer provides; it does not install the library's private dependencies"
  - "Vite library externalization: peers are packages where a second copy is a correctness bug (React); a stateless widget library is a dependency or is bundled"
related_skills: [eng-foundations, ds-advisor, lead-frontend-engineer, fe-component-architecture]
related_projects: []
relations:
  builds-on: ["[[contracts-first-delivery]]", "[[cds-host-consume-order]]"]
---

# An abstraction hides its dependencies

## For future agent

- **TL;DR:** A host that consumes a design system does not declare the libraries inside components it does not import. Peers are shared singletons (React). Widget libraries stay behind the package. An unmet peer is not a reason to grow the host `package.json`.
- **Key claims:**
  - *Timeless:* A dependency is part of the boundary. If the abstraction is doing its job, swapping the library inside it does not change the consumer's manifest.
  - *Timeless:* `peerDependencies` exist so two copies of a singleton cannot load (React, React DOM, a plugin host). A second copy of a date picker or OTP field is not a correctness bug. Those are `dependencies` of the system, or they are bundled.
  - *Timeless:* A barrel `export *` evaluates every re-export. Putting an unused widget on that barrel, then making the host install it, is how the widget enters the consumer bundle.
  - *Timeless:* Optional integrations use a deep export plus `peerDependenciesMeta.optional`, and they stay off the package barrel. The host installs that peer only when its own code imports the deep path.
  - *Dated 2026-09-21:* A host consume PR added two widget packages so vendored peers would resolve. Review rejected it: the host does not need to know CDS's libraries, and the extra direct dependency violates encapsulation and bloats the graph. The reply that explained the peer was the wrong boundary. Remove the host deps. Deep-import `@scope/ui/<name>` so the barrel is never evaluated.
- **As of:** 2026-09 · **Status:** current

---

## The rule

| Question | If yes | If no |
|---|---|---|
| Would two copies misbehave (hooks, context, a single runtime)? | Peer. The host already depends on it. | Not a peer. |
| Does this application import the package itself? | Direct dependency is honest. | Do not add it. |
| Is the import only inside the design system, on a component this app does not use? | The system owns it. | — |
| Must the widget be optional for hosts that never render it? | Deep export, off the barrel, `optional` peer. | — |

An `npm` unmet-peer warning is a report that the host did not provide a singleton. It is not a work order. Satisfying it by adding a library the app never imports publishes an implementation detail and makes that package eligible for the host bundle the moment any module evaluates the barrel.

## What "bloat" means here

Declaring the package does not, by itself, emit bytes. The bytes land when the module graph reaches the import. A package barrel that re-exports every widget reaches it as soon as the host imports the barrel, including from a test. Direct dependencies also sit on the install graph and invite the next import. Both are the leak: encapsulation fails first, the bundle follows.

## Where it is encoded

- Principle: [[eng-foundations]] (naming + abstraction)
- Engineering gate: [[14-engineering-operating-model]] UI surface
- Design-system ban: [[18-design-systems-ai-operating-model]]
- Advisor: [[ds-advisor]] principle 7
- Component packages: [[fe-component-architecture]] package boundary
