# -*- coding: utf-8 -*-
"""יוצר טקסט אחד להדבקה: רק תגיות <short pause> בסוגריים משולשים (הנימה נשארת בשדה הסגנון)."""
import re,sys
t=open(sys.argv[1],encoding='utf-8').read()
rep={'[Punch]':'<short pause>','[Big punch]':'<short pause> <short pause>','[Brief pause]':'<short pause>',
     '[Hold silence]':'<short pause> <short pause> <short pause>','[Gap]':'<short pause> <short pause> <short pause>',
     '[Pause, then renewed resolve]':'<short pause> <short pause>'}
for k,v in rep.items(): t=t.replace(k,v)
t=re.sub(r'\[[^\]]+\]\s*','',t)
t=re.sub(r'[ \t]+',' ',t); t=re.sub(r'\n ','\n',t); t=re.sub(r'\n{3,}','\n\n',t).strip()
t=re.sub(r'^(<short pause>(?: <short pause>)*)\n',r'\1 ',t,flags=re.M)
open(sys.argv[2],'w',encoding='utf-8').write(t+"\n"); print(t)
