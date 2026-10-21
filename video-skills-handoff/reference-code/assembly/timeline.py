import json,os,wave
from plan import P
ids=['K6']+[p[0] for p in P]
def tr(a,b):return (f'veo/{a}_{b}.mp4',0,8,False)
def chain(a,b):
    i,j=ids.index(a),ids.index(b);return [tr(ids[k],ids[k+1]) for k in range(i,j)]
GROUPS=[
(1,[('../ch1v4/veo/A1_lite.mp4',0,8,False),('../ch1v4/veo/B.mp4',0.5,5.5,False)]),
(2,[('../ch1v4/veo/C.mp4',0,8,False)]),
(3,[('../ch1v4/veo/D.mp4',0,8,False),('../ch1v4/veo/E4_lite.mp4',0,8,True)]),
(4,chain('K6','K9')),(5,chain('K9','K11')),(6,chain('K11','K16')),(7,chain('K16','K20')),(8,chain('K20','K23')),
(9,chain('K23','K27')),(10,chain('K27','K30')),(11,chain('K30','K33')),(12,chain('K33','K36')),(13,chain('K36','K40')),
(14,chain('K40','K44')),(15,chain('K44','K46')),(16,chain('K46','K49')),(17,chain('K49','K51')),(18,chain('K51','K54')),
(19,chain('K54','K58')),(20,chain('K58','K61')),(21,chain('K61','K64')),(22,chain('K64','K67')),
]
durs={int(k):v for k,v in json.load(open('vo/durs.json')).items()}
LEAD,TAIL=0.35,1.4
def build():
    t=0.0;segs=[];paras=[]
    for p,items in GROUPS:
        src=sum(e-s for _,s,e,_ in items);D=durs[p]
        if p==2:sp=[0.78];lead=0.1
        elif p==3:sp=[1.0,0.9];lead=1.5
        else:
            s=src/(D+LEAD+TAIL);s=min(1.3,max(0.8,s));sp=[s]*len(items);lead=LEAD
            W=src/s;lead=LEAD+max(0,(W-D-LEAD-TAIL))/2
        start=t
        for (f,s0,s1,fl),s in zip(items,sp):
            d=(s1-s0)/s;segs.append(dict(par=p,file=f,ss=s0,to=s1,flip=fl,speed=s,t0=t,dur=d,key=os.path.basename(f)[:-4]));t+=d
        paras.append(dict(par=p,t0=start,vo=start+lead,dur=D,end=t))
    return segs,paras,t
if __name__=='__main__':
    segs,paras,T=build()
    for q in paras:print(q['par'],round(q['t0'],1),round(q['vo'],1),round(q['vo']+q['dur'],1),round(q['end'],1))
    print('total',T)
