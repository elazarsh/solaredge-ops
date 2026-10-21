import os,sys,json,hashlib,concurrent.futures as cf
import numpy as np,cv2
from boxes import boxes
def key(img,label):return hashlib.md5((img+'|'+label).encode()).hexdigest()[:12]
def mask_from_box(img,box,shape='mask'):
    src=cv2.cvtColor(cv2.imread(f'img/{img}.png'),cv2.COLOR_BGR2RGB);H,W=src.shape[:2]
    y0,x0,y1,x1=[v/1000 for v in box];X0,Y0,X1,Y1=int(x0*W),int(y0*H),int(x1*W),int(y1*H)
    m=np.zeros((H,W),np.float32)
    if shape=='ellipse':
        cv2.ellipse(m,((X0+X1)//2,(Y0+Y1)//2),((X1-X0)//2,(Y1-Y0)//2),0,0,360,1.0,-1,cv2.LINE_AA);return m
    if shape=='rect':
        r=int(min(X1-X0,Y1-Y0)*0.06);cv2.rectangle(m,(X0+r,Y0),(X1-r,Y1),1.0,-1);cv2.rectangle(m,(X0,Y0+r),(X1,Y1-r),1.0,-1)
        for cx,cy in((X0+r,Y0+r),(X1-r,Y0+r),(X0+r,Y1-r),(X1-r,Y1-r)):cv2.circle(m,(cx,cy),r,1.0,-1)
        return cv2.GaussianBlur(m,(0,0),3)
    s=0.5;ss=cv2.resize(src,(int(W*s),int(H*s)),interpolation=cv2.INTER_AREA);h,w=ss.shape[:2]
    mg=int(0.025*w);rx0=max(1,int(x0*w)-mg);ry0=max(1,int(y0*h)-mg);rx1=min(w-2,int(x1*w)+mg);ry1=min(h-2,int(y1*h)+mg)
    gm=np.zeros((h,w),np.uint8);bg=np.zeros((1,65),np.float64);fg=np.zeros((1,65),np.float64)
    try:
        cv2.grabCut(ss,gm,(rx0,ry0,rx1-rx0,ry1-ry0),bg,fg,5,cv2.GC_INIT_WITH_RECT);f=((gm==1)|(gm==3)).astype(np.uint8)
    except Exception:f=np.zeros((h,w),np.uint8)
    f[:ry0]=0;f[ry1:]=0;f[:,:rx0]=0;f[:,rx1:]=0
    f=cv2.morphologyEx(f,cv2.MORPH_CLOSE,np.ones((9,9),np.uint8));n,lab,st,_=cv2.connectedComponentsWithStats(f)
    if n>1:
        keep=np.zeros_like(f)
        for i in range(1,n):
            if st[i,cv2.CC_STAT_AREA]>0.01*f.size*0.02+200:keep[lab==i]=1
        f=keep
    area=f.sum();box_area=max(1,(rx1-rx0)*(ry1-ry0))
    if area<0.06*box_area or area>0.985*box_area:
        f=np.zeros((h,w),np.uint8);cv2.ellipse(f,((rx0+rx1)//2,(ry0+ry1)//2),((rx1-rx0)//2,(ry1-ry0)//2),0,0,360,1,-1)
    m=cv2.resize(f.astype(np.float32),(W,H),interpolation=cv2.INTER_LINEAR);return cv2.GaussianBlur(m,(0,0),2.5)
def get(img,label,shape='mask'):
    k=key(img,label+shape);p=f'objcache/{k}.npz'
    if os.path.exists(p):
        d=np.load(p);return d['mask'],tuple(d['box'])
    return None
def prepare(items):
    """items: list of (img,label,shape). Detect boxes per image (batched) then build masks."""
    byimg={}
    for img,label,shape in items:byimg.setdefault(img,[]).append((label,shape))
    def work(img):
        labs=[l for l,_ in byimg[img]];res=boxes(f'img/{img}.png',labs)
        out=[]
        for (label,shape),r in zip(byimg[img],res or []):
            box=r['box_2d'];k=key(img,label+shape)
            m=mask_from_box(img,box,shape);np.savez_compressed(f'objcache/{k}.npz',mask=m.astype(np.float16),box=np.array(box,np.float32))
            out.append((img,label))
        return out
    with cf.ThreadPoolExecutor(3) as ex:
        for r in ex.map(work,list(byimg)):print('objs',r,flush=True)
