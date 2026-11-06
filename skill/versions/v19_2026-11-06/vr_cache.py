"""Permanent V&R syllabus-base cache (v19): data/vr_topics.json, keyed by the Syllabus Tag's Subtopic.

Usage (from /home/claude, clone at pyq_index-/):
  python3 pyq_index-/skill/vr_cache.py fill today_YYYY-MM-DD.json
      Newspaper rows whose Subtopic is cached get vr_topic copied from the cache (JSON rewritten).
      Prints the Subtopics still MISSING, with close cached Subtopics so an existing tag can be reused.
  python3 pyq_index-/skill/vr_cache.py add today_YYYY-MM-DD.json [--replace "Subtopic" ...]
      Saves vr_topic of every newspaper row whose Subtopic is not yet cached. A cached Subtopic is only
      overwritten when named after --replace (the user asked, or the day's news superseded a cached fact).
Entry: {"page": V&R page title or "", "facts": [...], "tag": first full tag, "first_date": date}; page "" + no
facts = no V&R page on that Subtopic (cached too, so it is not searched again).
"""
import difflib, json, os, sys

CACHE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'data', 'vr_topics.json')
NEWS = ('The Hindu', 'Indian Express')


def sub_of(o):
    parts = [p.strip() for p in o.get('tag', '').split('›')]
    if len(parts) != 4 or not all(parts):
        sys.exit(f"tag must be Paper › Subject › Topic › Subtopic: {o.get('topic', '')[:50]}")
    return parts[3]


def load_cache():
    return json.load(open(CACHE, encoding='utf-8')) if os.path.exists(CACHE) else {}


def save_cache(c):
    with open(CACHE, 'w', encoding='utf-8') as f:
        json.dump(dict(sorted(c.items())), f, ensure_ascii=False, indent=1)
        f.write('\n')


def block(e):
    return {'page': e['page'], 'facts': list(e['facts'])}


def main():
    if len(sys.argv) < 3 or sys.argv[1] not in ('fill', 'add'):
        sys.exit(__doc__)
    cmd, path = sys.argv[1], sys.argv[2]
    replace = set(sys.argv[sys.argv.index('--replace') + 1:]) if '--replace' in sys.argv else set()
    rows = json.load(open(path, encoding='utf-8'))
    cache = load_cache()
    news = [o for o in rows if o.get('source', '').startswith(NEWS)]
    if cmd == 'fill':
        missing, n = [], 0
        for o in news:
            s = sub_of(o)
            if s in cache:
                o['vr_topic'] = block(cache[s]); n += 1
            elif s not in missing:
                missing.append(s)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(rows, f, ensure_ascii=False, indent=1)
        print(f'filled from cache: {n} of {len(news)} newspaper rows')
        for s in missing:
            close = difflib.get_close_matches(s, list(cache), n=3, cutoff=0.5)
            print(f'MISSING: {s}' + (f'   (close cached: {close})' if close else ''))
        return
    day = {}
    for o in news:                                   # add
        s = sub_of(o)
        vt = o.get('vr_topic')
        if not (isinstance(vt, dict) and set(vt) == {'page', 'facts'} and isinstance(vt['facts'], list)):
            sys.exit(f'vr_topic missing or malformed for Subtopic: {s}')
        if s in day and day[s] != block(vt):
            sys.exit(f'same Subtopic, different vr_topic within the day: {s}')
        day[s] = block(vt)
    added, replaced = [], []
    for s, vt in day.items():
        o = next(x for x in news if sub_of(x) == s)
        if s not in cache:
            cache[s] = dict(vt, tag=o['tag'], first_date=o['date']); added.append(s)
        elif block(cache[s]) != vt:
            if s not in replace:
                sys.exit(f'cached Subtopic differs: {s}. Run fill (reuse the cache), or pass --replace "{s}" if the user asked or a fact is superseded.')
            cache[s].update(vt, updated=o['date']); replaced.append(s)
    unknown = replace - set(day)
    if unknown:
        sys.exit(f'--replace names a Subtopic not in this JSON: {sorted(unknown)}')
    save_cache(cache)
    print(f'cache: {len(cache)} Subtopics | added {len(added)}: {added} | replaced {len(replaced)}: {replaced}')


if __name__ == '__main__':
    main()
