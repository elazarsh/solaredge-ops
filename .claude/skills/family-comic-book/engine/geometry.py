"""Comic page geometry for Londner book 1, v0.8.
Pages are 100 units wide and H tall (A4 portrait: 141). Logical x runs from the START side
(the right edge in Hebrew), so reading order is the same in both languages; the renderer mirrors it.
A tree node is a leaf index (int) or {'h'|'v': at, 's': slope, 'a': node, 'b': node, 'mo': overlap}.
h cuts with y = at + s*(x-50) (a above); v cuts with x = at + s*(y-mid) (a on the start side)."""
H = 141.0
GAP = 2.4
S = 0.07


def half_plane(poly, a, b, c):
    out = []
    n = len(poly)
    for i in range(n):
        p1, p2 = poly[i], poly[(i + 1) % n]
        d1 = a * p1[0] + b * p1[1] - c
        d2 = a * p2[0] + b * p2[1] - c
        if d1 <= 1e-9:
            out.append(p1)
        if (d1 < -1e-9 < 1e-9 < d2) or (d2 < -1e-9 < 1e-9 < d1):
            k = d1 / (d1 - d2)
            out.append([p1[0] + (p2[0] - p1[0]) * k, p1[1] + (p2[1] - p1[1]) * k])
    return out


def bbox(poly):
    xs = [p[0] for p in poly]
    ys = [p[1] for p in poly]
    return min(xs), min(ys), max(xs) - min(xs), max(ys) - min(ys)


def cut(poly, node):
    s = node.get('s', 0)
    d = -node['mo'] / 2 if node.get('mo') else GAP / 2
    if 'h' in node:
        c0 = node['h'] - 50 * s
        return half_plane(poly, -s, 1, c0 - d), half_plane(poly, s, -1, -c0 - d)
    x, y, w, h = bbox(poly)
    c1 = node['v'] - s * (y + h / 2)
    return half_plane(poly, 1, -s, c1 - d), half_plane(poly, -1, s, -c1 - d)


def leaves(node):
    return [node] if isinstance(node, int) else leaves(node['a']) + leaves(node['b'])


def split(node, poly, out, meta):
    if isinstance(node, int):
        out[node] = poly
        return
    a, b = cut(poly, node)
    if node.get('mo'):
        for i in leaves(node['a']):
            meta.setdefault(i, {})['fade'] = 'b' if 'h' in node else 'e'
        for i in leaves(node['a']) + leaves(node['b']):
            meta.setdefault(i, {})['soft'] = True
    split(node['a'], a, out, meta)
    split(node['b'], b, out, meta)


def h(at, a, b, s=S):
    return {'h': at * H, 's': s, 'a': a, 'b': b}


def v(at, a, b, s=0.1):
    return {'v': at * 100, 's': s, 'a': a, 'b': b}


# recipes: name -> (panel count, tree builder)
RECIPES = {
    'splash': (1, lambda: 0),
    'splash-inset': (2, lambda: 0),
    'side-2': (2, lambda: v(.58, 0, 1, .06)),
    'big-small': (2, lambda: h(.64, 0, 1)),
    '2-1-2': (5, lambda: h(.37, v(.5, 0, 1, .1), h(.63, 2, v(.56, 3, 4, -.1), -S))),
    'wide-2': (3, lambda: h(.48, 0, v(.5, 1, 2, -.12))),
    '2-wide': (3, lambda: h(.42, v(.52, 0, 1, .12), 2, -S)),
    'tall-2': (3, lambda: v(.56, 0, h(.5, 1, 2), .05)),
    'stack-tall': (3, lambda: v(.46, h(.5, 0, 1), 2, -.05)),
    'strips-3': (3, lambda: h(.34, 0, h(.67, 1, 2))),
    'zig-4': (4, lambda: h(.5, v(.5, 0, 1, .1), v(.5, 2, 3, -.1))),
    'wide-3': (4, lambda: h(.5, 0, v(.34, 1, v(.67, 2, 3, .1), .1))),
    '3-wide': (4, lambda: h(.36, v(.34, 0, v(.67, 1, 2, .1), .1), 3, -S)),
    'tall-3': (4, lambda: v(.58, 0, h(.33, 1, h(.66, 2, 3, -S)), .05)),
    'grow-4': (4, lambda: h(.17, 0, h(.38, 1, h(.63, 2, 3, S), -S * .6), S * .5)),
    'rigid-4': (4, lambda: h(.5, v(.5, 0, 1, 0), v(.5, 2, 3, 0), 0)),
    'wide-2-wide': (4, lambda: h(.3, 0, h(.68, v(.5, 1, 2, .1), 3, -S))),
    'burst-5': (5, lambda: h(.3, 0, h(.64, v(.34, 1, v(.67, 2, 3, .1), .1), 4, -S))),
    'map-l': (3, lambda: v(.66, h(.64, 0, 1, 0), 2, .05)),
    'cols-3': (3, lambda: v(.34, 0, v(.67, 1, 2, .1), .1)),
    'six': (6, lambda: h(.33, v(.5, 0, 1, .1), h(.66, v(.5, 2, 3, -.1), v(.5, 4, 5, .1)))),
}


def bias(node, hero, amount=1.0):
    """Give the hero panel more room: every cut that separates it moves away from it."""
    if isinstance(node, int):
        return node
    la, lb = leaves(node['a']), leaves(node['b'])
    if hero in la or hero in lb:
        sign = 1 if hero in la else -1
        if 'h' in node:
            node['h'] += sign * 0.07 * H * amount
        else:
            node['v'] += sign * 9 * amount
    bias(node['a'], hero, amount)
    bias(node['b'], hero, amount)
    return node


def set_morph(node, i, j, mo=12):
    if isinstance(node, int):
        return False
    la, lb = leaves(node['a']), leaves(node['b'])
    if (i in la and j in lb) or (j in la and i in lb):
        if set_morph(node['a'], i, j, mo) or set_morph(node['b'], i, j, mo):
            return True
        node['mo'] = mo
        return True
    return set_morph(node['a'], i, j, mo) or set_morph(node['b'], i, j, mo)


def page_shapes(recipe, n, hero=None, morphs=(), inset=None, roomy=(), inset_dy=0):
    """Return {index: {'poly': [...]} or {'circle': (x,y,w,h)}} for n panels in reading order.
    The inset (if any) is a circle over the joint; the rest fill the page with the recipe."""
    if H < 100:   # landscape album: thin strips become columns
        recipe = {'strips-3': 'cols-3', 'wide-2-wide': 'zig-4', 'grow-4': 'tall-3'}.get(recipe, recipe)
    flow = [i for i in range(n) if i != inset]
    count, build = RECIPES.get(recipe, (None, None))
    if count != len(flow):
        recipe = {1: 'splash', 2: 'wide-2', 3: 'wide-2', 4: 'zig-4', 5: 'burst-5', 6: 'six'}.get(len(flow), 'six')
        if len(flow) == 2:
            build = lambda: h(.5, 0, 1)
        else:
            build = RECIPES[recipe][1]
    tree = build()
    # panels that carry speech or thought bubbles need room for them (user's rule): a gentler push
    for r in roomy:
        if r in flow and r != hero:
            bias(tree, flow.index(r), 0.55)
    if hero is not None and hero in flow:
        bias(tree, flow.index(hero))
    for a, b in morphs:
        if a in flow and b in flow:
            set_morph(tree, flow.index(a), flow.index(b))
    out, meta = {}, {}
    split(tree, [[0, 0], [100, 0], [100, H], [0, H]], out, meta)
    res = {}
    for k, idx in enumerate(flow):
        res[idx] = dict(poly=[[round(x, 2), round(y, 2)] for x, y in out[k]], **meta.get(k, {}))
    if inset is not None:
        # sit on the joint after the panel that precedes it, at the end side
        prev = res[flow[max(0, min(len(flow) - 1, inset - 1))]]['poly']
        x, y, w, hh = bbox(prev)
        d = 34 if H > 100 else 26
        cy = min(H - d - 2, max(2, y + hh - d * .55 + inset_dy))
        cx = min(100 - d - 3, max(3, x + w - d - 4))
        res[inset] = dict(circle=[round(cx, 2), round(cy, 2), d, d])
    return res
