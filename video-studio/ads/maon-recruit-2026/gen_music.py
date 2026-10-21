import os,json,base64,urllib.request,sys
KEY=os.environ["GEMINI_API_KEY"]; model=sys.argv[1]; out=sys.argv[2]
prompt=("Instrumental background music for a 37 second warm, witty Instagram ad, 96 BPM, no vocals. "
"Structure: 0:00-0:18 sparse and slightly weary: muted fingerpicked acoustic guitar, soft brushed snare, a lonely low piano note, a bit sleepy, like a long evening. "
"At 0:18 a clear warm lift, like opening a window in the afternoon: bright ukulele strums, handclaps, upright bass groove, glockenspiel sparkles, happy and light, gentle not loud. "
"Keep the energy warm and steady until 0:33, then resolve with a soft final chord and a short glockenspiel shimmer, ending cleanly at about 0:37.")
body={"contents":[{"parts":[{"text":prompt}]}]}
req=urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",data=json.dumps(body).encode(),headers={"Content-Type":"application/json","x-goog-api-key":KEY})
d=json.load(urllib.request.urlopen(req,timeout=600))
for p in d["candidates"][0]["content"]["parts"]:
    if "inlineData" in p:
        mt=p["inlineData"]["mimeType"]; ext="mp3" if "mp" in mt else "wav"
        open(out+"."+ext,"wb").write(base64.b64decode(p["inlineData"]["data"])); print(out+"."+ext,mt)
    elif "text" in p: print("text:",p["text"][:300])
