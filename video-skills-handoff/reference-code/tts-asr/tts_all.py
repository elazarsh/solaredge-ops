from tts_cal import *
import time
def r(i):
    out=f'vo/p{i+1:02d}.wav'
    for t in range(4):
        try:return i+1,tts(paras[i],STY['b'],out)
        except Exception as e:print(i+1,'err',str(e)[:80],flush=True);time.sleep(5)
    return i+1,None
with cf.ThreadPoolExecutor(4) as ex:
    res=list(ex.map(r,range(len(paras))))
print(res);json.dump(dict(res),open('vo/durs.json','w'))
