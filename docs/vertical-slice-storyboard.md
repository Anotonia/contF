# contF P0 vertical slice — original storyboard preview (2026-11-18)

Status: review branch only; NOT a production video, NOT merged, NOT an audience-performance experiment.

## Scope

First executable link from an original shot plan to a reproducible video preview. This module does not scrape social platforms, call paid or external AI models, generate speech, remove attribution, clone copyrighted videos, publish or ingest private Analytics. Every output is a silent, clearly labelled STORYBOARD PREVIEW, not a finished Maya & Ethan film. The original example story is fictional test content, not a validated viral-reference adaptation.

## Local commands

Requires Python >=3.11, FFmpeg with drawtext and libx264.

    PYTHONPATH=src python3 -m contf.shot_pipeline validate data/examples/maya_ethan_original_animatic.json --root .
    PYTHONPATH=src python3 -m contf.shot_pipeline plan data/examples/maya_ethan_original_animatic.json --root .
    PYTHONPATH=src python3 -m contf.shot_pipeline render data/examples/maya_ethan_original_animatic.json --root . --output /tmp/contf-preview.mp4 --cache /tmp/contf-shot-cache
    PYTHONPATH=src python3 -m unittest discover -s tests -v

The example has 16 original 12-second ShotSpecs, or 192 seconds (3:12) of storyboard timeline. Each shot remains pending creative review; approval_status is draft. Neither timeline duration nor local rendering proves a quality finished film.

The renderer writes preview.mp4 and preview.manifest.json, identifying source provenance, shot hashes and which segments were rendered versus reused. For reproducible partial rerender, edit only one shot and reuse the same cache directory. Only the changed shot must be re-rendered while the composition is rebuilt.

## Gated verification

| Stage | Required actual evidence | State after this change |
| --- | --- | --- |
| Reference discovery | Original videos and creator-relative matched controls | Missing; Issue #2 |
| Verified decomposition | Full footage observation, accurate timecoded shot map | Missing; Issue #7 |
| Mechanism model | Falsifiable abstract hook/conflict/payoff hypotheses | Templates available, not proven |
| Original writing | Owned scripts and provider-neutral ShotSpecs | Original synthetic story fixture available |
| Video assembly | Deterministic 3m+ storyboard and manifest | Compiler implemented, real run to verify |
| Partial rerender | Unchanged shot keys reused, changed shot rendered | Implemented with tests |
| Final animation | Consistent characters, motion, sound, QA | Missing; storyboard is silent |
| Audience evidence | Owner-authorized 24/72/168 h Studio/Analytics snapshots | Missing; Issues #1 and #5 |
| Evolution | Human-reviewed next-variant decisions | Existing synthetic evaluator only |

## Safety and engineering

- Source_media must be a local file under explicit root; traversal, absolute paths and missing files are rejected.
- Project rights must be owned-original. Each real media shot requires source_rights of owned or licensed. Such metadata is an assertion, not proof of permission.
- Clip bytes SHA-256, text, duration, encoder dimensions, FPS and renderer version define the cache key.
- FFmpeg is called without shell=True; no network, paid API, publishing or third-party tool integration.
- No reference footage, private audience data or secret credentials should be committed to this repository.
- Untrusted cache directories must not be shared across users: cached clips are not independently authenticated.
- No actual final content is claimed; the storyboard is intentionally silent and must undergo creative and audio QA.

## Next acceptance work

1. Complete the browser smoke check and rights-cleared clip comparison from PR #8.
2. Attach one owned 12–25-second reference, manually inspect frames and beats, and compare two decomposers against manual cut labels.
3. Replace storyboard cards with rights-cleared, human-approved Maya & Ethan shots; establish motion, character identity, audio, subtitles and real final 3-minute episode QA.
4. Connect authorized YouTube Studio CSV input to the existing descriptive evaluator and actual video/variant identifiers.
5. Log real run time, review minutes, shot-level failures, cost per accepted minute and an explicit adopt/narrow/reject decision. No automatic publication or Skill promotion.
