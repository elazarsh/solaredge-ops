import os,sys,json,base64,urllib.request,urllib.error,time
KEY=os.environ["GEMINI_API_KEY"]
BASE="Sparse, intimate cinematic score for a hand-drawn charcoal animated film about a man who survived a flood and the trauma that follows. Instrumental only, no vocals, no drums, spacious, quiet, about 60 seconds. "
M={
'm2':"Uneasy and wry: low cello pulses, plucked oud, a dry clarinet, slightly unsettled, minor mode, 60 BPM, the feeling of being mocked.",
'm3':"First a bright warm morning (soft piano and gentle strings, hopeful) that after 20 seconds suddenly collapses into a dark rumbling low drone with sub bass swell, then a shattering silence, then hollow breathing pads.",
'm4':"Deep desolation: bowed low strings, distant hollow glass harmonics, slow heartbeat-like soft low pulse, cold and empty, long silences, 50 BPM.",
'm5':"Fragile hope returning: a single gentle piano and soft strings in a major-leaning mode with one fragile warm melody, tender, like a rainbow, 66 BPM.",
'm6':"Hollow quiet and anxiety: sparse piano notes, a ticking soft clock-like texture, low drones, a trembling muted violin, tense but quiet, 58 BPM.",
'm7':"Tender compassion: warm cello and soft piano, slow, forgiving, a small human melody covering someone gently, 60 BPM.",
'm8':"Contemporary reflective: soft piano, subtle electronic pad, quiet urban air, slightly ironic and tender, 64 BPM, gradually opening to warm strings.",
'm9':"Gentle resolution and farewell: warm strings and piano resolving slowly, one last unresolved note held at the end, fading to quiet, 60 BPM.",
}
for k,v in M.items():
    out=f'mus/{k}.mp3'
    if os.path.exists(out):continue
    for t in range(8):
        body={"contents":[{"parts":[{"text":BASE+v}]}],"generationConfig":{"responseModalities":["AUDIO"]}}
        req=urllib.request.Request("https://generativelanguage.googleapis.com/v1beta/models/lyria-3-pro-preview:generateContent",data=json.dumps(body).encode(),headers={"Content-Type":"application/json","x-goog-api-key":KEY})
        try:
            d=json.load(urllib.request.urlopen(req,timeout=300))
            for c in d.get('candidates',[]):
                for p in c['content']['parts']:
                    if 'inlineData' in p:open(out,'wb').write(base64.b64decode(p['inlineData']['data']));print(k,'ok',flush=True)
            if os.path.exists(out):break
        except urllib.error.HTTPError as e:print(k,e.code,e.read().decode()[:100],flush=True);time.sleep(30*(t+1))
        except Exception as e:print(k,'exc',str(e)[:80],flush=True);time.sleep(20)
