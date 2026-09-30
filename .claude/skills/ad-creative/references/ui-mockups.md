# Recreating familiar app UIs in ads (WhatsApp, Instagram, notifications)

Familiar UI = instant context with zero explanation. Recreate the **look**, never the brand marks:
no WhatsApp/Instagram logo or name on screen, and no claim that the brand endorses the ad.

## WhatsApp — light mode (checked 2026)
| Element | Value |
|---|---|
| Chat wallpaper | #EFEAE2 + faint doodle pattern (subtle dots at 3–5% opacity work) |
| Incoming bubble | #FFFFFF, radius ~22px, tail corner square; **in Hebrew (RTL) incoming is on the RIGHT** |
| Outgoing bubble | #D9FDD3 (older: #DCF8C6), on the LEFT in RTL, blue ticks ✓✓ #53BDEB |
| Text / secondary | #111B21 / #667781 (timestamps, "הועבר פעמים רבות", member list) |
| Accent green | #00A884 (send/mic button), teal #008069 (older header / icons), brand #25D366 |
| Header | White (current Android/iOS), avatar circle, group name bold, "שירה, מיכל ועוד 353 חברות" |
| Group sender names | Distinct saturated colors per person (#C2185B, #1F7AEC, #7B3FE4 …) |
| Details that sell it | Date pill ("היום"), "⤻⤻ הועבר פעמים רבות" in italic gray, reaction chip under the bubble with a count, long-press menu (השב / סמן בכוכב / העבר / פרטי הודעה), bottom sheet for message info |

## Making a UI mock feel like TV, not a screenshot
- Put the phone on bold brand-color backgrounds that **cut on the beat**; add large kinetic headlines
  above the phone (outside the UI) that echo what happens inside it.
- Camera punch-ins (scale 1.04–1.08 → 1) and small rotations on beats; phone vibration on notifications.
- One physical interaction per bar: long-press ring, tap, pull-to-refresh drag.
- Counters that roll (reactions, forwards, ₪ amount) are cheap and energetic.
- End on the client's logo on its native background (white for most logos), iris-transition from an
  on-screen element (e.g. the refresh spinner) instead of a hard cut.
