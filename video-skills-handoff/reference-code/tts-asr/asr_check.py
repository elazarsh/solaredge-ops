import sys,json,re,difflib,time
sys.path.insert(0,'../ch1v2')
from asr import asr
paras=[l.strip() for l in open('narr_v7.md',encoding='utf-8').read().split('\n\n') if l.strip()]
def norm(t):
    t=re.sub(r'[֑-ׇ]','',t);t=re.sub(r'[^א-ת ]',' ',t.replace('־',' ').replace('—',' '));return t.split()
res={}
for i,p in enumerate(paras,1):
    for t in range(5):
        try:w=asr(f'vo/p{i:02d}.wav');break
        except Exception as e:time.sleep(15*(t+1));w=None
    if not w:print(i,'asr fail');continue
    got=[x['w'] for x in w];exp=norm(p)
    gj=norm(' '.join(got))
    r=difflib.SequenceMatcher(None,exp,gj).ratio()
    res[i]=dict(ratio=round(r,3),words=w)
    miss=[x for x in exp if x not in gj]
    print(i,round(r,3),'missing:',miss[:10],flush=True)
json.dump(res,open('vo/asr.json','w'),ensure_ascii=False)
