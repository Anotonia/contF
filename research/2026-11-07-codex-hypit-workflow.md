# Research note: Codex + Hypit + H3 (2026-11-07)

**Source:** https://x.com/AomyYing/status/2118654299689689417  
**Subject:** Creator-reported approach to reducing AI video retries with story/shot preflight, reference frames, partial reuse and human review.  
**Status:** Research source, not an independent reproduction or benchmark.

## Reported observations (author claims)

- 28-second, six-shot short produced in seven final generation calls, about 315 credits / RMB 2.8 and 35 minutes.
- Scripts, shot plans and style frames produced before costly generation.
- H3/CompShare used for short clips; Grok web workflow used for some talk-show clips.
- Partial trim/crop/retry and candidate reuse preferred to a whole-video restart.

## Independently checkable software/platform facts

- Hypit repository: https://github.com/hypit-ai/hypit
- Hypit planning/pricing: https://hypit.ai/quickstart/run/
- CompShare billing: https://compshare.cn/docs/minimax-h3/billing
- GitHub license: https://github.com/hypit-ai/hypit/blob/main/LICENSE

## Material caveats

- The provider's documented 768P rate may differ from the creator's 9 credits/s anecdote; check live estimates before spending.
- Hypit carries a modified Apache-style license with restrictions on multi-tenant commercial offerings and redistribution.
- Creator-reported cost excludes human overhead and may not generalize.
- 'Zero random draws' is not literally supported: dynamic video flaws still need review/retry.
- The technique reduces production variance; it does not validate a YouTube growth hypothesis.

## Hypothesis for contF

Front-loaded beat/script/frame checks plus shot-level reuse lower accepted-minute cost without worsening human quality approval.

## Next test

For a Maya & Ethan original 20–40s scene, compare baseline FT versus preflight/shot-level process. Record accepted shots, rerun duration, cost, time, and reviewer judgment. Human approves generation spend.
