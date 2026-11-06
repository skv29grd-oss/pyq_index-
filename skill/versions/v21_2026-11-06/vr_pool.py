"""V&R syllabus content pool (v21): data/vr_pool.json.

One-time build: every syllabus line in skill/syllabus.md gets up to TARGET V&R syllabus-notes pages,
each stored as 4-12 facts of FIXED THEORY in Claude's own words (never V&R's text; no news, no current
figures), with title, URL and subtopic keywords. Daily rows pick 2-4 theory facts by ID (vr_facts).

Usage (from /home/claude, clone at pyq_index-/):
  python3 pyq_index-/skill/vr_pool.py status            coverage per syllabus line; lines still below TARGET
  python3 pyq_index-/skill/vr_pool.py add batch.json    add pages for ONE syllabus line:
        {"line": "GS2 | Polity | <Topic>", "queries": ["search used", ...],
         "pages": [{"url": ..., "title": ..., "subtopics": [...], "facts": [...]}, ...]}
  python3 pyq_index-/skill/vr_pool.py find today_YYYY-MM-DD.json
        for each newspaper row: best pool pages for its tag and headline, facts numbered by ID
        ('~' = fact already in the row's recall: do not pick it)
  python3 pyq_index-/skill/vr_pool.py show V0003        one page in full
  python3 pyq_index-/skill/vr_pool.py remove V0003 ...  retire pages (IDs are never reused; the URL is not re-added)
"""
import json, os, re, sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
POOL = os.path.join(HERE, '..', 'data', 'vr_pool.json')
SYLLABUS = os.path.join(HERE, 'syllabus.md')
TARGET = 8
NEWS = ('The Hindu', 'Indian Express')
URL_RX = re.compile(r'^https://(web\.)?vajiramandravi\.com/\S+$')
NEWS_URL = re.compile(r'/20\d\d/\d\d/\d\d/|daily-current-affairs|upsc-(mains|prelims)-current-affairs')
NEWS_WORDS = re.compile(r'\b(recent(ly)?|latest|currently|as of|this year|ongoing|last (week|month|year)|news)\b', re.I)
STOP = set('a an the of in on and or for to by with from as at is are was be its it this that their his her into under over'
           ' india indian national new act law rules role issues issue related between vs'.split())


def syllabus_lines():
    out = []
    for l in open(SYLLABUS, encoding='utf-8'):
        if l.startswith('- ') and l.count('|') == 2:
            out.append(' | '.join(p.strip() for p in l[2:].split('|')))
    return out


def load():
    if os.path.exists(POOL):
        return json.load(open(POOL, encoding='utf-8'))
    return {'pages': {}, 'searched': {}, 'retired': {}}


def save(p):
    with open(POOL, 'w', encoding='utf-8') as f:
        json.dump(p, f, ensure_ascii=False, indent=1)
        f.write('\n')


def norm_url(u):
    return u.split('#')[0].split('?')[0].rstrip('/') + '/'


def words(s):
    return {w for w in re.findall(r'[a-z0-9]+', s.lower()) if w not in STOP and len(w) > 2}


def fact_ids(pool):
    return {f'{k}.{i}': f for k, v in pool['pages'].items() for i, f in enumerate(v['facts'], 1)}


def tag_line(tag):
    parts = [p.strip() for p in tag.split('›')]
    if len(parts) != 4:
        sys.exit(f'tag must be Paper › Subject › Topic › Subtopic: {tag}')
    return ' | '.join(parts[:3]), parts[3]


def cmd_status(pool):
    lines = syllabus_lines()
    cnt = {l: 0 for l in lines}
    for v in pool['pages'].values():
        cnt[v['line']] = cnt.get(v['line'], 0) + 1
    nf = sum(len(v['facts']) for v in pool['pages'].values())
    done = sum(1 for l in lines if cnt[l] >= TARGET)
    print(f"pool: {len(pool['pages'])} pages, {nf} facts | lines at target ({TARGET}): {done}/{len(lines)}")
    for l in lines:
        q = len(pool['searched'].get(l, []))
        print(f"  {cnt[l]:>2} pages  {q:>2} searches  {l}")


def cmd_add(pool, path):
    b = json.load(open(path, encoding='utf-8'))
    line = b.get('line', '')
    if line not in syllabus_lines():
        sys.exit(f'line not in syllabus.md: {line}')
    retired = pool.setdefault('retired', {})
    seen = {norm_url(v['url']) for v in pool['pages'].values()} | {norm_url(u) for u in retired.values()}
    n = max([int(k[1:]) for k in list(pool['pages']) + list(retired)] or [0])
    added = []
    for pg in b.get('pages', []):
        u = norm_url(pg.get('url', ''))
        assert URL_RX.match(u), f'not a V&R URL: {u}'
        assert not NEWS_URL.search(u), f'daily news page, not syllabus theory: {u}'
        if u in seen:
            print('skip (already in pool or retired):', u); continue
        t = pg.get('title', '').strip(); subs = [s.strip() for s in pg.get('subtopics', []) if s.strip()]
        facts = [f.strip() for f in pg.get('facts', []) if f.strip()]
        assert t and subs, f'title and subtopics required: {u}'
        assert 4 <= len(facts) <= 12, f'4-12 facts per page: {u} has {len(facts)}'
        long_ = [f for f in facts if len(f.split()) > 30]
        assert not long_, f'facts are short notes (<=30 words): {long_[0][:60]}'
        assert len({f.lower() for f in facts}) == len(facts), f'repeated fact: {u}'
        newsy = [f for f in facts if NEWS_WORDS.search(f)]
        assert not newsy, f'news wording in a theory fact (fixed theory only): {newsy[0][:70]}'
        for f in facts:
            if re.search(r'\b20(2[5-9])\b', f):
                print(f'  check: recent year in a theory fact (keep only if it is settled law or a fixed fact): {f[:80]}')
        n += 1
        k = f'V{n:04d}'
        assert k not in pool['pages']
        pool['pages'][k] = {'line': line, 'url': u, 'title': t, 'subtopics': subs, 'facts': facts,
                            'added': date.today().isoformat()}
        seen.add(u); added.append(k)
    qs = pool['searched'].setdefault(line, [])
    qs += [q for q in b.get('queries', []) if q not in qs]
    save(pool)
    print(f'added {len(added)} pages {added} to: {line}')


def cmd_find(pool, path):
    rows = json.load(open(path, encoding='utf-8'))
    done = set()
    for o in rows:
        if not o.get('source', '').startswith(NEWS):
            continue
        line, sub = tag_line(o.get('tag', ''))
        if (line, sub) in done:
            continue
        done.add((line, sub))
        want = words(sub) | words(o.get('topic', ''))
        recall = [r.lower() for r in o.get('prelims', []) + o.get('mains', [])]
        scored = []
        for k, v in pool['pages'].items():
            same_line, sub_hit = v['line'] == line, len(words(sub) & words(' '.join(v['subtopics']) + ' ' + v['title']))
            s = 3 * same_line + 2 * sub_hit + len(want & words(v['title'] + ' ' + ' '.join(v['subtopics'])))
            if same_line or sub_hit:                 # relevance rule shared with verify.py
                scored.append((s, k))
        scored.sort(key=lambda x: (-x[0], x[1]))
        print(f'\n### {sub}  [{line}]  - {o.get("topic", "")[:70]}')
        if not scored:
            print('  MISSING: no pool page. Search V&R once for this subtopic, add it (vr_pool.py add), then pick.')
        for s, k in scored[:8]:
            v = pool['pages'][k]
            print(f"  {k} (score {s}) {v['title']}  <{v['line'].split(' | ')[1]}>")
            for i, f in enumerate(v['facts'], 1):
                fw = words(f)
                dup = any(len(fw & words(r)) >= max(3, 0.6 * len(fw)) for r in recall)
                print(f"    {'~' if dup else ' '}{k}.{i}  {f}")


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in ('status', 'add', 'find', 'show', 'remove'):
        sys.exit(__doc__)
    pool = load()
    c = sys.argv[1]
    if c == 'status':
        cmd_status(pool)
    elif c == 'add':
        cmd_add(pool, sys.argv[2])
    elif c == 'find':
        cmd_find(pool, sys.argv[2])
    elif c == 'remove':
        r = pool.setdefault('retired', {})
        for k in sys.argv[2:]:
            r[k] = pool['pages'].pop(k)['url']; print('retired', k, r[k])
        save(pool)
    else:
        print(json.dumps(pool['pages'][sys.argv[2]], ensure_ascii=False, indent=1))


if __name__ == '__main__':
    main()
