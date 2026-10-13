# Sound design and mix

Sound does at least half of the work of an effect. Run it as a separate pass after picture is locked.

## Cue sheet first

Build a table before touching audio: `effect | final time (s) | sound | source | level`. Show it to the
user together with 3 frames that have the sound marked. Times come from the time map, so sound lands on
the same frame as the effect.

## Match sound to material and timing

- Pick a sound for the material: lighter click and gas hiss for fire; crisp paper crackle for a crumple;
  wet spray and squeak only while the cloth moves for a wipe; plastic crack plus tinkling shards for a pop;
  button click on the exact press frame; marker on glass only while the hand moves.
- **Motion sounds start when motion starts; late is better than early.** A sound a frame or two after the
  event feels natural; a sound before it feels wrong.
- Layer a low "thud" (30-80 Hz) under big hits and a short high "air" on whooshes; keep them dry and
  short rather than reverberant.
- Silence is an instrument: duck or cut music during a blackout, a freeze or the second before a drop.

## Mix

- Speech is the anchor: cut it with the same time map as the picture.
- Music under speech at low level (about -24 to -20 dB below speech peaks), ducked further under
  effects and stings; it fades out in blackouts and freezes.
- Sound effects placed with millisecond accuracy (sample position from the cue sheet).
- Normalise the final mix for social to about **-14 LUFS integrated, true peak below -1 dBTP**:

```bash
ffmpeg -i mix.wav -af loudnorm=I=-14:TP=-1.5:LRA=11 -ar 48000 out.wav
```

## Sourcing

- Use the user's own files first. Otherwise: sounds licensed for commercial use, or synthesise simple
  ones in code (noise bursts, sine sweeps, filtered clicks). Do not fetch copyrighted tracks.
- If the user has an ElevenLabs key, sound-effect generation is available; ask first, it costs money,
  and never ask them to paste the key in chat (use an environment variable).
- PixVerse also offers a sound-effect endpoint for a generated clip (`/video/sound_effect/generate`).

## Common mistakes

Same whoosh on every cut; music too loud under speech; sound before the event; effects with no tail;
clipping when stacking hits (lower each layer instead of limiting the whole mix).
