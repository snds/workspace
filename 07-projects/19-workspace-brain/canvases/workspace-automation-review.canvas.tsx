import {
  BarChart,
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
  useCanvasState,
} from "cursor/canvas";

type FilterId = "all" | "keep" | "mint" | "refuse";

const FILTERS: { id: FilterId; label: string }[] = [
  { id: "all", label: "All" },
  { id: "keep", label: "Already automated" },
  { id: "mint", label: "Mint a script" },
  { id: "refuse", label: "Do not automate" },
];

const EXISTING = [
  ["Graph builders", "build-related / build-registry / build-trigger-routes", "Stops hand-edited graphs", "keep"],
  ["Write-quality CI", "validate-integrity / links / workspace / capabilities", "Any agent may write; CI refuses zombies", "keep"],
  ["Negative fixtures", "test-validators.py + vqa calibrate", "A green detector that never saw a defect is not a detector", "keep"],
  ["Layer 0", "prompt_route.py + routing corpus", "Find skills without ingesting the registry", "keep"],
  ["Lexical fallback", "vault-retrieve.py", "Layer 1 when Layer 0 under-fires", "keep"],
  ["Visual prove", "vqa prove / capture / calibrate", "Pixels, not VLM “looks good”", "keep"],
  ["Intent kernel", "intent-run.py gate / verify", "Multi-agent jobs cannot self-approve", "keep"],
  ["Off-system CSS", "eslint-off-system/ (product repos)", "Off-system values inexpressible; CI is the contract", "keep"],
  ["Nightly recipe", "compact-sessions + rebuild chain (opt-in, not enabled)", "Fold / rebuild / report — does not invent skills", "keep"],
];

const RECS: {
  id: string;
  title: string;
  change: string;
  why: string;
  tokens: string;
  validity: string;
  bucket: FilterId;
  tone: "info" | "success" | "warning" | "neutral" | "deleted";
}[] = [
  {
    id: "A1",
    title: "skill-loadset CLI",
    change: "One stdlib script: utterance → ordered SKILL.md paths via load_chains.",
    why: "AGENTS.md already specifies the algorithm. Agents still ingest or guess.",
    tokens: "Replaces ~55k registry ingest with a 10-line print.",
    validity: "Next cold agent can compute the load set without reading the graph essay.",
    bucket: "mint",
    tone: "info",
  },
  {
    id: "A2",
    title: "Hub L3 coverage check",
    change: "CI: every command hub must name a detector (requires, toolkit in chain, or rigor_role measurement).",
    why: "#13 says audit without L3 is critique. 33/47 hubs have empty governed_by.",
    tokens: "Stops loading a 400-line hub that cannot refuse false done.",
    validity: "Construct: “operationally ready” = named independent check, not more prose.",
    bucket: "mint",
    tone: "info",
  },
  {
    id: "A3",
    title: "close-out dispatch CLI",
    change: "Hub/domain in → the one command to run (vqa, axe, validate-integrity, honest skip).",
    why: "Close-out is now injected; compliance is still “read this skill.” A CLI is the loop.",
    tokens: "Skip the skill body when the detector is already named.",
    validity: "Same-model self-test is not the detector; the CLI must exit non-zero.",
    bucket: "mint",
    tone: "info",
  },
  {
    id: "A4",
    title: "nightly.sh one-shot",
    change: "Wrap the existing recipe in one script. Do not enable cron until you say so.",
    why: "The recipe is markdown. Agents re-read it; machines need an entrypoint.",
    tokens: "Zero during chat if launchd runs it.",
    validity: "Report-first; no epistemic auto-rewrite (already the recipe’s guardrail).",
    bucket: "mint",
    tone: "neutral",
  },
  {
    id: "A5",
    title: "Ruff on 09-tools (CI-only)",
    change: "Lint/format the automation layer. Not a runtime dependency of the vault.",
    why: "2026 agent shops put ruff/ty on the hot path; our scripts are the steel curtain.",
    tokens: "None in-session. Catches script bugs before they launder green.",
    validity: "Does not violate stdlib-only runtime; CI image may install ruff.",
    bucket: "mint",
    tone: "neutral",
  },
  {
    id: "A6",
    title: "Secret scan in CI",
    change: "gitleaks or detect-secrets on tracked files.",
    why: "Personal vault + employer wall. Accuracy includes not leaking.",
    tokens: "None. Prevents a class of irreversible miss.",
    validity: "Independent refuse. Do not LLM-review diffs for secrets.",
    bucket: "mint",
    tone: "warning",
  },
  {
    id: "A7",
    title: "Schema-check Layer 0 JSON",
    change: "JSON Schema for trigger-routes, knowledge-hints, routing cases.",
    why: "A malformed route file fail-opens to silence (Cursor {}).",
    tokens: "Prevents a silent empty Layer 0.",
    validity: "Parse errors are already fail-open; schema makes that a CI red.",
    bucket: "mint",
    tone: "neutral",
  },
  {
    id: "A8",
    title: "Figma bind probe (smallest)",
    change: "MCP inspect: fills bound to semantic + mode tokens, not Color/*. Instances not rects.",
    why: "Process-rigor: construction doctrine exists; no machine check.",
    tokens: "Replaces a native-zoom essay when the probe can refuse.",
    validity: "Photoreal/#12 attach template: copy the done-gate, not GPU scripts.",
    bucket: "mint",
    tone: "warning",
  },
  {
    id: "A9",
    title: "Analysis pre-registration lint",
    change: "Reports that say VERIFIED must name detector + decision rule fields.",
    why: "experiment-validity-baseline: no pre-committed rule → narrative, not evidence.",
    tokens: "Blocks #15/#PM hubs from shipping a story as a finding.",
    validity: "Construct first: the metric must match the claim.",
    bucket: "mint",
    tone: "info",
  },
  {
    id: "A10",
    title: "cursor-externalize --check in CI",
    change: "Fail if Cursor canvases exist locally uncopied (this machine only) — or skip on GitHub.",
    why: "Reviews that live only in ~/.cursor never reach the other laptop.",
    tokens: "N/A on GitHub (INACCESSIBLE). Local doctor/session-end is the real gate.",
    validity: "GitHub cannot see ~/.cursor. Prefer session-end hook over CI theater.",
    bucket: "mint",
    tone: "neutral",
  },
  {
    id: "R1",
    title: "No promptfoo / LLM-as-judge hot path",
    change: "Do not add an eval harness that grades “looks good” with another model.",
    why: "Frost steel curtain + #06 + vqa calibrate: the producing model is not the witness.",
    tokens: "Would add cost and flakiness to every commit.",
    validity: "If the property has a verifiable answer, write the check. Taste stays human/Proofboard.",
    bucket: "refuse",
    tone: "deleted",
  },
  {
    id: "R2",
    title: "No cloned vqa toolkits per hub",
    change: "Do not copy visual-prove-engine into type / motion / PM / career.",
    why: "#13: replicate measurement intent, not GPU scripts. Photoreal is the attach template.",
    tokens: "Clone would explode preload for the wrong domain.",
    validity: "A type hub’s L3 is fonttools/contrast, not SSIM.",
    bucket: "refuse",
    tone: "deleted",
  },
  {
    id: "R3",
    title: "No always-on skill catalog ingest",
    change: "Do not “fix tokens” by pasting close-out into 47 hubs or SessionStart _INDEX.",
    why: "Token diet is #1. Injection + CLI beats duplicated law.",
    tokens: "Would recreate the 70k read-order miss.",
    validity: "More prose does not change what the next agent can prove.",
    bucket: "refuse",
    tone: "deleted",
  },
];

function toneFor(bucket: string): "info" | "success" | "warning" | "deleted" | "neutral" {
  if (bucket === "keep") return "success";
  if (bucket === "mint") return "info";
  if (bucket === "refuse") return "deleted";
  return "neutral";
}

export default function WorkspaceAutomationReview() {
  const [filter, setFilter] = useCanvasState<FilterId>("filter", "all");

  const existingRows = EXISTING.filter((r) => filter === "all" || filter === "keep").map(
    (r) => [r[0], r[1], r[2], <Pill size="sm" tone="success" active>keep</Pill>],
  );

  const mintRows = RECS.filter((r) => r.bucket === "mint").map((r) => [
    r.id,
    r.title,
    r.change,
    r.tokens,
    <Pill size="sm" tone={r.tone} active>mint</Pill>,
  ]);

  const refuseRows = RECS.filter((r) => r.bucket === "refuse").map((r) => [
    r.id,
    r.title,
    r.validity,
    <Pill size="sm" tone="deleted" active>refuse</Pill>,
  ]);

  return (
    <Stack gap={20}>
      <Stack gap={8}>
        <H1>Workspace automation review</H1>
        <Text tone="secondary" size="small">
          Source: live registry 2026-09-11 · 299 skills · 22 portable 09-tools scripts · 5
          GitHub workflows · process-rigor R1–R16, #13 Domain Rigor Stack, #06 QA, Frost steel
          curtain, experiment-validity-baseline, Nate Jones proof/diet loop, 2026 agent-harness
          field practice. Not a build. Map before mint.
        </Text>
      </Stack>

      <Callout tone="warning" title="Decision rule (written first)">
        If adding script X means the next cold agent on another device can refuse a false
        done or skip a 400-line skill, mint X. If both branches are “the model tries harder,”
        do not mint. Same-model critique is not a detector. Nightly must not invent skills.
      </Callout>

      <Grid columns={4} gap={12}>
        <Stat value="22" label="Portable scripts in 09-tools" />
        <Stat value="5" label="GitHub CI workflows" tone="success" />
        <Stat value="33 / 47" label="Hubs with no governed_by" tone="warning" />
        <Stat value="130 / 185" label="Spokes with empty triggers" />
      </Grid>

      <H2>Producer hubs vs judge attach</H2>
      <BarChart
        categories={["Has governed_by", "No governed_by"]}
        series={[{ name: "Hubs", data: [14, 33], tone: "warning" }]}
        height={180}
        showValues
      />
      <Text tone="tertiary" size="small">
        Source: 03-skills/skills.registry.json · 2026-09-11. Count of hub-tier skills.
        governed_by is navigational unless a script or hook loads it after produce.
      </Text>

      <Row gap={8} wrap>
        {FILTERS.map((f) => (
          <span key={f.id}>
            <Pill
              active={filter === f.id}
              tone={toneFor(f.id)}
              onClick={() => setFilter(f.id)}
            >
              {f.label}
            </Pill>
          </span>
        ))}
      </Row>

      {(filter === "all" || filter === "keep") && (
        <Stack gap={8}>
          <H2>Already a steel curtain — keep</H2>
          <Text tone="secondary">
            Do not rebuild these as new skills. Wire more work into them.
          </Text>
          <Table
            headers={["Job", "Machinery", "What it refuses", ""]}
            rows={existingRows}
            striped
            stickyHeader
          />
        </Stack>
      )}

      {(filter === "all" || filter === "mint") && (
        <Stack gap={8}>
          <H2>Mint if you approve the number</H2>
          <Text tone="secondary">
            Smallest stdlib script that changes what the next agent can prove. Not a new hub.
          </Text>
          <Table
            headers={["#", "Script", "Change", "Token / accuracy effect", ""]}
            rows={mintRows}
            striped
            stickyHeader
          />
        </Stack>
      )}

      {(filter === "all" || filter === "refuse") && (
        <Stack gap={8}>
          <H2>Do not automate</H2>
          <Table
            headers={["#", "Anti-pattern", "Why it fails validity", ""]}
            rows={refuseRows}
            striped
          />
        </Stack>
      )}

      <Divider />

      <Grid columns={2} gap={16}>
        <Card>
          <CardHeader>What synthesis already said</CardHeader>
          <CardBody>
            <Stack gap={8}>
              <Text>
                Frost: generation is cheap; “is it good?” is CI, axe, evals — not LLM-as-judge.
              </Text>
              <Text>
                #13: every domain needs L3 measurement. Missing L3 is a defect, not a style choice.
              </Text>
              <Text>
                #06 + close-out: capture → assess → correct. Mint the detector if it is missing.
              </Text>
              <Text>
                Validity baseline: write the decision rule before looking. Peeking is not evidence.
              </Text>
              <Text>
                Nate Jones: proof and diet are two of seven maintenance surfaces. Preload catalogs
                are drag.
              </Text>
            </Stack>
          </CardBody>
        </Card>
        <Card>
          <CardHeader>What 2026 field practice adds</CardHeader>
          <CardBody>
            <Stack gap={8}>
              <Text>
                Rule-based floor first (tests, linters, schema, ast-grep). LLM judge only after
                the floor, and never as the merge gate.
              </Text>
              <Text>
                Agent harness: init / test-all / review scripts. The agent never self-certifies.
              </Text>
              <Text>
                Trajectory quality (tool sequence) is a better regression signal than golden prose.
                We already have this shape in evaluate-skill-routing.py — extend it, don’t replace
                it with promptfoo.
              </Text>
              <Text>
                Secret scan + SAST on the automation layer. Product-repo eslint-off-system already
                covers off-system CSS; do not duplicate it in the vault.
              </Text>
            </Stack>
          </CardBody>
        </Card>
      </Grid>

      <Callout tone="info" title="Recommended first wave if you approve">
        A1 skill-loadset · A2 hub L3 coverage · A3 close-out dispatch · A6 secret scan · A7
        Layer 0 JSON schema. A8 Figma bind probe only when the next Figma produce cannot refuse
        Color/*. A4 nightly.sh without enabling cron. Skip A10 as GitHub CI theater.
      </Callout>
    </Stack>
  );
}
