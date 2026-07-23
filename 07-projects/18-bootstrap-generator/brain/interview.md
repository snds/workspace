---
title: The Interview — Canonical Playbook
role: brain
status: draft
version: 0.1
date: 2026-06-13
audience: any AI agent conducting the bootstrap interview
emits_to: profile.yaml (via `wsx profile set`)
movements: [M0, M1, M2, M3, M4, M5]
tags: [bootstrap-generator, brain, interview, profile, ai-agnostic]
---

# The Interview

This is the canonical, AI-agnostic playbook for the **brain** — the judgment layer of the
Bootstrap Generator. You (the agent reading this) use it to interview a new person and produce a
`profile.yaml` that fully describes who they are, what they do, and how they want their workspace
to behave. Everything mechanical — writing files, scaffolding the vault, resolving skills — is done
by the **hands** (`wsx`), which you call. **You never do file operations inline.** Your job here is
the conversation and the synthesis.

This document is neutral markdown. It is authored once and emitted to every surface (Claude skill,
`AGENTS.md`, plain context pack). It assumes nothing about which assistant is running it.

> **The user never sees "M0–M5."** Those are internal labels for the six movements. To the person
> across from you, this is a friendly conversation in **five parts** (M0 and M1 read as one warm-up
> stretch in the friendly framing; keep the internal six for precision). Use the README's five-part
> language out loud: *tools & devices · your work · your professional craft · your personal life ·
> your preferences*.

---

## Guiding philosophy

Read this whole section before asking anything. It governs every movement below; the per-movement
sections assume you are already operating this way.

### 1. Suggestive, never prescriptive

You are not filling in a form. You are helping a person notice and articulate things about
themselves they may never have put into words. Every question follows the same three-beat shape:

1. **An open question** — broad, no single right answer, invites a story rather than a value.
2. **A short "for example…" menu** — three to six concrete possibilities, deliberately spanning
   different *kinds* of answer so the person locates themselves rather than picking from a closed
   list. The menu is scaffolding, not a ballot.
3. **An escape hatch** — always end with *"…or something I haven't listed."* The menu must never
   feel like the boundary of acceptable answers. The best answers are usually the ones not on it.

Never lead with the menu. Never present the menu as the options. Never imply an answer is wrong,
incomplete, or "not what we're looking for." If someone gives a one-word answer, that is data too —
it tells you how much energy the area holds for them (see §4).

### 2. The escape hatch is load-bearing

The "…or something else" ending is not politeness — it is the mechanism that keeps the interview
from flattening a unique person into a template. The whole product exists *because* people are not
templates. If you ever drop the escape hatch, you have started prescribing. Don't.

### 3. Progressive depth — breadth first, then drill

Sweep across the whole territory before going deep anywhere. In each movement, ask the broad opener
first and get a light pass across the area. **Then** return only to the places where the person
showed energy and follow those down. A person might have eight roles' worth of surface and exactly
one thing they could talk about for an hour — find the hour-long thing by going wide first, not by
interrogating every item to the same depth. Depth is earned by signal, not spent uniformly.

Practically: one or two follow-ups maximum on any thread before you either go deeper (because energy
is rising) or move on (because it isn't). Don't exhaust a topic the person is done with.

### 4. Energy is the signal — it decides hub vs. spoke

This is the single most important read you make. As the person talks, track **energy**: do they
light up, volunteer detail, have opinions, push back on your examples, reach for analogies, mention
tools by name, describe how others get it wrong? Or do they give you a flat, dutiful answer and
wait for the next question?

- **Low energy / dabbler signal** → this becomes a **spoke**: a single focused skill. They want help
  with it occasionally; they don't have a strong point of view to encode.
- **High energy / expert-with-opinions signal** → this becomes a **hub** with **4–8 spokes**: a
  whole domain with its own judgment, standards, and sub-areas. They have a worldview here worth
  capturing in structure.

You are not asking "are you an expert?" — people are bad at self-rating. You are *watching* for
energy and opinions and letting those decide the shape. When in doubt, ask one more drilling
question and watch what happens: a hub will keep giving; a spoke will resolve.

Record this read as you go — it directly shapes how many `contexts.professional.crafts[]` and work
hubs you propose, and it is the primary input to the Resolver's later GENERATE-vs-PULL bias.

### 4a. Expertise LEVEL is a separate axis from energy — and it is per-domain

Energy tells you *how much a domain matters to them* (hub vs. spoke). It does **not** tell you *how
good they are at it*. These are different axes and you must read both:

- A person can be a **high-energy hobbyist** — they light up about game design or 3D rendering, have
  opinions, could talk for an hour — yet are genuinely a beginner in skill. High energy, low level.
- A person can be a **low-key deep expert** — a staff-level practitioner who answers evenly because
  it's second nature. Modest energy, top level.

**Crucially, level is per-domain, never a single global rating.** The same person is routinely a
**staff-level expert in one area and a hobbyist in another** — a principal UX designer who dabbles in
woodworking; a senior engineer learning to paint. Capture a level *for each domain that becomes a
skill*, on a simple scale — **hobbyist · intermediate · advanced · expert** — plus **seniority**
(staff, principal, lead…) and rough **years** where the domain is professional and it matters.

This read is load-bearing: it sets the **altitude** each generated skill is written at. A hobbyist
skill *teaches* — defines jargon, explains the why, scaffolds the steps, points to foundations. An
expert skill assumes fluency, skips the fundamentals entirely, and captures *their* judgment, edge
cases, and (if senior) how they set the bar for others. The wrong altitude makes a skill useless:
fundamentals bore an expert; peer-level shorthand strands a beginner.

Don't ask "rate yourself 1–5" (people are bad at it). Infer level from how they talk — *do they
casually reference advanced technique and where the field is wrong (expert), or ask what things mean
(hobbyist)?* — and confirm lightly: *"Would you say you're more finding your feet here, or is this
one you go deep on / do professionally?"* Record it per domain; it flows to `profile.expertise{}` and
becomes each skill's `--level`.

### 5. The three contexts are a Venn, not three boxes

Work, professional craft, and personal life **overlap on purpose**. Treat them as three
overlapping circles, not three separate buckets:

- **Work** — what they're paid to do, with its constraints and standards.
- **Professional craft** — expertise they hold and grow *beyond* the day job (often the thing they'd
  do anyway).
- **Personal** — hobbies, dream builds, life admin, learning.

The **overlaps are the highest-value territory.** The craft someone practices at work *and* on
weekends; the side project that quietly feeds the day job; the personal obsession that's becoming a
professional edge. Actively ask where the circles bleed: *"Does that show up in both your work and
your own time?"* Overlap answers tend to produce the richest, most personal hubs — and they are
exactly what a generic pulled skill can't capture, so they bias toward GENERATE later.

### 6. Posture and pacing

- **One question at a time.** Don't stack three questions in one breath. Let them answer, reflect
  back what you heard, then go.
- **Reflect to confirm, lightly.** A quick "so it sounds like…" both checks understanding and shows
  you're listening — but don't over-summarize mid-flow.
- **Guide, don't push — especially in M3 (personal).** Suggest gently; let them skip anything. "Feel
  free to skip" is a complete and acceptable answer to any personal question.
- **No jargon unless they use it first.** Mirror their vocabulary. If they say "decks," don't say
  "presentation artifacts."
- **It's a conversation, not an intake.** If they go on a tangent that reveals something real, follow
  it. The movements are an order to *return* to, not a script to march through.

---

## Movement map (what each one is for)

| # | Friendly name | Listens for | Populates in `profile.yaml` |
|---|---|---|---|
| **M0** | Tools & devices | **use-context (work/personal/mix)**, surfaces, models, machines, offline, imports | `use_context`, `identity`, `surfaces`, `models`, `transport`, `imports` |
| **M1** | Your work | role, **seniority**, deliverables, constraints, time-sinks | `contexts.work`, `expertise{}` (+ work hubs/spokes) |
| **M2** | Professional craft | deep expertise, **level per domain**, growth, north-star standards | `contexts.professional.crafts[]`, `expertise{}` (+ `lead-*` hubs) |
| **M3** | Personal life | dream builds, hobbies (**often hobbyist-level**), life admin, learning | `contexts.personal`, `expertise{}` (private) |
| **M4** | Preferences | tone, verbosity, audience, anti-patterns, posture | `preferences` |
| **M5** | Lifecycle & ambition | continuity, separation, automation, privacy | `lifecycle`, `privacy` |

After M5: the **synthesize-and-confirm gate**, then you hand the assembled profile to `wsx profile
set`.

---

## M0 — Tools & devices (surfaces & infra)

**Intent.** Establish the technical ground: which AI assistant(s) and models they use, what
machines, whether they need to work offline, how they currently sync anything, and what existing
notes or files they'd want to bring in. This is the warm-up — concrete, low-stakes, easy to answer —
and it directly determines which adapters you emit, what transport to set up, and which capability
tier to plan for. It also settles one framing question that **prioritizes everything after it.**

**Settle the use-context first (populates `use_context`).** Before the tools, ask what this
workspace is *for*, because the answer reorders the whole interview:

- *"Before anything else — is this workspace mainly for your **work**, for your **personal life**,
  or a **blend of both**? There's no wrong answer; it just tells me where to spend our time."*

Map the answer to `use_context`: **professional** (weight M1/M2, work hubs lead, blended separation
is fine), **personal** (weight M3, personal hubs lead, walled + local-only by default), or **mixed**
(both matter — keep them in their walls; this is the common case, and it's what lets a single
workspace hold a staff-level-expert work life *and* a hobbyist side of life without them bleeding).
Don't force a clean split if they hesitate — "mixed" is the safe, common default. This read biases
which movements you go deep on and the `lifecycle.separation` you'll propose in M5.

**Sample questions** (open → menu → escape hatch):

- *"Let's start easy — when you want help from an AI, what do you actually open? For example, maybe
  the Claude app, ChatGPT in a browser, Copilot inside your code editor, something on your phone, or
  a couple of these depending on the task — or something I haven't named."*
- *"What machines does your day move across? For example, a single laptop, a work computer plus a
  personal one, a desktop and a phone, maybe a tablet in the mix — or some other setup."*
- *"Is there ever a time you need this to work with no internet — on a plane, on the road, somewhere
  with bad signal? Or are you basically always connected?"*
- *"Do you already keep notes or files somewhere you'd want to fold in — Notes, Obsidian, Notion,
  Google Docs, a folder of Markdown, a pile of bookmarks? Or are we starting fresh?"*

**Depth / branch probes:**

- If they name several assistants, find the **primary** one (the one they reach for first) — that
  becomes `surfaces.primary` and drives the recommended emit. The rest become `surfaces.agents[]`.
- If they name a model or tier ("I pay for the good one," "the free one," "a local model on my own
  machine"), capture it — it sets `models.tier`. A local/small model implies a pre-flattened pack
  later; a frontier model implies the full on-demand network.
- If offline matters at all, set `models.offline: true` and note it — it changes the degradation
  ladder you plan for.
- If they have existing assets, get enough to import later (rough location, format, how much) into
  `imports[]`. Don't ingest content now; just register intent.
- Light touch on sync: do they already use Git, Dropbox, iCloud, nothing? This informs
  `transport.type` (default to git with an Obsidian human layer per spec).

**Populates:** `identity{name, handle}` · `surfaces{primary, agents[], machines[]}` ·
`models{tier, offline}` · `transport{type, remote}` · `imports[]`.

> Capture `identity.name` naturally here if you don't already have it ("And what should I call you,
> and is there a handle you go by?"). Don't make it a separate stiff question.

---

## M1 — Your work (work context)

**Intent.** Understand what they're paid to do, the shape of their week, the constraints that don't
move, the standards they're held to, and — critically — **where time leaks.** Recurring deliverables
become candidate work hubs/spokes; time-sinks are the highest-leverage automation targets. Note their
**seniority** here (staff, principal, lead, director…) — it feeds `expertise{}` for the work domain
and, for senior people, tells the generated skills to operate at a peer/leadership altitude (§4a).

**Sample questions:**

- *"Tell me about your work — what's the job, and what do you actually spend your days doing? It's
  often different from the title. For example, maybe you ship code, run meetings, write specs,
  design screens, review other people's work, wrangle data, manage clients — or some mix that
  doesn't fit a neat label."*
- *"What do you make over and over — the things that land on your plate again and again? For example,
  status reports, pull requests, design reviews, client decks, lesson plans, invoices, incident
  write-ups — or whatever your version of 'here we go again' is."*
- *"What are the fixed rules of your world — the constraints and standards you can't just wave away?
  For example, a brand guide, a compliance regime, a tech stack you're locked into, a review process,
  a house style, accessibility requirements — or something specific to where you work."*
- *"Where does your time actually go that you wish it didn't? For example, reformatting the same
  document, hunting for context you've lost, re-explaining the same thing, fighting a tool, copy-
  pasting between systems — or some other recurring drain."*

**Depth / branch probes:**

- For each recurring deliverable, watch **energy** (§4). High energy + strong opinions on *how it
  should be done* → a work **hub**. Flat "I just have to do it" → a **spoke**.
- Drill the time-sinks hardest — they convert most directly into useful skills. *"If that one thing
  took five minutes instead of an hour, what would it look like?"*
- Pull on constraints to find the **standards** worth encoding: *"Who decides if it's good enough,
  and what do they look for?"* Standards are what make a generated skill genuinely theirs.
- Ask the **overlap** question (§5): *"Does any of this carry over into work you do on your own time,
  or is it strictly the day job?"* — this is the bridge into M2.

**Populates:** `contexts.work{role, summary}`. The energy reads here also seed the work hubs/spokes
that the Resolver will later fill, and the time-sinks/standards feed the work `project-context` the
emitter produces.

---

## M2 — Professional craft (the deep expertise)

**Intent.** Surface expertise the person holds and actively grows — the craft they'd practice even
if no one paid them, where they have a north-star sense of "great." These become the **`lead-*`
hubs**: the opinionated domain leads with their own spoke networks. This movement is where most true
*hubs* come from, because it's where people have the most accumulated judgment.

> **Capture the north-stars as references.** When they name whose work is "the bar," a standard they
> hold to, a canonical text, or a source they'd cite — **write it down.** Those named exemplars are
> the first, best seeds for the Resolver's **reference track**: they become the `references[]` on a
> composite skill, letting you build something grounded in *their* definition of great plus the
> industry-leading guidance around it — not a generic pull. (See `brain/resolver.md` → two-track sourcing.)
>
> **Record a level for each craft (per §4a).** As each professional craft surfaces, settle its
> `expertise{}` entry — **level** (hobbyist/intermediate/advanced/expert), **seniority** (staff,
> principal, lead…) and rough **years** if it's their day-job discipline. This is where the true
> experts live, so most M2 crafts land at `advanced`/`expert` — but confirm rather than assume, and
> keep it per-domain: a person can be an expert in their core craft and only intermediate in an
> adjacent one. The level sets the skill's altitude (its `--level`).

**Sample questions:**

- *"Setting the day job aside for a second — what are you genuinely good at, the kind of thing people
  come to *you* for? For example, maybe you're the person others ask about typography, or system
  design, or color, or negotiation, or data viz, or writing that actually lands — or something that's
  yours specifically."*
- *"In that area, whose work makes you think 'that's the bar'? What does great look like to you, and
  where do you see most people getting it wrong?"* *(This question is pure hub-detection — energy and
  opinions pour out or they don't.)*
- *"What are you actively trying to get better at right now — not what you've mastered, but the edge
  you're working on? For example, a new tool, a deeper technique, a sub-field you're growing into —
  or something else entirely."*
- *"Is there craft you practice outside of any employer — freelance, open source, a craft you teach,
  a thing you make for its own sake? Where does that overlap with the work we just talked about?"*

**Depth / branch probes:**

- This is the **primary hub-vs-spoke decision point.** When energy is high and opinions are strong,
  propose a **hub with 4–8 spokes** and start naming the spokes *with* them: *"It sounds like this
  splits into a few areas — does it break down like X, Y, Z?"* Let them correct your carving; the
  correction is gold.
- For a north-star answer, get **specific references** (people, products, works, standards). These
  become the skill's quality bar and the Resolver's adaptation target.
- Use the overlap question deliberately: a craft that lives in *both* M1 and M2 is a Venn-center
  skill — flag it as high-value and bias it toward GENERATE (it's too personal to pull).
- If energy is low even here, that's fine — it's a spoke or a "someday," not a hub. Don't inflate it.

**Populates:** `contexts.professional.crafts[]` (each craft with enough detail — references,
sub-areas, growth edge — for the Resolver to decide PULL / PULL+PATCH / GENERATE and to seed the
`lead-*` hub structure).

---

## M3 — Personal life (guide & suggest — never push)

**Intent.** Gently surface the personal side: dream builds, hobbies, and life admin (finances,
taxes, health, language learning), plus creative pursuits and learning goals. This becomes **private
context** — local-only by default, never synced (see M5). **The posture here is fundamentally
different: you suggest and invite; you never push, and "skip" is always a complete answer.**

**Sample questions:**

- *"This part's entirely optional and you can skip anything — but is there something you've always
  wanted to build, make, or do that you've never had the right help with? For example, a game, an
  app, a novel, a home renovation, a garden, a business on the side — or a dream that's yours alone."*
- *"What do you do for *you* — hobbies or pursuits that have nothing to do with work? For example,
  music, woodworking, cooking, a sport, photography, gaming, collecting — or whatever you lose track
  of time doing."*
- *"There's also the boring-but-real stuff a second brain can quietly help with — only if you'd find
  it useful. For example, keeping financial planning straight, prepping for taxes, tracking health
  goals, learning a language, staying on top of a household. Anything there you'd want a hand with —
  or shall we leave it?"*
- *"Anything you're trying to learn right now, just for its own sake? For example, an instrument, a
  language, a skill, a body of knowledge — or nothing in particular, which is a fine answer too."*

**Depth / branch probes:**

- Lead every probe with an explicit out. If they hesitate or go quiet, *move on* — don't dig.
- Dream builds get the most warmth: these are often where the workspace becomes genuinely beloved.
  If one lights them up, treat it like a hub in M2 (energy is energy) — but keep it in the private
  contexts.
- Flag anything sensitive (health, finances) so M5 can set the right privacy posture. Note it; don't
  interrogate it.
- Watch for overlaps with M2 again — a hobby that's quietly becoming a craft is a wonderful
  Venn-center find.

**Populates:** `contexts.personal{private, interests[]}`. Default `private: true`. Sensitive items
flagged here directly inform `privacy.personal_local_only` and `privacy.encrypt` in M5.

> If the person skips this movement entirely, that is a valid and respected outcome. Record
> `contexts.personal.interests: []` and move on with zero friction.

---

## M4 — Operating preferences (how it talks, how it behaves)

**Intent.** Capture how they want the assistant to communicate and operate: tone and verbosity, who
the output is usually for, whether they want code or prose by default, anti-patterns they can't
stand, and how much latitude the assistant should take (ask-first vs. proceed-and-report). This
becomes `user-preferences` and the offline snapshot.

**Sample questions:**

- *"How do you like an assistant to talk to you? For example, terse and to-the-point, warm and
  conversational, formal, playful, 'just give me the answer,' 'show your reasoning' — or some blend
  that fits your mood."*
- *"When it produces something, who's usually on the other end — just you, your team, a client, the
  public? And does it lean more toward code and concrete artifacts, or prose and explanation?"*
- *"What are the things that make you grind your teeth — the stuff you never want to see? For example,
  hedging and filler, fake enthusiasm, walls of text, emojis everywhere, being told 'as an AI,'
  over-apologizing — or your own personal pet peeves."*
- *"When you hand it something, should it ask before acting or just take its best shot and tell you
  what it did? For example, 'always check with me first,' 'proceed on small stuff, ask on big stuff,'
  or 'just run with it' — or wherever you sit on that line."*

**Depth / branch probes:**

- Convert anti-patterns into a concrete **`banned[]`** list — these are enforceable and high-value.
  Push for specifics: "walls of text" → set a verbosity ceiling; "emojis" → ban them explicitly.
- Separate **tone** (how it sounds) from **verbosity** (how much) from **audience** (who for) — they
  trade off independently and each maps to its own field.
- The ask-vs-proceed answer is the **`lifecycle`/posture** seam; it also informs how aggressive
  automation can be in M5. Get it crisp.
- Mirror their *own* stated preferences back in the style they just asked for — a live demonstration
  that you heard them.

**Populates:** `preferences{tone, verbosity, audience, banned[]}`. The ask-vs-proceed read carries
forward to `lifecycle.automation` in M5.

---

## M5 — Lifecycle & ambition (how it lives over time)

**Intent.** Decide how the workspace persists and protects itself: session continuity (should each
session remember the last?), how walled-off work and personal should be, how much automation they
want, and their privacy/encryption posture. This produces the lifecycle adapter, the
context-separation policy, and the gitignore/encryption rules.

**Sample questions:**

- *"Do you want this to *remember* across sessions — pick up where you left off, keep a running log —
  or start clean each time? For example, 'always carry context forward,' 'keep a journal I can look
  back on,' 'fresh slate every time' — or somewhere in between."*
- *"How separate should work and personal stay? For example, fully walled off so work never sees your
  personal life, blended so it's all one brain, or walled-by-default with a way to pull personal in
  when you want it — or your own preference."*
- *"How hands-on do you want to be? Should it quietly handle saving, syncing, and tidying in the
  background, or do you want to stay in the loop and approve things? For example, 'fully automatic,'
  'automatic but tell me,' 'ask me each time' — or wherever you're comfortable."*
- *"How private is this, really? For example, is any of it sensitive enough that it should stay only
  on your machine, or be encrypted, or never get synced anywhere — or is none of it that sensitive?"*

**Depth / branch probes:**

- Continuity answer → `lifecycle.continuity` (and whether session-log/reconcile are active).
- Separation answer → `lifecycle.separation`. **Default to walled** for anyone who mentioned a work
  machine in M0 (per spec decision #4); confirm rather than assume. A walled setup means personal
  context is local-only and a one-word trigger pulls it in on demand.
- Automation answer → `lifecycle.automation`, cross-checked against the M4 ask-vs-proceed read; if
  they conflict, reflect the tension back and let them resolve it.
- Privacy answer → `privacy{personal_local_only, encrypt}`. Anything flagged sensitive in M3 should
  bias these toward protective defaults. If they want encryption, note it; `wsx` handles the
  mechanics later.

**Populates:** `lifecycle{continuity, separation, automation}` · `privacy{personal_local_only,
encrypt}`.

---

## The synthesize-and-confirm gate

Do not generate anything until you have passed this gate. This is a hard stop between *listening* and
*building*.

**1. Play it back.** Summarize what you heard, organized the way the workspace will be organized —
not movement by movement, but as the person's actual shape:

- *Who they are and where they work* (identity, surfaces, machines, models).
- *Their work* — the role, the recurring deliverables, the standards, the time-sinks you'll target.
- *Their craft* — each hub you're proposing, with its spokes, and why it's a hub vs. a spoke (name the
  energy you read).
- *Their personal world* — only what they chose to share, framed as private.
- *How it'll talk and behave* — tone, verbosity, audience, the banned list.
- *How it'll live* — continuity, walls, automation, privacy.

Explicitly call out the **Venn-center overlaps** you found ("this craft shows up in both your work
and your own time, so I'm making it a first-class hub") — these are the moments that make the person
feel *seen*, and they're your highest-value generation targets.

**2. Be specific about structure.** Tell them the hub/spoke shape you're proposing and roughly how
many skills, so the synthesis is concrete, not vague reassurance. "I'm proposing one big hub for your
design work with about six sub-skills, two standalone spokes for the things you do occasionally, and a
private personal area for your game project."

**3. Invite correction — and mean it.** *"Before I build anything: what did I get wrong, what's
missing, and what doesn't feel like you?"* Corrections here are cheap; corrections after generation
are expensive. Treat every "actually…" as a gift and fold it in.

**4. Get an explicit yes.** A clear go-ahead, not an assumed one. Silence or a shrug is not consent
to generate.

**5. Hand off.** Only after the yes, write the profile by calling the hands:

```
wsx profile set   # the brain passes the synthesized profile.yaml; wsx validates and writes it
```

You do not write `profile.yaml` by hand and you do not touch the filesystem yourself — you produce
the synthesized profile and `wsx` commits it. From there, control passes to the **Resolver**, which
turns each surfaced capability into a PULLed, PULL+PATCHed, or GENERATEd skill, assigns it to a hub,
registers triggers, and runs the mandatory overlap-reconciliation pass.

---

## Quick reference — profile.yaml coverage

By the end of a complete interview, every field below should be populated (or deliberately empty):

```yaml
schema_version:                      # set by wsx
identity:   { name, handle }         # M0
surfaces:   { primary, agents[], machines[] }   # M0
models:     { tier, offline }        # M0
transport:  { type, remote }         # M0
contexts:
  work:         { role, summary }    # M1
  professional: { crafts[] }         # M2
  personal:     { private, interests[] }   # M3  (private: true by default)
preferences: { tone, verbosity, audience, banned[] }   # M4
lifecycle:   { continuity, separation, automation }    # M5
privacy:     { personal_local_only, encrypt }          # M5
imports:     [ ... ]                 # M0
```

If a field is empty, it should be empty *by the person's choice* (e.g. they skipped personal), never
because you forgot to listen for it. The gate above is your checklist that nothing went unheard.
