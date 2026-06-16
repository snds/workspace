# Game Design Principles & Shared Vocabulary

This is the foundational vocabulary document for all Legion-related skills. It bridges Sean's design systems background to game design concepts and provides precise definitions for mechanics, narrative, and UX terminology used across the project.

---

## Core Game Design Concepts

### Player Agency
The degree to which player choices affect game outcomes in visible, understandable ways.

**High agency**: Player can achieve a goal through multiple viable paths. Trade-offs are explicit. Failure teaches something about the system.

**Low agency**: Player follows a linear script. Choices are cosmetic. Systems respond unpredictably.

**In Legion**: Agency is foundational. A player deciding to mine copper instead of iron should see immediate, traceable consequences: copper production rises, iron infrastructure starves, the economy shifts. The system must be transparent enough that the player understands their own power.

**Test question**: Can the player predict what will happen three turns after making a decision? If not, the agency is illusory.

---

### Emergent Gameplay
Outcomes that arise from systems interaction without explicit designer programming. Complex behavior emerges from simple rules.

**Examples**:
- **Factorio**: You design a production line. Unintended bottlenecks emerge. You optimize. The system teaches you about yourself.
- **Bobiverse**: Bob replicates. Each clone has personality drift. Clones pursue conflicting goals. Stories emerge that Taylor didn't write linearly.

**In Legion**: Faction conflicts should emerge from economic competition, not cutscenes. A Bob clone specializing in military production might trigger a cascade where rival clones feel threatened. That tension drives narrative.

**Test question**: Can the system create a situation that surprises even the designer?

---

### Feedback Loop (Positive & Negative)
Mechanisms that reinforce or restrain player actions.

**Negative feedback** (stabilizing): Action triggers consequence that reduces further action.
- Example: Factory overproduction → resource overflow → production slows (storage full, power spike)
- Function: Prevents runaway states. Teaches discipline.

**Positive feedback** (growth): Action triggers consequence that encourages more action.
- Example: Successfully defend a colony → resources secured → ability to defend larger colony
- Function: Creates momentum. Makes skilled play feel powerful.

**In Legion**: The economy needs both. Energy production is a negative feedback (expand too fast → power grid overloads). Military success is a positive feedback (win a battle → claim rare resources → upgrade fleet). Balancing these creates the rhythm of play.

**Design caution**: Pure positive feedback = winner takes all (unfun). Pure negative feedback = everything plateaus (stasis). Mix them.

---

### Pacing
The rhythm at which challenges escalate and players gain new capabilities.

**Pacing shapes**: 
- **Slow burn**: Early game learns mechanics. Mid-game solves first real problem. Late game scales to galactic scope.
- **Spike**: Sudden difficulty wall tests mastery.
- **Plateau**: Period of security where player explores and optimizes.

**In Legion V1**: Tutorial teaches factory → first combat is a spike (test learned skills) → victory grants resources → exploration plateau (discover what's possible) → endgame goal (reach a tech or defeat rival clone).

**Test question**: Is the player always aware of the next challenge ahead?

---

### Risk/Reward
The relationship between downside risk and potential gain. Meaningful decisions have both.

**In Legion**: Overextending military leaves colonies undefended (risk) but secures valuable star system (reward). Optimal play balances both. A player who never risks loses. A player who never plays defensively dies.

**Test question**: Can you lose by making locally-optimal but globally-risky decisions?

---

## Systems Design Vocabulary

### Resource Economy
The system governing how players acquire, convert, and spend valuable commodities.

**Key terms**:
- **Faucet**: Where resources enter the economy (mining, manufacturing, trade)
- **Sink**: Where resources leave or are locked up (construction, maintenance, combat loss)
- **Throughput**: Rate of resource flow through the economy
- **Bottleneck**: Constraint that limits throughput (e.g., smelter capacity limits ore processing)
- **Conversion loss**: Efficiency cost of transforming one resource into another

**In Legion**: Energy is the master resource. Everything costs energy. Mining costs energy. Manufacturing costs energy. Combat costs energy. A player who understands energy throughput masters the game.

**Balancing principle**: Faucets and sinks should be roughly equal in equilibrium. Skilled players optimize the gaps.

---

### Bottleneck
A constraint that limits system output below potential demand.

**Examples**:
- Factory making widgets needs 100 copper/turn. Mines produce 60 copper/turn. Copper is the bottleneck.
- Starship production needs rare earth. Rare earth planets are scarce. Planetary scarcity is the bottleneck.

**Why it matters**: Bottlenecks are *information*. They tell the player: this is your limiting factor. Solve it and you unlock the next tier of play.

**In Legion**: Bottlenecks should be visible (UI clearly shows "copper production: 60/100 needed"). Solving a bottleneck should feel like puzzle-solving, not grinding. The solution should be interesting: build a second mine, trade with a rival clone, discover a richer planet, develop refining technology.

---

### Tech Tree
A directed graph of technologies where unlocking A enables research of B, C, D; and reaching B unlocks X, Y, Z. Creates progression and gating.

**In Legion V1**: Light tech tree. Research guides progression but doesn't dominate. Example path: Basic Extraction → Efficient Smelting → Rare Earth Refining → Advanced Propulsion.

**Design principle**: Never force a single optimal path. Multiple routes to power should exist. A player specializing in military should reach equivalent strength to a player specializing in economics, just through different techs.

---

### Throughput
Rate of meaningful action in a system. How much stuff moves per unit time.

**In Legion factory**: A smelter converts 10 ore/minute into 8 ingots/minute (conversion loss). The factory's copper throughput is bottlenecked by smelter capacity. Player optimizes by adding smelters or upgrading to faster models.

**Relationship to player skill**: Mastery often means optimizing throughput. A novice factory produces 50 widgets/hour. An expert produces 200/hour through clever layout, supply chains, prioritization. The system rewards this.

---

### Scalability
Whether systems remain interesting as they grow in magnitude.

**Problem**: Factory management is fun at 10 factories. At 500 factories across 20 star systems, is it still fun or is it busywork?

**In Legion**: Hierarchical management. Player doesn't manually control each factory. Instead: set production quotas at the system level, let automation handle local optimization, player manages exceptions and strategic pivots.

**Test**: Does doubling the scope double the fun, or does it flatten into drudgery?

---

## Narrative Design Vocabulary

### Ludonarrative
The story told through mechanics and gameplay, distinct from scripted narrative.

**Distinction**:
- **Ludonarrative**: A rival Bob clone seizes a resource planet through superior military → that's the story the *game* told you through mechanics.
- **Narrative**: Cutscene explaining why the clone wanted the planet.

**In Legion**: V1 emphasizes ludonarrative (mechanics-driven story) over narrative (cutscenes). A player who builds an efficient economy and defeats a rival tells a story through gameplay. The narrative (dialogue, lore, faction flavor) *contextualizes* what the mechanics already told.

**Principle**: Don't contradict mechanics with story. If the game mechanics say "this player is resource-starved," don't write a cutscene where they're wealthy. Let mechanics and story reinforce.

---

### Environmental Storytelling
Conveying narrative and worldstate through world design, not exposition.

**Example**: A factory lies dormant, solar panels cracked, resource deposits depleted. No NPC explains what happened. The *environment* tells you: someone extracted everything and abandoned this planet.

**In Legion**: Abandoned colonies, wrecked fleets, depleted ore bodies — these tell stories. A star system ravaged by war looks different from one at peace. The world is readable.

---

### Personality Drift
In Bobiverse, Bob clones diverge due to quantum effects. Each develops unique values, priorities, fears.

**In Legion**: Bob clones start identical but develop personality traits affecting play. Clone A prioritizes military strength. Clone B focuses on exploration. Clone C pursues peaceful trade. They have conflicting goals.

**Mechanical implementation**: Traits affect production efficiency, combat aggression, trade favorability, research speed.

**Narrative layer**: These traits create emergent story. Two clones with compatible traits cooperate. Conflicting clones compete. Conflict isn't scripted; it's mechanical.

---

### Branching Narrative
Story paths that diverge based on player choice. Multiple endings exist.

**In Legion V1**: Minimal branching. Goal is fixed (reach a tech milestone, defend system, establish trade). Flavor (dialogue, NPC reactions) might branch based on how you achieved it.

**V2+**: More branching. Allying with Faction A might lock out Faction B's quests. Military victory path differs from diplomatic path.

---

## Systems Thinking & Balance

### Game Balance
Ensuring no single strategy dominates all others. Multiple viable playstyles should reach similar power levels.

**In Legion**: A military-focused player shouldn't always beat an economy-focused player. A trader shouldn't dominate a combatant. The system should have rock-paper-scissors dynamics.

**How to test**: Can a novice military player beat an expert economy player? If not, military is overtuned. Can an expert economy player defeat a novice military player? If not, economy is too weak.

---

### Dominant Strategy Problem
When one approach is *always* optimal, removing meaningful choice.

**Example (bad)**: Mining copper gives 10 resources per turn. Mining iron gives 5. Optimal play is always mine copper. Iron is dead. No choice.

**Fix**: Make copper more valuable but require more infrastructure, or give iron unique uses that create parity.

**In Legion**: Avoid situations where there's only one optimal military comp, or one perfect factory layout, or one dominant tech path. Variety should be rewarded.

---

### Economy Dynamics
How scarcity, abundance, and player skill affect resource flow.

**Scarcity**: Limits total possible production. Forces choices. Creates meaningful trade-offs.

**Abundance**: Can devolve into "pick any strategy." But total abundance (infinite resources) breaks gameplay. Sweet spot: resources are limited but skill allows optimization.

**In Legion**: Energy is always scarce. Raw materials vary (some planets rich in certain ores). Skilled players optimize extraction, minimize waste, scale efficiently.

---

## UX/Game Feel Vocabulary

### Juice (Game Feel)
The responsive feedback a system provides when a player acts. Includes visual, audio, haptic feedback. Makes interaction feel *alive*.

**Examples**:
- Factory producing a unit: visual pop-up, sound effect, animation of unit emerging. Not just a number incrementing.
- Successful dodge in combat: brief slow-mo, screen shake, impact sounds. Reward the player's skill with sensory feedback.
- Mining ore: environmental dust, rumble, sound. Not a silent progress bar.

**In Legion**: Factories should feel like living machines. Combat should feel impactful. Exploration should feel wondrous. This is aesthetic + audio + animation aligned to mechanics.

**Principle**: Reward every successful action with perceptible feedback. Make failure also *feel* like something (loss indicators, damage animations). Feedback loops are half mechanical, half sensory.

---

### Information Scent
How clearly the game communicates what's possible and what's at stake.

**Good scent**: Player sees a red warning icon → understands power grid is overloaded.

**Bad scent**: System crashes silently. Player doesn't know why.

**In Legion**: Status should be readable at a glance. A factory running at 80% capacity looks/behaves differently from 20%. A heavily militarized star system looks different from peaceful one. An overclocked reactor shows strain (heat bloom, efficiency loss).

**Test question**: Can a player understand game state without opening sub-menus?

---

### Cognitive Load
The mental effort required to understand and manage a system.

**High load**: Managing 50 production queues manually, tracking energy per facility, doing math.

**Low load**: Setting system-level quotas. Local automation handles details. Player manages exceptions.

**In Legion**: Keep moment-to-moment load low. Individual factory operation should be straightforward (set production target, automation handles rest). Strategic load (deciding which planets to expand to) can be higher; players expect complexity in strategy.

**Principle**: Make the simple case easy. Hide complexity behind accessible interfaces. Expose complexity to players who want it (advanced players can toggle detailed resource tracking).

---

### Flow State
Psychological state where challenge matches skill, and player is fully immersed.

**Conditions**:
- Clear goal
- Immediate feedback
- Challenge slightly above current skill
- Low extraneous interruption

**In Legion**: A player managing a 3-system economy with active combat should experience flow. Not too easy (bored), not too hard (frustrated). Difficulty scaling and tutorial progression support this.

---

### Tutorial Pacing
How quickly and efficiently the game teaches systems.

**Anti-pattern**: 20-minute mandatory tutorial explaining every UI element.

**Better**: Teach-by-doing. First mission: place an extractor (learn placement). Extractor produces resources (learn feedback). Resources fill storage (learn limits). Problem: storage full. Solution: place a smelter (learn conversion). Repeat: each challenge teaches one system.

**In Legion**: Tutorial should be <1 hour. Teach one core system per mission stage. Each stage has a clear goal. Success teaches the next system's existence.

---

## Design Systems ↔ Game Design Mapping

Sean's expertise in design systems (tokens, components, hierarchy, constraints) transfers directly to game design. Here's the translation:

| Design Systems | Game Design |
|---|---|
| **Design tokens** | Game variables & balancing parameters (energy cost, production rate, cooldown duration) |
| **Component** | Game entity (factory, ship, Bob clone) with properties and behaviors |
| **Component state** | Entity state (factory: idle/running/overloaded; ship: intact/damaged/destroyed) |
| **Variant** | Alternate entity type or mode (factory variant: extractor/smelter/assembler; ship variant: fighter/corvette/capital) |
| **Hierarchy** | Information architecture (colony contains factories; star system contains colonies; galaxy contains systems) |
| **Constraint** | Game limit or rule (energy budget, production capacity, tech prerequisites) |
| **Composition** | How complex systems are built from simpler parts (economy from factories; fleet from ships; faction from clones) |
| **Design feedback** | Game feedback (visual/audio indicating status, warning when bottleneck detected) |
| **Accessibility** | Game inclusivity (difficulty modes, readable UI, clear information hierarchy) |
| **Scalability** | Whether system remains engaging as magnitude grows (does 500 factories stay fun?) |

**Application**: When designing a new game system, think in terms of:
1. What are the **tokens** (variables, costs, rates)?
2. What are the **components** (entities that interact)?
3. What **states** can each component occupy?
4. What **constraints** limit growth?
5. How do components **compose** into larger systems?
6. What **feedback** makes interaction clear?

This systems-thinking approach prevents ad-hoc feature bloat and creates coherent, understandable gameplay.

---

## Balancing & Iteration

### A/B Testing (in game design)
Changing one variable and measuring impact.

**Example**: Copper production rate is 10 ore/min. Change to 12. Measure: Does this unblock bottleneck? Does it create a new bottleneck? Is economy healthier or broken?

**In Legion**: Use prototyping and playtesting. Change production rates, resource costs, tech unlock requirements. Measure whether goals feel achievable, whether skilled play is rewarded, whether bottlenecks are meaningful.

---

### Playtesting
Observing real players engaging with systems, without explanation.

**What to measure**:
- Do they understand the goal?
- Where do they get stuck?
- What do they do intuitively vs. what requires tutorial?
- Do they feel agency or do they feel lost?

**In Legion**: Early V1 playtests should focus on core loop: Can new player place a factory and understand resource flow? Does combat feel fair? Does tech tree feel like progression or confusion?

---

### Emergence vs. Fragility
Emergent systems can create unexpected outcomes. Some are delightful. Some break the game.

**Fragility**: System is so tightly balanced that small changes cascade into chaos.

**Robustness**: System handles edge cases gracefully. Player ingenuity is rewarded within bounds.

**In Legion**: Allow creative play (using factory layout tricks to optimize throughput). But add guardrails (cap on production speed, cap on army size) to prevent soft-locks or sequence breaks.

---

## References & Further Reading

### For mechanics: 
- Schell, *The Art of Game Design: A Book of Lenses* — comprehensive framework for thinking about games as systems
- Swink, *Game Feel: A Game Programmer's Guide to Virtual Sensation* — the technical layer beneath juiciness
- Factorio wiki on ratios and production chains — practical example of balanced resource economy

### For narrative:
- Taylor, *Bobiverse* series — AI personality, emergence, conflict through divergent values
- Weir, *Project Hail Mary* — problem-solving, hard sci-fi constraints
- Wright, *Emergence: The Connected Lives of Ants, Brains, Cities, and Software* — how complexity arises from simple rules

### For design systems lens:
- Your own design systems work (tokens, component architecture, constraint thinking) — this vocabulary is a reapplication of those principles to interactive systems rather than static UI

---

**Version**: 1.0  
**Last Updated**: 2026-03-27  
**Audience**: All Legion design & development work  
**For questions**: Reference SKILL.md for project context and decision framework
