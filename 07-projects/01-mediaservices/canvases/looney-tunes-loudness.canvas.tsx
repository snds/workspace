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
  LineChart,
  Row,
  Stack,
  Stat,
  Table,
  Text,
  useHostTheme,
} from "cursor/canvas";

// EBU R128 measurements via ffmpeg loudnorm (full decode; 3x10-min windows for
// files >8GB), run 2026-08-26 inside the MediaSentinel container on the Unraid
// server. 2,919 Looney Tunes files (both library folders) + 6 reference files.
// Data: /config/loudness/results.jsonl, summary.json, gains.csv (server) and
// MediaSentinel/scratch/loudness-data/ (local).

const TARGET = -21.9;
const NOMINAL_PLAYED = -6.6;
const NOMINAL_MANAGED = -7.4;

const REFS = [
  { label: "Stargate Atlantis S02E14 (episode)", codec: "EAC3 5.1", i: -26.55 },
  { label: "Wicked, 2024 (film)", codec: "AC3 5.1", i: -25.63 },
  { label: "Welcome to Wrexham S02E02 (episode)", codec: "EAC3 5.1", i: -22.06 },
  { label: "Thor: Ragnarok, 2017 (film)", codec: "AC3 5.1", i: -21.84 },
  { label: "Star Trek: TNG S03E12 (episode)", codec: "AC3 2.0", i: -21.67 },
  { label: "Whose Line Is It Anyway? S06E07 (episode)", codec: "AAC 2.0", i: -21.2 },
];

const HIST_BUCKETS = [
  ["-34", 1], ["-33", 2], ["-32", 7], ["-31", 14], ["-30", 30], ["-29", 50],
  ["-28", 60], ["-27", 58], ["-26", 51], ["-25", 41], ["-24", 31], ["-23", 15],
  ["-22", 26], ["-21", 21], ["-20", 9], ["-19", 6], ["-18", 5], ["-17", 3],
  ["-16", 58], ["-15", 238], ["-14", 319], ["-13", 19],
] as const;

const SEASONS = [
  ["1930", -14.96], ["1931", -14.96], ["1932", -14.33], ["1933", -14.06],
  ["1934", -13.91], ["1935", -14.02], ["1936", -14.34], ["1937", -14.5],
  ["1938", -14.52], ["1939", -21.54], ["1940", -22.14], ["1941", -16.09],
  ["1942", -15.11], ["1943", -19.34], ["1944", -20.65], ["1945", -22.94],
  ["1946", -24.38], ["1947", -26.37], ["1948", -26.03], ["1949", -15.26],
  ["1950", -15.38], ["1951", -15.6], ["1952", -15.56], ["1953", -15.63],
  ["1954", -15.87], ["1955", -15.01], ["1956", -15.4], ["1957", -15.32],
  ["1958", -14.71], ["1959", -15.58], ["1960", -15.26], ["1961", -15.28],
  ["1962", -14.98], ["1963", -14.9], ["1964", -15.0], ["1965", -20.78],
  ["1966", -14.24], ["1967", -14.22], ["1968", -14.44], ["1969", -14.05],
] as const;

const GROUPS = [
  { name: "What Plex plays today (1,064 eps)", median: -15.27, p10: -28.41, p90: -13.95, spread: 14.46 },
  { name: "Sonarr-managed copies (1,048 files)", median: -14.48, p10: -15.58, p90: -13.84, spread: 1.74 },
  { name: "Unmanaged dump copies (1,871 files)", median: -15.31, p10: -29.0, p90: -13.9, spread: 15.1 },
];

const LOUDEST = [
  ["S1963E02 Devil's Feud Cake (SDTV)", "-12.6"],
  ["S1939E24 Dangerous Dan McFoo (BDRip)", "-12.7"],
  ["S1983E01 Daffy Duck's Fantastic Island (WEBDL)", "-12.9"],
  ["S1940E37 Porky's Hired Hand (SDTV)", "-12.9"],
  ["S1941E34 Robinson Crusoe Jr (SDTV)", "-13.1"],
];

const QUIETEST = [
  ["S1945E04 The Unruly Hare (SDTV)", "-34.0"],
  ["S1938E31 Porky's Naughty Nephew (SDTV)", "-33.2"],
  ["S1936E31 Porky in the North Woods (DVDRip)", "-33.0"],
  ["S1944E09 Bugs Bunny Nips the Nips (SDTV)", "-32.4"],
  ["S1936E28 Little Beau Porky (DVDRip)", "-32.2"],
];

export default function LooneyTunesLoudness() {
  const theme = useHostTheme();
  const caption = { color: theme.text.tertiary, fontSize: 11 } as const;

  return (
    <Stack gap={20} style={{ maxWidth: 980, margin: "0 auto", padding: 20 }}>
      <Stack gap={4}>
        <H1>Looney Tunes: loudness evaluation and subtitle coverage</H1>
        <Text tone="secondary">
          EBU R128 measurement of all 2,919 show files on the server plus 6 reference titles
          from recent watch history. Source: ffmpeg loudnorm, run in the MediaSentinel
          container, 2026-08-26. Zero measurement errors.
        </Text>
      </Stack>

      <Grid columns={3} gap={12}>
        <Stat value="-21.9 LUFS" label="Reference target (median of watched episodes)" />
        <Stat value="-6.6 dB" label="Best nominal gain, current library" tone="info" />
        <Stat value="14.5 dB" label="Episode-to-episode spread (p10-p90)" tone="danger" />
      </Grid>

      <Callout tone="warning" title="A single gain cannot fix this show as it stands">
        The show plays 6.6 dB hotter than your other content, but its real problem is
        internal: episodes span -34 to -12.6 LUFS. A flat -6.6 dB pass leaves 422 of
        1,064 episodes more than 3 dB off target. The spread, not the level, is what
        forces the remote reaching.
      </Callout>

      <H2>The reference basis</H2>
      <Text tone="secondary">
        Measured from titles in recent Plex watch history. The target is the median of
        the four TV episodes; the films sit a few dB lower, as theatrical mixes do.
      </Text>
      <Table
        headers={["Reference title", "Audio", "Integrated LUFS"]}
        rows={REFS.map((r) => [r.label, r.codec, r.i.toFixed(1)])}
        columnAlign={["left", "left", "right"]}
      />

      <H2>Where the episodes actually sit</H2>
      <BarChart
        categories={HIST_BUCKETS.map(([b]) => b)}
        series={[{ name: "Episodes", data: HIST_BUCKETS.map(([, n]) => n) }]}
        height={220}
        showValues={false}
      />
      <Text style={caption}>
        Episodes Plex currently plays, by integrated loudness (LUFS, 1 dB bins; n=1,064).
        Bimodal: a hot mode at -14/-15 LUFS (557 eps) and a long quiet tail from -23 down
        to -34. Target: -21.9. Jumping between the mode and the tail is a 10 to 20 dB swing.
      </Text>

      <H2>The quiet years are an era, not random</H2>
      <LineChart
        categories={SEASONS.map(([y]) => y)}
        series={[{ name: "Season median LUFS", data: SEASONS.map(([, v]) => v), tone: "info" }]}
        height={200}
        beginAtZero={false}
        referenceLines={[{ value: TARGET, label: "target -21.9", tone: "success" }]}
        showValues={false}
      />
      <Text style={caption}>
        Median integrated loudness (LUFS) per season year, 1930-1969 main run, files Plex
        plays. The 1939-1948 seasons come from quiet sources (-19 to -26); nearly everything
        else sits at -14 to -16. That is the between-episode jump you feel on the remote.
      </Text>

      <H2>Three copies, three stories</H2>
      <Table
        headers={["File set", "Median LUFS", "p10", "p90", "Spread (dB)"]}
        rows={GROUPS.map((g) => [
          g.name,
          g.median.toFixed(1),
          g.p10.toFixed(1),
          g.p90.toFixed(1),
          g.spread.toFixed(1),
        ])}
        columnAlign={["left", "right", "right", "right", "right"]}
        rowTone={[undefined, "success", "danger"]}
      />
      <Text tone="secondary">
        The Sonarr-managed library is already internally leveled: 1.7 dB spread, essentially
        one volume setting for the whole show. But Plex auto-plays the unmanaged duplicate
        folder for 1,035 of 1,064 episodes, and that copy set has a 15.1 dB spread. One dump
        copy (S1938E35 The Night Watchman DVDRip) has a silent or broken audio track.
      </Text>

      <H2>What each fix would achieve</H2>
      <BarChart
        categories={["Flat -6.6 dB on current files", "Per-file gains (gains.csv)"]}
        series={[
          { name: "Within 1 dB of target", data: [366, 1064], tone: "success" },
          { name: "More than 3 dB off", data: [422, 0], tone: "danger" },
        ]}
        height={180}
        showValues={true}
      />
      <Text style={caption}>
        Episodes within tolerance after correction (n=1,064). Per-file values are exact by
        construction; 84 very quiet files get their boost capped to keep true peak at or
        below -1 dBTP and land slightly under target.
      </Text>

      <H2>Recommended path</H2>
      <Stack gap={10}>
        <Card>
          <CardHeader trailing={<Text size="small" tone="tertiary">structural, no re-encode</Text>}>
            1. Quarantine the duplicate folder via the MediaSentinel review flow
          </CardHeader>
          <CardBody>
            <Text>
              Serving the managed copies collapses the episode-to-episode spread from 15 dB
              to 1.7 dB with zero audio processing, and those copies already carry the
              subtitle set. Then a single nominal gain of <Text weight="semibold">-7.4 dB</Text> on
              the show brings it from -14.5 to the -21.9 LUFS your other content plays at,
              and one value genuinely fits nearly every episode.
            </Text>
          </CardBody>
        </Card>
        <Card>
          <CardHeader trailing={<Text size="small" tone="tertiary">if keeping current files</Text>}>
            2. Per-file gain from gains.csv
          </CardHeader>
          <CardBody>
            <Text>
              2,919 rows with measured LUFS, true peak, and clip-safe gain per file, on the
              server at /config/loudness/gains.csv. Applying gain means rewriting audio
              tracks, so it belongs in a journaled, reversible executor pass, offered as a
              future sentinel verb. The flat -6.6 dB answer exists but leaves 40 percent of
              episodes more than 3 dB off.
            </Text>
          </CardBody>
        </Card>
      </Stack>

      <Divider />

      <H2>Subtitles: every played episode now has one</H2>
      <Grid columns={4} gap={12}>
        <Stat value="1,064" label="Episodes in the show" />
        <Stat value="781" label="Sidecars placed and journaled" tone="success" />
        <Stat value="264" label="Already had embedded text subs" />
        <Stat value="0" label="Episodes still without subtitles" tone="success" />
      </Grid>
      <Text tone="secondary">
        Coverage audit found the copies Plex plays were mostly subtitle-less even though the
        managed twins were fully covered. Fix, in quality order: 721 human-made sidecars
        copied from the unplayed twin, 46 embedded ASS/SRT tracks extracted to sidecars, and
        only the 14 episodes with no human source anywhere transcribed through subgen
        (GPU whisper, large-v3-turbo). Existing subtitles were never overwritten; every new
        file is listed in a delete-list journal on the server. Final audit: 800 episodes
        resolve to a sidecar, 264 to embedded text, none uncovered. Plex partial scans
        confirmed the new English tracks are selectable.
      </Text>

      <H2>Extremes worth knowing about</H2>
      <Grid columns={2} gap={12}>
        <Stack gap={6}>
          <Text weight="semibold">Loudest played files (LUFS)</Text>
          <Table headers={["Episode", "LUFS"]} rows={LOUDEST} columnAlign={["left", "right"]} />
        </Stack>
        <Stack gap={6}>
          <Text weight="semibold">Quietest played files (LUFS)</Text>
          <Table headers={["Episode", "LUFS"]} rows={QUIETEST} columnAlign={["left", "right"]} />
        </Stack>
      </Grid>

      <Row gap={8}>
        <Text style={caption}>
          Artifacts: results.jsonl, summary.json, gains.csv, subtitle-sync-journal.txt in
          /mnt/user/appdata/media-sentinel/loudness/ on the server; mirrored summary and
          gains in MediaSentinel/scratch/loudness-data/.
        </Text>
      </Row>
    </Stack>
  );
}
