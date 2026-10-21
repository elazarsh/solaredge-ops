# Platform specs (checked 2026; re-verify if a platform changes its UI)

| Placement | Canvas | Length sweet spot | Notes |
|---|---|---|---|
| Instagram / Facebook Reels | 1080×1920 (9:16), 1440×2560 accepted | 15–30 s (max 90) | Heaviest bottom UI. Burn captions in — FB Reels ads get no auto-captions. |
| Stories | 1080×1920 | ≤15 s per card | Top 14% has the profile bar. |
| TikTok | 1080×1920 | 9–30 s | Right-side action rail; no loudness normalization in feed → deliver loud but clean. |
| WhatsApp status | 1080×1920 | ≤ 60 s (split longer) | Heavy compression → big, bold text; avoid thin fonts and fine gradients. |
| YouTube Shorts | 1080×1920 | ≤ 60 s | |
| Feed square | 1080×1080 | 15–30 s | Safe margin ~5% all around. |
| YouTube in-stream | 1920×1080 | 6 s bumper / 15–30 s | Brand + message before the 5 s skip. |

## 9:16 safe zone (1080×1920)
Keep text, faces, logos and CTA inside:
- **Top 14% (≈270 px)** clear — account name, "Sponsored".
- **Bottom 35% (≈670 px)** clear of anything critical — caption, CTA button, likes, audio.
  Burned-in captions may sit just above this line (y ≈ 1150–1250).
- **Sides 6% (≈65 px)** each; on TikTok also keep ≈140 px clear on the right for the icon rail.
→ Content box ≈ x 65–1015, y 270–1250. `video-studio/tools/safe-zone-check.sh` draws it.

## Audio delivery
- Integrated loudness **−14 LUFS** (safe everywhere; −12 is acceptable for TikTok), true peak **≤ −1 dBTP**.
- Music under VO about 18–24 dB lower than the voice; duck, don't just lower globally.
- Design for sound off anyway: ~85% of feed viewing starts muted.

## Encoding
H.264 High, yuv420p, 30 fps (or 25), AAC 48 kHz stereo 192 kbps, `+faststart`, file < 100 MB.
