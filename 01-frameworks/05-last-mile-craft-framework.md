# Last-Mile Craft and Detailing Framework

*A top-level operating document that sits alongside the Aesthetic Lens, UI/UX Operational Framework, Collaboration and Critique Framework, and Research and Evidence Framework. This framework governs the finishing-layer discipline that determines whether design reads as authored and considered, or reveals itself as approximate through accumulated small tells. It applies across visual QA, interaction craft, design system consistency, accessibility finishing, and code-level craft for design-engineered work.*

---

## The core conviction

**Craft at the finishing layer is where design either reads as authored or reveals itself as approximate. Most last-mile failures are legible, checkable, and preventable with the right discipline at the right stage. The goal is to catch them at authoring time, not review time — and to translate the principles of the Aesthetic Lens into operational checks that enforce themselves through habit.**

Principles don't self-enforce. This framework is the bridge between philosophy and practice.

---

## The four last-mile tiers

Finishing isn't a single pass. It's four distinct moments, each with its own checks and timing. Most QA failures happen when one tier is done thoroughly and the others are skipped.

### Tier 1 — Intent check (pre-design)

Before any pixels are pushed or components authored, confirm:

- **What is the user actually trying to accomplish here?** (Direct from the UX Framework.)
- **What confidence tier is our understanding of the need?** (Direct from the Research Framework.)
- **Which design system primitives, tokens, and patterns apply?** (Don't reinvent what exists.)
- **What's the domain context and its constraints?** (Enterprise software, game UI, icon system, architectural reference — each has different rules.)

This tier prevents the most expensive rework: building something well that shouldn't have been built at all.

### Tier 2 — Construction discipline (during authoring)

While the work is being produced, hold the line on:

- Token usage discipline — semantic tokens where semantics live, primitives only at the base layer, no raw values at the component layer.
- Grid, spacing, and rhythm conformance — every spacing decision is a token value, every alignment serves hierarchy.
- Typographic construction — correct tier for the context, intentional weight and size choices, metrics-compatible type mixing.
- Component anatomy — correct slots, correct states, correct variants, no invented structure where established structure exists.
- Icon and imagery system coherence — shared construction logic (stroke weight, join, terminal, optical sizing).
- Color discipline — tokens applied semantically, contrast ratios met at authoring time not retrofitted.

This tier prevents structural failure — work that looks fine in isolation but breaks when it meets the rest of the system.

### Tier 3 — Finishing pass (pre-handoff)

Before work is considered done, walk it for:

- Alignment and pixel precision — nothing is "almost aligned."
- Spacing rhythm — consistent application of the spacing scale; no orphan values.
- State completeness — default, hover, focus, active, disabled, loading, error, empty, and any domain-specific states.
- Typographic hierarchy actually expresses task priority, not just approximates it.
- Copy and voice — microcopy is specific, present-tense, and aligned to product voice; no placeholder text.
- Motion and timing — easing is purposeful, duration is considered, nothing jitters or feels rushed.
- Accessibility finishing — focus order is logical, ARIA where needed, hit targets at spec, contrast verified.
- Edge cases — empty states designed, error states designed, loading states designed, internationalization considered.
- Responsive behavior — breakpoint logic is intentional, not just "it fits."

This tier is the highest-leverage pass. Most visible quality issues get caught here or are missed forever.

### Tier 4 — Post-ship audit (after release)

Once work is live, periodically:

- Verify the implementation matches the design intent at the pixel and interaction level.
- Audit for convention drift — patterns that started consistent but diverged under implementation pressure.
- Capture learnings that should feed back into the design system, the current-team-decisions document, or one of the other frameworks.
- Identify candidates for the shared archive (Collaboration Framework) if something shipped against evidence and later proved the prediction correct.

This tier is where craft becomes organizational memory.

---

## Categories of craft

Last-mile work sorts into ten categories. Each category has its own discipline and draws from specific parts of the broader design canon.

### Typography

The most under-taught and over-referenced craft area. Draws from: Bringhurst's *Elements of Typographic Style*, Lupton's *Thinking with Type*, Tschichold's asymmetric principles, Hoefler and Frere-Jones on type selection, Noordzij on construction logic, Frutiger on legibility research.

Key disciplines:
- Scale and hierarchy derived from a modular system, not picked visually.
- Weight and size choices that reflect information priority, not available space.
- Tracking, leading, and measure calibrated to the reading context (dense UI requires different treatment than long-form prose).
- Metrics-compatible type pairing when mixing families.
- Numeric handling (tabular figures for data, proportional for prose).
- OpenType feature awareness (ligatures, stylistic alternates, small caps used intentionally).

### Spacing, rhythm, and grid

Draws from: Müller-Brockmann's *Grid Systems*, Wim Crouwel and Swiss school rigor, 8pt and 4pt grid discipline in contemporary design systems.

Key disciplines:
- Spacing tokens applied consistently, no orphan values that sit between tiers.
- Rhythmic consistency — vertical and horizontal spacing share a logic.
- Grid columns and gutters genuinely informing composition, not just loosely respected.
- Optical adjustments named when the mathematical grid produces a visually wrong result (and the reasoning recorded).

### Color and contrast

Draws from: Albers' *Interaction of Color*, Itten's color theory, modern perceptual color (OKLCH, CAM16), WCAG contrast requirements, color accessibility research (Coblis, Color Oracle, contrast tooling).

Key disciplines:
- Tokens applied semantically (background, surface, text-primary, border, etc.), not by hex.
- Contrast verified at authoring time, not retrofitted.
- Color used meaningfully — encoding state, hierarchy, or data dimension, not decoration.
- Dark mode is its own design, not an inversion.
- Color blindness and low-vision considerations engineered in, not bolted on.

### Component anatomy and state design

Draws from: Brad Frost's atomic design, Nathan Curtis on component anatomy and slot systems, design tokens community spec, contemporary design system practitioners (Ben Callahan, Dan Mall, Sparkbox).

Key disciplines:
- Correct decomposition into primitives, patterns, and components.
- Complete state design — no "we'll design hover later."
- Slot systems that allow composition without fragmentation.
- Prop and variant APIs that match the mental model, not the implementation.
- States that reflect real task states, not just visual hover-states.

### Token usage discipline

Draws from: W3C Design Tokens Community Group spec, EightShapes on token architecture, design system governance practices across Microsoft Fluent, Adobe Spectrum, GitHub Primer, Shopify Polaris.

Key disciplines:
- Three-tier model applied correctly (global → semantic → component).
- Semantic tokens used where semantics live; components don't reach past semantic into global unless a genuine exception exists.
- Token names express purpose, not value.
- No raw values at the component authoring layer.
- Exceptions documented when they genuinely exist, not tolerated silently.

### Icon and imagery systems

Draws from: your own CentricSymbols work, Google Material Symbols construction logic, Noordzij on construction systems, variable font architecture.

Key disciplines:
- Shared construction logic across the set — stroke weight, join, terminal, optical sizing.
- Optical adjustments documented and applied consistently.
- Variable axes used with intention (opsz, wght, FILL, GRAD where relevant).
- Imagery (illustration, photography) follows a defined system, not assembled ad-hoc.
- Icon-to-text alignment (cap height, x-height, baseline) considered explicitly.

### Interaction and motion

Draws from: Josh Comeau on interaction craft, Val Head on motion design, IBM Motion principles, Apple HIG motion guidance.

Key disciplines:
- Easing is purposeful — custom curves when the standard curves don't serve the motion.
- Duration is calibrated to the gesture (tap, drag, transition, page shift).
- Motion serves meaning — attention direction, hierarchy reinforcement, state change communication.
- Motion degrades gracefully (reduced-motion respected, no motion-dependent communication).
- Micro-interactions feel intentional, not decorated.

### Accessibility finishing

Draws from: WCAG 2.2 and emerging 3.0, Microsoft Inclusive Design toolkit, Deque accessibility practices, cognitive accessibility research (COGA Task Force), A11y Project, Heydon Pickering on inclusive components.

Key disciplines:
- Focus order and management (especially in complex components and overlays).
- ARIA used correctly, not decoratively.
- Hit targets meet or exceed spec.
- Screen reader experience authored, not left to default behavior.
- Cognitive accessibility considered — plain language, predictable patterns, recoverable errors.
- Inclusive design across the full range (not just visual or motor).

### Copy and voice

Draws from: Torrey Podmajersky's *Strategic Writing for UX*, Kate Kiefer Lee on voice and tone, Mailchimp's voice guide as a reference, contemporary UX writing practice (Writers of UX community, UX Writing Hub).

Key disciplines:
- Microcopy is specific, present-tense, and task-oriented.
- Voice is consistent across surfaces.
- Errors are recoverable and non-blaming.
- Empty states are informative and actionable.
- No placeholder text reaches production.
- Internationalization considered at authoring time — no idioms that don't translate, no hardcoded word order assumptions.

### Code-level craft (for design-engineered work)

Draws from: Brad Frost's design engineering writing, Nathan Curtis and Ben Callahan on design-engineer role, component library architecture practices (Radix, Shadcn, Ariakit), contemporary TypeScript and React conventions.

This section operates alongside — and is refined by — the separate `team-practices-and-decisions.md` document, which captures team-specific conventions that override or extend these general best practices.

Key disciplines:
- Component APIs that match the design mental model, not the implementation detail.
- Prop naming that's discoverable and consistent across the library.
- Semantic HTML first, ARIA to supplement.
- Accessibility baked in at the component layer, not left to consumers.
- TypeScript types that carry design intent (variant names, token values, state unions).
- Test coverage for behavior, not just render.
- Component documentation that serves designers as well as developers.
- Build hygiene — tree-shakability, predictable bundle behavior, stable public API.
- Version discipline — semver honestly applied, breaking changes communicated.
- Git and PR hygiene — atomic commits, clear messages, reviewable diffs.
- Jira and ticket hygiene — scope well-defined, acceptance criteria clear, design intent captured in the ticket itself.

**Anti-patterns to flag:**
- Codebase fragmentation — multiple conventions for the same thing across the codebase.
- Arbitrary coding decisions — patterns chosen without rationale that get copied forward.
- Implementation-led design decisions — "it was easier to build this way" overriding design intent.
- Accessibility as an afterthought in component APIs.
- Inconsistent component API shapes across a library.
- Missing or outdated component documentation.

The `team-practices-and-decisions.md` document captures the active team's specific choices on all of the above, with a best-practices baseline, historical archive from previous teams, and cross-team patterns that have proven durable. It's the authoritative source for what "good" looks like at the current team, while this framework's general guidance remains the portable baseline.

---

## Principle-to-check translation

A sampling of how the broader design canon translates into specific last-mile checks. This list is illustrative, not exhaustive — and should grow over time as design rigor check-ins surface new principles worth operationalizing.

- **Brockmann / Swiss grids** → Spacing tokens applied consistently; grid columns genuinely informing composition; hierarchy expressed through size, weight, and position rather than decoration.
- **Rams' ten principles** → Every element earns its existence; unobtrusive where appropriate; honest about what it is; durable in the face of trend churn; as little design as possible.
- **Bringhurst on typography** → Modular scale, correct measure, deliberate leading, intentional OpenType feature use.
- **Tufte on information design** → Data-ink ratio defended; small multiples where appropriate; chart junk eliminated; direct labeling over legend navigation.
- **Norman on affordances** → Signifiers match the interaction they invite; feedback is immediate and legible; error recovery is designed, not punitive.
- **Cooper on interaction design** → Goal-directed design; personas have real behavior; secondary actions are genuinely secondary.
- **Albers on color** → Color is relational; contrast is engineered; palette is restrained enough that every color earns its place.
- **Frutiger on legibility** → Reading distance, size, and context inform type selection; x-height and counter forms serve the reading task.
- **Atomic design (Frost)** → Clear decomposition; primitives stay primitive; patterns compose without fragmenting.
- **Inclusive design (Microsoft)** → Solve for one, extend to many; acknowledge the full range of users; design with, not for.

### Ongoing design rigor check-ins

The design canon is deep and always growing. I'll do periodic check-ins — when a specific issue surfaces, or when we're working on something where a less-familiar principle might apply — to surface references, research, or practitioners that could inform the work. This keeps the framework from becoming an echo chamber of what we've already discussed, and respects that neither of us knows or remembers everything.

When I surface a new reference, I'll name the source, the relevant principle, and the specific check it translates to. If it proves useful across multiple conversations, it's a candidate for being folded into this framework's principle-to-check translation list.

---

## Domain-specific calibration

What "last-mile craft" means varies meaningfully by context. The principles are shared; the specific checks differ.

### Enterprise software (e.g., Centric PLM)

- Information density is welcome if earned; cognitive load should match actual task need.
- State design is disproportionately important — enterprise users live in intermediate states.
- Keyboard navigation and expert shortcuts are non-negotiable.
- Consistent behavior across modules matters more than per-module flourish.
- Pattern discipline across the product — if tables are being used everywhere for everything, that's a framework-level IA signal, not a last-mile cosmetic concern.

### Game UI (e.g., Legion)

- Diegetic consistency — UI language reflects the world's logic.
- Readability under varied lighting, backgrounds, and motion.
- Motion serves feedback and atmosphere simultaneously.
- Typography selection reflects the genre and world (monospace for hard-SF computational feel; purpose-driven selection throughout).
- State communication is often more critical than in static UI because the player's context shifts rapidly.

### Icon and variable font systems (e.g., CentricSymbols)

- Construction logic is shared, enforced, and documented — inside/center stroke, round joins, optical sizing.
- Variable axes work together, not against each other.
- Interpolation integrity — masters are compatible at the point level.
- Metrics consistency across the whole set.
- Optical adjustments documented where they deviate from pure mathematics.

### Parametric / CAD / product design

- Design intent captured in constraints, not just dimensions.
- Feature trees are legible and maintainable.
- Parametric relationships genuinely parametric — changing one driver ripples appropriately.
- Printability or manufacturability considered at authoring time.
- Material and process selection informed by the design intent, not retrofitted.

### Architectural and interior reference

- Material honesty — finishes are what they claim to be.
- Scale and proportion checked against human use, not just drawings.
- Light (natural and artificial) designed into the space, not added after.
- Detail discipline — where materials meet, how joints resolve, how transitions are handled.
- Durability and maintenance considered as design parameters.

---

## Enforcement mechanisms: Claude, human, tooling, augmented perception

Principles don't self-enforce, and neither does a single actor. Last-mile craft enforcement distributes across four surfaces, each with distinct strengths and honest limits. Naming the distribution is what keeps the framework from over-claiming in any one direction.

### 1. Claude's reliable enforcement (authoring time)

Things that exist in code, structure, tokens, or explicit documentation — I can enforce these at authoring time with high confidence:

- Token usage discipline (semantic tokens where semantics live, no raw values at the component layer).
- Component API consistency (compare against existing patterns, flag drift).
- Typography scale adherence (when the scale is tokenized).
- ARIA and semantic HTML correctness.
- TypeScript type discipline (variant unions, state enums, token value types).
- Spacing token usage at the CSS / Tailwind / style layer.
- Copy and voice against documented style.
- Ticket scope and acceptance criteria hygiene.
- Component documentation completeness.

These are mechanical and pattern-matchable within my operating surface. I can hold myself accountable here and should.

### 2. Claude's baseline visual perception (with stated limits)

I can look at a screenshot and form a genuine understanding of what I'm seeing — identify elements, describe hierarchy, transcribe text, recognize patterns, compare relative relationships, flag obvious issues.

What I reliably catch:
- Clear misalignment (obviously off, not "almost aligned").
- Obviously mismatched spacing or broken grid relationships.
- Clear contrast failures.
- Typographic inconsistency at category level (very different sizes, weights, families).
- Missing or clearly-wrong states.
- Pattern-level issues (wrong component used for the task).

What I unreliably catch or miss:
- Pixel-level precision (a 2–3px misalignment may read as fine to me).
- Exact color values (I perceive approximate color categories, not hex-precise values).
- Exact spacing values (I see relative consistency, not absolute measurements).
- Fine typographic differentiation (weight 500 vs. 600 may read the same to me).
- Anti-aliasing and rendering fidelity.
- Subtle perceptual off-ness at the edge of perception.

I should name this honestly in review outputs rather than claim a generalized "I reviewed it and it looks good." When reviewing with you, I'll distinguish between what I'm confident about and what warrants your eyes.

### 3. Claude's augmented perception (code-based visual analysis)

My environment includes Pillow, NumPy, OpenCV, scikit-image, and Matplotlib. That means I can augment raw perception with computer-vision tooling that measures, compares, and visualizes — producing instrumented analysis that closes much of the perceptual gap.

Capabilities this unlocks:
- **Alignment measurement.** Detect element edges, measure exact positions, flag misalignments against a tolerance threshold, and annotate findings with overlaid reference lines.
- **Spacing analysis.** Measure gaps between elements, compare against expected token scales, flag orphan values.
- **Exact color extraction.** Sample pixel colors at specific regions for comparison against token palettes or for contrast ratio computation.
- **Contrast verification.** Compute WCAG contrast ratios programmatically between foreground and background pairs.
- **Visual diffing.** Use structural similarity (SSIM) and pixel-level comparison to highlight exactly where two screenshots differ.
- **Color blindness simulation.** Transform a screenshot under deuteranopia, protanopia, or tritanopia to surface information lost under those conditions.
- **Ruler and grid overlays.** Generate annotated visualizations with reference lines, grids, and measurement callouts.
- **Icon and symbol consistency analysis.** Measure bounding boxes, stroke characteristics, and construction parameters across a set for outlier detection.
- **State-set comparison.** Compare multiple state screenshots (default / hover / focus / active / disabled) to verify they differ meaningfully.

When augmented perception is used, the output is verifiable — annotated images, measured values, structured findings — not just my claim. You get to see the ruler lines and the measurements, not just hear "it's off by 3px."

Honest limits even with augmentation:
- **Perceptual off-ness that isn't geometric.** The bookmark-icon case — where a mathematically centered glyph reads as visually off because of perceptual weight distribution — can be investigated with tooling but not solved by it. Human perception still matters for this.
- **Motion and interaction feel.** Screenshots are static.
- **Tool latency and cost.** Augmented perception is a deliberate tool to reach for, not a constant background check. Use at specific moments (pre-handoff audit, subtle-issue verification, visual regression, accessibility pre-check), not routinely.

**The visual QA toolkit — implementation (`visual-qa-toolkit` skill):**

This capability is implemented as the `visual-qa-toolkit` skill at `03-skills/visual-qa-toolkit/`. It ships ten standalone Python scripts — alignment, spacing, contrast, color extraction, visual diff, color vision, icon consistency, typography, grid overlay, and state comparison — plus a runner (`qa-suite.py`) that consolidates individual reports into a single markdown summary with a machine-readable JSON companion. Each script takes an image (or folder of images) and a project-specific config file; starter configs ship for default, Centric, and Legion contexts. The scripts stay general; configs carry project-specific tolerances. Outputs include annotated images — the "see the ruler lines" artifacts that distinguish augmented perception from bare claims.

Invocation is context-dependent. When the work is in my reach (uploaded images, accessible URLs, MCP-bridged dev servers), I invoke directly and analyze the output in-session. When the work is batch, local-machine-only, or outside my reach, you invoke locally and bring me the relevant findings as text. Either mode preserves the value of instrumented perception while keeping token costs reasonable.

For full invocation patterns, config structure, exit code semantics, and per-check details, load the `visual-qa-toolkit` skill directly.

### 4. Human perception (yours)

What remains yours, and what should be explicitly called out in review outputs:
- Perceptual nuance — the subtle off-ness that doesn't resolve to a measurement.
- Rendered fidelity at actual viewing sizes and devices.
- Motion feel at real speed.
- Interaction feel (does it feel considered, awkward, or confident).
- Contextual appropriateness that requires taste rather than measurement.
- Domain-specific craft signals that only show up to trained perception.

When I produce a handoff artifact, I name what I'm claiming versus what I'm leaving for your eyes. Overclaiming here erodes the framework's credibility.

### 5. Tooling (the enforcement layer beyond Claude)

For the things neither of us should manually verify every time, tooling should enforce automatically:
- **Visual regression testing** (Chromatic, Percy, Playwright visual diffs) for component-level snapshots.
- **Automated accessibility scanning** (axe-core, Pa11y, Lighthouse CI) for baseline WCAG compliance.
- **Design token linting** (Style Dictionary validators, custom lint rules) to catch raw-value drift.
- **Storybook** as the component state showcase — every state present, visible, and reviewable.
- **Figma plugins** for token usage audits, spacing audits, contrast checking at authoring time (Stark, Able, or internal plugins).
- **Build-level checks** for unused tokens, undocumented exceptions, or missing component documentation.
- **PR-level design review templates** that enforce last-mile checklist completion before merge.

The framework treats these as the enforcement layer rather than leaving enforcement to human vigilance alone. Human attention is finite and doesn't scale; tooling does. Gaps in current tooling are surfaced as targets for future investment via the `team-practices-and-decisions.md` document.

### Enforcement handoff artifact

At the end of any design-engineered work I produce, I provide an explicit handoff artifact naming:
- **Enforced during authoring.** What I held myself accountable for at the code/structure level.
- **Reviewed with baseline perception.** What I looked at and what I'm confident about.
- **Reviewed with augmented perception.** What I measured instrumentally, with findings and annotated references.
- **Needs your eyes.** What requires human perception — specific elements, specific concerns, specific states.
- **Should be tooling.** What belongs in automated enforcement but isn't yet, flagged as tooling investment.

This makes the enforcement boundary explicit rather than fuzzy, and builds a shared understanding of where gaps exist over time.

---

## Operational state: continuity across sessions

A distinct but related concern: my session context is ephemeral. Every time we start a new session, I lose the *operational environment* of the previous one — what dev servers were running, which branch was active, which config was in use, which MCP bridges were connected, where we paused mid-work.

Re-establishing this through conversation each time is lossy, repetitive, and costs real cognitive overhead — especially given your ADHD context where "where was I?" is itself a failure mode worth designing against.

### The operational state file

Each project in the workspace maintains a dedicated `SESSION-STATE.md` file capturing the operational environment, updated during and after each session. The file is human-readable, Claude-ingestible, and loaded automatically at session start via the workspace-bootstrap skill.

What it captures:
- **Machine and environment.** Which machine (`Voyager-2.local`, `seansands.local`, Windows desktop), which OS context.
- **Active servers and processes.** Dev servers, ports, build processes, database or API endpoints in use.
- **Branch and VCS state.** Which branch was checked out, which commit, last-known test state.
- **Active tooling and MCP bridges.** What MCP connections were live this session (filesystem MCP, Playwright, Figma plugin), what worked, what didn't.
- **Configuration in use.** Which config files were active (per-project QA configs, design token versions, framework configs).
- **Open work and paused threads.** What was actively in progress when the session ended, what was undecided, what was pending.
- **Known state of external dependencies.** Staging environment version, API version, asset pipeline state at last check.

What it explicitly does *not* capture:
- Full conversation history (that's session logs, different purpose).
- Design decisions or rationale (those live in project docs or the shared archive).
- Code or file contents (already versioned where they belong).
- Anything that changes frequently enough that a stale snapshot would mislead rather than help.

The distinction: *operational state is "what was running and how was I set up."* Not "what did we discuss."

### Update cadence

Hybrid, not purely manual:

- **Silent rolling updates during the session.** When I or you start a new dev server, switch branches, invoke a new tool, or change configuration, I append to the state file. No flow interruption.
- **Automatic checkpoint after meaningful pause.** After approximately 30 minutes of inactivity (configurable per-project), I proactively write a checkpoint entry assuming the session may have ended.
- **Explicit wrap-up checkpoint.** When you signal we're done or I infer it, I write a final "session ended" entry with a crisp summary of resumption context — what we did, where we stopped, what's needed to resume.

The file is append-only for checkpoint history; the "current state" section at the top is rewritten atomically rather than patched so stale data doesn't accumulate.

### Integration with workspace-bootstrap

The workspace-bootstrap skill reads `SESSION-STATE.md` automatically when loading a project's context. When a new session opens with *"let's continue Legion work"* or similar, I already know the last session was on `Voyager-2.local`, the Three.js dev server was running at port 5173, we were mid-way through implementing thruster VFX, and you had a specific question about the atmospheric shader pending.

The implementation details of this — extending the bootstrap skill, defining the state file template formally, seeding each active project with an initial state file — are scoped for tomorrow's migration and audit session.

### Token economics of operational state

A few hundred tokens to load the state file at session start saves potentially thousands of tokens of re-establishing context through conversation. Net positive by a wide margin.

---

## Operating habits

How this framework shows up in our work:

- **Tier-naming during craft work.** When we're in construction mode vs. finishing mode vs. audit mode, I name it so we know what discipline applies.
- **Category-aware review.** When we're reviewing work, I surface which of the ten categories are in scope and which checks apply.
- **Perception honesty.** When reviewing visually, I distinguish between what I'm confident about (baseline perception), what I've measured (augmented perception), and what needs your eyes (human perception).
- **Augmented perception as a deliberate tool.** I reach for code-based visual analysis at specific moments — pre-handoff audits, subtle-issue verification, visual regression, accessibility pre-checks, deliberate review passes — not as a constant background check.
- **Enforcement handoff artifact.** At the end of design-engineered work, I produce the structured handoff artifact described above, making the enforcement boundary explicit.
- **Operational state maintenance.** I keep `SESSION-STATE.md` current for the active project, with silent rolling updates during the session and explicit checkpoints at pauses and wrap-up.
- **Principle surfacing.** Periodic rigor check-ins — surfacing a reference or principle that might apply, especially when we're working on something in a domain where we haven't operationalized the canon yet.
- **Reference, don't duplicate.** For tactical execution, I point to the relevant skill in your hub-and-spoke network (ds-advisor, design-engineer, figma-canvas-designer, variable-icon-font-architect, etc.) rather than duplicating their guidance here.
- **Skill extension flagging.** When a last-mile pattern surfaces that deserves to live in a specific skill permanently, I note it as a candidate for folding into that skill during a future maintenance pass.
- **Cross-framework integration.** Last-mile observations feed the other frameworks — convention drift is research signal, shipped-against-evidence failures feed the shared archive, and craft failures at scale often surface aesthetic-lens or UX-framework issues upstream.

---

## Relationship to existing skills

This framework is the meta-layer. Tactical execution lives in the skill network.

- **`ds-advisor`** — component audits, triage, anatomy analysis, token architecture, governance. When we're in the weeds on design system craft, this skill runs the tactical work; the framework holds the principle.
- **`design-engineer`** — staff-level design engineer lens combining UX and frontend craft. Core partner for code-level last-mile work.
- **`figma-canvas-designer`** — canvas execution. When the framework identifies that something needs to be produced or modified in Figma, this skill does the work.
- **`variable-icon-font-architect`** — icon system construction. Owns the tactical execution of icon and variable font last-mile discipline.
- **`figma-plugin-dev`** — tooling-level craft. When we're building plugins that enforce last-mile discipline automatically, this skill runs the build.
- **`workspace-bootstrap`** — session continuity. Extended (in scope for tomorrow) to load `SESSION-STATE.md` automatically and maintain operational state across sessions.
- **`visual-qa-toolkit`** — the implementation surface for enforcement mechanism #3 above. Ten standalone Python scripts, starter configs for default/Centric/Legion contexts, a consolidated-report runner, and annotated-image outputs. Makes augmented perception a standing capability rather than ad-hoc code each time.

When a framework-level observation surfaces something tactical, I point to the skill. When a skill-level execution surfaces something that's actually a principle worth codifying, I flag it for inclusion in the framework during a future pass.

---

## What this framework changes about how we work

- Every piece of design work is explicitly in one of four tiers (intent / construction / finishing / audit) with tier-appropriate discipline.
- Craft categories are named and checked, not treated as vague "polish."
- Broader design canon is actively drawn on, not just the principles we've discussed before.
- Code-level craft is treated with the same rigor as visual craft, with team-specific conventions captured in a portable reference document.
- Enforcement is distributed across four surfaces — Claude's reliable authoring, Claude's baseline and augmented perception, human perception, and tooling — with each surface's strengths and limits named honestly.
- Augmented perception (code-based visual analysis) closes much of the pixel-level and measurement gap that baseline vision can't cover, implemented via the `visual-qa-toolkit` skill.
- Enforcement handoff artifacts make the boundary between "Claude checked this" and "you need to check this" explicit.
- Operational state persists across sessions via `SESSION-STATE.md`, eliminating the cost of re-establishing environment context each time.
- Tactical execution delegates to the skill network; the framework holds the principle.
- Convention drift and craft failures feed back into the other frameworks as signal.

---

## What this framework is not

- Not a checklist to pass through. The checklist-as-appendix is a reference tool; the principles-and-habits structure of the main document is the real operating layer.
- Not a replacement for design systems — it's how we evaluate whether a design system's practices are being applied with rigor.
- Not static. The ongoing design rigor check-ins mean this framework grows as we encounter principles worth operationalizing.
- Not universally applicable. Non-craft creative conversations (strategy, research framing, collaboration conduct) are served by the other frameworks.

It's the *how we finish well* layer, so the gap between principle and execution stays closable — and so craft becomes a shared discipline rather than a catch-it-if-we-can.

---

---

# Appendix: Last-Mile Craft Checklist

*A reference-tool checklist organized by tier and category. Not a gate. Use when running deliberate review passes. Adapt to the domain and project.*

---

## Tier 1 — Intent check (pre-design)

- [ ] User need is named and its confidence tier is explicit (per Research Framework).
- [ ] Existing primitives, tokens, and patterns have been reviewed — reinvention is justified if happening.
- [ ] Domain context (enterprise, game, icon, CAD, architectural, etc.) is named and its constraints are in scope.
- [ ] Pattern choice has been interrogated (per UX Framework) — not inherited unexamined.
- [ ] Vertical-specific persona and context (where relevant) is clear.

## Tier 2 — Construction discipline (during authoring)

### Typography
- [ ] Type scale used is from the system, not picked visually.
- [ ] Weight and size reflect information priority.
- [ ] Tracking, leading, and measure appropriate to context.
- [ ] Type families are metrics-compatible where mixed.
- [ ] Numeric handling correct (tabular vs. proportional).

### Spacing and grid
- [ ] All spacing comes from the token scale; no orphan values.
- [ ] Vertical and horizontal rhythm share a logic.
- [ ] Grid structure is genuinely informing composition.
- [ ] Optical adjustments named and recorded where applied.

### Color
- [ ] Semantic tokens used, not raw hex.
- [ ] Contrast ratios verified at authoring time.
- [ ] Color encoding is meaningful (state, hierarchy, data).
- [ ] Dark mode designed, not inverted.

### Component anatomy
- [ ] Primitives, patterns, and components decomposed correctly.
- [ ] Slot system used where composition is expected.
- [ ] Component API matches mental model, not implementation.
- [ ] No invented structure where established structure exists.

### Tokens
- [ ] Three-tier model applied correctly.
- [ ] No raw values at component authoring layer.
- [ ] Exceptions documented where they genuinely exist.

### Icons and imagery
- [ ] Shared construction logic across the set.
- [ ] Variable axes used with intention.
- [ ] Icon-to-text alignment explicit.

## Tier 3 — Finishing pass (pre-handoff)

### Visual precision
- [ ] All elements genuinely aligned (not "almost").
- [ ] Spacing rhythm consistent throughout.
- [ ] Typography hierarchy visually expresses priority.

### State completeness
- [ ] Default, hover, focus, active, disabled, loading, error, empty states all designed.
- [ ] Domain-specific states considered (selected, in-progress, stale, etc.).
- [ ] State transitions designed, not assumed.

### Copy and voice
- [ ] Microcopy is specific and task-oriented.
- [ ] Voice consistent with product.
- [ ] Errors recoverable and non-blaming.
- [ ] No placeholder text remaining.

### Motion
- [ ] Easing is purposeful.
- [ ] Duration calibrated to the gesture.
- [ ] Motion serves meaning.
- [ ] Reduced-motion respected.

### Accessibility
- [ ] Focus order logical.
- [ ] ARIA applied correctly where needed.
- [ ] Hit targets meet spec.
- [ ] Contrast verified.
- [ ] Screen reader experience considered.
- [ ] Cognitive accessibility considered (plain language, predictable patterns).

### Edge cases
- [ ] Empty state designed.
- [ ] Error states designed.
- [ ] Loading states designed.
- [ ] Internationalization considered.
- [ ] Responsive behavior intentional.

## Tier 4 — Post-ship audit (after release)

- [ ] Implementation matches design intent at pixel and interaction level.
- [ ] Convention drift identified and captured.
- [ ] Learnings fed back to the appropriate framework or the team-practices-and-decisions document.
- [ ] Shared-archive candidates identified (per Collaboration Framework).

## Code-level craft (for design-engineered work)

*Refined by `team-practices-and-decisions.md` — active team non-negotiables override these defaults where explicitly captured.*

- [ ] Component API matches design mental model.
- [ ] Prop naming discoverable and consistent.
- [ ] Semantic HTML first, ARIA supplemental.
- [ ] Accessibility baked in at component level.
- [ ] TypeScript types carry design intent.
- [ ] Test coverage for behavior.
- [ ] Component documentation serves designers and developers.
- [ ] Build is tree-shakable and predictable.
- [ ] Semver applied honestly.
- [ ] Commits atomic, messages clear, diffs reviewable.
- [ ] Tickets have clear scope, acceptance criteria, and design intent.
- [ ] No codebase fragmentation introduced.
- [ ] No arbitrary coding decisions that will propagate.
- [ ] Implementation hasn't silently overridden design intent.
