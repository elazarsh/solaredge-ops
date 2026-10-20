import numpy as np, json, os, shutil
from PIL import Image
S='/tmp/claude-0/-home-user-solaredge-ops/b739defe-bfc9-5521-91fd-2d6f235476f6/scratchpad/'
env=np.array(json.load(open(S+'ind/env.json'))['amp'],float)   # 25fps
mouth=np.array(json.load(open(S+'pig/mouth.json')))
op=(mouth>800).astype(float)
bb=json.load(open(S+'pig/bbox.json'))
A,B=11,118   # talking segment (1-based frames @24fps)
L=B-A
scenes=[(3.0,10.8),(10.8,14.5),(14.5,17.9),(17.9,21.3)]
FPS=25
def src(t,p):   # t seconds local, p phase offset in source frames -> frame index (1-based)
    x=(t*24+p)%(2*L)
    if x>L: x=2*L-x
    return A+int(round(x))
plan=[]
for (s,e) in scenes:
    n=int(round((e-s)*FPS)); ev=np.array([env[min(len(env)-1,int(round(s*FPS))+i)] for i in range(n)])
    ev=(ev>0.25).astype(float)
    best=None
    for p in range(0,2*L):
        o=np.array([op[src(i/FPS,p)-1] for i in range(n)])
        c=np.corrcoef(o,ev)[0,1] if o.std()>0 and ev.std()>0 else -1
        if best is None or c>best[0]: best=(c,p)
    print(s,e,'corr %.2f phase %d'%best, 'open frac env %.2f anim %.2f'%(ev.mean(),np.mean([op[src(i/FPS,best[1])-1] for i in range(n)])))
    plan.append((s,e,best[1]))
# compose sequence: crop box, scale, place onto 1920x1080 transparent canvas
SC=0.64
X0=min(b[0] for b in bb[A-1:B]); X1=max(b[2] for b in bb[A-1:B]); Y0=min(b[1] for b in bb[A-1:B]); Y1=max(b[3] for b in bb[A-1:B])
print('bbox',X0,Y0,X1,Y1)
out=S+'pig/seqR'; shutil.rmtree(out,ignore_errors=True); os.makedirs(out)
# place: feet bottom at y=1048, left edge at x=30
w=int((X1-X0)*SC); h=int((Y1-Y0)*SC); left=1920-40-w; top=1048-h
print('size',w,h,'top',top)
k=0
for (s,e,p) in plan:
    n=int(round((e-s)*FPS))
    for i in range(n):
        f=src(i/FPS,p)
        im=Image.open(S+f'pig/rgba/r{f:03d}.png').crop((X0,Y0,X1,Y1)).resize((w,h),Image.LANCZOS)
        can=Image.new('RGBA',(1920,1080),(0,0,0,0)); can.paste(im,(left,top))
        can.save(out+f'/p{k:04d}.png'); k+=1
print('frames',k)
