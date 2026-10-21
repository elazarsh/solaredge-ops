import os,sys,json,base64,urllib.request,wave,concurrent.futures as cf
KEY=os.environ["GEMINI_API_KEY"]
paras=[l.strip() for l in open('narr_v7.md',encoding='utf-8').read().split('\n\n') if l.strip()]
STY={
'a':"Hebrew storyteller narration, warm and engaging, lively conversational pace, about 150 words per minute, flowing continuously with natural short breaths at commas and full stops, clear natural Israeli Hebrew pronunciation. Slightly softer and slower only on the very last words of each paragraph.",
'b':"Hebrew storyteller narration, warm and engaging, unhurried but flowing, about 135 words per minute, natural breaths at commas and full stops, clear natural Israeli Hebrew pronunciation. Slightly softer and slower on the very last words of each paragraph.",
}
def tts(text,style,out):
    body={"model":"gemini-3.8-flash-tts","input":[{"type":"user_input","content":[{"type":"text","text":text,"annotations":[{"type":"speech_metadata","style":style}]}]}],"response_format":{"type":"audio","mime_type":"audio/wav"},"generation_config":{"speech_config":[{"voice":"Sulafat"}]},"store":False}
    req=urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/interactions",data=json.dumps(body).encode(),headers={"Content-Type":"application/json","x-goog-api-key":KEY})
    d=json.load(urllib.request.urlopen(req,timeout=240))
    a=[p for s in d['steps'] if s['type']=='model_output' for p in s['content'] if p['type']=='audio'][0]
    open(out,'wb').write(base64.b64decode(a['data']))
    with wave.open(out) as w:return w.getnframes()/w.getframerate()
if __name__=='__main__':
    def r(k):return k,tts(paras[0],STY[k],f'vo/cal_{k}.wav')
    with cf.ThreadPoolExecutor(2) as ex:
        for x in ex.map(r,STY):print(x)
