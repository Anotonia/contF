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

## Offline receipt-to-audit slice

Hypothesis: fingerprint-bound receipt QA and explicit billing missingness let a
reviewer distinguish accepted shots from missing evidence before final production.
Decision changed: which shots need a new producer attempt or billing follow-up.

Use Python 3.11+ and FFmpeg/FFprobe. All generated media stays outside Git:

```bash
python3.11 -m venv ~/contf-venv
source ~/contf-venv/bin/activate
pip install -e .
SAMPLE_ROOT="$(mktemp -d)/SYNTHETIC-slice"
python tests/synthetic_slice_smoke.py "$SAMPLE_ROOT"
cat "$SAMPLE_ROOT/out/audit.json"
```

The script copies the 16-shot sample into the temporary root, generates an owned
SYNTHETIC 12-second 640×360 testsrc+sine clip, and writes a receipt for S01 with
the job fingerprint, named SYNTHETIC reviewer, all manual gates passing and a
fictional billing fixture (not real model pricing or actual spending). It runs:

```bash
contf slice "$SAMPLE_ROOT/project.json" --root "$SAMPLE_ROOT" --out "$SAMPLE_ROOT/out" \
  --receipt "$SAMPLE_ROOT/receipt.json" --width 320 --height 180 --fps 8
contf slice "$SAMPLE_ROOT/project.json" --root "$SAMPLE_ROOT" --out "$SAMPLE_ROOT/out" \
  --width 320 --height 180 --fps 8
```

The first run accepts S01, leaves 15 awaiting approval, and renders 16 segments;
the second retains acceptance and reuses all 16. Output includes queue.json,
audit.json, preview.mp4 and preview.manifest.json. `--no-render` omits rendering.
Repeat `--receipt` for multiple raw producer receipts. Validation/receipt errors
exit nonzero. Receipts must include the exact current `build_jobs` fingerprint;
dimensions/FPS are part of that contract. The standalone
`python -m contf.production_jobs reconcile --project ... --root ... --queue ...
--receipt ingest-report.json` accepts repeatable **ingest reports**, not raw receipts.

To ingest and reconcile one raw receipt in a single step, use
`python -m contf.production_jobs apply --project project.json --root . --queue queue.json --receipt receipt.json --output updated-queue.json`.
`apply` binds an omitted fingerprint to the current plan before ingestion; a
provided mismatched fingerprint is rejected. Acceptance still requires local
preflight and human review, never a provider's accepted flag. Both `apply` and
`ingest` require exactly one `--receipt`.

Queues store `plan_settings` (width/height/FPS). The jobs CLI accepts `--width`,
`--height`, and `--fps`; when a same-project `--queue` is supplied, its stored
settings are used unless explicit matching settings are given. Conflicting settings fail before
writing output. Legacy queues without settings use the original 640×360/12 defaults.
Production fingerprints now bind project ID and render cache key (queue contract
0.2.0); old cache-key-only receipts require re-ingestion against the new job contract.
Render cache keys remain unchanged. Previous queues from another project are
ignored, including their plan settings. Stale incoming receipts are listed in
`rejected_receipts`; they cannot erase a verified current accepted receipt. Slice still returns receipt errors
while retaining that approval in queue.json and audit.json.

Media inputs are restricted to plain `.mp4`, `.mov`, `.m4v`, `.mkv`, or `.webm`
containers with file-only protocols and restricted demuxers; playlists are not
accepted, even when renamed to a container extension. Preview and manifest paths
must not alias source/candidate media (including symlinks or hard links). QA
measures the first non-attached-picture video stream, not audio/container length;
unknown video duration and multiple real video tracks fail closed. Renderer
`storyboard-3` explicitly maps the first non-attached-picture video stream, treats
percent signs literally in captions, and invalidates earlier rendered segments.

Receipt `cost` is optional: `{ "amount": 3, "currency": "USD", "source": "billing record reference" }`.
Omitted cost stays null, including per-shot audit entries. Totals report counts,
known costs by currency, a single-currency sum (null for none/mixed currencies),
unknown-cost count among jobs with receipts, and a separate `not_produced_count`
for jobs without receipts. Cost per accepted minute is computed when every receipt
has known cost, one currency and positive accepted duration; unproduced jobs do
not block it. The sample reports 15.0 USD per accepted minute, zero unknown-cost
receipts and 15 not-produced shots. It includes rejected/pending
costs in the numerator; it is a current-queue snapshot, not a historical invoice
ledger across superseded attempts. No exchange rates or costs are inferred.
Every output is explicitly non-final and unpublished. Synthetic gate passes
exercise plumbing only, not character/motion/lip-sync quality evidence.

Next test: replace S01 with an authorized, human-reviewed original clip and its
actual billing source; leave other costs unknown until evidence arrives.

## Next acceptance work

1. Complete the browser smoke check and rights-cleared clip comparison from PR #8.
2. Attach one owned 12–25-second reference, manually inspect frames and beats, and compare two decomposers against manual cut labels.
3. Replace storyboard cards with rights-cleared, human-approved Maya & Ethan shots; establish motion, character identity, audio, subtitles and real final 3-minute episode QA.
4. Connect authorized YouTube Studio CSV input to the existing descriptive evaluator and actual video/variant identifiers.
5. Log real run time, review minutes, shot-level failures, cost per accepted minute and an explicit adopt/narrow/reject decision. No automatic publication or Skill promotion.
