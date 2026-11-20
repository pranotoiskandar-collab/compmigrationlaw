#!/usr/bin/env python3
"""Follow-a-country alerts: what was added for each country since a given commit.

Compares the published tables in data/ (never incoming/ or sources/) at an earlier commit with the current tree and
writes, for every country with something new, a short bilingual email (English, then Indonesian):
  <out>/<ISO2>/subject.txt, email.html, email.txt      and <out>/summary.json
With --buttondown and the BUTTONDOWN_API_KEY environment variable, each email is also created in Buttondown as a
DRAFT. Nothing is ever sent automatically: a person opens the draft, chooses the subscribers tagged country-<ISO2>
and presses Send.

Usage:  python3 tools/alerts/alerts.py --since "7 days ago" --out alerts-out [--buttondown]
        python3 tools/alerts/alerts.py --base <commit> --out alerts-out
"""
import argparse, csv, html, io, json, os, subprocess, sys, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, 'tools', 'features'))
import countries as CT

SITE = 'https://theimr.org'
LAWS = [('gcc/domestic-laws.csv', 's'), ('east-asia/domestic-laws.csv', 's'), ('southeast-asia/domestic-laws.csv', 's'),
        ('countries-of-origin/laws-policies.csv', 's')]
DEV = [('east-asia/developments.csv', 'jurisdiction', 'change', None), ('southeast-asia/developments.csv', 'state', 'change', 'change_id'),
       ('countries-of-origin/developments.csv', 'country', 'change', None)]


def git(*a):
    return subprocess.run(['git', '-C', ROOT] + list(a), capture_output=True, text=True, check=True).stdout


def table(rel, ref):
    try:
        t = git('show', f'{ref}:data/{rel}') if ref else open(os.path.join(ROOT, 'data', rel), encoding='utf-8').read()
    except (subprocess.CalledProcessError, OSError):
        return []
    return list(csv.DictReader(io.StringIO(t.lstrip('﻿'))))


def changes(base):
    new = {}
    def add(c, kind, en, idn, link=''):
        if c in CT.BY2:
            new.setdefault(c, []).append({'k': kind, 'en': en, 'id': idn, 'u': link})
    for rel, col in LAWS:
        old = {(r[col], r['title']) for r in table(rel, base)}
        for r in table(rel, None):
            if (r[col], r['title']) not in old:
                y = f" ({r['year']})" if r.get('year') else ''
                add(r[col], 'law', r['title'] + y, r['title'] + y, r.get('link') if (r.get('link') or '').startswith('http') else r.get('url', ''))
    old = {r['id'] for r in table('court-decisions/decisions.csv', base)}
    for r in table('court-decisions/decisions.csv', None):
        if r['id'] not in old:
            add(r['country'], 'decision', f"{r['name']} ({r['court']}, {r['date']})", f"{r['name']} ({r['court']}, {r['date']})",
                f"{SITE}/court-decisions/d/{r['id']}/")
    for rel, col, txt, idcol in DEV:
        old = {(r[col], r['date'], r[txt]) for r in table(rel, base)}
        for r in table(rel, None):
            if (r[col], r['date'], r[txt]) not in old:
                add(r[col], 'change', f"{r['date']}: {r[txt]}", f"{r['date']}: {r.get(idcol) or r[txt]}" if idcol else f"{r['date']}: {r[txt]}")
    old = {r['id'] for r in table('domestic-workers/instruments.csv', base)}
    for r in table('domestic-workers/instruments.csv', None):
        if r['id'] not in old and r.get('tier') == 'nat':
            add(r['countries'], 'law', f"{r['title']} ({r['year']})", f"{r['title']} ({r['year']})")
    return new


HEAD = {'law': ('Laws and regulations', 'Undang-undang dan peraturan'), 'decision': ('Court decisions', 'Putusan pengadilan'),
        'change': ('Changes in the law', 'Perubahan hukum')}


def email(c, items):
    en, idn = CT.BY2[c][2], CT.BY2[c][3]
    subject = f'New for {en} / Baru untuk {idn}: {len(items)} ' + ('entry' if len(items) == 1 else 'entries')
    E = html.escape
    parts_h, parts_t = [], []
    for lang, i, intro, outro in [
        ('en', 0, f'We added the following for {en} to the IMR databases.',
         'Unchecked entries are marked as such on the site. Summaries are not legal advice.'),
        ('id', 1, f'Kami menambahkan entri berikut untuk {idn} ke basis data IMR.',
         'Entri yang belum diperiksa diberi tanda di situs. Ringkasan bukan nasihat hukum.')]:
        h = [f'<p>{E(intro)}</p>']; t = [intro, '']
        for k in ('law', 'decision', 'change'):
            xs = [x for x in items if x['k'] == k]
            if not xs:
                continue
            h.append(f'<h3>{E(HEAD[k][i])}</h3><ul>')
            t.append(HEAD[k][i].upper())
            for x in xs:
                label = x[lang]
                h.append(f'<li><a href="{E(x["u"])}">{E(label)}</a></li>' if x['u'] else f'<li>{E(label)}</li>')
                t.append(f'- {label}' + (f' <{x["u"]}>' if x['u'] else ''))
            h.append('</ul>'); t.append('')
        tl = f'{SITE}/timeline/?c={c}' + ('&lang=id' if lang == 'id' else '')
        h.append(f'<p><a href="{tl}">' + ('See the timeline for ' + E(en) if lang == 'en' else 'Lihat lini masa ' + E(idn)) + '</a> · '
                 f'<a href="{SITE}/compare/?a={c}">' + ('Compare' if lang == 'en' else 'Bandingkan') + '</a></p>'
                 f'<p style="color:#555;font-size:14px">{E(outro)}</p>')
        t += [tl, outro, '']
        parts_h.append(''.join(h)); parts_t.append('\n'.join(t))
    body_h = parts_h[0] + '<hr>' + parts_h[1] + ('<p style="color:#555;font-size:13px">Institute for Migrant Rights · '
             'You receive this because you chose to follow this country at theimr.org/follow/. / Anda menerima surel ini karena memilih '
             'mengikuti negara ini di theimr.org/follow/.</p>')
    return subject, body_h, '\n----\n\n'.join(parts_t)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--since', default='7 days ago')
    ap.add_argument('--base')
    ap.add_argument('--out', default='alerts-out')
    ap.add_argument('--buttondown', action='store_true')
    a = ap.parse_args()
    base = a.base or git('rev-list', '-1', f'--before={a.since}', 'HEAD').strip()
    if not base:
        print('alerts: no commit before', a.since); return
    new = changes(base)
    os.makedirs(a.out, exist_ok=True)
    summary = {'base': base, 'countries': {}}
    key = os.environ.get('BUTTONDOWN_API_KEY', '')
    for c, items in sorted(new.items()):
        subject, body_h, body_t = email(c, items)
        d = os.path.join(a.out, c); os.makedirs(d, exist_ok=True)
        open(os.path.join(d, 'subject.txt'), 'w').write(subject + '\n')
        open(os.path.join(d, 'email.html'), 'w').write(body_h)
        open(os.path.join(d, 'email.txt'), 'w').write(body_t)
        summary['countries'][c] = len(items)
        if a.buttondown and key:
            req = urllib.request.Request('https://api.buttondown.com/v1/emails', method='POST',
                                         data=json.dumps({'subject': f'[country-{c}] ' + subject, 'body': body_h, 'status': 'draft'}).encode(),
                                         headers={'Authorization': f'Token {key}', 'Content-Type': 'application/json'})
            with urllib.request.urlopen(req, timeout=30) as r:
                print(f'alerts: Buttondown draft for {c}: HTTP {r.status}')
    json.dump(summary, open(os.path.join(a.out, 'summary.json'), 'w'), indent=1)
    print(f'alerts: {len(new)} countries with new entries since {base[:10]}:', ', '.join(f'{c} {n}' for c, n in summary['countries'].items()) or 'none')


if __name__ == '__main__':
    main()
