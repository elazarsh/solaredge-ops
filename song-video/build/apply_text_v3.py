#!/usr/bin/env python3
"""Apply the approved text changes (dashes, nikud, stanza 5 wording) -> assets/stanzas-v3.json. usage: apply_text_v3.py"""
import json, re, os
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NIQ = re.compile(r'[֑-ׇ]'); SH = 'ְ'
st = json.load(open(ROOT + '/assets/stanzas.json', encoding='utf-8'))
SPECIAL = {'וֶיִרַשׁ': 'וְיִרַשׁ', 'הַעָתִיד': 'הָעָתִיד', 'שֶׁנֵיהֶם': 'שְׁנֵיהֶם', 'וּשֶׁבוּיִים': 'וּשְׁבוּיִים', 'נִשְׁמֶרָה': 'נִשְׁמְרָה', 'בַּגֶּבוּרָה': 'בַּגְּבוּרָה',
 'יֶלָדִים': 'יְלָדִים', 'זֶרוֹעוֹת': 'זְרוֹעוֹת', 'יֶמֵי': 'יְמֵי', 'רֶשׁוּמִים': 'רְשׁוּמִים', 'יֶשׁוּעָה': 'יְשׁוּעָה', 'בֶרֵאשִׁית': 'בְּרֵאשִׁית', 'לֶךָ': 'לְךָ', 'כֶּתֶף': 'כְּתֵף'}
KEEP = {'זֶרַע', 'שֶׁקָּרָא', 'שֶׁקּוֹרַעַת', 'שֶׁנּוֹתְרוּ', 'שֶׁהָאֵם', 'שֶׁיַּעֲנֶה', 'שֶׁשָּׁבוּ', 'שֶׁנִּפְצַע', 'שֶׁנִּשְׁלְחוּ', 'שֶׁנֶּאֶחֲזָה', 'שֶׁיַּבִּיטוּ', 'אֶת', 'אֶל', 'הֶפְרֵשֵׁי', 'בֶּטֶרֶם', 'יֶשׁ', 'קֶמֶט', 'נֶעֱקַד', 'שֶׁלָּהֶם'}
def fixcore(c):
    if c in KEEP: return c
    if c in SPECIAL: return SPECIAL[c]
    m = re.match(r'^((?:וּ)?[א-ת]ּ?)ֶ(.*)$', c)
    if m and len(NIQ.sub('', c)) >= 3: return m.group(1) + SH + m.group(2)
    return c
def fixword(w):
    pre, core, post = re.match(r'^([״"׳\'(]*)(.*?)([״"׳\'.,:;)\s]*)$', w).groups()
    return pre + fixcore(core) + post
def fix(l): return ' '.join(fixword(w) for w in l.split())
OVERRIDE = {(5, 2): 'יֵשׁ בְּשׂוֹרָה שֶׁקּוֹרַעַת בְּחַיֵּי שָׂרָה,', (5, 3): 'מִמַּדִּים שֶׁנּוֹתְרוּ תְּלוּיִים אַחֲרֶיהָ.'}
out, nchg = [], 0
for s in st:
    lines = []
    for li, l in enumerate(s['lines']):
        if (s['id'], li) in OVERRIDE: new = OVERRIDE[(s['id'], li)]
        elif '—' in l:
            new = fix(l.replace(' — ', ', ')) if (s['id'], li) == (0, 2) else fix(re.sub(r'\s*—\s*$', '', l)) + (',' if s['id'] == 17 else '')
        else: new = fix(l)
        nchg += new != l; lines.append(new)
    out.append({**s, 'lines': lines})
json.dump(out, open(ROOT + '/assets/stanzas-v3.json', 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
assert not any('—' in l for s in out for l in s['lines']), 'dash left'
print('changed lines:', nchg)
