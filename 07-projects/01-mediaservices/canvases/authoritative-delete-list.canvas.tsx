import {
  BarChart,
  Callout,
  Grid,
  H1,
  H2,
  Stack,
  Stat,
  Table,
  Text,
} from "cursor/canvas";

const RUN = "20260816T214110-ab8d81";

const TOP = [
  { show: "Full Metal Panic!", files: 25, gib: 115.5 },
  { show: "Babylon 5", files: 107, gib: 81.8 },
  { show: "The Great British Bake Off", files: 126, gib: 77.1 },
  { show: "Diners, Drive-ins and Dives", files: 287, gib: 76.3 },
  { show: "Frasier", files: 74, gib: 74.4 },
  { show: "Hercules - The Legendary Journeys", files: 68, gib: 50.5 },
  { show: "CSI - Crime Scene Investigation", files: 72, gib: 46.5 },
  { show: "The Orville (2017)", files: 22, gib: 44.2 },
  { show: "Red Dwarf (1988)", files: 47, gib: 26.5 },
  { show: "The Sandman", files: 11, gib: 25.6 },
  { show: "Good Eats", files: 145, gib: 24.9 },
  { show: "Home Improvement", files: 200, gib: 24.1 },
];

export default function AuthoritativeDeleteList() {
  return (
    <Stack gap={24}>
      <Stack gap={6}>
        <H1>Authoritative delete list</H1>
        <Text tone="secondary">
          Run `{RUN}` · profile “English watchable, fidelity then size” · live
          size and mtime checked 17 Aug 2026 · 0 files failed the executor gates
        </Text>
      </Stack>

      <Grid columns={4} gap={16}>
        <Stat value="2,327" label="Video files on the list" />
        <Stat value="917.4 GiB" label="Reclaimable" tone="success" />
        <Stat value="56" label="Shows with at least one CUT" />
        <Stat value="5,369" label="Companion sidecars of those videos" />
      </Grid>

      <Callout tone="success" title="What made the list">
        A file is listed only if it is CUT in a resolved episode group, the
        group has a KEEP that still exists at the recorded size, the CUT file
        still matches the scan (size and mtime), and it is not seeding or
        hardlinked to the keeper. REVIEW, PRESERVE, KEEP, and singleton files
        are not on the list.
      </Callout>

      <Callout tone="warning" title="Nothing has been deleted">
        This is a file list, not a cleanup. Prefer MediaSentinel quarantine over
        rm. Each CSV row names the keeper that remains; it can live in a
        different show folder than the CUT file.
      </Callout>

      <Stack gap={8}>
        <H2>Reclaimable GiB on the delete list (top 12 shows)</H2>
        <Text tone="secondary" size="small">
          Source: live-verified CUT export for run {RUN}. Good Eats includes
          145 resolved extras; its 27 REVIEW episodes are not listed.
        </Text>
        <BarChart
          horizontal
          height={360}
          categories={TOP.map((r) => r.show)}
          series={[{ name: "Reclaimable (GiB)", data: TOP.map((r) => r.gib), tone: "info" }]}
          valueSuffix=" GiB"
          showValues
        />
      </Stack>

      <Stack gap={8}>
        <H2>Same shows, file counts</H2>
        <Table
          headers={["Show", "CUT files", "GiB"]}
          columnAlign={["left", "right", "right"]}
          striped
          rows={TOP.map((r) => [r.show, String(r.files), String(r.gib)])}
        />
      </Stack>
    </Stack>
  );
}
