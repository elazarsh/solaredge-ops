"""Register pictures into art/progress.json (the list the engine reads): makes a WebP copy, size and hash.
    python3 register_art.py            # every PNG/JPG in art/panels/ whose file name is a panel id (e.g. G1-P03-02.png)
Run detect_faces.py and build_sketch.py afterwards."""
import hashlib, json, sys
from pathlib import Path
from PIL import Image
V = Path(__file__).resolve().parent
CFG = json.loads((V / 'book.json').read_text(encoding='utf-8'))
B = (V / CFG.get('book_root', '..')).resolve()
prog_path = B / CFG['progress']
prog = json.loads(prog_path.read_text(encoding='utf-8')) if prog_path.exists() else {'assets': []}
have = {a['id']: a for a in prog['assets']}
panels, web = B / 'art/panels', B / 'art/web'
web.mkdir(parents=True, exist_ok=True)
n = 0
for f in sorted(list(panels.glob('*.png')) + list(panels.glob('*.jpg'))):
    pid = f.stem.split('.')[0]
    sha = hashlib.sha256(f.read_bytes()).hexdigest()
    if pid in have and have[pid].get('sha256') == sha:
        continue
    im = Image.open(f).convert('RGB'); w = web / (pid + '.webp'); im.save(w, quality=88)
    have[pid] = dict(have.get(pid, {}), id=pid, file=str(f.relative_to(B)), web_file=str(w.relative_to(B)),
                     actual_size=list(im.size), sha256=sha, status=have.get(pid, {}).get('status', 'generated'))
    n += 1
prog['assets'] = list(have.values())
prog_path.parent.mkdir(parents=True, exist_ok=True)
prog_path.write_text(json.dumps(prog, ensure_ascii=False, indent=1), encoding='utf-8')
print(f'{n} new or changed, {len(prog["assets"])} in total')
