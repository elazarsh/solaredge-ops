# -*- coding: utf-8 -*-
"""מנתק רקע ירוק מכל החלקים (S*.png) ל־PNG שקוף. אלפא לפי 'ירקרקות' (g - max(r,b)), חיתוך רך, ניקוי גלישת ירוק (despill)."""
import numpy as np, glob, os, sys
from PIL import Image, ImageFilter
SRC='art/sprites'; DST='build/sprites_rgba'
def key(path):
    im=Image.open(path).convert('RGB'); a=np.asarray(im).astype(np.float32)
    r,g,b=a[...,0],a[...,1],a[...,2]
    green=g-np.maximum(r,b)                      # ברקע ירוק: גבוה (≈150-255); בחפצים: נמוך/שלילי
    # אלפא: 1 כשאין ירוק, 0 כשירוק מלא; מעבר רך בין 40 ל־110
    alpha=np.clip(1-(green-40)/70.0,0,1)
    # חפצים ירוקים כהים (S11): שומרים לפי בהירות. ירוק כהה: g נמוך (<150) בעוד הרקע g גבוה (>200)
    dark=(g<170)
    alpha=np.where(dark&(green>20)&(g<170),1.0,alpha)
    m=Image.fromarray((alpha*255).astype(np.uint8))
    m=m.filter(ImageFilter.MedianFilter(3))       # מנקה פיקסלים בודדים
    alpha=np.asarray(m).astype(np.float32)/255
    # despill: מחסירים עודף ירוק בקצוות חלקיים
    gg=np.minimum(g,np.maximum(r,b)+8)
    gg=np.where(alpha<0.98,gg,g)
    out=np.dstack([r,gg,b,alpha*255]).astype(np.uint8)
    # רק רכיב הצורה הגדול (מוחק רסיסים קטנים מבודדים)
    return Image.fromarray(out,'RGBA')
for p in sorted(glob.glob(f'{SRC}/S*.png')):
    o=key(p); n=os.path.basename(p); o.save(f'{DST}/{n}')
    a=np.asarray(o)[...,3]; print(n, o.size, 'opaque%%=%.1f'%((a>127).mean()*100))
