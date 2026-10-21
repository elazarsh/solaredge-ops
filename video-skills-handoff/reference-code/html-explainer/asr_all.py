import sys,json,time,concurrent.futures as cf
sys.path.insert(0,'../ch1v2')
from asr import asr
N=json.load(open('v3/narr.json'))
def f(k):
    for t in range(6):
        try:return k,asr(f'v3/vo/{k}.wav')
        except Exception as e:time.sleep(8*(t+1))
    return k,[]
with cf.ThreadPoolExecutor(4) as ex:out=dict(ex.map(f,list(N)))
json.dump(out,open('v3/words.json','w'),ensure_ascii=False)
import re
st=lambda s:re.sub(r'[֑-ׇ]','',s)
for k in N:
    ref=re.sub(r'[^\w\s]','',st(N[k])).split();hyp=[re.sub(r'[^\w]','',x['w']) for x in out[k]]
    import difflib
    sm=difflib.SequenceMatcher(None,ref,hyp)
    d=[(' '.join(ref[a:b]),' '.join(hyp[c:d_])) for tag,a,b,c,d_ in sm.get_opcodes() if tag!='equal']
    print(k,len(ref),len(hyp),d)
