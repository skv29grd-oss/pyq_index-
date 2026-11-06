"""PYQ regex search (v19). Run from the folder where load_pyq.py wrote pyq_bank.json.
Usage: python3 q.py 'label::regex' ['label2!::Regex' ...]   (label ending '!' = case-sensitive)
Each hit prints its PYQ ID first: copy the IDs of genuine matches into the row's pyq_ids."""
import re, json, sys
bank = json.load(open('pyq_bank.json', encoding='utf-8'))
mains = [(k, v) for k, v in bank.items() if v['exam'] == 'Mains']
prel = [(k, v) for k, v in bank.items() if v['exam'] == 'Prelims']
for arg in sys.argv[1:]:
    label, pat = arg.split('::', 1)
    rx = re.compile(pat, 0 if label.endswith('!') else re.I)
    print(f'\n### {label}')
    n = 0
    for k, v in mains:
        if rx.search(v['text']) and n < 10:
            n += 1
            print(f"  {k}  [{v['paper']} {v['year']} {v['q']}, {v['marks']} m]: {v['text'][:420]}")
    seen = set()
    for k, v in prel:
        if rx.search(v['text']) and v['text'][:80] not in seen and len(seen) < 8:
            seen.add(v['text'][:80])
            print(f"  {k}  [P {v['year']} {v['q']}]: {v['text'][:420]}")
