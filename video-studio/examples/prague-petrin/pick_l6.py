import sys, time, re, subprocess, json
sys.path.insert(0,".")
import voice_tools as v, make_voice as mv
from pathlib import Path
ST=mv.STYLE.replace("tiny pauses only","tiny pauses only, EXCEPT one dramatic comic pause of about one second right before the very last word")+" The last word is delivered flat, deadpan and grave, with falling intonation (a statement, not a question), clearly pronounced. Say exactly and only:"
VARIANTS=["בְּקֶצֶת","בִּקְצָת","בקצת"]
def stt3(p):
    outs=[]
    for _ in range(3):
        for a in range(3):
            try: outs.append(v.transcribe(p)); break
            except Exception: time.sleep(15)
        time.sleep(2)
    return outs
res=[]
for rnd in range(2):
    for vi,last in enumerate(VARIANTS):
        text=f"רכבל פֶּטְרְז'ִין. יוֹתֵר אֶקְסְטְרִים מִמַּעֲלִית. ... {last}."
        n=f"{rnd}{vi}"; raw=Path(f"voice/L6c_raw.wav"); out=Path(f"voice/L6c_{n}.wav")
        for a in range(4):
            try: v.tts(text,raw,"Algenib",ST); mv.trim(raw,out); break
            except Exception as e: time.sleep(25)
        else: continue
        sec=v.duration(out)
        o=subprocess.run(["ffmpeg","-hide_banner","-i",str(out),"-af","silencedetect=n=-38dB:d=0.35","-f","null","-"],capture_output=True,text=True).stderr
        ss=[float(x) for x in re.findall(r"silence_start: ([\d.]+)",o)]; se=[float(x) for x in re.findall(r"silence_end: ([\d.]+)",o)]
        pause=max([b-a for a,b in zip(ss,se)],default=0); pend=se[-1] if se else None
        heard=stt3(out)
        good=sum(1 for h in heard if mv.norm(h).replace(" ","").endswith("בקצת") and "יותראקסטריםממעלית" in mv.norm(h).replace(" ",""))
        print(f"take {n} [{last}] {sec:.2f}s pause={pause:.2f} ends@{pend} good={good}/3 | {heard}",flush=True)
        res.append({"take":n,"variant":last,"sec":sec,"pause":pause,"pause_end":pend,"good":good})
        if good==3 and 0.5<=pause<=1.1 and sec<=5.4: break
    else: continue
    break
json.dump(res,open("voice/l6_candidates.json","w"),ensure_ascii=False,indent=1)
