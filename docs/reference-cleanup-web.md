# Reference cleanup Web bridge · P0 opt-in

**Status:** experimental preflight, not a watermark-removal engine and not an approved production adapter. Parent workstream: [Issue #7](https://github.com/Anotonia/contF/issues/7).

## Why this exists

Some **owned or explicitly licensed** reference footage has an obsolete logo, burned-in overlay, or date stamp that interferes with frame/shot inspection. This optional bridge records what an operator intends to clean and the exact frames/time intervals. It **does not** make third-party reference footage reusable. For TikTok/Douyin/Shorts competitor research, retain the original creator URL/attribution; analyze only abstract structure unless separate rights are proven.

## Run locally

```bash
python3 -m http.server 8765 --directory web/reference-cleanup
# Visit http://localhost:8765
```

No application account, dependency installation or service API is needed. The selected file stays in browser memory. The page does **not** send it to contF or an external processor. External tools are opened in a new tab only after an affirmative rights selection and attestation. If subsequently used, each tool has its own data handling and fees.

## Workflow / handoff

1. Select a locally held, rights-cleared source. Enter a stable `reference_id`, original URL if applicable, permission/evidence and duration from video metadata.
2. Pause on the relevant frame; enable draw mode and drag a bounding rectangle. Choose start/end seconds for its visibility. Repeat per moving-region interval. Multiple rectangles use normalized **percent coordinates** rather than baked-in pixels.
3. Optionally open WatermarkOut (client-side first), VidProc (time-bound regions) or Media.io (longer supported inputs). No automatic upload, charge, provider call or processed-output claim occurs. Inspect the external tool's current terms; use only material you can edit.
4. Export `*-cleanup-manifest.json`. This is a **preflight**, with `processor.execution_status = "not-run"`, `output_file_name = null` and `human_review.status = "pending"` regardless of whether an external page was opened.
5. After separate manual processing, human QA must compare the original with cleaned frames at cut boundaries, moving text/objects and faces; record actual tool/version, runtime, output checksum or private media pointer, failed intervals and permission. A future version may add a reviewed execution manifest. **Do not fabricate completed status.**
6. Feed only approved structure/timecode annotations (not unlicensed cleaned pixels) into `Reference-to-Variant Lab` G1, where hook/conflict/reaction/payoff are independently annotated. Continue to G3 with **original** Maya & Ethan actions, dialogue, props and shots; use a human gate before FT generation and publishing.

## Data contract

`data/schemas/cleanup-manifest.schema.json` is an additive v0.1.0 contract. `src/contf/cleanup.py::validate_cleanup_manifest` checks required structural and rights/time/coordinate invariants. It never accesses media or the network. The manifest is not a license record or a declaration that an external tool succeeded.

One object records `reference_id`, `source_url`, `captured_at`, `source_file`, `rights`, `processor`, `regions` and `human_review`. A region has `x_pct`, `y_pct`, `width_pct`, `height_pct`, `start_s`, `end_s`. Coordinates are frame-relative (0–100) and **each box must fit inside the frame**. A time range must be within source duration. Avoid persisting raw reference video, transcript copies or third-party cleaned videos to Git.

## Decision / measurable P0 test

**Decision: narrow.** Use this as manual preflight only; no API or open-source engine vendoring until one owned 12–25s source is evaluated. Compare no-cleanup baseline vs WatermarkOut vs VidProc on identical authorization-cleared footage. Log output fidelity (moving edge / text / face artifact), segment alignment, time-to-usable shot map, correction count, review minutes, actual spend and export reliability. Use Media.io later for a separately licensed 3–5min source if short-form quality passes.

**Adopt gate:** two reviewed samples, no material reconstruction errors at important beat/cut frames, useful drop in human inspection effort, verified processor privacy/license, reproducible manual handoff. Otherwise keep the opt-in link only or reject. Generated clips and audience metrics remain separate from this preprocessing comparison.
