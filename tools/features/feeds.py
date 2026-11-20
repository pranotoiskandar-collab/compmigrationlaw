#!/usr/bin/env python3
"""RSS feeds built from site/features/ (run after build_data.py; publish.py calls it).

  /feeds/decisions.xml   court decisions with a checked summary, newest decision date first (100)
  /feeds/c/<ISO2>.xml    one country: court decisions, laws and recorded changes (newest 50)
  /feeds/countries.json  the ISO2 codes that have a country feed (for the picker on /follow/)

The two older feeds stay as they are: /feed.xml (news) and /updates/feed.xml (monthly database update).
Dates are the date of the decision, law or change, so a reader sorts them by when they happened.
"""
import glob, json, os, sys
from email.utils import format_datetime
from datetime import datetime, timezone
from xml.sax.saxutils import escape

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SITE = os.path.join(ROOT, 'site')
BASE = 'https://theimr.org'


def when(d):
    """'2024-11-29', '1995-06', 1995 -> RFC 822 date, or '' if no year."""
    s = str(d or '')
    try:
        y = int(s[:4])
    except ValueError:
        return ''
    m = int(s[5:7]) if len(s) >= 7 and s[5:7].isdigit() else 1
    dd = int(s[8:10]) if len(s) >= 10 and s[8:10].isdigit() else 1
    try:
        return format_datetime(datetime(y, m, dd, 12, tzinfo=timezone.utc))
    except ValueError:
        return format_datetime(datetime(y, 1, 1, 12, tzinfo=timezone.utc))


def item(title, link, guid, date, desc, cat):
    return ('<item><title>%s</title><link>%s</link><guid isPermaLink="false">%s</guid>%s<category>%s</category>'
            '<description>%s</description></item>' % (escape(title), escape(link), escape(guid),
                                                       '<pubDate>%s</pubDate>' % when(date) if when(date) else '', escape(cat), escape(desc)))


def channel(title, link, self_url, desc, items):
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel>\n'
            '<title>%s</title><link>%s</link><atom:link href="%s" rel="self" type="application/rss+xml"/>'
            '<description>%s</description><language>en</language>\n%s\n</channel></rss>\n'
            % (escape(title), escape(link), escape(self_url), escape(desc), '\n'.join(items)))


def main():
    out = os.path.join(SITE, 'feeds')
    os.makedirs(os.path.join(out, 'c'), exist_ok=True)
    alldec, n, have = [], 0, []
    for p in sorted(glob.glob(os.path.join(SITE, 'features', 'c', '*.json'))):
        C = json.load(open(p, encoding='utf-8'))
        cc, name = C['c'], C['en']
        rows = []
        for d in C.get('dec', []):
            link = '%s/court-decisions/d/%s/' % (BASE, d['id'])
            desc = (d.get('pe') or '') + (' | ' + d['pi'] if d.get('pi') else '')
            rows.append((str(d.get('d') or ''), item('%s (%s)' % (d['n'], d.get('ct', '')), link, 'imr-dec-' + d['id'], d.get('d'),
                                                    desc, 'Court decision')))
            alldec.append((str(d.get('d') or ''), item('%s: %s (%s)' % (name, d['n'], d.get('ct', '')), link, 'imr-dec-' + d['id'],
                                                      d.get('d'), desc, 'Court decision')))
        for l in C.get('laws', []):
            if not l.get('y'):
                continue
            desc = ' '.join(x for x in (l.get('s1'), l.get('s2')) if x) or l.get('tp', '')
            rows.append((str(l['y']), item(l['t'], l.get('u') or '%s/timeline/?c=%s' % (BASE, cc), 'imr-law-' + l['k'], l['y'], desc, 'Law')))
        for i, c in enumerate(C.get('changes', [])):
            if not c.get('d'):
                continue
            rows.append((str(c['d']), item(c['en'][:120], '%s/timeline/?c=%s' % (BASE, cc), 'imr-chg-%s-%s-%d' % (cc, c['d'], i), c['d'],
                                           c['en'] + (' | ' + c['id'] if c.get('id') else ''), 'Change in the law')))
        if not rows:
            continue
        rows.sort(key=lambda r: r[0], reverse=True)
        open(os.path.join(out, 'c', cc + '.xml'), 'w', encoding='utf-8').write(channel(
            'IMR databases: %s' % name, '%s/timeline/?c=%s' % (BASE, cc), '%s/feeds/c/%s.xml' % (BASE, cc),
            'Court decisions, laws and changes in the law for %s in the Institute for Migrant Rights databases.' % name,
            [r[1] for r in rows[:50]]))
        n += 1
        have.append(cc)
    alldec.sort(key=lambda r: r[0], reverse=True)
    open(os.path.join(out, 'decisions.xml'), 'w', encoding='utf-8').write(channel(
        'IMR Court Decisions: migrant workers', BASE + '/court-decisions/', BASE + '/feeds/decisions.xml',
        'Court decisions on migrant workers with a checked plain-language summary (English and Indonesian).',
        [r[1] for r in alldec[:100]]))
    json.dump(have, open(os.path.join(out, 'countries.json'), 'w'))
    print('feeds: decisions.xml (%d) and %d country feeds' % (min(len(alldec), 100), n))


if __name__ == '__main__':
    main()
