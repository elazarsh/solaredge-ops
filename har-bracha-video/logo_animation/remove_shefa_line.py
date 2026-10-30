import cv2,numpy as np,os,subprocess
pts=[(6.6,640),(6.7,622),(6.8,608),(6.92,598),(7.0,588),(7.08,580),(7.17,572),(7.25,564),(7.33,556),(7.5,548),(7.58,544),(7.67,540),(7.75,534),(7.83,530),(8.0,530),(8.25,528),(8.5,524),(9.0,525),(9.25,520),(9.5,516),(9.75,514),(10.0,514)]
T=np.array([p[0] for p in pts]); Y=np.array([p[1] for p in pts],float)
def ymax(t): return float(np.interp(t,T,Y))
X0,X1=380,900
L1=[(6.8,500),(7.0,511),(7.1,520),(7.2,536),(7.3,531),(7.5,521),(7.75,513),(8.0,509),(8.5,503),(9.0,497),(10.0,495)]
LT=np.array([p[0] for p in L1]); LY=np.array([p[1] for p in L1],float)
def smooth(t,a,b): u=np.clip((t-a)/(b-a),0,1); return u*u*(3-2*u)
def clean(bgr,t):
    if t<6.6: return bgr
    ym=ymax(t); l1b=float(np.interp(t,LT,LY)); y0=int(max(ym-26,l1b+7)); y1=int(ym+72)
    out=bgr.astype(np.float32).copy()
    # vertical linear interpolation between rows above and below the band (per column, mean of 3 rows)
    top=bgr[y0-5:y0-1,X0-60:X1+60].astype(np.float32).mean(axis=0); bot=bgr[y1+2:y1+6,X0-60:X1+60].astype(np.float32).mean(axis=0)
    top=cv2.GaussianBlur(top.reshape(1,-1,3),(0,0),sigmaX=22).reshape(-1,3)[60:-60]; bot=cv2.GaussianBlur(bot.reshape(1,-1,3),(0,0),sigmaX=22).reshape(-1,3)[60:-60]
    h=y1-y0
    for k,y in enumerate(range(y0,y1)):
        u=(k+0.5)/h
        out[y,X0:X1]=top*(1-u)+bot*u
    # feather mask (vertical edges + horizontal ends)
    m=np.zeros(bgr.shape[:2],np.float32); m[y0:y1,X0:X1]=1
    m=cv2.GaussianBlur(m,(0,0),5)
    # keep original pixels where original band is already clean background? (sparkles will be lost - acceptable)
    res=bgr.astype(np.float32)*(1-m[...,None])+out*m[...,None]
    return res.clip(0,255).astype(np.uint8)
if __name__=="__main__":
    os.makedirs("fr2",exist_ok=True); n=len(os.listdir("fr"))
    for i in range(n):
        t=3.0+i/24; bgr=cv2.imread(f"fr/f{i+1:04d}.png"); cv2.imwrite(f"fr2/f{i+1:04d}.png",clean(bgr,t))
    print("done",n)
