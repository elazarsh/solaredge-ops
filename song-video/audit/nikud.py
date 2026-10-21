import json, re, difflib
S='/tmp/claude-0/-home-user-solaredge-ops/8f5877e5-ee60-5335-a789-ff5f3c5c3688/scratchpad/audit'
ROOT='/home/user/solaredge-ops/song-video'
NIQ=re.compile(r'[֑-ׇ]')
SEG='ֶ'; SHVA='ְ'; HSEG='ֱ'
st=json.load(open(ROOT+'/assets/stanzas.json',encoding='utf-8'))
tm=json.load(open(ROOT+'/timings.json',encoding='utf-8'))['stanzas']
def letters(w): return re.sub(r'[^א-ת]','',NIQ.sub('',w))
# ---- rule based: non-standard vocalization on screen
flags=[]
for s,t in zip(st,tm):
    for li,line in enumerate(s['lines']):
        for w in line.split():
            core=re.sub(r'^[״"׳\'(]+','',w)
            core_ltr=letters(core)
            # first letter + its marks
            m=re.match(r'^([א-ת])([֑-ׇ]*)(.*)$',core)
            if not m: continue
            l1,marks1,rest=m.groups()
            why=None
            if l1 in 'ובלכמ' and SEG in marks1 and len(core_ltr)>2:
                nxt=re.match(r'^([א-ת])([֑-ׇ]*)',rest)
                if not (nxt and HSEG in nxt.group(2)):
                    why='תחילית עם סגול (בדרך כלל שווא)'
            if l1=='ה' and re.match(r'^הַ',core) and re.match(r'^ה[֑-ׇ]*[אער]',core) and False: pass
            if l1=='ה' and 'ַ' in marks1:
                nxt=re.match(r'^([א-ת])',rest)
                if nxt and nxt.group(1) in 'אער': why='ה״א הידיעה לפני א/ע/ר (בדרך כלל קמץ)'
            if l1=='ש' and SEG in marks1 and core_ltr in ('שניהם','שבויים') : why='שין עם סגול במקום שווא'
            if core_ltr.startswith('ושבו') and 'שבויים' in core_ltr and re.search(r'שֶ',core): why='שין עם סגול במקום שווא'
            if why: flags.append({'stanza':t['id'],'line':li,'word':w,'plain':core_ltr,'why':why})
json.dump(flags,open(S+'/nikud_rule_flags.json','w'),ensure_ascii=False,indent=1)
print('rule flags:',len(flags))
for f in flags: print(f"S{f['stanza']:>2} | {f['word']:16} | {f['why']}")
# ---- model vocalization (hint): compare per word with on-screen nikud
g=json.load(open(S+'/gemini_raw.json'))
def norm(w): return re.sub('[ּֽֿׁׂ]','',re.sub(r'[^א-תְ-ֻּׁׂ]','',w))
def canon(w):
    c=re.sub(r'[יו]','',letters(w)) if len(letters(w))>3 else letters(w)
    return c.replace('ך','כ').replace('ם','מ').replace('ן','נ').replace('ף','פ').replace('ץ','צ')
def voc(model):
    out=[]
    for i in range(4):
        for it in g['res'][model][str(i)]:
            if isinstance(it,dict):
                txt=it.get('vocalized') or ''
                if not NIQ.search(txt): txt=it.get('plain','') if NIQ.search(it.get('plain','')) else ''
                out.append((g['cuts'][i]+it.get('s',0),txt))
    return out
V={'pro':voc('gemini-3.1-pro-preview'),'flash':voc('gemini-3.8-flash')}
print('\nvocalized lines available: pro',sum(1 for t,x in V['pro'] if x),'/',len(V['pro']),' flash',sum(1 for t,x in V['flash'] if x),'/',len(V['flash']))
res=[]
for s,t in zip(st,tm):
    a,b=t['start'],t['end']
    ref=[w for l in s['lines'] for w in l.split()]
    for k,lines in V.items():
        hw=[w for tt,x in lines if a-1.6<=tt<=b+0.3 for w in x.split()]
        sm=difflib.SequenceMatcher(None,[canon(w) for w in ref],[canon(w) for w in hw],autojunk=False)
        for tag,i1,i2,j1,j2 in sm.get_opcodes():
            if tag=='equal':
                for r,h in zip(ref[i1:i2],hw[j1:j2]):
                    if norm(r)!=norm(h) and NIQ.search(h):
                        res.append({'stanza':t['id'],'model':k,'screen':r,'heard':h})
json.dump(res,open(S+'/nikud_model_diffs.json','w'),ensure_ascii=False,indent=1)
by={}
for r in res: by.setdefault((r['stanza'],r['screen']),{})[r['model']]=r['heard']
both=[(k,v) for k,v in by.items() if len(v)==2 and norm(v['pro'])==norm(v['flash'])]
print('words where both models agree on a different vocalization:',len(both))
for (sid,scr),v in both: print(f"S{sid:>2} | screen {scr:14} | both heard {v['pro']}")
