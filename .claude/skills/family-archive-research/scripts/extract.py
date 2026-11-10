"""Extract text from documents (long-path safe).

usage: python extract.py PATH [PATH ...] [--max N]
  PATH = file or folder (recursive). Handles pdf, docx, doc/rtf/wp*/odt (via Word), pptx/ppt(Word-less: pptx only),
  xlsx/xls, txt/md/srt/vtt, htm/html, ged, csv.
  PDFs without a text layer are reported as SCANNED -> use render.py and read the images.
"""
import os, sys, re, argparse, tempfile, shutil
sys.path.insert(0, os.path.dirname(__file__))
from common import lp, short, walk_files, utf8_stdout

TEXT_EXT = {'.pdf', '.docx', '.doc', '.rtf', '.odt', '.wp3', '.wpd', '.pptx', '.xlsx', '.xlsm', '.xls', '.txt', '.md',
            '.srt', '.vtt', '.sbv', '.htm', '.html', '.ged', '.csv', '.json'}
_word = None


def read_txt(p):
    raw = open(lp(p), 'rb').read()
    for enc in ('utf-8-sig', 'utf-16', 'cp1255', 'latin-1'):
        try:
            t = raw.decode(enc)
            if enc == 'utf-16' and not raw[:2] in (b'\xff\xfe', b'\xfe\xff'):
                continue
            return t
        except Exception:
            pass
    return raw.decode('utf-8', 'replace')


def pdf_text(p):
    import fitz
    doc = fitz.open(lp(p))
    out, chars = [], 0
    for i, pg in enumerate(doc):
        t = pg.get_text()
        chars += len(t.strip())
        out.append(f'--- page {i + 1} ---\n{t}')
    n = len(doc)
    if chars < 40 * n:
        return f'[SCANNED PDF: {n} pages, ~{chars} text chars -> render pages with render.py and read visually]\n' + '\n'.join(out)
    return '\n'.join(out)


def docx_text(p):
    import docx
    d = docx.Document(lp(p))
    out = [para.text for para in d.paragraphs]
    for ti, t in enumerate(d.tables):
        out.append(f'--- table {ti + 1} ---')
        for r in t.rows:
            out.append(' | '.join(c.text.strip() for c in r.cells))
    nimg = sum(1 for r in d.part.rels.values() if 'image' in r.reltype)
    if nimg:
        out.append(f'[docx contains {nimg} embedded images]')
    return '\n'.join(out)


def word_text(p):
    global _word
    import win32com.client
    if _word is None:
        _word = win32com.client.DispatchEx('Word.Application')
        _word.Visible = False
        _word.DisplayAlerts = 0
    tmpd = tempfile.mkdtemp()
    src = os.path.join(tmpd, 'src' + os.path.splitext(p)[1])
    shutil.copyfile(lp(p), src)
    doc = _word.Documents.Open(src, ConfirmConversions=False, ReadOnly=True, AddToRecentFiles=False)
    out = os.path.join(tmpd, 'out.txt')
    doc.SaveAs2(out, FileFormat=7, Encoding=65001)  # wdFormatUnicodeText, utf-8
    doc.Close(False)
    t = open(out, encoding='utf-8', errors='replace').read()
    shutil.rmtree(tmpd, ignore_errors=True)
    return t


def pptx_text(p):
    from pptx import Presentation
    pr = Presentation(lp(p))
    out = []
    for i, s in enumerate(pr.slides):
        out.append(f'--- slide {i + 1} ---')
        for sh in s.shapes:
            if sh.has_text_frame:
                out.append(sh.text_frame.text)
            if getattr(sh, 'shape_type', None) == 13:
                out.append('[picture]')
        if s.has_notes_slide:
            out.append('[notes] ' + s.notes_slide.notes_text_frame.text)
    return '\n'.join(out)


def xlsx_text(p):
    if p.lower().endswith('.xls'):
        try:
            import xlrd
        except ImportError:
            return '[xls: xlrd not installed; open with Excel COM if needed]'
        wb = xlrd.open_workbook(lp(p))
        out = []
        for sh in wb.sheets():
            out.append(f'--- sheet {sh.name} ---')
            for r in range(sh.nrows):
                out.append(' | '.join(str(v) for v in sh.row_values(r)))
        return '\n'.join(out)
    import openpyxl
    wb = openpyxl.load_workbook(lp(p), data_only=True, read_only=True)
    out = []
    for ws in wb.worksheets:
        out.append(f'--- sheet {ws.title} ---')
        for row in ws.iter_rows(values_only=True):
            if any(v is not None for v in row):
                out.append(' | '.join('' if v is None else str(v) for v in row))
    return '\n'.join(out)


def html_text(p):
    from bs4 import BeautifulSoup
    s = BeautifulSoup(read_txt(p), 'html.parser')
    for t in s(['script', 'style']):
        t.decompose()
    imgs = [i.get('src') for i in s.find_all('img')]
    t = re.sub(r'\n\s*\n+', '\n\n', s.get_text('\n'))
    return t + ('\n[images: ' + ', '.join(str(x) for x in imgs[:60]) + ']' if imgs else '')


def extract(p):
    e = os.path.splitext(p)[1].lower()
    if e == '.pdf':
        return pdf_text(p)
    if e == '.docx':
        return docx_text(p)
    if e in ('.doc', '.rtf', '.odt', '.wp3', '.wpd'):
        return word_text(p)
    if e == '.pptx':
        return pptx_text(p)
    if e in ('.xlsx', '.xlsm', '.xls'):
        return xlsx_text(p)
    if e in ('.htm', '.html'):
        return html_text(p)
    return read_txt(p)


def main():
    utf8_stdout()
    ap = argparse.ArgumentParser()
    ap.add_argument('paths', nargs='+')
    ap.add_argument('--max', type=int, default=60000, help='max chars per file')
    a = ap.parse_args()
    for root in a.paths:
        for f in walk_files(root, TEXT_EXT):
            print(f'\n========== {f} ==========')
            try:
                t = extract(f)
                print(t[:a.max] + (f'\n[...truncated, {len(t)} chars total]' if len(t) > a.max else ''))
            except Exception as ex:
                print(f'[ERROR {type(ex).__name__}: {ex}]')
    if _word is not None:
        _word.Quit()


if __name__ == '__main__':
    main()
