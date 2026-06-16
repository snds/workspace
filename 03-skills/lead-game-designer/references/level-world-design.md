# Level and World Design for Legion

Legion's spaces—from star systems to factory floors—communicate strategy, enable player agency, and pace exploration. This reference covers spatial design across all scales.

## Star System Layout Design

**Real Star Positions**

Legion uses real star systems from the Hipparcos catalog. The first playable region: Alpha Centauri, Sirius, Vega, Barnard's Star (12 light-year radius from Sol).

Real positions create authenticity and constraint. Player can't teleport. Travel takes time proportional to distance. Communication delays matter.

**Orbital Mechanics Design**

Each star has:
- Habitable zone (where planets orbit)
- Asteroid belts (mined for resources)
- Derelict zones (exploration points)

Orbital positions aren't random. They follow Kepler's laws:
- Closer orbits have faster periods (Mercury-like planets orbit faster than Earths)
- Asteroid belts lie at specific distance bands
- Gas giants stabilize inner planetary systems

Player learns orbital mechanics through experience: "If I mine the inner asteroid belt, travel time is short but resources are depleted faster. Outer belt takes longer but has more ore."

**Strategic Positioning**

Orbits create positional complexity:
- A planet in a tight orbit has short response times (good for military defense)
- A planet in a wide orbit has long transit times (good for peaceful research)
- An asteroid belt between two planets creates a natural bottleneck (strategic warfare chokepoint)

Playtesting validates: Do orbital positions create interesting strategic decisions? Or are they arbitrary?

## Planetary and Surface Design

**Planetary Types**

Each star has 2-4 planets (varies by star). Types:

| Type | Resources | Hazards | Buildable Area | Story |
|------|-----------|---------|---|-------|
| **Terrestrial** | Iron, Copper, Rare Earth | Radiation, dust storms | 40% of surface | Candidate for terraforming |
| **Ocean** | Rare Earth, Water (research) | Tidal forces, corrosion | 20% (islands) | Lost research stations |
| **Gas Giant** | Helium-3, Methane | Radiation belts | 0% (moons only) | Ancient megastructure nearby |
| **Ice Dwarf** | Water, Volatiles | Extreme cold | 10% (warm zones) | Derelict alien probe |

Diversity encourages exploration. No two planets identical.

**Resource Distribution**

Resources aren't evenly distributed. This creates player decisions:
- Planet A has abundant Iron but no Thorium. Player commits to specialized trade.
- Planet B has balanced resources but limited buildable area. Player invests in vertical expansion (stacked modules).
- Planet C has rare materials hidden deep. Mining requires deep drilling tech (late-game unlock).

Resource scarcity drives progression and expansion.

**Buildable Zones**

On each planet, designate zones:
- **Primary zone**: Easy access, good resources. Starter area.
- **Secondary zone**: Harder access, better resources. Unlocked via tech or discovery.
- **Restricted zone**: Anomaly or artifact. Exploring it triggers story event.

Zoning creates exploration progression. Early game: one zone. Mid-game: two zones. Late-game: full planet explorable.

## Factory Floor Layout

**Grid System**

Factory modules snap to a 4×4 grid. This allows:
- Clean alignment (no floating modules)
- Predictable footprints (2×2 smelter, 3×3 assembly, 1×4 conveyor)
- Efficient packing (player optimizes like Tetris)

**Input/Output Connections**

Modules connect via logical routing (no physical pipes drawn):
- Mining output → Smelter input (direct connection)
- Smelter output → Assembly input (player chooses routing manually)
- Assembly output → Storage or export (player decides destination)

Visual feedback: Connection lines glow when active, pulse when backed up (bottleneck).

**Optimization Levers**

Player can optimize factory layout for:
1. **Throughput**: Minimize hops between modules (fewer routing delays)
2. **Energy efficiency**: Minimize distance (transmission loss scales with distance)
3. **Scalability**: Leave room for expansion (don't pack too tightly)
4. **Aesthetics**: Make it look good (modules arranged in patterns)

All four are valid. Playtesting ensures no single approach dominates.

**Expansion Paths**

Factory zones expand as player researches:
- Tier 1: 30×30 grid (starting zone)
- Tier 2: +10×10 zone adjacently placed (adjacent expansion only)
- Tier 3: Second disconnected factory site (linked via supply ship, costly)

Expansion creates long-term planning decisions. Where should the second factory be? (Same planet for efficiency, or new planet for diversity?)

## Strategic Terrain for RTS Combat

**Orbital Combat Arena**

Combat occurs in 2D orbital space (top-down view). Terrain:
- **Asteroids**: Provide cover. Can hide units. Can't move through (obstacles).
- **Nebulae**: Reduce vision range and weapon accuracy. Tactical hiding spots.
- **Energy anomalies**: Deal damage to units passing through. Create hazards.

Terrain forces positional play. Hiding behind asteroids is viable. Charging straight wins fights but takes damage.

**Chokepoints**

Design arenas with bottlenecks:
- Asteroid belt between two planets (only passage: narrow corridor)
- Nebula field with one clear lane
- Planet's magnetic field blocking direct route (units must go around)

Chokepoints create defensive positions. A smaller force can hold a chokepoint against larger numbers (if positioned well).

**Cover and Elevation**

Legion is 2D (top-down), so elevation is abstracted. Use cover tiers instead:
- Light cover: Halves incoming damage (small asteroid)
- Heavy cover: Blocks line of sight (large asteroid or nebula edge)
- Destructible cover: Explodes when hit, damages units behind it

Positional tactics emerge: "Do I destroy that asteroid (friendly fire risk) or maneuver around it?"

**Combat Scaling**

Arena sizes scale with unit counts:
- Small skirmish (10 units): 1000×1000 AU arena
- Medium battle (50 units): 2000×2000 AU arena
- Large war (200+ units): 4000×4000 AU arena

Larger arenas allow more maneuvering. Smaller arenas force decisive engagement.

## Pacing Through Space

**Discovery Moments**

Design sequences to create emotional peaks:

1. **Arrival** (10 min play): Jump to new star system. Reveal overview. "I'm alone in a new place."
2. **Exploration** (20 min): Discover planets and anomalies. "What's here?"
3. **Foundation** (30 min): Build first factory. "I'm taking root."
4. **Threat** (40 min): First alien contact or environmental hazard. "I'm not safe."
5. **Expansion** (60 min): Second star system or major tech unlock. "I'm growing."

This pacing loop repeats. Each star system follows similar beats, but with unique content (different planets, different factions, different story hooks).

**Tension and Release**

Sequence challenges and relief:

```
Early game (first 2 hours):
- 30 min: Safe mining → 10 min: First combat threat → 15 min: Tech unlock (relief) → 30 min: Second planet discovery → repeat

Mid game (5-20 hours):
- 30 min: Multi-system optimization → 20 min: Diplomatic crisis → 10 min: Alliance formed (relief) → 60 min: New megastructure discovered (mystery) → 20 min: Combat response → repeat
```

Balance: Too many threats = burnout. Too much safety = boredom. Playtesting calibrates rhythm.

**Points of Interest Density**

Not all space is equally interesting. Design density curves:

- **Core zone** (near starting planet): High density. Faction cities, mining operations, anomalies every 1-2 light-years.
- **Frontier** (3-5 light-years out): Medium density. Derelicts, scientific wonders, sparse faction presence.
- **Deep space** (10+ light-years out): Low density. Alien megastructures, ancient artifacts, vast empty stretches punctuated by discoveries.

Early game: Player stays in core. Mid-game: Reaches frontier. Late-game: Ventures into deep space.

Density progression paces exploration. Players don't feel overwhelmed early, bored mid, or lost late.

## Procedural Generation Constraints

**What to Proceduralize**

Good candidates for procedural generation:
- **Star positions**: Use Hipparcos catalog (not random)
- **Planet types**: Distribution varies (not always Terrestrial, Ocean, Gas giant, Ice)
- **Resource amounts**: Randomize within bounds (not uniform)
- **Anomaly locations**: Spawn randomly on planets (not hand-placed everywhere)

Procedural generation creates replayability and surprise.

**What to Hand-Craft**

Hand-craft these for narrative coherence:
- **Derelicts and artifacts**: Each tells a story. Can't be generic. Requires authored content.
- **Faction territory**: Must align with faction lore. Collective in inner systems, Hegemony in outer, Architects scattered.
- **Environmental storytelling**: "Why is this asteroid field here?" Needs cause (ancient collision, debris from destroyed station). Procedurally generated fields feel meaningless.
- **Story-critical locations**: First planet, first derelict, first faction contact. These are authored.

**Hybrid Approach**

Proceduralize the substrate (star positions, resource amounts, anomaly spawns). Hand-craft the content (story locations, faction territories, unique landmarks).

This gives players infinite space to explore (procedural) with narrative coherence (hand-crafted story nodes).

## Scale and Navigation

**Distance Representation**

Legion's distances are vast. Design representation:
- **Zoomed-in view** (factory floor): 4×4 grid, meters/kilometers scale
- **Planet view** (surface): 100×100 km scale
- **System view** (orbits): Millions of kilometers scale
- **Galactic view** (star to star): Light-years scale

Smooth camera zoom between views. No jarring transitions.

**Travel Time**

Real travel times at realistic speeds:
- Exploring a planet surface: 30 min-1 hour of play
- Traveling between planets in a system: 2-4 hours of play
- Traveling between star systems: 10-20 hours of play (or can queue auto-pilot, play other systems while traveling)

Long travel times create narrative opportunities. Clone isolated for 10 hours develops personality drift. Communicate back to Prime (pay Energy), or let the drift happen.

## Environmental Storytelling Framework

**Derelict Design**

Each derelict should tell a story through its state:
- **Intact but dark**: No power. Mystery. (Player must power it to access logs)
- **Breached**: Obvious damage. Someone attacked it. (Story: faction warfare)
- **Overgrown**: Organic life inside. Ancient structure. (Story: pre-human civilization)

Logs inside are written. Not procedurally generated. "Captain's log, Day 47: The radiation levels are spiking. I believe the Architects are waking." This is better than "Unknown situation detected."

**Anomalies as Questions**

Instead of "anomaly here—take your reward," design anomalies as mysteries:
- A perfectly spherical void in space (what removed that much matter?)
- A signal repeating an unknown language (who sent it? how long ago?)
- A graveyard of wrecks orbiting a planet (what happened here?)

Players investigate or speculate. Stories emerge.

**Progression Through Space**

Early planets: Simple biomes, light lore.
Mid planets: Complex biomes, deeper stories (hints of ancient conflict).
Late planets: Enigmatic structures, mysteries unsolved (player's actions affect them).

Space becomes a story experience when designed intentionally.
