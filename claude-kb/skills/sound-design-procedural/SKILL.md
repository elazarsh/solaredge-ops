---
name: sound-design-procedural
description: Sound design for motion videos - what each visual event should sound like (slam, whoosh, riser, tick, pop, shimmer, glitch, final hit), layering recipes, beat-locked music beds, sidechain pumping, panning, loudness targets, and how to generate everything procedurally with numpy (sfx.py) or choose licensed sources/AI tools when needed. Use when a video needs sound (ads, reels, explainers, intros), when a render feels "silent/flat", or when syncing cuts and hits to a beat (סאונד, אפקטים, מוזיקה, סינכרון לביט).
---

# Sound design for motion video

Sound is roughly half the perceived quality. A visually great video with generic music and no hits feels cheap; a good mix makes simple motion feel expensive.

## Principles
1. **Pick the BPM first; build the grid.** 120 BPM -> beat 0.5 s, bar 2 s. Scene boundaries on bars; slams/hits on beats; transitions end on a downbeat.
2. **Every visible impact gets a sound**, every sound has a visible cause. No sound without motion, no big motion without sound.
3. **Layer by function:** hit = sub boom + body thump + crack/transient + tail reverb; transition = whoosh (movement) + optional impact on landing; reveal = shimmer/pop; UI = tick/key/click.
4. **Anticipate:** risers end exactly on the hit frame (place with lead = riser length); leave 1-3 beats of relative quiet before the biggest hit; a reverse swell/riser into each major scene.
5. **Whoosh peaks mid-move**, not at the start; pan it in the direction of motion (move left -> sound travels right-to-left). Don't reuse an identical envelope for every cut (vary length/pitch/pan).
6. **Music supports hits:** sidechain/pump the bed on kicks (~45 % dip, 0.2 s release); build energy with the story (pad only -> kick -> bass+arp -> hats/clap -> peak -> taper for the CTA).
7. **Mix hierarchy:** hits/SFX > voice (if any) > music bed. Keep sub (<120 Hz) mono. Soft-limit; true peak <= -1 dBTP; integrated loudness about -14 LUFS for social (-16 for podcast-like voice pieces).
8. **Space:** a short plate/hall reverb on the SFX bus (wet ~0.15) glues one-shots; keep music pad dry-ish.
9. **Silence is a tool:** a half-second drop-out before the hero reveal makes the hit land.
10. **Audio-reactive visuals** only from pre-extracted data; text scale pulse <= 3-6 %, glow <= 30 %.

## Event -> sound map
| Visual event | Sound | Notes |
|---|---|---|
| Text slam | impact: sine thump 150->45 Hz + highpassed crack + 36 Hz sub | power 0.5-1.0 by importance |
| Scene transition (whip/zoom/push) | whoosh: band-passed noise sweep 350->7000 Hz, bell envelope | pan by direction; zoom = no pan |
| Build to a hit | riser: noise + rising tone, quadratic swell | ends on the hit frame |
| Counter counting | ticks rising in pitch | 6-10 ticks across the count |
| Typing | soft key ticks per character | quiet (0.35) |
| Chip/card pop | bubble pop: sine glide 380->1000 Hz | vary power |
| Success/check | click + shimmer | |
| Glitch | bit-crushed gated noise + square | 0.2-0.4 s |
| Final logo lock | hit: big impact + minor-chord stack + shimmer | cam shake + burst at the same frame |
| End fade | reverse swell into silence | last 0.8 s |

## Using the toolkit (`motion-toolkit/assets/sfx.py`)
Compositions emit cues with `HF.cue(t,type,opts)` (helpers like `HF.slam/whip/zoomThrough/burst/type` emit them automatically); `render.js` writes `cues.json`; `sfx.py cues.json out.wav --duration D --bpm B --energy "0:0.2,4:0.75,..." --key A` renders SFX + music and `build.sh` muxes it. Cue types: `slam hit whoosh riser swell tick key click pop shimmer glitch`. Cue time = landing/peak time: a `riser`/`swell` cue at `t` with `dur` starts at `t - dur` and peaks exactly at `t`, so cue it at the hit it builds into (riser `t=29,dur=2` for a hit at 29), never at the start of the build. Energy map: <0.35 pad only, >=0.35 kick, >=0.55 bass+arp, >=0.7 hats+clap, >=0.9 extra arp level. Tweak `--sfx-gain/--music-gain` (e.g. 1.2/0.8 for a punchier mix).

## Verifying without ears
You can't listen: verify structurally - `qa.sh` prints loudness/true peak; compare waveform peaks to visual hit times (`wave.png`); check no clipping (peak <= -1 dB); confirm silence/duck before hero hits; report "not auditioned" honestly and ask the user for taste feedback (more bass? calmer bed?).

## Other sources
- AI music/SFX: Suno (music, prompt for "cinematic hit/riser/transition" stems), ElevenLabs (SFX + voice/dubbing; Hebrew V3 best), MiniMax. Treat licences as per plan terms.
- Libraries: freesound/Pixabay/Sonniss (check licence per file). Never use unlicensed commercial music.
- Voice-over: Hebrew TTS quality varies; ElevenLabs V3 + niqqud for tricky names; record yourself when emotion matters. Duck music under voice by 8-12 dB.

See also: `motion-design-wow` (rhythm layer), `motion-toolkit`, `video-wow-review`.
