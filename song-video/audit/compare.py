import json, re, difflib, sys
S='/tmp/claude-0/-home-user-solaredge-ops/8f5877e5-ee60-5335-a789-ff5f3c5c3688/scratchpad/audit'
ROOT='/home/user/solaredge-ops/song-video'
NIQ=re.compile(r'[֑-ׇ]')
def plain(s): return re.sub(r'\s+',' ',re.sub(r'[^א-ת ]',' ',NIQ.sub('',s.replace('־',' ').replace('—',' ')))).strip()
def canon(w):
    c=re.sub(r'[יו]','',w) if len(w)>3 else w   # tolerate full/defective spelling
    return c.replace('ך','כ').replace('ם','מ').replace('ן','נ').replace('ף','פ').replace('ץ','צ')
st=json.load(open(ROOT+'/assets/stanzas.json',encoding='utf-8'))
tm=json.load(open(ROOT+'/timings.json',encoding='utf-8'))['stanzas']
g=json.load(open(S+'/gemini_raw.json'))
def gem(model):
    out=[]
    for i in range(4):
        for it in g['res'][model][str(i)]:
            if isinstance(it,dict): out.append((g['cuts'][i]+it.get('s',0), it.get('plain','')))
    return out
tr=json.load(open(ROOT+'/assets/transcript-whisper.json',encoding='utf-8'))
whisper=[(s['start'],s['text']) for s in tr]
src={'pro':gem('gemini-3.1-pro-preview'),'flash':gem('gemini-3.8-flash'),'whisper':whisper}
def words_for(lines,a,b):
    return [w for t,tx in lines if a-1.6<=t<=b+0.3 for w in plain(tx).split()]
report=[]
for s,t in zip(st,tm):
    sid=t['id']; a,b=t['start'],t['end']
    txt=[plain(l) for l in s['lines']]
    ref=' '.join(txt).split()
    entry={'id':sid,'ref':' '.join(ref),'diffs':{}}
    for k,lines in src.items():
        hw=words_for(lines,a,b)
        sm=difflib.SequenceMatcher(None,[canon(w) for w in ref],[canon(w) for w in hw],autojunk=False)
        ops=[(tag,' '.join(ref[i1:i2]),' '.join(hw[j1:j2])) for tag,i1,i2,j1,j2 in sm.get_opcodes() if tag!='equal']
        entry['diffs'][k]={'heard':' '.join(hw),'ops':ops}
    report.append(entry)
json.dump(report,open(S+'/compare.json','w'),ensure_ascii=False,indent=1)
for e in report:
    print(f"--- S{e['id']}: {e['ref']}")
    for k in ('pro','flash','whisper'):
        ops=e['diffs'][k]['ops']
        if k=='whisper': ops=[o for o in ops]  # whisper noisy, shown for reference
        print(f"   {k:7}", ' | '.join(f"{tag}: [{r}]→[{h}]" for tag,r,h in ops) if ops else 'MATCH')
