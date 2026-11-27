# Live Lore content strategy

The daily Short task reads this file before every run and follows it.
The weekly analytics task rewrites it every Monday from the data in analytics_log.csv.
OWNER INSTRUCTION (2026-11-24): the pipeline runs on its own. The daily task schedules each Short without waiting
for approval, and the weekly task may change anything the data supports: topics, hooks, length, titles, on-screen
text, graphics/animation (render.py house style), music, voice and speed. It can never override the core rules in
the task instructions (2-source fact checks, no criminal-allegation stories, original visuals and music only, privacy).

Data source: python3 pipeline/yt_analytics.py (YouTube Analytics API: per-video views, engaged views, avg view
duration, retention curves). Metricool stats are no longer needed.

Last updated: 2026-11-24 (first real per-video data: 14 Shorts, retention curves for 13)

## What our data says (YouTube Analytics, 2026-11-24, Shorts 1-15)
- Speed/voice is the biggest split. Shorts at speed 1.08-1.18 (#3,4,5,7,8) kept 49-61% of the video on average
  (mean 57%). Every Short at 1.25-1.3 (#9-15) kept 26-46% (mean 39%). Lengths were the same (~50-55 s), so it is
  not length. The three best (#3 57.9%, #5 59.3%, #7 60.9%) were all bm_george.
- Where people leave: on every Short the curve falls hardest between ~5 s and ~11 s (from ~95% to ~60%). The hook
  works (90%+ still there at 3 s); the "context" sentence right after it loses them.
- Views: best #14 Hunger Games 1,180, #5 1998 game 1,080, #15 dictionaries 1,074, #3 K-drama 881: big, widely known
  names with a number or a twist. Worst: niche local stories (#4 Seoul shopkeeper 32, #12 Netflix part-time job 87,
  #8 Symphony of Lights 104). Both nobody_talking_about Shorts with data got under 105 views.
- #13 (Godzilla again, 7-chunk first sentence) was the worst: only 16% stayed past the first seconds, 26% retention.
  Lesson: never repeat a story from the last 3 weeks, and keep the first sentence to one short line.
- Subs: 4 (+2 in two weeks). Views/day ~350. Far from YPP; retention is the lever, since it decides how far each
  Short is pushed.

## Topics
OWNER INSTRUCTION (2026-11-27): this is a WORLDWIDE pop culture channel. The Asia angle is a flavour, not the default.
Recent runs drifted: 12 of the last 14 Shorts were logged Asia-angle and 2 of the last 3 were Hong Kong stories.
- Hard quota per rolling 7 days (count from shorts_log.csv before picking): at least 4 GLOBAL stories (US/UK/Europe/
  worldwide: Hollywood and box office, streaming hits, music charts, gaming, celebrities, viral internet moments);
  at most 3 Asia-angle stories; at most 1 Hong Kong story. If a quota is full, pick a global story even if an Asia
  story looks stronger.
- Global stories stay global: do not bolt an "Asia watch" line onto a global story to make it count as Asia-angle.
  Log asia_angle = yes only when the story itself is about Asia or an Asian artist/company.
- Story discovery order: Google Trends US first, then worldwide WebSearch, then KR and JP, and HK last (HK only as a
  tie-breaker). Prefer stories that are trending in more than one country.
- Favour: big names people already know (major films/box office, GTA, BTS, Nintendo, Netflix hits, Taylor Swift-level
  music news, dictionaries/internet culture) with a surprising number or twist (data: these got 880-1,180 views;
  niche local stories got 32-104).
- Avoid: stories older than ~3 days unless there is a fresh angle; any topic or franchise covered in the last 21 days.

## Hooks (first 3 seconds)
- Lead with the most surprising number or claim, as a statement or a question.
- Rotate three hook types: surprising_number, contradiction, direct_question. DROPPED nobody_talking_about
  (2 Shorts with data: 104 and 87 views, vs 184-1,180 for the others). Log hook_type every time.
- First spoken sentence: one line, at most ~12 words / 4 caption chunks.
- Make the first on-screen text carry the hook on its own (works on mute). This is how we already build the
  first frame; keep it.

## The 5-11 s drop (new rule, from the retention curves)
- Sentence 2 must NOT be background. It raises the stakes or teases the payoff ("and the reason is wild", "but
  there's a catch", a second number). Background goes after ~12 s, in one sentence.
- At ~5 s, the render does a hard scene change: new background colour/scene, a big gold pill with the new number or
  claim, and a punch-in (scale 1.0 -> 1.08 over 0.3 s). No two consecutive scenes may look alike.
- Weekly task: check each Short's curve for the steepest drop and note the sentence that was playing.

## Length
- TEST (from Short 17, keep running; Shorts 17 and 18 are not live yet, so no result): alternate by Short number. Odd-numbered Shorts (17, 19, ...): ~35–40 s of narration.
  Even-numbered Shorts (18, 20, ...): ~48–52 s. Hard limit 58 s. Log the real length_s in shorts_log.csv.
- Why: 15 of 16 Shorts so far ran 45–55 s (only #6 at 40.9 s; #13–16 all ~54.5 s), so we have nothing to compare. The weekly task
  will judge by retention % (avg view duration ÷ length), not raw views, once per-video stats arrive.
- For a ~35–40 s Short: one hook line, 3–4 fact beats, one payoff, one short CTA. Cut context, not facts or sourcing.

## Tone
- OWNER INSTRUCTION (2026-11-10): scripts should be more casual, with Gen Z / Gen Alpha slang (e.g. "no cap", "lowkey", "it's giving", "cooked", "locked in", "rizz", "the vibes", "W / L", "bet", "ate", "fr"). Sound like a friend telling the story, not a news anchor.
- Keep it natural: 2-4 slang terms per Short, never forced, and don't use slang that mocks people or sits awkwardly on serious stories (e.g. deaths, tragedies). Facts, "reportedly" wording and the fact-check rules stay exactly as strict as before.
- No ALL CAPS in spoken text; spell slang the way Kokoro can pronounce it (test odd words like "rizz", "skibidi" before rendering).
- The weekly analytics task must not remove this without the owner's say.

## Voice
- From Short 21: bm_george, LANG en-gb, speed 1.18 (energetic FX as usual). Reason: its 3 Shorts kept 58-61% vs
  26-46% for every Short at 1.25-1.3 (see "What our data says"). Owner allowed voice changes on 2026-11-24.
- The weekly task judges it after 5 Shorts with data. If retention is not above ~45%, try am_michael at 1.18 next.

## Voice speed
- 1.18 (was 1.3; the owner's 2026-11-10 speed instruction is lifted by the 2026-11-24 instruction above).
  Allowed band now 1.10-1.32; the weekly task picks within it by data only.
- Hit the length target for that Short's test arm (see Length) by adding or cutting a sentence, not by changing speed.
  At 1.18 the same script runs ~10% longer, so write ~10% fewer words.

## Music
- TEST from Short 21: original background music from music.py (lofi, mixed under the voice; -14 LUFS, ducked) on
  Shorts where (number mod 4) is 1 or 2 (21, 22, 25, 26, ...); no music on the others (23, 24, 27, 28, ...).
  This crosses the odd/even length test so each length arm gets both. Log the music column in shorts_log.csv
  (style name or "none"). Run: python3 music.py lofi in/vo.wav in/vo.wav after voice.py. Judge by retention %.

## Post time
- 07:00 Asia/Hong_Kong daily. Allowed range for changes: 06:00–22:00 HKT, one daily slot.

## Publishing check (not a strategy change)
- Shorts 6, 17 and 18 were left as Metricool drafts (never published). Since approval is no longer needed, the daily
  task switches any leftover Live Lore drafts to scheduled in the next free slot, and checks each Short ends up
  "Published" (yt_analytics.py lists every live upload).

## Changelog
- 2026-11-24: first real per-video data (YouTube Analytics API). Owner made the pipeline autonomous (no approval
  step; weekly may change voice/visuals/music). Changes: voice bm_george en-gb 1.18 (58-61% vs 26-46% retention);
  dropped nobody_talking_about hook (87-104 views); new 5-11 s rule (biggest drop on every curve); 21-day repeat
  ban (#13 repeat was worst); favour big known names; music A/B test from Short 21.
- 2026-11-07: starting defaults.
- 2026-11-08: voice speed restored to ~1.27 after files were reverted to old values.
- 2026-11-09: weekly review. Only 2 subs and no per-video stats available (YouTube lag, 2 Shorts live). No change made.
- 2026-11-10: owner asked for faster narration; 2.0 was too fast, settled on speed 1.3 for future Shorts.
- 2026-11-10: owner asked for casual Gen Z / Gen Alpha slang in scripts.
- 2026-11-20: weekly review. Metricool still gives no per-video stats (only Shorts 1–3 listed, all blank), so
  hooks, voice, topics and post time are unchanged. One change: length A/B test (odd Shorts ~35–40 s, even ~48–52 s)
  from Short 17, because 15 of 16 Shorts were 45–55 s and there was nothing to compare. Voice: no data-backed
  winner; keep am_puck 1.3 (current default since Short 13).
  Speed band clarified to 1.22–1.32 (accent voices 1.25 if ever used again).
- 2026-11-23: weekly review. Metricool still gives no per-video stats (video list stops at Shorts 1-3), so topics,
  hooks, length test, voice, speed and post time are unchanged. Only 4 days of channel data this week (Nov 16-19:
  1,103 views, ~276/day vs ~367/day the week before); subs 2 -> 4. Added a note to keep hooks mute-proof (already
  our practice) and a publishing check after finding Short 6 never published.
- 2026-11-27 (owner): worldwide focus restored: per-7-day quota of 4+ global, max 3 Asia-angle, max 1 Hong Kong; Trends US first, HK last. Reason: 12/14 recent Shorts were Asia-angle; global big-name stories got the most views.
