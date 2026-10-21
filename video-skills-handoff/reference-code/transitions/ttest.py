import sys,json,concurrent.futures as cf,subprocess
import trans
tests=[('K17','K18','erase',{'dir':'r2l'}),('K14','K15','water',{'dir':'up'}),('K24','K25','tear',{}),('K33','K34','peel',{}),('K35','K36','ink',{'focus':(0.43,0.45)}),('K25','K26','ripple',{'focus':(0.7,0.4)})]
def run(t):
    a,b,k,p=t;trans.render_clip(a,b,k,p,5,False,False,f'tmp/tt_{k}.mp4');return k
with cf.ProcessPoolExecutor(3) as ex:
    for r in ex.map(run,tests):print(r,flush=True)
