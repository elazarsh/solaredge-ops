# -*- coding: utf-8 -*-
"""רצף לוגואים: שני הלוגואים מתחילים יחד בסצנה משותפת, הילדים חיים (פנים, צל, תנועה),
ואז הסצנה מתפצלת על המסך לשני לוגואים והדמויות 'משטחות' לקווים כמו בלוגו."""
import numpy as np, cv2, math, os
from PIL import Image
from fx import *
LM={};LH={}
def _load(d,store):
    for fn in os.listdir(d):
        a=np.array(Image.open(f"{d}/{fn}").convert('RGBA')); ys,xs=np.where(a[...,3]>5)
        if len(ys)==0: continue
        x0,x1,y0,y1=xs.min(),xs.max()+1,ys.min(),ys.max()+1
        store[fn[:-4]]=dict(img=a[y0:y1,x0:x1].copy(),c=((x0+x1)/2.,(y0+y1)/2.),bb=(int(x0),int(y0),int(x1),int(y1)))
def init():
    if LM: return
    _load(f"{SCR}/logo_m",LM); _load(f"{SCR}/logo_h",LH); _prep_figs()
# ---------- דמויות חיות
FIG={'person_orange':dict(head=(861,198),r=42,hip=0.58),'person_blue':dict(head=(1172,277),r=43,hip=0.58),'child':dict(head=(963,430),r=35,hip=0.6)}
PAD=60
def _prep_figs():
    for n,F in FIG.items():
        L=LM[n]; img=L['img']; h,w=img.shape[:2]
        pad=np.zeros((h+2*PAD,w+2*PAD,4),np.uint8); pad[PAD:PAD+h,PAD:PAD+w]=img
        a=pad[...,3].copy(); a[pad[...,:3].min(2)>205]=0; pad[...,3]=a; mask=(a>128).astype(np.uint8)
        dist=cv2.distanceTransform(mask,cv2.DIST_L2,5); dn=dist/max(dist.max(),1)
        base=pad[...,:3].astype(np.float32)
        H2,W2=a.shape; yy,xx=np.mgrid[0:H2,0:W2].astype(np.float32)
        shade=0.60+0.62*np.sqrt(dn); lg=1+0.20*(0.5-xx/W2)+0.20*(0.5-yy/H2)
        spec=np.clip((dn**2.5)*0.55,0,0.4)*255
        # הבהוב אור מצד שמאל-עליון
        hl=cv2.GaussianBlur((mask*255).astype(np.float32),(0,0),9); gx=cv2.Sobel(hl,cv2.CV_32F,1,0,ksize=5); gy=cv2.Sobel(hl,cv2.CV_32F,0,1,ksize=5)
        rim=np.clip((-gx-gy)/(np.abs(gx).max()+np.abs(gy).max()+1e-3)*2.2,-0.3,0.5)
        shaded=np.clip(base*shade[...,None]*lg[...,None]+spec[...,None]*0.55+rim[...,None]*70,0,255)
        F['base']=base;F['shaded']=shaded;F['alpha']=a;F['mask']=mask
        F['hc']=(F['head'][0]-L['bb'][0]+PAD,F['head'][1]-L['bb'][1]+PAD)
        F['xx']=xx;F['yy']=yy;F['size']=(W2,H2)
def figure_sprite(n,t,flat,phase,amp=1.0):
    F=FIG[n]; W2,H2=F['size']
    col=F['shaded']*(1-flat)+F['base']*flat
    rgb=np.clip(col,0,255).astype(np.uint8).copy()
    # פנים
    fa=1-flat
    if fa>0.02:
        cx,cy=F['hc']; r=F['r']; jt=abs(math.sin(math.pi*(t/1.0+phase)))
        blink=(t*0.9+phase*3)%2.6<0.12
        ov=rgb.copy(); ey=int(cy-0.08*r); ex=int(0.34*r)
        for sx in (-1,1):
            ex0=int(cx+sx*ex)
            if blink: cv2.line(ov,(ex0-int(.14*r),ey),(ex0+int(.14*r),ey),(30,30,40),max(2,int(.07*r)),cv2.LINE_AA)
            else:
                cv2.ellipse(ov,(ex0,ey),(int(.17*r),int(.22*r)),0,0,360,(255,255,255),-1,cv2.LINE_AA)
                cv2.circle(ov,(ex0+int(.03*r*sx*0),ey+int(.03*r)),int(.09*r),(25,25,40),-1,cv2.LINE_AA)
                cv2.circle(ov,(ex0-int(.03*r),ey-int(.03*r)),max(1,int(.03*r)),(255,255,255),-1,cv2.LINE_AA)
        # לחיים
        for sx in (-1,1): cv2.circle(ov,(int(cx+sx*0.58*r),int(cy+0.28*r)),int(.16*r),(255,150,150),-1,cv2.LINE_AA)
        # פה: חיוך רחב / פה פתוח בקפיצה
        my=int(cy+0.36*r)
        if jt>0.35: 
            cv2.ellipse(ov,(int(cx),my),(int(.30*r),int(.28*r*(0.6+jt*0.6))),0,0,180,(40,25,45),-1,cv2.LINE_AA)
            cv2.ellipse(ov,(int(cx),my+int(.1*r)),(int(.16*r),int(.1*r)),0,0,180,(150,90,200),-1,cv2.LINE_AA)
        else:
            cv2.ellipse(ov,(int(cx),my-int(.05*r)),(int(.30*r),int(.20*r)),0,15,165,(40,25,45),max(2,int(.07*r)),cv2.LINE_AA)
        m=(F['mask'][...,None]>0)
        rgb=np.where(m,(rgb*(1-fa)+ov*fa).astype(np.uint8),rgb)
    spr=np.dstack([rgb,F['alpha']])
    # עיוות 'פיתול' סביב המותניים: זרועות מתנדנדות וגוף מתכופף
    ang_amp=math.radians(7)*amp
    ang=ang_amp*math.sin(2*math.pi*(t/1.0+phase)+0.6)
    py=H2*(PAD/H2+(1-2*PAD/H2)*F['hip']); cxm=W2/2
    yy,xx=F['yy'],F['xx']; k=np.clip((py-yy)/(py+1),0,1)**1.1; a_=ang*k
    dx=xx-cxm; dy=yy-py
    sx=cxm+dx*np.cos(a_)+dy*np.sin(a_); sy=py-dx*np.sin(a_)+dy*np.cos(a_)
    return cv2.remap(spr,sx.astype(np.float32),sy.astype(np.float32),cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=(0,0,0,0))
# ---------- הגדרות פריסה
SM0=0.78; WM0=(960,760)          # מתנ"ס בסצנה המשותפת (עולם)
SH0=0.80; WH0=(1010,400)         # הר ברכה בסצנה המשותפת (רקע)
SC_M=0.50; FM=(W*0.27,H*0.5)     # מתנ"ס סופי
SH_F=0.66; FH=(W*0.73,H*0.5)     # הר ברכה סופי
M_ANCH=(768,683); H_ANCH=(466,466)
def wpos_m(n):
    c=LM[n]['c']; return (WM0[0]+(c[0]-M_ANCH[0])*SM0, WM0[1]+(c[1]-M_ANCH[1])*SM0)
def fpos_m(n):
    c=LM[n]['c']; return (FM[0]+(c[0]-M_ANCH[0])*SC_M, FM[1]+(c[1]-M_ANCH[1])*SC_M)
def wpos_h(n):
    c=LH[n]['c']; return (WH0[0]+(c[0]-H_ANCH[0])*SH0, WH0[1]+(c[1]-H_ANCH[1])*SH0)
def fpos_h(n):
    c=LH[n]['c']; return (FH[0]+(c[0]-H_ANCH[0])*SH_F, FH[1]+(c[1]-H_ANCH[1])*SH_F)
# הופעה (זמן, משך, אפקט) בסצנה המשותפת / בפיצול
APPEAR_M={'person_orange':(0.0,0.5,'popb'),'child':(0.08,0.5,'popb'),'person_blue':(0.16,0.5,'popb'),'hill':(0.3,0.6,'rise'),'hill_dark':(0.35,0.6,'rise'),
 'tree_big':(0.7,0.5,'grow'),'tree_dark':(0.8,0.5,'grow'),'book':(1.0,0.5,'pop'),'sun':(1.2,0.55,'pop'),'arc':(1.4,0.8,'draw'),'heart':(1.9,0.5,'pop')}
APPEAR_H={'tower':(1.0,0.5,'drop'),'bldg_orange':(1.1,0.5,'drop'),'bldg_back':(1.05,0.5,'drop'),'tree_pink':(1.3,0.5,'grow'),'tree_left':(1.4,0.5,'grow'),'tree_right':(1.5,0.5,'grow'),'house':(1.6,0.45,'pop'),'book':(1.75,0.5,'pop')}
SPLIT_T0=3.4
ORDER_H_BACK=['bldg_back','tower','bldg_orange','tree_pink','house','tree_left','tree_right','book']
def draw_layer(f,L,pos,scale,alpha=1.0,angle=0,sx=None,sy=None):
    blit(f,L['img'],pos[0],pos[1],scale=scale,angle=angle,alpha=alpha,sx=sx,sy=sy)
def logo_bg(tabs):
    f=np.full((H,W,3),255,np.uint8); ov=f.copy()
    for k,(cn,x,y,r) in enumerate([('blue',320,200,260),('orange',1650,300,200),('green',1500,950,300),('pink',260,900,180),('lime',960,120,150)]):
        c=PALETTE[cn]; cv2.circle(ov,(int(x+30*math.sin(tabs*0.6+k)),int(y+25*math.cos(tabs*0.5+k))),r,(c[2],c[1],c[0]),-1,cv2.LINE_AA)
    cv2.addWeighted(ov,0.10,f,0.90,0,f); return f
def lerp(a,b,x): return a+(b-a)*x
def render(t,tabs):
    init(); f=logo_bg(tabs)
    # מצלמה
    kz=1.0+1.3*(1-e_io(clamp(t/2.6)))
    fx_=lerp(1121,960,e_io(clamp(t/2.8))); fy_=lerp(585,540,e_io(clamp(t/2.8)))
    def cam(p): return (W/2+(p[0]-fx_)*kz, H/2+(p[1]-fy_)*kz)
    sp=clamp((t-SPLIT_T0)/1.5)                     # התקדמות פיצול כללית
    flat=e_io(clamp((t-SPLIT_T0)/1.8))
    hug=e_io(clamp((t-5.7)/1.0))*0.035*W
    idle=1.0 if t<SPLIT_T0+1.8 else 0.35
    # --- רקע: הר ברכה (נראה כרקע חיוור בסצנה המשותפת, מתמלא בפיצול)
    for n in ORDER_H_BACK:
        L=LH.get(n)
        if L is None: continue
        st,du,eff=APPEAR_H.get(n,(1.0,0.5,'pop')); x=clamp((t-st)/du)
        if x<=0: continue
        e=e_back(x,1.4); sx=sy=1.0; dy=0
        if eff=='drop': dy=-(1-e)*500
        elif eff=='grow': sy=max(0.01,e)
        elif eff=='pop': sx=sy=max(0.01,e)
        sw=SH0*kz; wp=cam(wpos_h(n)); 
        # תנועה לעמדה הסופית
        idx=ORDER_H_BACK.index(n); pe=e_back(clamp((t-SPLIT_T0-idx*0.05)/1.25),1.05)
        fp=fpos_h(n); fp=(fp[0]-hug,fp[1])
        pos=(lerp(wp[0],fp[0],pe),lerp(wp[1],fp[1],pe)+dy*kz*(1-pe)); sc=lerp(sw,SH_F,pe)
        al=lerp(0.42,1.0,e_io(clamp((t-SPLIT_T0)/1.2)))
        ang=math.sin(pe*math.pi)*(-6 if idx%2 else 6)
        draw_layer(f,L,pos,sc,alpha=al,angle=ang,sx=sc*sx,sy=sc*sy)
    # --- הר ברכה: גבעה, ילדים וטקסט, מופיעים בפיצול
    for n,st,du,eff in (('hill',SPLIT_T0+0.2,0.7,'rise'),('kids',SPLIT_T0+0.7,0.6,'pop'),('text_name',SPLIT_T0+1.5,0.7,'slide'),('text_sub',SPLIT_T0+1.9,0.6,'fade')):
        L=LH.get(n); x=clamp((t-st)/du)
        if L is None or x<=0: continue
        e=e_back(x,1.4); fp=fpos_h(n); fp=(fp[0]-hug,fp[1]); sx=sy=SH_F; al=1.0; dx=dy=0
        if eff=='rise': dy=(1-e)*400
        elif eff=='pop': sx=sy=SH_F*max(0.01,e); dy=-math.sin(math.pi*x)*40
        elif eff=='slide': dx=(1-e_out(x))*500; al=x
        elif eff=='fade': dy=(1-x)*40; al=x
        draw_layer(f,L,(fp[0]+dx,fp[1]+dy),SH_F,alpha=al,sx=sx,sy=sy)
    # --- מתנ"ס: שכבות
    ordM=['sun','arc','tree_big','tree_dark','book','hill_dark','hill','heart']
    for n in ordM:
        L=LM.get(n)
        if L is None: continue
        st,du,eff=APPEAR_M[n]; x=clamp((t-st)/du)
        if x<=0: continue
        e=e_back(x,1.5); sx=sy=1.0; dy=0
        if eff=='rise': dy=(1-e)*420
        elif eff=='grow': sy=max(0.01,e)
        elif eff=='pop': sx=sy=max(0.01,e)
        wp=cam(wpos_m(n)); sw=SM0*kz
        idx=ordM.index(n); pe=e_back(clamp((t-SPLIT_T0-idx*0.04)/1.25),1.05)
        fp=fpos_m(n); fp=(fp[0]+hug,fp[1])
        pos=(lerp(wp[0],fp[0],pe),lerp(wp[1],fp[1],pe)+dy*kz*(1-pe)); sc=lerp(sw,SC_M,pe)
        ang=math.sin(pe*math.pi)*(5 if idx%2 else -5)
        draw_layer(f,L,pos,sc,angle=ang,sx=sc*sx,sy=sc*sy)
        if n=='arc':
            pass
    # קו מקווקו: חשיפה זוויתית
    # (מיושם בתוך draw ע"י מסכה)
    # --- צללים ודמויות חיות
    for n,ph in (('person_orange',0.0),('child',0.12),('person_blue',0.26)):
        L=LM[n]; st,du,eff=APPEAR_M[n]; x=clamp((t-st)/du)
        if x<=0: continue
        e=e_elastic(x) if x<1 else 1
        wp=cam(wpos_m(n)); sw=SM0*kz
        idx=['person_orange','child','person_blue'].index(n)+8; pe=e_back(clamp((t-SPLIT_T0-idx*0.04)/1.25),1.05)
        fp=fpos_m(n); fp=(fp[0]+hug,fp[1])
        j=abs(math.sin(math.pi*(t/1.0+ph)));  # קפיצה כל שנייה (2 פעימות)
        jump=j*(0.20*(L['bb'][3]-L['bb'][1])*idle)
        sq=1+0.07*(1-j)*idle; stt=1-0.04*(1-j)*idle
        base=lerp(sw,SC_M,pe); sc=base
        pos=(lerp(wp[0],fp[0],pe),lerp(wp[1],fp[1],pe)-jump*sc)
        # צל על הקרקע
        bot=pos[1]+((L['bb'][3]-L['bb'][1])/2)*sc*0+ (L['bb'][3]-L['bb'][1])/2*sc
        if flat<0.98:
            sh=np.zeros((60,260,4),np.uint8); cv2.ellipse(sh,(130,30),(110,18),0,0,360,(40,40,40,150),-1,cv2.LINE_AA); sh=cv2.GaussianBlur(sh,(0,0),6)
            blit(f,sh,pos[0],bot-8*sc,scale=sc*(0.9+0.5*(1-j))*(L['bb'][2]-L['bb'][0])/260,alpha=(1-flat)*(0.8+0.2*(1-j)))
        spr=figure_sprite(n,t,flat,ph,amp=idle)
        s_=e if x<1 else 1.0
        blit(f,spr,pos[0],pos[1],sx=sc*stt*max(0.01,s_),sy=sc*sq*max(0.01,s_),angle=math.sin(2*math.pi*(t/1.0+ph))*2.0*idle)
    # --- טקסטים של מתנ"ס
    for n,st,du,eff in (('text_matnas',SPLIT_T0+1.3,0.6,'pop'),('text_harbracha',SPLIT_T0+1.8,0.6,'fade')):
        L=LM.get(n); x=clamp((t-st)/du)
        if L is None or x<=0: continue
        e=e_back(x,1.5); fp=fpos_m(n); fp=(fp[0]+hug,fp[1]); sx=sy=SC_M; al=1.0; dy=0
        if eff=='pop': sx=sy=SC_M*max(0.01,e); al=clamp(x*2)
        else: dy=(1-x)*30; al=x
        draw_layer(f,L,(fp[0],fp[1]+dy),SC_M,alpha=al,sx=sx,sy=sy)
    # --- אפקטים
    if t<0.2: f=flash(f,0.5*(1-t/0.2))
    if SPLIT_T0<=t<SPLIT_T0+0.9:
        x=(t-SPLIT_T0)/0.9; hgt=int(H*e_out(x)); 
        bar=np.zeros((H,40,4),np.uint8); bar[...,:3]=(255,255,255); bar[...,3]=255
        ov=f.copy(); cv2.rectangle(ov,(W//2-int(14*(1-x)),H//2-hgt//2),(W//2+int(14*(1-x)),H//2+hgt//2),(255,230,160),-1)
        a_=0.8*(1-x); cv2.addWeighted(ov,a_,f,1-a_,0,f)
        ring_burst(f,W/2,H/2,x,'sun',1200,30,0.6)
    if 4.5<t<7.0:
        for k in range(16):
            a=k*0.7+t*2.2; r=70+60*math.sin(t*3+k); col=('orange','blue','green','pink','lime')[k%5]
            blit(f,shape_sprite('spark',col,50),W/2+math.cos(a)*r*0.6,H/2+math.sin(a)*r*3.4-10,scale=0.55*clamp((t-4.5)*2)*max(0,1-(t-6.2)/0.9),angle=t*120)
    if t>5.9: cv2.line(f,(W//2,int(H*0.26)),(W//2,int(H*0.74)),(170,170,170),3,cv2.LINE_AA)
    if t>8.3: f=flash(f,e_io((t-8.3)/0.7)*0.98)
    return f
