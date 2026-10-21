import os,sys,json,time,concurrent.futures as cf
from kf import *
from plan import *
os.makedirs('img',exist_ok=True)
def one(item):
    kid,para,pal,desc,must,cam=item
    if os.path.exists(f'img/{kid}.png'):return kid,'exists'
    prompt=BASE+PAL[pal]+desc
    best=None;bestscore=-1
    for i in range(6):
        try:png=call_img(prompt,['img/K5.png'])
        except Exception as e:
            print(kid,i,'ERR',str(e)[:100],flush=True);time.sleep(15*(i+1));continue
        try:got=read_words(png)
        except Exception as e:got=[]
        j=' '.join(got);score=sum(1 for m in must if m in j)-(10 if 'נוח' in j.split() else 0)
        open(f'img/{kid}_try{i}.png','wb').write(png)
        ok=(score==len(must))
        print(kid,i,got[:12],'OK' if ok else f'retry {score}/{len(must)}',flush=True)
        if score>bestscore:best,bestscore=png,score
        if ok:break
    if best is None:return kid,'FAIL'
    open(f'img/{kid}.png','wb').write(best)
    return kid,('ok' if bestscore==len(must) else f'weak {bestscore}/{len(must)}')
if __name__=='__main__':
    ids=sys.argv[1:]
    items=[p for p in P if not ids or p[0] in ids]
    with cf.ThreadPoolExecutor(3) as ex:
        for r in ex.map(one,items):print('RESULT',r,flush=True)
