"""Build the comic sketch of a family book (engine of the family-comic-book skill).

Everything book-specific lives in book.json next to this file (see templates/new-book/layout/book.json):
paths to the image list (progress.json), the source text (for the verbatim-quote check), titles, id prefix.
Inputs in this folder: layout-plan.json (pages, panel order, recipe, lettering, shots), new-panels.json
(what each panel shows), special-pages.json (cover, dedication, closing card, back), faces.json.

    python3 build_sketch.py                      -> sketch.html (+ script-he.md, new-bubbles-review-he.md)
    python3 build_sketch.py --landscape          -> sketch-landscape.html (A4 landscape album)
    python3 build_sketch.py --embed OUT.html     -> one self-contained file with small images, for sending
"""
import base64
import io
import json
import re
import sys
from pathlib import Path

V = Path(__file__).resolve().parent
CFG = json.loads((V / 'book.json').read_text(encoding='utf-8'))
B = (V / CFG.get('book_root', '..')).resolve()
sys.path.insert(0, str(V))
import geometry  # noqa: E402

plan = json.loads((V / 'layout-plan.json').read_text(encoding='utf-8'))
script = json.loads((B / CFG['script']).read_text(encoding='utf-8')) if CFG.get('script') else {'pages': []}
progress = json.loads((B / CFG['progress']).read_text(encoding='utf-8')) if (B / CFG.get('progress', 'art/progress.json')).exists() else {'assets': []}
memoir = {p['id']: p['text'] for p in json.loads((B / CFG['source_text']).read_text(encoding='utf-8'))} if CFG.get('source_text') else {}
PFX = CFG.get('id_prefix', '')
new_specs = {}
if (V / 'new-panels.json').exists():
    new_specs = {p['id']: p for p in json.loads((V / 'new-panels.json').read_text(encoding='utf-8'))}

faces = json.loads((V / 'faces.json').read_text()) if (V / 'faces.json').exists() else {}
render_overrides = json.loads((V/'render-overrides.json').read_text()) if (V/'render-overrides.json').exists() else {}
embed = '--embed' in sys.argv
land = '--landscape' in sys.argv
if land:
    geometry.H = 70.7   # A4 landscape: 100 x 70.7
out_path = Path(sys.argv[sys.argv.index('--embed') + 1]) if embed else V / ('sketch-landscape.html' if land else 'sketch.html')

panels_v07 = {q['id']: (p['number'], q) for p in script.get('pages', []) for q in p.get('panels', [])}
assets = {a['id']: a for a in progress['assets'] if 'rejected' not in a['status']}
hay = ' '.join(' '.join(memoir.values()).split())


def art_for(pid):
    a = assets.get(pid)
    if not a:
        return None
    w, h = a['actual_size']
    src = '../../' + a['web_file']
    if embed:
        from PIL import Image
        with Image.open(B / a['web_file']) as im:
            im = im.convert('RGB')
            im.thumbnail((760, 760))
            buf = io.BytesIO()
            im.save(buf, 'WEBP', quality=68, method=5)
        src = 'data:image/webp;base64,' + base64.b64encode(buf.getvalue()).decode()
    settings=render_overrides.get(pid,{})
    if settings.get('source_sha256')!=a.get('sha256'):settings={}
    return dict(src=src, w=w, h=h, status=a['status'], nomirror=bool(a.get('nomirror')), source_sha256=a.get('sha256'), faces=[f for f in faces.get(pid, []) if f[2] >= 2.5], **{k:settings[k] for k in ['fit','fx','fy','zoom'] if k in settings})


def frame_art(art, shape, shot):
    """Fill the panel (cover) without extra zoom, centred on the scene rather than on one face.
    Close-ups and details keep the face-led crop."""
    if shot in ('close', 'detail', 'extreme-close', 'xcu', 'ecu'):
        return {}
    if 'circle' in shape:
        x, y, pw, ph = shape['circle']
    else:
        xs = [p[0] for p in shape['poly']]; ys = [p[1] for p in shape['poly']]
        pw, ph = max(xs) - min(xs), max(ys) - min(ys)
    pa, ia = pw / max(ph, 1e-6), art['w'] / art['h']
    lost = 1 - min(pa, ia) / max(pa, ia)
    fc = art.get('faces') or []
    cx = sum(f[0] + f[2] / 2 for f in fc) / len(fc) / 100 if fc else .5
    cy = sum(f[1] + f[3] / 2 for f in fc) / len(fc) / 100 if fc else .4
    # never letterbox or blur: the picture always fills its panel (family feedback 01/11)
    k = .4 if lost < .3 else .85   # when the panel crops a lot, keep the faces in view
    return dict(fit='cover', zoom=1.0, fx=round((1 - k) * .5 + k * cx, 3), fy=round((1 - k) * .42 + k * (cy - .04), 3))


problems = []
pages = []
for pg in plan['pages']:
    order = pg['order']
    hero = order.index(pg['hero']) if pg.get('hero') in order else None
    inset = order.index(pg['inset']) if pg.get('inset') in order else None
    morphs = [(order.index(a), order.index(b)) for a, b in pg.get('morph', []) if a in order and b in order]
    roomy = [i for i, pid in enumerate(order)
             if any(t.get('type') in ('speech', 'thought', 'whisper', 'shout') for t in pg['texts'].get(pid, []))]
    shapes = geometry.page_shapes(pg.get('recipe_land', pg['recipe']) if land else pg['recipe'], len(order), hero, morphs, inset, roomy, pg.get('inset_dy', 0))
    out = []
    words = 0
    for i, pid in enumerate(order):
        old = [t['he'] for t in panels_v07[pid][1]['texts']] if pid in panels_v07 else []
        if pid in pg.get('shows_override', {}):
            shows = pg['shows_override'][pid]
        elif pid in panels_v07:
            shows = panels_v07[pid][1]['action']
        else:
            shows = new_specs.get(pid, {}).get('shows', '')
        texts = pg['texts'].get(pid, [])
        for t in texts:
            t['isnew'] = t.get('type') != 'caption' and t.get('he', '') not in old
            if re.search('[—–]', t.get('he', '') + t.get('en', '')):
                problems.append(f"{pid}: long dash")
            words += len(t.get('he', '').split())
            if t.get('kind') == 'quote':
                needle = ' '.join(t['he'].strip(' .!?,:;').split())
                if hay and needle not in hay:
                    problems.append(f"{pid}: quote not verbatim: {t['he']}")
        pur = pg.get('purpose', {}).get(pid, {})
        art = art_for(pg.get('art_land', {}).get(pid, pid) if land else pid)
        if art and not any(k in art for k in ('fit', 'zoom', 'fx', 'fy')):
            art.update(frame_art(art, shapes[i], pg.get('shots', {}).get(pid, {}).get('shot', '')))
        out.append(dict(id=pid, shows=shows, art=art, texts=texts, new=pid not in panels_v07, purpose=pur.get('purpose_he', ''), verdict=('resolved' if pur.get('verdict')=='redirect' and (assets.get(pid,{}).get('claude_v08_review_complete') or (assets.get(pid,{}).get('claude_v08_review') or {}).get('verdict')=='pass') else pur.get('verdict','')),
                        hero=(i == hero), **shapes[i]))
    # shot variety: adjacent panels must differ in at least two of distance, angle, subject, light
    sp = pg.get('shots', {})
    seq = [sp.get(pid) for pid in order if pid != (order[inset] if inset is not None else None)]
    if all(seq) and seq:
        for x, y in zip(seq, seq[1:]):
            diff = sum(x.get(k) != y.get(k) for k in ('shot', 'angle', 'subject', 'light'))
            if diff < 2:
                problems.append(f"page {pg['page']}: adjacent panels too alike ({x.get('shot')}/{x.get('subject')})")
        if len(seq) >= 3 and all(s.get('subject') == 'yitzhak' for s in seq):
            problems.append(f"page {pg['page']}: Yitzhak in every panel")
    if words > 60:
        problems.append(f"page {pg['page']}: {words} words")
    photos = [dict(ph, src=('../../' + ph['file'])) for ph in pg.get('photos', [])]
    pages.append(dict(n=pg['page'], photos=photos, title=pg.get('title', ''), pace=pg.get('pace', ''), recipe=pg['recipe'],
                      note=pg.get('note_he', ''), panels=out, H=geometry.H))

ready = sum(1 for p in pages for q in p['panels'] if q['art'])
total = sum(len(p['panels']) for p in pages)
sp = json.loads((V / 'special-pages.json').read_text(encoding='utf-8')) if (V / 'special-pages.json').exists() else None
if sp and sp.get('coverArtFile'):
    cover = B / sp['coverArtFile']
    if embed:
        from PIL import Image
        with Image.open(cover) as im:
            im = im.convert('RGB')
            im.thumbnail((1000, 1500))
            buf = io.BytesIO()
            im.save(buf, 'WEBP', quality=75, method=5)
        sp['coverArt'] = 'data:image/webp;base64,' + base64.b64encode(buf.getvalue()).decode()
    else:
        sp['coverArt'] = '../../' + sp['coverArtFile']
elif sp and sp.get('coverArtId'):
    ca = art_for(sp['coverArtId'])
    sp['coverArt'] = ca['src'] if ca else ''
def file_src(rel, size=(900, 900), alpha=False):
    if not embed:
        return '../../' + rel
    from PIL import Image
    with Image.open(B / rel) as im:
        im = im.convert('RGBA' if alpha else 'RGB')
        im.thumbnail(size)
        buf = io.BytesIO()
        im.save(buf, 'WEBP', quality=75, method=5)
    return 'data:image/webp;base64,' + base64.b64encode(buf.getvalue()).decode()


for p_ in pages:
    for ph in p_.get('photos', []):
        ph['src'] = file_src(ph['file'], (700, 700))
if sp and sp.get('titleArtFile'):
    sp['titleArt'] = file_src(sp['titleArtFile'], (1000, 1500))
for p_ in pages:
    for q_ in p_['panels']:
        for t_ in q_['texts']:
            if t_.get('imgFile'):
                t_['img'] = file_src(t_['imgFile'], (600, 600), alpha=True)
data = dict(special=sp, pages=pages, ready=ready, total=total, title=CFG.get('title_he', ''), title_en=CFG.get('title_en', ''),
            live=not embed, landscape=land)
html = (V / 'sketch-template.html').read_text(encoding='utf-8').replace(
    '/*DATA*/null', json.dumps(data, ensure_ascii=False))
out_path.write_text(html, encoding='utf-8')
print(json.dumps(dict(out=str(out_path), pages=len(pages), panels=total, images_ready=ready,
                      bytes=len(html.encode()), problems=problems), ensure_ascii=False, indent=1))

# the script, page by page, as the family reads it (only from the plan, so it always matches the sketch)
TYPE_HE = {'caption': 'קריינות', 'speech': 'דיבור', 'thought': 'מחשבה', 'whisper': 'לחישה', 'shout': 'צעקה'}
RECIPE_HE = {'splash': 'תמונה אחת לכל העמוד', 'splash-inset': 'תמונה גדולה ועיגול תקריב', 'wide-2': 'רחבה למעלה ושתיים מתחת',
             '2-wide': 'שתיים למעלה ורחבה גדולה למטה', 'tall-2': 'גבוהה מימין ושתיים משמאל', 'strips-3': 'שלוש רצועות רחבות',
             'zig-4': 'ארבע בזיגזג', 'wide-3': 'רחבה למעלה ושלוש מתחת', '3-wide': 'שלוש קטנות ורחבה גדולה למטה',
             'tall-3': 'גבוהה מימין ושלוש משמאל', 'grow-4': 'פאנלים שגדלים כלפי מטה', 'rigid-4': 'ארבעה ריבועים שקטים',
             'wide-2-wide': 'רחבה, שתיים, רחבה', 'burst-5': 'חמש', 'six': 'שש מהירות'}
PACE_HE = {'slow': 'אטי', 'normal': 'רגיל', 'fast': 'מהיר', 'silence': 'שקט'}
if not embed and not land:
    L = [f"# {CFG.get('title_he', '')} · תסריט וקומיקס", '',
         'נוצר אוטומטית מ־layout-plan.json, יחד עם הסקיצה. ⚠️ = בימוי או מסגרת שלא כתובים ביומן. 🆕 = בועה או משבצת חדשה.', '',
         f'{len(pages)} עמודים, {total} משבצות, {ready} תמונות מוכנות.', '']
    for p in pages:
        L += [f"## עמוד {p['n']}: {p['title']}", '', f"פריסה: {RECIPE_HE.get(p['recipe'], p['recipe'])} · קצב: {PACE_HE.get(p['pace'], p['pace'])}", '']
        if p['note']:
            L += [f"> {p['note']}", '']
        for i, q in enumerate(p['panels'], 1):
            tag = ' (עיגול תקריב)' if q.get('circle') else ''
            tag += ' · הפאנל הגדול' if q['hero'] else ''
            tag += ' · 🆕 משבצת חדשה' if q['new'] else ''
            tag += ' · ✔ יש תמונה' if q['art'] else ''
            tag += ' · 🔁 לצייר אחרת' if q.get('verdict') == 'redirect' else ''
            L += [f"**{i}. {q['id'].replace(PFX, '')}**{tag}", '', f"רואים: {q['shows']}", '']
            sh = next((x.get('shots', {}).get(q['id']) for x in plan['pages'] if x['page'] == p['n']), None)
            if sh:
                L += [f"צילום: {sh.get('shot')} · {sh.get('angle')} · {sh.get('subject')} · {sh.get('light')}", '']
            if q.get('purpose'):
                L += [f"למה התמונה כאן: {q['purpose']}", '']
            for t in q['texts']:
                mark = ' ⚠️' if t.get('kind') in ('staging', 'editorial') else ''
                mark += ' 🆕' if t.get('isnew') else ''
                body = t['he'] or '(ענן מחשבה עם ציור קטן של הנכדים)'
                L.append(f"- {TYPE_HE.get(t.get('type'), 'קריינות')}, {t.get('speaker', '')}: {body}{mark}")
            L.append('')
    (V / 'script-he.md').write_text('\n'.join(L), encoding='utf-8')

    # every new bubble with what in the memoir it rests on, for the family to check
    R = ['# בועות חדשות: על מה כל אחת נשענת', '',
         'ציטוט = מילה במילה מהיומן (נבדק אוטומטית). עיבוד = אותו תוכן במילים פשוטות. ⚠️ = בימוי שלא כתוב ביומן.', '',
         '| עמוד | משבצת | סוג | מי | הטקסט | סוג נאמנות | ביומן |', '|---|---|---|---|---|---|---|']
    KIND_HE = {'quote': 'ציטוט', 'adapted_speech': 'עיבוד דיבור', 'adapted_thought': 'עיבוד מחשבה', 'adapted': 'עיבוד', 'staging': '⚠️ בימוי', 'editorial': '⚠️ עורך'}
    for p in pages:
        for q in p['panels']:
            for t in q['texts']:
                if t.get('isnew'):
                    R.append(f"| {p['n']} | {q['id'].replace(PFX, '')} | {TYPE_HE.get(t.get('type'), '')} | {t.get('speaker', '')} | {t['he'] or '(ציור הנכדים)'} | {KIND_HE.get(t.get('kind'), t.get('kind'))} | {(t.get('memoir') or '').replace('|', '/')} |")
    (V / 'new-bubbles-review-he.md').write_text('\n'.join(R) + '\n', encoding='utf-8')
