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
} from "cursor/canvas";

const LADDER = [
  {
    rung: "A. Pixel / structure",
    question: "This hex, gutter, count, crop?",
    tools: "SSIM, Δe, region count, cuespec probes",
    now: "In production (visual-prove-engine)",
  },
  {
    rung: "B. Psychovisual (HVS)",
    question: "Would a human see a difference at this distance?",
    tools: "NVIDIA FLIP, Butteraugli, HDR-VDP",
    now: "Δe only; no error maps, no viewing-distance model",
  },
  {
    rung: "C. Mid-level learned",
    question: "Same layout, pose, foreground object?",
    tools: "DreamSim, LPIPS, DISTS",
    now: "SSIM used as a stand-in; fails novel-view and GPU jitter",
  },
  {
    rung: "D. No-reference / aesthetic",
    question: "Is this good without a pixel-twin?",
    tools: "Q-Align, ArtiMuse, CLIP-IQA",
    now: "Absent. CLIP-IQA is a poor 3DGS metric anyway",
  },
  {
    rung: "E. Geometric / 3D-native",
    question: "Is the shape, splat, or asset valid?",
    tools: "VGGT / DUSt3R, GSOQA, glTF auditor",
    now: "Absent. Screenshot QA cannot catch hollow meshes",
  },
  {
    rung: "F. Process / interaction",
    question: "Did the action cause the intended change?",
    tools: "vqa interact, VisCritic, VeriGUI",
    now: "Pixel delta exists; no learned progress critic",
  },
  {
    rung: "G. Simulation / feel / balance",
    question: "Does it play? Does it feel?",
    tools: "Input-to-photon, CoTracker jerk, AutoSim, MCTS",
    now: "Coarse motion jerk only; no latency, no playtest lane",
  },
];

const CORRECTIONS = [
  ["1", "Name altitudes on each cue", "Prove engine + #06", "Stops 16/16 from meaning done-in-every-sense"],
  ["2", "FLIP maps beside SSIM", "vqa compare + render-qa", "Graphics-native error maps; SSIM stays the no-torch floor"],
  ["3", "Optional DreamSim", "Spirit / NVS / 3DGS", "Not for Literal gutters; document foreground bias"],
  ["4", "vqa mesh via glTF tools", "New cue class", "Structural 3D gate, no ML weights"],
  ["5", "VGGT orbit consistency", "interactive-capture-eval", "Two-view reconstruct vs authoring cameras"],
  ["6", "Saliency + OCR probes", "UI Spirit / LCARS attestations", "UEyes hierarchy; turn attested strings measured"],
  ["7", "Learned critic on interact", "vqa interact", "Pixel fail still wins; critic is progress-only"],
  ["8", "Tracks + input-to-photon", "vqa motion + game-feel", "CoTracker jerk; software latency for CI"],
  ["9", "Renderer in capture manifest", "Capture policy", "Software vs hardware tracks; MAD-FLIP not MD5"],
  ["10", "play-prove sibling", "lead-game-designer", "Win-rate / diversity stay out of vqa.py"],
  ["11", "Cross-model VLM protocol", "Spirit / Intent only", "Two families, A/B swap; never Literal spec"],
  ["12", "Name uncued residuals", "Ledger", "Coverage holes as a field, not a footnote"],
];

const LIMITS = [
  ["Taste / Intent", "MOS models score photos, not LCARS grammar or a northstar"],
  ["First fixation", "VLMs fail 1s gaze; UI-TARS has ~0 correlation with human attention"],
  ["Strategic play", "LLMs lose to MCTS; use LLM confusion as a rule-clarity detector"],
  ["Single VLM judge", "~26% of mesh-quality verdicts flip with presentation order"],
  ["Uncued residuals", "A passing cuespec cannot see what it did not probe"],
];

export default function PerceptionCritiqueStack() {
  return (
    <Stack gap={24} style={{ maxWidth: 960 }}>
      <Stack gap={8}>
        <H1>Perception critique stack</H1>
        <Text tone="secondary" size="small">
          Field research 2026-08-28 · sources in 08-knowledge/research/perception-critique-stack.md
        </Text>
        <Text>
          There is no single better metric than SSIM. The field is a ladder of
          altitudes. This workspace is strong at the pixel rung and almost silent
          above it, which is why a Literal UI pack can measure 16/16 while a
          human still sees missing structure, and why a still-grid cannot close
          3D, motion, or game feel.
        </Text>
      </Stack>

      <Grid columns={4} gap={12}>
        <Stat value="7" label="Metric altitudes" />
        <Stat value="A only" label="Where prove is production-ready" tone="warning" />
        <Stat value="12" label="Course corrections" />
        <Stat value="5" label="Hard honesty bounds" />
      </Grid>

      <Callout tone="warning" title="Do not replace the prove engine">
        Literal UI replication stays on rung A. DreamSim, CLIP, and VLMs are the
        wrong primary judge for 8px gutters. The 2026-08-26 measured-vs-attested
        split still holds. What was gated was the search past NumPy SSIM, not
        the refusal of VLM-as-spec.
      </Callout>

      <Stack gap={8}>
        <H2>Current coverage vs field</H2>
        <Text size="small" tone="secondary">
          Subjective 0–100 ratings of this workspace vs each altitude, not MOS.
          A is production; F is a pixel floor; the rest are gaps.
        </Text>
        <BarChart
          height={220}
          categories={[
            "A Pixel",
            "B HVS",
            "C Mid-level",
            "D Aesthetic",
            "E Geometry",
            "F Process",
            "G Feel/sim",
          ]}
          series={[
            {
              name: "Coverage (0–100)",
              data: [90, 15, 10, 5, 0, 40, 20],
              tone: "info",
            },
          ]}
          yMax={100}
          valueSuffix=""
          showValues
        />
      </Stack>

      <Stack gap={8}>
        <H2>The ladder</H2>
        <Table
          headers={["Altitude", "Question", "Field tools", "Here now"]}
          columnAlign={["left", "left", "left", "left"]}
          rows={LADDER.map((r) => [r.rung, r.question, r.tools, r.now])}
          rowTone={LADDER.map((_, i) => (i === 0 ? "success" : i === 5 ? "warning" : "neutral"))}
        />
      </Stack>

      <Divider />

      <H2>What the field added by medium</H2>
      <Grid columns={2} gap={16}>
        <Card>
          <CardHeader>UI and visual design</CardHeader>
          <CardBody>
            <Stack gap={8}>
              <Text>
                CANVAS (AAAI 2026) scores designs at three levels: SSIM, UEyes
                saliency, BLIP semantics. UIGaze: VLMs approximate 7-second
                exploration and fail 1-second first fixations. Operator agents
                are not hierarchy critics.
              </Text>
              <Row gap={8}>
                <Pill tone="info" size="sm">
                  UEyes
                </Pill>
                <Pill tone="info" size="sm">
                  OmniParser
                </Pill>
                <Pill size="sm">OCR measured</Pill>
              </Row>
            </Stack>
          </CardBody>
        </Card>
        <Card>
          <CardHeader>3D and neural rendering</CardHeader>
          <CardBody>
            <Stack gap={8}>
              <Text>
                Asset hygiene is structural (glTF validator, texel density,
                manifold). Appearance is perceptual: 3DGS papers show
                PSNR/SSIM/LPIPS poorly track MOS; DISTS, Q-Align, and
                primitive-native models do better. VGGT reconstructs cameras
                and depth in one pass for a consistency check, not a beauty score.
              </Text>
              <Row gap={8}>
                <Pill tone="warning" size="sm">
                  Chamfer lies
                </Pill>
                <Pill size="sm">VGGT</Pill>
                <Pill size="sm">FLIP</Pill>
              </Row>
            </Stack>
          </CardBody>
        </Card>
        <Card>
          <CardHeader>Interaction</CardHeader>
          <CardBody>
            <Stack gap={8}>
              <Text>
                VisCritic and VeriGUI train critics on pre/post screenshots.
                That is the Spirit layer on top of vqa interact. Pixel expected
                change remains the hard gate for dead controls and side effects.
              </Text>
              <Row gap={8}>
                <Pill tone="success" size="sm">
                  vqa interact
                </Pill>
                <Pill size="sm">VisCritic</Pill>
              </Row>
            </Stack>
          </CardBody>
        </Card>
        <Card>
          <CardHeader>Game engine and design</CardHeader>
          <CardBody>
            <Stack gap={8}>
              <Text>
                GPU goldens are not byte-stable: software renderer plus FLIP
                with MAD, not MD5. Feel is input-to-photon and track jerk.
                Balance is headless simulation (win-rate, no dominant strategy),
                not vision. MCTS plays; LLMs expose unclear rules.
              </Text>
              <Row gap={8}>
                <Pill size="sm">SwiftShader</Pill>
                <Pill size="sm">AutoSim</Pill>
                <Pill size="sm">MCTS</Pill>
              </Row>
            </Stack>
          </CardBody>
        </Card>
      </Grid>

      <Stack gap={8}>
        <H2>Honesty bounds</H2>
        <Table
          headers={["Bound", "Why it stays a human or a different tool"]}
          rows={LIMITS}
        />
      </Stack>

      <Stack gap={8}>
        <H2>Course corrections, ordered</H2>
        <Text size="small" tone="secondary">
          First slice that needs no new weights: cue altitudes, FLIP-optional
          compare, vqa mesh, saliency+OCR, renderer field on captures.
        </Text>
        <Table
          headers={["#", "Change", "Lands in", "Why"]}
          rows={CORRECTIONS}
        />
      </Stack>

      <Callout tone="info" title="Refuse these imports">
        A general beauty CNN as the Literal gate. CLIP-IQA as a 3DGS done-metric.
        VGGT as Construction IR. UI-TARS as a hierarchy critic. MD5 frames for
        Legion. One multimodal model that claims to do all of QA.
      </Callout>

      <H3>Related vault</H3>
      <Text size="small" tone="secondary">
        measured-visual-verdicts · visual-reference-replication-findings ·
        agentic-error-correction-foundations · vision-foundations · game-foundations
      </Text>
    </Stack>
  );
}
