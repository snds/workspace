# Game UX Design for Legion

Legion is a systems-heavy 4X/RTS game. Its UX must manage complexity without overwhelming players. This reference covers information architecture, HUD design, menus, tutorials, accessibility, and design systems—areas where Sean's UX expertise translates directly.

## Information Architecture for Complex Games

**Progressive Disclosure**

Like design systems, game UX reveals complexity in layers. Player should never see all information at once.

**Layer 1 (Novice)**: Single star system, local factory view.
- HUD shows: Resource bars (Iron, Energy), Current factory output, Local threats
- Available menus: Factory builder, Tech tree, Settings
- Hidden: Multi-system logistics, Advanced combat formations, Faction relations

**Layer 2 (Intermediate)**: Two star systems, interstellar logistics.
- HUD adds: Energy transmission overlay, System map, Trade status
- Available menus: Supply chain optimizer, Route planner
- Revealed: Cross-system economy, faction diplomacy

**Layer 3 (Expert)**: Three+ star systems, mastery.
- HUD adds: Predictive resource graphs, Threat analysis, Advanced unit formations
- Available menus: Scenario planner, AI diplomacy sim, Historical logs

Players unlock layers through progression. Accessing Layer 2 menus before you need them should be hard (buried in submenu) but possible (for curious players).

**Hierarchy as Information Scent**

Organize menus by *what players need to decide next*:
- Top level: What can I do *right now*? (Factory actions, unit commands, exploration)
- Second level: What should I plan for? (Tech tree, supply chains, threats)
- Third level: What happened before? (Historical logs, faction relations, combat replays)

Playtesting validates hierarchy. If players search for "research progress" and can't find it, hierarchy failed.

## HUD Design Patterns

**Resource Bars**

Top-left corner: Always visible, hard to miss.
```
[Iron ▓▓▓▓░] 450 / 500
[Energy ▓░░░░] 120 / 600
[Data ▓▓▓▓▓▓▓░] 2850 / 5000
```

Color coding (Sean's design system thinking applies):
- Iron: Gray/brown (earth element)
- Energy: Yellow/orange (light/heat)
- Data: Blue/cyan (information)

Over-capacity state: Bar turns orange, pulses. Clear visual signal: "You're wasting resources."

Under-capacity state: Bar turns red. Clear signal: "Production stalls."

**Minimap (System View)**

Bottom-right corner: Shows local star system or multi-star network (Layer 2+).
- Player's star systems: Blue
- Faction territories: Faction color (red for enemies, green for allies)
- Neutral zones: Gray
- Anomalies: Purple pulsing dot

Click minimap to pan camera. Double-click to jump to location (if revealed).

**Unit Selection and Orders**

HUD centerpiece during combat:
- Selected unit portrait (top-left of unit cluster)
- Unit stats: Health, Energy, Ammo
- Action buttons: Move, Attack, Special ability, Retreat
- Formation buttons: Line, Cluster, Spread (affects armor vs. DPS)

Keep to 6-8 visible buttons. Advanced controls hidden in right-click menu.

**Alert System**

Edge of screen, color-coded:
- Red pulse: Incoming threat (combat imminent)
- Orange flashing: Resource depleted (production halted)
- Blue fade: Intel update (faction message, discovery)
- Green slow pulse: Opportunity (new tech available, trade offer)

Sounds paired with alerts. Player can mute by alert type in settings.

## Menu and Screen Flow

**Main Menu Structure**

```
ROOT: Main Menu
├── New Game → Difficulty → Star Selection → Specialization → Tutorial
├── Load Game → [Saved files]
├── Settings → Audio / Video / Accessibility
└── Credits
```

**In-Game Menu Hierarchy**

```
ESC → Pause Menu
├── Resume
├── Objectives → [Active quests and goals]
├── Map System → View and navigate star systems, manage colonies
├── Tech Tree → Research priorities, unlock preview
├── Factory View → Zoom to detailed production chains
│   ├── Module Inspector → Edit single module
│   └── Production Planner → Multi-module chain design
├── Combat → Unit roster, formations, combat log
├── Diplomacy → Faction status, trade agreements, historical logs
├── Logs → All historical events, sorted by type
├── Settings
└── Quit to Main Menu
```

Design principles:
- Never bury critical info more than 2 clicks deep
- Tabs within views (not nested menus) for lateral navigation
- Back button always available

**Factory View Detail**

When zooming into a factory:
1. Show 3D grid with modules placed
2. Highlight input/output connections (visual spaghetti, color-coded by resource type)
3. Click module to inspect: Show throughput, energy draw, upgrade tier, add/remove module
4. Click empty grid square to build: Show compatible modules for that footprint

This mirrors Figma's component library workflow. Low hierarchy → direct selection.

## Tutorial and Onboarding

**Problem**: Legion has deep systems. Tutorial can't teach everything.

**Solution**: Layered tutorials triggered by need.

**Turn 1-5: Survival Basics**
- "You control a mining operation. Click the mining module to see its output."
- "Resources flow: mines produce Iron. Iron flows to smelter. Smelter produces Bar."
- Constraints: Can build only mining + smelting modules (other options hidden)

**Turn 6-15: Research and Expansion**
- Unlock research menu: "Choose a tech to research. This unlocks new factory modules."
- Highlight one faction contact: "They want to trade. Click to open diplomacy."
- Reveal minimap: "Other star systems exist. When you're ready, explore."

**Turn 16-30: Mastery Unlocks**
- Reveal advanced combat formations
- Unlock multi-system supply chain tools
- Introduce personality drift UI

**Evergreen Help System**
- Hover over any term (resource type, module, tech) to see tooltip
- Tooltips explain *why* (not just what): "Energy transmission loss is 2% per distance unit. This encourages local factories over long supply chains."
- Glossary menu: All terms, all definitions, searchable

**Accessibility in Onboarding**
- Tooltips read aloud (text-to-speech)
- Colorblind modes recolor resource bars (Deuteranopia: Iron→orange, Energy→purple)
- Tutorial text scales (user can increase font size)

## Accessibility in Games

**Visual Accessibility**

- **Colorblind support**: Offer 3 modes (Normal, Deuteranopia, Protanopia). Pair colors with icons. No color alone conveys meaning.
  - Example: Energy bar is yellow AND has a lightning bolt icon.
  
- **Contrast**: All text ≥ 4.5:1 contrast ratio (WCAG AA). HUD elements ≥ 3:1.

- **Font size**: Allow player to scale UI text 75% to 150%. Not just 100%.

**Motor Accessibility**

- **Remappable controls**: All actions bindable to custom keys. No fixed keybinds.
- **No time limits**: Pause available anytime. Combat doesn't require twitch reflexes (player can slow-mo or pause to plan).
- **Click-anywhere controls**: Clicking on a unit or location issues order. No chording (holding Ctrl+clicking). No double-taps.
- **Toggle options**: Hold-to-charge abilities can be toggled on/off in settings.

**Cognitive Accessibility**

- **Clear language**: Avoid jargon. Use tooltips for technical terms.
- **Consistent UI patterns**: Same button always means "build module." Same color always means "threat alert."
- **Reduced motion**: Minimize flashing and fast animations. Allow disabling parallax scrolling, screen shake.

## Game UI as Design System

Sean's design system expertise applies directly. Treat game UI components as a system:

**Reusable Patterns**

| Pattern | Use Cases | Anatomy |
|---------|-----------|---------|
| **Resource Bar** | Energy, Iron, Data, etc. | [Icon] [Label] [▓▓░] [Number] |
| **Stat Card** | Unit health, module throughput | [Title] [Stat Name: Value] [Change △] |
| **Action Button** | Build, research, attack | [Icon] [Label] [Hotkey] [Cooldown ring] |
| **Menu Item** | Any selectable list item | [Icon] [Label] [Submenu arrow?] [Hotkey?] |
| **Alert Badge** | Threat, opportunity, update | [Color dot] [Text] [Dismiss ✕] |

**Token System**

Define reusable design tokens:

```
Colors:
  --resource-iron: #8B7355
  --resource-energy: #FFD700
  --resource-data: #4A90E2
  --state-danger: #E74C3C (red for threats)
  --state-success: #27AE60 (green for opportunities)

Spacing:
  --gap-xs: 4px
  --gap-sm: 8px
  --gap-md: 16px
  --gap-lg: 24px

Typography:
  --font-body: Arial, sans-serif, 14px
  --font-label: Arial, sans-serif, 12px, bold
  --font-heading: Arial, sans-serif, 18px, bold
```

Apply tokens consistently. All action buttons use `--gap-sm` internally. All threat alerts use `--state-danger`. This creates visual coherence and makes changes global (e.g., rebrand all danger states by updating one token).

**State Machine Consistency**

Buttons have states: default, hover, active, disabled, cooldown. Define all states for each button type:

```
Action Button
├── default: Gray, clickable
├── hover: Darker gray, cursor changes
├── active (pressed): Blue highlight, pressed appearance
├── disabled: Grayed out, no cursor change
└── cooldown: Grayed with timer ring

Menu Item
├── default: Gray text
├── hover: Highlighted background
├── active (selected): Bright text, checkmark
└── disabled: Light gray, no hover
```

Apply these consistently. No button behaves differently without reason.

## Bridge from Sean's UX Expertise

**Design Tokens → Game Variables**: Design tokens (color, spacing) map to game variables (resource types, difficulty knobs). Both benefit from centralized definition and global updates.

**Component States → Game States**: A button's states (default/hover/active/disabled) mirror a unit's states (idle/moving/attacking/damaged). State machines clarify both. Document state transitions visually (e.g., "Unit can only move from Idle state, not from Attacking").

**Information Architecture → Menu Hierarchy**: Organize game menus by depth and frequency of access, same as design system docs. Most-used actions at top level. Advanced options nested.

**Consistency → Interaction Vocabulary**: In design systems, you have reusable button patterns. In games, you have reusable interaction patterns ("click to select," "drag to move," "right-click for context menu"). Define them once, apply everywhere.

**Don't force analogies** where they break. Fog-of-war in RTS has no UX parallel. Clone personality drift is narrative-specific. Stick to genuine bridges and acknowledge differences honestly.
