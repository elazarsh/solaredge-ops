# Style archetypes (adapted for Hebrew + 9:16 / 16:9)

Name a style after a designer/movement, define tokens, write what to do and avoid. Tokens: bg, fg, accent(s), type pair, radius, motion energy/easing, texture, transition. (Archetypes adapted from the HyperFrames visual-styles idea; fonts swapped for Hebrew-capable bundled families.)

| Style | Mood / use | Palette | Type (Hebrew-capable) | Motion | Texture | Transition |
|---|---|---|---|---|---|---|
| **Swiss Pulse** (Muller-Brockmann) | clinical, precise; SaaS, data, dev tools | near-black #14161c, off-white, one blue #2a6bff | Heebo 900 headlines + Heebo 400 labels, JetBrains Mono data | high energy, `expo.out`, hard cuts, counters | grid lines, registration marks | cinematic zoom / iris |
| **Velvet Standard** (Vignelli) | premium, timeless; luxury, enterprise, keynote | #0a0a0f, warm white, deep indigo #2a2f8f | Frank Ruhl Libre (serif) + Assistant 300 | slow glides, long holds, 0 % overshoot | fine grain, hairline rules | cross-warp morph / slow dissolve |
| **Deconstructed** (Brody) | raw, industrial; security, tech launch | charcoal, off-white, burnt orange #d4501e | Rubik 900 + JetBrains Mono caps | back-out entries, stepped exits, scramble/snap | scan lines, glitch, grain | glitch / whip |
| **Maximalist Type** (Scher) | loud, kinetic; big announcements | black, white, red #e63946, yellow #ffd60a | Karantina / Rubik 900 huge uppercase-feel, Heebo subheads | fast entries, hard stops, 2-3 s scenes, type fills 50-80 % | layered type, colour blocks | ridged burn / hard cut |
| **Data Drift** (Anadol) | futuristic, immersive; AI/ML | near-black, light grey, violet #7c3aed, cyan #06b6d4 | Assistant 300 thin, floating | smooth sine, continuous flow, extreme scale shifts | particle fields, light traces, radial glow | gravitational lens / domain warp |
| **Soft Signal** (Sagmeister) | intimate, warm; wellness, personal | cream #fff8ec, dark grey, amber #f5a623, rose, sage | Frank Ruhl Libre italic-feel + Assistant 300 | calm drifts, never snaps | soft gradients, warm grain | thermal distortion / dissolve |
| **Folk Frequency** (Terrazas) | cultural, vivid; consumer apps, food, community | white, dark text, pink #ff1493, blue #0047ab, yellow, green | Secular One / Rubik 800 rounded feel | bouncy back-out, spins, pops (playful overshoot OK) | pattern tiles, confetti, colour blocks | swirl / ripple |
| **Shadow Cut** (Hillmann) | dark, cinematic; reveals, security, exposes | deep black, cold grey #3a3a3a, off-white, blood red #c1121f | Karantina / Rubik 900 condensed feel + Heebo | slow creeping push-ins, dramatic scale reveals, a pause before impact | deep shadow, vignette, grain | domain warp / dip to black |
| **Aurora Glass** (used in claude-kb promo) | modern product/tool launch | ink #070a1a, accent orange #ff7a1a, teal #2ee6c5, violet #7c5cff | Rubik 900 + Heebo/Assistant + JetBrains Mono | beat-locked slams, 3D tilt cards, orbit, DoF | aurora blobs, dust, grain, vignette, glass cards | whip, zoom-through, rise push |

## Hebrew type pairing rules
- One expressive display + one quiet text face per scene; contrast on several axes (serif + sans, condensed + wide, geometric + humanist).
- Weight contrast must be extreme in video (~300 vs 900, not 400 vs 700).
- Bundled-safe Hebrew families (via @fontsource, offline): Heebo (400/700/900), Rubik (400/500/800/900), Secular One (400), Frank Ruhl Libre (serif, 400/900), Assistant (300-800), Karantina (condensed display 300-700), Alef/David Libre/Suez One available too. Latin companions: Space Grotesk, JetBrains Mono.
- Display tracking -0.03em to -0.05em (encoding eats letter detail); on dark add +0.01em at display sizes; dark-background body weight ~350 instead of 400; line-height +0.05-0.1 on dark.
- Sizes (1080-wide frame): in-feed headlines 90 px+ (Hebrew hero 100-250 px), body 32 px+, data labels 24 px+. Anything under 24 px needs justification. Content on screen 3 s must be readable in 2.
- `font-variant-numeric: tabular-nums` for stacked/animated numbers; LTR islands for latin/numbers (`direction:ltr`).

## Mood -> style
Data/analytical: Swiss Pulse. Premium: Velvet Standard. Raw/punk: Deconstructed. Hype: Maximalist Type. AI/futuristic: Data Drift. Human/warm: Soft Signal. Festive/consumer: Folk Frequency. Dark/dramatic: Shadow Cut. Product/tool launch: Aurora Glass.

## Palette recipe
Pick a hue; derive background (very dark/light, hue-tinted), foreground (near-white/near-black tinted), accent at full saturation, optional second accent. Same background across scenes; one accent hue carries emphasis (verbs/numbers). Check contrast >= WCAG AA (4.5:1) for text with decoratives removed. Palette families: Bold/Energetic, Warm/Editorial, Dark/Premium, Clean/Corporate, Nature/Earth, Neon/Electric, Pastel/Soft, Jewel/Rich, Monochrome.
