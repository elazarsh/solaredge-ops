---
name: hand-drawn-video
description: >
  אפקט "צויר ביד" בסרטון: קווים וצורות שמצטיירים בהדרגה (draw-on), סקיצה, חץ או הקפה שנמשכים, מראה איור ידני.
  להפעיל ב"ציור ביד", "קו שמצטייר", "אפקט סקיצה", "הקפה/חץ מצויר", "hand drawn", "draw-on", "stroke draw".
  Hand-drawn look: SVG stroke draw-on animation inside a HyperFrames/HTML composition.
---

# Hand Drawn: קו שמצטייר

אין כאן מנוע חדש. זו אנימציית SVG של קו בתוך קומפוזיציית HyperFrames/GSAP. מקור הטכניקה: `.claude/skills/hyperframes-keyframes/SKILL.md` (stroke draw). קרא אותו וקרא את `hyperframes-core` לפני כתיבת HTML.

## מתכון
1. צור צורה כ-`<path>` (המר צורות פשוטות ל-path). רק `stroke`, בלי `fill` בזמן הציור.
2. עדיפות ראשונה: `DrawSVGPlugin` של GSAP. אם אינו זמין: `stroke-dasharray` ו-`stroke-dashoffset` שווים לאורך הקו (`path.getTotalLength()`), והנפש את ה-offset ל-0.
3. קו מורכב: פצל לכמה paths פשוטים והצג ברצף (`trace`, כמה משיכות), לא path אחד ארוך.
4. אחרי הציור אפשר לחשוף `fill` בפייד קצר.
5. ה-timeline בודד ו"מושהה", בטוח לחיפוש (seek-safe), בלי `Math.random` ובלי `setTimeout`. כך הרינדור דטרמיניסטי.

## מראה "ידני"
- קצה עגול: `stroke-linecap: round`, `stroke-linejoin: round`.
- קו לא מושלם: path בעל עיקום קל, לא קו ישר. עובי משתנה קל בין משיכות.
- Ease איטי-מהיר-איטי (`power2.inOut`), משך 0.4–1.2 שניות למשיכה.
- סנכרן את תחילת הציור למילה בהקראה (cues מתמלול), כמו ב-`html-to-video`.

## בדיקה
- `npx hyperframes check` (lint), ואז צילום פריימים באמצע הציור ובסופו. ודא שהקו מלא ושאין חפיפה עם טקסט.

## אל תעשה
- לא לצייר טקסט עברי כקו (אותיות מתעוותות). טקסט נשאר טקסט, והקו רק מקיף או מדגיש אותו.
- לא להבטיח מראה איור "אמיתי" מתמונה. איור ידני מתמונה הוא `keyframe-images`.
