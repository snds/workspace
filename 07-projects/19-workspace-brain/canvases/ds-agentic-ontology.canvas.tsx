import {
  Callout,
  Card,
  CardBody,
  CardHeader,
  Divider,
  Grid,
  H1,
  H2,
  H3,
  Pill,
  Row,
  Spacer,
  Stack,
  Stat,
  Table,
  Text,
  BarChart,
  computeDAGLayout,
  useCanvasState,
  useHostTheme,
} from "cursor/canvas";
import type { CSSProperties } from "react";
import { useMemo } from "react";

type View =
  | "overview"
  | "ontology"
  | "graph"
  | "context"
  | "compare"
  | "remap"
  | "moves";

const VIEWS: { id: View; label: string }[] = [
  { id: "overview", label: "Overview" },
  { id: "ontology", label: "Ontology" },
  { id: "graph", label: "Knowledge graph" },
  { id: "context", label: "Context model" },
  { id: "compare", label: "Spec compare" },
  { id: "remap", label: "Remap" },
  { id: "moves", label: "Next moves" },
];

const COVERAGE = {
  categories: [
    "Intent layers",
    "DS-as-data",
    "Context eng.",
    "Harness loop",
    "Token/theme",
    "Product UX",
    "A2A / MCP",
    "Eval / prove",
    "Memory",
    "Human/agent split",
  ],
  series: [
    {
      name: "This workspace",
      data: [95, 45, 78, 72, 82, 68, 55, 88, 84, 58],
    },
    {
      name: "DSDS 0.20",
      data: [55, 96, 22, 8, 88, 42, 10, 28, 12, 94],
    },
    {
      name: "2026 agentic harness",
      data: [48, 12, 96, 96, 6, 8, 92, 90, 86, 40],
    },
    {
      name: "@ai-created/ui",
      data: [70, 52, 38, 28, 94, 96, 18, 48, 20, 72],
    },
  ],
};

function Graph({
  nodes,
  edges,
  labels,
  direction = "vertical",
  nodeWidth = 150,
}: {
  nodes: { id: string }[];
  edges: { from: string; to: string }[];
  labels: Record<string, string>;
  direction?: "vertical" | "horizontal";
  nodeWidth?: number;
}) {
  const theme = useHostTheme();
  const layout = useMemo(
    () =>
      computeDAGLayout({
        nodes,
        edges,
        direction,
        nodeWidth,
        nodeHeight: 42,
        rankGap: 52,
        nodeGap: 16,
        padding: 12,
      }),
    [nodes, edges, direction, nodeWidth],
  );

  return (
    <div style={{ overflowX: "auto" }}>
      <svg
        width={layout.width}
        height={layout.height}
        viewBox={`0 0 ${layout.width} ${layout.height}`}
        role="img"
        aria-label="Directed graph"
      >
        {layout.ranks.map((rank) => (
          <rect
            key={rank.rank}
            x={rank.x}
            y={rank.y}
            width={rank.width}
            height={rank.height}
            fill={theme.fill.tertiary}
            rx={4}
          />
        ))}
        {layout.edges.map((edge, i) => (
          <line
            key={`${edge.from}-${edge.to}-${i}`}
            x1={edge.sourceX}
            y1={edge.sourceY}
            x2={edge.targetX}
            y2={edge.targetY}
            stroke={edge.isBackEdge ? theme.stroke.tertiary : theme.stroke.secondary}
            strokeWidth={1.25}
            strokeDasharray={edge.isBackEdge ? "4 3" : undefined}
          />
        ))}
        {layout.nodes.map((node) => (
          <g key={node.id}>
            <rect
              x={node.x}
              y={node.y}
              width={nodeWidth}
              height={42}
              fill={theme.bg.elevated}
              stroke={theme.stroke.primary}
              rx={4}
            />
            <text
              x={node.x + nodeWidth / 2}
              y={node.y + 26}
              textAnchor="middle"
              fill={theme.text.primary}
              fontSize={11}
            >
              {labels[node.id] ?? node.id}
            </text>
          </g>
        ))}
      </svg>
    </div>
  );
}

function Caption({ children }: { children: string }) {
  return (
    <Text size="small" tone="tertiary">
      {children}
    </Text>
  );
}

function Band({
  title,
  body,
  style,
}: {
  title: string;
  body: string;
  style?: CSSProperties;
}) {
  const theme = useHostTheme();
  return (
    <div
      style={{
        border: `1px solid ${theme.stroke.secondary}`,
        background: theme.bg.elevated,
        padding: 12,
        ...style,
      }}
    >
      <Text weight="semibold" size="small">
        {title}
      </Text>
      <Text size="small" tone="secondary">
        {body}
      </Text>
    </div>
  );
}

function Overview() {
  return (
    <Stack gap={20}>
      <Grid columns={4} gap={12}>
        <Stat value="3" label="Graphs that must not mix" />
        <Stat value="5" label="DS delivery layers" />
        <Stat value="7" label="Remapped stack layers" />
        <Stat value="0.20.0" label="DSDS to project onto" />
      </Grid>

      <Callout tone="info" title="What this canvas is for">
        Visualize the workspace ontology, the two existing graphs plus a missing
        design-system artifact graph, and the Wolosin context model. Then hold
        those against DSDS, grokking agentic design, the 2026 harness update,
        and @ai-created/ui. Coverage bars are a 2026-09-01 judgment, not a
        measured benchmark.
      </Callout>

      <Grid columns="1.4fr 1fr" gap={16}>
        <Stack gap={10}>
          <H2>The claim</H2>
          <Text>
            This workspace already has a stronger intent model than any of the
            five sources. What it lacks is a single machine-readable design-system
            document, an explicit context-builder subsystem, and a named harness
            loop. Do not invent a sixth schema. Project the existing stack onto
            DSDS 0.20 for documentation-as-data, keep the contract schema for
            arbitration, and borrow 2026 harness vocabulary for control flow.
          </Text>
          <Text>
            Complements, not competitors: DTCG owns token values, DSDS owns
            meaning and usage, the Curtis contract owns what implementations
            must settle without a meeting, DESIGN.md owns portable look,
            A2UI owns the agent-to-UI wire format.
          </Text>
        </Stack>
        <Card>
          <CardHeader>Sources read 2026-09-01</CardHeader>
          <CardBody>
            <Stack gap={8}>
              <Text size="small">
                Grokking the System Design — Agentic System Design guide
              </Text>
              <Text size="small">
                gtzheng/Awesome-Agentic-System-Design
              </Text>
              <Text size="small">DSDS 0.20.0 — designsystemdocspec.org</Text>
              <Text size="small">@ai-created/ui — ui.ai-created.com</Text>
              <Text size="small">
                alirezadir/Agentic-AI-Systems — 2026 harness update
              </Text>
            </Stack>
          </CardBody>
        </Card>
      </Grid>

      <Stack gap={8}>
        <H2>Coverage by concern</H2>
        <Caption>
          Source: synthesis of vault model vs the five specs · 2026-09-01 ·
          scores 0–100 are judgment, not measurement
        </Caption>
        <BarChart
          height={280}
          categories={COVERAGE.categories}
          series={COVERAGE.series}
          yMax={100}
          valueSuffix=""
        />
      </Stack>
    </Stack>
  );
}

function Ontology() {
  return (
    <Stack gap={20}>
      <Text>
        The routing map answers one question before any write: where does this
        belong? Skill layers are a load-order model. Content layers are an
        ownership model. Mixing them is how agents dump domain insight into
        session logs or treat DESIGN.md as the whole system.
      </Text>

      <H2>Skill load order</H2>
      <Caption>
        Only foundation to hub to spoke is a hard load edge. Cross-cutting
        lenses attach sideways.
      </Caption>
      <Graph
        nodes={[
          { id: "found" },
          { id: "hub" },
          { id: "spoke" },
          { id: "lens" },
        ]}
        edges={[
          { from: "found", to: "hub" },
          { from: "hub", to: "spoke" },
          { from: "lens", to: "spoke" },
        ]}
        labels={{
          found: "Foundation",
          hub: "Hub",
          spoke: "Spoke",
          lens: "Cross-cutting",
        }}
        direction="horizontal"
        nodeWidth={130}
      />

      <H2>Where a fact lives</H2>
      <Table
        headers={["If it is", "It goes to", "Not"]}
        rows={[
          [
            "How to do X when Y",
            "03-skills / SKILL.md",
            "A knowledge essay or chat memory",
          ],
          [
            "What we learned about X",
            "08-knowledge / domain",
            "SESSION-STATE or a skill body",
          ],
          [
            "Sean / env / decision-why",
            "06-context/memory",
            "A design-system facet",
          ],
          [
            "Who owns / what is in flight",
            "project-context + Live handoff",
            "A durable knowledge claim",
          ],
          [
            "Deliberate tone / format",
            "04-preferences",
            "An agent profile or local memory",
          ],
          [
            "Cross-cutting method",
            "01-frameworks (3+ consumers)",
            "A one-off project note",
          ],
          [
            "Vocabulary / spec",
            "02-shared-references",
            "A skill that restates the spec",
          ],
          [
            "Generated deliverable",
            "05-artifacts, versioned",
            "Overwrite in place",
          ],
        ]}
        striped
      />

      <H2>Design-system stack inside that ontology</H2>
      <Caption>
        Wolosin: context is intent. Each intent type has one delivery form so
        Atlassian-style DESIGN.md collapse cannot happen.
      </Caption>
      <Graph
        nodes={[
          { id: "fw" },
          { id: "skill" },
          { id: "mcp" },
          { id: "designmd" },
          { id: "agents" },
        ]}
        edges={[
          { from: "fw", to: "skill" },
          { from: "fw", to: "mcp" },
          { from: "fw", to: "designmd" },
          { from: "fw", to: "agents" },
        ]}
        labels={{
          fw: "Framework #09",
          skill: "Skill / how",
          mcp: "MCP / facts",
          designmd: "DESIGN.md",
          agents: "AGENTS rules",
        }}
        nodeWidth={128}
      />

      <Grid columns={2} gap={12}>
        <Band
          title="18-facet schema"
          body="Documentation facets 1–17 inform. Facet 18 is the machine-readable intent record. The contract schema is the typed subset that arbitrates."
        />
        <Band
          title="Always-on vs on-demand"
          body="Foundations and AGENTS.md stay loaded. Per-component depth is MCP. DESIGN.md stays lean visual identity. That split is the Atlassian field-test fix."
        />
      </Grid>
    </Stack>
  );
}

function KnowledgeGraph() {
  return (
    <Stack gap={20}>
      <Callout tone="warning" title="Two graphs already. A third is missing.">
        Skills use Related edges (foundation, hub, spoke, governed-by,
        encodes-into). Knowledge and memory use relations (builds-on, relates-to,
        contradicts, refutes, exemplifies). Do not cross those graphs. The
        missing graph is a DSDS-shaped design-system artifact graph.
      </Callout>

      <H2>Skill-dependency graph</H2>
      <Caption>
        Load-order graph. Generated into skills.registry.json. Reciprocal edges
        are CI-enforced.
      </Caption>
      <Graph
        nodes={[
          { id: "df" },
          { id: "fc" },
          { id: "ds" },
          { id: "de" },
          { id: "ux" },
          { id: "a11y" },
        ]}
        edges={[
          { from: "df", to: "fc" },
          { from: "df", to: "ds" },
          { from: "df", to: "de" },
          { from: "ds", to: "ux" },
          { from: "a11y", to: "ds" },
          { from: "a11y", to: "de" },
        ]}
        labels={{
          df: "design-foundations",
          fc: "found-color",
          ds: "ds-advisor",
          de: "design-engineer",
          ux: "ux-component-lib",
          a11y: "a11y-visual",
        }}
        nodeWidth={142}
      />

      <H2>Epistemic graph</H2>
      <Caption>
        What builds on or refutes what. Retrieval preamble is the cheap head.
        Layer-1 vault-retrieve is fallback when triggers miss.
      </Caption>
      <Graph
        nodes={[
          { id: "contracts" },
          { id: "schema" },
          { id: "fw9" },
          { id: "dsds" },
          { id: "this" },
        ]}
        edges={[
          { from: "fw9", to: "contracts" },
          { from: "contracts", to: "schema" },
          { from: "contracts", to: "dsds" },
          { from: "contracts", to: "this" },
          { from: "fw9", to: "this" },
        ]}
        labels={{
          fw9: "Framework #09",
          contracts: "Contracts entry",
          schema: "Contract schema",
          dsds: "DSDS 0.15.2 note",
          this: "This remap",
        }}
        direction="horizontal"
        nodeWidth={132}
      />

      <H2>Proposed DS artifact graph (DSDS 0.20 kinds)</H2>
      <Caption>
        One document. Entries link to everything else. Values stay in DTCG.
        API contracts stay in CEM / Specs. DSDS records meaning, usage, and
        audience.
      </Caption>
      <Graph
        nodes={[
          { id: "system" },
          { id: "theme" },
          { id: "token" },
          { id: "component" },
          { id: "pattern" },
          { id: "shared" },
        ]}
        edges={[
          { from: "system", to: "theme" },
          { from: "system", to: "token" },
          { from: "system", to: "component" },
          { from: "system", to: "pattern" },
          { from: "token", to: "theme" },
          { from: "component", to: "token" },
          { from: "pattern", to: "component" },
          { from: "shared", to: "component" },
          { from: "shared", to: "pattern" },
        ]}
        labels={{
          system: "system",
          theme: "theme",
          token: "token",
          component: "component",
          pattern: "entry / pattern",
          shared: "shared",
        }}
        nodeWidth={128}
      />

      <H3>Folder projection</H3>
      <Table
        headers={["DSDS kind", "Vault home today", "What DSDS must not copy"]}
        rows={[
          [
            "system",
            "DESIGN.md + ds-agents-binding + #09 constitution",
            "Per-component anatomy dumps",
          ],
          [
            "component",
            "ux-components MCP + 18-facet record + contract spec",
            "Token hex values or CEM props",
          ],
          [
            "token",
            "DTCG / Figma variables / DESIGN.md token groups",
            "The value itself; DSDS points at source",
          ],
          [
            "theme",
            "DESIGN.md modes + density / accent axes",
            "A second visual language",
          ],
          [
            "entry",
            "08-knowledge/design patterns, foundations, guides",
            "Session state or Live handoff",
          ],
          [
            "shared",
            "a11y-visual, found-*, APG laws in #09 §8",
            "Component-local exceptions stated twice",
          ],
        ]}
        striped
      />
    </Stack>
  );
}

function ContextModel() {
  return (
    <Stack gap={20}>
      <Text>
        The workspace context model is already a 2026 context-engineering
        system. It just does not use that name. The remap is mostly vocabulary
        and one missing projection, not a rebuild.
      </Text>

      <H2>Wolosin intents to delivery</H2>
      <Table
        headers={["Intent", "Question", "Form", "Artifact"]}
        rows={[
          [
            "Framing",
            "Why does this exist?",
            "Durable prose, loaded on demand",
            "Framework #09",
          ],
          [
            "Workflow",
            "What are the steps now?",
            "Progressive procedure",
            "ux-component-library skill",
          ],
          [
            "Guidelines",
            "What exactly is X?",
            "Typed, on demand",
            "MCP + DSDS sections",
          ],
          [
            "Constraints",
            "What must / must not happen?",
            "Rules + portable tokens",
            "AGENTS.md + DESIGN.md",
          ],
        ]}
        rowTone={["info", "neutral", "success", "warning"]}
      />

      <H2>2026 context-engineering overlay</H2>
      <Caption>
        Alireza 2026: select, rank, compress, isolate, prove. Mapped onto
        mechanisms that already exist.
      </Caption>
      <Grid columns={2} gap={12}>
        <Band
          title="Sources"
          body="Role, Live handoff, project-context, knowledge, memory, DESIGN.md, MCP, tool output, cuespecs."
        />
        <Band
          title="Selection"
          body="Trigger-routes, load_chains, vault-retrieve, context profile, capability preflight."
        />
        <Band
          title="Compression"
          body="Heads not whole logs. For-future-agent preambles. DESIGN.md kept lean. MCP on demand."
        />
        <Band
          title="Provenance + isolation"
          body="Timeless / dated / pointer. Trust: MCP and tokens are deterministic; prose is verify. Employer vs personal walls."
        />
      </Grid>

      <H2>Memory: Grokking 3-tier onto the vault</H2>
      <Graph
        nodes={[
          { id: "short" },
          { id: "long" },
          { id: "shared" },
          { id: "loop" },
        ]}
        edges={[
          { from: "short", to: "loop" },
          { from: "long", to: "loop" },
          { from: "shared", to: "loop" },
        ]}
        labels={{
          short: "Working / session",
          long: "Knowledge + memory",
          shared: "Live handoff",
          loop: "Agent loop",
        }}
        direction="horizontal"
        nodeWidth={140}
      />
      <Table
        headers={["Grokking tier", "Vault equivalent", "Decay rule"]}
        rows={[
          [
            "Short-term",
            "Chat + Live handoff working set + session fragment",
            "Clears at session end; fragment is the residue",
          ],
          [
            "Long-term",
            "08-knowledge, 06-context/memory, 04-preferences",
            "Freshness tags; refutes marks superseded claims",
          ],
          [
            "Shared",
            "SESSION-STATE, project-context, side-chat-inbox",
            "Atomic rewrite of the baton; inbox is consumed",
          ],
        ]}
      />

      <H2>Harness loop (named, not new)</H2>
      <Caption>
        Grokking + 2026 update. This is the doctor, dispatcher, ritual, prove
        engine, and human gates drawn as one control path.
      </Caption>
      <Graph
        nodes={[
          { id: "req" },
          { id: "policy" },
          { id: "ctx" },
          { id: "act" },
          { id: "eval" },
          { id: "human" },
        ]}
        edges={[
          { from: "req", to: "policy" },
          { from: "policy", to: "ctx" },
          { from: "ctx", to: "act" },
          { from: "act", to: "eval" },
          { from: "eval", to: "human" },
          { from: "eval", to: "ctx" },
        ]}
        labels={{
          req: "Request / schedule",
          policy: "Profile + walls",
          ctx: "Context builder",
          act: "Tools / MCP",
          eval: "Prove / validators",
          human: "Human gate",
        }}
        direction="horizontal"
        nodeWidth={128}
      />
    </Stack>
  );
}

function Compare() {
  return (
    <Stack gap={20}>
      <Text>
        Each source owns a different layer. Treating any one as the whole
        model is how you either overconstrain the agent or lose the design
        system.
      </Text>

      <H2>What each source is actually for</H2>
      <Table
        headers={["Source", "Owns", "Does not own", "Fit here"]}
        rows={[
          [
            "This workspace",
            "Intent layers, routing, two graphs, prove culture, token-frugal load",
            "A portable DS document file",
            "Keep as operating system",
          ],
          [
            "DSDS 0.20.0",
            "Documentation as data; entry kinds; for: human|agent|all; refs; combos",
            "Token values, API contracts, runtime UI",
            "Adopt as projection of facets 1–17",
          ],
          [
            "Grokking agentic SD",
            "Roles, goals, tools-as-contracts, 3-tier memory, multi-agent patterns",
            "Design-system schemas or tokens",
            "Vocabulary for harness + memory",
          ],
          [
            "Awesome list",
            "Index of papers, SDKs, MCP/A2A/ANP/ACP",
            "A schema or a context model",
            "Reading list, not a contract",
          ],
          [
            "2026 harness update",
            "Context engineering, AgentOps, evals, MCP vs A2A, cost, security",
            "Component anatomy or visual identity",
            "Name the loop we already run",
          ],
          [
            "@ai-created/ui",
            "Living coded DS + product UX patterns + same-pass doc discipline",
            "A multi-repo ontology or vault graph",
            "Steal change discipline + UX-as-contract",
          ],
        ]}
        striped
      />

      <H2>DSDS 0.15.2 to 0.20.0</H2>
      <Callout tone="warning" title="Stale claim in the vault">
        component-contracts-and-schemas still describes DSDS as 6 entity types
        times 17 typed kind blocks (v0.15.2). 0.20.0 collapsed that: 5
        well-known entry kinds plus custom, and 3 section kinds plus generic
        section and freeform.
      </Callout>
      <Table
        headers={["0.15.2 (our note)", "0.20.0 (current spec)", "Action"]}
        rows={[
          [
            "6 entity types including foundations, patterns, guides",
            "system, component, token, theme, entry + custom kind",
            "Map foundations/patterns/guides onto entry + shared",
          ],
          [
            "17 typed kind blocks (anatomy, api, states…)",
            "guidelines, definitions, steps, section + freeform",
            "Put anatomy/states in component fields (traits, combos), not invented kinds",
          ],
          [
            "One audience",
            "for: human | agent | all",
            "Stamp existing For-future-agent blocks as for: agent",
          ],
          [
            "Docs as data",
            "Docs only; link DTCG, CEM, Storybook, Figma",
            "Matches our complements-not-competitors rule",
          ],
        ]}
      />

      <Grid columns={2} gap={16}>
        <Card>
          <CardHeader>Agree across sources</CardHeader>
          <CardBody>
            <Stack gap={8}>
              <Text size="small">
                Prompts, policies, and memory are first-class architecture.
              </Text>
              <Text size="small">
                Tools are contracts with blast radius, not raw APIs.
              </Text>
              <Text size="small">
                One file cannot hold the whole system. Depth must be on demand.
              </Text>
              <Text size="small">
                Meaning stays separate from values (DTCG) and from runtime API
                (CEM / code).
              </Text>
              <Text size="small">
                Agents need a way to stop, escalate, and leave an audit trail.
              </Text>
            </Stack>
          </CardBody>
        </Card>
        <Card>
          <CardHeader>Where they conflict</CardHeader>
          <CardBody>
            <Stack gap={8}>
              <Text size="small">
                Grokking optimizes autonomy. This workspace optimizes refusal
                and token cost. Keep refusal.
              </Text>
              <Text size="small">
                @ai-created keeps one living DESIGN-SYSTEM.md next to code.
                Atlassian showed a monolithic DESIGN.md fails at production
                component depth. Keep the split.
              </Text>
              <Text size="small">
                DSDS is documentation-only. Our contract schema is arbitration.
                Do not merge them.
              </Text>
              <Text size="small">
                A2A/A2UI are runtime. The vault is author-time context. Project
                a catalog; do not store the wire format as the ontology.
              </Text>
            </Stack>
          </CardBody>
        </Card>
      </Grid>

      <H3>Curtis four words, still the discriminator</H3>
      <Table
        headers={["Word", "Test", "Which spec"]}
        rows={[
          ["Description", "Informs a reader", "DSDS sections, skill prose, DESIGN.md rationale"],
          ["Schema", "What a contract can say", "DSDS shapes + our contract schema"],
          ["Spec", "What this instance says", "A filled DSDS entry or a signed contract"],
          ["Contract", "Arbitrates without a meeting", "component-contract-schema, not DSDS"],
        ]}
      />
    </Stack>
  );
}

function Remap() {
  return (
    <Stack gap={20}>
      <Text>
        Proposed operating name: Agentic Design System Context Model. Seven
        layers. Nothing below replaces a working vault file. Each layer names
        an existing mechanism or a projection we still owe.
      </Text>

      <H2>Seven-layer remap</H2>
      <Graph
        nodes={[
          { id: "l0" },
          { id: "l1" },
          { id: "l2" },
          { id: "l3" },
          { id: "l4" },
          { id: "l5" },
          { id: "l6" },
        ]}
        edges={[
          { from: "l0", to: "l1" },
          { from: "l1", to: "l2" },
          { from: "l2", to: "l3" },
          { from: "l3", to: "l4" },
          { from: "l4", to: "l5" },
          { from: "l5", to: "l6" },
        ]}
        labels={{
          l0: "L0 Harness",
          l1: "L1 Profile + route",
          l2: "L2 Intent delivery",
          l3: "L3 Three graphs",
          l4: "L4 Schema stack",
          l5: "L5 Memory",
          l6: "L6 AgentOps",
        }}
        nodeWidth={150}
      />

      <Table
        headers={["Layer", "Job", "Keep", "Borrow"]}
        rows={[
          [
            "L0 Harness",
            "Control flow around the model",
            "Dispatcher, doctor, ritual, walls",
            "2026 loop names: policy, context builder, budget, rollback",
          ],
          [
            "L1 Profile + route",
            "Who owns it, where it belongs",
            "Context profiles + routing map",
            "Grokking role/goal/stop conditions",
          ],
          [
            "L2 Intent delivery",
            "Right form at the right moment",
            "Wolosin 4 + 5 delivery layers",
            "DSDS for: human|agent|all on sections",
          ],
          [
            "L3 Three graphs",
            "Load, epistemology, DS artifacts",
            "Skill Related + relations:",
            "DSDS entry graph as the third",
          ],
          [
            "L4 Schema stack",
            "What is data vs what is law",
            "18 facets, contract schema, DESIGN.md, A2UI catalog",
            "DSDS 0.20 document as the portable DS file",
          ],
          [
            "L5 Memory",
            "What persists, what decays",
            "Knowledge / memory / handoff",
            "Grokking short / long / shared labels",
          ],
          [
            "L6 AgentOps",
            "Prove, cost, escalate, trace",
            "Validators, vqa, trust levels",
            "Trajectory evals, cost-per-task, approval rate",
          ],
        ]}
        striped
      />

      <H2>Do not collapse</H2>
      <Grid columns={3} gap={12}>
        <Band
          title="DSDS ≠ contract"
          body="DSDS informs and links. The contract still has to refuse an illegal combo without a human."
        />
        <Band
          title="DESIGN.md ≠ system"
          body="Portable look only. Component depth stays on demand. @ai-created's one-file living site is a product DS, not a vault."
        />
        <Band
          title="A2UI ≠ ontology"
          body="A2UI is a trusted catalog plus wire format. The vault authors the catalog. The renderer owns style."
        />
      </Grid>
    </Stack>
  );
}

function Moves() {
  return (
    <Stack gap={20}>
      <H2>Re-org that is worth doing</H2>
      <Table
        headers={["#", "Move", "Why", "Effort"]}
        rows={[
          [
            "1",
            "Project a project-independent DSDS 0.20 constitution; systems extend it",
            "Facets 1–17 become portable without a sixth schema",
            "M",
          ],
          [
            "2",
            "Stamp for: agent / for: all as notes are touched (convention, not a vault rewrite)",
            "DSDS audience split is the missing half of the preamble",
            "S",
          ],
          [
            "3",
            "Name the context builder in AGENTS / Live handoff (sources, selection, budget)",
            "2026 vocabulary without new files",
            "S",
          ],
          [
            "4",
            "Keep composition combos in the DSDS constitution; add pairs when #09 laws move",
            "Pairing rules become machine-checkable",
            "M",
          ],
          [
            "5",
            "Adopt @ai-created same-pass rule for product UX patterns",
            "enterprise-saas patterns stop drifting from the coded system",
            "S",
          ],
          [
            "6",
            "Keep contract schema as facet-18 arbitration; emit DSDS as a view",
            "Description and contract stay separable",
            "M",
          ],
          [
            "7",
            "Treat session-log + prove JSON as AgentOps traces; add cost later",
            "Do not build a new observability stack before the runner exists",
            "L",
          ],
          [
            "8",
            "Run ds-source-watch --check in /optimize; --fetch only when reviewing sources",
            "Onori, Curtis, DSDS, agentic specs stay current without silent ontology edits",
            "S",
          ],
        ]}
        rowTone={[
          "success",
          "success",
          "info",
          "info",
          "info",
          "warning",
          "neutral",
          "success",
        ]}
      />

      <H2>Refuse</H2>
      <Grid columns={2} gap={12}>
        <Band
          title="A general-purpose agent role"
          body="Grokking warns this fails in production. Keep hubs and spokes. Narrow authority."
        />
        <Band
          title="One always-loaded DS dump"
          body="Atlassian already measured this. Token bloat, omitted guidance, re-implementation."
        />
        <Band
          title="Merging the three graphs"
          body="Load edges, epistemic edges, and DS artifact edges answer different questions."
        />
        <Band
          title="DSDS as the contract"
          body="If two implementations disagree, a documentation entry cannot settle it."
        />
      </Grid>

      <Callout tone="neutral" title="Durable write">
        The remapped model and the DSDS 0.20 freshness fix land in the vault
        as 08-knowledge/design/agentic-ds-context-model.md plus a patch on
        component-contracts-and-schemas. This canvas is the working view.
      </Callout>
    </Stack>
  );
}

export default function DsAgenticOntology() {
  const [view, setView] = useCanvasState<View>("view", "overview");

  return (
    <Stack gap={20} style={{ maxWidth: 1080 }}>
      <Stack gap={8}>
        <Row align="center">
          <H1>Design-system ontology, graph, context</H1>
          <Spacer />
          <Pill size="sm" active>
            2026-09-01
          </Pill>
        </Row>
        <Text tone="secondary">
          Workspace model held against DSDS 0.20, grokking agentic system
          design, the 2026 harness update, and @ai-created/ui. Open a view,
          then use the remap.
        </Text>
      </Stack>

      <Row gap={8} wrap>
        {VIEWS.map((item) => (
          <span key={item.id}>
            <Pill active={view === item.id} onClick={() => setView(item.id)}>
              {item.label}
            </Pill>
          </span>
        ))}
      </Row>

      <Divider />

      {view === "overview" ? <Overview /> : null}
      {view === "ontology" ? <Ontology /> : null}
      {view === "graph" ? <KnowledgeGraph /> : null}
      {view === "context" ? <ContextModel /> : null}
      {view === "compare" ? <Compare /> : null}
      {view === "remap" ? <Remap /> : null}
      {view === "moves" ? <Moves /> : null}
    </Stack>
  );
}
