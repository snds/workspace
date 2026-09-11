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
  useCanvasState,
} from "cursor/canvas";

type FilterId = "all" | "miss" | "tax" | "dup" | "access" | "recs";

const FILTERS: { id: FilterId; label: string }[] = [
  { id: "all", label: "All" },
  { id: "miss", label: "Miss" },
  { id: "tax", label: "Token tax" },
  { id: "dup", label: "Duplicate home" },
  { id: "access", label: "Inaccessible" },
  { id: "recs", label: "Recs 1–15" },
];

const MISS_ROWS: [string, string, string, string][] = [
  [
    "Silent hubs",
    "34 / 47 hubs have empty triggers (qa, ds, motion, lead-ui/ux, ds-generation-pipeline)",
    "Layer 0 never loads them. AGENTS description-fallback is unimplemented.",
    "VERIFIED",
  ],
  [
    "Framework #18 Frost DS×AI",
    "Curated Frost phrases only; absent from AGENTS doctrine list",
    "Hookless agent never opens mortar / steel curtain / context-based DS.",
    "VERIFIED",
  ],
  [
    "Memory",
    "22 files, zero Layer-0 keys",
    "Decisions stay dark unless the agent follows read-order step 9.",
    "VERIFIED",
  ],
  [
    "Knowledge hints",
    "12 unique files vs ~75 notes",
    "INDEX-only doctrine (contracts, SaaS patterns, threat-model) needs a cap-4 survivor.",
    "VERIFIED",
  ],
  [
    "Generate-a-DS ban",
    "ds-generation-pipeline has no triggers",
    "“Generate a design system” loads advisor+#18, not the pipeline ban, unless #18 is read.",
    "VERIFIED",
  ],
  [
    "QA / visual-qa attach",
    "audit/review → framework #06 only",
    "/qa and visual-qa-toolkit never attach after a DS or Figma run.",
    "VERIFIED",
  ],
];

const TAX_ROWS: [string, string, string][] = [
  [
    "AGENTS steps 3–5 if obeyed",
    "~70k tokens",
    "Whole registry + trigger-routes.md + _INDEX. Hooks use JSON + caps instead.",
  ],
  [
    "Phrase “design system”",
    "~2,300 lines",
    "#18 + #09 (717) + ds-advisor (887) + design-engineer.",
  ],
  [
    "“audit this design system component”",
    "~3,800 lines",
    "QA #06 + DS stack + entire FIGMA_GENERATE_ROUTE. Wrong process for an audit.",
  ],
  [
    "Claude SessionStart _INDEX head-60",
    "~5k tokens",
    "Recurring Claude-only tax. First 60 lines are the densest Design blurbs.",
  ],
  [
    "Cursor Brain-first + native AGENTS",
    "~7.5k tokens",
    "Two alwaysApply mdc files + AGENTS. This chat’s root is ~/Projects so mdc does not attach.",
  ],
];

const DUP_ROWS: [string, string, string][] = [
  [
    "Frost mortar / stool / steel curtain",
    "#18 (canonical) · ds-advisor preamble · ai-design-systems · knowledge note",
    "Skill-first agents can skip #18 and still think they loaded canon.",
  ],
  [
    "Component contracts",
    "#09 §5a · component-contracts-and-schemas · component-contract-schema.md",
    "Three full restatements. Constrained agents pick one and miss the others’ corrections.",
  ],
  [
    "Figma authority",
    "ds-advisor: “Figma is the knowledge center.” #09/contracts: “Figma is a signatory.”",
    "Weaker rule wins if ds-advisor loads and contracts do not.",
  ],
  [
    "Write-quality gates",
    "AGENTS + 01-agent-controller.mdc",
    "Same law, two always-on homes.",
  ],
];

const ACCESS_ROWS: [string, string, string][] = [
  [
    "prompt_route.py",
    "Not in 09-tools gitignore allowlist",
    "GitHub clone cannot run Layer 0.",
  ],
  [
    "Cursor beforeSubmitPrompt",
    "User-global; Work MBP + Windows pending",
    "Employer-repo Cursor chats are beacon-only until the hook is installed.",
  ],
  [
    "Perplexity / GPT.com / Grok.com",
    "No hooks, no mdc, no CLAUDE.md",
    "Adapter must be the whole contract. PERPLEXITY.md currently forks it.",
  ],
  [
    "Most 07-projects SESSION-STATE",
    "Gitignore allowlist: 00, 18, 19, 20, 21-shadegraph, 22-course only",
    "Centric / Legion / CDS audit Live handoffs are machine-local. Intentional.",
  ],
  [
    "This chat’s Cursor rules",
    "Root is ~/Projects, not Brain-first",
    "brain.mdc does not attach. Plan-ahead in mdc is easy to skip.",
  ],
];

const RECS: {
  n: string;
  disp: string;
  owner: string;
  change: string;
  skip: string;
}[] = [
  {
    n: "1",
    disp: "Load later",
    owner: "AGENTS.md read order",
    change: "Lookup load_chains[name]. Read trigger-routes.json, not the generated .md. Match INDEX Triggers without ingesting 8k tokens.",
    skip: "Obedient agents burn ~70k before work.",
  },
  {
    n: "2",
    disp: "Turn into check",
    owner: ".gitignore + 09-tools/",
    change: "Allowlist prompt_route.py and cursor-prompt-route.py.",
    skip: "Remote clones have no matcher.",
  },
  {
    n: "3",
    disp: "Turn into check",
    owner: "Hub SKILL.md triggers",
    change: "Give /qa /ds /motion lead-ui/ux/fe real triggers — or delete AGENTS’ description-fallback sentence.",
    skip: "“qa this screen” never loads /qa.",
  },
  {
    n: "4",
    disp: "One home",
    owner: "trigger-routes.json",
    change: "Stop aliasing component/variant/mockup/wireframe to FIGMA_GENERATE_ROUTE.",
    skip: "Audits pull the generate stack; cap-8 drops #18.",
  },
  {
    n: "5",
    disp: "Load later",
    owner: "“design system” route",
    change: "Default pair = #18 + ds-advisor. Load #09 only on schema / Atomic Design keys.",
    skip: "Two words cost ~2,300 lines.",
  },
  {
    n: "6",
    disp: "Keep",
    owner: "AGENTS doctrine list",
    change: "One phrase: #18 DS×AI next to #17 intent. Do not paste Frost models into the contract.",
    skip: "Hookless agents never hear that Frost is L1.",
  },
  {
    n: "7",
    disp: "One home",
    owner: "CRITICAL_FACTS, _HOME, framework-check",
    change: "seventeen → eighteen. #17 stays intent; #18 is Frost.",
    skip: "Stale count trains agents to stop at 17.",
  },
  {
    n: "8",
    disp: "Load later",
    owner: "knowledge-hints.json",
    change: "Hint contracts, SaaS patterns, contracts-first, a11y-beyond-WCAG, threat-model, visual-failure-mode-ledger.",
    skip: "Doctrine stays dark unless INDEX is ingested.",
  },
  {
    n: "9",
    disp: "Turn into check",
    owner: "figma hub",
    change: "defers_to design-engineer; plugin figma-use is L5 mechanics.",
    skip: "Vendor skill wins on Cursor.",
  },
  {
    n: "10",
    disp: "One home",
    owner: "PERPLEXITY.md",
    change: "Thin adapter. Same read order as AGENTS. No session-log-append fork.",
    skip: "Perplexity runs a different workspace.",
  },
  {
    n: "11",
    disp: "Keep",
    owner: "Untracked knowledge/memory",
    change: "INDEX + MEMORY lines in the same commit as the files. Do not hint GitHub-missing paths.",
    skip: "Layer 0 404s on other machines.",
  },
  {
    n: "12",
    disp: "Probation",
    owner: "ds-advisor principle 5",
    change: "Reconcile “Figma is the knowledge center” with contracts (“signatory”). Pointer, not an essay.",
    skip: "Skill-first agents ship the weaker rule.",
  },
  {
    n: "13",
    disp: "Turn into check",
    owner: "workspace-doctor",
    change: "Install Cursor beforeSubmitPrompt on this Work MBP and Windows.",
    skip: "Employer-repo Cursor chats stay beacon-only.",
  },
  {
    n: "14",
    disp: "Keep",
    owner: "Contribution / plan-ahead",
    change: "Fetch before claiming the next framework or project integer.",
    skip: "This merge had to move Frost #17→#18 and course 21→22.",
  },
  {
    n: "15",
    disp: "Probation",
    owner: "Claude SessionStart",
    change: "Trim or stop injecting _INDEX head-60 (~5k tokens).",
    skip: "Recurring Claude-only tax AGENTS does not mention.",
  },
];

export default function AgentLoadMissReview() {
  const [filter, setFilter] = useCanvasState<FilterId>("filter", "all");

  const showMiss = filter === "all" || filter === "miss";
  const showTax = filter === "all" || filter === "tax";
  const showDup = filter === "all" || filter === "dup";
  const showAccess = filter === "all" || filter === "access";
  const showRecs = filter === "all" || filter === "recs";

  return (
    <Stack gap={24}>
      <Stack gap={8}>
        <H1>Agent load-miss review</H1>
        <Text tone="secondary">
          Workspace core + Cursor · main@1f87419 · 2026-09-11 · map-only. Target
          user: any cold LLM. Bar: important process is findable at acceptable
          token cost.
        </Text>
      </Stack>

      <Callout tone="warning" title="Map before clean">
        Nothing in always-on files was rewritten. Approve recs by number. Sean
        is running the same pass on other models — treat disagreements as
        signal, not a race to patch.
      </Callout>

      <Grid columns={4} gap={16}>
        <Stat value="34 / 47" label="Hubs with empty triggers" tone="danger" />
        <Stat value="12 / 75" label="Knowledge files with hints" tone="warning" />
        <Stat value="~70k" label="AGENTS steps 3–5 if obeyed" tone="warning" />
        <Stat value="15" label="Recs waiting on approval" />
      </Grid>

      <Row gap={8} wrap>
        {FILTERS.map((item) => (
          <span key={item.id}>
            <Pill
              active={filter === item.id}
              onClick={() => setFilter(item.id)}
            >
              {item.label}
            </Pill>
          </span>
        ))}
      </Row>

      <H2>What a cold agent actually gets</H2>
      <Text>
        Layer 0 is a hook plus a hope. The hook is Claude-project-local or
        Cursor-user-global and fail-open. The hope is that the model reads a 6k
        contract and then does not ingest a 55k registry. Framework #18, most of
        #01–#16, memory, and most knowledge are on-demand with no always-on
        pointer.
      </Text>

      <Grid columns={2} gap={16}>
        <Card>
          <CardHeader trailing="Protects">Portable core</CardHeader>
          <CardBody>
            <Text>
              AGENTS as the contract, context-profile fail-safe, write-quality
              validators, curated QA / Frost / plan-ahead / a11y keys, #18 as a
              real L1 instead of stuffing Frost into ds-advisor, gitignore that
              keeps employer substance off GitHub.
            </Text>
          </CardBody>
        </Card>
        <Card>
          <CardHeader trailing="Drag">Where agents fail</CardHeader>
          <CardBody>
            <Text>
              Read-order vs token diet. Silent hubs. component = Figma generate.
              Three contract copies. ds-advisor restates #18. PERPLEXITY.md
              still forks. Stale “seventeen” after #18 landed.
            </Text>
          </CardBody>
        </Card>
      </Grid>

      {showMiss ? (
        <Stack gap={12}>
          <H2>Miss — never loaded unless named</H2>
          <Table
            headers={["Cluster", "Evidence", "What the agent skips", "Grade"]}
            rows={MISS_ROWS}
            rowTone={MISS_ROWS.map(() => "danger" as const)}
            striped
            stickyHeader
          />
        </Stack>
      ) : null}

      {showTax ? (
        <Stack gap={12}>
          <H2>Token tax — loaded too soon or too much</H2>
          <Table
            headers={["Load", "Cost", "Why it is a tax"]}
            rows={TAX_ROWS}
            rowTone={TAX_ROWS.map(() => "warning" as const)}
            striped
          />
        </Stack>
      ) : null}

      {showDup ? (
        <Stack gap={12}>
          <H2>Duplicate home — same law, several owners</H2>
          <Table
            headers={["Law", "Homes", "Failure"]}
            rows={DUP_ROWS}
            striped
          />
        </Stack>
      ) : null}

      {showAccess ? (
        <Stack gap={12}>
          <H2>Inaccessible on some surfaces</H2>
          <Table
            headers={["Asset", "Why", "Who misses it"]}
            rows={ACCESS_ROWS}
            striped
          />
        </Stack>
      ) : null}

      {showRecs ? (
        <Stack gap={12}>
          <H2>Numbered recs — approve by number</H2>
          <Text tone="secondary">
            Disposition vocabulary: Keep · One home · Load later · Turn into
            check · Probation · Retire. Length is not a disposition — do not
            delete ds-advisor because it is 887 lines.
          </Text>
          <Table
            headers={["#", "Disposition", "Owner", "Change", "If skipped"]}
            rows={RECS.map((rec) => [
              rec.n,
              rec.disp,
              rec.owner,
              rec.change,
              rec.skip,
            ])}
            columnAlign={["right", "left", "left", "left", "left"]}
            striped
            stickyHeader
          />
        </Stack>
      ) : null}

      <Divider />

      <H3>This merge (already on origin/main)</H3>
      <Text>
        Origin was 44 commits ahead. Rebase kept Intent Coordination as
        framework #17 and ShadeGraph as project 21. Frost DS×AI is now #18.
        Course notes are 22-ai-design-systems-course. Fetch before claiming the
        next integer (rec 14).
      </Text>
      <Text tone="secondary" size="small">
        Durable twins: 08-knowledge/cross-domain/agent-load-miss-review.md ·
        07-projects/19-workspace-brain/reports/harness-map_v2.0_2026-09-11.md ·
        Source: disk inventory 2026-09-11, not a runtime load log (Cursor run
        maps are NOT_EXPOSED).
      </Text>
    </Stack>
  );
}
