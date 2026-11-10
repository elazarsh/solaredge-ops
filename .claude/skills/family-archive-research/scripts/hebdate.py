"""Gregorian <-> Hebrew date helpers (pyluach).

g2h(1930,10,31) -> 'ט׳ בחשוון תרצ״א'
year_h(1939)    -> 'תרצ״ט–ת״ש'   (Gregorian year spans two Hebrew years)
fmt(1930,10,31) -> '31.10.1930 (ט׳ בחשוון תרצ״א)'
Note: the Hebrew date changes at sunset; conversions assume a daytime event.
"""
from pyluach import dates, hebrewcal

MONTHS = {'חשון': 'חשוון'}


def _heb(h):
    s = h.hebrew_date_string()  # e.g. ט׳ חשון תרצ״א
    day, month, year = s.split(' ', 1)[0], h.month_name(hebrew=True), s.rsplit(' ', 1)[1]
    month = MONTHS.get(month, month)
    return f'{day} ב{month} {year}'


def g2h(y, m, d):
    return _heb(dates.GregorianDate(y, m, d).to_heb())


def year_h(y):
    a = dates.GregorianDate(y, 1, 1).to_heb()
    b = dates.GregorianDate(y, 12, 31).to_heb()
    ya = a.hebrew_date_string().rsplit(' ', 1)[1]
    yb = b.hebrew_date_string().rsplit(' ', 1)[1]
    return ya if ya == yb else f'{ya}–{yb}'


def month_h(y, m):
    import calendar
    a = dates.GregorianDate(y, m, 1).to_heb()
    b = dates.GregorianDate(y, m, calendar.monthrange(y, m)[1]).to_heb()
    ma, mb = MONTHS.get(a.month_name(hebrew=True), a.month_name(hebrew=True)), MONTHS.get(b.month_name(hebrew=True), b.month_name(hebrew=True))
    ya, yb = a.hebrew_date_string().rsplit(' ', 1)[1], b.hebrew_date_string().rsplit(' ', 1)[1]
    if ya == yb:
        return f'{ma}–{mb} {ya}' if ma != mb else f'{ma} {ya}'
    return f'{ma} {ya}–{mb} {yb}'


def fmt(y, m=None, d=None):
    if d:
        return f'{d}.{m}.{y} ({g2h(y, m, d)})'
    if m:
        return f'{m}.{y} ({month_h(y, m)})'
    return f'{y} ({year_h(y)})'


if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    # usage: hebdate.py 31.10.1930 | 10.1930 | 1930  [--after-sunset]
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    if not args:
        print(fmt(1930, 10, 31), '|', fmt(1939), '|', fmt(1954, 1), '|', fmt(2011, 5, 19))
    for a in args:
        p = [int(x) for x in a.replace('/', '.').split('.')]
        if len(p) == 3 and '--after-sunset' in sys.argv:
            h = dates.GregorianDate(p[2], p[1], p[0]).to_heb() + 1
            print(f'{p[0]}.{p[1]}.{p[2]} ({_heb(h)}, אחרי השקיעה)')
        elif len(p) == 3:
            print(fmt(p[2], p[1], p[0]))
        elif len(p) == 2:
            print(fmt(p[1], p[0]))
        else:
            print(fmt(p[0]))
