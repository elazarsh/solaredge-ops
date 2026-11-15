# סקילים וכלים חיצוניים שנבדקו (ולמה לא הותקנו)

המטרה: לא להוסיף כלים מיותרים. כל פריט פה נבדק; מה שהיה שימושי **מוזג כהנחיות** לסקילים הקיימים במקום להתקין עוד כלי.

| מקור | החלטה | הסבר |
|---|---|---|
| `iart-ai/motion-design-skills` (MIT) | **מוזג** | עקרונות תנועה, שפת תנועה, חיתוכים למוזיקה וקומפוזיציה עברו ל-`references/motion-craft.md`. לא הותקן כחבילה. Remotion ו-After Effects לא רלוונטיים לנו. |
| `ToBeWin/HandDraw-Skill` (MIT) | **מוזג** | כללי העבודה עברו ל-`hand-drawn-video`. לא הותקן: דורש Node+Edge TTS, ועברית/קול לא נבדקו. |
| `alexgreensh/anidoodle` (Apache-2.0, 95MB, 32 סגנונות) | **לא הותקן** | מתחרה ב-`keyframe-images` ובמסלול האיור הקיים, גדול מאוד, ולא נמצאו ביקורות עצמאיות ברשת (חיפוש בנובמבר 2026: רק רישומי ספריות, ובדיקת האבטחה בספרייה עדיין "בתור"). אפשר לשקול שוב אם יתבקשו סגנונות איור בקוד בלי תמונות AI. |
| 15 סגנונות של Arcads (`arcads-cut`) | **לא הותקן** | הסקיל לא היה בידינו; נרשמו רק הפקודות ב-`talking-head-effects.md`. |
| `google/skills` (178 סקילים) | **נבחרו 4** | `gemini-api`, `gemini-live-api`, `gemini-interactions-api`, `finding-google-skills`. השאר היו מכבידים על כל סשן. |
| `Manim`, `Claude Drawing`, `Claude Animation Base`, `Huashu Art Motion`, `Motion (LunaAI519)`, `JavaScript Animation` | **לא נבדקו לעומק** | הופיעו במאמר "9 skills" בלבד. `Motion` צורך קרדיטים ב-Higgsfield; `Manim` ברישיון לא מסחרי (ManimGL). |

כלל: לפני התקנה של סקיל חיצוני, קוראים את הקוד ואת הרישיון, וסורקים תבניות מסוכנות (`curl | sh`, הרצת פקודות מ-README).
