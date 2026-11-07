# Agent instructions — contF

This repository is an evidence-driven research and experiment system, not an autonomous growth or publishing bot.

## Before changes

1. Read README.md, ROADMAP.md, docs/architecture.md, docs/measurement.md and this file.
2. Inspect existing files, issues and open changes. Preserve user changes.
3. Record a concrete hypothesis and the decision it could alter.
4. Prefer small, testable changes with versioned data contracts.

## Sources and claims

- Record source URL, access date, publication date where known, observed metric definition, and whether the figure is public, creator-reported, or internally verified.
- Never fabricate views, audience retention, CTR, conversion, platform algorithm details, model prices or results.
- Public competitor metrics are *candidate-discovery proxies*. Private engagement and retention require owner authorization.
- Use official platform documentation for API fields and policies. Recheck time-sensitive product or cost claims.
- No deterministic claim that a creative pattern *causes* virality without controlled evidence.

## Experiment discipline

- Use one primary creative variable per controlled comparison where feasible.
- Tag channel, format, video duration, reference IDs, theme, hook, conflict, payoff, model, cost and observation window.
- Compare metrics at similar post-age and distribution source; keep missing values as missing, never zero-fill.
- Report sample size and unknowns. Underpowered studies yield proposed follow-ups, not automatic winners.
- Always preserve an audit trail: hypothesis → blueprint → variant → publication → observation → decision.
- E0–E5 Skill promotions must have traceable evidence and human approval; never self-promote.

## Production and rights

- Analyze structure; do not copy recognizable third-party footage, audio, faces, voices, logos or scripts without rights.
- Respect YouTube rules against low-value, repetitive or mass-produced near-duplicates.
- Scripts and frames require human approval before costly generation.
- No automatic publishing, external posts, financial spending, browser credential handling or paid generation without explicit user authorization.
- Keep secrets outside code and Git history. Save media elsewhere and store only approved metadata/references.

## Engineering

- Python 3.11+, standard library first.
- No external network calls in tests. Fixtures must say SYNTHETIC.
- Run `python3 -m unittest discover -s tests -v`; ensure `python3 -m contf.cli review ...` works after editable install.
- Maintain schema versions when contracts change; avoid breaking archived experiments.
- Each research note must end in a next test or explicit rejection rationale.

## Cadence

Each working day produce a bounded written decision: continue / narrow / pivot / pause / insufficient-data, with next owner action. Daily monitoring alone is not evidence of improvement.
