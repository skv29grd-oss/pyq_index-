# -*- coding: utf-8 -*-
"""Import a transcribed UPSC Mains GS paper (bilingual text) into 'Mains GSn YEAR.csv'.
Usage: python3 import_gs_text.py <transcript.txt> <GS1|GS2|GS3|GS4> <year> <source-label>"""
import re, csv, sys, os
FIELDS = ['id','exam','year','paper','qno','part','section','marks','word_limit','subject','topic','stem','options','answer','source','quality_flag']
DEV = re.compile(r'[ऀ-ॿ]')
def main(fn, paper, year, src):
    L = open(fn, encoding='utf-8').read().splitlines()
    rows, n = [], 0
    for k, l in enumerate(L):
        m = re.search(r'\(Answer in (\d+) words\)\s*$', l)
        if not m or DEV.search(l):
            continue
        mk = re.search(r'\((\d+(?:\.\d+)?)\s*Marks?\)', ' '.join(L[k + 1:k + 3]))
        stem = re.sub(r'^\s*[\*\-•]?\s*', '', l[:m.start()]).strip()
        n += 1
        rows.append(dict(id=f'M{year}-{paper}-{n:02d}', exam='Mains', year=year, paper=paper, qno=n, part='', section='',
                         marks=mk.group(1) if mk else '', word_limit=m.group(1), subject='', topic='', stem=stem,
                         options='', answer='', source=src, quality_flag='untagged;transcribed' + ('' if mk else ';marks_missing')))
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), f'Mains {paper} {year}.csv')
    with open(out, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, FIELDS); w.writeheader(); w.writerows(rows)
    print(out, len(rows), 'questions; marks total', sum(float(r['marks'] or 0) for r in rows))
if __name__ == '__main__':
    main(*sys.argv[1:5])
