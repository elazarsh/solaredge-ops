# Creative review (run on the contact sheet + QA report)

Score each 1–5; anything < 4 gets a fix before delivery.

**Hook (0–3 s)**
- First frame already has motion and a readable message (not a logo, not black).
- Hook text ≤ 6 words, readable at phone size in 0.5 s.

**Twist**
- The offer is *not* stated in the first 3 s; the reveal is one clear visual moment.
- After the reveal, the message + brand are unmistakable; the twist dramatizes a real product truth.
- Pace, text size and VO speed match the age band (`audiences.md`).

**Pacing (user feedback, ep. 1 v2 → v3)**
- Every punchline / reveal is **held ≥ 2–3 s** after it lands (≈ 5–6 beats at 120 BPM). Energy comes from
  motion *within* a held moment (punch-ins, pulses, slow push), not from cutting away early.
- Reading time: on-screen text needs ≈ 0.3 s per word + 0.5 s; a list of facts gets ≥ 1 s (2 beats) per item.
- The twist and the payoff are the two slowest moments of the ad; the setup can be fast.

**Voice-over**
- VO lines never overlap. Leave **1–2 s of silence between VO segments** (compute: next start ≥ previous
  start + measured duration + 1.0). Don't change the VO level to "fix" overlap — fix the timing.

**Clarity on mute**
- Every beat understandable from on-screen text alone.
- Captions match VO exactly, 1–2 lines, never split a phrase in a way that breaks RTL reading.

**Design**
- All key text inside the safe box (x 65–1015, y 270–1250 on 1080×1920).
- Contrast: text on photos has a scrim/shadow/plate. Max 2 font families, 3–4 colors.
- Hebrew renders correctly: no reversed punctuation, no broken niqqud, numbers/English in correct order.

**Story**
- One message. Body pays off the hook. Specific facts > adjectives.
- Emotional beat present (a face, a moment, a place).

**CTA**
- Single action, on screen ≥ 3 s, phone/WhatsApp large, brand name visible.
- Legal note if required (gender note for job ads).

**Tech** (from `ad-qa.sh`)
- Correct resolution/aspect, 25–30 fps, duration in target range.
- −14 LUFS ±1, true peak ≤ −1 dBTP, audio track present, no long black/silent gaps.

Output a short table: item · score · fix. Then fix and re-render.
