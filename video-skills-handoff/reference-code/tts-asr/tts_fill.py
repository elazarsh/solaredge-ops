from tts_cal import *
import time,os,wave
for i in range(len(paras)):
    out=f'vo/p{i+1:02d}.wav'
    if os.path.exists(out):continue
    for t in range(12):
        try:tts(paras[i],STY['b'],out);print(i+1,'ok',flush=True);break
        except Exception as e:print(i+1,'err',str(e)[:60],flush=True);time.sleep(20*(t+1))
durs={}
for i in range(len(paras)):
    with wave.open(f'vo/p{i+1:02d}.wav') as w:durs[i+1]=round(w.getnframes()/w.getframerate(),2)
json.dump(durs,open('vo/durs.json','w'));print(durs)
