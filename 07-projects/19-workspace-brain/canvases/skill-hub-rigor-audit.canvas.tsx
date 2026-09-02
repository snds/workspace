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
} from "cursor/canvas";

type Priority = "P0" | "P1" | "P2" | "P3" | "P4" | "Ref" | "Good" | "Defer";

type HubRow = {
  hub: string;
  knowledge: number;
  rigor: number;
  link: number;
  priority: Priority;
  gap: string;
};

const HUBS: HubRow[] = [
  {
    hub: "UI/UX / Design Systems",
    knowledge: 5,
    rigor: 5,
    link: 5,
    priority: "Ref",
    gap: "design-system-ops is a 4.8MB blob with no SKILL.md",
  },
  {
    hub: "Figma toolchain",
    knowledge: 4,
    rigor: 4,
    link: 5,
    priority: "Good",
    gap: "Best non-UI pattern; only diagramming is thin",
  },
  {
    hub: "Obsidian / vault tooling",
    knowledge: 3,
    rigor: 3,
    link: 4,
    priority: "Good",
    gap: "Already has instrumented /health + mirrored skills",
  },
  {
    hub: "Security",
    knowledge: 2,
    rigor: 1,
    link: 3,
    priority: "P0",
    gap: "4×~45-line spokes vs be-security-posture at 705 lines",
  },
  {
    hub: "Accessibility",
    knowledge: 4,
    rigor: 2,
    link: 3,
    priority: "P0",
    gap: "Deep a11y spokes, no axe/pa11y harness; lead lacks prerequisites",
  },
  {
    hub: "Plugin precedence (global)",
    knowledge: 5,
    rigor: 1,
    link: 1,
    priority: "P0",
    gap: "No AGENTS.md rule that workspace doctrine outranks plugins",
  },
  {
    hub: "Information Design / Dataviz",
    knowledge: 4,
    rigor: 1,
    link: 3,
    priority: "P1",
    gap: "Triple ownership (infod/fe/ux), no /qa lens",
  },
  {
    hub: "Icon / Vector",
    knowledge: 4,
    rigor: 2,
    link: 2,
    priority: "P1",
    gap: "Three leads missing prerequisites + Related",
  },
  {
    hub: "Frontend engineering",
    knowledge: 5,
    rigor: 2,
    link: 3,
    priority: "P1",
    gap: "29 spokes on one hub; perf/test is prose, no harness",
  },
  {
    hub: "Claude-1337 / arch-guild",
    knowledge: 4,
    rigor: 4,
    link: 1,
    priority: "P1",
    gap: "13 specialist agents exist; zero workspace routing",
  },
  {
    hub: "Career / job search",
    knowledge: 4,
    rigor: 1,
    link: 1,
    priority: "P1",
    gap: "~3.5k lines in ~/.agents, no workspace mirror",
  },
  {
    hub: "Information Architecture",
    knowledge: 4,
    rigor: 1,
    link: 3,
    priority: "P2",
    gap: "Best knowledge-per-line; zero pipeline/done-gates",
  },
  {
    hub: "Backend engineering",
    knowledge: 4,
    rigor: 1,
    link: 4,
    priority: "P2",
    gap: "Deep spokes, no engineering operating model",
  },
  {
    hub: "DevOps",
    knowledge: 4,
    rigor: 1,
    link: 3,
    priority: "P2",
    gap: "No incident/runbook done-gate; empty knowledge lane",
  },
  {
    hub: "Data Science / ML",
    knowledge: 4,
    rigor: 1,
    link: 3,
    priority: "P2",
    gap: "08-knowledge/data-science is README-only",
  },
  {
    hub: "Motion design",
    knowledge: 4,
    rigor: 3,
    link: 4,
    priority: "P2",
    gap: "/motion exists; motion-performance is prose-only",
  },
  {
    hub: "Mobile",
    knowledge: 2,
    rigor: 1,
    link: 2,
    priority: "P2",
    gap: "No lead-mobile; 4 spokes hang off frontend",
  },
  {
    hub: "Pstack / superpowers",
    knowledge: 4,
    rigor: 3,
    link: 1,
    priority: "P2",
    gap: "Silent collision risk with frameworks 06/11",
  },
  {
    hub: "Typography / Type",
    knowledge: 4,
    rigor: 3,
    link: 4,
    priority: "P3",
    gap: "qa_typography.py exists but /qa type lens is soft",
  },
  {
    hub: "Graphic / Brand",
    knowledge: 4,
    rigor: 3,
    link: 4,
    priority: "P3",
    gap: "No brand-consistency gate into color-Δe path",
  },
  {
    hub: "Product Management",
    knowledge: 3,
    rigor: 1,
    link: 3,
    priority: "P3",
    gap: "No PRD/spec contract artifact",
  },
  {
    hub: "Vision / CV",
    knowledge: 2,
    rigor: 1,
    link: 3,
    priority: "P4",
    gap: "Foundation-as-hub; no active project pull",
  },
  {
    hub: "Science / Math",
    knowledge: 3,
    rigor: 1,
    link: 3,
    priority: "P4",
    gap: "math-* deep; sci-* thin; low usage",
  },
  {
    hub: "Adobe App Builder",
    knowledge: 3,
    rigor: 2,
    link: 1,
    priority: "P4",
    gap: "Zero workspace reference; no consumer project",
  },
  {
    hub: "Imaging / Photo / VFX craft",
    knowledge: 2,
    rigor: 2,
    link: 2,
    priority: "Defer",
    gap: "Contested with photoreal session — leave alone",
  },
];

const OPPORTUNITIES: {
  id: string;
  title: string;
  leverage: string;
  why: string;
  moves: string[];
}[] = [
  {
    id: "1",
    title: "Security: stub hub → real discipline",
    leverage: "Highest",
    why: "Missed security detail is unrecoverable; whole cluster is ~226 lines while one backend slice is 705.",
    moves: [
      "Framework: security operating model (threat→build→scan→monitor + done-gates)",
      "Expand sec-* with decision tables; keep be-security-posture as implementation depth",
      "Wire review-security as evaluate half of evaluate→refine",
    ],
  },
  {
    id: "2",
    title: "Global plugin-precedence rule",
    leverage: "Cheapest blast radius",
    why: "Only 4 Figma skills + 2 hubs have Defers-to prose. ~120 plugins can silently override doctrine.",
    moves: [
      "AGENTS.md: workspace frameworks > workspace skills > plugins",
      "Add defers_to frontmatter + registry validation",
      "Do this before wiring arch-guild / pstack / superpowers",
    ],
  },
  {
    id: "3",
    title: "Wire or archive design-system-ops",
    leverage: "Largest dead mass",
    why: "4.8MB, 13 commands, 11 knowledge-notes, no SKILL.md → invisible to registry and routing.",
    moves: [
      "Either author SKILL.md as DS-ops command hub",
      "Or archive with provenance; relocate notes into 08-knowledge/design",
    ],
  },
  {
    id: "4",
    title: "Break measurement monoculture",
    leverage: "Enforcement",
    why: "visual-qa-toolkit is the only instrumented toolkit. Accessibility and FE perf audit as prose.",
    moves: [
      "a11y-audit-toolkit (axe/pa11y) mirroring visual-qa-toolkit shape",
      "Add /qa lenses: motion, dataviz, type",
      "FE perf harness for LCP/INP/CLS budgets",
    ],
  },
  {
    id: "5",
    title: "Domain operating models (eng + analysis + IA)",
    leverage: "Pipeline",
    why: "Only framework #02 is domain-operational. Deep hubs know truth, not order or done.",
    moves: [
      "engineering-operating-model (FE/BE/DevOps contracts-first + gates)",
      "analysis-operating-model (question→contract→method→validity→decision)",
      "Extend #02 Layer 1 for full IA pipeline (not a new file)",
      "Coordinate numbering with photoreal session (they may want #12)",
    ],
  },
  {
    id: "6",
    title: "Icon/vector orphan triad",
    leverage: "Highest fix/token ratio",
    why: "lead-icon/vector/technical-digital-artist lack prerequisites and Related; load_chains break.",
    moves: [
      "prerequisites: [design-foundations] + Related blocks",
      "Also add prerequisites on a11y + IA + visual-qa leads",
      "Rebuild registry + vault-health",
    ],
  },
  {
    id: "7",
    title: "Wire arch-guild into eng review",
    leverage: "Multi-voice parity",
    why: "Design gets 8 QA voices; eng gets one. Guild already ships 13 specialists + evals.",
    moves: [
      "Thin workspace wrapper (motion hub pattern)",
      "CLAUDE.md routing row after precedence rule lands",
    ],
  },
  {
    id: "8",
    title: "Knowledge rebalance + career home",
    leverage: "Retrieval health",
    why: "research/ is 7.8k lines (photoreal); data-science is empty; career skills are orphaned outside workspace.",
    moves: [
      "Mirror career-ops trio into 03-skills like obsidian-*",
      "Seed one knowledge entry per empty domain",
      "Add CLAUDE.md trigger rows",
    ],
  },
];

function pillTone(p: Priority): "neutral" | "info" | "success" | "warning" {
  if (p === "P0" || p === "P1") return "warning";
  if (p === "Good" || p === "Ref") return "success";
  if (p === "P2") return "info";
  return "neutral";
}

function OpportunityCard({
  op,
}: {
  op: (typeof OPPORTUNITIES)[number];
}) {
  return (
    <Card>
      <CardHeader trailing={<Pill tone="warning" size="sm">{op.leverage}</Pill>}>
        {`${op.id}. ${op.title}`}
      </CardHeader>
      <CardBody>
        <Stack gap={8}>
          <Text weight="semibold">{op.why}</Text>
          <Text tone="secondary" size="small">
            {op.moves.join(" · ")}
          </Text>
        </Stack>
      </CardBody>
    </Card>
  );
}

export default function SkillHubRigorAudit() {
  const p0 = HUBS.filter((h) => h.priority === "P0").length;
  const p1 = HUBS.filter((h) => h.priority === "P1").length;
  const softRigor = HUBS.filter(
    (h) => h.rigor <= 2 && h.priority !== "Defer",
  ).length;

  return (
    <Stack gap={24} style={{ padding: 24, maxWidth: 1100 }}>
      <Stack gap={8}>
        <H1>Skill hub rigor audit</H1>
        <Text tone="secondary" style={{ maxWidth: 720 }}>
          Cross-hub evaluation excluding the realtime photoreal / 3D / game work
          owned by the parallel session. Scores are against the UI/UX five-layer
          rigor pattern: operational framework, command hub, measurement toolkit,
          lead→spoke load chain, multi-voice routing.
        </Text>
      </Stack>

      <Grid columns={4} gap={12}>
        <Stat value={String(p0)} label="P0 clusters" tone="danger" />
        <Stat value={String(p1)} label="P1 clusters" tone="warning" />
        <Stat
          value={String(softRigor)}
          label="Rigor ≤2 (active)"
          tone="warning"
        />
        <Stat value="1" label="Instrumented toolkits" tone="danger" />
      </Grid>

      <Callout tone="success" title="Hardening pass landed (2026-08-03)">
        Framework #13 Domain Rigor Stack is now mandatory for new/improved hubs.
        Also shipped: #14–#16, doctrine precedence, security depth, measurement
        toolkits, /eng + arch-guild wrappers, design-system-ops wiring, career
        mirrors, knowledge seeds. Validators: links, integrity, capabilities green.
        Changes are staged in Workspace; commit when you want.
      </Callout>

      <Callout tone="info" title="Original diagnosis (pre-hardening)">
        Knowledge was broadly strong. The rigor layer had been a monoculture around
        UI/UX. That gap is what this pass closed across the other hubs.
      </Callout>

      <Stack gap={8}>
        <H2>Reference stack (already working)</H2>
        <Row gap={8} wrap>
          <Pill tone="success">#02 UI/UX ops</Pill>
          <Pill tone="success">#06 QA gate</Pill>
          <Pill tone="success">#10 perception</Pill>
          <Pill tone="success">#11 premortem</Pill>
          <Pill tone="success">/qa command hub</Pill>
          <Pill tone="success">visual-qa-toolkit</Pill>
          <Pill tone="success">Impeccable loop</Pill>
          <Pill tone="success">Figma Defers-to</Pill>
        </Row>
      </Stack>

      <Divider />

      <Stack gap={12}>
        <H2>Top 8 opportunities by leverage</H2>
        <Grid columns={2} gap={12}>
          <OpportunityCard op={OPPORTUNITIES[0]} />
          <OpportunityCard op={OPPORTUNITIES[1]} />
          <OpportunityCard op={OPPORTUNITIES[2]} />
          <OpportunityCard op={OPPORTUNITIES[3]} />
          <OpportunityCard op={OPPORTUNITIES[4]} />
          <OpportunityCard op={OPPORTUNITIES[5]} />
          <OpportunityCard op={OPPORTUNITIES[6]} />
          <OpportunityCard op={OPPORTUNITIES[7]} />
        </Grid>
      </Stack>

      <Divider />

      <Stack gap={12}>
        <H2>Hub scorecard</H2>
        <Text tone="secondary" size="small">
          Knowledge / Rigor / Link scored 1–5. Source: Workspace 03-skills +
          frameworks + plugin stacks. Photoreal/3D/game hubs omitted.
        </Text>
        <Table
          headers={["Hub", "Know", "Rigor", "Link", "Priority", "Top gap"]}
          columnAlign={["left", "center", "center", "center", "center", "left"]}
          rows={HUBS.map((h) => [
            h.hub,
            String(h.knowledge),
            String(h.rigor),
            String(h.link),
            h.priority,
            h.gap,
          ])}
          rowTone={HUBS.map((h) =>
            h.priority === "P0"
              ? "danger"
              : h.priority === "P1"
                ? "warning"
                : undefined,
          )}
        />
        <Row gap={8} wrap>
          <Pill tone={pillTone("P0")} size="sm">P0</Pill>
          <Pill tone={pillTone("P1")} size="sm">P1</Pill>
          <Pill tone={pillTone("P2")} size="sm">P2</Pill>
          <Pill tone={pillTone("Good")} size="sm">Good</Pill>
          <Pill tone={pillTone("Defer")} size="sm">Defer</Pill>
        </Row>
      </Stack>

      <Divider />

      <Grid columns={2} gap={16}>
        <Stack gap={8}>
          <H3>Deprioritize</H3>
          <Text size="small" tone="secondary">
            Figma (copy this pattern). Backend/DevOps/DS/Motion/Type/IA/Infod
            knowledge volume (add rigor, not spokes). Core validators +
            capability-registry. Obsidian tooling. Vision/Science/Adobe until a
            project pulls. found-* and *-foundations brevity is intentional.
          </Text>
        </Stack>
        <Stack gap={8}>
          <H3>Photoreal session boundary</H3>
          <Text size="small" tone="secondary">
            Do not touch img-photoreal, realtime-render-performance, 3d-*,
            game-*, legion-*, visual-qa-game-design, glsl/webgpu/threejs VFX, or
            08-knowledge/research + game-dev. Leave entire img-* craft chain to
            that session. Coordinate framework numbering before claiming #12.
          </Text>
        </Stack>
      </Grid>

      <Spacer height={8} />
      <Text size="small" tone="tertiary">
        Parallel session: Realtime Photoreal Rigor. Evidence checked on security
        line counts, design-system-ops size, icon-lead orphans, and missing
        AGENTS.md precedence rule.
      </Text>
    </Stack>
  );
}
