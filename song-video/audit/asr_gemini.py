import os, sys, json, base64, subprocess, urllib.request, concurrent.futures as cf, re
key = os.environ['GEMINI_API_KEY']          # never printed
AUDIO = '/home/user/solaredge-ops/song-video/assets/song.mp3'
CUTS = [0, 59.9, 129.4, 180.0, 232.4]
PROMPT = ("זו הקלטה בעברית של שיר שמוקרא ומושר. תמלל אותה בדיוק כפי שנשמע, מילה במילה, בלי להשלים ממקורות ובלי לתקן דקדוק או לשון, "
          "גם אם נשמע לך שהמילה שגויה או שונה מהמקור המוכר. אל תנחש שורות מהתנ\"ך או מהתפילה. אם מילה לא ברורה כתוב [?]. "
          "החזר JSON בלבד: רשימה של אובייקטים {\"s\": שניות_התחלה_יחסית_לקטע, \"e\": שניות_סיום, \"plain\": \"התמלול בלי ניקוד\", "
          "\"vocalized\": \"אותו טקסט עם ניקוד כפי שהוגה בפועל בהקלטה (ניקוד לפי ההגייה ששמעת, גם אם היא חריגה)\"}. שורה אחת לכל שורת שירה או משפט.")
def cut(i):
    out = f'/tmp/claude-0/-home-user-solaredge-ops/8f5877e5-ee60-5335-a789-ff5f3c5c3688/scratchpad/audit/chunk{i}.mp3'
    subprocess.run(['ffmpeg','-v','error','-y','-ss',str(CUTS[i]),'-to',str(CUTS[i+1]),'-i',AUDIO,'-ac','1','-b:a','128k',out],check=True)
    return out
def call(model, path):
    b = base64.b64encode(open(path,'rb').read()).decode()
    body = {"contents":[{"parts":[{"inlineData":{"mimeType":"audio/mpeg","data":b}},{"text":PROMPT}]}],
            "generationConfig":{"temperature":0,"responseMimeType":"application/json"}}
    req = urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        data=json.dumps(body).encode(), headers={"Content-Type":"application/json","x-goog-api-key":key})
    for attempt in range(3):
        try:
            d = json.load(urllib.request.urlopen(req, timeout=300))
            return json.loads(d["candidates"][0]["content"]["parts"][0]["text"])
        except Exception as e:
            err = str(e)[:200]
    return {"error": err}
def job(args):
    model, i = args
    items = call(model, cut(i))
    return model, i, items
models = sys.argv[1:]
res = {m: {} for m in models}
with cf.ThreadPoolExecutor(4) as ex:
    for m, i, items in ex.map(job, [(m, i) for m in models for i in range(4)]):
        res[m][i] = items
        n = len(items) if isinstance(items, list) else items
        print(m, 'chunk', i, '->', n, flush=True)
json.dump({'cuts': CUTS, 'res': res}, open('/tmp/claude-0/-home-user-solaredge-ops/8f5877e5-ee60-5335-a789-ff5f3c5c3688/scratchpad/audit/gemini_raw.json','w'), ensure_ascii=False, indent=1)
