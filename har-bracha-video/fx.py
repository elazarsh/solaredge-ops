# -*- coding: utf-8 -*-
"""ספריית אפקטים: easing, בליטת ספרייט, קונפטי, מדבקות, מעברים, גריידינג."""
import numpy as np, cv2, math
from functools import lru_cache
from PIL import Image, ImageDraw, ImageFont
W,H=1920,1080
SCR="/tmp/claude-0/-home-user-solaredge-ops/73fe8d55-5833-5852-9694-53b5adaa6cc2/scratchpad"
FONT=f"{SCR}/fonts/Heebo.ttf"
def rgb2bgr(c): return (c[2],c[1],c[0])
PALETTE={'blue':(18,118,188),'orange':(233,127,45),'green':(15,149,73),'pink':(181,48,111),'lime':(140,197,64),'sun':(255,200,60),'navy':(11,37,69),'white':(255,255,255)}
BR=['blue','orange','green','pink','lime']
# ---------- easing
def clamp(x,a=0.,b=1.): return max(a,min(b,x))
def e_io(x): x=clamp(x); return x*x*(3-2*x)
def e_out(x): x=clamp(x); return 1-(1-x)**3
def e_in(x): x=clamp(x); return x**3
def e_back(x,s=1.70158): x=clamp(x); return 1+(s+1)*(x-1)**3+s*(x-1)**2
def e_elastic(x):
    x=clamp(x)
    if x in (0,1): return x
    return 2**(-9*x)*math.sin((x*10-0.75)*(2*math.pi)/3)+1
# ---------- fonts / text sprites
@lru_cache(maxsize=None)
def font(size,wght=800):
    f=ImageFont.truetype(FONT,size,layout_engine=ImageFont.Layout.RAQM)
    try: f.set_variation_by_axes([wght])
    except Exception: pass
    return f
@lru_cache(maxsize=512)
def text_sprite(text,size,fg,bg=None,pad=(46,22),radius=None,shadow=True,outline=None,wght=800,direction='rtl'):
    f=font(size,wght)
    tmp=ImageDraw.Draw(Image.new('RGBA',(10,10)))
    l,t,r,b=tmp.textbbox((0,0),text,font=f,direction=direction)
    tw,th=r-l,b-t
    m=40 if shadow else 6
    w=tw+pad[0]*2+m*2; h=th+pad[1]*2+m*2
    img=Image.new('RGBA',(w,h),(0,0,0,0))
    if bg is not None:
        rad=radius if radius is not None else (th+pad[1]*2)//2
        if shadow:
            sh=Image.new('RGBA',(w,h),(0,0,0,0)); ImageDraw.Draw(sh).rounded_rectangle([m,m+10,w-m,h-m+10],rad,fill=(0,0,0,110))
            sh=sh.filter(__import__('PIL.ImageFilter',fromlist=['x']).GaussianBlur(14)); img.alpha_composite(sh)
        ImageDraw.Draw(img).rounded_rectangle([m,m,w-m,h-m],rad,fill=tuple(bg)+(255,))
    d=ImageDraw.Draw(img)
    if bg is None and shadow:
        sh=Image.new('RGBA',(w,h),(0,0,0,0)); ImageDraw.Draw(sh).text((m+pad[0]-l+4,m+pad[1]-t+8),text,font=f,fill=(0,0,0,150),direction=direction)
        sh=sh.filter(__import__('PIL.ImageFilter',fromlist=['x']).GaussianBlur(6)); img.alpha_composite(sh)
    if outline:
        d.text((m+pad[0]-l,m+pad[1]-t),text,font=f,fill=tuple(fg)+(255,),direction=direction,stroke_width=outline[0],stroke_fill=tuple(outline[1])+(255,))
    else:
        d.text((m+pad[0]-l,m+pad[1]-t),text,font=f,fill=tuple(fg)+(255,),direction=direction)
    a=np.array(img); return a  # RGBA
def blit(frame,spr,cx,cy,scale=1.0,angle=0.0,alpha=1.0,sx=None,sy=None):
    """spr: RGBA (H,W,4); frame: BGR uint8. כותב in-place."""
    if alpha<=0.003 or scale<=0.001: return
    h,w=spr.shape[:2]
    sxx=(sx if sx is not None else scale); syy=(sy if sy is not None else scale)
    ca,sa=math.cos(math.radians(angle)),math.sin(math.radians(angle))
    # bbox
    ow=int(abs(w*sxx*ca)+abs(h*syy*sa))+4; oh=int(abs(w*sxx*sa)+abs(h*syy*ca))+4
    if ow<=2 or oh<=2 or ow>6000 or oh>6000: return
    M=np.array([[sxx*ca,-syy*sa,0],[sxx*sa,syy*ca,0]],np.float32)
    M[:,2]=np.array([ow/2,oh/2])-M[:,:2]@np.array([w/2,h/2])
    out=cv2.warpAffine(spr,M,(ow,oh),flags=cv2.INTER_AREA if max(sxx,syy)<1 else cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=(0,0,0,0))
    x0=int(round(cx-ow/2)); y0=int(round(cy-oh/2))
    fx0,fy0=max(0,x0),max(0,y0); fx1,fy1=min(frame.shape[1],x0+ow),min(frame.shape[0],y0+oh)
    if fx1<=fx0 or fy1<=fy0: return
    o=out[fy0-y0:fy1-y0,fx0-x0:fx1-x0]
    a=(o[...,3:4].astype(np.float32)/255.)*alpha
    roi=frame[fy0:fy1,fx0:fx1].astype(np.float32)
    rgb=o[...,2::-1].astype(np.float32)  # RGBA->BGR
    frame[fy0:fy1,fx0:fx1]=(roi*(1-a)+rgb*a).astype(np.uint8)
def blit_bgra(frame,spr_bgra,*a,**k): pass
# ---------- shapes sprites
@lru_cache(maxsize=None)
def shape_sprite(kind,color,size=160):
    S=size*2; img=Image.new('RGBA',(S,S),(0,0,0,0)); d=ImageDraw.Draw(img); c=tuple(PALETTE[color] if isinstance(color,str) else color)+(255,); cx=cy=S/2; r=size*0.9
    if kind=='star':
        pts=[(cx+(r if i%2==0 else r*0.45)*math.sin(i*math.pi/5),cy-(r if i%2==0 else r*0.45)*math.cos(i*math.pi/5)) for i in range(10)]; d.polygon(pts,fill=c)
    elif kind=='spark':
        pts=[]
        for i in range(8):
            rr=r if i%2==0 else r*0.18; ang=i*math.pi/4
            pts.append((cx+rr*math.sin(ang),cy-rr*math.cos(ang)))
        d.polygon(pts,fill=c)
    elif kind=='heart':
        r2=r*0.5
        d.ellipse([cx-r2*1.05-r2*0.05,cy-r*0.75,cx+r2*0.05-0.0,cy-r*0.75+2*r2],fill=c)
        d.ellipse([cx-r2*0.05,cy-r*0.75,cx+r2*1.05+r2*0.05,cy-r*0.75+2*r2],fill=c)
        d.polygon([(cx-r*0.97,cy-r*0.2),(cx+r*0.97,cy-r*0.2),(cx,cy+r*0.9)],fill=c)
    elif kind=='circle': d.ellipse([cx-r*0.6,cy-r*0.6,cx+r*0.6,cy+r*0.6],fill=c)
    elif kind=='ring': d.ellipse([cx-r*0.8,cy-r*0.8,cx+r*0.8,cy+r*0.8],outline=c,width=int(size*0.14))
    elif kind=='tri': d.polygon([(cx,cy-r*0.8),(cx+r*0.8,cy+r*0.65),(cx-r*0.8,cy+r*0.65)],fill=c)
    elif kind=='squig':
        pts=[(cx-r+ i*r/6, cy+math.sin(i*1.4)*r*0.35) for i in range(13)]; d.line(pts,fill=c,width=int(size*0.14),joint='curve')
    elif kind=='plus':
        d.rectangle([cx-r*0.18,cy-r*0.7,cx+r*0.18,cy+r*0.7],fill=c); d.rectangle([cx-r*0.7,cy-r*0.18,cx+r*0.7,cy+r*0.18],fill=c)
    return np.array(img)
# ---------- backgrounds
@lru_cache(maxsize=32)
def gradient(c1,c2,angle=35):
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32); a=math.radians(angle)
    t=(xx*math.cos(a)+yy*math.sin(a)); t=(t-t.min())/(t.max()-t.min())
    g=np.zeros((H,W,3),np.float32)
    for i in range(3): g[...,i]=PALETTE[c1][2-i]*(1-t)+PALETTE[c2][2-i]*t   # BGR
    return g.astype(np.uint8)
def floating_shapes(frame,t,seed,n=14,colors=('white','sun','lime','pink'),alpha=0.35,speed=1.0):
    rng=np.random.RandomState(seed)
    for i in range(n):
        kind=rng.choice(['circle','ring','tri','star','plus','squig','spark']); col=colors[rng.randint(len(colors))]
        x0=rng.uniform(0,W); y0=rng.uniform(0,H); sc=rng.uniform(0.35,1.0); rot=rng.uniform(0,360); vx=rng.uniform(-40,40)*speed; vy=rng.uniform(-60,-20)*speed; rs=rng.uniform(-60,60)
        x=(x0+vx*t)%(W+200)-100; y=(y0+vy*t)%(H+200)-100
        blit(frame,shape_sprite(kind,col,90),x,y,scale=sc,angle=rot+rs*t,alpha=alpha)
def confetti(frame,t,seed,n=70,t0=0.0,fall=420,palette=None,sz=(10,22)):
    palette=palette or [PALETTE[c] for c in ('blue','orange','green','pink','lime','sun','white')]
    rng=np.random.RandomState(seed)
    tt=max(0,t-t0)
    for i in range(n):
        x0=rng.uniform(0,W); y0=rng.uniform(-H,0); vy=rng.uniform(.6,1.4)*fall; sw=rng.uniform(20,80); ph=rng.uniform(0,6.28); rot=rng.uniform(0,6.28); rv=rng.uniform(-6,6)
        s=rng.uniform(*sz); col=palette[rng.randint(len(palette))]
        y=y0+vy*tt; x=x0+math.sin(tt*2+ph)*sw
        if y<-30 or y>H+30: continue
        a=rot+rv*tt; c,s_=math.cos(a),math.sin(a); wv=abs(math.cos(tt*5+ph))*0.9+0.1
        pts=np.array([[-s,-s*0.5*wv],[s,-s*0.5*wv],[s,s*0.5*wv],[-s,s*0.5*wv]])
        R=np.array([[c,-s_],[s_,c]]); pts=(pts@R.T+[x,y]).astype(np.int32)
        cv2.fillConvexPoly(frame,pts,(col[2],col[1],col[0]),cv2.LINE_AA)
def bokeh(frame,t,seed,n=22,alpha=0.22):
    ov=frame.copy(); rng=np.random.RandomState(seed)
    for i in range(n):
        x=(rng.uniform(0,W)+rng.uniform(-30,30)*t)%W; y=(rng.uniform(0,H)-rng.uniform(15,45)*t)%H; r=int(rng.uniform(14,60))
        col=PALETTE[BR[rng.randint(5)]]; cv2.circle(ov,(int(x),int(y)),r,(col[2],col[1],col[0]),-1,cv2.LINE_AA)
    cv2.addWeighted(ov,alpha,frame,1-alpha,0,frame)
def ring_burst(frame,cx,cy,p,color='white',maxr=900,thick=24,alpha=0.9):
    if p<=0 or p>=1: return
    r=int(e_out(p)*maxr); th=max(2,int(thick*(1-p)))
    ov=frame.copy(); c=PALETTE[color]; cv2.circle(ov,(int(cx),int(cy)),r,(c[2],c[1],c[0]),th,cv2.LINE_AA)
    a=alpha*(1-p); cv2.addWeighted(ov,a,frame,1-a,0,frame)
# ---------- screen effects
def rgb_split(f,dx):
    dx=int(dx)
    if dx==0: return f
    o=f.copy(); o[...,2]=np.roll(f[...,2],dx,axis=1); o[...,0]=np.roll(f[...,0],-dx,axis=1); return o
def glitch(f,seed,amount=1.0):
    rng=np.random.RandomState(seed); o=f.copy()
    for _ in range(int(7*amount)):
        y=rng.randint(0,H-40); h=rng.randint(12,110); dx=rng.randint(-120,120)
        o[y:y+h]=np.roll(o[y:y+h],dx,axis=1)
    return rgb_split(o,int(14*amount))
def shake(f,seed,amp=10):
    rng=np.random.RandomState(seed); dx,dy=rng.uniform(-amp,amp,2)
    M=np.float32([[1,0,dx],[0,1,dy]]); return cv2.warpAffine(f,M,(W,H),borderMode=cv2.BORDER_REFLECT)
def flash(f,a):
    if a<=0.003: return f
    return cv2.addWeighted(f,1-a,np.full_like(f,255),a,0)
def duotone(f,c1,c2,a):
    if a<=0.01: return f
    g=cv2.cvtColor(f,cv2.COLOR_BGR2GRAY)
    lut=np.zeros((256,1,3),np.uint8)
    for i in range(3): lut[:,0,i]=np.linspace(PALETTE[c1][2-i],PALETTE[c2][2-i],256)
    d=cv2.LUT(cv2.merge([g,g,g]),lut)
    return cv2.addWeighted(f,1-a,d,a,0)
_leak={}
def light_leak(f,t,a=0.35,cols=('orange','pink')):
    key=cols
    if key not in _leak:
        yy,xx=np.mgrid[0:H,0:W].astype(np.float32); _leak[key]=(xx,yy)
    xx,yy=_leak[key]
    cx=(0.15+0.12*math.sin(t*0.9))*W; cy=(0.2+0.1*math.cos(t*0.7))*H
    d=np.sqrt(((xx-cx)/(0.5*W))**2+((yy-cy)/(0.7*H))**2); m=np.clip(1-d,0,1)**2
    c=PALETTE[cols[0]]; c2=PALETTE[cols[1]]
    layer=np.zeros((H,W,3),np.float32)
    for i in range(3): layer[...,i]=m*(c[2-i]*0.8)
    cx2=(0.9-0.1*math.sin(t*0.8))*W; d2=np.sqrt(((xx-cx2)/(0.4*W))**2+((yy-0.85*H)/(0.6*H))**2); m2=np.clip(1-d2,0,1)**2
    for i in range(3): layer[...,i]+=m2*(c2[2-i]*0.7)
    return np.clip(f.astype(np.float32)+layer*a*1.6,0,255).astype(np.uint8)
def vhs(f,seed):
    o=f.copy(); o[::4]=(o[::4]*0.82).astype(np.uint8); return rgb_split(o,4)
_vig=None
def vignette_mask():
    global _vig
    if _vig is None:
        yy,xx=np.mgrid[0:H,0:W].astype(np.float32); d=np.sqrt(((xx-W/2)/(W/2))**2+((yy-H/2)/(H/2))**2)
        _vig=(1-0.28*np.clip(d-0.55,0,1)**1.6)[...,None].astype(np.float32)
    return _vig
_grain=None
def grain(idx):
    global _grain
    if _grain is None:
        r=np.random.RandomState(7); _grain=[(r.randn(H//2,W//2)*5).astype(np.float32) for _ in range(6)]
    g=cv2.resize(_grain[idx%6],(W,H),interpolation=cv2.INTER_LINEAR)
    return g[...,None]
def final_grade(f,idx,vig=True,gr=True):
    o=f.astype(np.float32)
    if vig: o*=vignette_mask()
    if gr: o+=grain(idx)
    return np.clip(o,0,255).astype(np.uint8)
# ---------- transitions: A,B BGR uint8 ; p in 0..1
def tr_cross(A,B,p): return cv2.addWeighted(A,1-p,B,p,0)
def tr_whip(A,B,p,direction=1):
    pe=e_io(p); sh=int(pe*W)
    comp=np.empty_like(A)
    if direction>0:
        comp[:,:W-sh]=A[:,sh:]; comp[:,W-sh:]=B[:,:sh] if sh>0 else comp[:,W-sh:]
        # B enters from right
        comp=np.concatenate([A[:,sh:],B[:,:sh]],axis=1) if sh>0 else A.copy()
    else:
        comp=np.concatenate([B[:,W-sh:],A[:,:W-sh]],axis=1) if sh>0 else A.copy()
    k=int(4+110*math.sin(math.pi*p)); k|=1
    if k>3: comp=cv2.blur(comp,(k,1))
    return rgb_split(comp,int(18*math.sin(math.pi*p)))
def tr_push_vert(A,B,p):
    pe=e_io(p); sh=int(pe*H)
    return np.concatenate([A[sh:],B[:sh]],axis=0) if sh>0 else A.copy()
def scale_img(img,s,cx=W/2,cy=H/2):
    M=np.float32([[s,0,cx-s*cx],[0,s,cy-s*cy]]); return cv2.warpAffine(img,M,(W,H),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
def tr_zoomthrough(A,B,p):
    pe=e_io(p)
    a=scale_img(A,1+1.2*pe); b=scale_img(B,0.55+0.45*pe)
    out=cv2.addWeighted(a,1-clamp(pe*1.6-0.1),b,clamp(pe*1.6-0.1),0)
    k=int(3+40*math.sin(math.pi*p))|1
    return cv2.GaussianBlur(out,(k,k),0)
def tr_circle(A,B,p,cx=W/2,cy=H/2,ring='white'):
    pe=e_io(p); R=pe*math.hypot(W,H)*0.62
    mask=np.zeros((H,W),np.uint8); cv2.circle(mask,(int(cx),int(cy)),int(R),255,-1,cv2.LINE_AA)
    m=(mask[...,None]/255.).astype(np.float32); out=(A*(1-m)+B*m).astype(np.uint8)
    c=PALETTE[ring]; cv2.circle(out,(int(cx),int(cy)),int(R),(c[2],c[1],c[0]),max(2,int(26*math.sin(math.pi*p))),cv2.LINE_AA)
    return out
def tr_diag(A,B,p,color='orange',slope=0.45,flip=False):
    pe=e_io(p); off=(pe*(W+H*slope+260))-130
    yy,xx=np.mgrid[0:H,0:W].astype(np.float32)
    s=(xx if not flip else (W-xx))-yy*slope
    m=(s<off).astype(np.float32)[...,None]
    out=(A*(1-m)+B*m).astype(np.uint8)
    band=((s>=off)&(s<off+90)).astype(np.float32)[...,None]; c=PALETTE[color]
    out=(out*(1-band)+np.array([c[2],c[1],c[0]],np.float32)*band).astype(np.uint8)
    return out
def tr_flash(A,B,p):
    if p<0.5: return flash(A,e_in(p*2))
    return flash(B,1-e_out((p-0.5)*2))
def tr_glitch(A,B,p,seed=0):
    base=B if p>0.5 else A
    return glitch(base,seed+int(p*10),amount=1.4*math.sin(math.pi*p)+0.2)
def tr_blinds(A,B,p,n=8):
    pe=e_io(p); out=A.copy(); h=H//n
    for i in range(n):
        hh=int(h*pe); out[i*h:i*h+hh]=B[i*h:i*h+hh]
    return out
def tr_iris_black(B,p,color='white'):
    A=np.zeros_like(B); return tr_circle(A,B,p,ring=color)
TRANS={'cross':tr_cross,'whip':tr_whip,'whipL':lambda A,B,p:tr_whip(A,B,p,-1),'zoom':tr_zoomthrough,'circle':tr_circle,'diag':tr_diag,'diagO':lambda A,B,p:tr_diag(A,B,p,'pink',flip=True),
 'flash':tr_flash,'glitch':tr_glitch,'blinds':tr_blinds,'push':tr_push_vert,'cut':lambda A,B,p:B}
