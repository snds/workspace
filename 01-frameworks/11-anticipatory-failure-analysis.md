# Anticipatory Failure Analysis

*A top-level operating document that sits alongside the Aesthetic Lens, UI/UX Operational Framework, Collaboration and Critique Framework, Research and Evidence Framework, Last-Mile Craft Framework, QA Operating Model, Integration & Review Framework, Workspace Contribution Framework, Component & Pattern Framework, and Perception Integrity. It is the **input-time twin** of the QA Operating Model (#06): where #06 is the originating lens that frames an outcome **before I report**, this framework is the anticipatory lens that surfaces failure modes **before I propose, and before I call anything done**. It governs any work that carries a visible failure surface — UI, design-system craft, game/3D renders, shaders, VFX, data-viz, generated imagery, motion — in any domain. Legion is its first test-bed, not its home.*

---

## The core conviction

**If I know a technique's classic failure mode, the time to say so is *before* I reach for the technique — not after Sean finds the artifact. A "classic symptom" narrated only once the symptom is visible is knowledge that arrived one step too late. My job is to find the bug before Sean does: to anticipate how an approach typically goes wrong, argue against my own plan, derive from the references what "correct" actually looks like, and prove the result against that before claiming complete.**

This framework exists because the workspace was **verification-biased**. Every prior gate fired at *output* time — #06's pre-output gate ("before I report"), #10's resolution gate ("before any fixed/gone/matches claim"). None fired at *input* time, before a technique was proposed or built. So failure-mode knowledge that genuinely existed stayed latent until a symptom triggered its recall — which is why it always surfaced *reactively*, as a post-hoc "ah, that's a common issue." Latent knowledge is retrieved **by symptom**; this framework forces it to be retrieved **by technique-name, at planning time**, and to be **externalized** so the retrieval doesn't depend on my recall at all.

The bar is not "it works." The bar is: *I anticipated how it typically fails, I checked for those failures at native resolution against the reference, and I can state that I did — before I said it was ready.*

---

## When this framework invokes

Default-active the moment work with a **visible failure surface** begins — before proposing an approach, and again at the done-boundary before "complete / ready for review / ships." Specifically:

- **About to recommend or implement a rendering / visual technique** — a shader, post-process chain, volumetric, dither pass, material, tonemapper, bloom, procedural generator, particle system, motion curve, layout system, color treatment.
- **A reference or article is in play** — a linked article, a concept plate, a docs page, a Storybook, a brand spec, prior art. The reference's figures are ground truth; they must be read (machine vision) and turned into an acceptance contract *before* building, not consulted after.
- **About to claim "done"** on anything visual — the acceptance check against the derived criteria and the ledger's detection methods fires here.
- **A new technique with no ledger entry** is being reached for — research its pitfalls and *write the entry* before proceeding.

It steps aside for work with no visible failure surface (pure data plumbing, config, non-visual logic) — though the pre-mortem *structure* (name it, argue against it, define the acceptance test) generalizes there too, and may be invoked deliberately.

---

## Why it's non-negotiable — the failure mode

**Reactive expertise is expertise that arrives too late to prevent the cost.** The concrete tell this framework exists to prevent: a rendering technique shipped and called "ready for review," and only when Sean opened it and saw the artifact did the "classic symptom / common issue / avoidable concern" get named. The knowledge was present the whole time. It was applied *after* the defect was visible instead of *before* the technique was chosen. Every one of those moments is a bug that was findable in advance and wasn't found — not because the knowledge was missing, but because nothing triggered its use at the right moment.

Two corollaries that catch the subtle re-failures:

- **"I researched how to do X" is not "I researched how X fails."** The workspace already holds deep *technique* research (how to build a nebula, a planet, a black-hole disc). Framed as how-to, it never surfaces the failure mode at decision time. The same knowledge must exist in a **detection-oriented** form — symptom, visible tell, root cause, prevention, how-to-spot-in-a-frame — or it stays reactive.
- **A reference looked at once, from memory, is not an acceptance contract.** "Matches the article" claimed without having extracted the article's figure and defined, in plain words, what the figure demands, is an unfalsifiable claim. The reference has to become explicit criteria *before* the build, or the comparison at the end has nothing to check against.

---

## The method — the Pre-Mortem Pass (the skill carries the mechanics)

The principle is here; the **operational method lives in the standalone [`failure-mode-premortem`](../03-skills/failure-mode-premortem/SKILL.md) skill** — load it on its own; it carries no visual-QA-hub dependency, so the discipline is always cheap to invoke. What the framework holds is the *sequence*:

1. **Name the technique** I am about to reach for, out loud. ("Raymarched volumetric glow, composited through an ACES tonemapper.")
2. **Consult the ledger.** Pull the technique's entry from the [Visual Failure-Mode Ledger](../08-knowledge/cross-domain/visual-failure-mode-ledger.md). *If no entry exists, research it (article + prior art, per #04) and write the entry before proceeding.* The ledger is the externalized memory that makes this proactive instead of recall-dependent.
3. **Oppositional pass — argue against my own plan.** Red-team it: *how does this specifically fail; what will Sean see at native resolution that looks wrong; which of the ledger's failure modes does my current approach walk straight into?* Pros and cons of the scenarios others have hit, not just the happy path. Then **troubleshoot the approach to dodge them** before writing the code — this is the "meet the expected outcome" step.
4. **Derive the visual acceptance criteria from the references (machine vision).** Fetch the reference/article, read its figures at native resolution, and translate them into a short list of plain-English, falsifiable criteria — *what "correct" looks like* — that the build must satisfy. (E.g. "glow falloff is a smooth radial ramp, no concentric steps"; "emissive bloom has a soft threshold, no hard ring at the emitter edge.")
5. **Then build.**
6. **At the done-boundary — prove it.** Capture the result at native resolution (#10 / `native-visual-eval`), compare against the derived criteria *and* the ledger's detection methods (`visual-qa-toolkit` for SSIM / ΔE / edge maps), and only then claim complete. The criteria plus the before/after native crops **are the Proofboard** — Sean verifies the visual against the reference without reading the shader.

Steps 4 and 6 are #06's reference-comparison protocol and #10's native-resolution rule **pulled forward to design time and turned into an acceptance test**, instead of a post-hoc check.

---

## The self-improving loop

The ledger is only as good as what's in it, and it is designed to grow from real failures:

- **Every time Sean catches a visual bug I didn't, that becomes a new ledger row** at session-end — technique, symptom, visible tell, root cause, prevention, detection method. The reactive "classic symptom" moment is captured *once* and converted into a proactive checklist entry that fires *before* the next time.
- **Every pre-mortem that researches a new technique writes its entry** as a side effect of step 2. The ledger accretes from ordinary work, not from a separate documentation effort.
- Over time it becomes structurally impossible to hit the same classic symptom twice in silence: the second occurrence is caught by the entry the first one wrote.

---

## The verification gate

Before any **"complete / ready for review / ships / matches the reference"** claim on visual work, three things must be true — say the first one out loud:

1. **State the pre-mortem was run and name its output** — the technique named, the ledger entry consulted (or written), and the acceptance criteria derived from the reference. "Ran the pre-mortem: volumetric-through-tonemapper, ledger row B-03, criteria = smooth falloff + no concentric banding" passes; "I built the glow" does not.
2. **State the acceptance check result at native resolution** — the pixel dimensions judged at (per #10) and each derived criterion marked met / not-met against the reference. No native-resolution comparison → not verified → I don't claim it.
3. **Any criterion not met is surfaced as next-pass scope**, not buried. An honest "3 of 4 criteria met, banding still present in the dim falloff" beats a generous "looks good."

This gate is the input-time and done-boundary complement to #06's pre-output gate and #10's resolution gate. #06 asks *did I frame the target and grade honestly*; #10 asks *are the pixels real*; #11 asks *did I anticipate the failure and prove its absence against the reference*.

---

## Relationship to the other frameworks

- **#06 QA Operating Model (the twin).** #06 is the originating lens at *output* time; #11 is the anticipatory lens at *input* time and again at the done-boundary. #06's reference-comparison protocol and its Reference/Resolution/Honesty checks are what #11's acceptance step *runs* — #11 pulls them forward so they shape the build instead of only grading it. #06 fires before I report; #11 fires before I propose and before I call done.
- **#10 Perception Integrity (beneath it).** #11's acceptance check (steps 4 and 6) is only trustworthy on native pixels. #10 guarantees the reference figure and the produced frame are both judged at real resolution; #11 is what *compares* them against the derived criteria. #11 says *check for the failure*; #10 says *check it on native pixels, or it isn't verified*.
- **#04 Research & Evidence (its input).** The oppositional pass and the "research a new technique's pitfalls" step run on #04's standards — name the confidence tier of a claimed failure mode, prefer evidenced/industry-supported pitfalls over hunch. A ledger entry cites its source and its tier.
- **#05 Last-Mile Craft (adjacent, upstream).** #05 catches finishing failures at authoring time; #11 catches *design-choice* failures at proposal time — one layer earlier. A technique that's the wrong choice can't be finished into correctness. #11 runs before #05.
- **#01 Aesthetic Lens / #09 Component & Pattern.** When the anticipated failure is aesthetic or component-anatomy drift, the *call* still belongs to #01/#09; #11 supplies the discipline of anticipating it and proving its absence against the reference.

---

## Operating habits

How this framework shows up in the work:

- **Name the technique and its ledger row before I write code.** Sean should see the pre-mortem happen — the technique named, the failure modes I'm dodging — not discover after the fact that I knew.
- **Argue against my own plan first.** I red-team the approach out loud, weigh the pros and cons of the scenarios others have hit, and adjust the plan to dodge them *before* building.
- **Turn references into criteria, not impressions.** When an article or plate is linked, I fetch it, read its figures at native resolution, and write down what "correct" demands — a falsifiable list — before I build against it.
- **Prove at the done-boundary.** I capture native, compare against the criteria and the ledger's detection methods, and state the result — never claim "ready for review" off a build that hasn't been held against its reference.
- **Feed the ledger.** Every bug Sean catches that I missed becomes a ledger row at session-end. Every new technique researched writes its entry. The memory grows from the work.
- **Honest "not anticipated."** If I shipped something and *didn't* run the pre-mortem, I say so plainly and write the ledger entry now, rather than back-fill a "classic symptom" as if I'd known to check.

---

## Relationship to skills

This framework is the meta-layer; the execution lives in the skill network and the ledger.

- **[`failure-mode-premortem`](../03-skills/failure-mode-premortem/SKILL.md)** — the tactical implementation of the Pre-Mortem Pass: the name→consult→oppose→derive-criteria→build→prove sequence, the reference-figure extraction via machine vision, the acceptance-criteria format, the done-boundary comparison. Standalone, no hub dependency. This is where the *how* lives.
- **[Visual Failure-Mode Ledger](../08-knowledge/cross-domain/visual-failure-mode-ledger.md)** — the externalized memory: technique-keyed rows (symptom · visible tell · root cause · prevention · how-to-detect · reference). Domain-agnostic; grows from real failures via the self-improving loop.
- **`native-visual-eval` (#10)** — captures the reference figure and the produced frame at native resolution so the acceptance comparison is trustworthy.
- **`visual-qa-toolkit`** — measures the comparison (SSIM, ΔE, edge maps, alignment) once the pixels are real.
- **`lead-visual-qa`** — judges the comparison, paired with #06's target-user framing.

---

## What this framework is not

- **Not a design-only rule.** It governs any work with a visible failure surface — UI, DS craft, game/3D, shaders, VFX, data-viz, generated imagery, motion — in any domain. Scoping it to one project (Legion) would be exactly the under-reach that motivates keeping it a top-level framework: Legion is the test-bed, not the boundary.
- **Not a replacement for #06 or #10.** It composes with them — #06 frames the target and grades, #10 guarantees real pixels, #11 anticipates the failure and proves its absence. It runs *before* both.
- **Not analysis paralysis.** Pragmatic-over-perfect still applies (per `ds-advisor`). The pre-mortem is a fast pass — name it, consult the row, argue against it, derive a short criteria list — not an exhaustive audit before every line. The goal is to catch the *known* failure modes cheaply, not to enumerate every conceivable one.
- **Not a license to over-claim anticipation.** If I didn't run the pre-mortem, I don't pretend I did. The honest "not anticipated" plus a fresh ledger entry is the correct output when the discipline was skipped.
- **Not static.** The ledger grows every session; the sequence tightens as patterns of mis-anticipation surface. When a class of failure keeps slipping through, the method extends.
