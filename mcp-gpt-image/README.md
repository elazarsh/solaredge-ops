# mcp-gpt-image

שרת MCP שנותן ל-Claude את הכלים `generate_image` ו-`edit_image` ליצירה ועריכה של תמונות עם מודל התמונות של OpenAI (GPT image).

## Backends

| backend | דרישות | הערות |
|---|---|---|
| `api` | `OPENAI_API_KEY` | הדרך הרשמית והיציבה. חיוב לפי תמונה. |
| `codex` | Codex CLI עם `codex login` (חשבון ChatGPT) | **ניסיוני.** נשען על כלי יצירת התמונות של Codex, שאינו מתועד רשמית, ויכול להפסיק לעבוד. לא נבדק מול Codex אמיתי. |
| `auto` (ברירת מחדל) | | `api` אם יש מפתח, אחרת `codex`. |

`edit_image` נתמך רק ב-`api`.

## התקנה

```bash
pip install -r mcp-gpt-image/requirements.txt
claude mcp add gpt-image --scope user \
  -e OPENAI_API_KEY="$OPENAI_API_KEY" \
  -- python /abs/path/to/mcp-gpt-image/server.py
```

השרת נטען בתחילת סשן, לכן צריך לפתוח סשן חדש אחרי ההוספה.

**סשן בענן:** מוסיפים `OPENAI_API_KEY` כ-secret של הסביבה, ומוודאים שמדיניות הרשת מאפשרת `api.openai.com`. להפעלת השרת בכל סשן אפשר להוסיף `.mcp.json` בשורש הריפו עם אותה פקודה.

## משתני סביבה

`OPENAI_API_KEY`, `OPENAI_IMAGE_MODEL` (ברירת מחדל `gpt-image-1`, אפשר להחליף לדגם חדש יותר), `GPT_IMAGE_OUTPUT_DIR` (ברירת מחדל `generated-images/`), `GPT_IMAGE_TIMEOUT`, `OPENAI_BASE_URL`, `CODEX_BIN`.

## אבטחה

- אל תעשה commit למפתח API או ל-`~/.codex/auth.json`. הקובץ הזה שקול לסיסמה.
- בענן עדיף מפתח API עם מגבלת הוצאה על פני העתקת `auth.json`.
