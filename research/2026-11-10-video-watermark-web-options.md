# Web video watermark cleanup · primary-source scan

**Research date:** 2026-11-10 UTC. **Question:** which Web-based cleanup approach is a viable, low-cost, rights-safe optional input for contF reference decomposition? **Status:** documentation-screened, not output-quality tested.

| Option | Primary-source claims (not independently benchmarked) | Commercial/privacy/integration boundary | P0 decision |
| --- | --- | --- | --- |
| [WatermarkOut](https://github.com/IamRamgarhia/free-ai-watermark-remover) / [live](https://iamramgarhia.github.io/free-ai-watermark-remover/) | Client-side WebAssembly/WebGPU; image/video; live page says <=100 MB; rectangle/brush; 29MB MI-GAN, videos treated frame-by-frame; MIT [LICENSE](https://github.com/IamRamgarhia/free-ai-watermark-remover/blob/main/LICENSE) | Browser-local **per project claim**, small newer project; no published automation API; verify ONNX model licensing, output/audio, mobile memory/performance before embedding. Visible watermark removal does not erase provenance metadata/SynthID. | **First manual test; link only**, do not vendor. |
| [VidProc Web](https://www.vidproc.com/en) / [pricing](https://www.vidproc.com/en/pricing) | Browser UI offers multiple regions and start/end time per area; free guest 20s/3 videos/day, registered 20s/10 videos/day; advertised reusable templates and API | Site claims UI file stays local, yet API accepts video links; verify actual network behavior and license separately. PLUS advertised $8/month, PRO $20/month, without confirmation of checkout terms. | **Second test** for shot/time-scoped editing, free guest only. |
| [Media.io](https://www.media.io/video-watermark-remover.html) | MP4/MOV up to 15min; manual brush, prompt-based AI and Gaussian blur; preview before export | Treat as remote processor; pricing, credit consumption, retention, queue, output rights **not established in this scan**. | Hold as 3–5min benchmark candidate. |
| [AirMore](https://airmore.ai/video-watermark-remover) | MP4/MOV/WebM/MKV/AVI/M4V up to 4GB / 60min; fixed boxes, Basic/Advanced billed 5/10 credits per started 30s; selected boxes don't track moving watermarks | Explicitly uploads for processing; total euro cost not verified; fixed box is poorly suited to moving overlays. | Defer. |
| [Reclip API](https://www.reclip.io/api/tools/watermark-remover) | Async REST/MCP, uploaded asset + region in percent; 90s max, quote and idempotency job flow | Requires server-held API key, credits, asset upload. Actual quality/cost and media retention not verified. | Defer API until human-approved paid test. |
| [HitPaw Online](https://online.hitpaw.es/pricing.html) | Free video watermark removal is preview-only; paid plan required for more exports | The marketing heading says free, but free export is restricted; current tier prices and limits can change. | Not a first P0 route. |
| [videowatermarkremover.app](https://videowatermarkremover.app/) | Browser-local FFmpeg WASM delogo/blur, source example with parameters and before/after hashes | Local delogo can smear moving detail; source project/code/license for app integration not verified. | Useful independent baseline only. |

## Non-negotiable boundaries

- Do not strip creator attribution or platform marks to redistribute, reupload, or obscure ownership of third-party TikTok/Douyin/Shorts videos. Analysis of abstract hooks and editing structure does not need a de-watermarked copy. Keep source link, capture time and rights status.
- Process **owned/cleared** source material only. Preserve original bytes; record any region, time interval, tool, version, output file/checksum and QA result separately.
- A successful pixel edit is not evidence of rights, authenticity, provenance, originality, or YouTube performance. Don't call any cleaning method lossless without frame-level testing.
- P0 runs without account keys, spend, automatic downloading, batch API, publishing, skill promotion or committing raw/cleaned source media.

## Next test

Obtain one owned/expressly licensed Maya & Ethan 12–25s video with a **synthetic overlay added by the user** (so exact unmarked original is available as ground truth). Compare WatermarkOut and VidProc with the same manually marked region. Measure cleanup artifacts at 3 fixed frames, actual runtime, failed exports and person-minutes needed to produce the accepted shot/beat map. Then decide **adopt / narrow / reject**; there is currently insufficient evidence to automate or vendor either engine.
