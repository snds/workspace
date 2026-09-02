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
  Stack,
  Stat,
  Table,
  Text,
} from "cursor/canvas";

const RUN_ID = "20260816T214110-ab8d81";
const RECLAIM_GIB = 917.4;

const TOP_RECLAIM = [
  { show: "Full Metal Panic!", type: "TV", groups: 66, dups: 25, cuts: 25, review: 0, gib: 115.5 },
  { show: "Babylon 5", type: "TV", groups: 110, dups: 109, cuts: 107, review: 0, gib: 81.8 },
  { show: "The Great British Bake Off", type: "TV", groups: 200, dups: 126, cuts: 126, review: 0, gib: 77.1 },
  { show: "Diners, Drive-ins and Dives", type: "TV", groups: 784, dups: 289, cuts: 287, review: 2, gib: 76.3 },
  { show: "Frasier", type: "TV", groups: 264, dups: 74, cuts: 74, review: 0, gib: 74.4 },
  { show: "Hercules - The Legendary Journeys", type: "TV", groups: 123, dups: 68, cuts: 68, review: 0, gib: 50.5 },
  { show: "CSI - Crime Scene Investigation", type: "TV", groups: 446, dups: 72, cuts: 72, review: 0, gib: 46.5 },
  { show: "The Orville (2017)", type: "TV", groups: 30, dups: 22, cuts: 22, review: 0, gib: 44.2 },
  { show: "Red Dwarf (1988)", type: "TV", groups: 71, dups: 47, cuts: 47, review: 0, gib: 26.5 },
  { show: "The Sandman", type: "TV", groups: 23, dups: 11, cuts: 11, review: 0, gib: 25.6 },
  { show: "Good Eats", type: "TV", groups: 339, dups: 172, cuts: 145, review: 27, gib: 24.9 },
  { show: "Home Improvement", type: "TV", groups: 203, dups: 200, cuts: 200, review: 0, gib: 24.1 },
  { show: "Grand Designs", type: "TV", groups: 253, dups: 82, cuts: 81, review: 1, gib: 22.4 },
  { show: "Giada at Home", type: "TV", groups: 186, dups: 161, cuts: 117, review: 44, gib: 21.5 },
  { show: "Animaniacs", type: "TV", groups: 362, dups: 212, cuts: 207, review: 0, gib: 17.2 },
];

const TOP_MISSING = [
  ["Looney Tunes (1929)", "TV", "900", "1,871"],
  ["Looney Tunes", "TV", "473", "1,048"],
  ["The Big Bang Theory (2007)", "TV", "255", "279"],
  ["Pokémon (1997)", "TV", "229", "402"],
  ["Supernatural", "TV", "202", "327"],
  ["Whose Line Is It Anyway! (US)", "TV", "186", "432"],
  ["Stargate SG-1", "TV", "168", "213"],
  ["The Bullwinkle Show (1959)", "TV", "154", "157"],
  ["NCIS (2003)", "TV", "138", "507"],
  ["Fringe", "TV", "112", "113"],
];

const REVIEW_SHOWS = [
  ["Giada at Home", "44", "161", "21.5"],
  ["Giada Entertains", "30", "49", "3.2"],
  ["Good Eats", "27", "172", "24.9"],
  ["Sabrina, The Teenage Witch (1996)", "14", "138", "9.1"],
  ["Giada in Italy", "8", "32", "4.7"],
  ["Barefoot Contessa", "7", "47", "10.4"],
];

export default function DuplicateScanOutcome() {
  return (
    <Stack gap={24}>
      <Stack gap={6}>
        <H1>Duplicate scan outcome</H1>
        <Text tone="secondary">
          MediaSentinel run `{RUN_ID}` · 16 Aug 2026 21:41 UTC · profile
          “English watchable, fidelity then size” · TV + movies · ranking
          only, nothing quarantined
        </Text>
      </Stack>

      <Callout tone="info" title="Proposal, not a cleanup">
        The engine ranked keepers vs extras. No files were moved or deleted.
        142 groups still need a human look before any cut. Keepers missing
        English text subs were not queued in Bazarr.
      </Callout>

      <Grid columns={5} gap={16}>
        <Stat value="33,313" label="Files scanned" />
        <Stat value="2,510" label="Duplicate groups" />
        <Stat value="2,327" label="Proposed cuts" />
        <Stat value={`${RECLAIM_GIB} GiB`} label="Reclaimable if cuts applied" tone="success" />
        <Stat value="142" label="Groups in review" tone="warning" />
      </Grid>

      <Grid columns={2} gap={16}>
        <Card>
          <CardHeader>TV</CardHeader>
          <CardBody>
            <Stack gap={8}>
              <Text>32,235 files · 335 shows · 29,721 groups</Text>
              <Text>
                2,510 duplicate groups · 2,327 proposed cuts · {RECLAIM_GIB} GiB
                reclaimable
              </Text>
              <Text>5,328 keepers missing text subs · 142 groups in review</Text>
            </Stack>
          </CardBody>
        </Card>
        <Card>
          <CardHeader>Movies</CardHeader>
          <CardBody>
            <Stack gap={8}>
              <Text>1,078 files · 1,076 titles · 1,080 groups</Text>
              <Text>0 duplicate groups · 0 proposed cuts · 0 GiB reclaimable</Text>
              <Text>595 titles missing text subs (almost one each)</Text>
            </Stack>
          </CardBody>
        </Card>
      </Grid>

      <Stack gap={8}>
        <H2>Reclaimable space by show (GiB)</H2>
        <Text tone="secondary" size="small">
          Top 12 TV shows by CUT-member size that would actually free space.
          Movies contribute 0. Source: MediaSentinel library tree for run
          {` ${RUN_ID}`}
        </Text>
        <BarChart
          horizontal
          height={360}
          categories={[
            "Full Metal Panic!",
            "Babylon 5",
            "GBBO",
            "Diners, Drive-ins",
            "Frasier",
            "Hercules",
            "CSI",
            "The Orville (2017)",
            "Red Dwarf",
            "The Sandman",
            "Good Eats",
            "Home Improvement",
          ]}
          series={[
            {
              name: "Reclaimable (GiB)",
              data: [115.5, 81.8, 77.1, 76.3, 74.4, 50.5, 46.5, 44.2, 26.5, 25.6, 24.9, 24.1],
              tone: "info",
            },
          ]}
          valueSuffix=" GiB"
          showValues
        />
      </Stack>

      <Stack gap={8}>
        <H2>Largest duplicate clusters</H2>
        <Text tone="secondary" size="small">
          CUT bytes only. Review groups are ranked but not auto-cut.
        </Text>
        <Table
          headers={["Show", "Dup groups", "Cuts", "Review", "Reclaimable"]}
          columnAlign={["left", "right", "right", "right", "right"]}
          striped
          stickyHeader
          rows={TOP_RECLAIM.map((r) => [
            r.show,
            String(r.dups),
            String(r.cuts),
            String(r.review),
            `${r.gib} GiB`,
          ])}
          rowTone={TOP_RECLAIM.map((r) => (r.review > 0 ? "warning" : undefined))}
        />
      </Stack>

      <Divider />

      <Grid columns={2} gap={24}>
        <Stack gap={8}>
          <H2>Keepers missing text subs</H2>
          <Text tone="secondary" size="small">
            5,923 keepers total (5,328 TV, 595 movies). Count is the
            KEEP/PRESERVE survivor with no usable non-bitmap subtitle, not
            extra copies. Not queued in Bazarr.
          </Text>
          <Table
            headers={["Show", "Type", "Missing", "Groups"]}
            columnAlign={["left", "left", "right", "right"]}
            striped
            rows={TOP_MISSING}
          />
        </Stack>
        <Stack gap={8}>
          <H2>Needs human review</H2>
          <Text tone="secondary" size="small">
            142 groups across 12 shows. Cooking titles dominate: competing
            encodes where English/fidelity/size did not settle cleanly.
          </Text>
          <Table
            headers={["Show", "Review", "Dups", "GiB"]}
            columnAlign={["left", "right", "right", "right"]}
            striped
            rows={REVIEW_SHOWS}
            rowTone={REVIEW_SHOWS.map(() => "warning" as const)}
          />
        </Stack>
      </Grid>

      <Callout tone="neutral" title="How to read this">
        30,801 groups means one identity cluster per episode or movie. 28,291
        are singletons (no extra copy). A previous Remux/archival scan on a
        larger library proposed 438 GiB; this profile prefers the smaller file
        when visual quality is not actually higher, so TV reclaimable is 917
        GiB. Open the UI at :8484 against this run to inspect a group before
        staging anything.
      </Callout>
    </Stack>
  );
}
