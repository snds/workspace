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
  H3,
  Pill,
  Row,
  Stack,
  Stat,
  Table,
  Text,
  useCanvasState,
} from "cursor/canvas";

type FilterId = "all" | "attach" | "intent" | "clusters" | "recs";

const FILTERS: { id: FilterId; label: string }[] = [
  { id: "all", label: "All" },
  { id: "attach", label: "Attach miss" },
  { id: "intent", label: "Context / intent" },
  { id: "clusters", label: "Clusters" },
  { id: "recs", label: "Recs R1–R16" },
];

const HUB_DOMAINS = [
  "Design",
  "Eng",
  "Game",
  "Quality",
  "A11y",
  "Data",
  "Product",
  "Career",
  "Security",
];

const SILENT_HUBS = [23, 4, 2, 2, 1, 1, 1, 0, 0];
const TRIGGERED_HUBS = [5, 4, 2, 0, 0, 0, 0, 1, 1];

const ATTACH_ROWS: [string, string, string, string][] = [
  [
    "Judge hubs are dark",
    "`qa` and `lead-visual-qa` have no triggers key on disk",
    "Nothing can police a producer if the judge cannot be found.",
    "VERIFIED",
  ],
  [
    "Graph does not attach",
    "`governed_by` on 8/297 skills; `governs` is 0 everywhere",
    "`prompt_route.py` never loads related/governed_by after output.",
    "VERIFIED",
  ],
  [
    "Command wrappers except `/eng`",
    "`/qa` `/ds` `/figma` `/motion` `/type` `/redesign` — empty triggers",
    "The surfaces that should self-police are Layer-0 invisible.",
    "VERIFIED",
  ],
  [
    "Committed `/figma` vs local WIP",
    "HEAD: no triggers; prose still says load vendor `figma-use` first",
    "GitHub-only agents get the weaker hub. Local WIP reversed it — uncommitted.",
    "VERIFIED",
  ],
  [
    "UX hub is a roast button",
    "`lead-ux-designer` triggers: `challenge this`, `tear this apart`",
    "IA / enterprise UX / “how should this work” never Layer-0 loads.",
    "VERIFIED",
  ],
  [
    "plan-ahead is cds/proto-shaped",
    "Triggers are dual-repo / Pages phrases, not implement / PR / CI",
    "Generic coded work skips the order-of-operations print.",
    "VERIFIED",
  ],
];

const INTENT_ROWS: [string, string, string][] = [
  [
    "Who owns / who reviews?",
    "`00-context-profiles.md` — AGENTS says resolve first",
    "Layer 0 only on the exact phrase `context profile`.",
  ],
  [
    "Who is the target user of this output?",
    "#06 originating lens",
    "`audit`/`review` loads the framework file, not `/qa`. Other prompts skip it.",
  ],
  [
    "CREATE vs JUDGE?",
    "`/figma` `/ds` `/redesign` `/eng` vs `/qa`",
    "CREATE hubs have empty `governed_by`. Redesign can ship without QA.",
  ],
  [
    "What does done mean?",
    "Proofboard · mission-fit · #06 · #14 verify · #11 · plan-ahead",
    "Six languages, no invoke. Toolkit will not hunt screenshots.",
  ],
  [
    "Who owns the claim?",
    "#15 analysis frame",
    "`lead-data-scientist` and `lead-product-manager` are silent.",
  ],
  [
    "Trust boundary?",
    "#16 threat-model",
    "Security hair-triggers on the word; FE/DS generate does not attach it.",
  ],
];

const CLUSTER_ROWS: [string, string, string, string][] = [
  ["UI / UX / DS", "#02 #09 #18", "`ds-advisor` yes; `/ds` `/qa` silent", "No close-out"],
  [
    "Figma",
    "14 construction rules + token hard-gate prose",
    "No bind/instance machine check; protocol has no VQA stop",
    "Advice",
  ],
  [
    "Engineering",
    "#14 `/eng` #07",
    "lead-fe/be/devops silent; Proofboard not a ship verb",
    "Local green",
  ],
  ["Integration", "#07 stacking", "No Layer-0 key for PR / merge / rebase", "Prose"],
  ["QA / visual", "#06 #10 toolkit prove-engine", "Judge hubs silent", "Manners"],
  ["Motion / type / graphic", "#02 wrappers", "`/qa --lens` never loads", "Unattached"],
  ["Accessibility", "toolkit + lead", "Silent hub; not sideways on generate", "Opt-in"],
  ["Security", "#16 + triggered hub", "Only 3 spokes `governed_by` sec-*", "Sideways miss"],
  ["Analysis / PM", "#15", "Both leads silent", "Narrative risk"],
  [
    "Photoreal / game",
    "#12 + realtime-visual-craft",
    "Best instantiated cluster — attach template, not a GPU clone",
    "Keep",
  ],
  ["Intent / swarm", "#17 + intent-run.py", "Not used for ordinary single-agent work", "Keep off"],
  ["Workspace writes", "#08 validators", "Do not close out product/Figma/code in other repos", "This-repo only"],
  ["Career / Adobe / Vision / Science", "thin L1 allowed", "Checklists — honest INCOMPLETE", "Do not fake L3"],
];

const RECS: {
  n: string;
  disp: string;
  owner: string;
  change: string;
  skip: string;
}[] = [
  {
    n: "R1",
    disp: "One home",
    owner: "new close-out skill",
    change:
      "Self-test → self-validate (named detector) → self-confirm (#06) → human visual or Proofboard stop. Hubs invoke it; do not paste into 47 files.",
    skip: "Agents keep freestyling “looks good.”",
  },
  {
    n: "R2",
    disp: "Turn into check",
    owner: "build-registry / integrity",
    change:
      "Fail when a hub or foundation has empty triggers. Quote multi-word YAML trigger phrases.",
    skip: "Wrappers stay description-only; bad flow lists get zeroed.",
  },
  {
    n: "R3",
    disp: "Turn into check",
    owner: "command wrappers",
    change:
      "Real triggers on /qa /ds /figma /motion /type /redesign. /figma defers_to design-engineer; stop loading figma-use first.",
    skip: "Vendor mechanics win; judge hubs stay dark.",
  },
  {
    n: "R4",
    disp: "Turn into check",
    owner: "producer hubs",
    change:
      "governed_by: [qa] (visual) or eng/mission-fit (code). Registry must treat it as post-output load.",
    skip: "Graph remains a wiki.",
  },
  {
    n: "R5",
    disp: "Load later",
    owner: "plan-ahead",
    change:
      "Generalize past cds/proto: fetch, CI-contract vs overlay, merge-conflict files, generated artifacts, first later-breaker.",
    skip: "Local green, Pages/GHA red; rebase collisions.",
  },
  {
    n: "R6",
    disp: "One home",
    owner: "/eng ship",
    change: "Ship names or builds the Proofboard. Playbook stays canonical.",
    skip: "Sean still has to read code to believe done.",
  },
  {
    n: "R7",
    disp: "Turn into check",
    owner: "Figma prove-gate",
    change:
      "Refuse Color/* on components; instances not rects; variant matrix; native-zoom screenshot; stop for Sean.",
    skip: "Construction rules remain advice.",
  },
  {
    n: "R8",
    disp: "Load later",
    owner: "trigger-routes.json",
    change: "PR / pull request / rebase / stack these diffs → #07. Do not also dump #09.",
    skip: "Reviewability never loads at PR time.",
  },
  {
    n: "R9",
    disp: "Keep",
    owner: "lead-ux-designer",
    change: "Add the UX work the description already claims — or the hub stays a roast button.",
    skip: "UX depth never Layer-0 loads.",
  },
  {
    n: "R10",
    disp: "Load later",
    owner: "analysis / PM",
    change:
      "Triggers on both leads for “what does the data say” / experiment / decision owner. Close-out = #15 + Proofboard.",
    skip: "Narrative theater ships.",
  },
  {
    n: "R11",
    disp: "Turn into check",
    owner: "a11y sideways",
    change:
      "Figma generate + UI code close-out loads a11y-visual (contrast/CVD) before the human stop.",
    skip: "Inaccessible UI reaches Sean first.",
  },
  {
    n: "R12",
    disp: "Probation",
    owner: "security sideways",
    change:
      "Don’t hair-trigger the whole security hub on the word. governed_by on boundary-crossing eng spokes.",
    skip: "Either miss or token bomb.",
  },
  {
    n: "R13",
    disp: "Load later",
    owner: "context profile",
    change:
      "Repo actions resolve 00-context-profiles.md without requiring the user to say “context profile.” One sentence in close-out / plan-ahead.",
    skip: "Employer-repo self-merge risk.",
  },
  {
    n: "R14",
    disp: "Keep",
    owner: "photoreal cluster",
    change: "Do not clone GPU toolkits. Use it as the attach template for R1.",
    skip: "Fake L3 / token waste.",
  },
  {
    n: "R15",
    disp: "Probation",
    owner: "Intent #17",
    change: "Keep off ordinary single-agent work if R1 + R5 exist. Revisit if false done persists.",
    skip: "Always-on living-spec tax.",
  },
  {
    n: "R16",
    disp: "One home",
    owner: "close-out languages",
    change:
      "After R1: #06, mission-fit, Proofboard, #14 verify, #11, plan-ahead become invoke targets — pointer, not restatement.",
    skip: "Six done definitions, none fire.",
  },
];

export default function ProcessRigorGaps() {
  const [filter, setFilter] = useCanvasState<FilterId>("filter", "all");

  const showAttach = filter === "all" || filter === "attach";
  const showIntent = filter === "all" || filter === "intent";
  const showClusters = filter === "all" || filter === "clusters";
  const showRecs = filter === "all" || filter === "recs";

  return (
    <Stack gap={24}>
      <Stack gap={8}>
        <H1>Process rigor gaps</H1>
        <Text tone="secondary">
          Whole workspace · main@40d9f8e · 2026-09-11 · map-only. Target user:
          Sean as designer-of-designers, plus any cold LLM. Bar: the agent
          self-polices; Sean’s last act is visual or Proofboard confirmation.
        </Text>
      </Stack>

      <Callout tone="warning" title="Doctrine exists. It does not attach.">
        Coded order-of-operations, Figma construction, and hub self-test plus
        human visual QA are instances. The same miss hits analysis, a11y,
        motion, type, security-as-sideways, context profile, Proofboard, and
        #07 reviewability. Recs R1–R16 wait on approval. Load-miss recs 1–15
        stay open and are not replaced.
      </Callout>

      <Grid columns={4} gap={16}>
        <Stat value="34 / 47" label="Hubs with empty triggers" tone="danger" />
        <Stat value="8 / 297" label="Skills with governed_by" tone="warning" />
        <Stat value="0" label="Skills with governs" tone="danger" />
        <Stat value="16" label="R-series recs waiting" />
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

      {showAttach ? (
        <Stack gap={12}>
          <H2>Silent vs triggered hubs by domain</H2>
          <Text tone="secondary">
            Hub count · Source: skills.registry.json 2026-09-11. Quality, a11y,
            data, and product — the judge and decision domains — are entirely
            silent. Security and career are the exceptions that already have
            triggers.
          </Text>
          <BarChart
            categories={HUB_DOMAINS}
            series={[
              { name: "Silent (no triggers)", data: SILENT_HUBS, tone: "danger" },
              {
                name: "Triggered (Layer-0 findable)",
                data: TRIGGERED_HUBS,
                tone: "success",
              },
            ]}
            stacked
            height={240}
            showValues
          />

          <H2>Attach miss — process that cannot run</H2>
          <Table
            headers={["Gap", "Evidence", "What fails", "Grade"]}
            rows={ATTACH_ROWS}
            rowTone={ATTACH_ROWS.map(() => "danger" as const)}
            striped
            stickyHeader
          />
        </Stack>
      ) : null}

      {showIntent ? (
        <Stack gap={12}>
          <H2>Context and intent — skipped on ordinary work</H2>
          <Text>
            AGENTS already says resolve the context profile before a repo
            action, and #06 already says name the target user before producing.
            Neither fires unless the user types a curated phrase. That is an
            intent miss, not a missing essay.
          </Text>
          <Table
            headers={["Intent question", "Home", "What actually happens"]}
            rows={INTENT_ROWS}
            striped
            stickyHeader
          />
        </Stack>
      ) : null}

      {showClusters ? (
        <Stack gap={16}>
          <H2>Every cluster against the same bar</H2>
          <Grid columns={2} gap={16}>
            <Card>
              <CardHeader trailing="Keep">Already protects</CardHeader>
              <CardBody>
                <Text>
                  #06–#18, Proofboard, plan-ahead (cds/proto), #11 premortem,
                  /eng as a real L2, photoreal’s named done-gate, workspace
                  validators. Do not write a second copy of any of these.
                </Text>
              </CardBody>
            </Card>
            <Card>
              <CardHeader trailing="One home">Four protocols to add</CardHeader>
              <CardBody>
                <Text>
                  Close-out (R1). Generalized plan-ahead (R5). Figma prove-gate
                  (R7). Graph attach so QA/a11y actually load after produce
                  (R4). Pointers from wrappers — not 40 lines times 47 hubs.
                </Text>
              </CardBody>
            </Card>
          </Grid>
          <Table
            headers={["Cluster", "What exists", "What’s missing", "Today"]}
            rows={CLUSTER_ROWS}
            striped
            stickyHeader
          />
        </Stack>
      ) : null}

      {showRecs ? (
        <Stack gap={12}>
          <H2>Numbered recs — approve by number</H2>
          <Text tone="secondary">
            Complementary to load-miss 1–15 (especially silent hubs, component
            route, figma defers_to). Disposition: Keep · One home · Load later ·
            Turn into check · Probation. Invalid: cargo-cult visual-qa-toolkit
            onto security or career.
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

      <H3>How this relates to the load-miss map</H3>
      <Text>
        Load-miss asked: does the agent ever open the file? This map asks: if it
        did, would the work still skip order-of-operations, construction
        proof, a judge, a named detector, and a human stop? Fixing triggers
        without R1 still ships “looks good.” Shipping R1 without triggers still
        never loads the judge.
      </Text>
      <Text tone="secondary" size="small">
        Durable twins: 08-knowledge/cross-domain/process-rigor-gaps.md ·
        07-projects/19-workspace-brain/reports/process-rigor-gaps_v1.0_2026-09-11.md
        · Companion: harness-map_v2.0_2026-09-11.md. Registry snapshot 297
        skills / 47 hubs.
      </Text>
    </Stack>
  );
}
