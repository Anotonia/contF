# Cross-platform Viral Radar SOP v0.2 — video-first

**Priority:** actual TikTok / 抖音 / YouTube Shorts *videos* → provenance-graded evidence → visible beat/camera analysis → original Maya & Ethan experiment. Studying HYPIT/rea-video is a downstream tool choice, not a substitute for finding a working storytelling pattern.

## Daily search budget and discovery

1. **Specify cohort before searching:** Maya & Ethan English/visual family, character and situational comedy; include dog as a third “character”; starting 10–25s duration if verified. Also study slightly longer proof points without pretending direct comparability.
2. **Search all three platforms separately.** Use official discovery interfaces, creator pages, search results and permitted public indexing. Try topic clusters: unspoken relationship conflict, expectations vs reality, prop failure, delayed reaction, dog/child misunderstanding, household role reversal. Record exact video permalink. Prefer creator-posted originals; secondary articles can seed discovery **only**.
3. **Do not confuse source availability and performance:** a TikTok media report is secondary; Douyin search snippets may show counters with unknown labels; YouTube page text can show public views but not retention. Respect login/captcha/account restrictions, APIs and rights. No circumvention or mass scraping.
4. **Two-stage sample size:** pilot with ≥3 leads *per platform* plus ≥1 contrast candidate per platform; extend toward **10 success candidates + 10 genuinely matched controls** overall only once metadata are verified. When data are missing, state shortfall explicitly. Search volume is not evidence.
5. **Avoid selection bias:** match by creator/format/theme/duration/post age where feasible, not just a high absolute view count. Use creator recent same-format post-age median as context, not as guaranteed causal baseline. Low public count on a different creator is **not** a non-hit control.

## Mandatory reference row

- `reference_id`, platform, canonical_url, account, original_creator_status, title/description, publication date/time zone, observed_at, duration if verified.
- Evidence tier: `A` original page + **video visually inspected** + named public metric; `B` direct original metadata/metric but video not fully inspected; `C` credible secondary report with dated number; `D` title/index/claim only.
- For **each** figure: `value`, `unit` (views/likes/comments/shares/followers), `visible_label`, `source_url`, `as_of`, `source_type` (platform/creator/press/index), `confidence`. Unlabeled counters are `unknown_metric`, never assumed views. Note raw lifetime vs comparable post-age.
- Rights/access: video actually viewed? account/login barrier? external media reuse permission? Missing original link? Mark exact unknowns `null`.
- Control matching: creator-relative median where available, comparison video ids, age-window and main confounders. Evidence status `discovery | metadata-verified | visually-inspected | beat-mapped | experimental | rejected`.

## Required film-level decomposition

**Do not infer frames from a title.** Only visually observed material gets exact timecodes:

| Unit | Required observation |
| --- | --- |
| First 0–2s | first frame, readable conflict, expression, curiosity gap, onscreen text and VO |
| Every cut | start/end in seconds, shot scale, composition, camera movement, actors and prop continuity |
| Comedy beats | H hook / S setup / C conflict / E escalation / R reversal / P payoff / L callback or loop |
| Audio/visual grammar | music and edit tempo, pauses, action-to-reaction order, voice/face timing, subtitle density |
| Ending | new information, laugh/recognition moment, hold vs jump cut, replay invitation (if seen) |

Each claim is tagged **observed**, **reported**, **inferred**, or **untested**. Beat timings are `null` until the reference can be inspected; caption-only studies are not “shot-by-shot.”

## Selection / original production

- Score separately: evidence quality; Maya/Ethan character fit; within-budget filmability; mechanism clarity; rights/identity distance; test isolation. **Do not rank based only on views**.
- Choose 1–2 observable mechanisms; write at least two unrelated original premises for each. Preserve abstract tension/turn mechanics only, never scripts, recognizable props/gag details, soundtrack, likeness or reference frames.
- Draft two controlled variants changing one main creative lever (first image, conflict timing, reaction hold, staging). Block paid generation and posting until human approval.
- Publish outside contF only with explicit user authorization. Collect owner-authorized 24/72/168h analytics and production cost; separate Shorts raw views from engaged views.
- Decide **continue / narrow / pivot / pause / insufficient-data**, record alternatives and reason. E0–E5 Skill promotion needs repeated evidence and a human gate.

## Daily output / audit

1. Report **new original video URLs**, evidence tier, snapshot age and metrics quality; show actual shortfall if no source found.
2. Include one **visually verified** breakdown when accessible; otherwise a clearly labeled title/article hypothesis and the next video to inspect.
3. Include one contrast candidate; mark *unmatched* until same-creator comparable counts are available.
4. Attach one original 15–20s Maya & Ethan experiment hypothesis and an explicit production-approval gate.
5. Add dated note to `research/`; update existing [Issue #2](https://github.com/Anotonia/contF/issues/2) rather than multiplying overlapping research issues. Daily tool-landscape watches [Issue #7](https://github.com/Anotonia/contF/issues/7) are subordinate to actual reference evidence.

## Starting batch / next test

See [2026-11-07-cross-platform-viral-discovery.md](../research/2026-11-07-cross-platform-viral-discovery.md). **Next:** inspect full footage for YT1/YT2 and a rights-accessible TikTok original, then timecode one matched mechanism and produce two original A/B Maya & Ethan beat sheets. No paid generation or direct near-cloning.
