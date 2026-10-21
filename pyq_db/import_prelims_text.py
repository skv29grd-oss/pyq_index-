# -*- coding: utf-8 -*-
"""Import a bilingual Prelims transcript ('#### Qn.' / '**English:**' / '**Hindi:**').
Usage: python3 import_prelims_text.py <transcript.md> <year> <source-label>"""
import re, csv, sys, os
FIELDS = ['id','exam','year','paper','qno','part','section','marks','word_limit','subject','topic','stem','options','answer','source','quality_flag']
def norm(t): return re.sub(r'\s+', ' ', t.replace('​', '')).strip()

def tables(txt):
    out = []
    for l in txt.splitlines():
        if l.strip().startswith('|'):
            if re.match(r'^\s*\|[\s:\-|]+\|\s*$', l): continue
            cells = [c.strip() for c in l.strip().strip('|').split('|')]
            out.append('[' + ' / '.join(c for c in cells if c) + ']')
        else: out.append(l)
    return '\n'.join(out)

def main(fn, year, src):
    t = open(fn, encoding='utf-8').read()
    blocks = re.split(r'(?m)^#{2,4}\s*Q(\d+)\.\s*$', t)
    rows, bad = [], []
    for k in range(1, len(blocks), 2):
        n, body = int(blocks[k]), blocks[k + 1]
        m = re.search(r'\*\*English:\*\*(.*?)(?=\*\*Hindi:\*\*|\Z)', body, re.S)
        if not m: bad.append((n, 'no English')); continue
        eng = tables(re.sub(r'\n---\s*$', '', m.group(1).strip()))
        a = re.search(r'(?m)^\(a\)\s', eng)
        stem = norm(eng[:a.start()]) if a else norm(eng)
        opts = [f'({x}) {norm(y)}' for x, y in re.findall(r'(?ms)^\(([a-d])\)\s+(.*?)(?=^\([a-d]\)\s|\Z)', eng[a.start():])] if a else []
        flags = (['options_count_%d' % len(opts)] if len(opts) != 4 else []) + ['answer_missing', 'untagged', 'transcribed']
        if len(opts) != 4: bad.append((n, f'{len(opts)} options'))
        rows.append(dict(id=f'P{year}-{n:03d}', exam='Prelims', year=year, paper='GS-I', qno=n, part='', section='', marks=2,
                         word_limit='', subject='', topic='', stem=stem, options=' | '.join(opts), answer='', source=src,
                         quality_flag=';'.join(flags)))
    nums = [r['qno'] for r in rows]
    print('questions', len(rows), 'missing', sorted(set(range(1, 101)) - set(nums)), 'dups', sorted({x for x in nums if nums.count(x) > 1}), 'bad', bad)
    if '--dry' in sys.argv: return rows
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'Prelims {year}.csv')
    with open(out, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, FIELDS); w.writeheader(); w.writerows(sorted(rows, key=lambda r: r['qno']))
    print(out)
    return rows

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])
