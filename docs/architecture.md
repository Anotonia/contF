# Architecture v0.1

## Responsibilities

| Module | Input | Output | Current implementation |
| --- | --- | --- | --- |
| Viral Radar | Curated public URLs and observation dates | Candidate reference record | Contract + SOP |
| Pattern Extractor | Reference video, captions, shot metadata | Originality-safe structural blueprint | Human research template |
| Variant Factory | Blueprint + owned characters | Hypothesis, variants, experiment IDs | Experiment contract/template |
| Production Adapter | Approved script, shots, character bible | Per-shot asset/version/cost record | Contract only; FT not wired |
| Analytics Ingestion | Authorized owned-channel exports/API | Video observations with provenance | Synthetic fixture only |
| Evolution Engine | Experiments + observations + comparisons | Read-only daily decision suggestions | Python CLI v0.1 |
| Skill Registry | Hypotheses + repeated evidence | E0–E5 promotion proposal | Policy/template only |

## Provenance boundaries

**External public reference:** publication/source/observed public counts and structural hypothesis. No private audience retention, no inferred exact recommendation weights.

**Owned-channel analytics:** verified video IDs and permitted Analytics/Studio measures. Preserve content age, time zone, metric version and source.

**Production:** model/provider/version, shot IDs, accepted vs rejected clips, actual billing and approval records. Missing actual cost must remain null.

Cross-domain joins require stable reference_id, experiment_id, variant_id and video_id. Do not infer ownership from similar handles.

## Data model

- `reference`: external candidate, observation snapshot, structure + rights risk
- `experiment`: hypothesis, original variant, declared variable, channel and approval status
- `observation`: format-specific owned video metric snapshot; UTC timestamp and age in hours
- `decision`: proposal and evidence IDs, not automatically applied
- `skill_version`: pattern lineage, evidence set, maturity and human gate

All records carry `schema_version`. Example JSON documents live under data/examples and contain only synthetic records.

## Review cycle

1. Candidate selection checks source/age/scale/confounders.
2. Pattern deconstruction establishes a falsifiable hypothesis.
3. Human approves originality and creative direction.
4. FT executes approved shots; stores retry and cost metadata.
5. Owned Analytics produces comparable snapshots (24h / 72h / 7d).
6. Engine computes descriptive differences and uncertainty flags.
7. Human accepts, rejects or requests the next test.
8. Skill version increments only after review.

## Integration boundary with FT

Do not embed a model provider or Hypit-specific binary format into the core experiment contract. Expose stable JSON identifiers and a producer adapter. Preserve copyright/terms/licensing checks when importing an external tool.

## Governance

Default privacy: repository is private. Exported audience records and raw media should not be committed. Do not share keys, upload rights-restricted files, send external messages, incur model charges or publish videos automatically.
