# Prompt template: one-shape UI morph (adapted from a proven prompt)

Use as the internal brief when the user asks for a premium UI/brand motion piece. Fill the
brackets from the intake; keep the banned list verbatim.

```
Ask me for: [8–12] UI states the shape should become (e.g. button, loader, player, slider,
toggle, tabs, chart, command palette, toast), pure black & white or one accent color, and a
royalty-free song around [120] BPM with a commercial license.

Dribbble-level UI motion. One shape, never cut: every state is the same element morphing its
size, radius and color while its content swaps with a short blur. A cursor drives every change
with real clicks and drags. Light warm-gray canvas, black and white components, one clean UI font
(Heebo for Hebrew). Springs everywhere, a tiny overshoot at most. The camera zooms so each state
fills the frame. The last frame is the first frame, so it loops. All on-screen text in Hebrew.

Banned: bouncy easing, particle bursts, glows, gradients on UI chrome, mismatched icon strokes,
dead time, anything that looks like a template.

[BPM] BPM, [N] bars, something happens on every beat.
[State chain, e.g.] Button → loader → check → dynamic island → music player with play/pause morph
→ scrub the progress bar → volume slider that stretches when dragged past max → toggle flips on
the beat → knob becomes a liquid tab indicator → tabs open into a chart that draws itself with a
hover tooltip → collapses into ⌘K → type to filter → enter → toast → back to the button.

Build:
1. One HyperFrames composition, [1440x1440]. Every style is computed from time inside render(t)
   (Motion.bind): no CSS transitions, no timers, no state carried between frames.
2. Springs are closed-form step responses; a value that changes target many times is the sum of
   one spring per change (Motion.track).
3. The tab indicator's two edges ride different springs so the leading edge stretches ahead
   (Motion.edges). Same for the toggle knob.
4. Drags are direct manipulation: while held, the value comes from the cursor position; on release
   it springs back from wherever it was (Motion.drag, Motion.rubber).
5. Analyze the song for the beat grid (tools/beat-grid.py), start on a downbeat, place every UI
   sound by its measured peak (--peak).
6. Render with motion blur: tools/motion-blur.sh (4 subframes → 60 fps).
7. Render one frame per beat first (tools/beat-frames.sh); fix anything off the grid, cramped or
   hard to read.
Never put will-change on anything the camera scales. Text that swaps inside a morphing container
needs its own enter and exit timing. Make the last frame identical to the first, cursor position
and speed included.
Ask me for the inputs, then show me the state list on the beat grid before you write any code.
```

## Applying the same method to ads (/ad-creative)
- The "one shape, never cut" idea works for twist ads too: the hero object (a chat bubble, a
  payslip, a phone) morphs from the setup state into the reveal state instead of cutting.
- Put the **reveal on a downbeat**, the misdirection beats on the beats before it.
- The pull-to-refresh / notification / cursor devices are direct-manipulation moments — build
  them with `Motion.drag` so they feel physical.
