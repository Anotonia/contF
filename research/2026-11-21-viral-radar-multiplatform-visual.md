# Viral Radar — 2026-11-21: first visually inspected cross-platform batch

**Decision: NARROW / insufficient-data.** First run where footage was actually inspected on all three platforms (public pages, logged out, muted/visual-only). 10 new original permalinks + 3 previously unlinked Oddinary Couple Shorts resolved; 8 references visually inspected (tier A). **Audio was not heard anywhere** → all VO/music/dialogue/pause fields are `null`, so dialogue-dependent reversals stay unverified. No controlled evidence; nothing below is a causal claim.

Read: README, AGENTS, ROADMAP, architecture, measurement, [radar SOP](../docs/cross-platform-viral-radar.md), [daily operations](../docs/daily-operations.md), Nov 7–15 notes. Prior head `2d823f5`. Deduplicated every ID against `research/*.md`. observed_at 2026-11-21 ~09:05–09:30 UTC. All metrics `source_type=platform`, raw lifetime counts (not engaged views, not post-age-normalized). No login, CAPTCHA, download, redistribution, posting or spend.

**Pre-search unknown:** does a visible action followed by a second character's reaction/reversal read faster than dialogue-led setup? It decides the final-beat staging of the next Maya & Ethan storyboard.

## Candidate ledger

Metric labels: V = visible "views", K = likes button label, C = comments label, S = shares/收藏 label; icon-only counters = `unknown_metric`.

### YouTube Shorts (THE ODDINARY COUPLE = OC, @theoddinarycouple)

| ref | permalink | title | published | dur s | metrics | tier | watched |
|---|---|---|---|---:|---|---|---|
| YT-OC-NF | https://www.youtube.com/shorts/IcqbwIAzcdE | NO FILTER ON HER | 2026-10-26 | 16.68 | V 1,046,126; K 11,373; C 17 | A (visual) | scrubbed full timeline, muted |
| YT-OC-HIM | https://www.youtube.com/shorts/1I_qL2w2_Lc | Him every day | 2026-10-25 | 9.92 | V 36,331; K 511; C 2 | A (visual) | scrubbed, muted |
| YT-OC-PREG | https://www.youtube.com/shorts/6agUgtVuW_4 | Most painful moment is pregnancy | 2026-10-27 | 17.06 | V 27,127; K 460; C 2 | A (visual) | scrubbed, muted |
| YT-N21-1 | https://www.youtube.com/shorts/B51mKb_whcg | Every husband is crying after seeing this | 2026-11-20 | 24.72 | V 26,224; K 620 | B | opening only |
| YT-N21-2 | https://www.youtube.com/shorts/W-l0VquXWEI | 99% problems ka solution | 2026-11-18 | 23.22 | V 14,985; K 305 | B | opening only |
| YT-N21-3 | https://www.youtube.com/shorts/NJmyWUmGieY | Aj ka mood yhi hai | 2026-11-08 | 11.06 | V 14,565; K 366 | B | opening only |

- NF/HIM/PREG were Nov 10 vidIQ-only (grade C); now original-page verified. OC Shorts grid (latest 9, rounded): 26K,15K,35K,29K,14K,432K,29K,14K,25K → descriptive median 26K, mixed 11–44s, not age-normalized. NF ≈ 29–40× its two adjacent same-creator Shorts at ~25–27 days age (partially matched: same set/cast, different topic/duration for HIM).
- N21-1 vs N21-2: same creator, ~24s, 1 vs 3 days old → **unmatched post-age**; re-read both at 72h before comparing.
- **YT8** (Bong Couple's, https://www.youtube.com/watch?v=9nmmOG-wVZc) now shows "This video isn't available anymore" → retire from P0; the Nov 9 6.8M figure is historical only.
- Micah & Sarah (existing): oDJLvBfaRpM V 239,422 / K 6,017 (2026-05-13, 11.46s); Z3lVKzwildY V 273,147 / K 6,497 (2026-04-30, 15.04s). Refreshed counts, opening only; not a hit/control pair.

### TikTok (@thequistfamily, Courtney & Alex; original sound)

| ref | permalink | published | dur s | metrics | tier | watched |
|---|---|---|---:|---|---|---|
| TT-Q1 | https://www.tiktok.com/@thequistfamily/video/7247234943888166187 | 2023-06-21 | 10.98 | V 10.6M; K 918.7K; C 2,307; 91K unknown_metric | A (visual) | frame-stepped, muted |
| TT-Q2 | https://www.tiktok.com/@thequistfamily/video/7266452976175303982 | 2023-08-12 | 15.44 | V 4.3M; K 225.6K | B | no |
| TT-Q3 | https://www.tiktok.com/@thequistfamily/video/7269161237051641130 | 2023-08-19 | 14.95 | V 3.4M; K 97.6K | B | no (login modal) |
| TT-Q4 | https://www.tiktok.com/@thequistfamily/video/7248685313382616366 | 2023-06-25 | 5.87 | V 4.6M; K 330.1K | B | no |
| TT-C1 (contrast) | https://www.tiktok.com/@thequistfamily/video/7262101272206052651 | 2023-07-31 | 9.15 | V 26.7K; K 1,269 | B | no |

V = "N views" on the creator's COMEDY playlist modal; K = video-page aria-label. TT-C1 is same creator/playlist/duration band within 6 weeks of TT-Q1 but a different theme → **partially matched contrast**. Visible playlist (n=19): 11.4K–10.6M, median ~58.6K — a curated playlist, not a creator baseline. Posts are ~2.4 years old (2023 platform era). The creator was previously known only via the RefVid vendor claim (Nov 10); still not the same video.

### Douyin

| ref | permalink | creator | published (UTC) | dur s | metrics (views null) | tier |
|---|---|---|---|---:|---|---|
| DY-1121-01 | https://www.douyin.com/video/7675642578829888745 | 福宝乖乖 (dog vs spouse) | 2026-08-19 | 17.60 | 点赞 7; 评论 2 | A (visual) |
| DY-1121-02 | https://www.douyin.com/video/7673755137479791338 | 大玉有点甜 (series ep. 53) | 2026-08-20 | 14.73 | 点赞 659; 评论 83; 收藏 46; 分享 52 | A (visual) |
| DY-1121-03 | https://www.douyin.com/video/7671938070707660462 | 大陈小小苏 (literal styling requests; "虚构演绎") | 2026-08-09 | 45.80 | 点赞 6,829; 评论 277; 收藏 258; 分享 6,694 | A (visual) |
| DY-1121-04 (contrast) | https://www.douyin.com/video/7673776710538523753 | 大玉有点甜 (ep. 54) | 2026-08-18 | 23.53 | 点赞 401; 评论 77; 收藏 27; 分享 125 | A (visual) |

Douyin shows no public view counter on these pages; likes/shares are labeled. 02 vs 04 = adjacent episodes 48h apart, different duration/staging → **unmatched contrast candidate**; fewer likes ≠ non-hit. 03 is a longer proof point (45.8s), outside the 10–25s cohort.

## Film-level decomposition (visual only; cuts ±0.3s; audio null)

**TT-Q1 (10.98s, 3 shots)** — [observed] 0–1.6 wide exterior: husband carries wife over shoulder toward a house; frame-0 text card "Returning my wife because she's too expensive 💰" states the full premise (H+S at once). ~1.6–3.0 cut to handheld medium follow on porch. ~3.0–8.3 static medium-wide on front door, "*KNOCK*", father opens, subtitles "She's too expensive" → "I'm leaving her here!", wife set down (C/E). ~8.5–10.2 father "HEY!😡 … I said no returns!" pushes back (R/P, delivered by a **third party**). ~10.2–10.98 tighter on wife alone smiling; loop to frame 0 [loop intent inferred]. Burned-in captions on every line; action → third-party reaction.

**YT-OC-NF (16.68s, 4 shots)** — [observed] 0–~1.55 medium seated two-shot on bed, she raises a snack tub, he grabs her wrist (interrupted action = H/S/C, no text overlay). ~1.55–~7.8 tight man-dominant reverse, her hand/snack foreground. ~7.8–~15.15 woman-dominant close two-shot, knitted brows, sustained gesturing (E, inferred). ~15.15–16.68 **man alone** in tighter reaction framing, pressed lips, sideways look (P candidate, inferred). No dense subtitles; slight drift only. R/L null without audio.

**YT-OC-HIM (9.92s)** — [observed] doorway standing two-shot held ~8–9s with gesture exchange; brief wider reframe ~9–9.6; ends on a lettered graphic card "MY PREGNANT WIFE EVERY MORNING". No isolated reaction shot.

**YT-OC-PREG (17.06s, 3 shots)** — [observed] 0–~12 woman alone pacing in hallway, overlay "THE BIGGEST PAIN IN PREGNANCY IS"; ~12–15.15 cut to man reclining on bed with phone, overlay "SEEING HIM TOTALLY RELAXED & FREE EVRYDAY 😡" (reveal R, inferred); ~15.15–17.06 back to her displeased face. Has an isolated reaction ending yet low views → counterexample.

**DY-1121-01 (17.6s, single shot)** — [observed] caption "好想吓它一下" primes a startle; one drifting medium shot of a drowsy dog; eyes reopen ~15.8, head drops ~16.7, holds. Expectation set by text, resolved by a long hold (no human visible).

**DY-1121-02 (14.73s, 2 shots)** — [observed] 0–~7.85 handheld follow of dressed-up man in night plaza, caption about pretending to be single; cut ~7.85 to woman close-up with child behind → speaker/role reveal (R/P inferred).

**DY-1121-03 (45.8s, 1 fixed framing)** — [observed] centered static two-shot; ~10 appearance changes (~3.3, 6.9, 9.9, 15, 24, 26.7, 33.2, 35.8, 38.7s) escalating a literal reading of stated preferences; earnest faces unchanged (E by accumulation). Highest shares in the Douyin set.

**DY-1121-04 (23.53s, 2 shots)** — [observed] ~0–2.5 layered selfie, ~2.5–23.53 handheld mirror/over-shoulder; a card prop recurs ~2.5–4.3 and ~19.4–21 (callback L, inferred).

## Cross-platform pattern (observed sample, n small, survivorship-prone)

| | top item in creator set | its contrast(s) |
|---|---|---|
| Premise readable by ~1.6s without audio | TT-Q1 (text card), NF (grab) | PREG (text, yes), HIM (posture only) |
| Final beat = a *second* character's visible reaction that reverses the protagonist's move | TT-Q1 (father), NF (isolated partner face) | PREG (isolated reaction too), HIM (graphic card) |
| Shot count | 3–4 in 11–17s | 2–3 |

**H11 [untested]: the payoff is a second character refusing/answering the protagonist's move on camera, with the premise readable silently by ~2s.** Basis: TT-Q1 and NF, the clear top items in their same-creator sets. **Against it:** PREG has an isolated reaction ending and low views; HIM/TT-C1 differ in topic too; TT data is 2023-era; audio/dialogue (likely the real punchline in NF) is unheard; distribution, creator audience and selection bias are uncontrolled. Douyin offers a different lever (hold length before payoff; DY-01, DY-03) with no views data.

## Maya & Ethan original test — design only (approval-gated)

**"No Refunds" (18s, kitchen, Maya/Ethan/Biscuit; no reference dialogue, props, sound, likeness or framing):** 0–2s Ethan proudly slides a sticky-note-covered "chore coupon book" to Maya (silent-readable text: "1 FREE DISHWASH"). 2–8s Maya tears out a coupon and hands it back; Ethan points to tiny print "EXPIRED". 8–13s Maya flips the book: every page is stamped EXPIRED. Ethan tries to hand the whole book to Biscuit. 13–18s **Biscuit drops it back at Ethan's feet and walks off** (reversal by a third character); hold.

- **A:** final 3s on Biscuit's refusal held in the shared wide (both humans + dog).
- **B:** identical except the final 3s cut to an isolated close reaction (Ethan's face after the dog walks off).
- One lever only (final-beat framing); cast, script, timing, music fixed. Dog action may need a composited/practical cue. Measures, once owned data exists: stayed-to-watch, AVD, engaged views at 24/72/168h; else muted blind-viewer check "who rejected the coupon?" as a no-spend proxy.
- **Gate:** human script/rights approval before any storyboard generation; budget approval before paid generation; separate approval to publish. No Skill promotion.

## Access blockers (exact)

- **YouTube:** YT8 unavailable; Shorts player gave no audible monitoring in this environment → audio null.
- **TikTok:** logged-out `search/video` never loaded; @thecallaces grid → "Something went wrong" then slider CAPTCHA (closed, not attempted); direct permalinks overlay "Log in to TikTok" (TT-Q3 unwatched); playing from the profile playlist modal worked without login.
- **Douyin:** search requires login ("登录后即可搜索更多精彩视频"); one indexed lead deleted (7672949104981004681, "你要观看的视频不存在"); 胡大央 profile "服务异常"; login popup dismissed with its own X, app-open prompts declined.

## Next smallest test

1. With audio available, finish frame-accurate audiovisual maps of NF, PREG and TT-Q1, and watch TT-C1 + TT-Q2 (same-creator contrast) to check whether H11's "second-character reversal" actually separates them. If it does not, reject H11.
2. Re-read YT-N21-1 / YT-N21-2 at ≥72h for an age-matched same-creator pair.
3. Owner: approve or reject the "No Refunds" A/B script for a no-spend muted storyboard check. Owned YouTube Analytics still unconnected.
