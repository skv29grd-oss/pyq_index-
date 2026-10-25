# -*- coding: utf-8 -*-
"""Import a GS Paper IV transcript (labelled '* English:' lines; case studies 'N. Case Study k:').
Usage: python3 import_gs4_text.py <transcript.txt> <year> <source-label>"""
import re, csv, sys, os
FIELDS = ['id','exam','year','paper','qno','part','section','marks','word_limit','subject','topic','stem','options','answer','source','quality_flag']
DEV = re.compile(r'[ऀ-ॿ]')
def norm(t): return re.sub(r'\s+', ' ', t).strip()
TAIL = re.compile(r'\(Answer in (\d+) words\)\s*(?:[—–-]\s*(\d+(?:\.\d+)?)\s*Marks?)?\s*$')

def main(fn, year, src):
    L = open(fn, encoding='utf-8').read().replace('​', '').splitlines()
    rows = []
    secB = next(i for i, l in enumerate(L) if re.search(r"SECTION 'B'", l))
    # ---- Section A
    i, n, intro, dflt_wl = 0, 0, '', ''
    while i < secB:
        l = L[i]
        m = re.match(r'^(\d+)\.\s*(?:\(([a-z])\))?\s*(.*)$', l)
        if m:
            n = int(m.group(1)); rest = m.group(3)
            if rest and DEV.search(rest):          # shared-header question (Q3 quotations)
                hw = re.search(r'(\d+)\s*शब्दों', rest); dflt_wl = hw.group(1) if hw else ''
                intro = 'Quotation — what does it convey in the present context? '
            else:
                intro = ''; dflt_wl = ''
            i += 1; continue
        e = re.match(r'^\s*\*\s*English:\s*(.*)$', l)
        if e:
            t = norm(e.group(1))
            mm = re.search(r'\s*[—–-]\s*(\d+(?:\.\d+)?)\s*Marks?\s*$', t); mk = mm.group(1) if mm else ''
            if mm: t = t[:mm.start()]
            tm = TAIL.search(t); wl = tm.group(1) if tm else dflt_wl
            stem = norm(t[:tm.start()]) if tm else norm(t)
            lab = ''
            for j in range(i - 1, max(i - 4, -1), -1):
                pm = re.match(r'^\s*(?:\*\s*)?(?:\d+\.\s*)?\(([a-z])\)\s*$', L[j])
                if pm: lab = pm.group(1); break
            rows.append(dict(id=f'M{year}-GS4-{n:02d}{lab}', exam='Mains', year=year, paper='GS4', qno=n, part=lab, section='A',
                marks=mk, word_limit=wl, subject='Ethics', topic='', stem=intro + stem, options='', answer='', source=src,
                quality_flag='untagged;transcribed' + ('' if mk else ';marks_missing')))
        i += 1
    # ---- Section B
    starts = [k for k in range(secB, len(L)) if re.match(r'^\d+\.\s*Case Study', L[k])]
    for a, s in enumerate(starts):
        end = starts[a + 1] if a + 1 < len(starts) else len(L)
        q = int(re.match(r'^(\d+)\.', L[s]).group(1))
        ei = next(k for k in range(s, end) if re.match(r'^\s*\*\s*English:', L[k]))
        blk = [x.strip() for x in L[ei + 1:end] if x.strip()]
        case, parts, tail = [], [], None
        for x in blk:
            tm = TAIL.search(x)
            if tm: tail = tm; x = norm(x[:tm.start()])
            if re.match(r'^\([a-d]\)\s+\S', x): parts.append(x)
            elif x == '(a)': continue
            elif re.match(r'^What is your reaction', x): parts.append('(a) ' + x)
            else: case.append(x)
        mk = tail.group(2) if tail else ''; wl = tail.group(1) if tail else ''
        rows.append(dict(id=f'M{year}-GS4-{q:02d}', exam='Mains', year=year, paper='GS4', qno=q, part='', section='B',
            marks=mk, word_limit=wl, subject='Ethics', topic='', stem=norm(' '.join(case)) + ' || ' + ' '.join(parts),
            options='', answer='', source=src, quality_flag='untagged;case_study;transcribed' + ('' if mk else ';marks_missing')))
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), str(year), f'{year} Mains GS4.csv')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w', encoding='utf-8', newline='') as f:
        w = csv.DictWriter(f, FIELDS); w.writeheader(); w.writerows(rows)
    print(out, len(rows))

if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], sys.argv[3])
