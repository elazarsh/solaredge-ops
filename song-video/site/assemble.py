#!/usr/bin/env python3
"""Assemble src/*.html into site/*.html (inlines the Frank Ruhl Libre fallback font as data URIs)."""
import base64, glob, os
HERE = os.path.dirname(os.path.abspath(__file__))
A = os.path.join(os.path.dirname(HERE), "assets")
def face(w):
    b = base64.b64encode(open(os.path.join(A, "FrankRuhlLibre-%d.woff" % w), "rb").read()).decode()
    return '@font-face{font-family:"FRL Local";font-weight:%s;src:url(data:font/woff;base64,%s) format("woff");font-display:swap}' % ("400 500" if w == 400 else "600 900", b)
fonts = face(400) + "\n" + face(600)
for f in glob.glob(os.path.join(HERE, "src", "*.html")):
    s = open(f, encoding="utf-8").read().replace("/*@@FONTS@@*/", fonts)
    open(os.path.join(HERE, os.path.basename(f)), "w", encoding="utf-8").write(s)
    print("wrote", os.path.basename(f), len(s))
