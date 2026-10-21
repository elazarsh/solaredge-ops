import os,sys,json,base64,urllib.request,re,concurrent.futures as cf
KEY=os.environ["GEMINI_API_KEY"]
def b64(p):return base64.b64encode(open(p,'rb').read()).decode()
def mime(p):return 'image/png' if p.endswith('.png') else 'image/jpeg'
def call_img(prompt,inputs):
    parts=[{"inlineData":{"mimeType":mime(p),"data":b64(p)}} for p in inputs]+[{"text":prompt}]
    body={"contents":[{"parts":parts}],"generationConfig":{"responseModalities":["IMAGE"],"imageConfig":{"aspectRatio":"16:9","imageSize":"2K"}}}
    req=urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/models/gemini-3-pro-image:generateContent",data=json.dumps(body).encode(),headers={"Content-Type":"application/json","x-goog-api-key":KEY})
    d=json.load(urllib.request.urlopen(req,timeout=400))
    for p in d["candidates"][0]["content"]["parts"]:
        if "inlineData" in p:return base64.b64decode(p["inlineData"]["data"])
def read_words(png):
    body={"contents":[{"parts":[{"inlineData":{"mimeType":"image/png","data":base64.b64encode(png).decode()}},{"text":"List ALL Hebrew words and any digits that are hand-lettered in this drawing, separated by commas. Write each word exactly as spelled (letter by letter), no niqqud, no explanation. If there is no text, write NONE."}]}],"generationConfig":{"temperature":0}}
    req=urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent",data=json.dumps(body).encode(),headers={"Content-Type":"application/json","x-goog-api-key":KEY})
    d=json.load(urllib.request.urlopen(req,timeout=120));t=d['candidates'][0]['content']['parts'][0]['text']
    return [w.strip() for w in re.split(r'[,\n]',re.sub(r'[^א-ת0-9, \n]','',t)) if w.strip()]
def make(name,prompt,inputs,must,forbid=(),tries=5):
    for i in range(tries):
        try:png=call_img(prompt,inputs)
        except Exception as e:print(name,i,'ERR',str(e)[:120],flush=True);continue
        got=read_words(png);j=' '.join(got);ok=all(m in j for m in must) and not any(f in j.split() for f in forbid)
        print(name,i,got,'OK' if ok else 'retry',flush=True)
        open(f'img/{name}_try{i}.png','wb').write(png)
        if ok:open(f'img/{name}.png','wb').write(png);return True
    return False
