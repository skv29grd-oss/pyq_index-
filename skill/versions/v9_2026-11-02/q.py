import re, json, sys
recs = json.load(open('mains_recs.json'))
plines = list(dict.fromkeys(l.strip() for l in open('prelims_lines.txt', encoding='utf-8') if l.strip()))
def yr(l):
    m = re.match(r'^(20\d\d) Q\d+', l) or re.search(r'\((20\d\d)\)', l) or re.search(r'\b(20[12]\d)\b', l)
    return m.group(1) if m else None
for arg in sys.argv[1:]:
    label, pat = arg.split('::', 1)
    rx = re.compile(pat, 0 if label.endswith('!') else re.I)
    print(f'\n### {label}')
    n=0
    for r in recs:
        if rx.search(r['text']) and n<10:
            n+=1;
            print(f"  M {r['year']} {r['paper']} {r.get('q','')} [{r['marks']}]: {r['text'][:420]}")
    seen = set()
    for l in plines:
        y = yr(l)
        if y and rx.search(l) and l[:80] not in seen and len(seen)<8:
            seen.add(l[:80]); print(f'  P {y}: {l[:420]}')
