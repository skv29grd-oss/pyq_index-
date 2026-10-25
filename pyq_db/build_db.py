# -*- coding: utf-8 -*-
"""Build pyq_db records for one year from the raw paper text files (new unified schema)."""
import re, csv, sys, os, glob
SRC = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.dirname(os.path.abspath(__file__))
os.makedirs(OUT, exist_ok=True)
FIELDS = ['id', 'exam', 'year', 'paper', 'qno', 'part', 'section', 'marks', 'word_limit', 'subject', 'topic',
          'stem', 'options', 'answer', 'source', 'quality_flag']

def norm(t): return re.sub(r'\s+', ' ', t).strip()

def prelims(year, fn):
    txt = open(f'{SRC}/{fn}', encoding='utf-8').read()
    txt = re.sub(r'^TDMN-A-ASO \(\d+-A\)\s*$', '', txt, flags=re.M)
    pos, starts = 0, {}
    for n in range(1, 101):
        m = re.compile(rf'(?m)^{n}\.\s+').search(txt, pos)
        if not m: break
        starts[n] = m.start()
        d = re.compile(r'(?m)^\(d\)\s.*$').search(txt, m.end())
        pos = d.end() if d else m.end()
    rows = []
    for n in sorted(starts):
        end = starts.get(n + 1, len(txt))
        body = re.sub(rf'^{n}\.\s+', '', txt[starts[n]:end])
        m = re.search(r'(?m)^\(a\)\s', body)
        stem = norm(body[:m.start()]) if m else norm(body)
        opts = [f'({x}) {norm(y)}' for x, y in re.findall(r'(?ms)^\(([a-d])\)\s+(.*?)(?=^\([a-d]\)\s|\Z)', body[m.start():])] if m else []
        flag = (['options_count_%d' % len(opts)] if len(opts) != 4 else []) + ['answer_missing', 'untagged']
        rows.append(dict(id=f'P{year}-{n:03d}', exam='Prelims', year=year, paper='GS-I', qno=n, part='', section='',
                         marks=2, word_limit='', subject='', topic='', stem=stem, options=' | '.join(opts), answer='',
                         source=fn, quality_flag=';'.join(flag)))
    return rows

DEV = re.compile(r'[\u0900-\u097F]')

def mains_gs(year, paper, fn):
    L = open(f'{SRC}/{fn}', encoding='utf-8').read().splitlines()
    rows, exp, k = [], 1, 0
    first = next((i for i, l in enumerate(L) if re.match(r'^(?:Q)?1\.\s', l) and DEV.search(l)), None)
    if first is None:
        first = next(i for i, l in enumerate(L) if re.match(r'^Q1\.', l))
    k = first
    while k < len(L):
        m = re.match(rf'^(?:Q)?{exp}\.\s', L[k]) if exp <= 20 else None
        if not m or not DEV.search(L[k]):
            k += 1; continue
        j, eng = k + 1, []
        while j < len(L):
            l = L[j]
            if l.strip() and not DEV.search(l) and not l.startswith('KVMS'): eng.append(l.strip())
            if '(Answer in' in l: break
            j += 1
        t = norm(' '.join(eng))
        mm = re.search(r'\(Answer in (\d+) words\)\s*(\d+(?:\.\d+)?)\s*$', t)
        stem = norm(t[:mm.start()]) if mm else t
        rows.append(dict(id=f'M{year}-{paper}-{exp:02d}', exam='Mains', year=year, paper=paper, qno=exp, part='', section='',
                         marks=mm.group(2) if mm else '', word_limit=mm.group(1) if mm else '', subject='', topic='',
                         stem=stem, options='', answer='', source=fn,
                         quality_flag='untagged' + ('' if mm else ';marks_missing')))
        exp += 1; k = j + 1
    return rows

def mains_gs4(year, fn):
    L = open(f'{SRC}/{fn}', encoding='utf-8').read().splitlines()
    rows = []
    sec = ''
    k = 0
    def eng(s): return not re.search(r'[ऀ-ॿ]', s)
    n = 0
    while k < len(L):
        l = L[k]
        if 'SECTION—A' in l: sec = 'A'
        if 'SECTION—B' in l: sec = 'B'
        m = re.match(r'^(\d+)\.\s', l)
        if m and sec == 'A' and eng(L[k + 1] if k + 1 < len(L) else ''):
            n = int(m.group(1))
            wl = re.search(r'(\d+) words', L[k + 1]); mk = re.search(r'(\d+) marks', L[k + 1])
            j = k + 2
            while j < len(L) and not re.match(r'^\d+\.\s', L[j]) and 'SECTION' not in L[j]:
                pm = re.match(r'^\(([a-z])\)\s+(.*)', L[j])
                if pm and not eng(pm.group(2)):
                    e = next((x for x in L[j + 1:j + 4] if x.strip() and eng(x)), '')
                    pm = re.match(r'^()(.*)', e) and type('M', (), {'group': lambda self, i, p=pm.group(1), e=e: p if i == 1 else e})()
                    rows.append(dict(id=f'M{year}-GS4-{n:02d}{pm.group(1)}', exam='Mains', year=year, paper='GS4', qno=n,
                                     part=pm.group(1), section='A', marks=mk.group(1) if mk else '', word_limit=wl.group(1) if wl else '',
                                     subject='Ethics', topic='', stem=re.sub(r'\s+10$','',norm(pm.group(2))), options='', answer='', source=fn,
                                     quality_flag='untagged'))
                j += 1
            k = j; continue
        if m and sec == 'B':
            n = int(m.group(1))
            j = k + 1; case = []; parts = []; mk = ''; wl = ''
            while j < len(L) and not re.match(r'^\d+\.\s', L[j]):
                s = L[j]
                if eng(s) and s.strip():
                    am = re.match(r'^\(Answer in (\d+) words\)\s+(\d+)', s)
                    if am: wl, mk = am.group(1), am.group(2)
                    elif re.match(r'^\([a-z]\)\s', s): parts.append(norm(s))
                    elif not s.startswith('KVMS') and not s.startswith('Q'): case.append(norm(s))
                j += 1
            rows.append(dict(id=f'M{year}-GS4-{n:02d}', exam='Mains', year=year, paper='GS4', qno=n, part='', section='B',
                             marks=mk, word_limit=wl, subject='Ethics', topic='', stem=norm(' '.join(case)) + ' || ' + ' '.join(parts),
                             options='', answer='', source=fn, quality_flag='untagged;case_study'))
            k = j; continue
        k += 1
    return rows

def essay(year, fn):
    t = open(f'{SRC}/{fn}', encoding='utf-8').read()
    rows = []
    for sec, blk in re.findall(r'SECTION ([AB])\n(.*?)(?=SECTION [AB]|\Z)', t, flags=re.S):
        for n, s in re.findall(r'(?m)^(\d)\.\s+(.*)$', blk):
            rows.append(dict(id=f'E{year}-{sec}{n}', exam='Essay', year=year, paper='Essay', qno=int(n), part='', section=sec,
                             marks=125, word_limit='1000-1200', subject='Essay', topic='', stem=norm(s), options='', answer='',
                             source=fn, quality_flag='untagged'))
    return rows

def write(rows, name):
    # Raw rebuilds go to a staging folder, never over the web-verified YEAR/ files.
    # The raw 2026 .txt papers contain known errors (see README); diff staging against YEAR/ before promoting anything.
    stage = f'{OUT}/_staging_raw_build'
    os.makedirs(stage, exist_ok=True)
    with open(f'{stage}/{name}', 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, FIELDS); w.writeheader(); w.writerows(rows)

if __name__ == '__main__':
    y = 2026
    allr = prelims(y, 'UPSC CSE 2026 prelims paper.txt')
    for p, fn in (('GS1', 'UPSC CSE 2026 General Studies-I.txt'), ('GS2', 'UPSC CSE 2026 General Studies-II.txt'),
                  ('GS3', 'UPSC CSE 2026 General Studies-III.txt')):
        allr += mains_gs(y, p, fn)
    allr += mains_gs4(y, 'UPSC CSE 2026 General Studies-IV.txt')
    allr += essay(y, 'UPSC CSE 2026 mains essay paper.txt')
    names = {('Prelims', 'GS-I'): f'{y} Prelims GS1.csv', ('Essay', 'Essay'): f'{y} Mains Essay.csv'}
    for key in sorted({(r['exam'], r['paper']) for r in allr}):
        nm = names.get(key, f'{y} Mains {key[1]}.csv')
        write([r for r in allr if (r['exam'], r['paper']) == key], nm)
    import collections
    c = collections.Counter((r['exam'], r['paper']) for r in allr)
    print(dict(c))
    print('flags', collections.Counter(f for r in allr for f in r['quality_flag'].split(';')))
