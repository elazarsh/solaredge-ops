# Promo storyboard - "claude-kb" (30 s, 9:16, 1080x1920, 30 fps, Hebrew RTL)

Fixed style: navy background, orange accent (#ff8a1f), teal secondary (#2ee6c5), bold sans (DejaVu/Liberation), kinetic typography, no stock imagery. Only facts from this session: 27 skills, 5 hooks, 60+ pages researched, installer idempotent.

| # | Time | Narration-line (on-screen) | Visual action |
|---|---|---|---|
| 1 Hook | 0.0-3.6 | "עוד פרומפט. עוד תוצאה גנרית? מספיק." | lines rise in, "מספיק." pops in orange |
| 2 Proof | 3.6-8.6 | "סרקנו. למדנו. ארזנו." | three stat cards slide in, numbers count up: 60+ / 27 / 5 |
| 3 What | 8.6-14.6 | "27 סקילים. 6 תחומים." | 2x3 grid of domain cards pop in with skill names |
| 4 How | 14.6-20.6 | "כותבים רגיל. Claude כבר יודע." | prompt bubble types, router chip appears, "verified" checkmark row |
| 5 Tips | 20.6-26.2 | "4 דרכים להפיק מזה הכי הרבה" | four tips slide in one by one |
| 6 CTA | 26.2-30.0 | "claude-kb - התקנה אחת. כל הפרויקטים." | logo word-mark, `./install.sh` terminal line types, fade out |

Audio: generated synthetic track (pad + arpeggio + kick/hat), riser into the CTA, no voice-over (no Hebrew TTS available in the build environment).
Frame timing is deterministic: `render(t)` in promo.html is a pure function of time; `render.js` seeks to each frame and screenshots it.
