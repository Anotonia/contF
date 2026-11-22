# Changelog

All meaningful changes to data definitions, experiments, research SOPs, adapters and skill-promotion policy are versioned here.

## [Unreleased] — research update 2026-11-07

### Added
- Separate versioned human approval records, bound to shot/fingerprint/media hash and an independent reviewer; producer receipts are now 0.2.0 and reject embedded reviewer/gates. Legacy 0.1.0 receipts require re-issue. Slice and ingest/apply CLIs accept approval files and stored acceptance is re-verified against the original approval.
- Offline `contf slice` queue/receipt/preflight/audit/storyboard pipeline with fingerprint-bound receipts, optional actual billing provenance (missing remains null), accepted-shot persistence, and SYNTHETIC FFmpeg integration smoke coverage.
- Video-first TikTok / 抖音 / YouTube Shorts Viral Radar SOP v0.2, primary versus secondhand evidence tiers, and 2026-11-07 cross-platform reference seed ledger (not yet a controlled breakout study).
- Reprioritized actual content mechanism discovery and original Maya & Ethan hypotheses over HYPIT-class tool evaluation; no frame-level claims from title-only references.
- HYPIT-class reference-to-original-variant project matrix, source/licensing caveats, no-spend evaluation SOP and GitHub Issue #7.
- Read-only research lane covering shot reconstruction, edit QA, editable runtimes and explicit separation of production reproducibility from viral-performance evidence.

### Still not implemented
- Full timecoded visual inspection on the seeded set, authenticated platform-relative breakout/control cohorts, or verified viral transfer to our own channel.
- Installation or execution of external projects, paid rendering, an FT adapter or a verified reduction in human effort.

## [0.1.0] — 2026-11-07

### Added
- Evidence-first repository constitution and research operating procedure.
- Viral Radar / Pattern Extractor / Variant Factory / Evolution Engine architecture.
- Format-aware metrics, matched-age observation and no-fabrication guardrails.
- JSON contracts and explicitly synthetic fixtures for references, experiments and observations.
- Standard-library Python read-only experiment reviewer, tests and GitHub Actions CI.
- Originality-safe reference and experiment templates.
- Seed Hypit/CompShare engineering research and first P0/P1 GitHub issue backlog.
- Daily research/decision workflow coordinated outside the repository.

### Not implemented yet
- Owned YouTube analytics import, real channel baseline, competitor reference ingestion.
- Automated scene analysis, FT shot execution adapter and live skill registry.
- Publishing, monetization, model API execution or licensed multi-tenant SaaS.

### Compatibility
- All JSON contracts carry `schema_version: "0.1.0"`.
- The evaluator deliberately avoids automatic significance claims and strategy changes.
