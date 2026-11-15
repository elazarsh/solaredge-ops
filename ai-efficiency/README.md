# ai-efficiency

כלים דטרמיניסטיים (פייתון, בלי LLM, בלי רשת) להפחתת טוקנים, וסוכן שבועי שמפעיל אותם. ההנחיות לסוכן: `.claude/skills/ai-efficiency-governor/SKILL.md`. ממצאים: `FINDINGS.md`.

| כלי | מה עושה | נבדק |
|---|---|---|
| `tools/session_digest.py` | מנתח תמלילי סשנים (JSONL): טוקנים נמדדים, כלים, פקודות חוזרות, מה הוזרק להקשר | כן, על הסשן הנוכחי |
| `tools/skill_audit.py` | סריקה סטטית של ריפו סקילים לפני התקנה: רישיון, גודל, עלות הקשר, תבניות מסוכנות | כן, על CLI-Anything |
| `tools/img_prep.py` | הקטנת תמונות וגיליון מגע אחד, מזהה קריאה חוזרת | כן |
| `tools/patch_apply.py` | החלפות טקסט מדויקות מ-JSON, הרצה יבשה וחוזרת בבטחה | כן |
| `tools/preflight.py` | בדיקה מקדימה: שמות משתני סביבה, כלים, ריפו, רשת | כן |
| `tools/wait_render.py` | המתנה לרינדור בפקודה אחת | כן |
| `tools/events_digest.py` | ניתוח דפי `list_events` שנשמרו | כן |
| `tools/media_extract.py` | מדיה: מידע, פריימים, גיליון מגע אחד, תמלול מקומי (faster-whisper) | כן, על סרטון של 26 שניות |

דרישות: python3, ffmpeg, `numpy` ו-`faster-whisper` לתמלול (אופציונלי).

כללי עבודה שנלמדו: `PLAYBOOK.md`. ממצאים: `FINDINGS.md`.
