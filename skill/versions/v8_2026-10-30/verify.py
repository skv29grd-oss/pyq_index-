# -*- coding: utf-8 -*-
"""CA-PYQ VERIFY (v8). Usage: python3 verify.py today_YYYY-MM-DD.json upload_YYYY-MM-DD.csv source.txt [outputs_dir]
Prints OK when every check passes; the untraced-figure list is a review prompt, not a failure."""
import csv, json, re, sys, glob, os, openpyxl

TODAY_JSON, UPLOAD_CSV, SOURCE_TXT = sys.argv[1], sys.argv[2], sys.argv[3]
OUT = sys.argv[4] if len(sys.argv) > 4 else '/mnt/user-data/outputs'
today = json.load(open(TODAY_JSON, encoding='utf-8'))
XLSX = os.path.join(OUT, f"CA-PYQ Match Log {today[0]['date'][:7]}.xlsx")
TAGS = ('[Intro data]', '[Issue]', '[Judgment]', '[Committee]', '[Way forward]', '[Counterpoint]', '[Ethics]')
HEAD = ['Date', 'GS Area', 'Syllabus Tag', 'Match', 'CA Topic / Headline', 'Prelims Recall (CSE 2027)', 'Mains Recall (CSE 2027)',
        'PYQ Years (all occurrences)', 'Paper(s)', 'PYQ Excerpts (all, Prelims + Mains)', 'Relevance & Revision Note',
        'Source', 'V&R Recall (Vajiram & Ravi)']

wb = openpyxl.load_workbook(XLSX, rich_text=True)
assert wb.sheetnames == ['Revision Cards', 'Master Log', 'PYQ Year Frequency', 'How to Use']
ml = wb['Master Log']
assert [c.value for c in ml[1]] == HEAD

assert len({o['date'] for o in today}) == 1, 'one date per JSON'
V8 = today[0]['date'] >= '2026-10-31'          # v8 rules apply from 31 Oct 2026
NEWS = ('The Hindu', 'Indian Express')
is_news = lambda o: o['source'].startswith(NEWS)
if V8:
    here = os.path.dirname(os.path.abspath(__file__))
    SYL = set()
    for l in open(os.path.join(here, 'syllabus.md'), encoding='utf-8'):
        if l.startswith('- ') and l.count('|') == 2:
            SYL.add(tuple(p.strip() for p in l[2:].split('|')))
    n_news = sum(1 for o in today if is_news(o)); n_web = len(today) - n_news
    assert n_news <= 15 and n_web <= 5, f'cap exceeded: {n_news} newspaper, {n_web} web'
    by_tag = {}
    for o in today:
        t = o['topic'][:40]
        parts = [p.strip() for p in o.get('tag', '').split('\u203a')]
        assert len(parts) == 4 and all(parts), f'tag must be Paper \u203a Subject \u203a Topic \u203a Subtopic: {t}'
        assert tuple(parts[:3]) in SYL, f'tag not in syllabus.md: {t} -> {parts[:3]}'
        if is_news(o):
            vt = o.get('vr_topic'); assert isinstance(vt, dict) and 'facts' in vt and 'page' in vt, f'vr_topic missing: {t}'
            assert len(vt['facts']) == 0 or 2 <= len(vt['facts']) <= 4, t
            assert all(len(f.split()) <= 25 for f in vt['facts']), t
            key = o['tag']
            if key in by_tag:
                assert by_tag[key] == vt, f'same tag, different syllabus block: {t}'
            by_tag[key] = vt
        else:
            assert not o.get('vr_topic'), f'syllabus block only for newspaper items: {t}'
for o in today:
    t = o['topic'][:40]
    assert o['match'] in ('Direct', 'Thematic', 'Emerging'), t
    assert 3 <= len(o['prelims']) <= 5 and 3 <= len(o['mains']) <= 4, t
    assert all(any(m.startswith(g) for g in TAGS) for m in o['mains']), t
    assert all(len(p.split()) <= 22 for p in o['prelims']), t
    assert all(len(m.split()) <= 25 for m in o['mains']), t
    assert any(m.startswith(('[Way forward]', '[Counterpoint]')) for m in o['mains']), t
    c = [x.lower() for x in o['prelims'] + o['mains']]
    assert len(c) == len(set(c)), f'repeated fact: {t}'
    yrs = set(re.findall(r'\b(20[12]\d)\b', o['years']))
    exc = set(re.findall(r'\b(20[12]\d)\b', o['pyq_excerpt']))
    assert yrs <= exc, (t, sorted(yrs - exc))
    assert len([l for l in o['pyq_excerpt'].splitlines() if l.strip()]) >= len(yrs), t
    nl = [l.strip() for l in o['note'].splitlines() if l.strip()]
    assert len(nl) == 3 and nl[0].startswith('[Prelims 2027]') and nl[1].startswith('[Mains 2027]') and nl[2].startswith('[Link]'), t
    assert all(len(l.split()) <= 35 for l in nl), t
    assert re.search(r'\(GS[1-4],\s*\d{1,2}(\.5)?\)', nl[1]), f'Mains line needs (GSn, marks): {t}'
    assert len(o['topic'].split()) <= 45, t
    assert 'vr' in o, f'missing vr: {t}'
    if isinstance(o['vr'], list):
        assert len(o['vr']) == 0 or 2 <= len(o['vr']) <= 4, t
        assert all(len(v.split()) <= 25 for v in o['vr']), t

up = list(csv.reader(open(UPLOAD_CSV, newline='', encoding='utf-8')))
assert up[0] == HEAD and len(up) - 1 == len(today) and all(len(r) == 13 for r in up), 'upload CSV mismatch'

src = open(SOURCE_TXT, encoding='utf-8', errors='ignore').read()
norm = lambda s: re.sub(r'[\s‐-―]+', ' ', s.replace('’', "'").replace('“', '"').replace('”', '"'))
flat = norm(src)
for o in today:
    for q in re.findall(r'"([^"]{8,120})"', norm(' | '.join([o['topic']] + o['prelims'] + o['mains']))):
        assert norm(q) in flat, f"quote not in source: {o['topic'][:40]} -> {q[:60]}"
FILLER = ('it may be noted', 'in this regard', 'it is important to note', 'needless to say', 'plays a vital role')
dig = lambda s: re.sub(r'[,\s]', '', s).rstrip('.')
flat_d, untraced = dig(flat), []
for o in today:
    blob = ' '.join([o['topic']] + o['prelims'] + o['mains'] + (o['vr'] if isinstance(o['vr'], list) else [])
                    + ((o.get('vr_topic') or {}).get('facts') or []))
    assert not any(f in blob.lower() for f in FILLER), o['topic'][:40]
    for n in set(re.findall(r'\d[\d,.]*', blob)):
        if len(dig(n)) >= 3 and dig(n) not in flat_d:
            untraced.append((o['topic'][:35], n))
print('figures not in source (confirm each is static knowledge):', untraced)

rc = wb['Revision Cards']
W = {'A': 12, 'B': 18, 'C': 34, 'D': 11, 'E': 55, 'F': 55, 'G': 58, 'H': 22, 'I': 16, 'J': 62, 'K': 55, 'L': 18, 'M': 60}
design = [
    ('cards 20/100', (rc.column_dimensions['A'].width, rc.column_dimensions['B'].width) == (20, 100)),
    ('cards gridlines off', rc.sheet_view.showGridLines is False),
    ('master widths', all(ml.column_dimensions[c].width == w for c, w in W.items())),
    ('freeze E2', ml.freeze_panes == 'E2'),
    ('autofilter', ml.auto_filter.ref == f'A1:M{ml.max_row}'),
    ('header 36', ml.row_dimensions[1].height == 36),
    ('print title', str(ml.print_title_rows).replace('$', '') == '1:1'),
    ('Calibri 12', {(c.font.name, c.font.sz) for ws in wb for r in ws.iter_rows() for c in r if c.value is not None} == {('Calibri', 12)}),
    ('body wraps', all(c.alignment.wrap_text for c in ml[2])),
    ('tab colours', [wb[n].sheet_properties.tabColor.rgb[-6:] for n in wb.sheetnames] == ['1F3864', '2E75B6', '44546A', 'A6A6A6']),
]
bad = [n for n, ok in design if not ok]
assert not bad, bad
for f in glob.glob(os.path.join(OUT, 'CA-PYQ Match Log 20??-??.xlsx')):
    ym = f[-12:-5]
    m = openpyxl.load_workbook(f, read_only=True)['Master Log']
    assert all(str(r[0])[:7] == ym for r in m.iter_rows(min_row=2, values_only=True) if r[0]), f'mixed months in {f}'
print('OK', ml.max_row - 1, 'rows')
