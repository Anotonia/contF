# 2026-11-15 — Hypit 0.3.2 adoption gate: upstream security and rendering reports

**Decision: NARROW / do not adopt untrusted-reference processing yet.** Accessed 2026-11-15 (Europe/Madrid). Read contF main README, AGENTS, ROADMAP, architecture, measurement, cross-platform SOP, Nov 7 ledger, Reference-to-Variant SOP/matrix, and Nov 12 Hypit 0.3.2 note. Previous main commit: 330d7a4f75fde3312f4e998ad2c5027cc9c85f4c. No code, production, Skill, or publication changes.

## New primary-source *reports* since the existing release note

Hypit maintainers' GitHub issue tracker shows the following **open upstream reports**, not independently reproduced by contF; existence and reporter-supplied reproduction steps are verified, exploitability in our environment is not:

- [#478](https://github.com/hypit-ai/hypit/issues/478), opened Nov 7: Studio serves project SVGs in its own origin without a restrictive CSP; reporter says an SVG script can access Studio session and reach source-update routes. Fix proposed in #471. **Implication:** do not ingest untrusted SVG/project media in a local Studio pilot.
- [#479](https://github.com/hypit-ai/hypit/issues/479), opened Nov 7: local HTML render server reportedly accepts arbitrary Host headers despite binding to 127.0.0.1, creating a DNS-rebinding exposure window while rendering. Fix proposed in #472. **Implication:** no untrusted web content alongside the pilot; isolate network and media.
- [#489](https://github.com/hypit-ai/hypit/issues/489), opened Nov 12: Windows local WhisperX runtime reportedly fails to launch due to a log-file sharing conflict. Reporter provides a local workaround, not a released fix.
- [#490](https://github.com/hypit-ai/hypit/issues/490), opened Nov 12: typography Flow with word wrapping reportedly splits English words mid-letter. **Implication:** subtitle/text-layout QA required even for no-generation renders.

Official [releases](https://github.com/hypit-ai/hypit/releases) still show **v0.3.2 released Nov 11** as latest at check time; issues are **not** evidence of a patched release. These reports add a concrete safety and subtitle-accuracy gate to Issue #7, not a reason to run any third-party reference automatically. License remains Hypit Open Source License with SaaS redistribution restrictions as recorded previously. No version promotion.

## Issue #2 radar attempt and evidence quality

On 2026-11-15 separately searched TikTok, Douyin, YouTube Shorts for recent couple/family/relationship comedy original posts. TikTok direct creator-page access was blocked by robots/access policy; Douyin search was dominated by unrelated commerce/index pages; YouTube searches did not yield a new independently verifiable canonical creator permalink with labeled metrics and full playable footage. **New eligible original-video candidates: 0; full videos viewed: 0; new matched non-success controls: 0.** Do not reuse previously recorded titles as fresh evidence. Existing success *candidate* YT1 (Micah & Sarah, https://www.youtube.com/shorts/oDJLvBfaRpM) and same-creator YT2 (https://www.youtube.com/shorts/Z3lVKzwildY) remain **unmatched** because age-normalized comparable observations and complete film review are absent. Public counts from Nov 7 are historical only; not refreshed today.

**Untested mechanism H13 — visible priority inversion:** a household character announces a sensible priority, but their first action reveals a contradictory personal priority. Evidence basis: an abstract situational-comedy mechanism, **not** a new film observation or proven high-performing pattern. Alternative explanations: creator following, sound, exposure and posting time. No timecodes or audience outcomes invented.

## Original Maya & Ethan 18s design only: “The Quiet Zone”

0–2s Ethan proudly posts a QUIET ZONE sign on the living-room door. 2–5s Maya tiptoes in carrying a book, while Ethan gives an exaggerated shushing gesture. 5–9s Ethan starts unwrapping an impossibly crackly snack bag; Maya looks up. 9–13s Ethan tries to muffle the bag under a cushion, which makes the noise worse. 13–16s Biscuit walks in carrying a small squeaky toy; Ethan rushes to confiscate it. 16–18s Ethan steps on the toy himself: SQUEAK. Maya silently flips the sign to “ETHAN ZONE”; Ethan freezes.

**A/B variable only first 2 seconds:** A opens on Ethan's exaggerated shushing and immediately visible noisy bag; B opens on his proud QUIET ZONE announcement. Hold remaining cast, props, payoff, duration and rendering method constant. Design only: no external media reused, no model generation, no publishing. Rights risk low for independent script; validate no source-specific expression copied before production.

## Minimal next test

P0 Issue #2: legally view one original canonical Short end-to-end, timestamp all cuts and expressions, and acquire one same-creator near-age comparison; otherwise label reference insufficient and use an **owned** 12–25s clip to test annotation mechanics, not audience causality.

P0 Issue #7: before installing/running Hypit, verify upstream #478/#479 resolution at an exact commit and rerun sandboxed, offline, owned-media text/layout test. Do not use untrusted SVG, third-party media, private analytics, paid models, or publish. Production consistency and channel growth remain separate; owned YouTube Analytics not authorized/connected.
