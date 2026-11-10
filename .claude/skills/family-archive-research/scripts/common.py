import os, sys

BS = chr(92)


def lp(path):
    """Long-path-safe absolute Windows path."""
    p = os.path.abspath(path)
    if p.startswith(BS * 2 + '?' + BS):
        return p
    return BS * 2 + '?' + BS + p


def short(path):
    p = str(path)
    pre = BS * 2 + '?' + BS
    return p[len(pre):] if p.startswith(pre) else p


def utf8_stdout():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


IMG_EXT = {'.jpg', '.jpeg', '.png', '.bmp', '.tif', '.tiff', '.gif', '.webp'}


_CANON = None


def canon_map():
    """dup_path -> canonical_path (from _work/canon.tsv)."""
    global _CANON
    if _CANON is None:
        _CANON = {}
        f = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'canon.tsv')
        if os.path.exists(f):
            for line in open(f, encoding='utf-8').read().splitlines()[1:]:
                a, _, b = line.partition('\t')
                _CANON[a] = b
    return _CANON


def walk_files(root, exts=None, recursive=True, skipdups=False):
    """Yield files under root. skipdups=True skips files whose identical copy lives elsewhere (see canon.tsv)."""
    root = lp(root)
    if os.path.isfile(root):
        yield short(root)
        return
    cm = canon_map() if skipdups else {}
    for dp, dns, fns in os.walk(root):
        dns.sort()
        for f in sorted(fns):
            if exts is None or os.path.splitext(f)[1].lower() in exts:
                p = short(os.path.join(dp, f))
                if p in cm:
                    continue
                yield p
        if not recursive:
            break
