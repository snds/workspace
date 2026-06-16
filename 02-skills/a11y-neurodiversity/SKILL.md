---
name: a11y-neurodiversity
description: >
  Autism spectrum, sensory processing, predictability, sensory overload, executive
  function, and vestibular/motion sensitivity. Spoke skill in the lead-accessibility-architect
  network. Use this skill whenever the conversation touches: neurodiversity, autism,
  autism spectrum condition, ASD, Asperger's, sensory processing, sensory sensitivity,
  sensory overload, predictability, consistent navigation, literal language, social
  cues in UI, Tourette syndrome, dyspraxia, dyscalculia, proprioception, spatial
  processing, prefers-reduced-motion, reduced motion, vestibular disorder, vestibular
  migraine, motion sickness, animation sensitivity, ambient animation, looping animation,
  parallax, executive function, task initiation, task switching, planning, sequencing,
  breadcrumbs, shallow navigation, hypersensitivity, hyposensitivity, sensory diet,
  reduced contrast mode, low stimulation mode, environmental customization.
---

# a11y-neurodiversity

Specialist lens for neurodiversity: autism spectrum design, sensory processing
accommodation, motion sensitivity, and executive function support. Part of the
`lead-accessibility-architect` skill network.

---

## Domain Boundary

This skill owns **neurodivergent-specific design patterns** — autism, sensory
processing, motion sensitivity, and executive function from a neurodivergent perspective.

- **ADHD-specific patterns and cognitive load** → `a11y-cognitive` (significant overlap; ADHD spans both)
- **Legal requirements** → `a11y-legal-compliance`
- **Motion and animation design within accessibility constraints** → `lead-motion-designer`/`motion-accessibility`
- **Predictable information architecture** → `lead-information-architect`/`ia-enterprise-complexity`

---

## Neurodiversity as a Design Frame

Neurodiversity is the recognition that human neurological variation is a natural
and valuable form of human diversity, not a disorder to be corrected. Neurodivergent
conditions include:

- Autism spectrum conditions (ASC/ASD)
- ADHD (shared significantly with `a11y-cognitive`)
- Dyslexia (shared with `a11y-cognitive`)
- Dyspraxia / developmental coordination disorder (DCD)
- Dyscalculia
- Tourette syndrome
- Sensory processing differences (SPD)

An estimated 15–20% of the population is neurodivergent in some way. Designing for
neurodivergent users is designing for a significant, often-ignored segment. Many
neurodivergent users do not identify as "disabled" and will not appear in disability
self-identification surveys — but they still experience friction in neurotypically-designed interfaces.

---

## Autism Spectrum Design

Autism spectrum conditions (ASC, also written ASD) are characterized by differences
in social communication, sensory processing, need for predictability, and often
(but not always) intense focused interests. There is enormous variation within the
spectrum — "high-masking" autistic professionals often have no obvious support needs
but experience significant friction from poorly-designed interfaces.

### Predictability

Unpredictability is cognitively and emotionally costly for many autistic users.
Inconsistent behavior violates the learned mental model and requires re-evaluation.

**Design principles**:
- Navigation must be in the same location on every page — do not rearrange primary
  navigation between sections
- Interactive elements must behave consistently — if a card navigates to a detail view,
  every similar card must navigate the same way (see also `a11y-cognitive`)
- UI changes must be explicit and communicated — a state change that is implied
  through subtle color or opacity shift may be entirely missed; use explicit labels,
  icons, or messages to communicate state changes
- Avoid "smart" UI changes that happen without user action — auto-collapsing sidebars,
  auto-refreshing content, and content that reorders or changes position without user
  input violate predictability expectations
- Modal dialogs must behave predictably — the escape key closes them, the close button
  closes them, clicking the overlay closes them; modal behavior that deviates from
  this convention requires explicit communication

### Literal Language

Many autistic users process language literally. UI text that relies on metaphor,
idiom, or implied meaning creates comprehension barriers.

**Failure patterns**:
- "Let's get started!" — implies the system has social initiative; creates ambiguity
- "Something went wrong" — describes nothing; provides no recovery path
- "Click here to learn more" — what will I learn? About what?
- Error text that uses passive voice to avoid assigning blame: "An error was encountered"
  — who encountered it? What error?
- Ambiguous pronoun references: "Change your settings to update it" — what is "it"?

**Design principles**:
- All instructions should be explicit, step-by-step, and literal
- All error messages should state exactly what failed and exactly how to fix it
- Avoid rhetorical questions in UI text
- Avoid social pleasantries that serve no functional purpose ("Hi, Sarah!") in
  functional contexts (form labels, error messages, status updates)
- When using metaphors that are established conventions (trash for delete, folder for
  directory), use consistent and clearly-established metaphors only — do not introduce
  new metaphors that require inferring meaning

### Social Processing in UI

Some UI designs simulate social dynamics that require social inference skills:
- Friend requests and social graph features
- Ambiguous notifications ("X is thinking about you")
- Reaction systems with culturally-loaded emoji meanings
- Group dynamics indicators

For autistic users who process social signals differently, these features may be
confusing, misread, or anxiety-inducing. Design social features with explicit,
literal communication alongside or instead of implicit social signals:
- Explicit meaning: "X liked your post" not just a ♥ counter
- Explicit relationship states: "X follows you" not just implied connection
- Explicit invitation language: "X wants to connect with you" not ambiguous engagement nudges

---

## Sensory Processing

Sensory processing differences affect how the nervous system receives, integrates,
and responds to sensory input. Both hypersensitivity (over-responsive) and
hyposensitivity (under-responsive) occur across all senses, including:
- Visual (light, color, contrast, motion, visual complexity)
- Auditory (volume, frequency, sudden sounds)
- Tactile (haptic feedback on devices)

### Visual Sensory Sensitivity

Some users — particularly autistic users and those with sensory processing disorder —
experience high contrast, bright colors, and dense visual complexity as genuinely
uncomfortable or overwhelming.

**Design responses**:
- **Reduced contrast mode**: an alternative to high-contrast mode; provides softer,
  lower-saturation color schemes for users who find standard contrast uncomfortable
  — distinct from `prefers-contrast: less` in CSS which is intended for low vision
  correction
- **Low stimulation mode**: reduces visual decoration, removes ambient animation,
  reduces color saturation — a mode for users who need a calmer interface
- **Reduced color saturation option**: very saturated colors (particularly yellow,
  orange, bright green) can be uncomfortable; offering a desaturated palette option
  provides accommodation without degrading the default experience
- **Avoid pure white (#FFFFFF) backgrounds as the only option**: some users with
  sensory sensitivity (and dyslexia) find high-luminance backgrounds uncomfortable;
  offer off-white or cream alternatives

### Ambient and Continuous Animation

This is the highest-priority sensory processing concern for digital products:
**continuously moving elements are significantly distressing and distracting for
users with sensory processing sensitivity, autism, ADHD, and vestibular disorders.**

**`prefers-reduced-motion` must eliminate ALL ambient animation**. "Ambient" means:
- Background video or parallax effects
- Loading spinners that remain visible during idle states
- Looping GIFs or animated illustrations
- Auto-playing carousels or slideshows
- "Idle" animations on UI elements (subtle breathing effects, pulsing indicators)
- Animated transitions between states that recur repeatedly

`prefers-reduced-motion` should NOT eliminate:
- Focus indicators that use motion (reduce, but some motion feedback is appropriate)
- Single-occurrence transitions that the user explicitly triggered (page navigation,
  opening a dialog) — these can be reduced to instant or near-instant

**CSS pattern**:
```css
@media (prefers-reduced-motion: reduce) {
  *,
  ::before,
  ::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
  }
}
```

### Auditory Sensory Sensitivity

Sudden or unexpected sounds are a significant sensory trigger:
- Default all media to muted; require explicit user opt-in to sound
- Avoid notification sounds that play by default
- Never play audio without user initiation in a background tab
- UI interaction sounds (button clicks, confirmation chimes) should be opt-in globally
  for users who cannot tolerate them

### Haptic Feedback

On mobile devices, haptic feedback is used to communicate confirmation, error,
and notification states. For users with tactile sensory sensitivity:
- Platform haptic intensity settings (iOS/Android system level) should propagate to
  in-app haptics where technically possible
- High-intensity haptic feedback for routine actions (every keystroke, every tap)
  may be distressing; reserve for notifications and significant state changes only

---

## Vestibular Disorders and Motion Sensitivity

Vestibular disorders affect the inner ear balance system and affect approximately
35% of adults over age 40. Visual motion (animation, parallax, scrolling effects)
can trigger vertigo, nausea, and disorientation — symptoms that make a website
or app completely unusable during an episode.

Conditions: vestibular migraine, BPPV (benign paroxysmal positional vertigo),
labyrinthitis, Meniere's disease, post-concussion syndrome, motion sickness.

### Vestibular Triggers in Digital Design

| Effect | Risk Level |
|--------|-----------|
| Parallax scrolling (elements at different speeds) | High — depth and motion illusion is directly vestibular-triggering |
| Large background video | High — large-field motion is more triggering than small motion |
| Sticky elements with parallax offset | High |
| Zoom/scale transitions | Moderate |
| Slide transitions across full viewport | Moderate |
| Subtle fade transitions | Low |
| Small, contained loading spinners | Low |

**Rule**: Any motion that affects a large portion of the viewport, or creates
a depth/parallax illusion, is a vestibular risk. `prefers-reduced-motion` must
disable these — not reduce them. Route to `lead-motion-designer`/`motion-accessibility`
for animation design that respects this constraint.

---

## Proprioceptive and Spatial Processing

Proprioception is the sense of one's body in space. Spatial processing involves
the mental representation of spatial relationships — including navigation hierarchies.

Some neurodivergent users (and many users generally) have difficulty tracking their
location in complex navigation hierarchies. "Where am I?" is a high-cognitive-load
question when the navigation architecture is deep, inconsistent, or lacks orientation cues.

**Design responses**:
- **Breadcrumbs**: persistent orientation in hierarchical navigation
- **Current location indicators**: active state in navigation clearly distinguishes
  where the user currently is
- **Page titles**: every page/view has a unique, descriptive title (browser tab + page heading)
  that answers "where am I?" without requiring the user to read the navigation
- **Shallow IA**: fewer navigation levels reduces the spatial tracking burden; route
  to `lead-information-architect` for IA decisions
- **Consistent visual zones**: content areas, navigation, and actions always in the
  same visual regions across pages — the spatial memory of "navigation is always
  at the top-left" is a significant accommodation

---

## Executive Function from a Neurodivergent Perspective

Executive function affects task planning, initiation, switching, and sustained
effort toward a goal. This is shared with ADHD (`a11y-cognitive`) but deserves
additional depth for autistic users and those with DCD/dyspraxia.

### Task Switching

Switching between tasks or contexts has a higher cognitive cost for many neurodivergent
users. Design implications:
- Minimize unsolicited context switches (auto-opening dialogs, redirects, notifications
  that require immediate attention)
- When context switches are necessary, prepare the user: "You'll be redirected to
  your account settings page" rather than silent redirect
- Preserve state when context switches occur — if a user is mid-task and must respond
  to a notification, their work should be preserved and easy to return to

### Explicit Structure

Many neurodivergent users benefit from explicit, visible structure that neurotypical
users often process implicitly from visual grouping and whitespace:
- Explicit section labels, not just visual spacing to imply sections
- Explicit step counts in multi-step flows ("Step 2 of 5")
- Explicit relationship language in navigation: "Related products" not just a product
  carousel appearing below

---

## Quality Checklist

- [ ] `prefers-reduced-motion` disables all ambient/looping animation
- [ ] No autoplay video or audio; all media defaults to muted
- [ ] Navigation in consistent location across all views
- [ ] Interactive element behavior consistent across similar contexts
- [ ] State changes communicated explicitly (label, icon, message) — not only through
      subtle color/opacity shifts
- [ ] All UI text is literal and unambiguous — no idioms, metaphors, or implied meaning
      in functional copy
- [ ] Error messages state exactly what failed and exactly how to fix it
- [ ] Breadcrumbs or consistent location indicators present in deep hierarchies
- [ ] Page titles unique and descriptive for each view
- [ ] No parallax or large-field motion effects (vestibular risk)
- [ ] Ambient animation absent; loading spinners contained and small
- [ ] Modal behavior consistent (Escape closes, overlay click closes, close button closes)
- [ ] Reduced contrast / low stimulation mode available for users with sensory sensitivity
      (when product warrants it)
- [ ] Task flows support interruption and resumption; state preserved across context switches

---

## Cross-Links

| Skill | Relationship |
|-------|-------------|
| `a11y-cognitive` | ADHD, executive function, and cognitive load overlap; route there for working memory, plain language, COGA SC depth |
| `lead-motion-designer` / `motion-accessibility` | `prefers-reduced-motion` is the primary implementation surface for vestibular accommodation in motion design |
| `a11y-legal-compliance` | WCAG 2.3.1 (flashing), 3.2.1/3.2.2/3.2.3/3.2.4 (predictability criteria) |
| `a11y-assistive-tech` | `forced-colors` and WHCM testing; media query handling in AT-tested environments |
| `uid-color-for-ui` | Color saturation for sensory-sensitive users; dark mode and forced-colors token system |
| `lead-accessibility-architect` | Hub — routes to this spoke for ASD design, sensory processing, prefers-reduced-motion, and sensory overload |
