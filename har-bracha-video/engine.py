# -*- coding: utf-8 -*-
import numpy as np, cv2, math, json, os, sys
from fx import *
from scenes import S as SCENES, BEAT
FPS=30; TOTAL=81.0
files_rel=json.load(open(f"{SCR}/order.json"))
# ---------- הגדרות לכל סצנה: סגנון, אפקטים, מעבר
# style: full / card / circle / dip_slant / dip_straight
CFG={
"M01":dict(style="full",fx=["leak","sparkle"],tr=("iris",0.9)),
"M02":dict(style="card",bg=("blue","lime"),tilt=-3,fx=["shapes"],tr=("diag",0.5)),
"M03":dict(style="dip_slant",bg=("pink","orange"),tr=("push",0.45)),
"M04":dict(style="full",fx=["sparkle"],tr=("zoom",0.45)),
"M05":dict(style="dip_straight",bg=("green","lime"),tr=("flash",0.3)),
"M06":dict(style="circle",bg="orange",fx=["confetti_slow"],tr=("cross",0.4)),
"M07":dict(style="full",fx=["leak_soft"],tr=("whip",0.35)),
"M08":dict(style="full",fx=["rgbpulse","flashbeat","shake"],tr=("whip",0.3)),
"M09":dict(style="full",fx=["ring","stickers_star"],tr=("cut",0.0)),
"M10":dict(style="dip_slant",bg=("blue","navy"),tr=("glitch",0.2)),
"M11":dict(style="full",fx=["confetti","ring"],tr=("zoom",0.45)),
"M12":dict(style="dip_straight",bg=("orange","pink"),tr=("flash",0.2)),
"M13":dict(style="card",bg=("orange","pink"),tilt=4,fx=["shapes"],tr=("circle",0.35)),
"M14":dict(style="full",fx=["vhs","rgbpulse"],tr=("whipL",0.25)),
"M15":dict(style="circle",bg="green",fx=["shapes"],tr=("diag",0.3)),
"M16":dict(style="full",fx=["confetti","ring"],tr=("whip",0.25)),
"M17":dict(style="dip_slant",bg=("lime","green"),flip=True,tr=("cut",0.0)),
"M18":dict(style="full",fx=["leak","ring","stickers_spark"],tr=("circle",0.4)),
"M19":dict(style="card",bg=("pink","blue"),tilt=-4,fx=["shapes"],tr=("flash",0.2)),
"M20":dict(style="full",fx=["glitch"],tr=("glitch",0.2)),
"M21":dict(style="dip_straight",bg=("blue","lime"),tr=("blinds",0.3)),
"M22":dict(style="full",fx=["confetti","stickers_heart","ring"],tr=("zoom",0.4)),
"M23":dict(style="full",fx=["duotone_orange","rgbpulse"],tr=("cut",0.0)),
"M24":dict(style="circle",bg="blue",fx=["shapes"],tr=("diagO",0.3)),
"M25":dict(style="card",bg=("sun","orange"),tilt=3,fx=["shapes"],tr=("glitch",0.2)),
"M26":dict(style="full",fx=["leak"],tr=("cross",0.6)),
"M27":dict(style="dip_straight",bg=("lime","blue"),fx=["bokeh"],tr=("cross",0.6)),
"M28":dict(style="card_video",bg=("navy","blue"),tilt=0,fx=["bokeh"],tr=("cross",0.5)),
"M29":dict(style="dip_slant",bg=("navy","pink"),fx=["bokeh"],tr=("cross",0.5)),
"M30":dict(style="full",fx=["leak_soft"],tr=("cross",0.5)),
"M31":dict(style="full",fx=["bokeh"],tr=("cross",0.6)),
"M32":dict(style="full",fx=["leak_soft"],tr=("flash",0.25)),
"M33":dict(style="dip_straight",bg=("orange","sun"),fx=["bokeh"],tr=("cross",0.6)),
"M34":dict(style="full",fx=["bokeh"],tr=("cross",0.6)),
"M35":dict(style="full",fx=["leak_soft"],tr=("circle",0.6)),
"C01":dict(style="night",bg=("navy","blue"),tr=("cross",0.8)),
"C02":dict(style="night",bg=("navy","pink"),tr=("cross",0.7)),
"C03":dict(style="night",bg=("navy","green"),tr=("cross",0.7)),
"L01":dict(style="logo",tr=("cross",0.6)),
}
FOC={24:(0.5,0.42),26:(0.55,0.4),58:(0.55,0.45),63:(0.6,0.5),13:(0.5,0.55),14:(0.5,0.6),36:(0.5,0.5),65:(0.5,0.55),55:(0.5,0.5),
 71:(0.5,0.55),62:(0.5,0.4),16:(0.5,0.55),3:(0.5,0.6),48:(0.5,0.5),6:(0.5,0.55)}
CROPB={42:0.09,60:0.07}
# ---------- טעינת תמונות + גריידינג צעיר ("pop")
_img_cache={}
def grade_pop(bgr):
    hsv=cv2.cvtColor(bgr,cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[...,1]=np.clip(hsv[...,1]*1.22,0,255); hsv[...,2]=np.clip(hsv[...,2]*1.04+3,0,255)
    o=cv2.cvtColor(hsv.astype(np.uint8),cv2.COLOR_HSV2BGR).astype(np.float32)
    o=(o-128)*1.10+128; o[...,2]*=1.03; o[...,0]*=0.98   # חמימות קלה
    return np.clip(o,0,255).astype(np.uint8)
def load(i):
    if i in _img_cache: return _img_cache[i]
    from PIL import Image,ImageOps
    im=ImageOps.exif_transpose(Image.open(f"{SCR}/{files_rel[i]}")).convert('RGB')
    a=cv2.cvtColor(np.array(im),cv2.COLOR_RGB2BGR)
    if max(a.shape[:2])>2300: s=2300/max(a.shape[:2]); a=cv2.resize(a,None,fx=s,fy=s,interpolation=cv2.INTER_AREA)
    if i in CROPB: a=a[:int(a.shape[0]*(1-CROPB[i]))]
    a=grade_pop(a); _img_cache[i]=a; return a
_vid=None
def video_frame(t):
    global _vid
    if _vid is None:
        cap=cv2.VideoCapture(f"{SCR}/src/מוזיקה/WhatsApp_Video_2026-07-30_at_19.03.17.mp4"); fr=[]
        while len(fr)<int(4.2*30):
            ok,f=cap.read()
            if not ok: break
            fr.append(grade_pop(f))
        _vid=fr
    return _vid[min(len(_vid)-1,int(t*30))]
# ---------- מצלמה: מחזיר BGR בגודל (ow,oh)
def cam(img,ow,oh,z=1.0,panx=0.0,pany=0.0,foc=(0.5,0.45)):
    h,w=img.shape[:2]; sc=max(ow/w,oh/h)*z
    tlx=ow/2+panx-sc*foc[0]*w; tly=oh/2+pany-sc*foc[1]*h
    tlx=min(0,max(ow-sc*w,tlx)); tly=min(0,max(oh-sc*h,tly))
    M=np.float32([[sc,0,tlx],[0,sc,tly]])
    return cv2.warpAffine(img,M,(ow,oh),flags=cv2.INTER_AREA if sc<0.8 else cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
def camera_params(kind,t,d):
    x=clamp(t/d if d>0 else 1)
    if kind=="push": return 1.0+0.13*e_io(x),0,0
    if kind=="pull": return 1.14-0.14*e_io(x),0,0
    if kind=="panR": return 1.10,(0.04-0.08*e_io(x))*W,0
    if kind=="panL": return 1.10,(-0.04+0.08*e_io(x))*W,0
    if kind=="punch": return 1.0+0.07*e_out(x),0,0
    if kind=="hold": return 1.0+0.035*x,0,0
    if kind=="dim": return 1.05+0.06*x,0,0
    return 1.0,0,0
def beat_pulse(tabs):
    from scenes import start
    if not (start('M08')<=tabs<start('M27')): return 0.0
    ph=(tabs/BEAT)%1.0; return max(0,1-ph/0.28)
# ---------- שכבות ביניים לפי סגנון
def S_by_id(): return {s[0]:s for s in SCENES}
SB=S_by_id()
def scene_start(sid):
    t=0
    for s in SCENES:
        if s[0]==sid: return t
        t+=s[2]
def render_full(sid,s,t,tabs):
    i=s[3][0]; z,px,py=camera_params(s[5],t,s[2]); z*=1+0.012*beat_pulse(tabs)
    return cam(load(i),W,H,z,px,py,FOC.get(i,(0.5,0.45)))
def bgfill(c,t,seed=1):
    f=gradient(c[0],c[1],35+10*math.sin(t*0.4)).copy(); return f
def render_card(sid,s,t,tabs,cfg,video=False):
    f=bgfill(cfg['bg'],t); floating_shapes(f,t+tabs*0.0,hash(sid)%1000,n=16)
    if video: src=video_frame(t); cw,ch=1240,700
    else:
        i=s[3][0]; src=load(i); portrait=src.shape[0]>src.shape[1]*1.05; cw,ch=((700,900) if portrait else (1200,780))
    z=1.03+0.07*clamp(t/s[2])
    foc=FOC.get(s[3][0],(0.5,0.45)) if not video else (0.5,0.5)
    img=cam(src,cw,ch,z,0,0,foc)
    pad=22; bot=70 if not video else 22
    pol=np.full((ch+pad+bot,cw+2*pad,3),250,np.uint8); pol[pad:pad+ch,pad:pad+cw]=img
    a=np.dstack([pol,np.full(pol.shape[:2],255,np.uint8)])
    spr=np.dstack([a[...,2],a[...,1],a[...,0],a[...,3]])   # -> RGBA for blit
    # shadow
    sh=np.zeros((spr.shape[0]+120,spr.shape[1]+120,4),np.uint8); sh[...,3]=0
    sh[70:70+spr.shape[0],70:70+spr.shape[1],3]=120; sh=cv2.GaussianBlur(sh,(0,0),22)
    p_in=e_back(clamp(t/0.5),1.4); cx=W/2; cy=(H*0.40 if video else H*0.46)+ (1-p_in)*H*0.9
    tilt=cfg.get('tilt',0)*(0.4+0.6*e_out(clamp(t/0.5)))+math.sin(t*1.4)*0.8
    blit(f,sh,cx+8,cy+22,1.0,tilt,0.9)
    blit(f,spr,cx,cy,1.0,tilt,1.0)
    # tape
    tape=np.zeros((70,200,4),np.uint8); tape[...]=(255,235,140,200)
    blit(f,tape,cx-30,cy-(ch+pad+bot)/2+6,1.0,tilt+8,0.9)
    return f
def render_circle(sid,s,t,tabs,cfg):
    c=PALETTE[cfg['bg']]; f=np.full((H,W,3),(c[2],c[1],c[0]),np.uint8)
    # רקע טבעות
    for k in range(5):
        r=int(250+k*190+ (t*60)%190); cv2.circle(f,(W//2,H//2),r,(255,255,255),6,cv2.LINE_AA) if k%2==0 else None
    ov=f.copy(); 
    for k in range(5): cv2.circle(ov,(W//2,H//2),int(250+k*190+(t*60)%190),(255,255,255),-1) if False else None
    floating_shapes(f,t,hash(sid)%1000,n=18,colors=('white','sun','lime','pink'))
    i=s[3][0]; src=load(i); D=860; z=1.05+0.08*clamp(t/s[2])
    img=cam(src,D,D,z,0,0,FOC.get(i,(0.5,0.42)))
    mask=np.zeros((D,D),np.uint8); cv2.circle(mask,(D//2,D//2),D//2-6,255,-1,cv2.LINE_AA)
    spr=np.dstack([img[...,2],img[...,1],img[...,0],mask])
    ringimg=np.zeros((D+60,D+60,4),np.uint8); cv2.circle(ringimg,((D+60)//2,(D+60)//2),D//2+10,(255,255,255,255),14,cv2.LINE_AA)
    ps=e_back(clamp(t/0.45),1.6); 
    blit(f,ringimg,W/2,H/2-10,ps,t*25,1.0); 
    dash=np.zeros((D+120,D+120,4),np.uint8)
    for a0 in range(0,360,18): cv2.ellipse(dash,((D+120)//2,(D+120)//2),(D//2+45,D//2+45),0,a0,a0+9,(255,225,90,255),8,cv2.LINE_AA)
    blit(f,dash,W/2,H/2-10,ps,-t*40,0.95)
    blit(f,spr,W/2,H/2-10,ps,0,1.0)
    return f
def panel(i,w,h,t,d,zin=True):
    src=load(i); x=clamp(t/d); z=(1.0+0.10*x) if zin else (1.12-0.10*x)
    return cam(src,w,h,z,0,0,FOC.get(i,(0.5,0.4)))
def render_dip(sid,s,t,tabs,cfg,slant):
    c=cfg['bg']; f=bgfill(c,t); a,b=s[3][0],s[3][1]; 
    if cfg.get('flip'): a,b=b,a
    sk=140 if slant else 0; gap=12
    pe=e_out(clamp(t/0.4))
    # panel B (right)
    wB=W//2+sk+gap; B=panel(b,wB,H,t,s[2],False)
    off=int((1-pe)*H)
    right=np.full((H,W,3),0,np.uint8); right[:]=f
    xB=W-wB
    ob=np.roll(B,off,axis=0) if off>0 else B
    if off>0: ob[:off]=f[:off,xB:]
    right[:,xB:]=ob
    wA=W//2+sk+gap; A=panel(a,wA,H,t,s[2],True); oa=np.roll(A,-off,axis=0) if off>0 else A.copy()
    if off>0: oa[H-off:]=f[H-off:,:wA]
    out=right
    mask=np.zeros((H,W),np.uint8)
    poly=np.array([[0,0],[W//2+sk//2,0],[W//2-sk//2,H],[0,H]],np.int32) if slant else np.array([[0,0],[W//2-gap//2,0],[W//2-gap//2,H],[0,H]],np.int32)
    cv2.fillConvexPoly(mask,poly,255,cv2.LINE_AA)
    left=np.zeros((H,W,3),np.uint8); left[:,:wA]=oa
    m=(mask[...,None]/255.).astype(np.float32); out=(out*(1-m)+left*m).astype(np.uint8)
    # stripe
    col=PALETTE['white']
    if slant: cv2.line(out,(W//2+sk//2+4,0),(W//2-sk//2+4,H),(col[2],col[1],col[0]),gap,cv2.LINE_AA)
    else: cv2.line(out,(W//2,0),(W//2,H),(col[2],col[1],col[0]),gap)
    return out
def render_dim(sid,s,t,tabs,dim=0.32):
    i=s[3][0]; z,px,py=camera_params("dim",t,s[2]); f=cam(load(i),W,H,z,px,py,FOC.get(i,(0.5,0.45)))
    f=cv2.GaussianBlur(f,(0,0),3.2); f=(f.astype(np.float32)*dim+np.array([40,22,10])*0.35).astype(np.uint8)
    bokeh(f,tabs,hash(sid)%100,alpha=0.18); return f
def render_night(sid,s,t,tabs):
    f=gradient(*CFG[sid]['bg'],60).copy(); f=(f.astype(np.float32)*(0.55+0.15*math.sin(t))).astype(np.uint8)
    bokeh(f,tabs,3,n=30,alpha=0.3)
    for k in range(8): blit(f,shape_sprite('spark','white',70),(k*277+t*30)%W,(k*131*2+ (t*-40))%H,scale=0.4+0.2*math.sin(t*3+k),angle=t*30,alpha=0.5)
    return f
# ---------- לוגו
LOGO_H={};LOGO_M={}
SC_M=0.50
def load_logo(d,store):
    if store: return
    for fn in os.listdir(d): store[fn[:-4]]=np.array(__import__('PIL.Image',fromlist=['x']).open(f"{d}/{fn}").convert('RGBA'))
def logo_bg(t):
    f=np.full((H,W,3),255,np.uint8)
    ov=f.copy()
    for k,(cn,x,y,r) in enumerate([('blue',320,200,260),('orange',1650,300,200),('green',1500,950,300),('pink',260,900,180),('lime',960,120,150)]):
        c=PALETTE[cn]; cv2.circle(ov,(int(x+30*math.sin(t*0.6+k)),int(y+25*math.cos(t*0.5+k))),r,(c[2],c[1],c[0]),-1,cv2.LINE_AA)
    cv2.addWeighted(ov,0.10,f,0.90,0,f); return f
def place_layer(f,spr,anchor,scale,t_off,x_off=0,y_off=0,alpha=1.0,angle=0,sx=None,sy=None,bb=None):
    """מצייר שכבת לוגו שהיא PNG בגודל מלא; (anchor)=מרכז הלוגו בקואורדינטות מקור -> מסך"""
    pass
def draw_logo(f,layers,order,size,center,t,sched,exit_t=None,exit_dir=1,extra=None,hide=()):
    """layers: dict name->RGBA(full size). sched: name->(start,dur,effect). t בתוך האנימציה.
    center: מרכז מסך של מרכז הלוגו; size: (w,h) מקור; פועל בקנה מידה uniform 'scale'."""
    pass
def logo_scene_hb(f,t,center,scale,progress_t,out_t=None,back_t=None):
    """הרכבת/פירוק לוגו הר ברכה. progress_t=שניות מתחילת הבנייה."""
    load_logo(f"{SCR}/logo_h",LOGO_H); Wl,Hl=932,933
    SCH={'hill':(0.00,0.55,'rise'),'bldg_back':(0.25,0.45,'drop'),'bldg_orange':(0.30,0.5,'drop'),'tower':(0.35,0.55,'drop'),'tree_left':(0.65,0.45,'grow'),
     'tree_pink':(0.7,0.5,'grow'),'tree_right':(0.8,0.45,'grow'),'house':(0.95,0.45,'pop'),'kids':(1.15,0.55,'jump'),'book':(1.35,0.5,'pop'),'text_name':(1.6,0.6,'slideR'),'text_sub':(1.95,0.5,'fade')}
    for n,spr in LOGO_H.items():
        st,du,eff=SCH.get(n,(0,0.4,'pop')); x=clamp((progress_t-st)/du)
        if x<=0: continue
        e=e_back(x,1.5) if eff in('pop','jump','grow','drop','rise') else e_out(x)
        sx=sy=scale; dx=dy=0; ang=0; al=1.0
        h,w=spr.shape[:2]; ys,xs=np.where(spr[...,3]>5); cx_l=(xs.min()+xs.max())/2; cy_l=(ys.min()+ys.max())/2
        if eff=='rise': dy=(1-e)*500*scale
        elif eff=='drop': dy=-(1-e)*700*scale
        elif eff=='grow': sy=scale*max(0.01,e); 
        elif eff=='pop': sx=sy=scale*max(0.01,e)
        elif eff=='jump': sx=sy=scale*max(0.01,e); dy=-math.sin(math.pi*x)*60*scale
        elif eff=='slideR': dx=(1-e)*600*scale; al=x
        elif eff=='fade': dy=(1-e)*40*scale; al=x
        # יציאה (פרוק) / חזרה
        if out_t is not None:
            xo=clamp((out_t-0.03*list(SCH).index(n))/0.5); eo=e_in(xo); dx+=eo*1900; dy-=eo*220*(1 if list(SCH).index(n)%2 else -1); ang+=eo*40; al*=1-eo*0.2
        if back_t is not None:
            xb=1-clamp((back_t-0.05*list(SCH).index(n))/0.9); eb=e_out(1-xb)
            dx+=(1-eb)*1900; dy-=(1-eb)*220*(1 if list(SCH).index(n)%2 else -1); ang+=(1-eb)*-40
        # הצבה: מרכז הלוגו במקור (466,466) -> center
        px=center[0]+(cx_l-466)*scale+dx; py=center[1]+(cy_l-466)*scale+dy
        crop=spr[int(ys.min()):int(ys.max())+1,int(xs.min()):int(xs.max())+1]
        blit(f,crop,px,py,sx=sx,sy=sy,angle=ang,alpha=al)
def logo_scene_m(f,t,center,scale,progress_t,mode,zoomk=1.0,focus=(1000,400),jump_t=0.0,figpop=1.0):
    """מתנ"ס: מציג שכבות לפי לוח זמנים; zoomk גורם הגדלה סביב focus; """
    load_logo(f"{SCR}/logo_m",LOGO_M)
    SCH={'hill':(0.35,0.55,'rise'),'hill_dark':(0.4,0.5,'rise'),'tree_big':(0.8,0.5,'grow'),'tree_dark':(0.9,0.5,'grow'),'book':(1.2,0.5,'pop'),'sun':(1.55,0.55,'pop'),
         'arc':(1.8,0.7,'draw'),'heart':(2.5,0.5,'pop'),'text_matnas':(2.7,0.55,'rise2'),'text_harbracha':(3.05,0.5,'fade')}
    FIG=['person_orange','person_blue','child']
    # סדר ציור: שכבות אחורה->קדימה
    order=['sun','arc','tree_big','tree_dark','book','hill_dark','hill','heart','person_orange','child','person_blue','text_matnas','text_harbracha']
    s_eff=scale*zoomk
    for n in order:
        spr=LOGO_M.get(n)
        if spr is None: continue
        ys,xs=np.where(spr[...,3]>5)
        if len(ys)==0: continue
        cx_l=(xs.min()+xs.max())/2; cy_l=(ys.min()+ys.max())/2
        crop=spr[int(ys.min()):int(ys.max())+1,int(xs.min()):int(xs.max())+1]
        al=1.0; dx=dy=0; sx=sy=s_eff; ang=0
        if n in FIG:
            # קפיצות שמחה: כל דמות בפאזה אחרת
            ph={'person_orange':0.0,'person_blue':0.33,'child':0.66}[n]
            j=abs(math.sin(math.pi*((jump_t/0.6)+ph)))
            lift=j*(70 if n!='child' else 95)*(1.0 if zoomk>1.5 else 0.35)
            dy=-lift*s_eff/ max(scale,1e-3)*scale*0.0 - lift*(s_eff/ (scale if scale else 1))*0.5*scale
            sy=s_eff*(1+0.05*(1-j))*max(0.01,figpop); sx=s_eff*(1-0.03*(1-j))*max(0.01,figpop)
            if figpop<=0.01: continue
        else:
            st,du,eff=SCH[n]; x=clamp((progress_t-st)/du)
            if x<=0: continue
            e=e_back(x,1.5)
            if eff=='rise': dy=(1-e)*420*s_eff/scale*scale*0.0+(1-e)*420*s_eff
            elif eff=='rise2': dy=(1-e)*160*s_eff; al=clamp(x*2)
            elif eff=='grow': sy=s_eff*max(0.01,e)
            elif eff=='pop': sx=sy=s_eff*max(0.01,e)
            elif eff=='fade': al=x; dy=(1-x)*30*s_eff
            elif eff=='draw':
                # חשיפה זוויתית של הקו המקווקו
                pass
        # מיקום: המרה של מרכז המקור ביחס ל-focus
        px=center[0]+(cx_l-focus[0])*s_eff+dx; py=center[1]+(cy_l-focus[1])*s_eff+dy
        if n=='arc':
            x=clamp((progress_t-SCH['arc'][0])/SCH['arc'][1])
            if x<=0: continue
            h,w=crop.shape[:2]; yy,xx=np.mgrid[0:h,0:w]
            gx=xs.min(); gy=ys.min(); ccx,ccy=1090-gx,440-gy
            ang_=(np.degrees(np.arctan2(yy-ccy,xx-ccx))+90)%360   # 0 למעלה, עם כיוון השעון
            m=(ang_<=x*360*0.78+8).astype(np.uint8)
            crop=crop.copy(); crop[...,3]=crop[...,3]*m
        blit(f,crop,px,py,sx=sx,sy=sy,angle=ang,alpha=al)
def render_logo(sid,t,tabs):
    import logo_anim; return logo_anim.render(t,tabs)
# ---------- הרכבת סצנה
def render_scene(sid,t,tabs,idx=0):
    s=SB[sid]; cfg=CFG[sid]; st=cfg['style']; d=s[2]; t=clamp(t,0,d)
    if st=="full": f=render_full(sid,s,t,tabs)
    elif st=="card": f=render_card(sid,s,t,tabs,cfg)
    elif st=="card_video": f=render_card(sid,s,t,tabs,cfg,video=True)
    elif st=="circle": f=render_circle(sid,s,t,tabs,cfg)
    elif st=="dip_slant": f=render_dip(sid,s,t,tabs,cfg,True)
    elif st=="dip_straight": f=render_dip(sid,s,t,tabs,cfg,False)
    elif st=="dim": f=render_dim(sid,s,t,tabs)
    elif st=="night": f=render_night(sid,s,t,tabs)
    elif st=="logo": return render_logo(sid,t,tabs)
    fxs=cfg.get('fx',[]); fi=int(tabs*FPS)
    for e in fxs:
        if e=="leak": f=light_leak(f,tabs,0.32)
        elif e=="leak_soft": f=light_leak(f,tabs,0.18,('sun','orange'))
        elif e=="rgbpulse":
            bp=beat_pulse(tabs); f=rgb_split(f,int(16*bp)) if bp>0 else f
        elif e=="flashbeat": f=flash(f,0.35*beat_pulse(tabs))
        elif e=="shake": f=shake(f,fi,int(9*max(0,1-t/0.7))+2)
        elif e=="glitch":
            if (fi%7)<3: f=glitch(f,fi,0.9)
        elif e=="duotone_blue": f=duotone(f,'navy','sun' ,0.85*max(0,1-t/0.28)) if False else duotone(f,'navy','blue',0.9*max(0,1-t/0.3))
        elif e=="duotone_orange": f=duotone(f,'pink','sun',0.9*max(0,1-t/0.3))
        elif e=="vhs": f=vhs(f,fi)
        elif e=="confetti": confetti(f,t,int(hash(sid)%1000),n=80,fall=650)
        elif e=="confetti_slow": confetti(f,t,int(hash(sid)%1000),n=40,fall=260)
        elif e=="ring":
            ring_burst(f,W/2,H/2,clamp(t/0.5),'white',1000,28,0.8)
            ring_burst(f,W/2,H/2,clamp((t-0.15)/0.5),'sun',1000,16,0.7)
        elif e=="sparkle":
            for k in range(7): blit(f,shape_sprite('spark','white',60),(k*311+tabs*35)%W,(k*177+200-tabs*28)%H,scale=0.35+0.25*math.sin(tabs*3+k),angle=tabs*40,alpha=0.85)
        elif e=="stickers_star":
            for k,(x,y) in enumerate([(300,250),(1650,260),(1500,820),(250,800)]):
                p=e_back(clamp((t-0.1*k)/0.35),2.0); blit(f,shape_sprite('star',BR[k],90),x,y,scale=p*0.9,angle=math.sin(tabs*3+k)*14+k*20)
        elif e=="stickers_spark":
            for k,(x,y) in enumerate([(280,230),(1660,240),(1620,860),(300,850)]):
                p=e_back(clamp((t-0.15*k)/0.4),2.0); blit(f,shape_sprite('spark',('sun','white','pink','lime')[k],90),x,y,scale=p*1.0,angle=tabs*40)
        elif e=="stickers_heart":
            for k in range(8):
                p=clamp((t-0.12*k)/1.8); 
                if 0<p<1: blit(f,shape_sprite('heart',('pink','orange','white')[k%3],80),300+k*190+math.sin(t*3+k)*40,H*0.9-p*H*0.8,scale=0.8*(0.6+0.5*math.sin(math.pi*p)),angle=math.sin(t*2+k)*18,alpha=1-p*0.7)
        elif e=="shapes": floating_shapes(f,tabs,hash(sid)%1000,n=10,alpha=0.35)
        elif e=="bokeh": bokeh(f,tabs,hash(sid)%100,alpha=0.18)
        elif e=="eq":
            for k in range(14):
                h=int(40+160*abs(math.sin(tabs*4+k*0.8)*math.cos(tabs*2.3+k))); x=W//2-460+k*70
                cv2.rectangle(f,(x,H-120-h),(x+34,H-120),PALETTE['sun'][::-1],-1)
    return f
# ---------- טקסטים (ציר זמן גלובלי)
from scenes import start as _st
def _T(**k):
    sid=k.pop('sid'); o=k.pop('o'); d=k.pop('d'); k['t0']=_st(sid)+o; k['t1']=k['t0']+d; return k
TEXTS=[
 _T(sid="M01",o=0.4,d=2.5,txt="שנת תשפ\"ו במתנ\"ס",kind="pill",col='orange',size=104,pos=(W/2,H*0.84)),
 _T(sid="M02",o=0.3,d=2.1,txt="הכול מתחיל בסקרנות",kind="pill",col='blue',size=100,pos=(W/2,H*0.88)),
 _T(sid="M05",o=0.0,d=3.4,txt="ידיים קטנות, חלומות גדולים",kind="pill",col='pink',size=96,pos=(W/2,H*0.88)),
 _T(sid="M08",o=0.05,d=2.8,txt="ואז זה מתחיל לזוז",kind="big",col='orange',size=170,pos=(W/2,H*0.78)),
 _T(sid="M11",o=0.0,d=2.6,txt="600+",sub="משתתפים בחוגים",kind="counter",col='green',num=600,pos=(W/2,H*0.5)),
 _T(sid="M16",o=0.0,d=2.9,txt="500",sub="ילדים בקייטנות הקיץ",kind="counter",col='orange',num=500,pos=(W/2,H*0.5)),
 _T(sid="M26",o=0.1,d=2.8,txt="מתחברים ביחד",kind="pill",col='green',size=108,pos=(W/2,H*0.85)),
 _T(sid="M27",o=0.1,d=2.3,txt="לומדים. יוצרים. גדלים.",kind="pill",col='blue',size=96,pos=(W/2,H*0.88)),
 _T(sid="M28",o=0.1,d=2.8,txt="70",sub="תלמידי מוזיקה",kind="counter",col='pink',num=70,pos=(W/2,H*0.84),small=True),
 _T(sid="M29",o=0.0,d=2.0,txt="בבניין החדש",kind="pill",col='pink',size=100,pos=(W/2,H*0.88)),
 _T(sid="M30",o=0.0,d=2.0,txt="ספרים, צלילים, צבעים",kind="pill",col='orange',size=96,pos=(W/2,H*0.88)),
 _T(sid="M34",o=0.1,d=3.7,txt="הקהילה שלנו",kind="pill",col='blue',size=110,pos=(W/2,H*0.88)),
 _T(sid="C01",o=0.2,d=2.6,txt="תודה על שנה מדהימה",kind="end",size=118,pos=(W/2,H*0.5)),
 _T(sid="C02",o=0.2,d=2.6,txt="והשנה החדשה כבר כאן",kind="end",size=112,pos=(W/2,H*0.5)),
 _T(sid="C03",o=0.2,d=3.6,txt="תקופת השינויים בחוגים",sub="עד יום רביעי 07/10  ·  הקישור בהודעה",kind="end",size=116,pos=(W/2,H*0.45),accent=True),
]
def draw_text(f,tabs):
    for T in TEXTS:
        if not (T['t0']-0.01<=tabs<=T['t1']): continue
        t=tabs-T['t0']; dur=T['t1']-T['t0']; tout=clamp((dur-t)/0.3)
        k=T['kind']; col=PALETTE[T['col']] if 'col' in T else None
        if k=="pill":
            spr=text_sprite(T['txt'],T['size'],(255,255,255),col,pad=(54,24))
            p=e_back(clamp(t/0.45),1.8); y=T['pos'][1]+(1-p)*120
            blit(f,spr,T['pos'][0],y,scale=0.5+0.5*p if False else max(0.01,p),angle=-2.5+math.sin(tabs*2)*0.6,alpha=tout)
        elif k=="big":
            spr=text_sprite(T['txt'],T['size'],(255,255,255),None,outline=(10,col),pad=(20,10))
            p=e_elastic(clamp(t/0.7)); sh=1+0.03*math.sin(tabs*28)*max(0,1-t/1.2)
            blit(f,spr,T['pos'][0],T['pos'][1],scale=max(0.01,p)*sh,angle=-3+math.sin(tabs*3)*1.2,alpha=tout)
        elif k=="counter":
            x=clamp(t/0.9); n=int(T['num']*e_out(x)); s=("%d"%n)+("+" if T['txt'].endswith('+') and x>=1 else "")
            big=170 if T.get('small') else 260
            cy=T['pos'][1]-(40 if T.get('small') else 70)
            numspr=text_sprite(s,big,(255,255,255),None,outline=(12,col),pad=(20,5),direction='ltr')
            subspr=text_sprite(T['sub'],84 if T.get('small') else 96,(255,255,255),col,pad=(50,20))
            pe=e_elastic(clamp(t/0.6))
            blit(f,numspr,T['pos'][0],cy,scale=max(0.01,pe),angle=-4,alpha=tout)
            ps=e_back(clamp((t-0.25)/0.45),1.6); blit(f,subspr,T['pos'][0],cy+(150 if T.get('small') else 220)+(1-ps)*80,scale=max(0.01,ps),angle=-1.5,alpha=tout)
        elif k=="end":
            a=e_out(clamp(t/0.6))*clamp((dur-t)/0.5)
            spr=text_sprite(T['txt'],T['size'],(255,255,255),None,shadow=True,pad=(10,6),wght=700)
            y=T['pos'][1]+(1-e_out(clamp(t/0.8)))*30
            if T.get('accent'):
                # פס צבעוני מתחת
                w=int(spr.shape[1]*0.82*e_out(clamp((t-0.3)/0.8)))
                if w>5: cv2.rectangle(f,(int(W/2-w/2),int(y+spr.shape[0]*0.38)),(int(W/2+w/2),int(y+spr.shape[0]*0.38)+10),PALETTE['orange'][::-1],-1)
            blit(f,spr,T['pos'][0],y,scale=1.0+0.02*(t/dur),alpha=a)
            if T.get('sub'):
                a2=e_out(clamp((t-0.5)/0.6))*clamp((dur-t)/0.5)
                sp2=text_sprite(T["sub"],72,(255,200,90),None,shadow=True,pad=(10,6),wght=700)
                blit(f,sp2,T['pos'][0],y+spr.shape[0]*0.95+(1-e_out(clamp((t-0.5)/0.8)))*20,alpha=a2)
# ---------- מסגרת ראשית
TIMES=[]; _t=0
for s in SCENES: TIMES.append((s[0],_t,_t+s[2])); _t+=s[2]
def frame_at(fi):
    tabs=fi/FPS; tabs=min(tabs,TOTAL-1e-6)
    k=next(i for i,(sid,a,b) in enumerate(TIMES) if a<=tabs<b)
    sid,a,b=TIMES[k]; t=tabs-a; cfg=CFG[sid]
    f=render_scene(sid,t,tabs,fi)
    ttype,td=cfg['tr']
    if k>0 and td>0 and t<td:
        pid=TIMES[k-1][0]; A=render_scene(pid,SB[pid][2],tabs,fi); p=t/td
        if ttype=="iris": f=tr_iris_black(f,p)
        else: f=TRANS[ttype](A,f,p)
    elif k==0 and ttype=="iris":
        f=tr_iris_black(f,clamp(t/td))
    draw_text(f,tabs)
    # פעימה: הבזק עדין + גריידינג
    if sid.startswith("L"): 
        if sid=="L03" and t>3.0: pass
        return f
    f=final_grade(f,fi)
    if tabs>106.5: pass
    return f
if __name__=="__main__":
    import cv2
    ts=[float(x) for x in sys.argv[1:]]
    for tt in ts:
        fr=frame_at(int(tt*FPS)); cv2.imwrite(f"{SCR}/prev_{tt:06.2f}.jpg",fr)
