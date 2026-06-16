---
name: a11y-auditory
description: >
  Deafness, hearing impairment, captions, transcripts, visual notification alternatives,
  and sign language interpretation. Spoke skill in the lead-accessibility-architect
  network. Use this skill whenever the conversation touches: deafness, hearing impairment,
  hearing loss, hard of hearing, tinnitus, age-related hearing loss, presbycusis,
  captions, closed captions, subtitles, transcripts, audio description, sign language
  interpretation, visual alerts, notification sounds, alert tones, audio cues, autoplay,
  muted defaults, WCAG 1.2.1, WCAG 1.2.2, WCAG 1.2.3, WCAG 1.2.4, WCAG 1.2.5,
  WCAG 1.2.6, WCAG 1.4.2, audio control, video with captions, podcast accessibility,
  audio-only content, live captions, real-time captioning, CART, synchronous media,
  prerecorded media.
aliases: [a11y-auditory]
tier: cross-cutting
domain: accessibility
hub: lead-accessibility-architect
spec_version: "2.0"
---

# a11y-auditory

Specialist lens for hearing impairments: captions, transcripts, visual notification
alternatives, and audio accessibility. Part of the `lead-accessibility-architect`
skill network.

---

## Domain Boundary

This skill owns **auditory disability design** — captions, transcripts, visual
alternatives to audio cues, and hearing-aware content design.

- **Legal requirements for WCAG 1.2.x** → `a11y-legal-compliance`
- **Visual notification design (toast, badge)** → `ux-interaction-design`
- **Cognitive impact of complex audio content** → `a11y-cognitive`

---

## Hearing Impairment Spectrum

Hearing impairment exists on a spectrum with very different design implications
at each point:

| Classification | Hearing Loss | Design Priority |
|---------------|-------------|----------------|
| Profound deafness | No functional hearing | Captions, transcripts, visual alerts; BSL/ASL/signed languages may be primary language |
| Severe hearing loss | 70-95 dB loss | Hearing aids; captions essential; spoken content unreliable even with aids in loud contexts |
| Moderate hearing loss | 40-70 dB loss | Hearing aids; captions helpful; difficulty in poor acoustic conditions |
| Mild hearing loss | 25-40 dB loss | Often undiagnosed; captions still beneficial; difficulty in noisy environments |
| Tinnitus | Constant background noise | Difficulty discriminating audio against internal noise; captions reduce cognitive load |
| Age-related (presbycusis) | High-frequency first; affects ~1 in 3 over 65 | Difficulty with consonant discrimination; captions significantly helpful |

**466 million people worldwide have disabling hearing loss** (WHO). By 2050, WHO
projects over 900 million will have some form of hearing loss. Captioning is not
an edge-case accommodation — it is infrastructure.

**The deaf community** (capital-D Deaf) identifies with a linguistic and cultural
community centered on signed languages (ASL, BSL, Auslan, etc.). For many Deaf
users, English (or other spoken language) text is a second language. Plain language
and visual design quality matters more, not less.

---

## Captions

Captions are text equivalents of the audio content in synchronized media (video
with audio). They include dialogue, speaker identification, and meaningful sound
effects and music.

### Captions vs. Subtitles

**Captions**: Translation of ALL audio content for deaf/hard-of-hearing users:
- Dialogue (with speaker identification in multi-speaker content)
- Sound effects: `[Door slams]`, `[Notification chime]`
- Music descriptions: `[Upbeat jazz music playing]`
- Tone/manner indicators when relevant: `[Whispering]`, `[Sarcastically]`

**Subtitles**: Translation of dialogue only, for viewers who can hear but don't
speak the language. Subtitles are NOT the same as captions and do not satisfy
WCAG 1.2.2.

This distinction matters: auto-generated captions that only transcribe speech
without sound descriptions are incomplete captions. They satisfy a checkbox but
not the spirit of WCAG 1.2.2.

### WCAG 1.2.x Caption Requirements

| Criterion | Requirement | Level |
|-----------|------------|-------|
| 1.2.1 Audio-only and Video-only | Prerecorded audio needs a transcript; prerecorded video-only needs audio description or transcript | A |
| 1.2.2 Captions (Prerecorded) | All prerecorded synchronized media (video + audio) needs captions | A |
| 1.2.4 Captions (Live) | Live broadcasts need real-time captions | AA |
| 1.2.6 Sign Language (Prerecorded) | Sign language interpretation for prerecorded synchronized media | AAA |

**1.2.2 is Level A** — not AA. This means captions for prerecorded video are the
minimum bar, not an enhancement. Shipping video content without captions is a
critical WCAG failure.

### Caption Quality Standards

Caption quality matters as much as caption presence. Poor-quality captions are
better than nothing but create a worse experience than printed text:

**Accuracy**: Captions must accurately reflect what is spoken. Auto-generated captions
average 80-90% word accuracy on clean audio — this means 1 in 10 words wrong.
Errors compound in proper nouns, technical terms, and accented speech. Review and
correct auto-captions before publishing.

**Synchronization**: Captions must appear within 5 seconds of the corresponding
audio. Longer delays make it impossible to connect captions to on-screen action.
Most automated caption tools produce synchronization errors that require manual
correction in fast-spoken or overlapping speech.

**Completeness**: Include all relevant audio — sound effects that convey meaning,
music descriptions when music is used for emotional/narrative effect. A product
launch video that ends with triumphant music needs `[Triumphant music playing]`,
not silence in the caption track.

**Reading speed**: 130-160 WPM is the maximum comfortable reading speed for caption
content. Rapid speech may require paraphrasing rather than verbatim transcription
to maintain readable pacing.

**Display quality**: Captions must be readable as text:
- Sufficient contrast (caption text against caption background and against video)
- Caption background or semi-transparent overlay to ensure legibility over varying
  video backgrounds — white text on a light background fails
- User-adjustable size where technically feasible
- Default size sufficient to read without leaning toward the screen

### Live Captions

Real-time captioning (CART — Communication Access Realtime Translation) is used
for live events, meetings, and broadcasts. WCAG 1.2.4 requires live captions for
synchronized live media at AA.

Modern platforms:
- Zoom, Teams, Meet: built-in AI real-time captions (quality varies; significant
  improvement in recent years but still imperfect)
- CART services: professional human captioners with near-100% accuracy; used for
  high-stakes events
- Otter.ai and similar: AI transcription; quality similar to built-in platform tools

Design consideration: when building a live event platform or video conferencing tool,
caption controls must be accessible — captioning toggle must be keyboard accessible
and not buried in an inaccessible submenu.

---

## Transcripts

A transcript is a full text version of audio content. Unlike captions (synchronized
with media), a transcript is standalone text that can be read independently of the
media player.

### When Transcripts Are Required

- **Audio-only content** (podcast, audio description): WCAG 1.2.1 (Level A)
- **Video-only content**: WCAG 1.2.1 — needs either audio description or transcript

### Transcripts vs. Captions: Both Matter

Transcripts and captions serve related but different needs:
- Users who cannot hear and cannot watch (e.g., reading in a context where video
  is impractical) need the transcript
- Users who cannot hear while watching need captions
- Users who want to skim, search, translate, or reference content prefer a transcript
- Users in noisy environments often open a transcript even if they have normal hearing

A transcript also benefits SEO (searchable text), localization, and reuse.

### Transcript Quality

A good transcript includes:
- All spoken dialogue
- Speaker identification: "Host: How has the product changed? Guest: We've..."
- Relevant non-verbal audio: `[Applause]`, `[Question from audience]`
- Timestamps at intervals (every 1-2 minutes for long content) for easier navigation
- Heading structure — break the transcript into sections matching the content structure

---

## Visual Alternatives to Audio Cues

Products frequently use sound to communicate state — notification sounds, error
tones, success chimes, alert beeps. Each audio cue needs a visual alternative.

| Audio Cue | Visual Alternative |
|-----------|------------------|
| New message notification sound | Toast/badge with unread count |
| Error tone (form submission) | Error message with visible error state |
| Success chime (action completed) | Success confirmation message or visual state change |
| Alert/warning tone | On-screen alert message with appropriate visual design |
| Progress sound (download, upload) | Visual progress indicator |
| Ding (timer complete) | Visible timer completion state or full-screen notification |
| System sounds (email, calendar) | System notification with visual indicator |

### Autoplay Audio

**WCAG 1.4.2 Audio Control**: If audio plays automatically for more than 3 seconds,
users must be able to pause/stop it or control its volume independently of the
system volume.

This is particularly important for deaf and hard-of-hearing users who may have
hearing aids or cochlear implants that interface with system audio in complex ways —
unexpected audio through an aid is painful or disorienting.

**Best practice**: Default to muted for all autoplay audio and video. Provide an
explicit opt-in for audio, not an opt-out.

---

## Sign Language

Approximately 70 million people worldwide use signed languages as a primary or
preferred language. For many Deaf users, signed languages are their first language;
written text in a spoken language is a second language.

**WCAG 1.2.6 Sign Language (Prerecorded)** (Level AAA): Sign language interpretation
for all prerecorded synchronized media.

Although AAA, sign language interpretation is worth considering for products:
- Serving Deaf communities or public-facing government services
- Where critical safety or legal information is conveyed via video
- In regions with specific legal requirements for sign language access

**Design considerations for embedded sign language video**:
- Signer must be visible and large enough to read clearly (minimum 25% of video height)
- Signer positioned in a consistent area (typically bottom-right)
- High contrast between signer and background (interpreters typically wear solid
  neutral tops)
- Adequate lighting and video quality — low resolution makes handshapes illegible

---

## Hearing Aid and Cochlear Implant Considerations

Users with hearing aids and cochlear implants (CIs) have specific audio needs
that go beyond simple captioning:

**Telecoil (T-coil) compatibility**: Many hearing aids have a telecoil setting for
direct electromagnetic coupling to audio sources. This is more relevant to physical
spaces but relevant to browser and OS audio routing in kiosk/dedicated-device contexts.

**Audio quality**: Hearing aids process audio in ways that can make low-quality audio
(heavily compressed, with background noise, with clipping) harder to understand than
for people without aids. Clean, uncompressed audio is better for aid users.

**Sudden loud sounds**: Automatic gain control in hearing aids and CIs handles loud
sounds differently; sudden volume spikes (notification sounds, attention sounds at
high volume) can be uncomfortable or painful. This reinforces the recommendation to
default all audio to muted with user opt-in.

---

## Quality Checklist

- [ ] All prerecorded video has captions (WCAG 1.2.2 — Level A)
- [ ] All prerecorded audio-only content has a transcript (WCAG 1.2.1)
- [ ] Captions are accurate (reviewed, not raw auto-generated)
- [ ] Captions include sound effects and music descriptions (not just dialogue)
- [ ] Caption contrast is sufficient (caption text against background)
- [ ] Live video content has real-time captions where technically feasible (WCAG 1.2.4)
- [ ] All audio notification cues have visual equivalents
- [ ] Autoplay audio defaults to muted or does not autoplay (WCAG 1.4.2)
- [ ] Users can control audio volume independently (WCAG 1.4.2)
- [ ] Transcripts are provided for audio-only content
- [ ] Transcripts include speaker identification and non-verbal audio notes
- [ ] No information conveyed solely through audio without visual alternative

---

## Cross-Links

| Skill | Relationship |
|-------|-------------|
| `a11y-legal-compliance` | WCAG 1.2.x legal requirements — this spoke provides design depth; legal-compliance owns the audit framework |
| `a11y-cognitive` | Cognitive impact of dense audio content; plain language in transcripts for users with reading difficulties |
| `a11y-neurodiversity` | Audio control for sensory-sensitive users; auditory sensory overload triggers |
| `ux-interaction-design` | Visual notification design (toast, badge) as audio alternatives |
| `lead-accessibility-architect` | Hub — routes to this spoke for captions, transcripts, audio alternatives, and WCAG 1.2.x |
