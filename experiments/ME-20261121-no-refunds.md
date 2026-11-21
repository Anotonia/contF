# Production spec — ME-20261121-NO-REFUNDS (v0.1)

- Channel: Maya & Ethan, vertical 9:16 Short, 18s, silent-readable (no dialogue).
- Research lineage: [2026-11-21 radar](../research/2026-11-21-viral-radar-multiplatform-visual.md), H11 [untested]. Structure only; no reference footage, dialogue, props, sound, likeness or framing reused.
- Status: **script + A/B design approved by owner 2026-11-21** (relayed by the Bot). **Not approved:** spend, paid generation, character designs, publishing. Every shot `review_status: pending`.
- Machine-readable ShotSpecs (schema 0.2.0, compatible with the unmerged `contf.shot_pipeline` on PR #9; validated there, 18.0s each): [variant A](ME-20261121-no-refunds/variant-a.shots.json), [variant B](ME-20261121-no-refunds/variant-b.shots.json). Extra fields (`shot_scale`, `camera`, `props`, `onscreen_text_in_post`, `sound_in_post`, `variant_scope`) are informational and ignored by that validator.

## Hypothesis and single variable

- Hypothesis (from H11): with an identical setup, ending on the third character's refusal **held in the shared wide** (A) makes the reversal more legible / more replayable than **cutting to an isolated close-up** of the protagonist (B). Untested; no winner can be declared from one pair.
- Primary variable: **final 3s framing only** (S06A vs S06B). S01–S05 are one shared, identical render used in both cuts; cast, timing, props, sound and captions are fixed.

## Shot list (both variants)

| Shot | Time | Beat | Frame / camera | Action | Text & sound added in edit |
| --- | --- | --- | --- | --- | --- |
| S01 | 0–2s | hook | medium-wide two-shot + Biscuit at floor, static eye level | Ethan slides sticky-note coupon book to Maya | "1 FREE DISHWASH" readable muted by 2.0s; slide foley |
| S02 | 2–5s | setup | medium on Maya, static | Maya tears out a coupon, hands it back | paper tear |
| S03 | 5–8s | conflict | top-down insert, static | Ethan's finger taps the tiny print | "EXPIRED" tiny print; tap |
| S04 | 8–13s | escalation | medium two-shot, static, no push-in | Maya flips: every page stamped; Ethan crouches, offers book to Biscuit | EXPIRED stamps; page flips |
| S05 | 13–15s | reversal | wide shared frame, all three full-body | Biscuit takes the book, drops it at Ethan's feet, turns away | soft drop |
| **S06A** | 15–18s | payoff | **same wide held** | Biscuit trots out; Ethan stares at the book; Maya folds arms | paws off |
| **S06B** | 15–18s | payoff | **isolated close-up of Ethan** | Ethan's deadpan defeat; Biscuit exits unseen | paws off (off-screen) |

Loop: last frame (book on floor) reads into S01's book-on-counter.

## Character and stage bible

- **Maya:** composed, dry, unimpressed; reacts with small, precise expressions. Never mugs to camera.
- **Ethan:** proud, then quietly defeated; physical comedy through posture (crouch, offering with both hands), not big faces.
- **Biscuit (dog):** calm, deliberate; the refusal must read as a choice (take → drop → turn away), not an accident.
- **Looks: not specified here on purpose.** Use the owner's existing approved Maya/Ethan/Biscuit reference sheets (face, hair, wardrobe, breed/coat). None are in this repo; if Biscuit has no approved design yet, the owner must approve one before any frame is generated.
- Stage: one home kitchen, warm late-afternoon light, one counter, one coupon book (blank sticky-note pages). Same wardrobe, light and prop placement in every shot.
- **No text inside generated footage.** Coupon wording and stamps are composited in edit (generators garble text).
- Audio: no dialogue, no voice clones, no music by default; foley only, from an owned or licensed library.

## Production QA gates (per shot, before accept)

CHARACTER_DRIFT (faces/coat across S01–S06), OBJECT_CONTINUITY (book: size, colour, page count; drop position in S05 = S06A), MOTION_ARTIFACT (dog mouth/paws in S05), JOKE_NOT_LEGIBLE (muted viewer can say "who rejected the coupons?"), TEXT_OVERFLOW (captions inside 9:16 safe area), HOOK_UNCLEAR (premise readable by 2.0s). S06A must be continuous with S05 (same framing, no jump).

## What production needs

1. Owner-approved character reference assets for Maya, Ethan and Biscuit (blocking; not in repo).
2. A provider account + API key held outside Git, and a written **budget cap** (spend approval).
3. Per-shot receipts recording model, version, attempt, duration, actual billed cost and reviewer decision (`cost` stays null until a real billing record exists).
4. Local edit: ffmpeg composite of text overlays and foley; owned/licensed foley source.
5. Human review time per shot (unmeasured) and a separate publishing approval.

## Cost estimate (not authorized, not spent)

Source: [Runway Dev API pricing](https://docs.dev.runwayml.com/guides/pricing/), accessed 2026-11-21: $0.01 per credit; per-second rates below; tax may apply. Rates are time-sensitive — recheck before spend.

Unique footage to generate: S01–S05 shared (15s) + S06A (3s) + S06B (3s) = **21s**; S03 can instead be a local still + composite (then 18s). Assumption (not evidence): **3–5 attempts per accepted shot**, billed by output seconds. Clip-length granularity / per-generation minimums were not verified for these models; if every attempt bills ≥5s, a pass is 7 × 5 = 35s and costs roughly 1.7× the figures below.

| Model (no-audio rate; foley added in edit) | Rate | 21s × 3 attempts | 21s × 5 attempts |
| --- | --- | --- | --- |
| `veo3.1_fast` | 10 cr/s = $0.10/s | $6.30 | $10.50 |
| `gen4.5` / `kling3.0_pro` | 12 cr/s = $0.12/s | $7.56 | $12.60 |
| `veo3.1` | 20 cr/s = $0.20/s | $12.60 | $21.00 |

Not included (unknown, stays null): character/keyframe image generation, foley licensing, tax, human review minutes. **Suggested cap for owner decision: $40 for both variants**, which covers the highest row with the ≥5s-minimum worst case (35s × 5 × $0.20 = $35) plus keyframe images. Stop and report if S05 fails QA twice.

## Measurement and decision gate

- No-spend proxy first: run both ShotSpecs through the storyboard preview; blind muted viewers answer "who rejected the coupons?" and "where did it end?".
- After approved publication: stayed-to-watch, AVD, engaged views at 24/72/168h per variant, same post-age. One pair is observational; label distribution confounds; do not repost near-duplicates to force a test.
- Current decision: **NARROW — ready for spend approval.** Next owner action: supply character references and approve (or reject) the cap above.
