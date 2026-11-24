"""Recall bank (v24): verified static facts per syllabus Subtopic, reused across days (data/recall_bank.json).

  python3 pyq_index-/skill/recall_bank.py find today_YYYY-MM-DD.json   bank items already held for each row's Subtopic
  python3 pyq_index-/skill/recall_bank.py add batch.json               add verified items:
        {"Subtopic text": {"prelims": [{"text": ..., "url": ...}], "mains": [{"tag": "[Provision]", "text": ..., "url": ...}]}}
Every item needs an https URL on an authentic source (same allowlist as verify.py); `checked` is stamped with today's date.
Refresh an item (re-search) when the news changes a figure; never fill an item from memory.
"""
import json, os, sys
from datetime import date

PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'recall_bank.json')


def load():
    return json.load(open(PATH, encoding='utf-8')) if os.path.exists(PATH) else {}


def main():
    cmd, arg = sys.argv[1], sys.argv[2]
    bank = load()
    if cmd == 'find':
        for o in json.load(open(arg, encoding='utf-8')):
            sub = o.get('tag', '').split('›')[-1].strip()
            b = bank.get(sub)
            print(f"### {sub}: " + ('MISSING - search authentic sources, then add' if not b else
                  f"{len(b['prelims'])} prelims, {len(b['mains'])} mains items"))
            for k in ('prelims', 'mains'):
                for i in (b or {}).get(k, []):
                    print(f"   [{k}] {i.get('tag', '')} {i['text']} {i['url']} (checked {i['checked']})")
    elif cmd == 'add':
        today = date.today().isoformat()
        for sub, d in json.load(open(arg, encoding='utf-8')).items():
            e = bank.setdefault(sub, {'prelims': [], 'mains': []})
            for k in ('prelims', 'mains'):
                for i in d.get(k, []):
                    assert i['url'].startswith('https://') and i['text'].strip(), i
                    e[k] = [x for x in e[k] if x['text'] != i['text']] + [dict(i, checked=today)]
        json.dump(bank, open(PATH, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
        print('bank subtopics:', len(bank))


main()
