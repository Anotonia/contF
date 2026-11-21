# contF — Content Intelligence & Evolution

> A research-to-production system for identifying promising video patterns, creating original variants, measuring outcomes, and evolving creative skills.

**Status:** v0.1.0 foundation · **Home:** [Anotonia/contF](https://github.com/Anotonia/contF) · **Initial testbed:** Maya & Ethan family / character / situational comedy.

## The problem

AI video tooling can generate clips, but it often lacks (1) a defensible way to discover *why* content succeeds, (2) controlled adaptation of reference patterns into original stories, and (3) a traceable link from decisions and production changes to real audience outcomes.

contF connects those three missing loops. It does **not** promise guaranteed virality or reverse engineer YouTube's ranking algorithm.

## System boundaries

1. **Viral Radar:** Discover external candidates with dated, attributed public signals. External metrics never substitute for an owner's private retention data.
2. **Pattern Extractor:** Document hooks, character conflicts, beat timings, payoffs, visual grammar, and hypotheses. Reuse general techniques, not protected footage or identities.
3. **Variant Factory:** Design distinct original videos with a stated experiment variable; human creative approval is required.
4. **Production Adapter:** Pass approved shot and character specs to FT / model providers. Record versions, budget, model calls, failed and accepted shots.
5. **Evolution Engine:** Join content metadata with owned-channel Analytics observations; compare like-for-like, propose continue / narrow / pivot / pause.
6. **Skill Registry:** Track E0–E5 skill evidence, version history and explicit human promotion.

## Principles

- **Evidence before claims.** Label observed facts, creator claims, inferences and untested hypotheses separately.
- **Same-age comparisons.** Observe 24 h, 72 h and 7 d windows; never compare a fresh video to a mature lifetime total.
- **Separate formats.** Shorts views / engaged views and long-form impressions / watch time have different meanings.
- **No autonomous publishing, spend, charging, credential creation or strategy promotion.** Approval is required.
- **No unlicensed duplication.** Reference URLs and analysis are safer than redistributing footage.
- **Models are replaceable.** No exclusive dependency on Hypit, H3, Grok or any rendering provider.

## Repository map

- [docs/architecture.md](docs/architecture.md) — responsibilities, data flow and interfaces
- [docs/measurement.md](docs/measurement.md) — metrics, comparison cohorts and decision rules
- [docs/viral-research-sop.md](docs/viral-research-sop.md) — discovery, reverse engineering, originality checks
- [docs/cross-platform-viral-radar.md](docs/cross-platform-viral-radar.md) — **video-first** TikTok / 抖音 / Shorts discovery, source grading and film-level analysis
- [research/2026-11-07-cross-platform-viral-discovery.md](research/2026-11-07-cross-platform-viral-discovery.md) — dated real-video seed ledger, evidence limits and Maya & Ethan hypotheses
- [docs/reference-to-variant-lab.md](docs/reference-to-variant-lab.md) — HYPIT-class reference-to-original-variant benchmark SOP
- [research/2026-11-07-reference-recreation-project-landscape.md](research/2026-11-07-reference-recreation-project-landscape.md) — primary-source tool matrix and license caveats
- [docs/skill-lifecycle.md](docs/skill-lifecycle.md) — E0–E5 evidence and review gates
- [ROADMAP.md](ROADMAP.md) — day-by-day execution and acceptance criteria
- [CHANGELOG.md](CHANGELOG.md) — released capabilities and explicit non-goals
- [docs/daily-operations.md](docs/daily-operations.md) — repeatable daily research and review
- [research/](research/) — sourced research notes
- [templates/](templates/) — reusable study / experiment / review records
- [data/schemas/](data/schemas/) — machine-readable contracts
- [data/examples/](data/examples/) — explicitly synthetic fixtures only
- [src/contf/](src/contf/) — standard-library experiment analysis CLI
- [tests/](tests/) — repeatable local checks

## Getting started (no account keys needed)

```bash
PYTHONPATH=src python3 -m unittest discover -s tests -v
PYTHONPATH=src python3 -m contf.cli review --observations data/examples/observations.json --experiments data/examples/experiments.json
```

Use Python 3.11+ and set `PYTHONPATH=src` for the second command, or install editable: `python3 -m pip install -e .`.

The included observations are **synthetic test records**, not Maya & Ethan performance data. Real YouTube Analytics ingestion is not enabled yet.

For the offline shot queue → receipt QA → cost audit → cached storyboard preview,
see [the vertical slice walkthrough](docs/vertical-slice-storyboard.md#offline-receipt-to-audit-slice).
After editable install: `contf slice data/examples/maya_ethan_original_animatic.json --root . --out /tmp/contf-slice`.
This creates a silent storyboard, not a final or published video; no provider or paid generation runs.

## What comes first: real viral-video evidence

Start with original TikTok / Douyin / YouTube Shorts **video URLs** and inspect the video, source and public figures; assemble hit/contrast pairs with credible same-creator and post-age baselines, then timecode the actual hook, conflict, escalation, shots, expressions and payoff. Only then consider HYPIT-class reconstruction or FT production. Initial 2026-11-07 discovery is **not** a completed verified breakout/control study, and title-only references are not shot analyses.

## Reference-to-Variant research track

Issue [#7](https://github.com/Anotonia/contF/issues/7) benchmarks HYPIT, rea-video, edit-recreator, Frameloop, OrkasVideoStudio and HyperFrames as optional components. This is a **research workstream, not an installed integration**. Evaluate authorized source-to-original-story reconstruction, local editability, cost and human supervision; compare YouTube outcomes separately using owned analytics.

## Operating loop

Daily: source watch → candidate notes → creative brief → approval → publish elsewhere → 24/72/168 h snapshots → causal caution → proposed changes → human confirmation → version bump.

Start with a small set of matched controls and record what *did not* work. Do not automatically modify an existing winning video or repost near-duplicates.

## Decisions & safety

See [AGENTS.md](AGENTS.md). No personal information, private audience analytics exports, credentials or generated copyrighted reference media should be committed without a separate explicit decision. This repository is private, but privacy does not remove rights or platform-policy obligations.
