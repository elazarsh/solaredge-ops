# usage: img.py out.jpg "prompt" [ref1.jpg ref2.jpg ...]  (9:16, 2K)
import os,sys,json,base64,urllib.request
KEY=os.environ["GEMINI_API_KEY"]; out,prompt,refs=sys.argv[1],sys.argv[2],sys.argv[3:]
parts=[{"inlineData":{"mimeType":"image/jpeg" if r.endswith("jpg") else "image/png","data":base64.b64encode(open(r,"rb").read()).decode()}} for r in refs]+[{"text":prompt}]
body={"contents":[{"parts":parts}],"generationConfig":{"responseModalities":["IMAGE"],"imageConfig":{"aspectRatio":"9:16","imageSize":"2K"}}}
req=urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image:generateContent",data=json.dumps(body).encode(),headers={"Content-Type":"application/json","x-goog-api-key":KEY})
d=json.load(urllib.request.urlopen(req,timeout=400))
for p in d["candidates"][0]["content"]["parts"]:
    if "inlineData" in p: open(out,"wb").write(base64.b64decode(p["inlineData"]["data"])); print(out); break
else: print("no image", str(d)[:300])
