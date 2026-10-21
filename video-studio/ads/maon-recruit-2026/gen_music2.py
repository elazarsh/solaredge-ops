import os,json,base64,urllib.request,sys,time
KEY=os.environ["GEMINI_API_KEY"]
P={"A":"Instrumental, no vocals, 96 BPM, key of D major, 22 seconds long. A slightly weary, late-evening mood but still gentle and warm, not sad: solo muted fingerpicked acoustic guitar with soft brushed snare and a quiet ticking clock-like shaker. Steady consistent groove from start to end, no breaks, no build-ups, no drones.",
   "B":"Instrumental, no vocals, 96 BPM, key of D major, 20 seconds long. Bright, happy, warm afternoon mood, light and smiling: strummed ukulele, fingerpicked acoustic guitar, handclaps on 2 and 4, upright bass groove and small glockenspiel sparkles. Starts immediately at full groove on the first beat, steady and cheerful, then ends cleanly on a soft final D major chord with a glockenspiel shimmer at about 19 seconds."}
def gen(k,out):
    body={"contents":[{"parts":[{"text":P[k]}]}]}
    req=urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/models/lyria-3-pro-preview:generateContent",data=json.dumps(body).encode(),headers={"Content-Type":"application/json","x-goog-api-key":KEY})
    d=json.load(urllib.request.urlopen(req,timeout=600))
    if "candidates" not in d: print(k,"fail",str(d)[:200]); return
    for p in d["candidates"][0]["content"]["parts"]:
        if "inlineData" in p: open(out,"wb").write(base64.b64decode(p["inlineData"]["data"])); print(out)
for k,i in [("A",1),("B",1),("A",2),("B",2)]:
    try: gen(k,f"assets/music/{k}{i}.mp3")
    except Exception as e: print(k,i,e)
