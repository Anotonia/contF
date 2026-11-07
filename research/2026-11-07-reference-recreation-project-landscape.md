# Reference-to-Variant project landscape — 2026-11-07

**Status:** maintainer-source research; NOT installed, executed, benchmarked, or validated for audience growth.
**Owner objective:** a repeatable, original Maya & Ethan video-production experiment — not a guarantee of virality.
**Issue:** https://github.com/Anotonia/contF/issues/7
**Evidence accessed:** 2026-11-07. Project capabilities below are claims or documented interfaces from maintainers, not measured local outcomes.

## Key distinction

1. **Structural replication:** extract an observable editing/story grammar (hook, timing, escalation, reversal, captions, camera and sound cues); write a new premise and performance.
2. **Workflow replication:** preserve editable instructions, timeline, assets, prompts, cost and approvals, then locally revise or rerender selected shots.
3. **Audience replication:** *not possible to infer* from a reference video's public views; effectiveness must be tested with owner-authorized analytics and matched exposure windows.

The first two are engineering benchmarks. The third is an independent content/market experiment.

## Primary project matrix

| Project / source | Strength and documented contract | Likely place in contF | License / cost / caution | Readiness |
| --- | --- | --- | --- | --- |
| [Hypit](https://github.com/hypit-ai/hypit) | Agent Skill + editable semantic video system (SVML, word-linked events, renderable composition); proposes reference-to-workflow cloning and many variants | Optional producer adapter / editable variant workflow | [Hypit Open Source License](https://github.com/hypit-ai/hypit/blob/main/LICENSE): modified Apache 2.0; own organization's commercial use allowed, multi-tenant SaaS and commercial redistribution restricted; third-party model/API costs separate | Documented by maintainer; **not run locally** |
| [rea-video](https://github.com/JuneYaooo/rea-video) | Video shot analysis, mixed-source method identification, per-shot prompts and reconstruction report | First candidate for Pattern Extractor intake | Apache-2.0 per repository; extra models/FFmpeg capabilities and asset rights checked in pilot | Documented; **not benchmarked** |
| [edit-recreator](https://github.com/Ahsuu27488/edit-recreator) | Dense reference-edit analysis, timing / cut / transition measurement, own-media substitution, Remotion side-by-side QA | Edit grammar and timing-quality test | MIT for repository; Remotion and model/weights may have separate terms; small early project, *not* proof of robustness; pixel closeness to an unrelated work creates copying risks | Experimental candidate |
| [Frameloop](https://github.com/Alan-Lucena/Frameloop) | Extract key/dense frames; author Remotion; compare rendered preview to reference and iterate | Visual QA loop prototype | Repo describes MIT; verify Remotion's separate license before integration; same reference-rights issue | Experimental candidate |
| [OrkasVideoStudio](https://github.com/Orkas-AI/Orkas-VideoStudio) | Editable segment plan.json, separate compose/edit/generate paths, local checks and partial rerender | Alternative to Hypit as execution/plan adapter | MIT per maintainer; uses HyperFrames/FFmpeg. README says best for explainers/ads; does **not** guarantee camera/performance reproduction or frame-level matching | Good architecture comparison |
| [HyperFrames](https://github.com/heygen-com/hyperframes) | Deterministic HTML/CSS/media animation and rendering with explicit timing | Provider-neutral, deterministic render back end for graphics/captions | Apache-2.0 per repo; **not** by itself a video reverse-engineering or viral-prediction engine | Render-layer benchmark |

Note: use the canonical project repository and its LICENSE at the exact future integration commit; the table does not license dependencies automatically. These systems are different categories, not a single ranked leaderboard.

## Hypit-specific technical findings

- The official README states reference/video content can become an editable, rerunnable composition including captions, B-roll, effects and generation requests. Its showcased UGC, podcast and street-interview clone examples include **creator-stated**, non-independent model costs; these are not accepted budgets.
- The shipped Skill distinguishes reference interpretation from directly using reference footage as model input; semantics can anchor events to dialogue instead of hard-coded seconds.
- Hypit can work without a paid generative video model for code-rendered graphics and reused licensed assets. A full realistic family-comedy recreation may still need separate model/service spend and human retakes.
- The slogan about 100 variants / 100M views is marketing, **not evidence** that an algorithm rewards repeated clones.
- The license permits internal and own-client commercial work in defined circumstances, but does **not** provide unrestricted permission to package Hypit into contF as a multi-tenant SaaS. Do not vendor/copy its source until the use case and license are separately cleared.

## Fit for Maya & Ethan

A family comedy clip differs from a motion-graphics explainer: reaction microexpressions, hand-object continuity, crossed dialogue, dog behavior and payoff timing may dominate quality. A technically similar edit does not ensure a funny performance.

**Shortlist to test in sequence:**
1. rea-video (or a manual FFmpeg-based process) to propose a beat/cut map, compared against human annotations.
2. Hypit versus a minimal neutral shot-spec/renderer workflow on a rights-cleared *owned* 12–25s clip. Prefer no-cost planning and dry-run before any model call.
3. Borrow evaluation ideas from edit-recreator / Frameloop: contact sheets and spot checks for timing, continuity and visual clarity. Avoid treating copyrighted source pixels as the target.
4. Consider Orkas or HyperFrames only when the approved FT adapter requires deterministic composition; do not add all runtimes by default.

## Testable hypothesis and disconfirming evidence

**H-RR-001:** a reference-to-structured-blueprint workflow reduces human preparation/revision time per accepted original video, without reducing reviewer-rated originality and comic clarity.

**Could disconfirm:** no better shot-boundary detection than manual review; excessive setup; generic/unfunny new stories; inconsistent characters/objects; repeated generation calls; rights/license roadblocks; saved rendering time dwarfed by supervision.

**Measurements:** human minutes for initial beat map, cuts deviation from human labels, editable spec completeness, render failure/retries, continuity errors, actual provider cost, accepted-minutes ratio, reviewer decision. No provider spend without approval. Later audience experiments measure 24/72/168h engaged reach and retention independently.

## Evidence and provenance

Primary sources (maintainer repositories, accessed 2026-11-07):
- https://github.com/hypit-ai/hypit
- https://github.com/hypit-ai/hypit/blob/main/LICENSE
- https://github.com/hypit-ai/hypit/blob/main/skills/hypit/SKILL.md
- https://github.com/JuneYaooo/rea-video
- https://github.com/Ahsuu27488/edit-recreator
- https://github.com/Alan-Lucena/Frameloop
- https://github.com/Orkas-AI/Orkas-VideoStudio
- https://github.com/heygen-com/hyperframes

Secondary tutorial for example setup only, not a benchmark: https://note.com/ai_shiryo/n/nebeb27f4f99d

## Decision and next test

**Decision: narrow to a no-spend comparative pilot**, not integrate or endorse a tool yet. Obtain one owner-controlled video; human-label its beat map; run or evaluate at least two candidate routes using the same source, task, output contract and logged supervision. Propose FT integration only after findings are reproducible and the user accepts the cost/license boundary.
