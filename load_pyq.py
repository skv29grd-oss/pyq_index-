import re, json, glob
DEV = re.compile(r'[ऀ-ॿ]')
def mains_2026(fn, paper):
    keep = []
    for line in open(fn, encoding='utf-8').read().splitlines():
        s = line.strip()
        if not s or DEV.search(s) or s.startswith('KVMS') or 'Booklet' in s or 'word limit' in s.lower():
            continue
        keep.append(s)
    flat = re.sub(r'\s+', ' ', ' '.join(keep))
    flat = flat[flat.find('in 250 words.') + 13:] if 'in 250 words.' in flat else flat
    if paper == 'GS4' and 'Lata, a mother' in flat:   # skip Section A theory text; it is parsed by gs4_theory_2026
        flat = flat[flat.find('Lata, a mother'):]
    out = []
    for m in re.finditer(r'(.+?)\(Answer in \d+ words\)\s*(\d{1,2})', flat):
        q = re.sub(r'^\s*(Q\.?\s*)?\d{1,2}\.?\s*', '', m.group(1)).strip(' .')
        q = re.sub(r'^KVMS-\S+\s*', '', q)
        q = re.sub(r'^\(?[a-c]\)\s*', '', q)
        if len(q) > 25:
            out.append({'paper': paper, 'year': '2026', 'text': q, 'marks': m.group(2)})
    return out
def gs4_theory_2026(fn):
    """GS4 2026 theory parts: English line ending in marks, Hindi lines dropped (scan quality)."""
    out = []
    for line in open(fn, encoding='utf-8').read().splitlines():
        s = line.strip()
        if not s or DEV.search(s) or s.startswith('KVMS'):
            continue
        m = re.match(r'^(.{25,}?)\s{3,}(\d{1,2})$', s)
        if m and 'Answer in' not in m.group(1):
            out.append({'paper': 'GS4', 'year': '2026', 'text': m.group(1).strip(), 'marks': m.group(2)})
    return out
def prelims_2026(fn):
    t = open(fn, encoding='utf-8').read()
    out = []
    for m in re.finditer(r'(?ms)^(\d{1,3})\.\s+(.*?)(?=^\(a\))', t):
        stem = re.sub(r'\s+', ' ', m.group(2)).strip()
        if stem and not DEV.search(stem):
            out.append(f'2026 Q{m.group(1)}: {stem}')
    return out
if __name__ == '__main__':
    import sys
    os_dir = sys.argv[1] if len(sys.argv) > 1 else '.'
    recs = []
    for i, fn in enumerate(['GS1_Index.txt', 'GS2_Index.txt', 'GS3_Index.txt', 'GS4_Index.txt'], 1):
        flat = re.sub(r'\s+', ' ', open(f'{os_dir}/{fn}', errors='ignore').read())
        for m in re.finditer(r'\b\d{1,3}\s+(20(?:1[3-9]|2[0-5]))\s+(.{25,700}?)\s+(\d{1,2}(?:\.5)?)\s+(?=\d{1,3}\s+20(?:1[3-9]|2[0-5])\s|$)', flat):
            recs.append({'paper': f'GS{i}', 'year': m.group(1), 'text': m.group(2), 'marks': m.group(3)})
        recs += mains_2026(f'{os_dir}/UPSC CSE 2026 General Studies-{"I"*i if i<4 else "IV"}.txt', f'GS{i}')
        if i == 4:
            recs += gs4_theory_2026(f'{os_dir}/UPSC CSE 2026 General Studies-IV.txt')
    # completeness gate: each 2026 Mains paper carries exactly 250 marks; a partial parse fails loudly
    for g in ('GS1', 'GS2', 'GS3', 'GS4'):
        tot = sum(float(r['marks']) for r in recs if r['paper'] == g and r['year'] == '2026')
        assert tot == 250, f'{g} 2026 parsed marks = {tot}, expected 250 - parser missed questions'
    json.dump(recs, open('mains_recs.json', 'w'), ensure_ascii=False)
    P = [l for fn in sorted(glob.glob(f'{os_dir}/Prelims_Index*.txt')) for l in open(fn, errors='ignore').read().splitlines()]
    P += prelims_2026(f'{os_dir}/UPSC CSE 2026 prelims paper.txt')
    open('prelims_lines.txt', 'w', encoding='utf-8').write('\n'.join(P))
    from collections import Counter
    print('mains records:', dict(Counter((r['paper'], r['year'] == '2026') for r in recs)))
    print('prelims lines:', len(P), '| 2026 stems:', sum(1 for l in P if l.startswith('2026 Q')))
