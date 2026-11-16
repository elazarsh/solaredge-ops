#!/usr/bin/env python3
"""בדיקת מפתחות ורשת לשירותי ההפקה, בלי לעלות כסף ובלי להדפיס מפתחות.

בודק: האם GEMINI_API_KEY / OPENAI_API_KEY מוגדרים (רק "יש/אין" + אורך), ובקשת רשימת מודלים (חינמית) לכל שירות.
  python3 check_env.py            # הכול
  python3 check_env.py --models   # גם מדפיס מודלי וידאו/תמונה/קול/מוזיקה שזמינים בחשבון
קוד יציאה 0 = הכול תקין, 1 = משהו חסר.
"""
import json, os, sys, urllib.error, urllib.request

def get(url, headers):
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30)
        return r.status, json.load(r)
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()[:150]
    except Exception as e:
        return None, f"{type(e).__name__}: {str(e)[:120]}"

def main():
    show = "--models" in sys.argv
    ok = True
    k = os.environ.get("GEMINI_API_KEY")
    print("GEMINI_API_KEY:", f"מוגדר (אורך {len(k)})" if k else "חסר")
    if k:
        st, d = get("https://generativelanguage.googleapis.com/v1beta/models?pageSize=200", {"x-goog-api-key": k})
        if st == 200:
            names = [m["name"].split("/")[-1] for m in d.get("models", [])]
            print(f"  רשת + מפתח תקינים ({len(names)} מודלים)")
            if show:
                for kw in ("tts", "image", "veo", "lyria", "flash"):
                    print(f"  {kw}:", ", ".join(n for n in names if kw in n) or "-")
        else:
            ok = False; print("  נכשל:", st, d, "(403 מהפרוקסי = הדומיין לא מאושר בהגדרות הרשת של הסביבה)")
    else:
        ok = False
    k = os.environ.get("OPENAI_API_KEY")
    print("OPENAI_API_KEY:", f"מוגדר (אורך {len(k)})" if k else "חסר (אופציונלי: רק לתמונות OpenAI)")
    if k:
        st, d = get("https://api.openai.com/v1/models", {"Authorization": "Bearer " + k})
        if st == 200:
            names = sorted(m["id"] for m in d.get("data", []))
            print(f"  רשת + מפתח תקינים ({len(names)} מודלים)")
            if show:
                print("  תמונה:", ", ".join(n for n in names if "image" in n))
        else:
            print("  נכשל:", st, d)
    for tool in ("ffmpeg", "node", "python3"):
        from shutil import which
        print(f"{tool}:", which(tool) or "חסר")
    sys.exit(0 if ok else 1)

main()
