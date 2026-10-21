import os,json,base64,urllib.request,time,wave,re,concurrent.futures as cf
KEY=os.environ["GEMINI_API_KEY"]
N=json.load(open('v3/narr.json',encoding='utf-8'))
STYLE="Hebrew storyteller narration, warm and engaging, unhurried but flowing, about 140 words per minute, natural breaths at commas and full stops, clear natural Israeli Hebrew pronunciation."
def tts(k):
    out=f'v3/vo/{k}.wav'
    if os.path.exists(out):
        with wave.open(out) as w:return k,round(w.getnframes()/w.getframerate(),2)
    body={"model":"gemini-3.8-flash-tts","input":[{"type":"user_input","content":[{"type":"text","text":N[k],"annotations":[{"type":"speech_metadata","style":STYLE}]}]}],"response_format":{"type":"audio","mime_type":"audio/wav"},"generation_config":{"speech_config":[{"voice":"Sulafat"}]},"store":False}
    for t in range(10):
        try:
            req=urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/interactions",data=json.dumps(body).encode(),headers={"Content-Type":"application/json","x-goog-api-key":KEY})
            d=json.load(urllib.request.urlopen(req,timeout=240))
            a=[p for s in d['steps'] if s['type']=='model_output' for p in s['content'] if p['type']=='audio'][0]
            open(out,'wb').write(base64.b64decode(a['data']))
            with wave.open(out) as w:return k,round(w.getnframes()/w.getframerate(),2)
        except Exception as e:print(k,'err',str(e)[:60],flush=True);time.sleep(15*(t+1))
with cf.ThreadPoolExecutor(3) as ex:
    res=dict(ex.map(tts,list(N)))
words={k:len(re.sub(r'[֑-ׇ]','',v).split()) for k,v in N.items()}
tot=sum(words.values());print('words',tot,'dur',sum(res.values()),'wpm',round(tot/sum(res.values())*60))
for k in N:print(k,words[k],res[k],round(words[k]/res[k]*60))
json.dump(res,open('v3/vo/durs.json','w'))
