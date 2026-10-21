import json, re, difflib
S='/tmp/claude-0/-home-user-solaredge-ops/8f5877e5-ee60-5335-a789-ff5f3c5c3688/scratchpad/audit'
ROOT='/home/user/solaredge-ops/song-video'
NIQ=re.compile(r'[֑-ׇ]')
def plain(s): return re.sub(r'\s+',' ',re.sub(r'[^א-ת ]',' ',NIQ.sub('',s.replace('־',' ').replace('—',' ')))).strip()
FIN=str.maketrans('ךםןףץ','כמנפצ')
def canon(w):
    w=w.translate(FIN)
    return w[0]+re.sub(r'[יו]','',w[1:]) if len(w)>3 else w      # keep the first letter: conjunction/prefix matters
def sound(w): return w.replace('ס','ש')                           # sin = samekh in speech
st=json.load(open(ROOT+'/assets/stanzas.json',encoding='utf-8'))
tm=json.load(open(ROOT+'/timings.json',encoding='utf-8'))['stanzas']
g=json.load(open(S+'/gemini_raw.json'))
def gem(model):
    return [(g['cuts'][i]+it.get('s',0), it.get('plain','')) for i in range(4) for it in g['res'][model][str(i)] if isinstance(it,dict)]
src={'pro':gem('gemini-3.1-pro-preview'),'flash':gem('gemini-3.8-flash')}
for s,t in zip(st,tm):
    if t['id']==19: continue
    a,b=t['start'],t['end']; ref=' '.join(plain(l) for l in s['lines']).split()
    out=[]
    for k,lines in src.items():
        hw=[w for tt,x in lines if a-1.6<=tt<=b+0.3 for w in plain(x).split()]
        sm=difflib.SequenceMatcher(None,[sound(canon(w)) for w in ref],[sound(canon(w)) for w in hw],autojunk=False)
        for tag,i1,i2,j1,j2 in sm.get_opcodes():
            if tag!='equal' and tag!='insert' : out.append(f"{k}: [{' '.join(ref[i1:i2])}]→[{' '.join(hw[j1:j2])}]")
    if out: print(f"S{t['id']:>2}: "+' ; '.join(out))
