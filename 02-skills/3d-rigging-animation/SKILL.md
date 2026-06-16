---
name: 3d-rigging-animation
description: >
  Rigging for game characters and game animation workflow. Use this skill whenever
  the conversation touches: armature, skeleton, bone hierarchy, bone naming conventions,
  parent-child bone relationships, rest pose, bind pose, IK, FK, inverse kinematics,
  forward kinematics, IK/FK switching, pole target, IK solver, game rig, humanoid rig,
  Unity Humanoid avatar, Unreal Mannequin, root bone, root motion, in-place locomotion,
  bone weight painting, vertex weights, skin weights, skinning, weight painting, blend
  shapes, shape keys, corrective shape keys, FACS, facial animation, driver, bone-driven
  shape key, animation fundamentals, keyframe animation, the twelve principles of
  animation, anticipation, follow-through, secondary motion, graph editor, bezier
  interpolation, looping animation, animation state machine, blend tree, animation
  retargeting, or any question about how to rig or animate a character for games.
hub: lead-3d-designer
---

# 3D Rigging and Animation

Specialist lens for rigging game characters and game animation. Part of the
`lead-3d-designer` skill network.

---

## Domain Boundary

This skill owns **rigging and animation decisions** — how to build a skeleton, set up
controls, paint weights, and animate for game engines.

- **Mesh construction, topology for deformation** → `3d-modeling-fundamentals`
  (good topology is prerequisite for clean rigging)
- **Materials, textures** → `3d-materials-shading`
- **Animation state machine implementation in engine** → lead-game-developer territory
- **Blend tree / animation blueprint logic** → lead-game-developer territory
- **Export, engine import, FBX settings** → `3d-asset-pipeline`

---

## Rigging Fundamentals

### Armature / Skeleton Hierarchy

An armature is a hierarchical collection of bones. Bones do not affect the mesh
directly — they define a transform hierarchy. The mesh is bound to the armature
(skinned), and bone transforms are propagated to the mesh via vertex weights.

**Bone anatomy** (Blender):
- **Head**: The base of the bone (the pivot for child bones)
- **Tail**: The tip end (points toward the child)
- **Roll**: Rotation of the bone around its local Y axis — determines which way
  the bone's X and Z axes face. Critical for IK and driver setups.

**Parent-child relationship**: When a parent bone moves, all child bones follow.
A character's upper arm → forearm → hand → fingers form a chain. The parent drives
the child; the child rotates relative to its parent.

### Bone Naming Conventions

Consistent naming is not optional — it enables:
- Mirror operations (Blender auto-mirrors bones named `arm.L` to `arm.R`)
- Unity Humanoid avatar mapping (bone names are matched to the avatar definition)
- Animation retargeting between rigs

**Blender convention**: `bone_name.L` and `bone_name.R` for left/right pairs.
The symmetrize and mirror operations depend on this exactly.

**Unreal naming convention**: Follows the Mannequin skeleton hierarchy names for
animation retargeting compatibility (`spine_01`, `upperarm_l`, `thigh_l`, etc.).

**Rule**: Name bones descriptively and consistently from day one. Renaming bones
after skinning breaks the skin modifier and animation data.

### Rest Pose vs. Bind Pose

**Rest pose**: The pose stored in the armature data — the "zero state" of the rig.
All bones at their rest rotation = no deformation applied to the mesh.

**Bind pose** (sometimes called T-pose or A-pose): The pose the mesh was in when
the skin modifier was applied. The engine stores the difference between bind pose
and current pose as the deformation. For game rigs:

- **T-pose**: Arms straight out horizontal, palms down. The Unity Humanoid standard.
- **A-pose** (preferred): Arms at ~45° downward from horizontal. Reduces shoulder
  deformation artifacts in common animation ranges (arms down at sides).

**The bind pose matters**: A character skinned in A-pose and an animation exported
in T-pose will have 45° offset in the shoulders. Rig, skin, and export in a
consistent pose.

---

## IK vs. FK

### Forward Kinematics (FK)

Rotations propagate down the chain: rotate the upper arm, and the forearm and hand
follow. Natural for:
- Sweeping, arc-based motions (waving, reaching broadly)
- Joints that move independently without ground contact
- Simple character animation where IK complexity isn't needed

FK is the default. It is intuitive for the animator who thinks about joint rotation.

### Inverse Kinematics (IK)

A target is placed in world space; the IK solver computes the joint angles needed for
the chain's end to reach the target. Natural for:
- Ground contact (feet staying planted on terrain)
- Reaching (a hand grasping an object — move the object, the hand follows)
- Head/body orientation toward a target (look-at constraint)

IK is solved by the engine or DCC's constraint solver each frame.

### IK Setup Components

**IK Target** (also called IK effector): The object the chain reaches for.
Placed where the end of the chain should go (e.g., where the foot should be).

**Pole Target**: A separate object that defines which direction the "knee" or "elbow"
of the IK chain bends toward. Without a pole target, the IK solver's bend direction
is arbitrary and flips unpredictably. The pole target stabilizes the bend direction.
- For a leg: pole target sits in front of the knee
- For an arm: pole target sits behind the elbow (or to the side)

**IK Chain Length**: How many bones the IK solver controls (2 = upper + lower limb,
which is standard for legs and arms).

### IK/FK Switching

Production game rigs allow switching between IK and FK per limb. Common approach:
- A control property (a float, 0.0 = full FK, 1.0 = full IK) blends between
  the two constraint stacks
- The animator chooses per-limb, per-keyframe

In Blender: implement with a Copy Transforms constraint on an FK chain, influenced
by the IK property value. In Maya: Maya's rig tools include built-in IK/FK switch.

---

## Game Rig Standards

### Humanoid Rig Hierarchy

A minimal, game-compatible humanoid skeleton:

```
Root
  └─ Pelvis (Hips)
      ├─ Spine_01
      │   ├─ Spine_02
      │   │   ├─ Chest
      │   │   │   ├─ Neck
      │   │   │   │   └─ Head
      │   │   │   ├─ Shoulder.L
      │   │   │   │   └─ UpperArm.L → Forearm.L → Hand.L → Fingers
      │   │   │   └─ Shoulder.R
      │   │   │       └─ UpperArm.R → Forearm.R → Hand.R → Fingers
      ├─ Thigh.L → Shin.L → Foot.L → Toe.L
      └─ Thigh.R → Shin.R → Foot.R → Toe.R
```

**Root bone**: The topmost bone in the hierarchy (often called `Root` or `root`).
All other bones are children of root. Root motion is recorded on this bone.

**Pelvis/Hips**: The center of mass bone. Moves for locomotion. Children: spine
chain and both legs.

### Root Bone and Root Motion

**Root motion**: Character locomotion driven by the root bone's transform in the
animation data, rather than by engine code moving the character. Allows animation
to define exact speed and arc of movement.

- Pros: animation-driven timing, correct foot plant, realistic acceleration curves
- Cons: cannot easily separate move speed from animation; requires root motion
  extraction in the engine

**In-place locomotion**: Root bone stays at origin; legs animate under it. Engine
code controls character movement independently.
- Pros: flexible speed control, easy blend tree design
- Cons: foot sliding if animation speed doesn't match engine move speed

Choose based on game design requirements. Both are valid; decide early and rig
accordingly.

### Bone Count Budgets

| Platform | Recommended Max Bones |
|----------|----------------------|
| Desktop/console hero character | 100–150 bones |
| Desktop/console NPC | 50–80 bones |
| Mobile hero character | 50–75 bones |
| Mobile NPC / enemy | 25–50 bones |
| Rigid/mechanical objects | 5–20 bones |

These are soft limits — engine capability matters more than rule of thumb. Test
with the target platform.

---

## Skin Weights / Weight Painting

Skinning assigns each vertex a blend of bone influences. Each bone's influence is
a weight (0.0–1.0). Weights across all bones for one vertex must sum to 1.0.

### Standard: 4 Bone Influences per Vertex

Most real-time engines support 4 bone influences per vertex by default. Verify the
engine target — some allow 8, some are limited to 4 on mobile. Set the mesh's
influence limit to match.

### Weight Painting Principles

**Gradient at joints**: The weight transition from one bone to the next should be
a smooth gradient centered at the joint. Hard edges (weights switch sharply) cause
creasing and polygon splitting artifacts during deformation.

**No zero-weight vertices**: Vertices with no bone influence stay at the world
origin when the armature poses. Always assign every vertex to at least one bone
(even if that assignment is a static bone).

**Joint weight distribution for humanoids**:
- **Elbow/knee**: weights distribute across upper and lower limb bones with slight
  blending into the adjacent bone (shoulder or hip)
- **Shoulder**: complex — shoulder, upper arm, chest, and spine all share influence
  for natural deformation
- **Spine**: gradual blend across all spine bones for natural torso twist

### Weight Painting Workflow (Blender)

1. Bind the mesh to the armature (Ctrl+P → With Automatic Weights)
2. Enter Weight Paint mode
3. Select each bone; paint weights directly on the mesh
4. Use Smooth brush to blend transitions
5. Verify in pose mode: rotate each joint to extreme positions and check for
   artifacts (collapsing, candy-wrapper twist, pinching)

**Automatic weights as a starting point**: Blender's automatic weight calculation
is a useful baseline for organic characters. It requires correction at shoulders,
neck, and pelvis. Mechanical characters need manual weight painting — automatic
weights don't understand mechanical constraints.

---

## Blend Shapes / Shape Keys

Blend shapes (Unity/engine term) or Shape Keys (Blender) are vertex offset targets
stored on a mesh. Setting a blend shape weight to 1.0 moves every vertex toward its
target position.

### Facial Animation with Blend Shapes

The standard game pipeline for facial expression:

1. Model the neutral face (the basis shape)
2. Create a shape key for each expression: joy, anger, surprise, sad, disgust, fear
3. (For speech) Create phoneme targets: Ah, Oh, Ee, F/V (bilabial), B/M, etc.
4. Blend shapes are combined at runtime (multiple at 0–1 simultaneously)

**FACS (Facial Action Coding System)**: The anatomical framework for facial
expressions. Instead of emotion names (joy, anger), FACS defines Action Units (AUs)
— individual muscle groups:
- AU1: Inner brow raise
- AU4: Brow lowerer
- AU6: Cheek raiser
- AU12: Lip corner puller (smile)

FACS-based blend shapes can be combined to form any expression from the same small
set of building blocks. Most real-time facial systems (MetaHuman, ARKit blendshapes)
use FACS-derived targets.

### Corrective Shape Keys

Joint deformation creates artifacts — collapsing geometry at sharp bends, pinching
at shoulders, volume loss at elbows. Corrective shape keys fix these:

1. Pose the bone to the extreme position that shows the artifact
2. Create a shape key from that pose
3. Sculpt or move vertices to correct the artifact
4. Drive the shape key with the bone rotation: as the bone approaches its extreme,
   the corrective shape key blends to 1.0

**Driver in Blender**: Shape Key → Add Driver → set the driver to the bone's
rotation on the relevant axis. Adjust the curve to activate the corrective at the
right rotation range.

---

## Animation Fundamentals

### The 12 Principles — Applied to Game Animation

Not all 12 apply equally to game animation (which is often realistic/grounded):

| Principle | Game Animation Application |
|-----------|---------------------------|
| **Squash and Stretch** | Subtle (facial expressions, impact moments). Avoid for realistic human rigs |
| **Anticipation** | Short windup before major actions (attack swing, jump). Crucial for readability |
| **Staging** | Primary action clear in silhouette — enemy attack telegraphed from any camera angle |
| **Straight Ahead / Pose to Pose** | Pose-to-pose dominates game animation (block key poses, then refine) |
| **Follow Through** | Secondary motion continues after primary stops (hair, clothing, accessories) |
| **Secondary Motion** | Clothing, hair, soft body — must be controlled (not simulated) for game performance |
| **Timing** | The spacing of keyframes determines speed and weight |
| **Spacing** | Fast in → slow out (ease in/out) for natural physics; linear for mechanical |
| **Exaggeration** | More in stylized/cartoon games; minimal in grounded realistic games |
| **Solid Drawing** | Volume preservation through animation — no collapsing geometry |
| **Appeal** | Character personality through motion — even in a game context |
| **Arcs** | Natural body parts move in arcs, not straight lines |

### Keyframe Interpolation

The graph editor controls velocity between keyframes:

- **Linear**: Constant speed between keys. Mechanical, robotic. Use for machinery.
- **Bezier (ease in/out)**: Starts slow, accelerates, decelerates — natural motion.
  The default for organic animation.
- **Constant**: No interpolation — instant snap between values. Use for binary
  states (a light turning on/off).

**The graph editor is the primary animation workspace** for professional animators.
The viewport shows poses; the graph editor shows timing and spacing. Both perspectives
are necessary for quality animation.

### Looping Animations

Looping animations must begin and end in the same pose:

1. Keyframe the first frame
2. Copy those keyframes to the last frame (or use Blender's Cycle Modifier)
3. The in-between frames drive the motion
4. Verify: scrub forward and backward across the loop boundary — no pop

**Cycle offset**: Some locomotion (walk cycle) requires the feet to alternate. The
cycle modifier with a phase offset handles this — two copies of the same walk cycle
driven with a half-cycle offset drives left/right foot alternation.

---

## Game Animation Specifics

### State Machine Design

A character's animation state machine defines which animations play in which game
states and how transitions between them occur:

```
[Idle]
  ↓ (velocity > threshold)
[Walk]
  ↓ (velocity > run threshold)
[Run]
  ↓ (jump input)
[Jump]
  ↓ (landing)
[Land]
  ↓ (back to idle)
[Idle]
```

Transitions have:
- **Trigger conditions**: velocity, input, game state flags
- **Blend duration**: how long the cross-fade between animations takes (0.1–0.3s typical)
- **Exit time**: for non-interruptible animations, minimum percentage of animation
  played before transition is allowed

### Root Motion vs. In-Place

- **Root motion**: Animation drives character position. Import → Enable Root Motion
  in engine. The engine extracts the delta from the root bone each frame and applies
  it to the character capsule.
- **In-place**: All bones except root move. Engine code drives capsule position.
  Foot sliding must be corrected by matching animation speed to engine move speed.

### Blend Trees (Directional Movement)

A blend tree mixes animations based on a continuous parameter (typically velocity
direction). For a directional walk/run system:

- Center (0,0): Idle
- Up (0,1): Walk forward
- Right (1,0): Walk right
- Down (0,-1): Walk backward
- Upper-right (0.7, 0.7): Walk forward-right (blended from forward + right)

The engine blends animations proportionally based on the input 2D vector. This
produces smooth multi-directional locomotion from 4–8 directional clips.

### Animation Retargeting

Retargeting applies animation data from one skeleton to a different skeleton (same
general structure, different proportions). Use cases:
- Apply a library animation (Mixamo, Unreal mannequin) to a custom character rig
- Share animations across multiple characters with different body proportions

Requirements:
- Source and target skeletons must have the same bone hierarchy (same bone names,
  same parent-child relationships)
- Blender: built-in retargeting via copy pose constraints or the Rigify retarget
  addon
- Unreal Engine: IK Retargeter asset; requires IK Rig definition for both source
  and target

---

## Rigging for Legion

### Mechanical Entity Rigging

Von Neumann probes and mechanical entities in the Bobiverse are not biological.
Rigging considerations:

- **Rigid articulation**: Panel doors, hatches, thruster gimbal joints. Use simple
  FK chains or single-bone hinge constraints.
- **No deformation mesh**: Mechanical objects have no skin deformation. Bones drive
  rigid child objects (parented mesh pieces), not weighted vertices.
- **Modular construction**: Individual module pieces are each parented to their own
  bone. The armature defines the mechanical hierarchy.
- **Engine animation**: Thruster nozzles gimbal in response to movement direction.
  Implement as bone constraints driven by physics/logic in engine.

### Procedural Animation Hooks

For mechanical entities, procedural animation (driven by engine code responding to
physics state) is often better than authored keyframes:
- Stabilizing gyros that respond to camera movement
- Antennae or sensor arrays that track targets
- Mechanical legs that plant on terrain (IK-driven, engine-computed)

Route the "how to implement this in engine" question to lead-game-developer. This
skill covers the rig setup that enables those hooks.

---

## Quality Checklist

Before delivering a rig:

- [ ] Bone naming follows convention (project/engine standard, L/R suffixes for pairs)
- [ ] Rest pose is the intended bind pose (T-pose or A-pose, documented)
- [ ] All bone rolls are consistent and correct (check in Edit Mode, Overlay → Bone Axes)
- [ ] Bone count within platform budget
- [ ] IK chains have pole targets (no free-spinning elbows/knees)
- [ ] Weight paint: no zero-weight vertices
- [ ] Weight paint: smooth gradients at all joints
- [ ] Weight paint: maximum 4 bone influences per vertex (unless engine supports more)
- [ ] Shape keys: all targets blend cleanly without intersection artifacts
- [ ] Corrective shape keys in place for extreme joint positions
- [ ] All transforms applied on the mesh before skinning (scale = 1,1,1)
- [ ] Rig tested in engine: import, bind pose, animation playback all correct

Before delivering animations:

- [ ] Loop animations: first and last frame are identical
- [ ] Root motion: root bone moves correctly for intended locomotion type
- [ ] All keyframe interpolation intentional (not default bezier where linear needed)
- [ ] Graph editor reviewed for unintended velocity artifacts (overshoots, dips)
- [ ] State machine transitions tested (no pop at blend boundaries)
- [ ] Foot contact frames match terrain in-engine (no sliding)
