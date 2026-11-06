"""Build the PYQ search files for the ca-pyq-daily-match skill.

Usage:  python3 load_pyq.py <repo dir>
Writes: mains_recs.json   [{paper, year, text, marks}]  (GS1-GS4 + Essay)
        prelims_lines.txt one Prelims question per line; full year papers as 'YYYY Qn: stem'
        pyq_bank.json     {PYQ ID: {exam, paper, year, marks, q, text}} for every Prelims and Mains question.
                          IDs: pyq_db `id` column (P2021-001, M2021-GS3-07, M2026-GS4-03b, E2026-A1);
                          old-index Prelims records 'MoH Q13 (2012) [...]: text' -> P2012-MoH-Q13.

Single source per year (no duplicates):
  - pyq_db/<year>/<year> <paper>.csv (the only copy): Prelims 2013-2026, Mains 2013-2026
    (official papers; Mains 2024 and 2025-26 web-verified)
  - old *_Index.txt files: Prelims 2011-2012 only (no Mains years remain)
"""
import csv, glob, json, os, re, sys
from collections import Counter

D = sys.argv[1] if len(sys.argv) > 1 else '.'
# old-index years per Mains paper (a year can move to pyq_db paper by paper)
YRS_OLD = {i: r'(?!x)x' for i in (1, 2, 3, 4)}   # never matches: no Mains years left in the old indexes

MARKS = {'2.5', '5', '7.5', '8', '10', '12.5', '15', '20', '25'}
recs = []
for i in (1, 2, 3, 4):
    START = re.compile(rf'(?<!\S)\d{{1,3}}\s+({YRS_OLD[i]})\s+(?=\S)')
    txt = open(f'{D}/GS{i}_Index.txt', encoding='utf-8', errors='ignore').read()
    txt = txt.split('[NOTE: This is a plain-text extraction')[0]          # drop trailing file notes
    st = list(START.finditer(txt))
    for k, m in enumerate(st):
        end = st[k + 1].start() if k + 1 < len(st) else len(txt)
        body = re.sub(r'\s+', ' ', txt[m.end():end]).strip()
        # cut section headings that sit between this record and the next one
        body = re.split(r' (?:\[[^\]]*\]|Qs\. No\.|No\. Qs\.|={3,}|SECTION-|[A-Z][A-Z &,/()-]{6,}(?= [A-Z][a-z]))', body)[0].strip()
        nums = [t for t in re.findall(r'(?<![\d.])(\d{1,2}(?:\.5)?)(?![\d.])', body) if t in MARKS]
        if len(body) >= 25:
            recs.append({'paper': f'GS{i}', 'year': m.group(1), 'text': body, 'marks': nums[-1] if nums else ''})

P = [l for fn in sorted(glob.glob(f'{D}/Prelims_Index*.txt'))
     for l in open(fn, encoding='utf-8', errors='ignore').read().splitlines()]

bank_db = []
db_years = sorted(int(os.path.basename(p)) for p in glob.glob(f'{D}/pyq_db/20[0-9][0-9]') if os.path.isdir(p))
for y in db_years:
    for path in sorted(glob.glob(f'{D}/pyq_db/{y}/{y} *.csv')):
        rows = list(csv.DictReader(open(path, encoding='utf-8', newline='')))
        name = os.path.basename(path)[len(str(y)) + 1:-4]          # 'Prelims GS1', 'Mains GS2', 'Mains Essay'
        if name.startswith('Prelims'):
            assert [int(r['qno']) for r in rows] == list(range(1, 101)), f'{path}: Prelims must have Q1-Q100'
            P += [f"{y} Q{r['qno']}: {r['stem']} Options: {r['options']}" for r in rows]
            bank_db += [(r['id'], {'exam': 'Prelims', 'paper': 'Prelims', 'year': str(y), 'marks': r['marks'], 'q': f"Q{r['qno']}",
                                   'text': f"{r['stem']} Options: {r['options']}"}) for r in rows]
        else:
            paper = name.split()[-1].replace('Essay', 'Essay')
            tot = sum(float(r['marks']) for r in rows)
            assert tot == (1000 if paper == 'Essay' else 250), f'{path}: marks {tot}'
            for r in rows:
                label = f"Q{r['qno']}{'(' + r['part'] + ')' if r['part'] else ''}"
                recs.append({'paper': paper, 'year': str(y), 'text': r['stem'], 'marks': r['marks'], 'q': label, 'id': r['id']})
                bank_db.append((r['id'], {'exam': 'Mains', 'paper': paper, 'year': str(y), 'marks': r['marks'], 'q': label, 'text': r['stem']}))

json.dump(recs, open('mains_recs.json', 'w', encoding='utf-8'), ensure_ascii=False)

# PYQ bank: one entry per question, keyed by a stable ID (CA-PYQ rows store IDs, the workbook shows the text)
bank = {}
def put(k, v):
    assert k not in bank, f'duplicate PYQ ID {k}'
    bank[k] = v
for k, v in bank_db:
    assert re.match(rf"^[PME]{v['year']}-", k), f'ID/year mismatch: {k}'
    put(k, v)
OLD_P = re.compile(r'^([A-Za-z&]+) (Q\d+) \((20\d\d)\)(?: \[[^\]]*\])?: (.*)$')
for l in P:
    if re.match(r'^20\d\d Q\d+:', l):
        continue
    m = OLD_P.match(l)
    multi = re.match(r'^[A-Za-z&]+ Q\d+ \((20\d\d(?:/20\d\d)+)\)', l)
    if multi and all(int(y) in db_years for y in multi.group(1).split('/')):
        continue                                    # e.g. 'AC Q42 (2014/2015)': every year already in pyq_db
    assert m or not re.match(r'^[A-Za-z&]+ Q\d+ \(', l), f'old-index Prelims record not parsed: {l[:80]}'
    if m:
        put(f'P{m.group(3)}-{m.group(1)}-{m.group(2)}', {'exam': 'Prelims', 'paper': 'Prelims', 'year': m.group(3),
                                                       'marks': '', 'q': f'{m.group(1)} {m.group(2)}', 'text': m.group(4).strip()})
k_old = Counter()
for r in recs:
    if 'id' not in r:                               # old-index Mains record (none at present)
        k_old[(r['year'], r['paper'])] += 1
        r['id'] = f"M{r['year']}-{r['paper']}-IX{k_old[(r['year'], r['paper'])]:03d}"
        put(r['id'], {'exam': 'Mains', 'paper': r['paper'], 'year': r['year'], 'marks': r['marks'], 'q': '', 'text': r['text']})
json.dump(recs, open('mains_recs.json', 'w', encoding='utf-8'), ensure_ascii=False)
json.dump(bank, open('pyq_bank.json', 'w', encoding='utf-8'), ensure_ascii=False)
open('prelims_lines.txt', 'w', encoding='utf-8').write('\n'.join(P))

# duplicate guard: a year must come from exactly one source
old_keys = {(r['paper'], r['year']) for r in recs if 'q' not in r}
db_keys = {(r['paper'], r['year']) for r in recs if 'q' in r}
assert not old_keys & db_keys, 'a pyq_db paper-year is also present in the old index'
print('mains records:', dict(sorted(Counter((r['paper'], r['year']) for r in recs if r['year'] in map(str, db_years)).items())),
      '| old index Mains records:', sum(1 for r in recs if 'q' not in r))
print('pyq bank:', len(bank), 'IDs |', dict(sorted(Counter(v['paper'] for v in bank.values()).items())))
print('prelims lines:', len(P), '| full-paper stems by year:',
      dict(sorted(Counter(l[:4] for l in P if re.match(r'^20\d\d Q\d+:', l)).items())))
