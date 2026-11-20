#!/usr/bin/env python3
"""Page-ready country files for the comparison tool, the law-change timeline, the coverage map and the
plain-language law list.

Reads the published tables in data/ (never incoming/ or sources/) and writes:
  site/features/index.json      one line per country: names, which data layers exist, counts
  site/features/c/<ISO2>.json   everything the compare and timeline pages show for one country
  site/features/laws.json       every law and instrument with its plain Indonesian summary
Rerunnable; also run at publish time (tools/features/publish.py) so the files never go stale.
Usage: python3 tools/features/build_data.py [REPO_ROOT]
"""
import csv, json, os, re, sys
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import countries as CT

ROOT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(HERE))
DATA = os.path.join(ROOT, 'data')
OUT = os.path.join(ROOT, 'site', 'features')

# Decisions merged into others by the record clean-up (thread "Optimize the IMR databases and website").
DROP_DECISIONS = {'c-h-sg-2020-sghc-187', 'c-h-hk-ga-2014', 'c-h-kr-ccourt-2007hun-ma1083-2011'}

DATASETS = {
    'gcc': ('Gulf States', 'Negara-negara Teluk', '/gcc/'),
    'east-asia': ('East Asia', 'Asia Timur', '/east-asia/'),
    'southeast-asia': ('Southeast Asia', 'Asia Tenggara', '/southeast-asia/'),
    'countries-of-origin': ('Countries of Origin', 'Negara Asal', '/countries-of-origin/'),
    'domestic-workers': ('Migrant Domestic Workers', 'Pekerja Rumah Tangga Migran', '/domestic-workers/'),
    'migration-law': ('Migration Law Atlas', 'Atlas Hukum Migrasi', '/migration-law/'),
    'court-decisions': ('Court Decisions', 'Putusan Pengadilan', '/court-decisions/'),
    'legal-help': ('Find free legal help', 'Cari bantuan hukum gratis', '/legal-help/'),
}

SITUATIONS = {
    'residence': ('Residence and deportation', 'Izin tinggal dan deportasi'),
    'arrest': ('Arrest and detention', 'Penangkapan dan penahanan'),
    'fees': ('Recruitment fees and agencies', 'Biaya rekrutmen dan agen'),
    'forced': ('Forced labor and trafficking', 'Kerja paksa dan perdagangan orang'),
    'injury': ('Injury, illness or death at work', 'Kecelakaan, sakit, atau kematian saat bekerja'),
    'discrimination': ('Discrimination', 'Diskriminasi'),
    'wages': ('Unpaid wages', 'Upah tidak dibayar'),
    'health': ('Health care', 'Layanan kesehatan'),
    'dismissed': ('Dismissed or sent home', 'Dipecat atau dipulangkan'),
    'welfare': ('Social security and welfare', 'Jaminan sosial'),
    'housing': ('Housing', 'Perumahan'),
    'union': ('Joining a union', 'Bergabung dengan serikat pekerja'),
    'passport': ('Passport kept by the employer', 'Paspor ditahan majikan'),
    'coverage': ('Coverage by labor law', 'Cakupan hukum ketenagakerjaan'),
    'employer': ('Changing employer', 'Pindah majikan'),
}

LAYERS = [  # key, EN, ID
    ('laws', 'National laws listed', 'Undang-undang nasional'),
    ('coded', 'Coded legal features', 'Fitur hukum yang dikodekan'),
    ('agreements', 'Bilateral and regional agreements', 'Perjanjian bilateral dan kawasan'),
    ('treaties', 'Treaty status (ILO and UN)', 'Status perjanjian internasional (ILO dan PBB)'),
    ('decisions', 'Court decisions', 'Putusan pengadilan'),
    ('changes', 'Dated law changes', 'Perubahan hukum bertanggal'),
    ('help', 'Free legal help (checked)', 'Bantuan hukum gratis (sudah dicek)'),
]

TREATY_NAMES = {
    'C11': 'ILO C11 Right of Association (Agriculture)', 'C19': 'ILO C19 Equality of Treatment (Accident Compensation)',
    'C29': 'ILO C29 Forced Labour', 'P29': 'ILO P29 Protocol to the Forced Labour Convention',
    'C87': 'ILO C87 Freedom of Association', 'C95': 'ILO C95 Protection of Wages', 'C97': 'ILO C97 Migration for Employment',
    'C98': 'ILO C98 Right to Organise and Collective Bargaining', 'C99': 'ILO C99 Minimum Wage Fixing (Agriculture)',
    'C105': 'ILO C105 Abolition of Forced Labour', 'C110': 'ILO C110 Plantations', 'C111': 'ILO C111 Discrimination',
    'C129': 'ILO C129 Labour Inspection (Agriculture)', 'C141': 'ILO C141 Rural Workers\' Organisations',
    'C143': 'ILO C143 Migrant Workers (Supplementary Provisions)', 'C155': 'ILO C155 Occupational Safety and Health',
    'C169': 'ILO C169 Indigenous and Tribal Peoples', 'C181': 'ILO C181 Private Employment Agencies',
    'C184': 'ILO C184 Safety and Health in Agriculture', 'C188': 'ILO C188 Work in Fishing',
    'C189': 'ILO C189 Domestic Workers', 'C190': 'ILO C190 Violence and Harassment',
    'ICRMW': 'UN Migrant Workers Convention (ICRMW)', 'ICESCR': 'UN Covenant on Economic, Social and Cultural Rights',
    'ICCPR': 'UN Covenant on Civil and Political Rights', 'CEDAW': 'UN Women\'s Convention (CEDAW)',
    'CERD': 'UN Convention on Racial Discrimination (CERD)', 'CAT': 'UN Convention against Torture',
    'CRC': 'UN Convention on the Rights of the Child',
}


def rows(rel):
    p = os.path.join(DATA, rel)
    if not os.path.exists(p):
        return []
    with open(p, encoding='utf-8-sig', newline='') as f:
        return list(csv.DictReader(f))


def clean(s):
    return re.sub(r'\s+', ' ', (s or '').strip())


def year_of(s):
    m = re.search(r'(1[89]\d\d|20\d\d)', s or '')
    return int(m.group(1)) if m else None


UN_KEYS = [('Economic, Social and Cultural', 'ICESCR'), ('Civil and Political', 'ICCPR'), ('Racial Discrimination', 'CERD'),
           ('Discrimination against Women', 'CEDAW'), ('Torture', 'CAT'), ('Rights of the Child', 'CRC'),
           ('Migrant Workers and Members', 'ICRMW')]


def un_code(title):
    for k, v in UN_KEYS:
        if k.lower() in title.lower():
            return v
    m = re.search(r'\b(?:C|No\.\s*)0*(\d{2,3})\b', title)
    return f'C{m.group(1)}' if m and 'ILO' in title.upper() else None


def law_key(ds, s, title):
    return f'{ds}|{s}|{clean(title)}'


def load_summaries():
    out = {}
    for r in rows('plain-summaries/laws-id.csv'):
        out[r['key']] = r
    return out


def main():
    SUM = load_summaries()
    C = defaultdict(lambda: {'laws': [], 'coded': [], 'agreements': [], 'treaties': [], 'decisions': [],
                             'changes': [], 'help': 0, 'datasets': set()})
    all_laws = []

    def add_law(ds, s, r, title, orig, year, amended, typ, topic, url, extra=None):
        key = law_key(ds, s, title)
        sm = SUM.get(key, {})
        law = {'k': key, 'ds': ds, 'c': s, 't': clean(title), 'o': clean(orig), 'y': year, 'am': clean(amended),
               'ty': clean(typ), 'tp': clean(topic), 'u': clean(url),
               's1': sm.get('line1', ''), 's2': sm.get('line2', ''), 'chk': sm.get('check', ''),
               'why': sm.get('check_reason', '')}
        if extra:
            law.update(extra)
        all_laws.append(law)
        if s in CT.BY2:
            C[s]['laws'].append(law)
            C[s]['datasets'].add(ds)
        return law

    # National laws
    for ds, fn in [('gcc', 'gcc/domestic-laws.csv'), ('east-asia', 'east-asia/domestic-laws.csv'),
                   ('southeast-asia', 'southeast-asia/domestic-laws.csv'),
                   ('countries-of-origin', 'countries-of-origin/laws-policies.csv')]:
        for r in rows(fn):
            topic = r.get('topic', '')
            if r.get('groups') and ds == 'gcc':
                topic = f"{topic}: {r['groups']}"
            add_law(ds, r['s'], r, r['title'], r.get('orig', ''), year_of(r.get('year')), r.get('amended', ''),
                    r.get('type', ''), topic, r.get('link') if (r.get('link') or '').startswith('http') else r.get('url', ''),
                    {'no': clean(r.get('no', '')), 'chkd': clean(r.get('checked', ''))})
    # Domestic-worker instruments (national ones count for the country)
    for r in rows('domestic-workers/instruments.csv'):
        cs = [c for c in re.split(r'[;, ]+', r.get('countries', '')) if c in CT.BY2]
        tier = r.get('tier', '')
        if tier == 'bil':
            for c in cs:
                other = ', '.join(x for x in cs if x != c)
                C[c]['agreements'].append({'ds': 'domestic-workers', 'p': other, 't': clean(r['title']), 'lv': 'bilateral',
                                           'na': clean(r.get('type')), 'sg': str(year_of(r.get('year')) or ''),
                                           'if': '', 'sc': clean(r.get('sum'))[:300]})
                C[c]['datasets'].add('domestic-workers')
            continue
        s = cs[0] if tier == 'nat' and len(cs) == 1 else ('all' if tier == 'intl' else clean(r.get('countries')))
        add_law('domestic-workers', s, r, r['title'], '', year_of(r.get('year')), '', r.get('type', ''),
                r.get('sum', ''), '', {'id': r['id'], 'tier': tier})
    # Global and regional norms
    for r in rows('migration-law/migration-norms.csv'):
        add_law('migration-law', {'G': 'global', 'R': 'regional', 'N': 'national'}.get(r.get('tier'), r.get('tier', '')),
                r, r['name'], '', year_of(r.get('adopted')), '', r.get('family', ''), r.get('provisions', ''),
                r.get('link', ''), {'cit': clean(r.get('citation', '')), 'tps': clean(r.get('topics', ''))})

    # Coded features; Indonesian names and value labels from the codebooks where they exist
    CB = {}
    for r in rows('southeast-asia/codebook.csv'):
        CB[('southeast-asia', r['feature'])] = {'fi': r.get('name_id', ''), **{k: r.get(f'value_{k}', '') for k in '210'},
                                                **{k + 'i': r.get(f'value_{k}_id', '') for k in '210'}}
    for r in rows('countries-of-origin/codebook.csv'):
        d = {'fi': r.get('id', ''), **{k: r.get(f'l{k}', '') for k in '210'}, **{k + 'i': r.get(f'l{k}_id', '') for k in '210'}}
        CB[('countries-of-origin', r['k'])] = d
        CB[('southeast-asia', 'o-' + r['k'])] = d

    def add_code(ds, s, feature, fname, value, label, note, source, checked, group=''):
        if s not in CT.BY2:
            return
        cb = CB.get((ds, feature), {})
        v = clean(value)
        label = label or cb.get(v, '')
        C[s]['coded'].append({'ds': ds, 'f': feature, 'fn': clean(fname), 'fi': clean(cb.get('fi')), 'vi': clean(cb.get(v + 'i')),
                              'v': v, 'vl': clean(label),
                              'n': clean(note)[:600], 'src': clean(source)[:300], 'ok': clean(checked), 'g': clean(group)})
        C[s]['datasets'].add(ds)
    for r in rows('east-asia/codings.csv'):
        add_code('east-asia', r['state'], r['feature'], r['feature_name'], r['value'], r['value_label'], r['note'],
                 r['source'], r.get('checked_official_text', ''), r.get('group_name', ''))
    for r in rows('southeast-asia/codings.csv'):
        add_code('southeast-asia', r['state'], r['feature'], r['feature_name'], r['value'], r['value_label'], r['note'],
                 r['source'], r.get('checked_official_text', ''), r.get('group_name', ''))
    for r in rows('southeast-asia/origins.csv'):
        add_code('southeast-asia', r['country'], 'o-' + r['feature'], r['feature_name'], r['value'], '', r['note'],
                 r['source'], '', 'As a country of origin')
    for r in rows('countries-of-origin/codings.csv'):
        add_code('countries-of-origin', r['country'], r['feature'], r['feature_name'], r['value'], r['value_label'],
                 r['note'], r['source'], r.get('checked_official_text', ''))
    for r in rows('domestic-workers/codings.csv'):
        add_code('domestic-workers', r['country'], r['feature'], r['feature_name'], r['value'], r['value_label'],
                 r['note'], r['source'], '', r.get('benchmark', ''))

    # Agreements (bilateral, regional) and treaty status
    GCC_T = {}
    for ds, fn in [('east-asia', 'east-asia/instruments.csv'), ('southeast-asia', 'southeast-asia/instruments.csv'),
                   ('countries-of-origin', 'countries-of-origin/instruments.csv'), ('gcc', 'gcc/frameworks.csv')]:
        for r in rows(fn):
            s = r.get('s', '')
            if s not in CT.BY2:
                continue
            if r.get('level') == 'international':
                code = un_code(r.get('title', ''))
                if code and year_of(r.get('in_force')) and (s, code) not in GCC_T:
                    GCC_T[(s, code)] = {'i': code, 'st': (r.get('scope') or '').split(':')[0].strip() or 'party',
                                        'd': clean(r.get('in_force')), 'src': clean(r.get('url'))}
                continue
            C[s]['agreements'].append({'ds': ds, 'p': clean(r.get('partner')), 't': clean(r.get('title')),
                                       'lv': clean(r.get('level')), 'na': clean(r.get('nature')),
                                       'sg': clean(r.get('signed')), 'if': clean(r.get('in_force')),
                                       'sc': clean(r.get('scope'))[:300]})
            C[s]['datasets'].add(ds)

    rat = rows('ratifications/ratifications.csv')
    if rat:  # the tracker built in thread "Add rights checklist, case highlights and more"
        for r in rat:
            s = (r.get('iso2') or '').upper()
            if s in CT.BY2:
                ins = re.sub(r'^C0+', 'C', r['instrument'])
                C[s]['treaties'].append({'i': ins, 'st': r.get('status', ''), 'd': r.get('date_ratified') or r.get('date_signed', ''),
                                         'src': r.get('source_url', '')})
    else:
        for r in rows('atlas/ratifications.csv'):
            s = CT.iso2(r['country'])
            if s:
                C[s]['treaties'].append({'i': r['instrument'], 'st': r.get('status', ''), 'd': r.get('date', ''), 'src': ''})
    for (s, code), t in GCC_T.items():
        if not any(x['i'] == code for x in C[s]['treaties']):
            C[s]['treaties'].append(t)
    seen = {(s, t['i']) for s in C for t in C[s]['treaties']}
    for r in rows('domestic-workers/treaty-status.csv'):
        s = r['country']
        if s in CT.BY2 and (s, r['instrument']) not in seen and r.get('status') not in ('no', ''):
            C[s]['treaties'].append({'i': r['instrument'], 'st': r['status'], 'd': r.get('date', ''), 'src': ''})
            seen.add((s, r['instrument']))
    for fn in ['east-asia/treaty-status.csv', 'southeast-asia/treaty-status.csv', 'countries-of-origin/treaty-status.csv']:
        for r in rows(fn):
            ins = r.get('instrument', '')
            for s, v in r.items():
                if s in CT.BY2 and v and (s, ins) not in seen:
                    kind = {'p': 'ratified', 'a': 'accession', 'd': 'applied (declared)', 's': 'signed'}.get(v.split()[0], v.split()[0])
                    C[s]['treaties'].append({'i': ins, 'st': kind, 'd': year_of(v) or '', 'src': ''})
                    seen.add((s, ins))

    # Court decisions
    for r in rows('court-decisions/decisions.csv'):
        s = r['country']
        if r['id'] in DROP_DECISIONS or s not in CT.BY2:
            continue
        C[s]['decisions'].append({'id': r['id'], 'n': clean(r['name']), 'ct': clean(r['court']), 'd': r['date'],
                                  'st': r['status'], 'o': r['outcome'], 'fo': r['forum'],
                                  'si': [x for x in r['situations'].split(';') if x],
                                  'pe': clean(r.get('plain_en'))[:400], 'pi': clean(r.get('plain_id'))[:400]})
        C[s]['datasets'].add('court-decisions')

    # Dated law changes
    for ds, fn, col, idcol in [('east-asia', 'east-asia/developments.csv', 'jurisdiction', None),
                               ('southeast-asia', 'southeast-asia/developments.csv', 'state', 'change_id'),
                               ('countries-of-origin', 'countries-of-origin/developments.csv', 'country', None)]:
        for r in rows(fn):
            s = r.get(col, '')
            if s in CT.BY2:
                C[s]['changes'].append({'ds': ds, 'd': r['date'], 'en': clean(r['change']),
                                        'id': clean(r.get(idcol, '')) if idcol else '', 'k': r.get('kind', '')})

    # Free legal help (only entries with a checked date)
    p = os.path.join(ROOT, 'site', 'legal-help', 'places.js')
    if os.path.exists(p):
        for m in re.finditer(r'\{\s*c:\s*"([A-Z]{2})"[^{}]*?checked:\s*"\d{4}', open(p, encoding='utf-8').read()):
            if m.group(1) in CT.BY2:
                C[m.group(1)]['help'] += 1

    # Write
    os.makedirs(os.path.join(OUT, 'c'), exist_ok=True)
    for f in os.listdir(os.path.join(OUT, 'c')):
        if f.endswith('.json'):
            os.remove(os.path.join(OUT, 'c', f))
    index = []
    for s in sorted(C):
        d = C[s]
        code, num, en, idn = CT.BY2[s]
        dec = d['decisions']
        lay = {
            'laws': len(d['laws']), 'coded': len(d['coded']), 'agreements': len(d['agreements']),
            'treaties': len(d['treaties']), 'decisions': len(dec), 'changes': len(d['changes']), 'help': d['help'],
        }
        checked = {
            'decisions': sum(1 for x in dec if x['st'] in ('S', 'P')),
            'coded': sum(1 for x in d['coded'] if x['ok'] and x['ok'].lower() not in ('no', '')),
            'laws': sum(1 for x in d['laws'] if x.get('chkd') == 'yes'),
        }
        index.append({'c': s, 'n': num, 'en': en, 'id': idn, 'L': lay, 'ck': checked,
                      'ds': sorted(d['datasets']), 'k': sum(1 for v in lay.values() if v)})
        sit = Counter(x for dd in dec for x in dd['si'])
        by_year = Counter((dd['d'] or '')[:4] for dd in dec if dd['st'] == 'C' and year_of(dd['d']))
        out = {
            'c': s, 'en': en, 'id': idn, 'L': lay, 'ck': checked, 'ds': sorted(d['datasets']),
            'laws': [{k: v for k, v in l.items() if v not in ('', None)} for l in sorted(d['laws'], key=lambda l: (l['y'] or 0))],
            'coded': d['coded'], 'agreements': d['agreements'],
            'treaties': sorted(d['treaties'], key=lambda t: t['i']), 'changes': sorted(d['changes'], key=lambda x: x['d']),
            'sit': [[k, n] for k, n in sorted(sit.items())],
            'dec': [x for x in sorted(dec, key=lambda x: x['d']) if x['st'] in ('S', 'P')],
            'decC': [[y, n] for y, n in sorted(by_year.items())],
            'out': dict(Counter(x['o'] for x in dec)), 'help': d['help'],
        }
        with open(os.path.join(OUT, 'c', s + '.json'), 'w', encoding='utf-8') as f:
            json.dump(out, f, ensure_ascii=False, separators=(',', ':'))
    meta = {'layers': LAYERS, 'datasets': DATASETS, 'situations': SITUATIONS, 'treaties': TREATY_NAMES}
    with open(os.path.join(OUT, 'index.json'), 'w', encoding='utf-8') as f:
        json.dump({'meta': meta, 'countries': index}, f, ensure_ascii=False, separators=(',', ':'))
    laws = [{k: v for k, v in l.items() if v not in ('', None)} for l in all_laws]
    with open(os.path.join(OUT, 'laws.json'), 'w', encoding='utf-8') as f:
        json.dump({'meta': {'datasets': DATASETS}, 'names': {s: [CT.BY2[s][2], CT.BY2[s][3]] for s in CT.BY2},
                   'laws': laws}, f, ensure_ascii=False, separators=(',', ':'))
    print(f'build_data: {len(index)} countries, {len(all_laws)} laws ({sum(1 for l in all_laws if l["s2"])} with a plain summary)')


if __name__ == '__main__':
    main()
