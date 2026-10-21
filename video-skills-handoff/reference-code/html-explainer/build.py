import json
c=json.load(open('v3/cues.json'))['cues'];D=json.load(open('v3/durations.json'))
cues=[c[f's{i:02d}'] for i in range(1,17)]
t=open('index3.html',encoding='utf-8').read().replace('__DUR__',json.dumps(D)).replace('__CUES__',json.dumps(cues,ensure_ascii=False))
open('page3.html','w',encoding='utf-8').write(t);print('built',len(t))
