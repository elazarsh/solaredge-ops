import numpy as np, math, os, shutil
from PIL import Image, ImageDraw
FPS=25; W,H=1920,1080
import json
TL=json.load(open('tl.json')); S=lambda n:TL[n]['start']; END=TL['_total']+0.2
WINS=[(S('wait1'),S('wait1')+TL['wait1']['dur'],0.12,0.45,1.0,True),(S('wait2'),S('wait2')+TL['wait2']['dur'],0.45,0.80,1.0,True),(S('steam'),S('steam')+TL['steam']['dur'],0.80,1.0,0,False)]
PULSES=[S('c2b')+0.1,S('wait2')+0.05,S('steam')+0.05]
fx=lambda f:150+f*1620
fy=lambda f:f*1080
ICONS=[(S('Ldrop')+0.45,'ok',fx(0.36),fy(0.66),S('Ldrop')+TL['Ldrop']['dur']),(S('Ldrop')+1.0,'x',fx(0.51),fy(0.56),S('Ldrop')+TL['Ldrop']['dur']),(S('c5')+2.3,'x',fx(0.42),fy(0.58),S('c5')+TL['c5']['dur']),(S('G')+0.4,'x',fx(0.27),fy(0.50),S('G')+TL['G']['dur']),(S('K')+0.9,'x',fx(0.45),fy(0.57),S('K')+TL['K']['dur']),(S('K')+1.5,'ok',fx(0.33),fy(0.42),S('K')+TL['K']['dur'])]
BULB=(S('K'),S('K')+TL['K']['dur'],fx(0.52),fy(0.17))
def E(x): return max(0,min(1,x))
def tintcol(p):
    # p in [0,1): day -> dusk -> night -> dawn -> day
    keys=[(0.0,(0,0,0,0)),(0.25,(255,120,30,85)),(0.5,(10,20,70,150)),(0.75,(255,140,170,80)),(1.0,(0,0,0,0))]
    for (a,ca),(b,cb) in zip(keys,keys[1:]):
        if a<=p<=b:
            u=(p-a)/(b-a); return tuple(ca[i]+(cb[i]-ca[i])*u for i in range(4))
    return (0,0,0,0)
def clock(d,cx,cy,r,ang,alpha):
    S=3; sz=int(2*r*1.2); im=Image.new("RGBA",(sz*S,sz*S),(0,0,0,0)); g=ImageDraw.Draw(im); c=sz*S//2; R=r*S
    g.ellipse([c-R,c-R,c+R,c+R],fill=(255,246,214,255),outline=(40,30,20,255),width=9*S//2)
    g.ellipse([c-R-10*S,c-R-10*S,c+R+10*S,c+R+10*S],outline=(240,170,40,255),width=7*S//2)
    for k in range(12):
        a=k*math.pi/6; r1=R*0.82; r2=R*0.94; g.line([c+r1*math.sin(a),c-r1*math.cos(a),c+r2*math.sin(a),c-r2*math.cos(a)],fill=(40,30,20,255),width=6*S//2)
    am=ang*2*math.pi; ah=am/12
    g.line([c,c,c+R*0.55*math.sin(ah),c-R*0.55*math.cos(ah)],fill=(40,30,20,255),width=11*S//2)
    g.line([c,c,c+R*0.8*math.sin(am),c-R*0.8*math.cos(am)],fill=(200,40,40,255),width=7*S//2)
    g.ellipse([c-8*S//2,c-8*S//2,c+8*S//2,c+8*S//2],fill=(40,30,20,255))
    im=im.resize((sz,sz),Image.LANCZOS)
    if alpha<1: im.putalpha(im.getchannel("A").point(lambda v:int(v*alpha)))
    d.alpha_composite(im,(int(cx-sz/2),int(cy-sz/2)))
def meter(d,x,y,h,lvl,alpha,t):
    S=2; w=90; pad=60; im=Image.new("RGBA",((w+2*pad)*S,(h+2*pad+170)*S),(0,0,0,0)); g=ImageDraw.Draw(im)
    X=pad*S+w*S//2; top=170*S+pad*S; bot=top+h*S; tw=44*S
    col=(int(240+15*lvl),int(190*(1-lvl)+30),int(40*(1-lvl)+20),255)
    g.rounded_rectangle([X-tw//2,top,X+tw//2,bot],radius=tw//2,fill=(255,255,255,255),outline=(30,30,30,255),width=6*S)
    fh=int((bot-top)*lvl); g.rounded_rectangle([X-tw//2+7*S,bot-fh,X+tw//2-7*S,bot],radius=tw//2,fill=col)
    g.ellipse([X-48*S,bot-14*S,X+48*S,bot+82*S],fill=col,outline=(30,30,30,255),width=6*S)
    # angry face
    fy=top-95*S; fr=62*S; fc=(255,int(215-150*lvl),int(60-30*lvl),255)
    g.ellipse([X-fr,fy-fr,X+fr,fy+fr],fill=fc,outline=(30,30,30,255),width=6*S)
    k=0.2+0.5*lvl
    g.line([X-44*S,fy-22*S-k*14*S,X-10*S,fy-8*S],fill=(30,30,30,255),width=8*S); g.line([X+44*S,fy-22*S-k*14*S,X+10*S,fy-8*S],fill=(30,30,30,255),width=8*S)
    g.ellipse([X-30*S,fy-2*S,X-14*S,fy+14*S],fill=(30,30,30,255)); g.ellipse([X+14*S,fy-2*S,X+30*S,fy+14*S],fill=(30,30,30,255))
    g.arc([X-26*S,fy+22*S,X+26*S,fy+60*S],200,340,fill=(30,30,30,255),width=7*S)
    if lvl>0.8:
        for i in range(3):
            ph=(t*1.6+i/3)%1; px=X+(i-1)*34*S; py=fy-fr-ph*70*S; rr=(14+14*ph)*S
            g.ellipse([px-rr,py-rr,px+rr,py+rr],fill=(255,255,255,int(230*(1-ph))))
    im=im.resize((im.width//S,im.height//S),Image.LANCZOS)
    if alpha<1: im.putalpha(im.getchannel("A").point(lambda v:int(v*alpha)))
    d.alpha_composite(im,(x-pad-w//2+10,y-170))

def back(x):
    x=E(x); c=1.9; return 1+(c+1)*(x-1)**3+c*(x-1)**2
def icon(d,kind,cx,cy,u,fade):
    S_=2; r=62; sz=int(2*r*1.7); im=Image.new("RGBA",(sz*S_,sz*S_),(0,0,0,0)); g=ImageDraw.Draw(im); c=sz*S_//2; sc=max(0.01,back(u/0.32)); R=r*S_*sc
    col=(15,150,72,255) if kind=="ok" else (214,58,47,255)
    # pulse ring
    pr=E((u-0.1)/0.6); 
    if 0<pr<1: g.ellipse([c-R*(1+0.7*pr),c-R*(1+0.7*pr),c+R*(1+0.7*pr),c+R*(1+0.7*pr)],outline=col[:3]+(int(200*(1-pr)),),width=int(8*S_))
    g.ellipse([c-R+6*S_,c-R+10*S_,c+R+6*S_,c+R+10*S_],fill=(0,0,0,70))
    g.ellipse([c-R,c-R,c+R,c+R],fill=col,outline=(255,255,255,255),width=int(7*S_))
    k=R*0.42; w=int(15*S_*sc)
    if kind=="ok": g.line([c-k*0.9,c+k*0.05,c-k*0.2,c+k*0.7,c+k,c-k*0.7],fill=(255,255,255,255),width=w,joint="curve")
    else: g.line([c-k,c-k,c+k,c+k],fill=(255,255,255,255),width=w); g.line([c+k,c-k,c-k,c+k],fill=(255,255,255,255),width=w)
    im=im.resize((sz,sz),Image.LANCZOS)
    if fade<1: im.putalpha(im.getchannel("A").point(lambda v:int(v*fade)))
    d.alpha_composite(im,(int(cx-sz/2),int(cy-sz/2)))
def glow(d,cx,cy,t,al):
    pulse=0.75+0.25*math.sin(t*9); R=170
    yy_,xx_=np.mgrid[0:2*R,0:2*R]; rr=np.sqrt((xx_-R)**2+(yy_-R)**2)/R
    a=np.clip(1-rr,0,1)**2*200*pulse*al
    g=np.zeros((2*R,2*R,4),np.uint8); g[...,0]=255; g[...,1]=225; g[...,2]=90; g[...,3]=a.astype(np.uint8)
    d.alpha_composite(Image.fromarray(g,"RGBA"),(int(cx-R),int(cy-R)))
os.makedirs("ovl",exist_ok=True)
blank=Image.new("RGBA",(W,H),(0,0,0,0)); blank.save("ovl/blank.png")
yy,xx=np.mgrid[0:H,0:W]; vig=np.clip(((xx-W/2)/(W/2))**2+((yy-H/2)/(H/2))**2-0.35,0,1)  # edge mask
n=int(END*FPS)
for i in range(n):
    t=i/FPS; out=f"ovl/o{i:04d}.png"
    act=None
    for wnd in WINS:
        if wnd[0]-0.01<=t<wnd[1]: act=wnd
    pulse=max([max(0,1-abs(t-pt-0.2)/0.25) for pt in PULSES]+[0])
    ic=[x for x in ICONS if x[0]<=t<x[4]]; bl=BULB[0]<=t<BULB[1]
    if act is None and pulse<=0.01 and not ic and not bl:
        try: os.remove(out)
        except: pass
        os.link("ovl/blank.png",out); continue
    im=Image.new("RGBA",(W,H),(0,0,0,0))
    if act:
        a,b,l0,l1,cyc,tint=act; u=max(0.0,(t-a)/(b-a)); al=min(E((t-a)/0.25),E((b-t)/0.25))
        if tint and cyc>0:
            c=tintcol((u*cyc)%1.0); ov=np.zeros((H,W,4),np.uint8); ov[...,:3]=np.array(c[:3],np.uint8); ov[...,3]=int(c[3]*al); im=Image.fromarray(ov,"RGBA")
            if 0.4<(u*cyc)%1.0<0.6:
                rng=np.random.default_rng(i); st=Image.new("RGBA",(W,H),(0,0,0,0)); g=ImageDraw.Draw(st)
                for _ in range(26):
                    x=int(rng.integers(0,W)); y=int(rng.integers(0,500)); r=int(rng.integers(3,7)); g.ellipse([x-r,y-r,x+r,y+r],fill=(255,255,220,int(210*al)))
                im.alpha_composite(st)
        if tint:
            clock(im,1740,170,95,u*cyc*4 if cyc else 0,al)
        lvl=l0+(l1-l0)*(u**0.8)
        meter(im,130,330,420,lvl,al,t)
    if bl: glow(im,BULB[2],BULB[3],t,min(E((t-BULB[0])/0.2),E((BULB[1]-t)/0.2)))
    for (t0,k,x,y,t1) in ic: icon(im,k,x,y,t-t0,min(1,E((t1-t)/0.15)))
    if pulse>0.01:
        ov=np.zeros((H,W,4),np.uint8); ov[...,0]=235; ov[...,1]=30; ov[...,2]=30; ov[...,3]=(vig*170*pulse).astype(np.uint8)
        im.alpha_composite(Image.fromarray(ov,"RGBA"))
    im.save(out)
print("ok",n)
