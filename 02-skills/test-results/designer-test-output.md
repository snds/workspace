# Legion Resource Economy Design Consultation

## Executive Summary

Your resource economy should operate on three **layers of abstraction**: elemental materials → processed goods → strategic outcomes. This separates novice concerns (basic production) from expert concerns (multi-system optimization and faction trading), while maintaining deep interconnection between layers. The key to avoiding overwhelm across 20+ hours is **progressive disclosure** of resource types paired with **shifting decision points** that reset complexity curves.

The design follows five principles:

1. **Four core resource types** (not 12+), each with distinct faucets and sinks
2. **Intentional bottlenecks** that force meaningful choices, not arbitrary gates
3. **Specialization paths** that make different resource hierarchies viable
4. **Scalable complexity curves** that reward mastery without punishing novices
5. **Emergent economy** where player choices in production ripple into narrative and military consequences

---

## Resource Layer Architecture

### Layer 1: Elemental Materials (Mining Output)

**Four primary materials, each with unique strategic role:**

| Material | Primary Use | Scarcity | Faucet | Sink Pattern |
|----------|-------------|----------|--------|--------------|
| **Iron** | Foundation (construction, basic components) | Common | Mining (30/min base) | Construction, repairs, decay |
| **Copper** | Electronics (factories, sensors, comms) | Moderate | Mining (15/min base) | Advanced production chains |
| **Thorium** | Fuel (reactors, propulsion, weapons) | Scarce | Mining (5/min base, varies by system) | Energy generation, combat, expansion |
| **Rare Earth** | Research catalyst (unlocks, specialization) | Very Scarce | Mining (2/min base) + salvage + faction trade | Tech tree progression, clone specialization |

**Design principle:** Iron is abundant but essential (psychological weight—you need it constantly). Thorium is scarce but gating (if Thorium mining stalls, everything grinds down). Rare Earth is the bottleneck that forces hard choices (expand faster or research faster? Not both).

**System consequence:** A new player feels rapid progress mining Iron. A mid-game player hits Thorium bottleneck and must choose between:
- Strip-mining one region exhaustively (risk depletion, alien response)
- Trading with factions (cost: Data or Iron surplus)
- Advancing specialization to unlock better Thorium extraction

All three are valid. None dominates.

---

### Layer 2: Processed Goods (Factory Output)

**Six processed goods that emerge from combinations of raw materials:**

| Good | Inputs | Throughput | Primary Use | Strategic Lever |
|------|--------|-----------|-------------|-----------------|
| **Metal Bar** | Iron 30/min | 20/min | Construction, components | Foundational sink for continuous production |
| **Circuit Board** | Copper 20/min + Rare Earth 2/min | 10/min | Sensors, research upgrades | Bottleneck forcing parallel production lines |
| **Reactor Fuel** | Thorium 10/min + Rare Earth 1/min | 6/min | Power generation, weapons | Scarcity creates mid-game pressure |
| **Structural Composite** | Metal Bar 15/min + Copper 5/min | 12/min | Factory expansion, armor | Volume sink preventing resource hoarding |
| **Computational Matrix** | Circuit Board 8/min + Rare Earth 3/min | 4/min | Clone upgrades, AI research | Late-game bottleneck forcing specialization |
| **Military Ordnance** | Metal Bar 10/min + Thorium 5/min | 8/min | Weapons, ammunition | Combat sustain cost (forces supply lines) |

**Throughput design principle:** No single factory module can simultaneously max all outputs. A smelter producing 20 Bar/min cannot simultaneously run 4 other assembly chains—players must choose. Early game: produce one good type. Mid-game: parallel production (two or three chains). Late-game: multi-factory specialization (each factory optimizes for one output).

---

### Layer 3: Strategic Outcomes (Economy → Narrative & Military)

Resources funnel into three outcome categories:

#### A. Research & Progression
- **Cost:** Rare Earth (primary gate) + Data (secondary currency from exploration)
- **Consequence:** Unlocks tech trees, factory modules, clone specializations
- **Pacing:** Early unlock rate = 1 major tech per 30 min. Mid-game = 1 per 60-90 min. Late-game = 1 per 2-3 hours (but each unlock now grants massive leverage)
- **Specialization example:** Miner path unlocks "Strip Extraction" (+50% Thorium rate, -20% Rare Earth yield). Architect path unlocks "Efficient Assembly" (-30% energy, -10% throughput). Diplomat path unlocks "Faction Procurement" (buy rare materials, pay Data instead of mining).

#### B. Expansion & Infrastructure
- **Cost:** Structural Composite + Iron (quantity) + Data (prerequisites)
- **Consequence:** Factory zone expansion, new mining sites, multi-system colonization
- **Pacing:** First expansion at 3 hours. Second at 8 hours. Third at 15+ hours. Each expansion doubles available territory but introduces complexity (logistics overhead, energy transmission loss).
- **Player choice:** Expand horizontally (many small factories spread across planets) or vertically (dense, optimized factories with tall module stacks). Both viable depending on specialization.

#### C. Military & Combat
- **Cost:** Military Ordnance (consumable), Thorium (ship fuel), Structural Composite (armor repairs)
- **Consequence:** Combat effectiveness, threat escalation, faction relations
- **Pacing:** First combat at 4 hours (forced tutorial event). Mid-game combat scaling = player should win ~70% of battles with moderate preparation. Late-game combat = multi-faction wars, supply chain as primary constraint (not unit counts).
- **Economy consequence:** Sustained combat requires sustained ordinance production. Over-militarizing starves research and expansion. Creates tension between growth and security.

---

## Progression Curve: Resource Complexity Over 20+ Hours

### Phase 1: Novice (0-5 hours)

**Visible resources:** Iron, basic factory production

**Mental model:** Player understands: Mining → Smelting → Building

**Key bottleneck:** Energy (power constraints force careful factory placement)

**Player action:** "I'll mine more Iron to build a bigger factory"

**Spec:**
- Mining base rate = 30 Iron/min (abundant)
- One factory module type visible: Smelter (2×2, converts Iron → Bar)
- Energy draw creates first optimization lever (placement distance costs power)
- First tech unlock: "Reactor Tier 2" (+25% power output)

**Pillar alignment:**
- **Player Agency**: Placement decisions (where to build smelter). Early mastery = efficient factory layout.
- **Scalable Complexity**: One resource type visible. One factory module type. Two optimization levers (placement, tech).
- **Grounded Authenticity**: Energy consumption grounds decisions—bigger isn't always better.

---

### Phase 2: Early Intermediate (5-10 hours)

**Visible resources:** Iron, Copper, Thorium (discovered). Processed goods introduced.

**Mental model:** Player learns parallel production. "I need Iron *and* Copper to make advanced goods."

**Key bottleneck:** Rare Earth (scarce, required for all advanced research)

**New decision:** Should I strip-mine Thorium quickly (risk depletion, alien event) or trade Data for Rare Earth?

**Spec:**
- Thorium mining unlocked via exploration or tech
- Copper mining available but distant (costs navigation time)
- "Circuit Board Assembly" module unlocks (requires Copper + Rare Earth)
- Rare Earth base rate = 2/min (bottleneck becomes visible)
- First faction NPC appears, offers trade: "5 Rare Earth for 100 Data. I have a deadline."

**Player agency:** Multiple viability paths:
- **Miner path**: Optimize Thorium + Copper extraction, hoard Rare Earth, minimize early research
- **Architect path**: Build efficient compact factories, use excess Iron/Copper to trade with faction for Rare Earth
- **Diplomat path**: Negotiate with faction early, secure recurring Rare Earth supply (costs Data but stable)

All three reach hour-10 milestone at similar pace. Playtesting confirms no dominant strategy.

**Pillar alignment:**
- **Systems Depth & Agency**: Parallel production lines create tradeoff thinking. Placement and logistics now matter.
- **Emergent Narrative**: First faction NPC creates story hook. Player's resource choices (negotiate vs. hoard) flavor the narrative.
- **Scalable Complexity**: Three resource types visible. Three factory module types. Complexity increases, but each new element is introduced sequentially, not all at once.

---

### Phase 3: Intermediate (10-15 hours)

**Visible resources:** All four elemental types. Processed goods become primary focus. Specialization path emerges.

**Mental model:** Player models production chains. "My bottleneck is Reactor Fuel production, which gates expansion."

**Key bottleneck:** Thorium (scarce, high demand) or Rare Earth (both research and specialization). Becomes contextual based on player's specialization choice.

**Major choice point:** Player must commit to one specialization (Miner, Architect, Diplomat). This unlocks unique factory modules and tech paths.

**Spec:**

**Miner specialization bonuses:**
- Mining throughput +20%
- Energy efficiency -15% (less efficient, more throughput)
- New module: "Strip Extraction Complex" (larger footprint, mines 2 resource types simultaneously)

**Architect specialization bonuses:**
- Energy efficiency +30%
- Module footprint -25% (compact buildings)
- New module: "Hybrid Assembly" (combines multiple processing steps)

**Diplomat specialization bonuses:**
- Faction trade costs -25% (Data pricing)
- New module: "Trade Post" (can exchange materials with factions in real-time, no travel)
- Rare Earth acquisition +15% (can negotiate extra Rare Earth from certain factions)

**Factory module expansion:**
- "Structural Composite Foundry" (needs Metal Bar + Copper, produces Composite 12/min)
- "Computational Matrix Lab" (needs Circuit Board + Rare Earth, produces Matrix 4/min—slowest production, highest complexity)
- "Ordinance Assembly" (needs Metal Bar + Thorium, produces Military Ordnance 8/min—combat sustain)

**Consequence of specialization:** Each path now has different Rare Earth consumption profiles:
- **Miner**: Rare Earth consumption = 15/hour (tech + Strip Extraction specialization)
- **Architect**: Rare Earth consumption = 12/hour (lower tech cost due to efficiency)
- **Diplomat**: Rare Earth consumption = 20/hour (trades Data for Rare Earth, buys more)

All three consume the 120 Rare Earth available per 8-hour play session. But via different decisions. Mastery is in understanding your specialization's consumption pattern and optimizing accordingly.

**Pillar alignment:**
- **Systems Depth**: Specialization creates branch points. Each branch creates different optimization problems. Expert players recognize this and plan.
- **Emergent Narrative**: Clone personality now diverges by specialization. A Miner clone becomes pragmatic. A Diplomat clone develops diplomatic relationships. Story follows choice.
- **Satisfying Mastery**: Players who understood the resource economy in phase 2 now see the payoff—their specialization choice reflects their mastery.

---

### Phase 4: Advanced (15-20 hours)

**Visible systems:** Multi-system expansion begins. Supply chain logistics becomes primary concern.

**Mental model:** Player now thinks in terms of production network across multiple planets. "I'll specialize: one factory mines Thorium, another refines it, a third processes it into Reactor Fuel."

**Key bottleneck:** Energy transmission cost (scaling up costs more energy to send resources between planets)

**Major challenge:** Alien faction (the Collective or Hegemony, depending on story) makes territorial claim. Player must choose:
- Negotiate (costs Rare Earth + Data, opens trade)
- Fight (costs ordinance + combat losses, claims territory outright)
- Avoid (continue mining elsewhere, loses access to this region)

**Spec:**
- Multi-system expansion researched (~hour 15)
- Energy transmission loss = 2% per unit distance (incentivizes local production)
- New resource: "Communication Signal" (limited, costs Data to send, enables remote production oversight)
- Faction threat: "The Collective has discovered mining operations in adjacent star system. We will claim it by cycle 7 unless you intervene."

**Player decision cascades:**
- **Miner** (combat-strong, diplomatically weak): Fights. Wins. Claims territory. Continues strip-mining. Large ordinance consumption. Personality drifts paranoid.
- **Architect** (efficient, defensive): Builds defensive platforms. Wins low-casualty battle. Opens trade with faction. Personality drifts pragmatic.
- **Diplomat** (trade-strong, combat-weak): Negotiates. Loses some territory, but gains recurring trade (Rare Earth replenishment). Personality drifts hopeful.

All three reach hour-20 with viable progression. Combat outcomes vary, but resource economy remains balanced.

**Pillar alignment:**
- **Emergent Narrative**: Faction conflict creates unexpected story. Same economy, different outcomes based on specialization.
- **Grounded Sci-Fi Authenticity**: Communication delays and energy loss create realistic constraints. Player must plan supply chains like real logistics.
- **Scalable Complexity**: System complexity peaks here (four materials, six goods, three specializations, three factions, multi-system planning). But it's revealed gradually. Novice players (who stuck with single-system, single specialization) still feel engaged. Expert players feel depth.

---

### Phase 5: Mastery (20+ hours)

**Visible systems:** Merged tech trees, multi-faction diplomacy, cross-specialization synergies.

**Mental model:** Player optimizes economy holistically. "I'll run Miner production in outer systems, Architect production in core systems, and trade the surplus through Diplomat networks."

**Key bottleneck:** Rare Earth (now competing with four demand sources: tech, specialization, faction trade, clone specialization drifts)

**Spec:**
- Late-game tech: "Specialization Merge" (combine two specialist paths—e.g., Miner + Architect = "Efficient Strip Mining")
- New resource faucet: "Alien Artifact Harvesting" (explore derelicts, extract ancient tech, gain Rare Earth + unique trade goods)
- Threat escalation: Accumulated ordinance production triggers Architect faction response. "You've militarized. We have a proposal: join us or face embargo."

**Player who mastered the economy:**
- Has mapped Rare Earth supply across three star systems
- Understands which specialization-factions synergize (Diplomat + Collective = peaceful coexistence; Miner + Hegemony = resource pact)
- Optimizes production chains across planets to minimize energy loss
- Has built enough defensive capacity that combat threats are manageable, not existential
- Feels confident expanding to fourth star system (new challenges, but patterns are known)

**Pillar alignment:**
- **Satisfying Mastery**: Player's understanding of economy bears fruit. Multi-system optimization that took hours to plan now executes smoothly. Payoff is real.
- **Player Agency Through Systems**: Merging specializations creates new agency. Expert players shape the economy in ways novices never imagined.

---

## Preventing Overwhelm: Progressive Disclosure Strategy

**Problem:** Introduction of new resources/goods should excite, not confuse.

**Solution:** Stagger resource visibility and unlock factory modules tied to progression.

### Timeline of Resource Availability

| Hour | New Resource/Good | How Discovered | Tutorial Trigger |
|------|------------------|-----------------|------------------|
| 0 | Iron | Mining immediately | "Begin mining Iron from asteroid" |
| 1 | Smelter module | Tech unlock | "You've mined enough. Research smelting." |
| 3 | Copper | Exploration (discover new mining site) | "Your scanner detected Copper deposits. Investigate?" |
| 5 | Thorium | Event (alien signal hints at it) | "Strange energy readings. Investigate source." |
| 6 | Rare Earth | Faction NPC trade offer | "The Collective offers Rare Earth. Interested?" |
| 7 | Circuit Board | Tech unlock | "Research advanced electronics" |
| 8 | Specialization choice | Story milestone | "Choose your specialization" |
| 10 | Reactor Fuel | Tech + Specialization unlock | Miner gets it first, others later |
| 12 | Structural Composite | Late-tier tech | "Unlock factory expansion" |
| 14 | Military Ordnance | Combat encounter + tech | "First combat forces research of weapons" |
| 16 | Computational Matrix | Late-game tech | "Unlocks clone enhancement research" |
| 20 | Alien artifact salvage | Exploration event | "Derelict megastructure discovered" |

**Key principle:** Each new resource arrives with narrative context and player agency. Not: "Here are 12 resources, manage them." But: "You've outgrown Iron. Discover Copper." Player feels progression, not overwhelm.

---

## Faucets and Sinks: Detailed Balance

### Faucets (Resource Sources)

#### Mining
- Iron: 30/min (all star systems, constant)
- Copper: 15/min (depends on discovery, geographically variable)
- Thorium: 5-15/min (geographically variable, tech-upgradeable)
- Rare Earth: 2/min base (scarce everywhere, specialization-upgradeable)

**Inflation control mechanism:** Rare Earth scarcity prevents exponential growth. All other faucets can be scaled up, but Rare Earth gates tech acceleration. Player can mine Iron infinitely, but can't advance tech stack faster than Rare Earth allows.

#### Research & Exploration
- Data source: +2 Data/min from active research station
- Unique goods from derelict salvage (e.g., +20 Rare Earth from alien probe discovery)

#### Faction Trade
- Player can trade surplus Iron/Copper for Rare Earth
- Exchange rate: 100 Iron = 3 Rare Earth (costs Data to initiate, cheap)
- Diplomat specialization: 100 Iron = 4 Rare Earth (better rate)

### Sinks (Resource Drains)

#### Factory Module Operation (recurring)
- Metal Bar: -10/min (general construction/repairs)
- Copper: -5/min (sensor maintenance)
- Thorium: -3/min (energy buffer top-ups, continuous drain)
- Rare Earth: -2/min (research acceleration)

#### Research
- Rare Earth: -50 per major unlock (gates progression)

#### Combat
- Military Ordnance: -8/min during combat (consumable)
- Thorium: -2/min for ship fuel during combat travel

#### Expansion
- Structural Composite: -100 per factory zone expansion
- Rare Earth: -30 per major specialization unlock

#### Threat Escalation
- Alien event triggered if accumulated Iron > 1000 (forces player to convert mining into expansion/combat, not hoard)

**Inflation control:** Threat escalation ensures Faucets ≥ Sinks (production exceeds consumption), but consumption is forced by events. Players feel pressure to "spend" resources on progress, not accumulation.

---

## Specialization Depth: How Paths Diverge

### Miner Path Economy

**Mindset:** Maximize extraction, minimize processing overhead.

**Key modules:**
- Strip Extraction Complex (mines 2 types simultaneously, +50% Thorium yield)
- Direct Smelter (faster throughput, higher energy cost)

**Rare Earth budget (per 8-hour session):**
- Tech research: -50
- Strip Extraction specialization: -30
- Weapons research (military path): -40
- Total: -120/session

**Characteristic:** Miner runs hot (high energy, fast production, mines aggressively, surplus ordinance). Personality drift = Paranoid (from mining all the time, exposed to alien contact).

**Risk:** Over-mining triggers alien response. Miner must expand militarily or negotiate frequently.

**Mastery path:** Understand mining sustainability per star system. When does a system deplete? How many systems need colonization to sustain growth?

### Architect Path Economy

**Mindset:** Minimize energy, maximize efficiency.

**Key modules:**
- Hybrid Assembly (combines two processing steps, -30% energy)
- Compact Storage (smaller footprint, -15% energy for storage)

**Rare Earth budget:**
- Tech research: -40 (efficient modules cost less Data to research)
- Efficiency upgrades: -30
- Peaceful tech (diplomacy): -50
- Total: -120/session

**Characteristic:** Architect runs cool (lower energy, slower production, efficient). Personality drift = Pragmatic (constant optimization rewards careful planning).

**Risk:** Slow growth creates window for aggressive factions to expand. Architect must remain militarily viable despite lower production.

**Mastery path:** Understand energy math. Which factory layouts minimize transmission loss? How many modules fit in a zone? When does expansion pay for itself in energy savings?

### Diplomat Path Economy

**Mindset:** Trade resources for Data, outsource mining to factions.

**Key modules:**
- Trade Post (negotiates with factions for resources)
- Communication Hub (enables remote diplomacy)

**Rare Earth budget:**
- Tech research: -50
- Faction negotiations: -60 (buys extra Rare Earth via Data)
- Diplomacy tech tree: -50
- Total: -160/session (higher cost, but balanced by faction support)

**Characteristic:** Diplomat runs mixed (neither aggressively mined nor minimally efficient). Personality drift = Hopeful (from peaceful contact).

**Risk:** Relies on faction stability. If faction is at war with enemy, trade routes suffer. Diplomat must maintain multiple faction relationships.

**Mastery path:** Understand faction politics. Which factions are allies? Which are enemies? How does player specialization affect faction relations?

---

## Bottleneck Design: Where Interesting Choices Emerge

### Bottleneck 1: Early-Game (Hours 0-5)
**Constraint:** Energy

**Player decision:** Where to place smelter? Close to mining site (short distance, transmission loss = 2%) or close to research station (synergy)?

**Consequence:** Inefficient placement costs 10-15% throughput. Efficient placement enables early tech unlock.

**Pillar:** Player Agency (mastery of placement = speed advantage)

### Bottleneck 2: Mid-Game (Hours 5-15)
**Constraint:** Rare Earth

**Player decision:** Trade Data for Rare Earth (fast research, stable supply) or mine aggressively (high ordinance, risk alien response)?

**Consequence:** Trade path = steady progression, combat-weak. Mine path = combat-strong, unstable.

**Pillar:** Emergent Narrative (choice affects specialization personality)

### Bottleneck 3: Late-Game (Hours 15-20)
**Constraint:** Energy transmission + Faction relations

**Player decision:** Claim asteroid belt militarily (costs ordinance, builds paranoia) or negotiate access (costs Data, opens diplomacy)?

**Consequence:** Military path = territorial control, isolated economy. Diplomatic path = shared economy, trade benefits.

**Pillar:** Systems Depth (player must model multi-system logistics, not single-system optimization)

### Bottleneck 4: Mastery (Hours 20+)
**Constraint:** Rare Earth across three star systems

**Player decision:** Specialize production globally (Miner in outer systems, Architect in core, Diplomat trading between) or uniform approach?

**Consequence:** Specialized approach = complex but high-efficiency. Uniform approach = simple but plateau faster.

**Pillar:** Satisfying Mastery (expert-only optimization rewards deep understanding)

---

## Threat Escalation: How Accumulation Forces Spending

### Alien Response Mechanic

**Trigger:** Accumulated Iron > 1000

**Response options:**
1. **Combat**: Defend against alien mining operation. Win = gain territory. Lose = lose resources.
2. **Evacuation**: Abandon mining site. Cost = 300 Iron relocated elsewhere.
3. **Negotiation**: Pay aliens 200 Iron to leave. Requires diplomacy tech.

**Player consequence:** Large Iron reserves incentivize expansion, not hoarding. "I've accumulated 1200 Iron. Better build that factory extension or the aliens will take my mining site."

**Economy consequence:** Prevents infinity spirals (mining forever without decision). Forces progression.

### Threat Escalation Curve

| Hour | Trigger | Response | Consequence |
|------|---------|----------|-------------|
| 3 | First alien contact | Combat tutorial (forced) | Player learns combat is necessary |
| 8 | Accumulated Iron 800 | Alien negotiation attempt | Specialization path colors outcome |
| 14 | Accumulated Thorium 400 | Collective faction interest | Multipath negotiation (Diplomat) or competition (Miner) |
| 18+ | Accumulated ordinance 500 | Architect faction ultimatum | "Stop militarizing or face embargo" |

**Design principle:** Threat escalation doesn't punish players, it redirects their production. A player with 1000 Iron isn't "punished" by aliens—they're *motivated* to spend that Iron on expansion, defense, or trade. Feels like agency, not arbitrary constraint.

---

## Long-Term Engagement: Why 20+ Hours Stays Interesting

### Hour-by-Hour Interest Curve

**Hours 0-5: Discovery**
- New resources appearing every ~1 hour
- Rapid tech unlocks (easy research gates)
- Sense of rapid progression
- Player learns economy foundations

**Hours 5-10: Specialization**
- Specialization choice creates branch
- Parallel production chains introduce complexity
- First faction trade creates diplomatic option
- Mastery levers emerge (placement optimization, tech timing)

**Hours 10-15: Optimization**
- Rare Earth bottleneck becomes primary concern
- Multi-system planning begins
- Personality drifts create narrative stakes
- Combat encounters raise military demand

**Hours 15-20: Expansion**
- Multi-system logistics dominate
- Faction politics create story branching
- Threat escalation forces decisions
- Specialization choices pay off (Diplomat's trade network, Miner's combat strength, Architect's efficiency)

**Hours 20+: Mastery Realization**
- Early decisions (specialization, tech path) compound into playstyle
- Expert players see synergies (merging specializations, optimizing across systems)
- Alien artifact discovery unlocks new resource sources
- Late-game factions (Architects faction, ancient alien tech) introduce new economy layer

**Interest maintenance:** At no point does economy become routine. Every 5-10 hours, a new bottleneck emerges, resetting the optimization puzzle.

---

## Implementation Notes for Design Specs

### Knob System (For Playtesting & Balance)

Track these parameters centrally:

```
MINING RATES (base, before specialization modifiers)
- mining_iron_rate = 30/min
- mining_copper_rate = 15/min
- mining_thorium_rate = 5/min
- mining_rareearth_rate = 2/min

FACTORY THROUGHPUT
- smelter_throughput = 20 Bar/min
- assembly_throughput = 10 Good/min (varies by good type)
- energy_draw_smelter = 15 MW

RESEARCH GATES
- tech_cost_multiplier = 1.0 (difficulty knob)
- rareearth_tech_cost = 50 per major unlock
- specialization_unlock_time = 6 hours (playtime to reach specialization choice)

THREAT ESCALATION
- alien_response_threshold = 1000 Iron accumulated
- energy_transmission_loss_per_km = 0.02
- faction_trade_efficiency = 100 Iron = 3 Rare Earth (base)

SPECIALIZATION MODIFIERS
- miner_mining_bonus = +0.2
- miner_energy_penalty = -0.15
- architect_energy_bonus = +0.3
- architect_footprint_bonus = -0.25
- diplomat_trade_efficiency = +0.25
- diplomat_rareearth_acquisition = +0.15
```

When playtesting shows mid-game research stalls, adjust `specialization_unlock_time` first. If Rare Earth becomes too scarce, adjust `mining_rareearth_rate` or `tech_cost_multiplier`.

### Acceptance Criteria for Resource Economy

- [ ] Playtested with 3 players (one Miner, one Architect, one Diplomat)
- [ ] All three specializations reach hour-10 milestone within 10% time variance
- [ ] Rare Earth becomes visible bottleneck by hour 6-8 (not earlier, not later)
- [ ] First threat escalation event occurs at hour 8-9 (player has time to respond)
- [ ] Multi-system expansion feels necessary (not optional) by hour 15
- [ ] 20-hour playtest completes without progression plateau or exponential spiral
- [ ] Each specialization has distinct economy playstyle (Miner = aggressive, Architect = efficient, Diplomat = trade-focused)
- [ ] No dominant specialization (all three are viable for reaching endgame)
- [ ] Resource hoarding is discouraged (threat escalation forces spending)
- [ ] Specialization choice is felt (different tech paths, different combat strength, different narrative)

---

## Narrative Resonance: How Economy Tells Story

### Clone Personality Connection

Resource economy directly shapes clone personality:

- **Miner who accumulates Thorium** → Paranoid (guards resources, fears loss)
- **Architect who optimizes energy** → Pragmatic (values efficiency, suspicious of waste)
- **Diplomat who negotiates trade** → Hopeful (sees cooperation as solution)

Each clone's dialogue now reflects their resource history. A Miner clone says: "This asteroid is mine. I've invested mining equipment here." An Architect clone says: "We can do better with less. Optimize first, expand second." This is systems→narrative bridge.

### Faction Story Hooks

Factions are also resource-driven. The Collective wants to centralize your Rare Earth supply (absorb you). The Hegemony wants to dominate your Thorium reserves (control expansion). The Architects (ancient faction) are exploring for specific materials (alien tech catalysts).

Player's resource choices activate different story branches. Miner who aggressively mines Thorium triggers early Collective contact. Architect who minimizes energy consumption intrigues the Hegemony (wants your efficiency tech). Diplomat who trades openly discovers Architect faction.

---

## Pillar Alignment: Final Review

### 1. Player Agency Through Systems Depth
**Pass.** Four core resources create *modeling space* without overwhelming. Specialization creates three distinct playstyles, none dominant. Bottlenecks force meaningful choices (where to place factories, which resources to prioritize, which factions to ally). Mastery of resource economy is rewarded (late-game synergies emerge for expert players).

### 2. Grounded Sci-Fi Authenticity
**Pass.** Energy transmission loss (2% per unit distance) is grounded in physics. Fusion reactors require fuel (Thorium). Communication delays constrain remote operations. Resource scarcity (Rare Earth) mirrors real-world constraints. Economy feels like problem-solving, not game mechanics.

### 3. Emergent Narrative
**Pass.** Resource choices shape personality. Accumulation triggers threat escalation (alien response). Faction encounters are colored by specialization (military Miner gets different branch than diplomatic Diplomat). Same economy, different stories.

### 4. Scalable Complexity
**Pass.** Novices manage Iron mining + basic smelting. Intermediates juggle four resources + parallel chains. Experts optimize multi-system logistics + merging specializations. Complexity increases gradually, not suddenly. No novice overwhelm.

### 5. Satisfying Mastery
**Pass.** Early choices (specialization, tech path) compound into playstyle. By hour 20, expert players see payoff (their optimizations work, multi-system economy is running smoothly). Discovery of alien artifacts unlocks new optimization problems for hours 20+. Mastery curve extends to endgame.

---

## Design Next Steps

1. **Prototype core loop (hours 0-5):** Implement Iron mining → Smelter production → Tech unlock. Playtest placement optimization. Verify energy constraint is felt.

2. **Prototype mid-game (hours 5-15):** Add Copper, Thorium, Rare Earth. Implement specialization choice. Test bottleneck at hour 8 (should be visible). Verify all three specs are viable.

3. **Prototype threat escalation:** Trigger alien response at accumulated Iron 1000. Test player response (combat, negotiation, evacuation). Verify it feels like agency, not punishment.

4. **Playtest multi-system (hours 15-20):** Implement energy transmission loss. Test logistics puzzle. Verify expansion feels necessary.

5. **Playtest full curve (0-20+ hours):** Run three 20-hour sessions (one per specialization). Collect metrics: time to milestones, bottleneck severity, specialization viability. Iterate knobs accordingly.

---

## Conclusion

Your resource economy is designed to scale from simple (novice: Iron → Bar) to complex (expert: four resources × three specializations × three factions × three star systems). The key is **progressive disclosure**—introduce resources as the player is ready, unlock modules as they progress, and let specialization create branch points that prevent overwhelm while rewarding depth.

Bottlenecks are *intentional design*, not arbitrary gates. They force interesting choices: which resources do I prioritize? Which factions do I ally with? When do I expand? These choices ripple into combat, narrative, and personality.

Play this 20+ hours should feel like continuous problem-solving: first, how do I mine efficiently? Then, how do I produce multiple goods? Then, how do I manage supply chains across star systems? Then, how do I merge specializations for late-game synergies?

At no point should players feel they "understand the economy fully and now it's just numbers." There's always a new bottleneck, always a new optimization lever waiting for the expert to discover.
