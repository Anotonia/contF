# No Refunds — Google Flow (web) prompt pack

Owner renders manually in Google Flow on web; this file only prepares inputs. Nothing here was generated or spent by Devin.

Flow facts used (official [models & features](https://support.google.com/flow/answer/16352836) and [create videos](https://support.google.com/flow/answer/16353334) help, accessed 2026-11-21): Omni Flash 1.2 supports Text/Frames/Ingredients to Video in both aspect ratios, 3–10s clips (3–15s with a Google AI subscription); Frames to Video is web-only. **Check the active model, resolution and credit cost in the prompt box before each Generate** — credit costs were not verified here.

## Setup (once per project)

1. Aspect ratio **9:16 (portrait)**; model Omni Flash 1.2; 1 output per prompt to save credits (raise to 2 only for S05).
2. Upload as **Ingredients** (owner's approved designs only, do not invent): `Maya`, `Ethan`, `Biscuit`, `Kitchen`, `Coupon book` (plain pastel sticky-note pad, blank pages).
3. Every prompt ends with the shared style line below. **Never ask Flow to write text**: coupon words and EXPIRED stamps are added in the edit.

Shared style line:
> Warm late-afternoon natural light in a cozy home kitchen, realistic live-action sitcom look, locked-off static camera, vertical 9:16 framing, natural subtle acting, no on-screen text, no captions, no dialogue, no music.

## Shots (generate 3–4s minimum, trim in edit)

| Shot | Flow mode / length | Ingredients | Prompt (then append the style line) |
| --- | --- | --- | --- |
| S01 (keep 2s) | Ingredients, 4s | Maya, Ethan, Biscuit, Kitchen, Coupon book | Medium-wide shot at a kitchen counter. Ethan, beaming with pride, slides a small pastel sticky-note booklet across the counter to Maya. Maya looks at it, unimpressed. A dog, Biscuit, sits on the floor at the right edge of frame watching them. |
| S02 (3s) | Ingredients, 4s | Maya, Ethan, Coupon book | Medium shot of Maya at the counter. She calmly tears the top page off the sticky-note booklet and hands it straight back to Ethan, whose hand reaches into frame. |
| S03 (3s) | **Skip Flow** | — | Top-down insert of the coupon + fingertip: shoot a phone photo of a real sticky note, or a still; "EXPIRED" tiny print composited in edit. |
| S04 (5s) | Ingredients, 6s | Maya, Ethan, Biscuit, Kitchen, Coupon book | Medium two-shot. Maya flips quickly through every page of the sticky-note booklet, each page bearing a large blank red stamp mark. Ethan sighs, crouches down to the dog's level and offers the whole booklet to Biscuit with both hands. |
| S05 (2s) | Ingredients, 4s, **2 outputs** | Maya, Ethan, Biscuit, Kitchen, Coupon book | Wide shot showing all three full-body: Ethan crouching, Maya standing behind with arms crossed. The dog gently takes the booklet in its mouth, deliberately drops it at Ethan's feet, and turns away. |
| S06A (3s) | **Frames to Video**, 4s; start frame = last frame of accepted S05 | Maya, Ethan, Biscuit | Same wide shot, camera does not move. The dog trots calmly out of frame to the right. Ethan stays crouched, staring at the booklet on the floor. Maya folds her arms. Hold. |
| S06B (3s) | **Frames to Video**, 4s; start frame = a close-up still of crouched Ethan from S05 lighting | Ethan | Static close-up of Ethan's face at crouching height, looking down at the floor, a slow deadpan look of quiet defeat. He does not speak. Hold. |

S05 is the riskiest shot (dog mouth/object continuity). If two generations fail QA, stop and report; the fallback is a practical or composited cue.

## Edit (local, no credits)

Trim to the [variant A](variant-a.shots.json) / [variant B](variant-b.shots.json) timings (S01–S05 identical in both). Mute Flow audio, add foley, add "1 FREE DISHWASH" (S01, readable by 2.0s), "EXPIRED" (S03) and stamps (S04). Record per clip: model, length, credits charged, attempt number, accept/reject + QA code, into the receipt fields in [the spec](../ME-20261121-no-refunds.md).

## Credit budget

Billed footage per pass ≈ 4+4+6+4×2+4+4 = 30s (S03 skipped). With 3–5 attempts on the generated shots that is ~90–150s of output. Read the per-second/per-clip credit cost shown in Flow, multiply, and stay under the cap the owner approved.
