# Measurement & attribution contract v0.1

The purpose is to decide what to create next, not to assert access to YouTube's ranking model.

## Time windows

Snapshot at roughly 24, 72 and 168 hours after publication. Store the **actual** age in hours; do not pretend it is exactly 24/72/168. Compare at the same age window and channel/format.

## Primary decisions

1. **Qualified reach:** Shorts use `engaged_views` (not raw starts/replays). Long-form pairs watch time with views/impressions. No composite mixing incompatible denominators.
2. **Viewer relationship:** `subscribers_gained` relative to the appropriate video exposure metric. Video-scoped API subscribers can exclude subscriptions that happen elsewhere.
3. **Production efficiency:** actual monetary cost per *accepted* finished minute and minutes of human review per accepted minute. Unknown costs are unknown.

Drivers: Shorts shown in feed, stayed-to-watch %, average view duration / percentage; long-form thumbnail impressions, CTR, average duration, retention curve; traffic source and geography when available.

Guardrails: originality/rights compliance, audience satisfaction signals, error rate, total human oversight, and monthly spend cap.

## Explicit data hazards

- YouTube changed Shorts raw views counting on 2025-03-31. Keep both `views` and `engaged_views` when available.
- Public competitor view counts do not reveal feed impressions, average view duration, CTR, retention or recommendation reasons.
- `shown_in_feed` and `engaged_views` may cover different traffic scopes; compute a ratio only when numerator and denominator are demonstrably aligned.
- Some retention/CTR measures require Studio exports rather than a generic Analytics API report. Do not synthesize missing fields.
- A snapshot from a 3-hour-old video cannot be compared with a 7-day lifetime count.
- Algorithmic exposure is a confounder; observational comparisons are hypotheses, not clean causal effects.
- Separate Shorts / long / live, duration bucket, channel, topic and traffic source before interpretation.
- When matched samples are fewer than 5, tag `insufficient-data` for an automatic winner. Five is only an operational guardrail, not statistical significance.
- Zero measurements are real zeros; missing measurements are null and must stay missing.

## Evidence-backed review

For each experiment:
1. State the creative change before looking at the result.
2. Show the matching comparison set, age, channel, format and count.
3. Report actual views/engaged_views and other relevant measures without a fabricated magic score.
4. State distribution differences, missing data and timing caveats.
5. Recommend continue / narrow / pivot / pause / insufficient-data.
6. Require human confirmation before applying production strategy or skill changes.

## References

- YouTube Analytics API metric definitions: https://developers.google.com/youtube/analytics/metrics
- YouTube Analytics channel reports: https://developers.google.com/youtube/analytics/channel_reports
- Shorts Analytics: https://support.google.com/youtube/answer/12942217?co=YOUTUBE._YTVideoType%3Dshorts&hl=en
- YouTube inauthentic / reused content policy: https://support.google.com/youtube/answer/1311392?hl=en
