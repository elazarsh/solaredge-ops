import os,sys,json,base64,urllib.request,re
KEY=os.environ["GEMINI_API_KEY"]
paras=[l.strip() for l in open('../noach-narration-v6-nikud.md',encoding='utf-8').read().split('\n\n') if l.strip()][:3]
voice=sys.argv[1] if len(sys.argv)>1 else 'Sulafat'
STYLE=("Hebrew storyteller narration, intimate and poetic, like a quiet story told by candlelight. "
 "Warm, slightly low voice, slow and unhurried. Clear natural Israeli Hebrew pronunciation. "
 "Flowing continuous delivery with soft natural breaths: a short pause at commas and dashes, a longer pause between sentences. "
 "Do not rush, do not sound like a news reader. The very last words of each paragraph fade gently.")
out={}
for i,t in enumerate(paras,1):
    body={"model":"gemini-3.8-flash-tts","input":[{"type":"user_input","content":[{"type":"text","text":t,"annotations":[{"type":"speech_metadata","style":STYLE}]}]}],
          "response_format":{"type":"audio","mime_type":"audio/wav"},"generation_config":{"speech_config":[{"voice":voice}]},"store":False}
    req=urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/interactions",data=json.dumps(body).encode(),headers={"Content-Type":"application/json","x-goog-api-key":KEY})
    d=json.load(urllib.request.urlopen(req,timeout=180))
    if d.get('status')!='completed': print('FAIL',i,str(d)[:300]);sys.exit(1)
    a=[p for s in d['steps'] if s['type']=='model_output' for p in s['content'] if p['type']=='audio'][0]
    open(f'vo/p{i}_{voice}.wav','wb').write(base64.b64decode(a['data']));print('ok',i,len(a['data']))
