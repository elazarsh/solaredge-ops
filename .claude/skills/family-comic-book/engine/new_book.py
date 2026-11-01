"""Start a new family comic book in one command (family-comic-book skill).

    python3 new_book.py BOOK_DIR --title "הדרך של ..." --title-en "..." --prefix G1 [--hero "סבא ..."]

Creates the folders, copies this engine into BOOK_DIR/layout, and writes book.json, an empty plan,
special pages, progress.json, CLAUDE.md (for Claude), AGENTS.md (for Codex / the image tool) and README.md.
Then: put the family material in BOOK_DIR/sources/ (untrusted: read with python3 -I), and follow SKILL.md.
"""
import argparse, json, shutil
from pathlib import Path
E = Path(__file__).resolve().parent
T = E.parent / 'templates' / 'new-book'
a = argparse.ArgumentParser(); a.add_argument('book'); a.add_argument('--title', required=True); a.add_argument('--title-en', default='')
a.add_argument('--prefix', default='B1'); a.add_argument('--hero', default='סבא'); a.add_argument('--slug', default='')
o = a.parse_args()
B = Path(o.book).resolve()
if (B / 'layout' / 'book.json').exists():
    raise SystemExit(f'{B} already has a book. Nothing changed.')
for d in ['sources', 'ref', 'research', 'layout', 'art/panels', 'art/web', 'art/receipts', 'art/claude', 'handoffs/claude', 'handoffs/codex', 'print']:
    (B / d).mkdir(parents=True, exist_ok=True)
for f in ['geometry.py', 'build_sketch.py', 'sketch-template.html', 'detect_faces.py', 'print_pdf.js', 'print_pdf.py', 'register_art.py', 'map_satellite.py', 'map_labels.py', 'shot.js']:
    shutil.copy(E / f, B / 'layout' / f)
slug = o.slug or o.prefix.lower()
cfg = dict(book_root='..', title_he=o.title, title_en=o.title_en, id_prefix=o.prefix + '-', progress='art/progress.json',
           source_text='research/source-text.json', script=None, file_prefix=slug)
(B / 'layout/book.json').write_text(json.dumps(cfg, ensure_ascii=False, indent=1), encoding='utf-8')
(B / 'art/progress.json').write_text(json.dumps({'assets': []}, indent=1), encoding='utf-8')
(B / 'research/source-text.json').write_text('[]', encoding='utf-8')
for name in ['layout-plan.json', 'new-panels.json', 'special-pages.json']:
    txt = (T / name).read_text(encoding='utf-8').replace('{{PREFIX}}', o.prefix).replace('{{TITLE}}', o.title).replace('{{TITLE_EN}}', o.title_en).replace('{{HERO}}', o.hero)
    (B / 'layout' / name).write_text(txt, encoding='utf-8')
for name in ['CLAUDE.md', 'AGENTS.md', 'README.md']:
    txt = (T / name).read_text(encoding='utf-8').replace('{{PREFIX}}', o.prefix).replace('{{TITLE}}', o.title).replace('{{HERO}}', o.hero)
    (B / name).write_text(txt, encoding='utf-8')
print(f'ready: {B}\n  build: cd {B}/layout && python3 build_sketch.py   (serve the book folder over http to see images)')
