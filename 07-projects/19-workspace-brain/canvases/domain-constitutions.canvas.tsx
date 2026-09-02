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

type View = "map" | "complements" | "graphs" | "gaps";

const VIEWS: { id: View; label: string }[] = [
  { id: "map", label: "Domain map" },
  { id: "complements", label: "Complements" },
  { id: "graphs", label: "Three graphs" },
  { id: "gaps", label: "Gaps" },
];

const AUTHORED = [
  ["design-systems", "Design systems", "DSDS 0.20", "#09", "canonical"],
  ["ux-ui", "UX / UI / interaction", "dc-ux-ui", "#02 + #01", "authored"],
  ["motion", "Motion", "dc-motion", "#02", "authored"],
  ["research", "User research", "dc-research", "#04 + #15", "authored"],
  ["engineering", "Front- and back-end", "dc-engineering", "#14", "authored"],
  ["game", "Game design / engines", "dc-game", "#12 + game-foundations", "authored"],
  ["imaging", "3D / environment", "dc-imaging", "#12", "authored"],
  ["vision", "Machine vision", "dc-vision", "#15", "authored"],
  ["visual-qa", "Visual QA", "dc-visual-qa", "#06 + #10", "authored"],
  ["illustration", "Illustration / graphic", "dc-illustration", "#01", "authored"],
  ["architecture", "Architecture / interior", "dc-architecture", "#01 borrowed", "authored"],
] as const;

function Graph({
  nodes,
  edges,
  labels,
  direction = "horizontal",
  nodeWidth = 160,
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
        rankGap: 48,
        nodeGap: 14,
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
            stroke={theme.stroke.secondary}
            strokeWidth={1.25}
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

function MapView() {
  return (
    <Stack gap={20}>
      <Callout tone="info" title="Same intents as the DS constitution">
        Methods not values. Complements table required. Three graphs do not mix.
        DSDS 0.20 is the design-systems file format only. Other domains use
        domain-constitution/1.0. Coverage bars below are a 2026-09-02 judgment,
        not a measured benchmark.
      </Callout>
      <Row gap={16} wrap>
        <Stat value="11" label="Authored packs" />
        <Stat value="1" label="Canonical (DSDS)" />
        <Stat value="3" label="Mapped, no YAML" />
      </Row>
      <H2>Job contexts</H2>
      <Table
        headers={["Id", "Job context", "Artifact", "L1", "Status"]}
        rows={AUTHORED.map((row) => [...row])}
        striped
        rowTone={AUTHORED.map((row) =>
          row[4] === "canonical" ? "success" : "info",
        )}
      />
      <H2>Connective tissue judgment</H2>
      <Text size="small" tone="secondary">
        Source: Domain Rigor Stack L1–L5 vs constitution completeness.
        Architecture and vision score lower on L2 (no lead hub). That is named
        in those YAML files, not hidden.
      </Text>
      <BarChart
        categories={[
          "DS",
          "UX/UI",
          "Motion",
          "Research",
          "Eng",
          "Game",
          "Imaging",
          "Vision",
          "VQA",
          "Graphic",
          "Arch",
        ]}
        series={[
          {
            name: "L1–L5 already in vault",
            data: [92, 88, 82, 70, 90, 84, 86, 62, 94, 74, 48],
          },
          {
            name: "Constitution pack (this pass)",
            data: [96, 88, 86, 82, 88, 86, 88, 80, 92, 78, 72],
          },
        ]}
        height={220}
        yMin={0}
        yMax={100}
      />
      <Text size="small" tone="secondary">
        Y axis: judgment 0–100. Bars are not detector output.
      </Text>
    </Stack>
  );
}

function ComplementsView() {
  return (
    <Stack gap={20}>
      <Text>
        Five cells, always. Collapsing two cells is how hex and engine versions
        become fake law.
      </Text>
      <Table
        headers={["Concern", "Question"]}
        rows={[
          ["Values", "What may change when brand, engine, repo, or study changes?"],
          ["Meaning", "Where is the method stated? (constitution + L1)"],
          ["Arbitration", "What can refuse deterministically?"],
          ["Look", "Where does project identity live?"],
          ["Runtime", "Wire format, engine, deployed model. Not the ontology."],
        ]}
        striped
      />
      <H2>Filled cells (examples)</H2>
      <Grid columns={2} gap={16}>
        <Card>
          <CardHeader>Engineering</CardHeader>
          <CardBody>
            <Stack gap={8}>
              <Text size="small">
                Values: stack versions. Meaning: #14 + eng-foundations.
                Arbitration: OpenAPI / ADR / SLO. Look: consume the DS.
                Runtime: deployed services plus observability.
              </Text>
            </Stack>
          </CardBody>
        </Card>
        <Card>
          <CardHeader>Vision</CardHeader>
          <CardBody>
            <Stack gap={8}>
              <Text size="small">
                Values: weights and datasets. Meaning: task taxonomy.
                Arbitration: dataset contract, frozen split, task metric.
                Look: n/a. Runtime: exported model vs latency budget.
                VLM prose is attested, never Literal.
              </Text>
            </Stack>
          </CardBody>
        </Card>
        <Card>
          <CardHeader>Game</CardHeader>
          <CardBody>
            <Stack gap={8}>
              <Text size="small">
                Values: Unity / Unreal / Three.js version. Meaning: loop,
                agency, feel. Arbitration: play-prove. Look: NORTHSTAR.md.
                Runtime: the engine adapter. Legion is a testbed.
              </Text>
            </Stack>
          </CardBody>
        </Card>
        <Card>
          <CardHeader>Visual QA</CardHeader>
          <CardBody>
            <Stack gap={8}>
              <Text size="small">
                Values: the artifact. Meaning: #06 + #10 + altitudes A–G.
                Arbitration: cuespec probes. Look: named northstar.
                Runtime: capture manifest. Thumbnail is a locator.
              </Text>
            </Stack>
          </CardBody>
        </Card>
      </Grid>
      <H3>When to load two packs</H3>
      <Table
        headers={["Job", "Load"]}
        rows={[
          ["Screen in a DS", "ux-ui + design-systems"],
          ["Animated UI", "motion + ux-ui"],
          ["Game environment", "imaging + game (not architecture)"],
          ["Literal UI recreation", "visual-qa + ux-ui"],
          ["CV on our renders", "vision + visual-qa"],
          ["FE implementing DS", "engineering + design-systems"],
        ]}
        striped
      />
    </Stack>
  );
}

function GraphsView() {
  return (
    <Stack gap={20}>
      <Text>
        One job context still has three graphs. Edge vocabularies do not cross.
      </Text>
      <Graph
        nodes={[
          { id: "req" },
          { id: "skill" },
          { id: "epist" },
          { id: "art" },
          { id: "act" },
        ]}
        edges={[
          { from: "req", to: "skill" },
          { from: "req", to: "epist" },
          { from: "req", to: "art" },
          { from: "skill", to: "act" },
          { from: "epist", to: "act" },
          { from: "art", to: "act" },
        ]}
        labels={{
          req: "Request",
          skill: "Skill-load",
          epist: "Epistemic",
          art: "Artifact",
          act: "Act / prove",
        }}
        nodeWidth={132}
      />
      <Grid columns={3} gap={16}>
        <Card>
          <CardHeader>Skill-load</CardHeader>
          <CardBody>
            <Text size="small">
              Foundation → hub → spoke. Related edges. Registry load_chains.
              Constitutions point here; they do not duplicate spoke tables.
            </Text>
          </CardBody>
        </Card>
        <Card>
          <CardHeader>Epistemic</CardHeader>
          <CardBody>
            <Text size="small">
              knowledge/memory relations: builds-on, refutes, exemplifies.
              Legion entries exemplify game/imaging law. They are not the law.
            </Text>
          </CardBody>
        </Card>
        <Card>
          <CardHeader>Domain artifact</CardHeader>
          <CardBody>
            <Text size="small">
              DSDS kinds for design-systems. domain-constitution/1.0 shared,
              entry, combos for everyone else. Same intents.
            </Text>
          </CardBody>
        </Card>
      </Grid>
      <Callout tone="warning" title="Always-on ban">
        Constitutions load on domain trigger, like foundations. Dumping every
        dc-*.yaml is the Atlassian field-test failure mode.
      </Callout>
    </Stack>
  );
}

function GapsView() {
  return (
    <Stack gap={20}>
      <H2>Named gaps (honest, not stubs)</H2>
      <Table
        headers={["Id", "Why not a YAML"]}
        rows={[
          ["product", "product-foundations + #15 exist; methods not extracted"],
          ["data", "Same. Seed is experiment-validity-baseline"],
          ["security", "#16 is a sideways lens on engineering"],
        ]}
        rowTone={["warning", "warning", "warning"]}
        striped
      />
      <H2>Authored with an explicit hole</H2>
      <Table
        headers={["Id", "Hole"]}
        rows={[
          ["vision", "No lead-vision hub. Foundation + vis-* spokes."],
          ["architecture", "No lead-architect. QA lenses + #01."],
          ["research", "No research hub. Spoke of lead-ux-designer + #04."],
          ["illustration", "No illustration L1. #01 plus graphic hub."],
        ]}
        striped
      />
      <H2>Do not do next</H2>
      <Stack gap={8}>
        <Text>Invent a sixth schema per domain.</Text>
        <Text>Clone DSDS token/theme kinds onto datasets or engines.</Text>
        <Text>Create orphan hubs so architecture or vision look complete.</Text>
        <Text>Auto-edit ontology from a source-watch hash change.</Text>
        <Text>Put Legion hull metalness or C8 hex into shared[].</Text>
      </Stack>
      <H2>Worth doing later</H2>
      <Stack gap={8}>
        <Text>
          Promote product / data / security when methods can be extracted
          without restating the hub.
        </Text>
        <Text>
          Add domain-tagged rows to ds-source-watch (report-first) once a
          source set is real.
        </Text>
        <Text>
          If a real architecture project starts: brief contract, then consider
          a hub (3+ consumers first).
        </Text>
      </Stack>
    </Stack>
  );
}

export default function DomainConstitutionsCanvas() {
  const theme = useHostTheme();
  const [view, setView] = useCanvasState<View>("view", "map");

  const shell: CSSProperties = {
    minHeight: "100%",
    background: theme.bg.editor,
    color: theme.text.primary,
    padding: 24,
  };

  return (
    <div style={shell}>
      <Stack gap={16}>
        <Stack gap={6}>
          <H1>Job-context constitutions</H1>
          <Text tone="secondary">
            Workspace pack · 2026-09-02 · design-systems as the template
          </Text>
        </Stack>
        <Row gap={8} wrap>
          {VIEWS.map((v) => (
            <span key={v.id}>
              <Pill active={view === v.id} onClick={() => setView(v.id)}>
                {v.label}
              </Pill>
            </span>
          ))}
        </Row>
        <Divider />
        {view === "map" ? <MapView /> : null}
        {view === "complements" ? <ComplementsView /> : null}
        {view === "graphs" ? <GraphsView /> : null}
        {view === "gaps" ? <GapsView /> : null}
      </Stack>
    </div>
  );
}
