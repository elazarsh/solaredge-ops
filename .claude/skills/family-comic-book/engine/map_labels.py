"""Hebrew labels, arrows and a home marker on a real satellite base (made by map_satellite.py).

    python3 map_satellite.py LON0 LON1 CENTER_LAT WIDTH HEIGHT OUT   # e.g. 18.55 21.95 51.3 1024 1536 tall
    python3 map_labels.py OUT places.json                            # writes OUT.html; screenshot it to PNG
places.json:
  {"home": {"label": "יונדזיוב, הבית: חוה ורייזל", "lat": 50.645, "lon": 20.303, "off": [275, 44]},
   "places": [{"label": "קילץ: שרהלה", "lat": 50.866, "lon": 20.628, "off": [170, -18]}, ...],
   "country": "פולין", "credit": "צילום לוויין: EOX, Sentinel-2 2016 (CC BY 4.0)"}
Rules (family feedback): Hebrew only, real coordinates, every label clear of dots, arrows and captions.
Make a map in the shape of its panel (tall map for a tall panel), never letterbox it.
"""
import base64, json, math, sys
from PIL import Image, ImageEnhance
OUT, PL = sys.argv[1], json.load(open(sys.argv[2], encoding='utf-8'))
x0, y0, w, h, Z = [float(v) for v in open(OUT + '_geo.txt').read().split()]
N = 2 ** int(Z) * 256
im = Image.open(OUT + '.jpg'); W, H = im.size
def P(lat, lon):
    r = math.radians(lat); X = (lon + 180) / 360 * N; Y = (1 - math.log(math.tan(r) + 1 / math.cos(r)) / math.pi) / 2 * N
    return (X - x0) / w * W, (Y - y0) / h * H
im = ImageEnhance.Brightness(im).enhance(1.35); im = ImageEnhance.Contrast(im).enhance(1.08); im = ImageEnhance.Color(im).enhance(.9)
im = Image.blend(im, Image.new('RGB', im.size, (255, 214, 150)), .12); im.save(OUT + '_warm.jpg', quality=92)
b64 = base64.b64encode(open(OUT + '_warm.jpg', 'rb').read()).decode()
T = 'font-family="Frank Ruhl Libre,serif" font-weight="900" fill="#fff6e2" stroke="#2a1a0c" stroke-width="8" paint-order="stroke" text-anchor="middle"'
s = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
     '<defs><marker id="ar" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#ffcf5a"/></marker>',
     '<radialGradient id="vg" cx="50%" cy="50%" r="72%"><stop offset=".6" stop-color="#000" stop-opacity="0"/><stop offset="1" stop-color="#1a0f05" stop-opacity=".55"/></radialGradient></defs>',
     f'<image href="data:image/jpeg;base64,{b64}" width="{W}" height="{H}"/><rect width="{W}" height="{H}" fill="url(#vg)"/>']
hm = PL['home']; hx, hy = P(hm['lat'], hm['lon'])
for pl in PL['places']:
    x, y = P(pl['lat'], pl['lon']); dx, dy = x - hx, y - hy; L = math.hypot(dx, dy) or 1; ux, uy = dx / L, dy / L
    sx, sy, ex, ey = hx + ux * 36, hy + uy * 36, x - ux * 28, y - uy * 28
    cx, cy = (sx + ex) / 2 - uy * L * .12, (sy + ey) / 2 + ux * L * .12
    d = f'M{sx:.1f},{sy:.1f} Q{cx:.1f},{cy:.1f} {ex:.1f},{ey:.1f}'
    s.append(f'<path d="{d}" fill="none" stroke="#2a1a0c" stroke-width="11" opacity=".55"/><path d="{d}" fill="none" stroke="#ffcf5a" stroke-width="6" stroke-dasharray="16 10" marker-end="url(#ar)"/>')
    s.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="15" fill="#c0392b" stroke="#fff6e2" stroke-width="5"/>')
    o = pl.get('off_tall' if H > W else 'off', [0, -60])
    s.append(f'<text x="{x + o[0]:.1f}" y="{y + o[1]:.1f}" font-size="48" {T}>{pl["label"]}</text>')
s.append(f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="28" fill="#e0a84f" stroke="#2a1a0c" stroke-width="5"/>'
         f'<path d="M{hx-15:.1f},{hy+6:.1f} L{hx:.1f},{hy-13:.1f} L{hx+15:.1f},{hy+6:.1f} L{hx+15:.1f},{hy+15:.1f} L{hx-15:.1f},{hy+15:.1f}Z" fill="#2a1a0c"/>')
o = hm.get('off_tall' if H > W else 'off', [0, 84])
s.append(f'<text x="{hx + o[0]:.1f}" y="{hy + o[1]:.1f}" font-size="48" {T}>{hm["label"]}</text>')
cx, cy = W - 150, 170
s.append(f'<g><circle cx="{cx}" cy="{cy}" r="56" fill="#000" fill-opacity=".25" stroke="#fff6e2" stroke-width="3"/><path d="M{cx},{cy-66} L{cx+13},{cy} L{cx},{cy+66} L{cx-13},{cy}Z" fill="#fff6e2"/><text x="{cx}" y="{cy-78}" font-size="30" {T}>צפון</text></g>')
if PL.get('country'): s.append(f'<text x="330" y="{H-170}" font-size="44" {T}>{PL["country"]}</text>')
s.append(f'<text x="{W-40}" y="{H-24}" font-family="Heebo" font-size="16" fill="#fff6e2" opacity=".8" text-anchor="end">{PL.get("credit", "צילום לוויין: EOX, Sentinel-2 2016 (CC BY 4.0)")}</text></svg>')
open(OUT + '.html', 'w', encoding='utf-8').write('<!doctype html><meta charset="utf-8"><link href="https://fonts.googleapis.com/css2?family=Frank+Ruhl+Libre:wght@900&family=Heebo:wght@400;700&display=swap" rel="stylesheet"><style>body{margin:0}</style>' + '\n'.join(s))
