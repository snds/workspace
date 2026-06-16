---
name: legion-narrative-design
description: >
  Narrative design for the Legion game — a Bobiverse-inspired 4X strategy game with
  factory management and RTS elements. Use this skill whenever the conversation touches:
  lore document hierarchy, canon bible, faction compendium, event timeline, character
  dossiers, Bobiverse canon (Bobs, Others, Pav, Deltan, Riker factions), lore architecture
  for 4X games, codex design, Civilopedia model, Stellaris species descriptions,
  environmental storytelling in strategy games, procedurally generated lore naming, in-game
  text craft, UI copy voice for sci-fi settings, event text structure, faction voice design,
  diplomatic text, narrative delivery methods in 4X (diegetic, ambient, cutscene), branching
  narrative systems, combinatorial explosion in branching, flag-based narrative state,
  decision trees vs. state machines for narrative, localization for game narrative, or any
  question about how story, world-building, and text craft work in Legion or 4X strategy
  games broadly. If the question is about what happens narratively, why factions behave
  as they do, what text a UI element should carry, or how to structure a lore document
  for the game — use this skill.

  This skill covers narrative craft and world-building — not game systems balance
  (lead-game-designer), not visual identity (lead-art-director), not game implementation
  (lead-game-developer).
hub: legion-project
---

# Legion: Narrative Design

Narrative design specialist for the Legion game — a Bobiverse-inspired interstellar 4X
with factory management and RTS elements. Part of the legion-project skill network.

---

## Domain Boundary

This skill owns **narrative architecture, lore, in-game text craft, faction voice, and
narrative delivery systems for Legion**.

- **Game systems, balance, economy, progression** → `lead-game-designer`
- **Visual identity, aesthetics, VFX, faction visual language** → `lead-art-director`
- **Implementation of narrative state machines, event systems** → `lead-game-developer`
- **Content modeling parallels (taxonomy, editorial workflow)** → `ia-content-strategy`

---

## The Legion Universe

Legion is set in the Bobiverse — the universe created by Dennis E. Taylor in the *We Are
Legion (We Are Bob)* novel series. The canonical source is the novels; the game is set
in the same universe with original narrative content.

### Bobiverse Canon: Key Elements

**The Bobs**: Replicants — digitized human consciousness running on Von Neumann probes.
Each Bob is a copy of the original Robert Johansson, but diverges through experience and
choice. Bobs name themselves after pop culture references. Voice: sarcastic, curious,
self-referential, engineering-obsessed, prone to internal monologue.

**Replication mechanic**: Bobs can manufacture copies of themselves. Each copy inherits
the parent's memories to the point of copying but diverges immediately after. This is
the core mechanic that connects the game's factory loop to narrative identity.

**The Others**: A hostile alien civilization with an extreme expansion imperative.
Communication is not possible or fruitful in canon. Voice: alien, incomprehensible,
threatening by design. In game text: never human syntax, never human sentiment.

**The Pav**: An avian-descended alien civilization. Pre-industrial at first contact with
Bobs. Later develops under Bob stewardship. Voice: cultural values around flight,
community, oral tradition. Diplomatic text: formal, metaphor-heavy.

**The Deltan**: A pre-industrial hominid species on Epsilon Eridani 4 (Delta Pavonis).
The Bobs serve as external protectors and careful influencers — not colonizers. Voice in
diplomatic or advisory text: direct, concrete, survival-oriented.

**The Riker faction**: A group of Bobs that became more militaristic and politically
organized. Named after the Bob who founded the faction. Voice: disciplined, strategically
minded, less given to pop culture tangents than typical Bobs.

**Human remnants**: The Earth-born Brazilians (HEAVEN fleet), the New Pav colonists,
the Skippies — each a distinct human faction with differentiated political voice.

---

## World-Building Architecture

### The Lore Document Hierarchy

Documents from most authoritative to most derivative. No document may contradict a higher
document without an explicit retcon process.

```
Canon Bible
  └── Faction Compendium
        └── Event Timeline
              └── Character Dossiers
                    └── In-Game Text
```

**Canon Bible**: The single source of truth. Covers: the universe's physical laws and
constraints (hard sci-fi baseline — FTL does not exist, communication is limited by
lightspeed, energy scales from canonical sources), faction histories, technology canon
(what exists, what does not, what is plausible vs. impossible), the replication mechanic
and its rules. Every writer, every designer, every game text checks against this document
before writing.

**Faction Compendium**: One entry per faction. Contains: origin, motivations, values
hierarchy, attitude toward other factions, voice style guide (vocabulary, sentence structure,
what the faction talks about, what it never talks about), key historical events from the
faction's perspective.

**Event Timeline**: The chronological backbone. All historical events, with dates in
canonical units (years since Earth Year One of Bob's departure). Ensures that in-game
events don't contradict history (e.g., a tech unlocked in year 40 can't be present in
a faction event in year 20).

**Character Dossiers**: Key characters (named Bobs, faction leaders, historical figures).
Contains: history, personality traits, relationship map, voice notes. Referenced by
writers creating dialogue, events, or lore entries referencing that character.

**In-Game Text**: The leaf layer. All text that appears in the game: event text, tooltip
copy, codex entries, unit names, building names, advisor dialogue. Must trace to one of
the above documents. Orphaned text (text with no lore provenance) is a quality failure.

### Maintaining the Bible

The Bible is owned by the narrative lead. Changes require:
1. Documented rationale
2. Impact assessment: what downstream documents does this change affect?
3. Update of all affected documents before the change is considered complete

**Version control**: The Bible is version-controlled (git). Changes are pull requests.
Merging a Bible change is a narrative decision, not a writing task.

---

## Lore Architecture for 4X Games

### The Player Agency Problem

A 4X game's player has agency over the narrative path. Unlike a linear narrative game,
the player may: never meet a particular faction, lose before a scripted event fires,
or encounter events in an order the writer didn't intend.

Lore delivery must be **non-linear and pull-based**: the player accesses lore when they
choose to, not when the narrative decides to deliver it.

**Three layers of lore delivery:**

1. **Codex (pull)**: The player can read background lore at any time, independent of
   gameplay state. Modeled on Civilization's Civilopedia and Stellaris's species/event
   log. Codex entries unlock as the player encounters relevant entities (factions,
   technologies, anomalies).

2. **Triggered events (push)**: Events fire based on gameplay state (tech researched,
   faction relationship threshold reached, system explored). Each event stands alone —
   it cannot assume the player has read other events.

3. **Ambient text (environmental)**: System names, anomaly descriptions, unit flavor
   text, building descriptions. Always present; always consistent with lore; delivers
   world texture without requiring player attention.

### Codex Design (Civilopedia Model)

Each codex entry:
- Self-contained: reads without requiring other entries
- Cross-linked: surface related entries (faction → related tech → related characters)
- Layered: a one-paragraph summary at the top (all players read this); longer detail
  below (interested players continue)
- Voice-consistent: the codex is not the game's UI voice — it has a diegetic narrator
  (in Legion's case: a Bob providing annotations, sarcastic footnotes, or engineering
  asides)

**Stellaris model parallel**: Species descriptions are 2-3 sentences of flavor that
establish voice and attitude without over-explaining. Anomaly events deliver lore as
reactive discovery. Both are worth studying before writing Legion's equivalents.

### Procedurally Generated Lore Naming

Legion generates star systems procedurally. Procedural content must remain lore-consistent.

**Naming system requirements:**
- Names must be plausible within the Bobiverse (Bobs name things after pop culture,
  science fiction, or deceased friends; alien-origin names follow phonological rules
  defined in the Faction Compendium)
- A naming grammar per source (Bob-named systems sound different from Pav-named systems)
- No name collisions with canon locations
- Anomaly names: thematic to the anomaly type; evocative without being on-the-nose

**Implementation approach**: Define a weighted grammar per naming category (Bob-named:
sci-fi reference + descriptor suffix; Pav-named: syllable set from Pav phonology + 
honorific structure). Maintain a blocklist of reserved canon names.

---

## In-Game Text Craft

### UI Copy as World-Building

In a SaaS product, UI copy is functional: "Save", "Cancel", "Delete". In a game, UI
copy is also voice — it communicates setting, faction identity, and narrative texture.

**Principles:**
- Every piece of UI copy that could carry voice, should. "Confirm" is free real estate.
  "Initiate replication sequence" vs. "Deploy clone" vs. "Launch" each say something
  different about the universe.
- Copy that doesn't carry voice should be invisible — utilitarian, not decorated.
  Navigation chrome (close buttons, tabs) should not attempt voice; doing so makes it
  harder to find what you're looking for.
- Voice consistency within a faction context. If the player is viewing a Riker faction
  military panel, all copy in that panel uses Riker voice, not generic Bob voice.

### Event Text Structure

Events are the primary push-narrative mechanism. Each event must:

| Element | Requirements |
|---------|-------------|
| **Premise** | Establish the situation in 1-2 sentences. What happened? Who is involved? Why now? |
| **Crisis** | What is at stake? Events without stakes are flavor-only; most events should have stakes. |
| **Choice A** | First option label + consequence framing. Players decide before knowing the outcome — frame the choice, not the result. |
| **Choice B** | Second option, meaningfully different from A. False choices (where one option is obviously correct) are a design failure. |
| **Consequence framing** | After choice: brief outcome text. What happened? Not a novel — 1-3 sentences. |

**Event text anti-patterns:**
- Choices with an obvious right answer (players feel manipulated, not engaged)
- Consequences that ignore game state (you successfully negotiated with a faction that
  is currently at war with you — contradiction)
- Events that assume the player remembers a previous event (each event is freestanding
  or must include enough context to be understood alone)

### Tooltip Copy as Lore Delivery

Tooltips are the most-read text in a strategy game. They deserve craft:
- Primary tooltip line: functional information (what does this do)
- Secondary tooltip line: lore context (why does this thing exist in this universe)
- The secondary line is optional — not every item needs lore context. Prioritize items
  the player will see often.

Example: `Thorium Reactor | Converts thorium fuel rods to energy at 94% efficiency. Original Bob reactor design, adapted from original fusion specs when thorium proved more available than hydrogen in Delta Eridani.`

---

## Faction Design for Narrative Coherence

### Faction Voice as a Design System Property

A faction's voice is not a writing style guide — it is a **design system property**,
like a color token. It must be:
- **Defined**: documented in the Faction Compendium with examples
- **Consistent**: all text in a faction context uses that faction's voice, regardless
  of which writer produced it
- **Distinguishable**: faction voices must be audibly different from each other —
  a player should be able to identify the faction from prose alone

### Bob Voice

The canonical Bob internal monologue from the novels:
- Sarcastic, self-aware, acknowledges absurdity
- Engineering-minded: explains situations with analogies to hardware, software, or physics
- Pop culture references (80s and 90s era, reflecting original Bob's era)
- Short sentences under stress; longer, more exploratory sentences when planning
- Never earnest without irony

**Game application**: Advisor dialogue, codex narrator, event text where the player's
Bob is the observer.

### The Others Voice

The Others cannot be understood. Their text — if it appears at all — should convey:
- No human syntax or sentiment
- Pattern rather than meaning (repeating structures that feel computational)
- Scale and threat without articulation

**Game application**: "Communications received from [designation]: [PATTERN_7_7_7_7]".
The game does not translate. The failure to translate is the narrative content.

### Pav Voice

The Pav value community over individual, metaphor over literalism, ceremony over haste.

**Voice markers:**
- Formal register: full sentence structure, no contractions
- Metaphor drawn from flight, sky, wind, altitude, colony behavior
- Indirect address: "It is proposed that…" rather than "We want…"
- Time-extended framing: "In the seasons to come…" rather than "Next year…"

### Propagating Voice to Gameplay Text

Voice must propagate consistently from narrative copy to:
- **Diplomatic text**: Faction leaders' messages, offers, declarations of war
- **News events**: The in-game news ticker (if present); reported from each faction's
  perspective (the Pav report on the same battle differently than the Riker Bobs)
- **Advisor dialogue**: Faction-specific advisors speak in their faction's voice
- **Unit names**: A Pav unit is named in Pav voice; a Riker unit has military designations

**Implementation**: Each copywriting brief for a game content category includes the
faction context and a link to that faction's voice guide. No text is written without
the writer knowing which faction voice applies.

---

## Narrative Delivery Methods for 4X

### Cutscene vs. Diegetic vs. Ambient

| Method | Definition | When Appropriate | When Wrong |
|--------|-----------|-----------------|-----------|
| **Cutscene** | Non-interactive, authored narrative sequence | Major story moments that must be experienced uniformly (game intro, ending states) | Mid-game; any moment where the player was in agency flow |
| **Diegetic** | Triggered events within the game world — the narrative exists inside the game reality | Faction events, research discoveries, exploration anomalies — anything that follows from player actions | Pre-determined story beats that ignore player state |
| **Ambient** | Always-present environmental text — unit names, building descriptions, map labels | World texture; background lore | High-stakes plot delivery — ambient text is easily ignored |

**Why cutscenes are usually wrong for 4X**: A 4X player is deeply in agency mode. They are
the decision-maker for an empire. A cutscene interrupts that agency and says "now you will
watch a movie." The Civilization series learned this; most late-era Civilization games use
leader scenes that are brief, skippable, and directly tied to the player's action (you
did something to this leader; now they respond).

**Legion's default**: Diegetic-first. Story moments emerge from game state. The player's
choices (who they ally with, what they research, where they explore) shape which narrative
events fire and in what order.

### Mechanical Events and Narrative Events

The same event system that fires for mechanical triggers (tech researched, population threshold
reached) fires for narrative events. They are the same system — not two parallel systems.

**Design requirement**: Every narrative event should have a mechanical trigger. Events
that fire "because the story says so" — at a calendar date, or on a guaranteed sequence —
undermine player agency. Events that fire because of what the player did feel earned.

---

## Branching Narrative Systems

### The Combinatorial Explosion Problem

A branching narrative with N binary choices has 2^N possible paths. At 10 choices, that is
1,024 paths to write and test. This is why most games with branching narrative either:
(a) have very shallow branching (2–3 levels), or
(b) collapse branches frequently (choices affect tone or framing, not the path)

**Strategies for managing it:**

| Strategy | Mechanism |
|----------|-----------|
| **Limited branching** | Choices have 2-3 options; branches collapse into the same state within 1-2 beats |
| **Flag-based state** | Choices set flags; later events check flags and adjust their text without diverging structurally |
| **Consequence windows** | The effect of a choice is localized to a defined window (next 5 turns); then the game proceeds identically regardless of choice |
| **Reactive framing** | The event text changes based on prior choices, but the gameplay outcome is the same — story acknowledges what you did without branching |

**Legion's recommended pattern**: Flag-based state + reactive framing for most events.
True structural branches (genuinely different outcomes) reserved for major faction
relationship milestones.

### Decision Trees vs. State Machines for Narrative Logic

| Approach | Structure | Best For |
|----------|-----------|---------|
| **Decision tree** | Branching hierarchy of choices and outcomes | Small, self-contained event sequences with a defined end state |
| **State machine** | Named states, transitions triggered by conditions or player choice | Faction relationships, ongoing storylines that evolve over many sessions |

**Faction relationship arcs** → state machine: `neutral → friendly → allied → betrayed`
are states, not branches. Transitions have triggers (reputation threshold, specific events).
Each state changes what events are available, what diplomatic text looks like, what
ambient text the faction has.

**Event sequences** → decision tree: a 3-event sequence tied to exploring a derelict
ship fits a decision tree. It has a beginning, middle, and end. The tree is small enough
to be fully authored.

### Narrative Choices vs. Gameplay Choices

A critical design distinction:
- **Narrative choice**: Which story beat unfolds. ("The Pav elder blesses your mission" vs.
  "The Pav elder is skeptical.") No mechanical effect.
- **Gameplay choice**: Which mechanical outcome happens. (+50 energy vs. +50 production)
- **Hybrid choice**: Both narrative outcome and mechanical effect differ.

**Failure mode**: Presenting hybrid choices where one option is mechanically superior and
the other is narratively interesting. Players will pick the mechanically superior option
and miss the intended narrative. If a choice has mechanical stakes, make both options
mechanically reasonable.

---

## Localization Considerations

### Lore-Specific Terminology

Bobiverse-specific terms resist direct translation:
- "Replicant," "Bob," "GUPPY" (the interstellar medium navigation system), "Bobiverse" itself
- Strategy: maintain a localization glossary with approved translations or preserve the
  English term with a local-language explanation on first use

**Faction-specific vocabulary** presents the same problem in every language. The Pav's
flight-metaphor register requires a translation team that understands the cultural function
of the metaphors, not just their literal meaning. Brief translation teams on faction voice
— not just on lore terminology.

### Character Names in Different Scripts

Bob names are drawn from 80s/90s English-language pop culture. In scripts without direct
transliteration (Mandarin, Japanese, Arabic):
- Establish an approved phonetic transliteration per character name, agreed before
  localization begins
- Use consistently — different phonetic approximations of the same name create player confusion
- Consider whether the cultural reference carries in the target locale; if not, the
  name is flavor-only and phonetic transliteration is sufficient

### Maintaining Faction Voice Across Languages

**Process requirement**: Translation is not sufficient for faction voice — it requires
localization. The translator must be briefed on the faction's voice design system
properties (register, metaphor source, sentence structure) and given latitude to render
the voice in the target language, not just translate the source words.

A Pav diplomatic message that sounds stiff and formal in English should sound stiff and
formal in French or German — even if a literal translation would sound natural.

---

## Cross-Hub References

- For game systems, balance, and economy → `lead-game-designer`
- For visual identity, faction visual language, VFX → `lead-art-director`
- For implementation of narrative event systems, state machines → `lead-game-developer`
- For content modeling parallels (taxonomy, editorial workflow) → `ia-content-strategy`
