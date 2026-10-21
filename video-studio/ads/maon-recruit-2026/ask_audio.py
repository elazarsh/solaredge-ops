import os,sys,json,base64,urllib.request
KEY=os.environ["GEMINI_API_KEY"]; f=sys.argv[1]; q=sys.argv[2]
mt="audio/mpeg" if f.endswith("mp3") else "audio/wav"
body={"contents":[{"parts":[{"inlineData":{"mimeType":mt,"data":base64.b64encode(open(f,"rb").read()).decode()}},{"text":q}]}]}
req=urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent",data=json.dumps(body).encode(),headers={"Content-Type":"application/json","x-goog-api-key":KEY})
d=json.load(urllib.request.urlopen(req,timeout=300)); print(d["candidates"][0]["content"]["parts"][0]["text"])
