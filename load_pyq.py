"""Build the PYQ search files for the ca-pyq-daily-match skill.

Usage:  python3 load_pyq.py <repo dir>
Writes: mains_recs.json   [{paper, year, text, marks}]  (GS1-GS4 + Essay)
        prelims_lines.txt one Prelims question per line; full year papers as 'YYYY Qn: stem'

Single source per year (no duplicates):
  - 2022 onwards: pyq_db/<year>/<year> <paper>.csv  (the only copy; 2022-24 from official papers, 2025-26 web-verified)
  - 2013-2021 Mains / 2011-2021 Prelims: the old *_Index.txt files
"""
import csv, glob, json, os, re, sys
from collections import Counter

D = sys.argv[1] if len(sys.argv) > 1 else '.'
YRS_OLD = r'20(?:1[3-9]|2[01])'

START = re.compile(rf'(?<!\S)\d{{1,3}}\s+({YRS_OLD})\s+(?=\S)')
MARKS = {'2.5', '5', '7.5', '8', '10', '12.5', '15', '20', '25'}
recs = []
for i in (1, 2, 3, 4):
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

db_years = sorted(int(os.path.basename(p)) for p in glob.glob(f'{D}/pyq_db/20[0-9][0-9]') if os.path.isdir(p))
for y in db_years:
    for path in sorted(glob.glob(f'{D}/pyq_db/{y}/{y} *.csv')):
        rows = list(csv.DictReader(open(path, encoding='utf-8', newline='')))
        name = os.path.basename(path)[len(str(y)) + 1:-4]          # 'Prelims GS1', 'Mains GS2', 'Mains Essay'
        if name.startswith('Prelims'):
            assert [int(r['qno']) for r in rows] == list(range(1, 101)), f'{path}: Prelims must have Q1-Q100'
            P += [f"{y} Q{r['qno']}: {r['stem']} Options: {r['options']}" for r in rows]
        else:
            paper = name.split()[-1].replace('Essay', 'Essay')
            tot = sum(float(r['marks']) for r in rows)
            assert tot == (1000 if paper == 'Essay' else 250), f'{path}: marks {tot}'
            for r in rows:
                label = f"Q{r['qno']}{'(' + r['part'] + ')' if r['part'] else ''}"
                recs.append({'paper': paper, 'year': str(y), 'text': r['stem'], 'marks': r['marks'], 'q': label})

json.dump(recs, open('mains_recs.json', 'w', encoding='utf-8'), ensure_ascii=False)
open('prelims_lines.txt', 'w', encoding='utf-8').write('\n'.join(P))

# duplicate guard: a year must come from exactly one source
old_years = {r['year'] for r in recs if 'q' not in r}
assert not old_years & {str(y) for y in db_years}, 'a pyq_db year is also present in the old index'
print('mains records:', dict(sorted(Counter((r['paper'], r['year']) for r in recs if r['year'] in map(str, db_years)).items())),
      '| old index 2013-2021:', sum(1 for r in recs if 'q' not in r))
print('prelims lines:', len(P), '| full-paper stems by year:',
      dict(sorted(Counter(l[:4] for l in P if re.match(r'^20\d\d Q\d+:', l)).items())))
