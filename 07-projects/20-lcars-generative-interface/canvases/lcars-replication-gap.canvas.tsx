import {
  Callout,
  Card,
  CardBody,
  CardHeader,
  Divider,
  Grid,
  H1,
  H2,
  Pill,
  Row,
  Stack,
  Stat,
  Table,
  Text,
} from "cursor/canvas";

const GAPS = [
  {
    id: "G1",
    gap: "VLM narrative as measurement",
    severity: "critical",
    evidence: "Hex, gutters, segment counts invented from image prose; never probed native pixels",
    specialty: "Machine vision / metrology",
    ledger: "C-03",
  },
  {
    id: "G2",
    gap: "Spirit treated as Literal done",
    severity: "critical",
    evidence: "LCARS-ish CSS grid shipped; cue matrix never written; 'reads as' accepted",
    specialty: "Fidelity contracts",
    ledger: "C-04",
  },
  {
    id: "G3",
    gap: "No Construction IR before code",
    severity: "critical",
    evidence: "Jumped to React modules without region graph / segment inventory",
    specialty: "Design structure transcription",
    ledger: "C-05",
  },
  {
    id: "G4",
    gap: "Constraint-driven aesthetic collapse",
    severity: "high",
    evidence: "APCA / density / tokens reshaped look away from stills without ADR",
    specialty: "Authority hierarchy",
    ledger: "C-06",
  },
  {
    id: "G5",
    gap: "Fake / memory-drawn assets",
    severity: "high",
    evidence: "Hand-waved SVGs vs traced sourceCrop geometry",
    specialty: "Asset tracing",
    ledger: "C-07",
  },
  {
    id: "G6",
    gap: "Elbow grammar approximated",
    severity: "high",
    evidence: "border-radius boxes stand in for constant-thickness L",
    specialty: "Okudagram construction",
    ledger: "C-08",
  },
  {
    id: "G7",
    gap: "Measurement stack unused as done-gate",
    severity: "critical",
    evidence: "native-visual-eval / visual-qa-toolkit / lead-visual-qa existed; not enforced",
    specialty: "Process discipline",
    ledger: "Z-04",
  },
  {
    id: "G8",
    gap: "Thumbnail / chat preview as verdict",
    severity: "medium",
    evidence: "Fit-to-window screenshots used for craft judgment",
    specialty: "Perception integrity",
    ledger: "Z-05",
  },
] as const;

const ARTIFACTS = [
  ["General skill", "03-skills/visual-reference-replication/", "Literal pipeline: IR → cues → implement → prove"],
  ["Schema", "…/reference/construction-ir.md", "Machine-checkable frame/segment/type/asset IR"],
  ["Knowledge", "08-knowledge/…/visual-failure-mode-ledger.md", "C-03…C-08, Z-04–05 technique rows"],
  ["Project law", "07-projects/20-…/NORTHSTAR.md", "S-SYS47-01 Literal contract + cue stub"],
  ["Project law", "…/docs/visual-replication-requirements.md", "Hard stops + prove gate"],
  ["App rules", "lcars-generative-interface/.cursor/rules/", "literal-replication + construction-grammar"],
  ["Triggers", "02-shared-references/trigger-routes.json", "farce / recreate / literal match → skill"],
] as const;

const PIPELINE = [
  ["0", "Contract", "Name Literal (default for recreation)"],
  ["1", "Northstar", "S-ID + path + crop plan"],
  ["2", "Native capture", "PNG at subject resolution"],
  ["3", "Construction IR", "Measure frame, segments, type, assets"],
  ["4", "Cue matrix", "Falsifiable must-pass list"],
  ["5", "Implement", "Code only from IR; extend grammar if missing"],
  ["6", "Prove", "Side-by-side + SSIM/Δe/alignment"],
  ["7", "Verdict", "Matches Literal | Partial | Fail"],
] as const;

export default function LcarsReplicationGapCanvas() {
  const critical = GAPS.filter((g) => g.severity === "critical").length;
  const high = GAPS.filter((g) => g.severity === "high").length;

  return (
    <Stack gap={24} style={{ padding: 24, maxWidth: 1100 }}>
      <Stack gap={8}>
        <H1>LCARS visual replication — gap analysis</H1>
        <Text tone="secondary">
          Adversarial evaluation of why craft output failed vs Sean's reference library, and what
          was installed so Literal recreation becomes enforceable. As of 2026-08-09.
        </Text>
      </Stack>

      <Callout tone="danger" title="Verdict">
        The failure was not "needs more polish." It was the wrong done contract: Spirit vibe-match
        and test-green shipped where Literal structure transcription + instrumented prove were
        required. Existing visual QA skills were never the acceptance gate.
      </Callout>

      <Callout tone="info" title="Program intent (clarified)">
        LCARS is pack #1 and the hard proof. The goal is systemic recreation (concept, context,
        intent, aesthetic) via Construction IR → Scene IR → renderer so other aesthetics can load
        as packs later. Pixel clone without programmatic emission fails the ladder.
      </Callout>

      <Grid columns={4} gap={12}>
        <Stat value={String(critical)} label="Critical gaps" tone="danger" />
        <Stat value={String(high)} label="High gaps" tone="warning" />
        <Stat value="Literal" label="Required contract" />
        <Stat value="S-SYS47-01" label="First recreation target" />
      </Grid>

      <Divider />

      <Stack gap={12}>
        <H2>Capability gaps (adversarial)</H2>
        <Table
          headers={["ID", "Gap", "Sev", "What happened", "Specialty missing", "Ledger"]}
          rows={GAPS.map((g) => [
            g.id,
            g.gap,
            g.severity,
            g.evidence,
            g.specialty,
            g.ledger,
          ])}
          rowTone={GAPS.map((g) =>
            g.severity === "critical" ? "danger" : g.severity === "high" ? "warning" : undefined,
          )}
          columnAlign={["left", "left", "center", "left", "left", "center"]}
        />
      </Stack>

      <Grid columns={2} gap={16}>
        <Card>
          <CardHeader>Had skills — did not use as done-gates</CardHeader>
          <CardBody>
            <Stack gap={8}>
              <Text>native-visual-eval · visual-qa-toolkit · reference-video-review</Text>
              <Text>lead-visual-qa (Literal/Spirit vocabulary existed)</Text>
              <Text tone="secondary">
                Gap G7: process discipline, not missing tooling. New skill forces the order and
                locks Literal for recreation briefs.
              </Text>
            </Stack>
          </CardBody>
        </Card>
        <Card>
          <CardHeader>Specialty holes the new skill covers</CardHeader>
          <CardBody>
            <Stack gap={6}>
              <Text>Design structure transcription (frame graph before React)</Text>
              <Text>Pixel metrology (Lab/Δe, ratios, radii) over VLM prose</Text>
              <Text>Okudagram grammar (constant-thickness elbows, gutters)</Text>
              <Text>Authority hierarchy (northstar wins over secondary constraints)</Text>
              <Text>Prove language (Matches / Partial / Fail only)</Text>
            </Stack>
          </CardBody>
        </Card>
      </Grid>

      <Stack gap={12}>
        <H2>Artifacts landed this pass</H2>
        <Table
          headers={["Kind", "Where", "Job"]}
          rows={ARTIFACTS.map((a) => [a[0], a[1], a[2]])}
        />
      </Stack>

      <Stack gap={12}>
        <H2>Enforced pipeline (next coding pass)</H2>
        <Text tone="secondary">
          Blocked until S-SYS47-01 IR probes are filled. Do not implement Literal recreation from
          the stub.
        </Text>
        <Table
          headers={["Step", "Phase", "Requirement"]}
          rows={PIPELINE.map((p) => [p[0], p[1], p[2]])}
          columnAlign={["center", "left", "left"]}
        />
      </Stack>

      <Callout tone="warning" title="Next agent action">
        Extract a native still from System47 Enterprise-E Schematics MKV → fill
        docs/construction/S-SYS47-01 → cue matrix → implement from IR only in the app → prove with
        native crops + visual-qa-toolkit. Backup northstar: S-TITAN-01.
      </Callout>

      <Row gap={8} wrap>
        <Pill tone="neutral">Workspace skill</Pill>
        <Pill tone="neutral">Project NORTHSTAR</Pill>
        <Pill tone="neutral">App cursor rules</Pill>
        <Pill tone="info">Prove gate</Pill>
      </Row>

      <Text tone="secondary">
        Source: session 2026-08-09 adversarial review · LCARS generative interface
      </Text>
    </Stack>
  );
}
