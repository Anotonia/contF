# ADR-0001 — Evidence-first content evolution

**Date:** 2026-11-07  
**Status:** Accepted for v0.1 foundation

## Context

Our FT / Craftaste direction had production and multi-format compilation concepts but no systematic way to tie viral reference research to original experiments, creator approvals, real YouTube outcomes and versioned improvement.

## Decision

1. Treat reference research, creative experiments, owned-channel observations, production costs and Skill versions as separate typed records joined through explicit IDs.
2. Start with a conservative read-only evaluator instead of an opaque 'virality score'.
3. Use matched-age, same-channel and same-format comparisons. Mark confounding, small samples and missing data explicitly.
4. Keep competitor public metrics separate from private account analytics.
5. Store generalized creative structure, never republish third-party media by default.
6. Keep creative direction, spending, publishing, and mature Skill promotion under human confirmation.
7. Make Hypit and video models optional adapters rather than core dependencies.

## Consequences

- Initial velocity is slower than 'one-click clone and upload', but results are reviewable and commercially safer.
- A future Analytics import and reference database can be added without redefining the current experiment contract.
- Until enough comparable observations exist, decisions remain 'insufficient-data' and no Skill is promoted.

## Revisit criteria

Revisit after the first complete publish-and-observe cycle, if source/API constraints change, or if a licensed client workflow requires different governance.
