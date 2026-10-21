import os,sys,json,base64,urllib.request
KEY=os.environ["GEMINI_API_KEY"]
prompt=("Sparse, intimate, slow cinematic score for an animated shadow-puppet fairy tale set in the ancient Near East. "
"Solo oud and soft duduk with a low bowed cello drone and distant bowed glass harmonics, minor mode (D minor), around 56 BPM, no drums, no percussion, no vocals. "
"Fragile, melancholic, reverent, very quiet and spacious with long silences between phrases, slowly darkening toward the end. Instrumental only, about 60 seconds.")
model=sys.argv[1] if len(sys.argv)>1 else "lyria-3-pro-preview"
body={"contents":[{"parts":[{"text":prompt}]}],"generationConfig":{"responseModalities":["AUDIO"]}}
req=urllib.request.Request(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",data=json.dumps(body).encode(),headers={"Content-Type":"application/json","x-goog-api-key":KEY})
try: d=json.load(urllib.request.urlopen(req,timeout=300))
except urllib.error.HTTPError as e: print(e.code,e.read().decode()[:400]);sys.exit(1)
n=0
for c in d.get('candidates',[]):
    for p in c['content']['parts']:
        if 'inlineData' in p:
            mt=p['inlineData']['mimeType'];ext='mp3' if 'mpeg' in mt else 'wav'
            open(f'mus/bgm_{model}.{ext}','wb').write(base64.b64decode(p['inlineData']['data']));print('saved',mt,ext);n+=1
        elif 'text' in p: print('text:',p['text'][:200])
print(n)
