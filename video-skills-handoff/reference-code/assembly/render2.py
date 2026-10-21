import os,subprocess,sys,json
from timeline import build
from plan import P
segs,paras,T=build()
HOLD=7.5
IDS=['K6']+[p[0] for p in P]
N="scale=1920:1080:flags=lanczos,fps=24,format=yuv420p"
DARK=json.load(open('plates/dark.json'))
SPECIAL={'A1_lite':('K1','K2'),'B':('K2','K3'),'C':('K3','K4'),'D':('K4','K5'),'E4_lite':('K5','K6')}
def sh(c):
    r=subprocess.run(c,shell=True,capture_output=True,text=True)
    if r.returncode:print(r.stderr[-800:]);raise SystemExit(1)
def kidx(k):
    return IDS.index(k) if k in IDS else int(k[1:])-1
def cam(kind,s0,n,ease_s,ease_e):
    """zoompan expressions for n frames; continuous path f(s), s = s0 + on/24 seconds.
    ease_s/ease_e: ease to the neutral (full-frame, centered) state at start/end so it matches the clean source frame."""
    s=f"({s0}+on/24)"
    es=f"min(1,on/{24*1.2})" if ease_s else "1"
    ee=f"min(1,({n}-on)/{24*1.2})" if ease_e else "1"
    w=f"(({es})*({ee}))"
    w=f"({w}*{w}*(3-2*{w}))"
    if kind==0:zr=f"(1.03+0.012*{s})";px="0.5";py="0.5"
    elif kind==1:zr="1.14";px=f"(0.1+0.08*({s}+1))";py="0.4"
    elif kind==2:zr=f"(1.15-0.012*{s})";px="0.5";py="0.5"
    else:zr="1.14";px=f"(0.9-0.08*({s}+1))";py="0.6"
    z=f"1+({zr}-1)*{w}"
    x=f"(iw-iw/zoom)*(0.5+({px}-0.5)*{w})"
    y=f"(ih-ih/zoom)*(0.5+({py}-0.5)*{w})"
    return z,x,y
def zp(img,kind,s0,n,ease_s,ease_e):
    z,x,y=cam(kind,s0,n,ease_s,ease_e)
    return f"scale=2400:1350,zoompan=z='{z}':x='{x}':y='{y}':d={n}:s=1920x1080:fps=24,trim=end_frame={n},setpts=PTS-STARTPTS"
def fallback(a,b,out,idx,ease_a,ease_b):
    mode=[0,1,0,0,1][idx%5]          # 0 smoke, 1 dissolve
    pl=[1,2,1,2][idx%4];flip=['','hflip,','vflip,','hflip,vflip,'][(idx//2)%4];tm=float(DARK[str(pl)]);st=max(0,tm-1.6)
    ka=kidx(a)%4;kb=kidx(b)%4
    ia,ib=f'img/{a}.png',f'img/{b}.png'
    if mode==0:
        na=nb=96
        fa=zp(ia,ka,4,na,ease_a,False);fb_=zp(ib,kb,0,nb,False,ease_b)
        fc=(f'[0:v]{fa},format=gbrp[a];[1:v]{fb_},format=gbrp[b];[a][b]concat=n=2:v=1:a=0[ab];'
            f'[2:v]{flip}trim=start={st}:duration=3.2,setpts=PTS-STARTPTS,scale=1920:1080,fps=24,fade=t=in:st=0:d=1.0:color=white,fade=t=out:st=2.2:d=1.0:color=white,format=gbrp[ps];'
            f'color=c=white:s=1920x1080:r=24:d=2.4,format=gbrp[w1];color=c=white:s=1920x1080:r=24:d=2.4,format=gbrp[w2];[w1][ps][w2]concat=n=3:v=1:a=0[p];'
            f'[ab][p]blend=all_mode=multiply:shortest=1,format=yuv420p[v]')
    else:
        na=nb=113  # 4.7 s each, 1.4 s cross-dissolve
        fa=zp(ia,ka,4,na,ease_a,False);fb_=zp(ib,kb,-0.7,nb,False,ease_b)
        fc=f'[0:v]{fa},format=yuv420p[a];[1:v]{fb_},format=yuv420p[b];[a][b]xfade=transition=fade:duration=1.4:offset=3.3,format=yuv420p[v]'
    sh(f'ffmpeg -v error -y -loop 1 -i {ia} -loop 1 -i {ib} -i plates/smk{pl}.mp4 -filter_complex "{fc}" -map "[v]" -t 8 -c:v libx264 -crf 18 {out}')
    return out
def real_seg(s,out):
    f=s['file'];ss,to=s['ss'],s['to'];d=(to-ss)/s['speed']
    flip='hflip,' if s['flip'] else ''
    a=b=None
    if s['key'] in SPECIAL:a,b=SPECIAL[s['key']]
    elif '_' in s['key'] and s['key'][0]=='K':a,b=s['key'].split('_')
    full=(ss==0 and to==8)
    if a and full and os.path.exists(f'img/{a}.png') and os.path.exists(f'img/{b}.png'):
        fd=0.5
        fc=(f'[0:v]{flip}setpts=(PTS-STARTPTS)/{s["speed"]:.4f},{N}[v];'
            f'[1:v]scale=1920:1080,format=rgba,fade=t=out:st=0:d={fd}:alpha=1[ia];'
            f'[2:v]scale=1920:1080,format=rgba,fade=t=in:st={d-fd:.3f}:d={fd}:alpha=1[ib];'
            f'[v][ia]overlay=format=auto[x1];[x1][ib]overlay=format=auto,format=yuv420p[o]')
        sh(f'ffmpeg -v error -y -ss {ss} -t {to-ss} -i {f} -loop 1 -framerate 24 -t {d:.3f} -i img/{a}.png -loop 1 -framerate 24 -t {d:.3f} -i img/{b}.png -filter_complex "{fc}" -map "[o]" -t {d:.3f} -an -c:v libx264 -crf 17 -preset fast -r 24 {out}')
    else:
        sh(f'ffmpeg -v error -y -ss {ss} -t {to-ss} -i {f} -vf "{flip}setpts=(PTS-STARTPTS)/{s["speed"]:.4f},{N}" -an -c:v libx264 -crf 17 -preset fast -r 24 {out}')
import trans,concurrent.futures as cf
from tplan2 import PLAN
fb=[];names=[];jobs=[]
real=[os.path.exists(s['file']) for s in segs]
for i,s in enumerate(segs):
    isr=real[i];ea=bool(i>0 and real[i-1]);eb=bool(i<len(segs)-1 and real[i+1])
    if isr:
        s['trans']='real';out=f"tmp/{s['key']}_r2_{s['speed']:.3f}.mp4"
        names.append(os.path.basename(out))
        if not os.path.exists(out):real_seg(s,out)
    else:
        a,b=s['key'].split('_');kind,params=PLAN.get(s['key'],('dissolve',{}));s['trans']=kind;fb.append(s['key'])
        vt=f"v{int(os.path.exists(f'veo/shot_{a}.mp4'))}{int(os.path.exists(f'veo/shot_{b}.mp4'))}"
        tmp=f"tmp/x_{a}_{b}_{kind}_{int(ea)}{int(eb)}_{vt}.mp4"
        out=f"tmp/{s['key']}_t{kind}_{int(ea)}{int(eb)}_{vt}_{s['speed']:.3f}.mp4";names.append(os.path.basename(out))
        if not os.path.exists(out):jobs.append((a,b,kind,params,i,ea,eb,tmp,out,s['speed']))
def do_job(j):
    a,b,kind,params,i,ea,eb,tmp,out,sp=j
    if not os.path.exists(tmp):
        pp={k:(tuple(v) if isinstance(v,list) else v) for k,v in params.items()}
        trans.render_clip(a,b,kind,pp,i,ea,eb,tmp)
    sh(f'ffmpeg -v error -y -i {tmp} -vf "setpts=(PTS-STARTPTS)/{sp:.4f},{N}" -an -c:v libx264 -crf 17 -preset fast -r 24 {out}')
    return out
if jobs:
    with cf.ProcessPoolExecutor(3) as ex:
        for r in ex.map(do_job,jobs):print('done',r,flush=True)
print('fallbacks',len(fb))
open('tmp/list.txt','w').write(''.join(f"file '{n}'\n" for n in names))
lastkey=segs[-1]['key'].split('_')[1]
sh(f'ffmpeg -v error -y -i img/{lastkey}.png -vf "scale=2112:1188,zoompan=z=\'1+0.0008*on\':x=\'iw/2-(iw/zoom/2)\':y=\'ih/2-(ih/zoom/2)\':d={int(HOLD*24)}:s=1920x1080:fps=24,format=yuv420p" -frames:v {int(HOLD*24)} -c:v libx264 -crf 17 tmp/hold.mp4')
open('tmp/list.txt','a').write("file 'hold.mp4'\n")
sh('ffmpeg -v error -y -f concat -safe 0 -i tmp/list.txt -c copy tmp/body.mp4')
tot=T+HOLD
sh(f'ffmpeg -v error -y -i tmp/body.mp4 -i out/caption.png -filter_complex "[1:v]format=rgba,fade=t=in:st={T+1.2}:d=1.2:alpha=1,fade=t=out:st={tot-1.8}:d=1.0:alpha=1[c];[0:v][c]overlay=0:0:enable=\'gte(t,{T})\',fade=t=in:st=0:d=0.8,fade=t=out:st={tot-1.0}:d=1.0,noise=alls=3:allf=t[v]" -map "[v]" -c:v libx264 -crf 21 -preset fast -r 24 tmp/video_final.mp4')
print('video ok',tot)
json.dump(dict(total=tot,paras=paras,segs=segs,fallbacks=fb),open('tmp/timeline.json','w'))
