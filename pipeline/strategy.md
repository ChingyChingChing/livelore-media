# Live Lore content strategy

The daily Short task reads this file before every run and follows it.
The weekly analytics task rewrites it every Monday from the data in analytics_log.csv.
It can tune topics, hooks, length, voice and post time. It can never override the core rules in the task
instructions (fact-checking, no criminal-allegation stories, original visuals only, privacy, and the owner's
approval before anything is scheduled).

Last updated: 2026-11-20 (Metricool still has no per-video stats; one change: length A/B test)

## Topics
- Mix: ~60% global headline stories, ~40% Asia-angle stories (at least 2 Asia-angle a week).
- Favour: film/TV releases and box office, K-pop / C-pop / anime news, viral internet moments, stories from
  Chinese-language sources that English channels haven't covered yet.
- Avoid: stories older than ~3 days unless there is a fresh angle; topics covered in the last 7 days.

## Hooks (first 3 seconds)
- Lead with the most surprising number or claim, as a statement or a question.
- Keep rotating the four hook types (surprising_number, contradiction, direct_question, nobody_talking_about) and
  log hook_type every time. No winner yet: no per-video stats (as of 2026-11-20).

## Length
- TEST (from 2026-11-20): alternate by Short number. Odd-numbered Shorts (13, 15, ...): ~35–40 s of narration.
  Even-numbered Shorts (14, 16, ...): ~48–52 s. Hard limit 58 s. Log the real length_s in shorts_log.csv.
- Why: 11 of 12 Shorts so far ran 45–55 s (only #6 at 40.9 s), so we have nothing to compare. The weekly task
  will judge by retention % (avg view duration ÷ length), not raw views, once per-video stats arrive.
- For a ~35–40 s Short: one hook line, 3–4 fact beats, one payoff, one short CTA. Cut context, not facts or sourcing.

## Tone
- OWNER INSTRUCTION (2026-11-10): scripts should be more casual, with Gen Z / Gen Alpha slang (e.g. "no cap", "lowkey", "it's giving", "cooked", "locked in", "rizz", "the vibes", "W / L", "bet", "ate", "fr"). Sound like a friend telling the story, not a news anchor.
- Keep it natural: 2-4 slang terms per Short, never forced, and don't use slang that mocks people or sits awkwardly on serious stories (e.g. deaths, tragedies). Facts, "reportedly" wording and the fact-check rules stay exactly as strict as before.
- No ALL CAPS in spoken text; spell slang the way Kokoro can pronounce it (test odd words like "rizz", "skibidi" before rendering).
- The weekly analytics task must not remove this without the owner's say.

## Voice
- The 12-Short test is done but NO winner can be named: Metricool has returned no per-video views or watch time
  for any Short (as of 2026-11-20). Until the weekly task names a voice here, run the VOICES.md rotation a second
  time in the same order (Short 13 = am_michael, 14 = bm_george, 15 = am_puck, 16 = bm_george Scottish,
  17 = am_onyx Caribbean, 18 = hm_omega, 19 = jm_kumo, 20 = zm_yunxi, 21 = im_nicola) so every voice gets a 2nd data point.
- Weak lead only (not a decision): the two biggest whole-channel view days were am_michael days (#2: 856, #4: 992);
  the two smallest were bm_george days (#3: 57, #5: 63). Daily channel views mix all videos, so this is not proof.

## Voice speed
- OWNER INSTRUCTION (2026-11-10): narration speed 1.3 for future Shorts (owner tried 2.0, too fast). VOICES.md speeds (about 1.13-1.24) are slightly slower than this; use 1.3 for the main voices, accent voices proportionally slower. The weekly analytics task must not change this without the owner's say.
- Allowed band is 1.22–1.32 (1.18 is too slow, 1.35 slightly fast). Main voices 1.3; accent voices 1.25
  (as used for Shorts 9–12), never below 1.22 even though VOICES.md lists 1.13.
- Hit the length target for that Short's test arm (see Length) by adding or cutting a sentence, not by changing speed.

## Post time
- 07:00 Asia/Hong_Kong daily. Allowed range for changes: 06:00–22:00 HKT, one daily slot.

## Changelog
- 2026-11-07: starting defaults.
- 2026-11-08: voice speed restored to ~1.27 after files were reverted to old values.
- 2026-11-09: weekly review. Only 2 subs and no per-video stats available (YouTube lag, 2 Shorts live). No change made.
- 2026-11-10: owner asked for faster narration; 2.0 was too fast, settled on speed 1.3 for future Shorts.
- 2026-11-10: owner asked for casual Gen Z / Gen Alpha slang in scripts.
- 2026-11-20: weekly review. Metricool still gives no per-video stats (only Shorts 1–3 listed, all blank), so
  hooks, voice, topics and post time are unchanged. One change: length A/B test (odd Shorts ~35–40 s, even ~48–52 s)
  because 11 of 12 Shorts were 45–55 s and there was nothing to compare. Voice: no winner; rotation round 2.
  Speed band clarified to 1.22–1.32 (accent voices 1.25, as already used).
