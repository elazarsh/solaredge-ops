#!/usr/bin/env python3
"""ספריית מעברים משמעותיים בין שתי תמונות (25 סוגים), מרונדרת ל-mp4 באורך 8 ש' (192 פריימים, 24fps, 1920x1080).

שימוש:  python3 trans.py A.png B.png KIND [--params '{"focus":[0.5,0.5]}'] [--out out.mp4] [--idx 0]
         [--ease-a] [--ease-b] [--vid-a clipA.mp4] [--vid-b clipB.mp4] [--obj-dir objcache] [--frames 192]
KIND אחד מ: dissolve defocus washout dipblack goldbloom colordrain colorseep erase water tear iris zoomthrough whip smash ripple ink peel wipe smoke burn fill matte portal shatter match
מעברי אובייקט (fill matte portal shatter match) צריכים מסכות: קודם  python3 objects.py prepare plan.json  (ראה objects.py),
ואז params עם objA/objB (תווית האובייקט) ו-shape (mask|ellipse|rect). fobj/fobjB = נקודת מיקוד מאובייקט.
המעבר נמצא באמצע הקליפ (שניות 4.0 +- D/2); לפניו תנועת מצלמה על A, אחריו על B. ease = האטה לקצה כדי להתחבר לקליפ סמוך.
vid-a/vid-b: קליפ Veo של התמונה (אם יש) ישמש כמקור הפריימים במקום התמונה הנייחת.
smoke מחושב פרוצדורלית (אין תלות בקבצי plate חיצוניים).
תלויות: numpy, opencv-python(-headless), ffmpeg.
"""
import os,sys,json,subprocess,math,argparse
import numpy as np,cv2
W,H=1920,1080;FPS=24;NF=192
XX,YY=np.meshgrid(np.linspace(0,1,W,dtype=np.float32),np.linspace(0,1,H,dtype=np.float32))
def smooth(x):
    x=np.clip(x,0,1);return x*x*(3-2*x)
def gray(a):return (a[...,0]*0.299+a[...,1]*0.587+a[...,2]*0.114)
def lerp(a,b,m):
    if np.ndim(m)==2:m=m[...,None]
    return a*(1-m)+b*m
def fbm(seed,sx=1.0,sy=1.0,octs=5):
    r=np.random.default_rng(seed);out=np.zeros((H,W),np.float32);amp=1;tot=0
    for o in range(octs):
        w=max(2,int(6*(2**o)*sx));h=max(2,int(4*(2**o)*sy))
        n=r.random((h,w)).astype(np.float32)
        out+=amp*cv2.resize(n,(W,H),interpolation=cv2.INTER_CUBIC);tot+=amp;amp*=0.5
    out/=tot;out=(out-out.min())/(out.max()-out.min()+1e-6);return out
_IMG={}
def load(k):
    if k not in _IMG:
        im=cv2.imread(k,cv2.IMREAD_COLOR)
        if im is None:raise SystemExit(f'cannot read image {k}')
        im=cv2.resize(im,(W,H),interpolation=cv2.INTER_AREA) if im.shape[1]!=W else im
        _IMG[k]=cv2.cvtColor(im,cv2.COLOR_BGR2RGB)
    return _IMG[k]
def camstate(kind,s,w):
    if kind==0:z=1.03+0.012*s;px=0.5;py=0.5
    elif kind==1:z=1.14;px=0.1+0.08*(s+1);py=0.4
    elif kind==2:z=1.15-0.012*s;px=0.5;py=0.5
    else:z=1.14;px=0.9-0.08*(s+1);py=0.6
    z=1+(z-1)*w;px=0.5+(px-0.5)*w;py=0.5+(py-0.5)*w
    return z,px,py
def render_cam(img,kind,s,w):
    z,px,py=camstate(kind,s,w);h0,w0=img.shape[:2]
    cw=w0/z;ch=h0/z;x0=(w0-cw)*px;y0=(h0-ch)*py
    sx=W/cw;sy=H/ch
    M=np.array([[sx,0,-x0*sx],[0,sy,-y0*sy]],np.float32)
    return cv2.warpAffine(img,M,(W,H),flags=cv2.INTER_AREA if z<1.01 else cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE).astype(np.float32)/255.0
def zoom_about(f,z,fx,fy):
    if z<=1.0001:return f
    cw=W/z;ch=H/z;x0=min(max(fx*W-cw/2,0),W-cw);y0=min(max(fy*H-ch/2,0),H-ch)
    sx=W/cw;sy=H/ch;M=np.array([[sx,0,-x0*sx],[0,sy,-y0*sy]],np.float32)
    return cv2.warpAffine(f,M,(W,H),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
def blur_big(f,sigma):
    s=cv2.resize(f,(480,270),interpolation=cv2.INTER_AREA);s=cv2.GaussianBlur(s,(0,0),max(0.1,sigma));return cv2.resize(s,(W,H),interpolation=cv2.INTER_LINEAR)
PAPER=np.array([0.95,0.91,0.82],np.float32)
# ---------------- transitions: T(fa,fb,p,c) -> frame
def t_dissolve(fa,fb,p,c):return lerp(fa,fb,smooth(p))
def t_defocus(fa,fb,p,c):
    m=lerp(fa,fb,smooth(p));k=math.sin(math.pi*min(1,max(0,p)));return lerp(m,blur_big(m,1+9*k),min(1,k*1.3))
def t_washout(fa,fb,p,c):
    col=c.get('col',np.array([1.0,0.97,0.9],np.float32))
    if p<0.5:return lerp(fa,col,smooth(p*2)*0.98)
    return lerp(col,fb,smooth(p*2-1))
def t_dipblack(fa,fb,p,c):
    col=np.array([0.02,0.02,0.03],np.float32)
    if p<0.4:return lerp(fa,col,smooth(p/0.4))
    if p<0.6:return np.broadcast_to(col,fa.shape).copy()
    return lerp(col,fb,smooth((p-0.6)/0.4))
def t_goldbloom(fa,fb,p,c):
    m=lerp(fa,fb,smooth(p));fx,fy=c['focus'];d=np.hypot((XX-fx)*W/H,YY-fy)
    g=np.clip(1.1-d*1.1,0,1)**1.5*math.sin(math.pi*p)*0.75
    gold=np.array([1.0,0.76,0.34],np.float32);return 1-(1-m)*(1-g[...,None]*gold)
def t_colordrain(fa,fb,p,c):
    ad=lerp(fa,gray(fa)[...,None].repeat(3,2)*np.array([1.0,0.98,0.94],np.float32),smooth(p/0.6));return lerp(ad,fb,smooth((p-0.4)/0.6))
def t_colorseep(fa,fb,p,c):
    bg=lerp(gray(fb)[...,None].repeat(3,2)*np.array([1.0,0.98,0.94],np.float32),fb,smooth((p-0.3)/0.7));return lerp(fa,bg,smooth(p/0.7))
def t_erase(fa,fb,p,c):
    d=c.get('dir','r2l');n=c['n1'];stripe=c['n2']
    u={'r2l':1-XX,'l2r':XX,'diag':(XX*0.75+YY*0.35)/1.1,'u2d':YY}[d]
    u2=u+0.10*(n-0.5)+0.05*(stripe-0.5)
    t=-0.2+p*1.45;e=(t-u2);m=smooth(e/0.07)
    ghost=0.17*(1-smooth((p-0.8)/0.2))
    bg=fb*((1-ghost)+ghost*gray(fa)[...,None])
    out=lerp(fa,bg,m)
    band=np.exp(-((e-0.0)/0.045)**2)*(0.5+0.5*stripe)
    out=out*(1-0.32*band[...,None])+0.04*band[...,None]*0.7
    return out
def t_water(fa,fb,p,c):
    up=c.get('dir','up')=='up';ps=smooth(p)
    wv=0.018*np.sin(XX*14+p*20)+0.01*np.sin(XX*33-p*27)+0.006*np.sin(XX*71+p*40)
    if up:
        line=1.04-1.1*ps+wv;below=(YY>line).astype(np.float32);edge=(YY-line)
        tint=np.array([0.80,0.92,1.04],np.float32)
        wat=fb*tint;m=smooth(edge/0.004)
        out=lerp(fa*np.array([0.96,0.97,1.0],np.float32),wat,m)
    else:
        line=-0.04+1.1*ps+wv;edge=(line-YY)
        tint=np.array([0.82,0.92,1.04],np.float32)
        m=smooth(edge/0.004);out=lerp(fa*tint,fb,m)
    foam=np.exp(-((edge)/0.012)**2)*0.5
    out=out+foam[...,None]*np.array([0.5,0.55,0.55],np.float32)
    caus=(0.5+0.5*np.sin(XX*60+YY*40+p*30))*(0.5+0.5*np.sin(XX*43-YY*55-p*22))
    reg=(edge>0)
    out=out+(reg*(caus*0.05))[...,None]*0.6
    return np.clip(out,0,1)
def t_tear(fa,fb,p,c):
    n=c['n1'];g=int(smooth(p)*0.62*W)
    xe=(0.5+0.07*(c['n2']-0.5)*2+0.05*(n-0.5))
    xe=np.mean(xe,axis=1)  # per-row
    xe=cv2.GaussianBlur(xe.reshape(-1,1).astype(np.float32),(0,0),3)[:,0]
    xi=(xe*W).astype(np.int32)[:,None]
    X=np.arange(W,dtype=np.int32)[None,:]
    left=X<(xi-g);right=X>(xi+g)
    shL=np.roll(fa,-g,axis=1);shR=np.roll(fa,g,axis=1)
    shade=np.clip(1-np.abs((X-xi)/max(g,1))*0.0,0,1)
    gap_sh=np.clip((np.minimum(np.abs(X-(xi-g)),np.abs(X-(xi+g)))/90.0),0,1)
    out=fb*(0.62+0.38*gap_sh[...,None])
    out=np.where(left[...,None],shL,out);out=np.where(right[...,None],shR,out)
    fr=(np.abs(X-(xi-g))<7)&(X>=(xi-g)-7)&(~left)|(np.abs(X-(xi+g))<7)&(~right)
    edge=(((X>=xi-g-9)&(X<xi-g+0))|((X<=xi+g+9)&(X>xi+g-0)))
    out=np.where(edge[...,None]&(g>3),PAPER*0.96,out)
    return out
def t_iris(fa,fb,p,c):
    fx,fy=c['focus'];d=np.hypot((XX-fx)*W/H,YY-fy);r=smooth(p)*1.9;e=r-d
    m=smooth(e/0.02);out=lerp(fa*(1-0.25*smooth(p)),fb,m)
    ring=np.exp(-(e/0.012)**2)*0.6;out=out*(1-ring[...,None])
    return out
def t_zoomthrough(fa,fb,p,c):
    fx,fy=c['focus'];s=smooth(p)
    a=zoom_about(fa,1+3.2*s**1.6,fx,fy);b=zoom_about(fb,1+1.1*(1-s)**1.6,fx,fy)
    return lerp(a,b,smooth((p-0.3)/0.45))
def t_whip(fa,fb,p,c):
    d=c.get('dir','l');ps=smooth(p);vel=abs(math.sin(math.pi*p))
    if d in('l','r'):
        cat=np.concatenate([fa,fb],1) if d=='l' else np.concatenate([fb,fa],1)
        off=int(ps*W) if d=='l' else int((1-ps)*W)
        k=int(6+70*vel);acc=np.zeros_like(fa);n=7
        for j in range(n):
            o=int(off+(j-(n-1)/2)*k/(n-1)*2);o=min(max(o,0),W);acc+=cat[:,o:o+W]
        return acc/n
    cat=np.concatenate([fb,fa],0);off=int((1-ps)*H);k=int(4+50*vel);acc=np.zeros_like(fa);n=7
    for j in range(n):
        o=int(off+(j-(n-1)/2)*k/(n-1)*2);o=min(max(o,0),H);acc+=cat[o:o+H]
    return acc/n
def shake(f,amp,seed):
    r=np.random.default_rng(seed);dx,dy=(r.random(2)-0.5)*2*amp
    M=np.array([[1,0,dx],[0,1,dy]],np.float32);return cv2.warpAffine(f,M,(W,H),borderMode=cv2.BORDER_REFLECT)
def t_smash(fa,fb,p,c):
    if p<0.3:return shake(fa,10*p/0.3,int(p*1000))
    if p<0.38:return np.ones_like(fa)*np.array([1.0,0.98,0.94],np.float32)
    q=(p-0.38)/0.62;return shake(fb,34*(1-q)**2.2,int(p*1000))
def t_ripple(fa,fb,p,c):
    fx,fy=c['focus'];m=lerp(fa,fb,smooth(p));k=math.sin(math.pi*p)
    dx=(XX-fx)*W/H;dy=(YY-fy);r=np.hypot(dx,dy)+1e-4
    wave=np.sin(2*np.pi*(r*9-p*3.5))*np.exp(-r*1.8)*0.022*k
    mapx=((XX+wave*dx/r*H/W)*W).astype(np.float32);mapy=((YY+wave*dy/r)*H).astype(np.float32)
    return cv2.remap(m,mapx,mapy,cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
def t_ink(fa,fb,p,c):
    fx,fy=c['focus'];n=c['n1'];d=np.hypot((XX-fx)*W/H,YY-fy)/1.1
    ink=np.array([0.03,0.03,0.035],np.float32)
    if p<0.6:
        e=p*2.1-d+0.35*(n-0.5);m=smooth(e/0.07);return lerp(fa,ink,m)
    base=np.broadcast_to(ink,fa.shape);return lerp(base,fb,smooth((p-0.6)/0.4))
def t_peel(fa,fb,p,c):
    ps=smooth(p);d=(XX+YY)/2;df=1.02-ps*1.1;cw=0.045
    out=fb.copy();sh=np.clip((d-df)/0.08,0,1);under=np.clip(1-(d-df)/0.07,0,1)
    out=np.where((d>df)[...,None],fb,fa)
    # shade A near fold
    k=np.clip((df-d)/0.12,0,1);out=np.where((d<=df)[...,None],out*(0.78+0.22*k[...,None]),out)
    # curl back of page
    strip=(d>df-cw)&(d<=df);t=(d-(df-cw))/cw
    back=PAPER*(0.88+0.12*t[...,None])
    out=np.where(strip[...,None],back,out)
    # shadow onto B beyond fold
    sd=np.clip(1-(d-df)/0.05,0,1)*0.35*((d>df))
    out=out*(1-sd[...,None])
    return out
def t_wipe(fa,fb,p,c):
    xe=1.08-smooth(p)*1.2+0.03*(c['n1']-0.5)*np.sin(YY*9);e=(xe-XX)
    m=smooth(-e/0.03)  # right of line -> A ; left -> B
    out=lerp(fb,fa,m) if False else lerp(fa,fb,smooth(-(XX-xe)/0.03))
    line=np.exp(-((XX-xe)/0.006)**2)*0.8;out=out*(1-line[...,None])
    return out
def t_smoke(fa,fb,p,c):
    # עשן פרוצדורלי (אין plate חיצוני): רעש נע ימינה, צפיפות עולה לשיא באמצע ויורדת; A מתחלף ל-B בהמסה בתוך העשן
    n2=np.roll(c['n1'],int(p*W*0.35),axis=1)
    cover=math.sin(math.pi*min(1,max(0,p)))**0.8*1.35
    dens=smooth((cover-0.9*n2-0.3)/0.3)*0.95
    base=lerp(fa,fb,smooth((p-0.38)/0.24))
    smoke=np.array([0.20,0.19,0.18],np.float32)
    return lerp(base,np.broadcast_to(smoke,base.shape),dens)
def t_burn(fa,fb,p,c):
    n=c['n1'];tt=-0.1+p*1.35;e=tt-n
    m=smooth(e/0.02);band=np.exp(-((e-0.045)/0.05)**2)
    ahead=np.clip(1-(-e)/0.18,0,1)*(e<0)
    base=lerp(fa*(1-0.55*ahead[...,None]*np.array([0.1,0.6,0.9],np.float32)),fb,m)
    ember=np.array([1.0,0.45,0.1],np.float32);hot=np.array([1.0,0.85,0.45],np.float32)
    core=np.exp(-((e-0.012)/0.014)**2);out=base*(1-0.75*band[...,None])+band[...,None]*0.0
    out=out+core[...,None]*ember*0.85+np.exp(-((e-0.0)/0.006)**2)[...,None]*hot*0.5
    return np.clip(out,0,1)

def render_cam_gray(m,kind,s,w):
    z,px,py=camstate(kind,s,w);h0,w0=m.shape[:2]
    cw=w0/z;ch=h0/z;x0=(w0-cw)*px;y0=(h0-ch)*py;sx=W/cw;sy=H/ch
    M=np.array([[sx,0,-x0*sx],[0,sy,-y0*sy]],np.float32)
    return cv2.warpAffine(m,M,(W,H),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=0)
def csz(m):
    ys,xs=np.nonzero(m[::4,::4]>0.5)
    if len(xs)<8:return W/2,H/2,W*0.2,H*0.2
    return xs.mean()*4,ys.mean()*4,(xs.max()-xs.min()+1)*4.0,(ys.max()-ys.min()+1)*4.0
INK=np.array([0.03,0.03,0.035],np.float32)
def aff(s,cx,cy,tx,ty):
    return np.array([[s,0,tx-s*cx],[0,s,ty-s*cy]],np.float32)
def t_fill(fa,fb,p,c):
    ma=c['mA']();cx,cy,ow,oh=csz(ma);S=min(14.0,max(W/max(ow,40),H/max(oh,40))*1.5)
    if p<0.5:
        q=smooth(p/0.5);s=1+(S-1)*q**1.5;M=aff(s,cx,cy,W/2*q+cx*(1-q),H/2*q+cy*(1-q))
        sm=cv2.warpAffine(ma,M,(W,H),flags=cv2.INTER_LINEAR);spr=cv2.warpAffine(fa,M,(W,H),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
        base=lerp(c['cA'](),np.broadcast_to(INK,fa.shape),smooth((p-0.25)/0.25))
        return lerp(base,lerp(spr,np.broadcast_to(INK,fa.shape),min(1,q*1.6)),sm)
    q=smooth((p-0.5)/0.5);base=lerp(np.broadcast_to(INK,fb.shape),fb,smooth((q-0.15)/0.85))
    if 'mB' in c:
        mb=c['mB']();cxb,cyb,owb,ohb=csz(mb);Sb=min(14.0,max(W/max(owb,40),H/max(ohb,40))*1.5)
        s=1+(Sb-1)*(1-q)**1.5;M=aff(s,cxb,cyb,W/2*(1-q)+cxb*q,H/2*(1-q)+cyb*q)
        sm=cv2.warpAffine(mb,M,(W,H),flags=cv2.INTER_LINEAR);spr=cv2.warpAffine(fb,M,(W,H),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
        return lerp(base,lerp(np.broadcast_to(INK,fb.shape),spr,smooth(q*1.2)),sm)
    return base
def t_matte(fa,fb,p,c):
    ma=c['mA']();cx,cy,ow,oh=csz(ma);S=min(16.0,max(W/max(ow,40),H/max(oh,40))*1.8)
    q=smooth(p);s=1+(S-1)*q**1.6;M=aff(s,cx,cy,cx+(W/2-cx)*q,cy+(H/2-cy)*q)
    sm=cv2.warpAffine(ma,M,(W,H),flags=cv2.INTER_LINEAR);sm=np.maximum(sm,smooth((p-0.86)/0.14))
    inner=zoom_about(fb,1.3-0.3*q,0.5,0.5);outer=c['cA']()*(1-0.3*q)
    out=lerp(outer,inner,sm);line=np.exp(-((sm-0.5)/0.1)**2)*0.55
    return out*(1-line[...,None])
def t_portal(fa,fb,p,c):
    ma=c['mA']();cx,cy,ow,oh=csz(ma);Z=min(14.0,max(W/max(ow,40),H/max(oh,40))*1.15)
    q=smooth(p);z=1+(Z-1)*q**1.5;ccx=cx+(W/2-cx)*q;ccy=cy+(H/2-cy)*q
    MA=aff(z,cx,cy,ccx,ccy);av=cv2.warpAffine(fa,MA,(W,H),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
    mv=cv2.warpAffine(ma,MA,(W,H),flags=cv2.INTER_LINEAR)
    sb=z*max(ow/W,oh/H);MB=aff(sb,W/2,H/2,ccx,ccy);bv=cv2.warpAffine(fb,MB,(W,H),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
    mv=np.maximum(mv,smooth((p-0.9)/0.1));av=av*(1-0.25*q)
    return lerp(av,bv,mv)
def t_shatter(fa,fb,p,c):
    if 'chunks' not in c:
        ma=c['mA']();m0=ma>0.5;ys,xs=np.nonzero(m0[::2,::2]);
        if len(xs)<20:xs=np.array([W//4,3*W//4])//2;ys=np.array([H//4,3*H//4])//2
        x0,x1,y0,y1=xs.min()*2,xs.max()*2,ys.min()*2,ys.max()*2;r=np.random.default_rng(c['seed']);N=34
        seeds=np.stack([r.uniform(x0,x1,N),r.uniform(y0,y1,N)],1)
        gx,gy=np.meshgrid(np.arange(x0,x1+1),np.arange(y0,y1+1));d=(gx[...,None]-seeds[:,0])**2+(gy[...,None]-seeds[:,1])**2;lab=d.argmin(-1)
        chunks=[]
        for i in range(N):
            reg=(lab==i)&m0[y0:y1+1,x0:x1+1]
            if reg.sum()<80:continue
            yy,xx=np.nonzero(reg);px0,px1,py0,py1=xx.min(),xx.max()+1,yy.min(),yy.max()+1
            patch=np.zeros((py1-py0,px1-px0,4),np.float32);sub=fa[y0+py0:y0+py1,x0+px0:x0+px1]
            patch[...,:3]=sub;patch[...,3]=cv2.GaussianBlur(reg[py0:py1,px0:px1].astype(np.float32),(0,0),1.2)
            cx=x0+px0+(px1-px0)/2;cy=y0+py0+(py1-py0)/2
            chunks.append(dict(patch=patch,cx=cx,cy=cy,delay=0.04+0.40*(1-(cy-y0)/max(1,y1-y0))+r.uniform(0,0.1),vx=(cx-(x0+x1)/2)/max(1,x1-x0)*520+r.uniform(-90,90),vy=-r.uniform(40,260),om=r.uniform(-3.2,3.2)))
        c['chunks']=chunks
    base=lerp(c['cA'](),fb,smooth((p-0.12)/0.7));out=base.copy();D=c['D']
    for ch in c['chunks']:
        tau=max(0.0,(p-ch['delay'])*D)
        x=ch['cx']+ch['vx']*tau;y=ch['cy']+ch['vy']*tau+0.5*2400*tau*tau;ang=ch['om']*tau
        al=1-smooth((tau-0.6)/0.9)
        if al<=0.01:continue
        ph,pw=ch['patch'].shape[:2];M=cv2.getRotationMatrix2D((pw/2,ph/2),-math.degrees(ang),1.0);M[0,2]+=x-pw/2;M[1,2]+=y-ph/2
        warped=cv2.warpAffine(ch['patch'],M,(W,H),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=0)
        a=(warped[...,3]*al)[...,None];out=out*(1-a)+warped[...,:3]*a
    return out
def t_match(fa,fb,p,c):
    ma=c['mA']();mb=c['mB']();cxa,cya,owa,oha=csz(ma);cxb,cyb,owb,ohb=csz(mb)
    tw=0.42*W;tcx,tcy=W/2,H/2
    sa=float(np.clip(tw/max(owa,40),0.7,3.0));sb=float(np.clip(tw/max(owb,40),0.7,3.0))
    ea=smooth(p/0.75);eb=smooth((p-0.25)/0.75)
    s=1+(sa-1)*ea;a=cv2.warpAffine(fa,aff(s,cxa,cya,cxa+(tcx-cxa)*ea,cya+(tcy-cya)*ea),(W,H),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
    s2=1+(sb-1)*(1-eb);b=cv2.warpAffine(fb,aff(s2,cxb,cyb,cxb+(tcx-cxb)*(1-eb),cyb+(tcy-cyb)*(1-eb)),(W,H),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
    return lerp(a,b,smooth((p-0.33)/0.34))
TR={'dissolve':(t_dissolve,2.2),'defocus':(t_defocus,2.8),'washout':(t_washout,2.4),'dipblack':(t_dipblack,3.0),'goldbloom':(t_goldbloom,2.6),
 'colordrain':(t_colordrain,2.8),'colorseep':(t_colorseep,2.8),'erase':(t_erase,3.2),'water':(t_water,3.4),'tear':(t_tear,1.6),'iris':(t_iris,2.4),
 'zoomthrough':(t_zoomthrough,2.2),'whip':(t_whip,0.9),'smash':(t_smash,0.7),'ripple':(t_ripple,2.8),'ink':(t_ink,3.2),'peel':(t_peel,2.2),'wipe':(t_wipe,1.8),
 'smoke':(t_smoke,3.2),'burn':(t_burn,3.2),'fill':(t_fill,3.4),'matte':(t_matte,3.0),'portal':(t_portal,3.2),'shatter':(t_shatter,3.2),'match':(t_match,3.2)}
class VidSrc:
    """sequential reader over a Veo shot video; holds first/last frame outside its range"""
    def __init__(self,path):
        self.cap=cv2.VideoCapture(path);self.n=int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 192;self.pos=-1;self.last=None
    def get(self,s):
        idx=int(min(max(s*FPS,0),self.n-1))
        while self.pos<idx:
            ok,fr=self.cap.read()
            if not ok:break
            self.pos+=1;self.last=cv2.cvtColor(fr,cv2.COLOR_BGR2RGB)
        if self.last is None:return None
        if self.last.shape[1]!=W:return cv2.resize(self.last,(W,H),interpolation=cv2.INTER_LANCZOS4)
        return self.last
def clean_plate(fa,ma):
    low=cv2.resize((fa*255).astype(np.uint8),(480,270),interpolation=cv2.INTER_AREA)
    mk=(cv2.resize(ma,(480,270))>0.25).astype(np.uint8);mk=cv2.dilate(mk,np.ones((7,7),np.uint8))
    inp=cv2.inpaint(low,mk*255,5,cv2.INPAINT_TELEA);up=cv2.resize(inp,(W,H),interpolation=cv2.INTER_CUBIC).astype(np.float32)/255.0
    m=cv2.GaussianBlur(cv2.resize(mk.astype(np.float32),(W,H)),(0,0),7)[...,None];return fa*(1-m)+up*m
def render_clip(a,b,kind,params,idx,ease_a,ease_b,out,frames=NF,vid_a=None,vid_b=None,obj_dir='objcache'):
    fn,D=TR[kind];c=dict(params)
    ka=idx%4;kb=(idx+1)%4   # סוג תנועת מצלמה (0-3), מתחלף בין קליפים
    A=load(a);B=load(b)
    c.setdefault('focus',(0.5,0.5))
    if 'col' in c:c['col']=np.array(c['col'],np.float32)
    c['n1']=fbm(idx*7+1);c['n2']=fbm(idx*7+2,sx=0.15,sy=2.5,octs=4);c['seed']=idx*13+5;c['D']=D
    import objects
    objects.OBJ_DIR=obj_dir
    cur=[0.0]
    def wA():
        w=1.0
        if ease_a:e=min(1,cur[0]/1.2);w=e*e*(3-2*e)
        return w
    def wB():
        w=1.0
        if ease_b:e=min(1,(8-cur[0])/1.2);w=e*e*(3-2*e)
        return w
    sh=params.get('shape','mask')
    oa=objects.get(a,params['objA'],sh) if 'objA' in params else None
    ob=objects.get(b,params['objB'],'mask') if 'objB' in params else None
    if 'fobj' in params:
        g=objects.get(a,params['fobj'],'mask')
        if g:c['focus']=((g[1][1]+g[1][3])/2000,(g[1][0]+g[1][2])/2000)
    if 'fobjB' in params:
        g=objects.get(b,params['fobjB'],'mask')
        if g:c['focus']=((g[1][1]+g[1][3])/2000,(g[1][0]+g[1][2])/2000)
    if oa is not None:
        mAs=oa[0].astype(np.float32)
        c['mA']=lambda:render_cam_gray(mAs,ka,4+cur[0],wA())
        c['cA']=lambda:clean_plate(c['fa_cur'],c['mA']())
    if ob is not None:
        mBs=ob[0].astype(np.float32);c['mB']=lambda:render_cam_gray(mBs,kb,cur[0]-4,wB())
    tc=4.0;t0=tc-D/2;t1=tc+D/2
    ff=subprocess.Popen(['ffmpeg','-v','error','-y','-f','rawvideo','-pix_fmt','rgb24','-s',f'{W}x{H}','-r',str(FPS),'-i','-','-c:v','libx264','-crf','17','-preset','fast','-pix_fmt','yuv420p',out],stdin=subprocess.PIPE)
    SA=VidSrc(vid_a) if vid_a and os.path.exists(vid_a) else None;SB=VidSrc(vid_b) if vid_b and os.path.exists(vid_b) else None
    sA0=0.0 if ease_a else 4.0
    for f in range(frames):
        t=f/FPS;cur[0]=t
        def cam_a():
            s=sA0+t;w=1.0
            if ease_a:e=min(1,t/1.2);w=e*e*(3-2*e)
            src=SA.get(s) if SA else None
            if src is None:return render_cam(A,ka,4+t,w)
            return render_cam((src*255).astype(np.uint8) if src.dtype!=np.uint8 else src,ka,4+t,w)
        def cam_b():
            s=t-4;w=1.0
            if ease_b:e=min(1,(8-t)/1.2);w=e*e*(3-2*e)
            src=SB.get(s) if SB else None
            if src is None:return render_cam(B,kb,s,w)
            return render_cam(src,kb,s,w)
        if t<t0:fr=cam_a();c['fa_cur']=fr
        elif t>=t1:fr=cam_b()
        else:
            p=(t-t0)/D;fa=cam_a();c['fa_cur']=fa;fb=cam_b()
            fr=fn(fa,fb,p,c)
        ff.stdin.write((np.clip(fr,0,1)*255+0.5).astype(np.uint8).tobytes())
    ff.stdin.close();ff.wait()
def _tup(v):return {k:(tuple(x) if isinstance(x,list) else x) for k,x in v.items()}
if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__,formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('a');ap.add_argument('b');ap.add_argument('kind',choices=sorted(TR))
    ap.add_argument('--params',default='{}');ap.add_argument('--out',default='tt.mp4');ap.add_argument('--idx',type=int,default=0)
    ap.add_argument('--ease-a',action='store_true');ap.add_argument('--ease-b',action='store_true')
    ap.add_argument('--vid-a');ap.add_argument('--vid-b');ap.add_argument('--obj-dir',default='objcache');ap.add_argument('--frames',type=int,default=NF)
    x=ap.parse_args()
    render_clip(x.a,x.b,x.kind,_tup(json.loads(x.params)),x.idx,x.ease_a,x.ease_b,x.out,x.frames,x.vid_a,x.vid_b,x.obj_dir)
    print('saved',x.out)
