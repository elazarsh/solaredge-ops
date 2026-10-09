# Transitions

Principle: **velocity-matched**. Exit with an accelerating ease + blur ramp, enter with a decelerating ease + blur clearing; the fastest moments of both curves meet at the cut so the motion reads as continuous (match speeds within ~5 %). In montages the transition IS the exit - no extra exit animations between scenes; only the last scene fades out.

## Choosing
- **Hard cut:** rapid lists, percussive edits, 3+ quick tempo-matched switches, register shifts.
- **CSS/transform transitions:** connective beats that feel like one continuous camera move; editorial pacing.
- **Shader-grade (WebGL):** centerpieces, product/logo unveils, moments landing on a downbeat/SFX hit. Use 1-2 per 5-7 beat reel; more flattens impact.
- **Crossfade** = "this continues"; **slow dissolve** = "drift with me"; **hard cut** = disruption.

## Presets (CSS/GSAP)
| Name | Exit | Enter | Use |
|---|---|---|---|
| Whip pan | `x:-400..-W, blur 24, 0.3 s power3.in` | `x:+W..0, blur 24->0, 0.3-0.5 s power3.out` (starts ~0.28 of the way through the exit) | energetic cut between related beats; pair with whoosh panned toward the movement |
| Velocity-matched vertical | `y:-150, blur 30, 0.33 s power2.in` | `y:150 -> 0, blur 30 -> 0, 1.0 s power2.out` | upward reveal, lists |
| Zoom through | `scale 1 -> 1.2-1.9, blur 20, 0.2-0.35 s power3.in` | `scale .6-.75 -> 1, blur 20 -> 0, 0.5 s expo.out` | emphasis cut, into a hero |
| Rise push | out `y -0.6H, opacity 0, power3.in` | in `y +0.5H -> 0, power3.out` | section change in vertical formats |
| Blur through | out blur 20 (0.3 s) | in blur 20 -> 0 (0.25 s power3.out) | soft but quick |
| Flash/light leak | white/warm overlay peak .5-.8, 0.35-0.5 s | | on impacts and bar downbeats |
| Focus pull | defocus out / refocus in | | calm, premium |
| Circle/diamond iris, diagonal split | animate clip-path (outgoing on top, z-index 10) | | graphic, retro |
| Staggered blocks / blinds | full-screen blocks (not thin strips); blind count scales with energy: calm 4/6, medium 6-8/8, high 12-16/16 | | graphic cover transitions |
| Light leak / overexposure | overlay >= 2400 px so no shape shows; overexposure via `filter:brightness()` on the scene | | warm, filmic |
| Glitch/chromatic | RGB overlays normal-blend ~35 % (multiply is invisible on dark) | | tech register |
| Page burn / VHS / ripple | specialised; use sparingly | | stylised |

Timing presets: instant .15 s, snappy .2, smooth .4, dramatic .5, gentle .6, luxe .7.

## Shader transitions (WebGL, 14 common ones)
domain-warp .5-.8 s, ridged-burn .5-.8, whip-pan .3-.5, sdf-iris .5-.7, ripple-waves .6-1.0, gravitational-lens .6-1.0, cinematic-zoom .4-.6, chromatic-split .3-.5, swirl-vortex .5-.8, thermal-distortion .5-.8, flash-through-white .01-.3, cross-warp-morph .5-.8, light-leak .5-.8, glitch .3-.5. Match to style (see styles.md). Custom GLSL is fine when none fits. In HyperFrames: `npx hyperframes add <name>`.

## Don'ts
Star iris, tilt-shift (no selective CSS blur), fake lens flares that draw a visible shape, hinge/door transitions (distort too quickly). Never put filters/opacity<1 on a `preserve-3d` parent (flattens 3D). Never leave a scene on black unless intended; hold the final frame.

## Match cuts / handoffs
Hand off a shared element across the cut (same position/scale/colour) with numeric handoff values; whip-pan match cuts need the same rotation direction in both shots.
