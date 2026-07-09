---
name: game-foundations
description: >
  Context-free game first principles shared across design, development, and art
  direction — the core loop, meaningful choice, feedback and game feel, balancing
  challenge against skill (flow), and player-experience-first thinking. The shared
  root beneath game design, game engineering, and game art. Load BEFORE a game hub
  or its spokes. Triggers: game design, core loop, game feel, player experience,
  game balance, progression, flow, mechanics.
aliases: [game-foundations]
triggers: [game design, core loop, game feel, player experience, game balance, progression, flow state, mechanics, feedback loop, player agency]
tier: foundation
domain: game
surfaces: ["*"]
spec_version: "2.0"
---

# Game Foundations

The principles that hold whether you're designing a system, coding it, or art-directing it. The three
game hubs diverge in craft (systems vs. code vs. visuals) but share these. Discipline-specific depth
(tech trees, ECS architecture, shader pipelines) lives in the hubs and their spokes. Visual craft also
inherits [[design-foundations]].

## Player experience first
The game is the *experience in the player's head*, not the systems on disk. Every mechanic, line of code,
and asset is justified by the feeling or decision it produces for the player. "Is it correct?" is
necessary but not sufficient — "does it feel right to play?" is the bar.

## The core loop
Every game has a central loop of action → feedback → reward → renewed motivation. If the second-by-second
loop isn't satisfying, no amount of content saves it. Design and tune the smallest loop first; layer
meta-loops (progression, economy) on top of a loop that already feels good alone.

## Meaningful choice + agency
Interactivity is the medium's defining trait. Choices must be *meaningful* — distinct options, legible
consequences, real trade-offs. A "choice" with a dominant strategy or invisible outcomes is a button.
Agency is the feeling that the player's decisions, not the designer's script, drive what happens.

## Feedback + game feel
The player learns the game through feedback: immediate, legible, proportional response to input (juice,
audio, animation, state change). Game feel is the moment-to-moment tactile quality — it's mostly feedback
timing and weight, and it's where "technically working" becomes "fun".

## Challenge, skill, and flow
Engagement lives in the channel between boredom (too easy) and anxiety (too hard) — and the channel moves
as the player improves. Balance, difficulty curves, and progression exist to keep challenge tracking
skill. Tune against the *target player*, not the designer's mastery.

## Related
- applies-in ← [[lead-art-director]] · [[lead-game-designer]] · [[lead-game-developer]]
