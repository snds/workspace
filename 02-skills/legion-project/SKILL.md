---
name: legion-project
description: >
  Persistent project context for the Legion game. Load this skill IMMEDIATELY whenever the
  user says "legion", "Legion", "the game", "my game", "game project", or any reference to
  Legion game development. This is the foundation skill — it provides design pillars, visual
  identity, tech stack, and project state that all other Legion skills depend on. Also trigger
  on: game design, combat systems, factory mechanics, exploration, AI behavior, resource economy,
  narrative design, visual style, Three.js + WebGPU implementation, Bob clone mechanics, star
  system mechanics, faction systems, RTS gameplay, 4X strategy, factory management, hard sci-fi
  aesthetics, player progression, combat balance, technology trees, tutorial design, difficulty
  scaling, emergent gameplay, Bobiverse, or any Legion-related feature or system. When this skill
  loads, also load the relevant hub skill (lead-game-designer, lead-art-director, or
  lead-game-developer) based on the topic. If the topic is unclear, load lead-game-designer
  as the default.
aliases: [legion-project]
spec_version: "2.0"
---

# Legion Project Context

## Setting & Player Fantasy

You are building an interstellar hard sci-fi game inspired by Dennis E. Taylor's Bobiverse novels. The player commands a self-replicating artificial intelligence probe — a Bob clone — who explores the real star systems of our spiral arm, builds resource extraction and manufacturing infrastructure, and engages in strategic combat against rival factions and threats.

The player fantasy: **omniscient strategist + mad scientist engineer + space explorer**. You manage exponential growth across multiple star systems, optimize production chains, face meaningful constraints (energy, raw materials, manufacturing capacity), and discover emergent problems that force you to think sideways. Build a robot armada. Defend your colonies. Expand, optimize, survive.

The emotional core: **Autonomy and consequence**. Your decisions ripple across star systems. Your AI identity has personality drift — each Bob clone evolves differently, creating unique perspectives and unexpected conflicts. This is an RTS where you're not commanding faceless units; you're coordinating versions of yourself with diverging values.

## Design Pillars

### 1. Player Agency Through Systems Depth

**Definition**: Players make meaningful decisions with transparent cause-and-effect. Systems are deep enough to reward mastery, simple enough to learn incrementally.

**Test Questions**:
- Can the player achieve a goal through multiple viable paths?
- Are trade-offs explicit and knowable in advance?
- Does player skill progression feel like mastery rather than grind?
- When systems interact, do the outcomes feel logical rather than arbitrary?

**Implication**: Design is not about linearity or visual polish first. It's about mechanical honesty. A factory bottleneck at copper production tells the player something true about their economy. Combat that rewards positioning teaches risk/reward. Every system is a conversation with the player.

### 2. Grounded Sci-Fi Authenticity

**Definition**: Technology, physics, and constraints feel rooted in real science and engineering. When players break the rules, the game explains the cost transparently.

**Test Questions**:
- Could a reasonable engineer understand the system from first principles?
- Are energy budgets real constraints, not soft limits?
- Do real orbital mechanics and communication delays matter?
- Does the game feel like operating a machine, not navigating UI theater?

**Implication**: Draw from The Martian, Project Hail Mary, The Expanse — hard sci-fi that respects audience intelligence. This builds immersion deeper than flashy graphics. A resource economy grounded in thermodynamic realism (energy input → output) is more engaging than arbitrary number juggling.

### 3. Emergent Narrative

**Definition**: Story emerges from systems and player decisions, not branching trees. Factions clash, technology trees open new strategies, rival Bob clones pursue conflicting goals.

**Test Questions**:
- Do systems create surprising situations the designer didn't explicitly program?
- Can the player write their own story through emergent outcomes?
- Does failure feel like character development rather than game-over?
- Are faction dynamics player-driven or scripted?

**Implication**: V1 is light on faction narrative (window dressing). But the architecture must support emergent storytelling from day one. A Bob clone who specializes in military production has a different narrative than one focused on exploration. Let systems tell that story.

### 4. Scalable Complexity

**Definition**: The core loop is learnable in minutes. New mechanics layer on without overwhelming. Mid-game players tackle problems v1-novices don't know exist.

**Test Questions**:
- Can a new player succeed with intuitive rules?
- Does adding one new system break five existing ones?
- Do difficulty curves feel natural, not arbitrary?
- Is there always a clear "next challenge" visible?

**Implication**: Tutorial teaches factory basics → first combat → multi-system economy → rival Bob clones → factions. Each layer multiplies depth without erasing foundation knowledge. Mechanics compound; learning doesn't restart.

### 5. Satisfying Mastery

**Definition**: Skilled play is visibly, quantifiably better. Optimization is rewarding. The game makes you feel smart.

**Test Questions**:
- Can an expert player triple a novice's resource throughput?
- Does optimization feel like puzzle-solving, not spreadsheet work?
- Do systems reward creative abuse (within bounds)?
- Is there a skill ceiling players can see and chase?

**Implication**: Victory should feel earned. A perfectly tuned factory producing 1000 units/cycle while using half the energy is viscerally satisfying. Combat where micro matters creates flow state. Let players express competence.

## Visual Identity

Clean NASA-industrial hard sci-fi realism. Reference: The Martian (functional engineering), Project Hail Mary (wonder + pragmatism), The Expanse (grounded tech), Oblivion (architectural scale and geometry).

Aesthetic pillars:
- **Function over ornament**: Every visual element serves gameplay. A conduit carrying resources is visually distinct from inert structure.
- **Industrial scale**: Factories are massive. Structures have weight, volume, and presence. No cartoon simplification.
- **Color discipline**: Neutral grays, blacks, industrial blues and oranges. Thematic coherence per faction. Resource types are color-coded (rare earth = blue, common metals = orange, energy = yellow).
- **Material honesty**: Metal looks like metal. Light refracts realistically. Weathering and wear tell stories of hard use.
- **Information density**: UI and world convey status at a glance. A factory running at 80% capacity looks different than 20% (thermal imaging, glow patterns, operational hum).

## Current Project State & V1 Scope

### V1 Target: Playable Prototype
Core systems functional and balanced. Not complete, not polished, but *playable*. Success = player can declare victory by solving a defined problem (reach a tech goal, defend a colony, establish trade routes).

### V1 Systems (Minimum Viable)
1. **Exploration**: Single system (Sol), scannable planets, resource discovery, basic research
2. **Factory Building**: Place extractors, smelters, assemblers. Resource flow physics. Bottleneck feedback
3. **Resource Economy**: Energy as hard constraint. Extraction rate, conversion loss, storage
4. **RTS Combat**: Unit types (fighter, corvette, capital), positioning, weapon ranges, player-controlled tactics
5. **Bob Clone Mechanics**: Personality traits affecting production/combat efficiency. Simple divergence system
6. **Tutorial Flow**: Learning curve that teaches one system per mission stage

### V1 Out of Scope
- Faction diplomacy systems (narratively present, mechanically light)
- Procedural galaxy (single star system initially)
- Advanced AI opponents
- Multiplayer
- Complex research trees
- Quantum mechanics flavor (cosmetic only in v1)

### V2+ Roadmap (Context for Architecture)
- Multi-system exploration and trade
- Complex faction alignments and wars
- Advanced Bob clone divergence (personality → strategy shifts)
- Player-driven narrative with consequences
- Procedural galaxy generation
- Cooperative play (Bob clones as networked entities)

## Technology Stack

### Three.js + WebGPU

**Why web-native over traditional engines**:

**Maximum Claude Agency**: Claude writes all game code, shaders, and materials directly as TypeScript and GLSL. No intermediary 3D editor, no node-graph black boxes. "I describe, you build" workflow: you articulate intent, Claude generates working code.

**Performance & Capability**: WebGPU (production-ready January 2026) delivers 2-10x performance over WebGL. Handles PBR materials, custom GLSL shaders, post-processing chains, and InstancedMesh compute for thousands of factory entities without performance degradation — achieving NASA-industrial hard sci-fi visual fidelity at scale.

**Visual Flexibility**: Three.js provides the 3D foundation; visual shader editors (Lumina Workbench with AI generation, NodeToy, Three.js Shader Graph) allow Sean to tweak material parameters and post-processing without touching code. Custom GLSL shaders give absolute control over factory glow, energy flow visualization, and material weathering.

**Deployment & Iteration**: Browser deployment eliminates friction for playtesting, sharing prototypes, and iterating with stakeholders. No build pipelines, no engine compilation. Change code, refresh page.

**Future Flexibility**: This prototype maximizes Claude's generative capabilities during the design exploration phase. Unreal Engine 5 remains a viable migration path for production-quality 3D and complex systems if later versions require console/native performance or AAA-grade tooling.

## Key References

### Narrative & Worldbuilding
- **Bobiverse series** (Dennis E. Taylor): Replicating probes, personality drift, emergent conflict, hard sci-fi sensibility
- **The Expanse** (TV/books): Grounded space operations, faction dynamics, orbital mechanics matter
- **Project Hail Mary** (Andy Weir): Problem-solving engineer hero, clear constraints, emergent solutions

### Game Mechanics & Systems
- **Factorio**: Feedback loops, bottleneck clarity, satisfying optimization, scaling complexity
- **Stellaris**: 4X strategy, systems-driven gameplay, faction flavor without overwhelming mechanics
- **StarCraft**: RTS combat, unit composition, positioning, readable skill expression
- **Kenshi**: Emergent narrative from systems, player-defined goals, consequence-driven storytelling

### Visual & Aesthetic Reference
- **The Martian** (film): Industrial problem-solving, functional beauty, scale
- **Satisfactory** (game): First-person factory building, scale and presence, color-coded resources
- **Oblivion** (game): Architectural grandeur, environmental storytelling through space design

## Foundational Vocabulary

This skill provides project context. For shared game design terminology, mechanics vocabulary, and the bridge between Sean's design systems background and game design concepts, see **`references/game-design-principles.md`**.

Load that file when discussing:
- Feedback loops and pacing
- Player agency and emergence
- Systems design vocabulary (economy, bottleneck, throughput)
- Narrative design concepts
- Game feel and juiciness
- Information architecture and cognitive load
- How design tokens translate to game variables and balancing

---

**Project Owner**: Sean Sands (Principal Product Designer, enthusiast-level game dev)
**Current Focus**: V1 prototype — exploration, factory, RTS combat, basic Bob mechanics
**Technology**: Three.js + WebGPU (TypeScript + GLSL)
**Last Updated**: 2026-03-27
