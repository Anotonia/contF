# Reference-to-Variant Lab SOP v0.1

**Research track:** HYPIT-class reference reconstruction tools, issue https://github.com/Anotonia/contF/issues/7.
**Scope:** study reusable storytelling and editing techniques to produce materially original shorts. Reference similarity is not a substitute for viewer response.

## Inputs and provenance

- One video that is owned or authorized for analysis (record permission, source, date, duration, format, reference_id). Do not commit its media to Git.
- Destination: Maya & Ethan English-language family / character / situational comedy, original character identities and scripts.
- Creative constraint: what abstract technique may be studied, what visual/script/audio/likeness may not be reused.
- Optional comparable non-hit reference to counter selection bias.
- Tool build SHA, model/provider/version, environment and actual billing only if executed.

## Stage gates

| Gate | Required artifact | Decision |
| --- | --- | --- |
| G0 Rights and eligibility | source, permission, original-vs-reference boundaries | Stop if rights unclear |
| G1 Reference decomposition | frame samples, manually checked cut timecodes, H/S/C/E/R/P/L beat map, audio/caption timing where relevant | Accept or repair evidence |
| G2 Mechanism hypothesis | visible hook, audience expectation, conflict, escalation, reaction delay, payoff, loop; alternate explanations | No claim of proven causality |
| G3 Original variant | two distinct stories with new actions/props/dialogue, original shot list and clear laugh mechanism | Human creative approval |
| G4 Dry-run | provider-neutral ShotSpec and no-charge layout/storyboard previews; per-shot budget estimate | Explicit approval before any spend |
| G5 Production and QA | accepted/rejected shots, partial rerenders, contact sheet, identity/object continuity, captions/sync/readability, cost and reviewer minutes | Human accepts final |
| G6 Audience observation | owner-authorized video ID, actual age, views + engaged_views, stayed-to-watch and AVD where available | Compare by channel/format/age; insufficient-data as needed |
| G7 Evolution proposal | evidence IDs, failed alternatives, new hypothesis, continue/narrow/pivot/pause | Human confirmation before Skill E0–E5 change |

## Minimal provider-neutral beat / shot worksheet

Each segment records: reference_id, start_s, end_s, beat (H/S/C/E/R/P/L), camera_scale, subjects, visible_action, dialogue_or_sound_cue, facial_reaction, setup_to_payoff_relation, uncertainty, original_reinterpretation, shot_id.

Additional production fields: project_id, reference_link, approved_script_version, model/provider/version, asset_version, attempt_id, accepted, cost_actual, reviewer_minutes, QC_failure_code. Unknown fields remain null, not zero. Keep restricted assets, secrets and personally identifying audience exports out of Git history.

## Baseline bake-off

Choose **one** rights-cleared 12–25-second family-comedy source. Two independent views of the *same clip*:
- A: manual shot labels and creative adaptation.
- B: rea-video analysis (or the simplest comparable tool), then human correction.
- C: HYPIT-style semantic/shot workflow; dry-run without charge, compare the completeness of reusable editable specification.
- Optional D: Frameloop/edit-recreator quality technique for contact-sheet review. If Remotion is used, inspect its own license.

Compare observation-to-observation, not promotional screenshots:
1. cut boundary error vs manual labels (seconds), missed cuts and human correction count;
2. time-to-approved blueprint, tool setup minutes, review minutes;
3. number of independent original premises accepted by the user;
4. renderer/agent iterations, continuity errors, cost per **accepted** second if any generation authorized;
5. project reproducibility: deterministic spec, versions, outputs, partial rerender and rollback.

A technical benchmark on one clip cannot establish that any tool will grow a YouTube channel. Owner analytics over matched 24/72/168h windows supply the *separate* content-performance evaluation. Do not auto-select a winner when the sample is underpowered.

## Suggested agent analysis prompt (planning only)

> Analyze this explicitly authorized reference for abstract short-form storytelling/editing mechanics. Produce a timecoded shot/beat map with observed evidence versus inference. Explain hook, relationship conflict, escalation, payoff and loop. Create two or more new Maya & Ethan premises that use the *general mechanism* but not the reference's script, frames, audio, distinctive set pieces or other protected expression. Identify continuity and performance risks, give a no-spend storyboard, and stop before any model call or publication. Provide a source-to-new-work change log and human approval checklist.

## Failure labels

RIGHTS_UNCLEAR; REFERENCE_INSUFFICIENT; SHOT_BOUNDARY_ERROR; HOOK_UNCLEAR; STORY_TOO_SIMILAR; JOKE_NOT_LEGIBLE; CHARACTER_DRIFT; OBJECT_CONTINUITY; MOTION_ARTIFACT; AUDIO_SYNC; TEXT_OVERFLOW; EXCESSIVE_COST; HUMAN_REWORK; ANALYTICS_NOT_COMPARABLE.

## Next test

Implement a bounded, read-only manual comparison on one owned family comedy video and attach the evidence to issue #7. **No paid generation, publishing or copying external assets in this research stage.**
