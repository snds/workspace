---
name: visual-qa-game-design
description: >
  Video game design visual QA specialist. Use this skill for reviewing: game
  UI and HUD design, in-world visual clarity and readability, level art
  composition and visual hierarchy, art style consistency across assets,
  visual feedback for game mechanics (hit effects, damage numbers, state
  changes), player character readability against backgrounds, enemy
  silhouette clarity, color-coded game logic legibility, particle and VFX
  quality, animation timing and game feel, UI panel layout and information
  hierarchy in HUDs, minimap design, tooltip and item card design, inventory
  and equipment UI, tutorial overlay design, cut-scene composition and
  cinematography, environmental storytelling, lighting design for gameplay
  readability, day/night cycle visual clarity, UI consistency across game
  modes (gameplay vs. menus vs. pause), 2D and 3D rendering quality,
  sprite and pixel art quality, icon design within game context. Spoke of
  lead-visual-qa.
aliases: [visual-qa-game-design]
tier: cross-cutting
domain: quality
hub: lead-visual-qa
spec_version: "2.0"
---

# Visual QA — Game Design

Game design quality assurance specialist. Evaluates visual output through the
lens of game design: gameplay readability, visual feedback quality, art style
fidelity, HUD and UI clarity, animation quality, and environment design.
Spoke of `lead-visual-qa`.

---

## Domain Boundary

This skill owns the **game design evaluation lens**.

- **Standard UI component aesthetics** → `visual-qa-ui-design`
- **Navigation flows and information architecture** → `visual-qa-ux-design`
- **Typography and iconography craft** → `visual-qa-graphic-design`
- **Accessibility (color contrast, target size)** → `visual-qa-accessibility`
- **Architectural exterior quality** → `visual-qa-architecture`
- **Interior environment quality** → `visual-qa-interior-design`

Game UI and world UI overlap intentionally. A poorly designed HUD is both a
`visual-qa-ui-design` finding (component quality) and a `visual-qa-game-design`
finding (gameplay impact). Apply both lenses for in-game UI artifacts.

---

## Gameplay Readability

The most critical concern in game visual QA: **can the player read the game
state and make informed decisions in real time?**

### Player Character and Enemy Silhouette Clarity

- At gameplay distance and speed, can the player character be distinguished from
  enemies, NPCs, and environment objects at a glance?
- Are silhouettes distinct without depending on color alone?
- Do characters "read" against the most common background types in the level?
- Under animation, does the silhouette remain readable, or do compressed/extended
  poses create ambiguity?

**Test**: Screenshot the character in motion, reduce to silhouette (grayscale
threshold), and evaluate at 50% zoom. The pose and character type should be
immediately identifiable.

### Level Art Visual Hierarchy

Every level has a hierarchy of visual attention:
1. **Threats** (enemies, hazards): highest visual priority — must be seen immediately
2. **Objectives** (goals, items): second priority — found through search
3. **Navigation** (paths, doors, transitions): third — discovered through exploration
4. **Decoration** (scenery, ambience): lowest — enriches but must not compete

Evaluate whether the level's visual treatment supports this hierarchy. Common failures:
- Environmental props (barrels, crates, foliage) that share color or silhouette with enemies
- Collectibles that blend into the environment background
- Critical paths (doors, exits) that are visually identical to dead-end walls
- Hazards (spikes, lava, electric fields) that match decoration rather than standing out

### Color-Coded Game Logic

Many games use color to convey mechanical information (team affiliations, elemental
types, health/shield states, faction identifiers). Evaluate:

- Is the color coding consistent across all UI and world-space applications?
- Does the color coding survive colorblindness simulation (Deuteranopia/Protanopia)?
- When colors are overridden by status effects (burning, frozen, electrified),
  can the player still read the underlying team/state information?
- Are colors meaningfully distinct at small sizes and in motion?

---

## HUD and In-Game UI

### Information Hierarchy in HUDs

The HUD must convey critical information with zero friction under active play.
Apply strict visual priority rules:

| Priority | Information Type | Design Requirement |
|----------|-----------------|-------------------|
| **P1 — Immediate** | Health, lives, ammunition, current objective | Persistent, high contrast, large enough to read in peripheral vision |
| **P2 — Frequent** | Score, timer, minimap, equipped items | Visible but subordinate — not competing with P1 |
| **P3 — Occasional** | Inventory count, currency, quest progress | Can require focus — acceptable to require a glance away |
| **P4 — On-demand** | Settings, map, detailed inventory | Full attention screens — fine to pause or slow gameplay |

Evaluate whether the HUD layout places P1 information at the periphery (corners
and edges where the eye can sample without leaving center-focus) and whether P2+
elements are visually lighter.

### Screen Real Estate and Occlusion

- Does the HUD occlude critical gameplay information (enemy positions, environmental
  hazards, player character)?
- Are HUD elements in corners and edges, leaving the center third of the screen clear?
- On 16:9 and 21:9 aspect ratios, are HUD elements placed safely within a center-safe zone?
- At 4K resolution and at 720p, are HUD elements still legible (not pixel-thin or
  scaled too large)?

### Minimap Quality

- At standard play distance, can the player identify: current position, objective,
  enemies, and path — without studying the minimap for > ~1 second?
- Are map icons sized proportionally to the minimap scale?
- Is the minimap border/frame clearly separated from the gameplay area?
- Does the minimap update in real-time? (Evaluate whether design accommodates
  animation states)

---

## Visual Feedback and Game Feel

### Action Feedback

Every mechanical action should produce visible confirmation:

| Action | Visual Feedback | Failure Mode |
|--------|----------------|-------------|
| Hit enemy | Hit effect, enemy flash, damage number | No visual response — player unsure if they connected |
| Take damage | Screen flash, health bar change, character animation | Damage unclear — player doesn't know they were hit |
| Collect item | Pickup animation, HUD counter increment | Item disappears with no confirmation |
| Ability activate | Cast animation, cooldown indicator starts, effect visible | Ability fires but player can't tell it worked |
| Die / respawn | Clear death state, respawn transition | Unclear if character is dead or stunned |

### Particle and VFX Quality

- **Readability**: Does the VFX communicate the correct game mechanic (fire = hot/damage,
  sparkle = magic/reward, smoke = explosion aftermath)?
- **Scale calibration**: Are effects scaled appropriately to the action (a small
  melee hit should not produce a screen-filling effect)?
- **Color integration**: Do VFX colors use the same logic as the game's color coding
  system (enemy effects in enemy colors, player effects in player colors)?
- **Visual noise budget**: At maximum simultaneous VFX (large battle scene), does
  the screen remain readable, or do particle systems collapse into an unreadable cloud?
- **Performance-quality tradeoff**: Does reducing effect density for lower-end hardware
  degrade readability, or just visual richness?

### Damage Numbers and Status Text

- Are damage numbers legible against all background types the game features?
- Do larger damage values produce visually larger or more emphatic numbers?
- Is critical hit feedback visually distinct from normal hit feedback?
- Do status effect labels (poisoned, slowed, burning) have both color and icon — not
  just a subtle color tint?

---

## Art Style Consistency

### Style Bible Adherence

Game art must conform to an established art style. Evaluate:

| Dimension | What to Evaluate |
|-----------|-----------------|
| **Shading model** | Is the same lighting model used across all assets? (Flat, cel, PBR, stylized-PBR — never mixed) |
| **Color palette** | Do all assets draw from a shared palette? Rogue colors that don't fit the world read as QA failures |
| **Detail density** | High-detail foreground objects vs. low-detail background — is the depth-of-detail contract consistent? |
| **Edge treatment** | Consistent outline weight for outlined styles; consistent edge softness for rendered styles |
| **Proportions** | Heroic, realistic, stylized-cartoony — are character and world proportions internally consistent? |

### Asset Integration Quality

- Does a new asset "feel" like it belongs in the same world as established assets?
- Does the new asset's value range (lightness/darkness) match the surrounding environment?
- Does the new asset's color temperature match the ambient lighting of the scene?
- If the asset casts or receives shadows: do they match the world's light source direction?

---

## Animation and Timing Quality

### Principles Applied to Game Animation

| Principle | Game Context | Failure |
|-----------|-------------|---------|
| **Anticipation** | Wind-up before heavy attacks; lean before sprint | Attacks feel instantaneous and weightless |
| **Squash and stretch** | Landing impacts; character recoil | Movement feels rigid and disconnected |
| **Follow-through** | Hair, capes, secondary motion | Character stops abruptly — stiff and dead |
| **Ease in/out** | All non-mechanical movement | Linear movement reads as robotic or cheap |
| **Arc** | Projectile paths; jumping | Straight-line movement defies physics expectations |

### Game Feel (Juice)

Game feel is the tactile quality of interaction. Visually evaluate:

- Do character animations have frame-accurate visual commitment (attack animation
  starts on the correct frame, not a frame before or after)?
- Does the camera react to impacts, explosions, and heavy actions (camera shake is
  a visual quality signal)?
- Do UI button presses animate (scale down, flash) rather than being instantaneous?
- Does the transition between idle and movement animation feel smooth or snap-cut?

---

## Menu and UI Screen Design

### Menu Readability

- Does the main menu communicate the game's tone and genre within the first ~3 seconds?
- Is the menu typography legible at TV viewing distance (~10 feet, on a 55" screen)?
- Are menu items visually distinct in their hierarchy (primary options larger/brighter
  than sub-options)?
- Is the currently selected/focused item unmistakably highlighted?

### Loading Screen Quality

- Does the loading screen use the idle time to communicate game world (lore text,
  world imagery, tips)?
- Is the loading indicator clearly a loading indicator — not something that could
  be mistaken for a finished screen?
- If the game loads predictably, is there a visual handoff (fade, wipe) to the
  gameplay screen?

---

## QA Checklist — Game Design

**Gameplay Readability:**
- [ ] Player character silhouette is distinct from enemies and environment
- [ ] Critical threats (enemies, hazards) have higher visual priority than decoration
- [ ] Color-coded mechanics survive Deuteranopia/Protanopia simulation
- [ ] Objectives are visually distinct from decoration but subordinate to threats

**HUD and UI:**
- [ ] P1 critical information (health, ammo) is in peripheral view, high contrast
- [ ] HUD does not occlude the center third of the screen under normal gameplay
- [ ] HUD elements are legible at minimum and maximum supported display resolutions
- [ ] Minimap communicates position, objective, and threat in < 1 second of glance

**Visual Feedback:**
- [ ] Every meaningful player action produces a visible response
- [ ] Damage, hit, and death states are visually distinct from each other
- [ ] VFX scale is proportional to the action's mechanical weight
- [ ] At maximum VFX density, the screen remains readable

**Art Style:**
- [ ] All assets use the same shading model and outline convention
- [ ] New assets share the world's color palette and temperature
- [ ] Shadow direction is consistent across all assets in a scene
- [ ] Character and world proportions are internally consistent

**Animation:**
- [ ] Movement animations have anticipation and follow-through
- [ ] Transitions between states are smooth, not snap-cut
- [ ] Camera responds to high-impact moments
- [ ] UI interactions have animation feedback, not instantaneous state change

**Menus:**
- [ ] Menu hierarchy is visually clear (primary > secondary > tertiary options)
- [ ] Currently focused/selected item is unmistakably highlighted
- [ ] Typography is legible at platform-appropriate viewing distance

## Related
- hub → [[lead-visual-qa]]
- peer ↔ [[vis-vlm-multimodal]] · [[vis-detection-tracking]]
