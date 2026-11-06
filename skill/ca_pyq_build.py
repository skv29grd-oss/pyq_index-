# -*- coding: utf-8 -*-
"""CA-PYQ Match Log builder (v19: 13 columns; Master Log shows one sub-row per matched PYQ; rows store PYQ IDs).

Usage:
  python3 ca_pyq_build.py --logs day1.csv day2.csv ... --today TODAY.json \
      --out-xlsx "CA-PYQ Match Log.xlsx" --out-day-csv today_upload.csv

--logs     = the per-day logs exported from Drive as CSV (11-column schema below; header row required;
             day-sheets whose ninth header still reads 'Representative PYQ (excerpt)' are accepted).
TODAY.json = list of objects: date, topic, source, gs_area, tag, pyq_ids [list of PYQ IDs], match,
             note, prelims [list of str], mains [list of str, each starting with a [Tag]], vr_topic.
             v19 (rows from 4 Nov 2026): pyq_ids replaces years, papers and pyq_excerpt; the builder
             derives PYQ Years and Paper(s) from the IDs, stores the IDs (one per line) in the CSV and
             shows the full question text from --pyq-bank (pyq_bank.json written by load_pyq.py).
             Older JSON (years, papers, pyq_excerpt with full text) is still accepted.
             note holds the three tagged lines [Prelims 2027] / [Mains 2027] / [Link].
Writes the formatted workbook (all days, locked design: Calibri 12 everywhere) and a Drive-safe CSV
of today's rows only. This script is the single source of truth for the look — never hand-format.
"""
import argparse, csv, json, math, re
from collections import Counter, OrderedDict
from datetime import datetime
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.cell.rich_text import CellRichText, TextBlock
from openpyxl.cell.text import InlineFont

# Internal row order (index-stable since v6) + Syllabus Tag appended at index 12.
INTERNAL = ['Date', 'GS Area', 'Match', 'CA Topic / Headline', 'Prelims Recall (CSE 2027)',
            'Mains Recall (CSE 2027)', 'PYQ Years (all occurrences)', 'Paper(s)',
            'PYQ Excerpts (all, Prelims + Mains)', 'Relevance & Revision Note', 'Source',
            'V&R Recall (Vajiram & Ravi)', 'Syllabus Tag']
# Display / CSV order (v8): Syllabus Tag sits after GS Area.
HEAD = ['Date', 'GS Area', 'Syllabus Tag', 'Match', 'CA Topic / Headline', 'Prelims Recall (CSE 2027)',
        'Mains Recall (CSE 2027)', 'PYQ Years (all occurrences)', 'Paper(s)',
        'PYQ Excerpts (all, Prelims + Mains)', 'Relevance & Revision Note', 'Source',
        'V&R Recall (Vajiram & Ravi)']
PERM = [INTERNAL.index(h) for h in HEAD]
NEWSPAPER = ('The Hindu', 'Indian Express')
FONT, SZ = 'Calibri', 12
NAVY, SLATE = '1F3864', '44546A'
MATCH_FILL = {'Direct': 'C6EFCE', 'Thematic': 'FFF2CC', 'Emerging': 'E7E6E6'}
MATCH_INK = {'Direct': '145A32', 'Thematic': '7D6608', 'Emerging': '3B3838'}
BAND = ['FFFFFF', 'F2F6FB']
THIN = Side(style='thin', color='BFBFBF')
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
TOP = Alignment(vertical='top', wrap_text=True)
TOPC = Alignment(vertical='top', horizontal='center', wrap_text=True)

ID_RX = re.compile(r'^[PME]20\d\d-[A-Za-z0-9&-]+$')     # P2021-001, M2021-GS3-07, E2026-A1, P2012-MoH-Q13
NO_MATCH = 'No PYQ match in corpus'
PAPER_ORDER = ['Prelims', 'GS1', 'GS2', 'GS3', 'GS4', 'Essay']
BANK = {}                                            # filled from --pyq-bank

def id_lines(cell):
    """The PYQ IDs of a stored excerpt cell, or None if the cell holds text (rows before v19)."""
    ls = [l.strip() for l in str(cell or '').split('\n') if l.strip()]
    return ls if ls and all(ID_RX.match(l) for l in ls) else None

def bank_entry(k):
    if k not in BANK:
        raise SystemExit(f'PYQ ID not in the PYQ bank: {k} (run load_pyq.py; pass --pyq-bank)')
    return BANK[k]

def pyq_line(k):
    v = bank_entry(k)
    if v['exam'] == 'Prelims':
        return f"P {v['year']}: {v['text']}"
    return f"{v['paper']} {v['year']}" + (f" ({v['marks']})" if v['marks'] else '') + f": {v['text']}"

def expand(cell):
    """Stored cell -> excerpt text: IDs become 'P <year>: ...' / 'GS<n> <year> (<marks>): ...' lines."""
    ids = id_lines(cell)
    return '\n'.join(pyq_line(k) for k in ids) if ids else cell

def sort_ids(ids):
    return sorted(ids, key=lambda k: (bank_entry(k)['year'], PAPER_ORDER.index(bank_entry(k)['paper']), k))

def derive(ids):
    """PYQ Years and Paper(s) cells from the IDs ('—' when there is no match)."""
    yrs = sorted({bank_entry(k)['year'] for k in ids})
    pap = [p for p in PAPER_ORDER if any(bank_entry(k)['paper'] == p for k in ids)]
    return (', '.join(yrs) or '\u2014'), (' + '.join(pap) or '\u2014')

def F(**kw):
    return Font(name=FONT, size=SZ, **kw)

def fill(hex_):
    return PatternFill('solid', fgColor=hex_)

def bullets(xs):
    return '\n'.join('• ' + x.strip() for x in xs if x and x.strip())

def est_height(text, width):
    """Row height (pt) for wrapped Calibri-12 text in a column of given width."""
    cpl = max(8, int(width * 1.15))
    n = sum(max(1, math.ceil(len(seg) / cpl)) for seg in str(text or '').split('\n'))
    return min(409, n * 15.6 + 6)

def mains_rich(text):
    """Bold the [Tag] at the start of each Mains bullet."""
    rt = CellRichText()
    lines = str(text or '').split('\n')
    for i, line in enumerate(lines):
        m = re.match(r'^(•\s*)?(\[[^\]]+\])(.*)$', line)
        if m:
            rt.append(TextBlock(InlineFont(rFont=FONT, sz=SZ), m.group(1) or ''))
            rt.append(TextBlock(InlineFont(rFont=FONT, sz=SZ, b=True, color=NAVY), m.group(2)))
            rt.append(TextBlock(InlineFont(rFont=FONT, sz=SZ), m.group(3) + ('\n' if i < len(lines) - 1 else '')))
        else:
            rt.append(TextBlock(InlineFont(rFont=FONT, sz=SZ), line + ('\n' if i < len(lines) - 1 else '')))
    return rt

def load(log_paths, today_path):
    rows = []
    for log_path in log_paths or []:
        with open(log_path, newline='', encoding='utf-8') as f:
            r = list(csv.reader(f))
        hdr = [h.replace('Representative PYQ (excerpt)', 'PYQ Excerpts (all, Prelims + Mains)') for h in r[0]]
        assert set(hdr) <= set(INTERNAL) and hdr[:2] == ['Date', 'GS Area'], f'Unexpected header in {log_path}: {r[0]}'
        pos = {h: i for i, h in enumerate(hdr)}
        for x in r[1:]:
            if x and x[0].strip():
                rows.append([x[pos[h]] if h in pos and pos[h] < len(x) else '' for h in INTERNAL])
    if today_path:
        for o in json.load(open(today_path, encoding='utf-8')):
            if 'pyq_ids' in o:                       # v19
                ids = sort_ids(o['pyq_ids'])
                yrs, pap = derive(ids)
                exc = '\n'.join(ids) or NO_MATCH
            else:
                yrs, pap, exc = o['years'], o['papers'], o['pyq_excerpt']
            rows.append([o['date'], o['gs_area'], o['match'], o['topic'], bullets(o['prelims']),
                         bullets(o['mains']), yrs, pap, exc, o['note'], o['source'],
                         vr_text(o), o.get('tag', '')])
    seen, out = set(), []
    for x in rows:                                  # de-duplicate on date + topic start
        k = (x[0], x[3][:80])
        if k in seen:
            continue
        seen.add(k); out.append(x)
    order = {id(x): i for i, x in enumerate(out)}
    out.sort(key=lambda x: (x[0], -order[id(x)]), reverse=True)   # newest date first, original order within a date
    return out

def is_newspaper(o):
    return any(o.get('source', '').startswith(n) for n in NEWSPAPER)

def vr_text(o):
    """Column 13. v9 rows (with 'vr_topic'): syllabus base only, newspaper rows only.
    Rows written before v9 (no 'vr_topic') keep the old [CA] text from 'vr'."""
    dmy = o['date'][8:10] + '-' + o['date'][5:7] + '-' + o['date'][:4]
    t = o.get('vr_topic')
    if t is None:                      # legacy rows (29-30 Oct 2026)
        v = o.get('vr')
        if isinstance(v, list):
            return bullets(v) if v else f'Not covered by V&R ({dmy})'
        return v or ''
    if not is_newspaper(o):
        return ''
    sub = o.get('tag', '').split(' \u203a ')[-1]
    if t.get('facts'):
        return f"[Syllabus base \u2013 {sub}] (V&R: {t.get('page', '')})\n" + bullets(t['facts'])
    return f'[Syllabus base \u2013 {sub}] No V&R topic page found'

PYQ_LINE = re.compile(r'^(?:(P)\s+(20\d\d)|(GS[1-4]|Essay)\s+(20\d\d)(?:\s*\(([^)]*)\))?)\s*:\s*(.*)$', re.S)

def split_pyqs(exc):
    """One entry per matched PYQ: (year, paper label, full question text). Lines that are not
    'P <year>:' / 'GS<n> <year> (<marks>):' (e.g. '+N more' in old rows) are kept as text-only entries."""
    out = []
    for line in [l.strip() for l in str(exc or '').split('\n') if l.strip()]:
        m = PYQ_LINE.match(line)
        if m and m.group(1):
            out.append((m.group(2), 'Prelims', m.group(6).strip()))
        elif m:
            out.append((m.group(4), m.group(3) + (f' ({m.group(5)} m)' if m.group(5) else ''), m.group(6).strip()))
        else:
            out.append(('', '', line))
    return out or [('', '', str(exc or ''))]

def nice_date(d):
    try:
        return datetime.strptime(d, '%Y-%m-%d').strftime('%d %b %Y')
    except ValueError:
        return d

def build(rows, out_xlsx):
    wb = Workbook()
    by_date = OrderedDict()
    for x in rows:
        by_date.setdefault(x[0], []).append(x)

    # ---------- Sheet 1: Revision Cards (phone-friendly, 2 columns) ----------
    ws = wb.active; ws.title = 'Revision Cards'
    ws.column_dimensions['A'].width = 20
    ws.column_dimensions['B'].width = 100
    ws.sheet_view.showGridLines = False
    r = 1
    for d, items in by_date.items():
        mix = Counter(x[2] for x in items)
        ws.merge_cells(start_row=r, start_column=1, end_row=r, end_column=2)
        c = ws.cell(r, 1, f"{nice_date(d)}   ·   {len(items)} items   ·   Direct {mix.get('Direct',0)}  |  Thematic {mix.get('Thematic',0)}  |  Emerging {mix.get('Emerging',0)}")
        c.font = F(bold=True, color='FFFFFF'); c.fill = fill(NAVY)
        c.alignment = Alignment(vertical='center', horizontal='left', indent=1)
        ws.row_dimensions[r].height = 26
        r += 1
        for n, x in enumerate(items, 1):
            date, area, match, topic, pre, mai, yrs, pap, exc, note, src, vr, tag = x
            card = [
                (f'#{n}  ·  {match}', topic, 'head'),
                ('Area · Source', f'{area}   ·   {src}', 'meta'),
            ] + ([('Syllabus', tag, 'tag')] if tag else []) + [
                ('PYQ years', f'{yrs}   —   {pap}', 'years'),
                ('Prelims recall', pre, 'pre'),
                ('Mains recall', mai, 'mains'),
            ] + [(('Prelims ' + yy) if pp == 'Prelims' else (f"{pp.split(' ')[0]} {yy}" + (' ' + pp.split(' ', 1)[1] if ' ' in pp else '')) if yy else 'PYQ', q, 'pyq') for yy, pp, q in split_pyqs(expand(exc))] + [
                ('Expected 2027 Qs', note, 'note'),
            ] + ([('V&R recall', vr, 'vr')] if vr else [])
            for label, val, kind in card:
                a, b = ws.cell(r, 1, label), ws.cell(r, 2)
                a.font = F(bold=True, color=SLATE); a.alignment = TOP
                a.border = Border(bottom=THIN); b.border = Border(bottom=THIN)
                b.alignment = TOP
                if kind == 'head':
                    a.fill = fill(MATCH_FILL.get(match, 'E7E6E6'))
                    a.font = F(bold=True, color=MATCH_INK.get(match, '3B3838'))
                    b.value = val; b.font = F(bold=True); b.fill = fill('EEF3FA')
                elif kind == 'mains':
                    b.value = mains_rich(val); b.font = F()
                elif kind == 'tag':
                    b.value = val; b.font = F(bold=True, color=SLATE)
                elif kind == 'years':
                    b.value = val; b.font = F(bold=True, color=NAVY)
                elif kind == 'pyq':
                    b.value = val; b.font = F(italic=True, color='404040')
                elif kind == 'vr':
                    b.value = val; b.font = F(); b.fill = fill('FFF7E6')
                elif kind == 'pre':
                    b.value = val; b.font = F(); b.fill = fill('F4F9F1')
                else:
                    b.value = val; b.font = F()
                ws.row_dimensions[r].height = max(est_height(val, 100), est_height(label, 20))
                r += 1
            ws.row_dimensions[r].height = 10     # spacer between cards
            r += 1
        r += 1
    ws.freeze_panes = 'A1'
    ws.sheet_properties.tabColor = NAVY
    ws.page_setup.orientation = 'portrait'
    ws.page_setup.fitToWidth = 1; ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True

    # ---------- Sheet 2: Master Log (filterable table) ----------
    wl = wb.create_sheet('Master Log')
    widths = {'A': 12, 'B': 18, 'C': 34, 'D': 11, 'E': 55, 'F': 55, 'G': 58, 'H': 22, 'I': 16, 'J': 62, 'K': 55, 'L': 18, 'M': 60}
    MAINS_C, MATCH_C, YRS_C, EXC_C = HEAD.index('Mains Recall (CSE 2027)') + 1, HEAD.index('Match') + 1, HEAD.index('PYQ Years (all occurrences)') + 1, HEAD.index('PYQ Excerpts (all, Prelims + Mains)') + 1
    NC = len(HEAD)
    for col, w in widths.items():
        wl.column_dimensions[col].width = w
    wl.append(HEAD)
    for c in wl[1]:
        c.font = F(bold=True, color='FFFFFF'); c.fill = fill(NAVY); c.border = BOX
        c.alignment = Alignment(vertical='center', horizontal='center', wrap_text=True)
    wl.row_dimensions[1].height = 36
    band = {d: BAND[i % 2] for i, d in enumerate(by_date)}
    KEYS = {1, 2, 3, MATCH_C}                       # repeated on every sub-row so filters keep whole items
    SUB = {YRS_C, YRS_C + 1, EXC_C}                  # one value per PYQ sub-row
    prev = None
    for x in rows:
        y = [x[k] for k in PERM]
        pyqs = split_pyqs(expand(x[8]))
        first = wl.max_row + 1
        for s_i, (yy, pp, q) in enumerate(pyqs):
            vals = []
            for j in range(1, NC + 1):
                if j in SUB:
                    vals.append({YRS_C: yy or y[j - 1] if len(pyqs) == 1 else yy,
                                 YRS_C + 1: pp or (y[j - 1] if len(pyqs) == 1 else ''), EXC_C: q}[j])
                elif j in KEYS or s_i == 0:
                    vals.append(None if j == MAINS_C else y[j - 1])
                else:
                    vals.append(None)
            wl.append(vals)
            i = wl.max_row
            if s_i == 0:
                wl.cell(i, MAINS_C).value = mains_rich(x[5])
            for j in range(1, NC + 1):
                c = wl.cell(i, j)
                c.font = F(); c.alignment = TOP; c.border = BOX; c.fill = fill(band[x[0]])
            for j in (1, 2, MATCH_C, YRS_C, YRS_C + 1):
                wl.cell(i, j).alignment = TOPC
            wl.cell(i, YRS_C).font = F(bold=True, color=NAVY)
            wl.cell(i, YRS_C + 1).font = F(bold=True, color=SLATE)
            wl.cell(i, EXC_C).font = F(italic=True, color='404040')
            wl.cell(i, 3).font = F(bold=True, color=SLATE) if s_i == 0 else F(color='A6A6A6')
            m = wl.cell(i, MATCH_C)
            if x[2] in MATCH_FILL:
                m.fill = fill(MATCH_FILL[x[2]]); m.font = F(bold=True, color=MATCH_INK[x[2]])
            if s_i > 0:
                for j in (1, 2):
                    wl.cell(i, j).font = F(color='A6A6A6')
            if s_i == 0 and prev is not None and x[0] != prev:
                for j in range(1, NC + 1):
                    wl.cell(i, j).border = Border(left=THIN, right=THIN, bottom=THIN, top=Side(style='medium', color=NAVY))
            if s_i == 0:
                wl.cell(i, 1).font = F(bold=(x[0] != prev))
            wl.row_dimensions[i].height = max(est_height(v, widths[chr(64 + j)]) for j, v in enumerate(vals, 1)
                                              if j in SUB or j in KEYS)
        last = wl.max_row
        if last > first:                            # merge the long item cells across its PYQ sub-rows
            for j in range(1, NC + 1):
                if j not in KEYS and j not in SUB:
                    wl.merge_cells(start_row=first, start_column=j, end_row=last, end_column=j)
        need = max(est_height(v, widths[chr(65 + k)]) for k, v in enumerate(y) if k + 1 not in SUB)
        have = sum(wl.row_dimensions[r].height for r in range(first, last + 1))
        if need > have:
            wl.row_dimensions[last].height = min(409, wl.row_dimensions[last].height + need - have)
        prev = x[0]
    wl.freeze_panes = 'E2'
    wl.auto_filter.ref = f'A1:M{wl.max_row}'
    wl.sheet_properties.tabColor = '2E75B6'
    wl.print_title_rows = '1:1'
    wl.page_setup.orientation = 'landscape'
    wl.page_setup.fitToWidth = 1; wl.page_setup.fitToHeight = 0
    wl.sheet_properties.pageSetUpPr.fitToPage = True

    # ---------- Sheet 3: PYQ Year Frequency ----------
    wf = wb.create_sheet('PYQ Year Frequency')
    yc, yd = Counter(), Counter()
    for x in rows:
        for y in set(re.findall(r'\b(20[12]\d)\b', x[6] or '')):
            yc[y] += 1
            if x[2] == 'Direct':
                yd[y] += 1
    wf.append(['PYQ Year', 'CA items linked', 'of which Direct', 'Bar'])
    for c in wf[1]:
        c.font = F(bold=True, color='FFFFFF'); c.fill = fill(NAVY); c.border = BOX
        c.alignment = Alignment(vertical='center', horizontal='center', wrap_text=True)
    mx = max(yc.values()) if yc else 1
    for y in sorted(yc):
        wf.append([y, yc[y], yd[y], '█' * max(1, round(yc[y] * 40 / mx))])
        i = wf.max_row
        for j in range(1, 5):
            c = wf.cell(i, j); c.font = F(); c.border = BOX
            c.alignment = Alignment(horizontal='center' if j < 4 else 'left', vertical='center')
        wf.cell(i, 4).font = F(color='2E75B6')
    wf.append([]); wf.append(['Match mix', 'Items'])
    hr = wf.max_row
    for j in (1, 2):
        wf.cell(hr, j).font = F(bold=True, color='FFFFFF'); wf.cell(hr, j).fill = fill(NAVY)
    for k in ('Direct', 'Thematic', 'Emerging'):
        wf.append([k, sum(1 for x in rows if x[2] == k)])
        i = wf.max_row
        wf.cell(i, 1).fill = fill(MATCH_FILL[k]); wf.cell(i, 1).font = F(bold=True, color=MATCH_INK[k])
        wf.cell(i, 2).font = F()
    for col, w in {'A': 14, 'B': 18, 'C': 16, 'D': 48}.items():
        wf.column_dimensions[col].width = w
    wf.freeze_panes = 'A2'
    wf.sheet_view.showGridLines = False
    wf.sheet_properties.tabColor = SLATE

    # ---------- Sheet 4: PYQ Bank (v19): every matched PYQ once, full text ----------
    wp = wb.create_sheet('PYQ Bank')
    used = OrderedDict()
    for x in rows:
        for k in id_lines(x[8]) or []:
            used.setdefault(k, []).append(x[0])
    wp.append(['PYQ ID', 'Paper', 'Year', 'Q', 'Marks', 'Full question', 'CA items', 'CA dates'])
    for c in wp[1]:
        c.font = F(bold=True, color='FFFFFF'); c.fill = fill(NAVY); c.border = BOX
        c.alignment = Alignment(vertical='center', horizontal='center', wrap_text=True)
    wp.row_dimensions[1].height = 36
    pw = {'A': 18, 'B': 10, 'C': 8, 'D': 10, 'E': 8, 'F': 90, 'G': 10, 'H': 30}
    for col, w in pw.items():
        wp.column_dimensions[col].width = w
    order = sorted(used, key=lambda k: (-len(used[k]), -int(bank_entry(k)['year']), PAPER_ORDER.index(bank_entry(k)['paper']), k))
    for k in order:
        v = bank_entry(k)
        dates = ', '.join(nice_date(d)[:6] for d in sorted(set(used[k]), reverse=True))
        wp.append([k, v['paper'], v['year'], v['q'], v['marks'] if v['exam'] == 'Mains' else '', v['text'], len(used[k]), dates])
    if not order:
        wp.append(['\u2014', '', '', '', '', 'No PYQ IDs in these rows: rows dated before 4 Nov 2026 keep the full question in the PYQ excerpt column.', '', ''])
    for i in range(2, wp.max_row + 1):
        for j in range(1, 9):
            c = wp.cell(i, j); c.font = F(); c.border = BOX; c.alignment = TOPC if j in (2, 3, 4, 5, 7) else TOP
        wp.cell(i, 1).font = F(bold=True, color=NAVY)
        wp.cell(i, 6).font = F(italic=True, color='404040')
        wp.row_dimensions[i].height = max(est_height(wp.cell(i, 6).value, pw['F']), est_height(wp.cell(i, 8).value, pw['H']))
    wp.freeze_panes = 'B2'
    wp.auto_filter.ref = f'A1:H{wp.max_row}'
    wp.sheet_properties.tabColor = '8497B0'

    # ---------- Sheet 5: How to Use ----------
    wh = wb.create_sheet('How to Use')
    guide = [
        ('What this is', ''),
        ('', "A running log matching each day's current affairs to every UPSC CSE PYQ year in which the same theme was asked (Prelims 2011-2026 and Mains GS1-GS4 2013-2026 from your GitHub PYQ corpus). Each item carries Prelims and Mains key points to recall for CSE 2027."),
        ('Tabs', ''),
        ('Revision Cards', 'Read-first view. One card per news item, newest day first; two columns so it reads on a phone without sideways scrolling.'),
        ('Master Log', 'The same data as a filterable table. Filter Match = Direct or a GS Area; sort by PYQ Years.'),
        ('PYQ Year Frequency', 'How many logged items link to each PYQ year, and how many of those are Direct.'),
        ('PYQ Bank', 'Every past question matched in these rows, once: PYQ ID, paper, year, full text, how many CA items matched it and on which dates (most-matched first). From 4 Nov 2026 the data CSV stores PYQ IDs; the cards and Master Log show the full text from the bank.'),
        ('Card fields', ''),
        ('#n · Match', 'Direct = a PYQ asked this exact theme. Thematic = the item is a fresh example for a related PYQ. Emerging = not asked yet; high-probability for 2027.'),
        ('PYQ years', 'Every year the theme appeared, Prelims and Mains, with the papers.'),
        ('Prelims recall', 'Testable one-line facts: Acts and years, Articles, bodies, places, numbers.'),
        ('Mains recall', 'Answer-ready points, tagged [Intro data], [Issue], [Judgment], [Committee], [Way forward], [Counterpoint], [Ethics].'),
        ('PYQ excerpts', 'Every past question matched to the item, in full, one per year: P = Prelims, GS1-GS4 = Mains with marks. In the Master Log each PYQ is its own sub-row (year, paper, full question) under the item; the item cells are merged across its sub-rows, and Date, GS Area, Syllabus Tag and Match repeat (greyed) so filters keep whole items.'),
        ('Syllabus', 'Exact syllabus portion: Paper \u203a Subject \u203a Topic (official syllabus line) \u203a Subtopic. Filter the Master Log on it to revise topic-wise.'),
        ('V&R recall', "Syllabus base for newspaper items (from 31 Oct 2026): core facts from Vajiram & Ravi's page on that exact syllabus subtopic; identical for items sharing a subtopic. V&R's daily news facts are merged into the Prelims/Mains recall, like Next IAS and Drishti. Rows of 29-30 Oct 2026 show V&R daily facts here."),
        ('Expected 2027 Qs', 'How the examiner would use this item in 2027: one probable Prelims stem, one probable Mains question with paper and marks, and the PYQ years it extends. The two lines test different things by design.'),
        ('Revision routine', ''),
        ('Daily (10 min)', "Read today's cards: Prelims recall aloud, one Mains point per card in your own words."),
        ('Weekly', 'Master Log, filter Match = Direct: write intros using the [Intro data] points; attempt one [Mains 2027] question in full.'),
        ('Before a test', 'Filter by GS Area; revise the Prelims recall column and the [Prelims 2027] lines only.'),
        ('Daily run', 'Upload or drop the day\'s paper in UPSC Prep/Daily Newspaper/ and ask for the CA-PYQ match (skill: ca-pyq-daily-match).'),
    ]
    wh.append(['Field', 'Explanation'])
    for c in wh[1]:
        c.font = F(bold=True, color='FFFFFF'); c.fill = fill(NAVY)
    for a, b in guide:
        wh.append([a, b])
        i = wh.max_row
        wh.cell(i, 1).font = F(bold=True); wh.cell(i, 2).font = F()
        wh.cell(i, 1).alignment = TOP; wh.cell(i, 2).alignment = TOP
        if a and not b:
            for j in (1, 2):
                wh.cell(i, j).fill = fill('D9E2F3')
        wh.row_dimensions[i].height = est_height(b, 100)
    wh.column_dimensions['A'].width = 22; wh.column_dimensions['B'].width = 100
    wh.freeze_panes = 'A2'
    wh.sheet_view.showGridLines = False
    wh.sheet_properties.tabColor = 'A6A6A6'
    wb.save(out_xlsx)

def sheet_safe(v):
    """Google Sheets strips one leading apostrophe and evaluates =,+,- as formulas: guard them."""
    v = str(v)
    return "'" + v if v[:1] in ("'", '=', '+', '-') else v

def write_csv(rows, path):
    with open(path, 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
        w.writerow(HEAD); w.writerows([[sheet_safe(x[k]) for k in PERM] for x in rows])

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--logs', nargs='*', default=[]); ap.add_argument('--today')
    ap.add_argument('--out-xlsx', required=True); ap.add_argument('--out-day-csv')
    ap.add_argument('--monthly-dir', help='also write one workbook per month: <dir>/CA-PYQ Match Log YYYY-MM.xlsx')
    ap.add_argument('--pyq-bank', default='pyq_bank.json', help='PYQ bank from load_pyq.py (needed for rows with PYQ IDs)')
    a = ap.parse_args()
    import os
    if os.path.exists(a.pyq_bank):
        BANK.update(json.load(open(a.pyq_bank, encoding='utf-8')))
    rows = load(a.logs, a.today)
    build(rows, a.out_xlsx)
    if a.monthly_dir:
        import os
        os.makedirs(a.monthly_dir, exist_ok=True)
        for ym in sorted({x[0][:7] for x in rows}):
            month_rows = [x for x in rows if x[0][:7] == ym]
            build(month_rows, os.path.join(a.monthly_dir, f'CA-PYQ Match Log {ym}.xlsx'))
            print('monthly:', ym, len(month_rows), 'rows')
    if a.today and a.out_day_csv:
        d = json.load(open(a.today, encoding='utf-8'))[0]['date']
        day = [x for x in rows if x[0] == d]
        write_csv(day, a.out_day_csv)
        chk = list(csv.reader(open(a.out_day_csv, newline='', encoding='utf-8')))
        assert len(chk) == len(day) + 1 and all(len(x) == len(HEAD) for x in chk), 'CSV round-trip failed'
        print('today CSV:', a.out_day_csv, len(day), 'rows,', len(open(a.out_day_csv, encoding='utf-8').read()), 'chars')
    print('workbook rows:', len(rows), '| by date:', sorted(Counter(x[0] for x in rows).items(), reverse=True),
          '| match:', dict(Counter(x[2] for x in rows)))
