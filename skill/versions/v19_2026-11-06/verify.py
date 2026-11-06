# -*- coding: utf-8 -*-
"""CA-PYQ VERIFY (v19). Usage: python3 verify.py today_YYYY-MM-DD.json upload_YYYY-MM-DD.csv source.txt [outputs_dir]
Run from the folder holding pyq_bank.json (load_pyq.py output).
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
assert wb.sheetnames == ['Revision Cards', 'Master Log', 'PYQ Year Frequency', 'PYQ Bank', 'How to Use']
ml = wb['Master Log']
assert [c.value for c in ml[1]] == HEAD

assert len({o['date'] for o in today}) == 1, 'one date per JSON'
V8 = today[0]['date'] >= '2026-10-31'          # v8 rules apply from 31 Oct 2026
V19 = today[0]['date'] >= '2026-11-04'         # v19: rows store PYQ IDs (pyq_ids); text comes from the PYQ bank
BANK = json.load(open('pyq_bank.json', encoding='utf-8')) if os.path.exists('pyq_bank.json') else None
assert not V19 or BANK, 'pyq_bank.json not found: run verify from the folder where load_pyq.py wrote it'
ID_RX = re.compile(r'^[PME]20\d\d-[A-Za-z0-9&-]+$')
PAPER_ORDER = ['Prelims', 'GS1', 'GS2', 'GS3', 'GS4', 'Essay']
def pyq_line(k):
    v = BANK[k]
    if v['exam'] == 'Prelims':
        return f"P {v['year']}: {v['text']}"
    return f"{v['paper']} {v['year']}" + (f" ({v['marks']})" if v['marks'] else '') + f": {v['text']}"
def excerpt_lines(o):
    if V19:
        return [pyq_line(k) for k in o['pyq_ids']] or ['No PYQ match in corpus']
    return [l.strip() for l in o['pyq_excerpt'].splitlines() if l.strip()]
VR_CACHE = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'vr_topics.json'), encoding='utf-8'))
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
        area = 'Essay' if parts[0] == parts[1] else f'{parts[0]} {parts[1]}'   # v18: GS Area = tag Paper + Subject
        assert o.get('gs_area') == area, f'GS Area must be "{area}" (Paper + Subject of the tag), got "{o.get("gs_area")}": {t}'
        if is_news(o):
            vt = o.get('vr_topic'); assert isinstance(vt, dict) and 'facts' in vt and 'page' in vt, f'vr_topic missing: {t}'
            assert len(vt['facts']) == 0 or 2 <= len(vt['facts']) <= 4, t
            assert all(len(f.split()) <= 25 for f in vt['facts']), t
            cached = VR_CACHE.get(parts[3])        # v19: permanent V&R cache keyed by Subtopic
            assert cached is not None, f'Subtopic not in data/vr_topics.json (run vr_cache.py add): {parts[3]}'
            assert vt == {'page': cached['page'], 'facts': cached['facts']}, f'vr_topic differs from the cache (run vr_cache.py fill): {parts[3]}'
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
    if V19:
        ids = o.get('pyq_ids')
        assert isinstance(ids, list), f'v19: pyq_ids list required: {t}'
        assert not ({'years', 'papers', 'pyq_excerpt'} & set(o)), f'v19: years/papers/pyq_excerpt are derived from pyq_ids, do not write them: {t}'
        assert all(isinstance(k, str) and ID_RX.match(k) and k in BANK for k in ids), f'unknown PYQ ID: {t} -> {[k for k in ids if k not in BANK]}'
        assert len(ids) == len(set(ids)), f'duplicate PYQ ID: {t}'
        yp = [(BANK[k]['year'], BANK[k]['paper']) for k in ids]
        assert len(yp) == len(set(yp)), f'one PYQ per year per paper: {t}'
        assert o['match'] == 'Emerging' or ids, f'Direct/Thematic row needs at least one PYQ ID: {t}'
    else:
        yrs = set(re.findall(r'\b(20[12]\d)\b', o['years']))
        exc = set(re.findall(r'\b(20[12]\d)\b', o['pyq_excerpt']))
        assert yrs <= exc, (t, sorted(yrs - exc))
        assert len([l for l in o['pyq_excerpt'].splitlines() if l.strip()]) >= len(yrs), t
    nl = [l.strip() for l in o['note'].splitlines() if l.strip()]
    assert len(nl) == 3 and nl[0].startswith('[Prelims 2027]') and nl[1].startswith('[Mains 2027]') and nl[2].startswith('[Link]'), t
    assert all(len(l.split()) <= 35 for l in nl), t
    assert re.search(r'\(GS[1-4],\s*\d{1,2}(\.5)?\)', nl[1]), f'Mains line needs (GSn, marks): {t}'
    assert len(o['topic'].split()) <= 45, t
    if not V8:                                    # legacy rows only
        assert 'vr' in o, f'missing vr: {t}'
    else:
        assert not o.get('vr'), f'v9: merge V&R daily facts into recall, not a vr field: {t}'

V10 = today[0]['date'] >= '2026-11-01'           # v10: full PYQ text, no cap, one Master Log sub-row per PYQ
PYQ_RX = re.compile(r'^(P 20\d\d|(GS[1-4]|Essay) 20\d\d( \([^)]*\))?): \S')
if V10:
    n_sub = 0
    for o in today:
        lines = excerpt_lines(o)
        n_sub += len(lines)
        if o['match'] == 'Emerging' and lines == ['No PYQ match in corpus']:
            continue
        assert all(PYQ_RX.match(l) for l in lines), f"PYQ line format: {o['topic'][:40]}"
        assert not any(l.endswith('\u2026') or re.match(r'^\+\d+ more', l) for l in lines), f"truncated/capped PYQs: {o['topic'][:40]}"
    got = sum(1 for r in ml.iter_rows(min_row=2, values_only=True) if str(r[0])[:10] == today[0]['date'])
    assert got == n_sub, f'Master Log sub-rows {got} != PYQ lines {n_sub}'
if V19:                                           # full text in the workbook comes from the bank
    from collections import Counter
    want = Counter(BANK[k]['text'] for o in today for k in o['pyq_ids'])
    have = Counter(r[9] for r in ml.iter_rows(min_row=2, values_only=True) if str(r[0])[:10] == today[0]['date'] and r[9] in want)
    assert have == want, 'Master Log PYQ text does not match the PYQ bank'
    bank_ids = {r[0] for r in wb['PYQ Bank'].iter_rows(min_row=2, values_only=True)}
    assert {k for o in today for k in o['pyq_ids']} <= bank_ids, 'PYQ Bank tab misses an ID of this date'

up = list(csv.reader(open(UPLOAD_CSV, newline='', encoding='utf-8')))
assert up[0] == HEAD and len(up) - 1 == len(today) and all(len(r) == 13 for r in up), 'upload CSV mismatch'
if V19:                                           # CSV keeps IDs, never question text
    for r in up[1:]:
        cell = [l for l in r[9].split('\n') if l]
        assert cell == ['No PYQ match in corpus'] or all(ID_RX.match(l) for l in cell), f'v19 CSV must hold PYQ IDs: {r[4][:40]}'
        if cell != ['No PYQ match in corpus']:
            assert r[7] == ', '.join(sorted({BANK[k]['year'] for k in cell})), f'PYQ Years not derived from IDs: {r[4][:40]}'

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
    blob = ' '.join([o['topic']] + o['prelims'] + o['mains'] + (o.get('vr') if isinstance(o.get('vr'), list) else [])
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
    ('tab colours', [wb[n].sheet_properties.tabColor.rgb[-6:] for n in wb.sheetnames] == ['1F3864', '2E75B6', '44546A', '8497B0', 'A6A6A6']),
    ('bank freeze/filter', wb['PYQ Bank'].freeze_panes == 'B2' and wb['PYQ Bank'].auto_filter.ref == f"A1:H{wb['PYQ Bank'].max_row}"),
]
bad = [n for n, ok in design if not ok]
assert not bad, bad
for f in glob.glob(os.path.join(OUT, 'CA-PYQ Match Log 20??-??.xlsx')):
    ym = f[-12:-5]
    m = openpyxl.load_workbook(f, read_only=True)['Master Log']
    assert all(str(r[0])[:7] == ym for r in m.iter_rows(min_row=2, values_only=True) if r[0]), f'mixed months in {f}'
print('OK', len(today), 'items,', ml.max_row - 1, 'Master Log sub-rows')
