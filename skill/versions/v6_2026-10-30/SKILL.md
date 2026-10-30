---
name: "ca-pyq-daily-match"
description: "Run the daily UPSC current-affairs to PYQ match: read the day's The Hindu plus Next IAS/Drishti IAS, quote every past question for every year a theme was asked (Prelims 2011-26, Mains GS1-4 2013-26; corpus cloned from GitHub), add CSE 2027 recall points and MECE expected-question notes, and rebuild the CA-PYQ Match Log to a locked Calibri-12 design."
---

# Daily CA → PYQ Match (UPSC CSE 2027)

Triggered manually by the user ("run today's match", a newspaper PDF upload, or this skill's name). Never schedule it.

## At a glance

| Stage | What happens | Time |
|---|---|---|
| 1. Inputs | Get the paper (Drive), pull Next IAS + Drishti (web), clone PYQ corpus (**GitHub — never Drive**), load past daily data (Drive CSV store) | 5 min |
| 2. Processing | Extract items → match all PYQ years → classify → write recall points and expected 2027 questions | bulk of run |
| 3. Output | Build the monthly workbook (locked design) → send it → upload today's CSV to the data folder → verify | 10 min |
| 4. Reply | 5-8 lines: count, top Direct hits, new Emerging themes, caveats | — |

Run checklist (tick every box before replying):

- [ ] PYQ corpus cloned from GitHub and loaded (`load_pyq.py` prints 2020-2026 from `pyq_db` (each year GS1-GS3 20 each, GS4 19, Essay 8), 552 old-index Mains records for 2013-2019, and full-paper Prelims stems 2020/2021/2022/2023/2024/2025/2026 = 100 each)
- [ ] Every page of the paper read (state page count read)
- [ ] Next IAS and Drishti IAS for the date pulled, or reason stated
- [ ] Every row has: all PYQ years, **one quoted question for every year listed** (4 years → 4 quotes), Match class, 3-5 Prelims + 3-4 Mains recall points
- [ ] Every row's note carries the three MECE lines: `[Prelims 2027]`, `[Mains 2027]`, `[Link]`
- [ ] Every figure, name and quoted phrase traceable to the source text (P-5.5)
- [ ] Workbook built with the Appendix A script, design assertions passed; month-wise files written (O-2b) and the current month's file sent
- [ ] Today's CSV (`CA-PYQ Data YYYY-MM-DD`) uploaded to the Drive data folder and verified cell-by-cell against the local CSV; no gap in the month's dates (I-6)

---

## 1. INPUTS

| # | Input | Where | How to read it |
|---|---|---|---|
| I-1 | The day's newspaper (The Hindu, Delhi) | Chat upload, or Drive `UPSC Prep/Daily Newspaper/` (file `YYYY-MM-DD` or `TH- Delhi DD-MM.pdf`; search `title contains 'DD-MM'`) | Upload: `Read` with `pages` (max 20 per call). Drive PDF ≤10 MB: `download_file_content`. Drive PDF >10 MB: `read_file_content` (returns full text; saved to a JSON file → `fileContent`) |
| I-2 | Next IAS current affairs, same date | `nextias.com/ca/current-affairs/DD-MM-YYYY` | WebFetch; if blocked, WebSearch with `allowed_domains` |
| I-3 | Drishti IAS news analysis, same date | `drishtiias.com/current-affairs-news-analysis-editorials/news-analysis/DD-MM-YYYY` | Same. Pull these yourself — never ask the user for links |
| I-4 | **PYQ corpus — Prelims 2011-2026 + Mains GS1-GS4 2013-2026 + Essay 2020-2026** | **GitHub only:** public repo `https://github.com/skv29grd-oss/pyq_index-`. One copy per year, named year-wise then paper-wise: **2020 onwards in `pyq_db/<year>/<year> <paper>.csv`** — six files per year: `<year> Prelims GS1.csv`, `<year> Mains GS1.csv` … `<year> Mains GS4.csv`, `<year> Mains Essay.csv` (2020-2024 from the official UPSC scans, 2025-2026 web-verified; Prelims in Set/Series A numbering); **Prelims 2011-2019** in `Prelims_Index.txt`, `Prelims_Index_Part2_*.txt`, `Prelims_Index_Part3_*.txt`; **Mains 2013-2019** in `GS1_Index.txt`…`GS4_Index.txt` | `git clone --depth 1 https://github.com/skv29grd-oss/pyq_index- pyq` in bash, then `python3 pyq/load_pyq.py pyq` (the repo's own loader; Appendix B). **Do not download PYQ files from Drive** — Drive returns them inline into the chat instead of to disk, which floods context and leaves nothing for regex search. If the clone fails, use `https://raw.githubusercontent.com/skv29grd-oss/pyq_index-/main/<file>` with curl; if GitHub is unreachable, stop and tell the user rather than matching from memory |
| I-6 | Past daily data (Drive CSV store) | Drive folder `CA-PYQ Data (CSV store)` (`115FUx1SQC6_EcbsFyjHX_epYGbpQgCck`, inside `UPSC Prep/CA-PYQ Daily Logs`), one small Google Sheet per day titled `CA-PYQ Data YYYY-MM-DD` | `search_files` with `parentId = '115FUx1SQC6_EcbsFyjHX_epYGbpQgCck' and title contains 'CA-PYQ Data '`; for each, `download_file_content(exportMimeType='text/csv')` → save as `logs/day_YYYY-MM-DD.csv`. **Gap check (mandatory):** the dates found must run unbroken from the first logged day of the current month to yesterday's newspaper date (skip dates the user never ran, but ask if unsure). A missing day means history would silently vanish from the workbook — use I-6b to restore it before building. Titles `CA-PYQ Log YYYY-MM-DD` (older name, in the parent folder) are legacy: read them too if present, never write new ones |
| I-6b | Fallback when a day is missing | The latest `CA-PYQ Match Log YYYY-MM.xlsx` (chat upload, or the parent Drive folder; sort by modifiedTime) | `download_file_content` → result is saved to a JSON file → base64-decode `content` to `prev.xlsx` → split its Master Log into `logs/day_YYYY-MM-DD.csv` by Date (Appendix B snippet) for the missing dates only, and **upload each restored day to the data folder (O-4)** so the gap is closed for good |

Both sites publish late: a 404 or "No article found" for today usually means it is not up yet. Fall back to the most recent date not already in the log (yesterday's page, `.../news-in-short-DD-MM-YYYY` on Next IAS carries the short items), merge those items, and write that date into `Source` (`Next IAS (21-09-2026)`). Say in the reply which dates were used.

PYQ coverage note: each year exists in exactly one place in the repo (no duplicates). **2020-2026 are full papers in `pyq_db/`** (Prelims 100 Qs; Mains GS1-GS3 20 Qs, GS4 13 parts + 6 full case studies, Essay 8 topics) — 2020, 2021, 2022, 2023 and 2024 transcribed from the official UPSC scans (Mains 2024 web-verified), 2025-2026 web-verified. 2013-2019 Mains come from the old topic-wise indexes; their GS4 case studies are a topic index only (no full text), so quote what the index gives and mark it `[partial]`, and there is no Essay before 2020. Prelims 2011-2019 are topic-wise and incomplete. A new year is added to `pyq_db/` only — as the six `<year> <paper>.csv` files in `pyq_db/<year>/` — and its records are removed from the old indexes in the same commit, with `YRS_OLD` in `load_pyq.py` narrowed so the duplicate guard passes. When stripping a year from the old indexes, also (a) re-tag records tagged with that year that are not in the official paper — confirm the true year on a published copy first (2020 run: Gandhara art → 2019, National Watershed Project → 2019, "national wealth … enclaves of modernity" → 2017) — and (b) drop records tagged with another year that are really that year's question (2020 run: GS4 "will to power", tagged 2017 but Mains 2020 GS4 Q3(b)).

Where each input lives (no exceptions): **newspaper and logs → Google Drive; PYQ corpus → GitHub; Next IAS/Drishti → web.** The Drive file IDs that once held PYQ indexes are retired.

Drive rules learned the hard way:

- Drive is for the newspaper and logs only. `read_file_content` is unreliable for large plain-text files — use `download_file_content` and decode; small files may come back inline rather than saved to disk.
- Oversized tool results are saved to a JSON file; decode `content` (base64) or `fileContent` (text) with Python. Never paste them into context.
- `create_file` takes only inline `textContent`; there is no append, no edit-in-place (`update_file` changes only title/parent), no Sheets formatting, and no binary upload you can trust (base64 of an xlsx is too large to paste daily). That is why Drive keeps a **machine-readable CSV store of one small sheet per day** (append-only, each file pasted once) and the styled workbook is the **only user-facing deliverable**, rebuilt from the store every run and sent with SendUserFile. A single running monthly CSV is not feasible: it would have to be re-pasted in full every day, growing to megabytes.
- Google Sheets strips one leading `'` and treats leading `=`,`+`,`-` as formulas. The Appendix A script guards these.

## 2. PROCESSING

**P-1 Extract.** Read every page. Keep items with a syllabus hook: polity, governance, IR, economy, environment, S&T, security, society, disaster management, art & culture, plus Prelims-able sports/awards/places. Skip city crime, obituaries, classifieds, puzzles, club football. Expect 25-35 items. For each capture: one self-contained topic sentence with the quotable figures, and the page reference.

**P-2 Merge.** One row per theme. If a later page or Next IAS/Drishti covers the same story, merge the facts into that row. If it continues a row from an earlier day, keep it as a new row and write "Refines the DD Mon entry" in the note's `[Link]` line.

**P-3 Match all PYQ years.** Search the corpus with 2-4 precise patterns per item (Appendix B helper: case-sensitive for acronyms, word boundaries, no noisy short tokens like `NGO` that hit `Congo`). Read every hit; keep only genuine thematic matches. List **every** year the theme appeared across Prelims and Mains, ascending, plus the papers (e.g. `Prelims + GS2 + GS3`). Quote **every** matched question verbatim into `pyq_excerpt`, one per line, ascending by year (Prelims `P <year>:`, Mains `GS<n> <year> (<marks>):`). Put the closest match first only if it shares the earliest year; otherwise keep strict year order. Cap at eight lines — beyond that keep the eight nearest and add `+N more`.

**One year → one quoted question. No exceptions.** If a theme was asked in 2013, 2016, 2019 and 2024, the cell carries four quoted questions, not the closest one. Repeat the question text even when two years asked almost the same thing — the repetition across years is exactly the signal the user is tracking. If the same year asked it in two papers (Prelims and GS3, say), that is two lines. Never write "also asked in 2016, 2019" as a summary line instead of quoting them.

**P-4 Classify.**

| Match | Rule |
|---|---|
| Direct | A PYQ asked this exact theme or place/fact |
| Thematic | The item is a fresh example or data point for a related PYQ |
| Emerging | No PYQ yet; flag as high-probability for 2027 |

**P-5 Write the CSE 2027 recall points** — the part the user revises from.

- *Prelims recall*: 3-5 one-line, testable facts, each ≤22 words: Act + year, Article/Schedule, body + parent ministry, statutory status, place on map, species status, key number from the item.
- *Mains recall*: 3-4 points, each ≤25 words, each starting with a tag: `[Intro data]`, `[Issue]`, `[Judgment]`, `[Committee]`, `[Way forward]`, `[Counterpoint]`, `[Ethics]`. At least one `[Way forward]` or `[Counterpoint]`.
- Accuracy rule: only facts stated in the source item, or static facts you are certain of. Never invent figures, dates or names; if unsure, leave it out. No fact repeated across the two lists.

**P-5.5 Source fidelity — say it the way the source says it.**

- *Numbers*: copy exactly as printed, with unit, period and the source's own numbering convention — `₹7,280 crore`, `41.95%`, `3,052 km`, `53,700 tonnes in FY2024-25`, `1,13,943 electors` (not "1.14 lakh"). Never round, convert or "about"-ify a printed figure; if a lakh/crore form reads better, put the printed figure first and the conversion in brackets. If the source gives a range (`13-14% of GDP`), keep the range.
- *Names*: Act or scheme with its year (`Poisons Act, 1919`), case with its year (`Sadiq Ali v ECI (1971)`), body with its parent ministry, person with designation on first use, place with district/State.
- *Quotes*: at most one per row, ≤15 words, inside double quotes, only words that actually appear in the source, attributed (`SC Bench`, `Editorial`, `Commerce Minister`). Use them for judicial dicta, official statements and coined phrases (`"delete first, verify later"`); paraphrase everything else.
- *Topic sentence*: ≤45 words, actor → action → number → consequence, self-contained so it reads without the headline. Semicolons to stack the two or three facts that matter.
- *Recall bullets*: one testable fact each, active voice, no filler ("it may be noted", "in this regard"). Each must stand alone out of context.
- *No invention*: if a figure, date or name is not in the source and you are not certain of it as static knowledge, leave it out. Unverifiable is worse than absent.

**P-6 Relevance & Revision Note — the expected CSE 2027 questions, MECE.** This column answers one question: *if the examiner uses this item in 2027, how would it be asked?* Write exactly three tagged lines, in this order:

```
[Prelims 2027] <one probable MCQ stem, in UPSC's own phrasing>
[Mains 2027] <one probable question with directive verb, paper and marks>
[Link] <PYQ years it extends; earlier log entry it refines>
```

- **Mutually exclusive**: the Prelims stem and the Mains question must test different things. Draw each from a different bucket — Prelims buckets: statutory basis or parent body · provision (Article, Schedule, Section) · place or map · number, threshold or timeline · status (species, index rank, scheme stage). Mains buckets: causes and drivers · impacts and stakeholders · institutional and governance design · ethics and rights · way forward and reform · comparison (another State, country or earlier episode).
- **Collectively exhaustive**: between the two lines, the item's whole testable surface is covered — the static fact a Prelims setter would lift, and the analytical demand a Mains setter would frame. If an item genuinely carries two strong Prelims angles, pick the one the sources make testable today and let the Mains line carry the rest; never leave a bucket half-covered by a vague "significance of..." line.
- Write them as questions, in the examiner's voice, not as topics. Prelims as a statement-type, pairs or "how many of the above" stem; Mains with the directive verb and marks — `Discuss. (GS2, 15)`, `Critically examine. (GS3, 10)`.
- Each line ≤35 words. Do not repeat the Prelims/Mains recall bullets — those are the raw material; this column is the question they would be asked in.
- `[Link]` names the PYQ years the item extends, plus "Refines the DD Mon entry" when it continues an earlier row. For an `Emerging` row write `first appearance — no PYQ yet`.

Example (Kasturirangan report row):

```
[Prelims 2027] Consider statements on ecologically sensitive areas: notified under the Environment (Protection) Act, 1986; Kasturirangan HLWG reported in 2013. Which are correct?
[Mains 2027] Ecologically sensitive area notifications pit conservation against livelihoods in the Western Ghats. Examine, with State responses. (GS3, 15)
[Link] Extends 2011, 2013, 2016, 2021, 2025; refines the 20 Sep entry.
```

Write today's rows to `today_YYYY-MM-DD.json` in the scratchpad — a list of objects with keys `date, topic, source, gs_area, years, papers, pyq_excerpt, match, note, prelims, mains` (`prelims`/`mains` are lists of strings; `pyq_excerpt` is a newline-separated block, one quoted question per line; `note` is the three tagged lines from P-6, newline-separated).

## 3. OUTPUT

**O-1 Schema** (11 columns, fixed order — the Drive CSV store and the workbook's Master Log use it):

`Date | GS Area | Match | CA Topic / Headline | Prelims Recall (CSE 2027) | Mains Recall (CSE 2027) | PYQ Years (all occurrences) | Paper(s) | PYQ Excerpts (all, Prelims + Mains) | Relevance & Revision Note | Source`

`Date` is the newspaper's date, not the run date. `Source` carries publication **and page** so the original can be found again — `The Hindu (p1,12)`, `The Hindu (p6 Editorial)`, `Next IAS (21-09-2026)`. `PYQ Excerpts (all, Prelims + Mains)` carries **every** matched question, not just the closest one — one per line, ascending by year, Prelims tagged `P <year>` and Mains `GS<n> <year> (<marks>)`, each quoted verbatim:

```
P 2011: "Three criteria contributing to the recognition of Western Ghats-Sri Lanka and Indo-Burma regions as biodiversity hotspots..."
GS1 2013 (5): "Bring out the causes for more frequent landslides in the Himalayas than in Western Ghats."
P 2016: "'Gadgil Committee Report' and 'Kasturirangan Committee Report' relate to..."
GS1 2021 (10): "Differentiate the causes of landslides in the Western Ghats and the Himalayas."
GS4 2025 (10): "...ethical dilemmas related to environmental clearance of projects in ecologically sensitive areas."
```

That row's `PYQ Years` reads `2011, 2013, 2016, 2021, 2025`, so the cell carries five quoted questions — one per year. A cell with one quote against four listed years is the single most common defect in this log; VERIFY fails the run when it happens.

The years listed in `PYQ Years` and the lines here must agree — one line per year-paper pair. Where the index is unclear (OCR gaps), quote the fragment you have and mark it `[partial]` rather than paraphrasing. For an `Emerging` row with no match, write `None yet` plus the nearest adjacent question in one line.

`Relevance & Revision Note` carries the three MECE lines from P-6 — the expected 2027 Prelims stem, the expected 2027 Mains question with paper and marks, and the `[Link]` line. It is a forecast column, not a summary column.

Rows logged before 2026-09-23 carry only the single closest question in the excerpts column and a prose note; do not retro-expand them unless the user asks.

**O-2 Build the workbook.** Save Appendix A as `ca_pyq_build.py` in the scratchpad. Keep the daily CSVs downloaded in I-6 in their own `logs/` subfolder, separate from today's outputs — never let `upload_YYYY-MM-DD.csv` (O-4's output) land in `logs/` before this step runs again, or the `day_*.csv` glob below will pick up today twice. Run:

```
python3 ca_pyq_build.py --logs logs/day_*.csv --today today_YYYY-MM-DD.json \
  --out-xlsx "master/CA-PYQ Match Log.xlsx" --out-day-csv upload_YYYY-MM-DD.csv \
  --monthly-dir /mnt/user-data/outputs
```

(`load()` also dedupes on date+topic-prefix as a second line of defence, but don't rely on it — keep the folders separate. It also accepts day-sheets whose ninth header still reads `Representative PYQ (excerpt)`.)

The workbook has four tabs, all Calibri 12:

| Tab | Layout | Purpose |
|---|---|---|
| Revision Cards | Two columns (label 20, content 100), newest day first; navy day banner with Direct/Thematic/Emerging counts; each card = headline, Area·Source, PYQ years, Prelims recall (green tint), Mains recall (bold tags), PYQ excerpts (italic, one line per question), Expected 2027 Qs (three tagged lines); row heights pre-computed | Read-first view that works on a phone without sideways scrolling |
| Master Log | 11-column filterable table, date-banded, Match colour-coded, frozen at D2 | Filter by Match / GS Area, sort by years |
| PYQ Year Frequency | Year → items linked, of which Direct, bar; match mix | Spot which PYQ years the news keeps refreshing |
| How to Use | Field glossary and revision routine | — |

**O-2b Month-wise split.** The `--monthly-dir` flag writes one workbook per calendar month — `CA-PYQ Match Log YYYY-MM.xlsx` — each built by the same `build()` from only that month's rows, so every monthly file carries all four tabs, the locked design, and a PYQ Year Frequency tab for that month alone. The month is taken from the newspaper `Date`, never the run date. **One workbook per month is the only workbook the user reads; it is rebuilt in full every run and a new month starts a new file automatically.** The full multi-month master is built into `master/` (not outputs) for I-6b only. Never create per-day workbooks or per-day user-facing sheets.

**O-2a Design lock — the look must not drift between days.** The Appendix A script is the single source of truth; never hand-format a cell in Excel or Sheets. If the design has to change, change the script and this table together, then rebuild every day from the CSV store so old and new days match.

| Element | Fixed value |
|---|---|
| Typeface | Calibri **12** in every cell of every tab — no exceptions, no second size. Emphasis comes from weight, colour and fill, never from size |
| Palette | Navy `1F3864` (headers, day banners, PYQ years, Mains tags) · slate `44546A` (card labels) · blue `2E75B6` (frequency bars) · grey `404040` italic (PYQ excerpts) |
| Match colours | Direct fill `C6EFCE` ink `145A32` · Thematic fill `FFF2CC` ink `7D6608` · Emerging fill `E7E6E6` ink `3B3838` |
| Date banding | Alternating `FFFFFF` / `F2F6FB` per date block; medium navy top border on the first row of each new date; bold date cell on that row |
| Borders | Thin `BFBFBF` box on Master Log and frequency cells; bottom-only rule between card lines |
| Alignment | Every body cell top-aligned with wrap on; Date, GS Area, Match, PYQ Years, Paper(s) centred; everything else left |
| Revision Cards | Two columns only — label 20, content 100 — so it reads on a phone; gridlines off; navy day banner (height 26) with the day's Direct/Thematic/Emerging counts; seven labelled lines per card in fixed order (headline · Area·Source · PYQ years · Prelims recall on `F4F9F1` tint · Mains recall with bold `[Tags]` · PYQ excerpts in italic · Expected 2027 Qs); 10-pt spacer row between cards; portrait, fit to one page wide |
| Master Log widths | `A:12 B:18 C:11 D:55 E:55 F:58 G:22 H:16 I:62 J:55 K:18`; header row height 36, white bold on navy, centred and wrapped; freeze at `D2`; autofilter `A1:K<last>`; landscape, fit to one page wide, header row repeated on every printed page |
| Row heights | Pre-computed by `est_height()` (chars ÷ (width × 1.15) × 15.6 pt + 6, capped 409) — never left to Excel's autofit, which collapses wrapped text on phones |
| PYQ Year Frequency | Year, items linked, of which Direct, and a `█` bar scaled to 40 characters; match-mix block below; freeze `A2`; gridlines off |
| How to Use | Field glossary and revision routine; section rows tinted `D9E2F3`; freeze `A2`; gridlines off |
| Tab order & colours | Revision Cards (navy `1F3864`) → Master Log (`2E75B6`) → PYQ Year Frequency (`44546A`) → How to Use (`A6A6A6`). Revision Cards is always the first sheet the file opens on |

Why this shape: the user reads on a phone, so the first tab is a single narrow column of cards with no sideways scrolling; the table view is kept for filtering on a laptop. One typeface at one size keeps wrapped text predictable, which is what makes pre-computed row heights hold.

**O-3 Deliver.** Send the **current month's** workbook (`CA-PYQ Match Log YYYY-MM.xlsx` for today's newspaper date) with `SendUserFile`/`present_files`, one-line caption. Send earlier months only on the first run after this split was introduced, or when a backfilled row changed an earlier month.

**O-4 Store in the Drive CSV store.** Upload **only today's rows**: `create_file(title='CA-PYQ Data YYYY-MM-DD', parentId='115FUx1SQC6_EcbsFyjHX_epYGbpQgCck', contentMimeType='text/csv', textContent=<exact text of upload_YYYY-MM-DD.csv>)`. For long files (most days), delegate the upload to a subagent that reads the file and pastes it verbatim — and tell it to report the Drive id only; **you run the verification yourself**. Verify by exporting back and comparing cell-by-cell with Python (whitespace-normalised). `download_file_content(exportMimeType='text/csv')` saves to disk only when the result exceeds the token cap, and a small file comes back inline instead (not machine-comparable) — in that case export with `exportMimeType='application/zip'` (always large, always saved), unzip the `.html`, parse the `<td>` cells and compare those; do not use PDF export. If a mismatch comes from transcription, trash the new file and re-upload (max twice). `fileSize: "1"` on a Google-native file is normal. **O-4b Tell the user** in the reply that the Drive CSV store was updated and that the workbook in chat is the file to keep: the connector cannot overwrite the user's Drive copy of the workbook, so they replace it themselves. Do not offer to edit Drive sheets in place.

**O-5 Reply** (user wants concise, no pleasantries): rows added and match mix; 3-5 highest-yield Direct items with their PYQ years; new Emerging themes; any input not read (e.g., Next IAS/Drishti blocked) and the PYQ-coverage caveat.

## 4. VERIFY (the same output every run)

Before replying, fill in `XLSX = "/mnt/user-data/outputs/CA-PYQ Match Log YYYY-MM.xlsx"` (current month), `TODAY_JSON = "today_YYYY-MM-DD.json"`, `UPLOAD_CSV = "upload_YYYY-MM-DD.csv"` and `SOURCE_TXT` (the cleaned newspaper text from I-1) (the exact paths used in O-2/O-4), then run and fix until all pass:

```python
import csv, json, re, openpyxl

XLSX, TODAY_JSON, UPLOAD_CSV, SOURCE_TXT = "...", "...", "...", "..."   # fill in, see above; XLSX = the current month file
TAGS = ('[Intro data]', '[Issue]', '[Judgment]', '[Committee]', '[Way forward]', '[Counterpoint]', '[Ethics]')

wb = openpyxl.load_workbook(XLSX, rich_text=True)
assert wb.sheetnames == ['Revision Cards', 'Master Log', 'PYQ Year Frequency', 'How to Use']
ml = wb['Master Log']
hdr = [c.value for c in ml[1]]
assert hdr == ['Date','GS Area','Match','CA Topic / Headline','Prelims Recall (CSE 2027)','Mains Recall (CSE 2027)',
               'PYQ Years (all occurrences)','Paper(s)','PYQ Excerpts (all, Prelims + Mains)','Relevance & Revision Note','Source']
sizes = {c.font.sz for ws in wb for row in ws.iter_rows() for c in row if c.value is not None}
assert sizes == {12}, sizes

today = json.load(open(TODAY_JSON))
dates = {o['date'] for o in today}
assert len(dates) == 1, f"today's JSON must be a single date, found {dates}"
for o in today:
    assert o['match'] in ('Direct', 'Thematic', 'Emerging')
    assert 3 <= len(o['prelims']) <= 5, o['topic']
    assert 3 <= len(o['mains']) <= 4, o['topic']          # P-5: 3-4, not 2-4
    assert all(any(m.startswith(t) for t in TAGS) for m in o['mains']), o['topic']   # tag whitelist
    assert all(len(p.split()) <= 22 for p in o['prelims']), o['topic']   # word limits
    assert all(len(m.split()) <= 25 for m in o['mains']), o['topic']
    assert any(m.startswith('[Way forward]') or m.startswith('[Counterpoint]') for m in o['mains']), o['topic']
    combined = [x.lower() for x in o['prelims'] + o['mains']]
    assert len(combined) == len(set(combined)), f"repeated fact in {o['topic']}"     # no repeats across the two lists
    assert o['years'] and o['pyq_excerpt']
    # P-3: one quoted question per listed year — four years must show four quotes
    yrs = set(re.findall(r'\b(20[12]\d)\b', o['years']))
    exc = set(re.findall(r'\b(20[12]\d)\b', o['pyq_excerpt']))
    assert yrs <= exc, f"years without an excerpt in {o['topic'][:40]}: {sorted(yrs - exc)}"
    lines = [l for l in o['pyq_excerpt'].splitlines() if l.strip()]
    assert len(lines) >= len(yrs), f"{len(lines)} quoted lines for {len(yrs)} years in {o['topic'][:40]}"
    # P-6: the note is three MECE lines of expected 2027 questions
    nl = [l.strip() for l in o['note'].splitlines() if l.strip()]
    assert len(nl) == 3, f"note must have 3 lines, has {len(nl)}: {o['topic'][:40]}"
    assert nl[0].startswith('[Prelims 2027]') and nl[1].startswith('[Mains 2027]') and nl[2].startswith('[Link]'), o['topic'][:40]
    assert all(len(l.split()) <= 35 for l in nl), o['topic'][:40]
    assert re.search(r'\(GS[1-4],\s*\d{1,2}(\.5)?\)', nl[1]), f"Mains line needs paper and marks: {o['topic'][:40]}"

# O-4: the Drive upload CSV must match today's JSON row-for-row, not just the script's own round-trip
with open(UPLOAD_CSV, newline='') as f:
    up_rows = list(csv.DictReader(f))
assert len(up_rows) == len(today), (len(up_rows), len(today))

# P-5.5 source fidelity: every quoted phrase in today's rows must appear in the source text.
# The note is excluded on purpose — its lines are forecast questions in the examiner's voice, not quotations.
src = open(SOURCE_TXT, encoding='utf-8', errors='ignore').read()
norm = lambda t: re.sub(r'[\s‐-―]+', ' ', t.replace('’', "'").replace('“', '"').replace('”', '"'))
flat = norm(src)
for o in today:
    for q in re.findall(r'"([^"]{8,120})"', norm(' | '.join([o['topic']] + o['prelims'] + o['mains']))):
        assert norm(q) in flat, f"quote not in source: {o['topic'][:40]} -> {q[:60]}"

# P-5.5 expression: topic length, banned filler, and figures that cannot be traced to the source
FILLER = ('it may be noted', 'in this regard', 'it is important to note', 'needless to say', 'plays a vital role')
digits = lambda t: re.sub(r'[,\s]', '', t)
flat_d, untraced = digits(flat), []
for o in today:
    assert len(o['topic'].split()) <= 45, o['topic'][:60]
    blob = ' '.join([o['topic']] + o['prelims'] + o['mains']).lower()
    assert not any(f in blob for f in FILLER), o['topic'][:40]
    for n in set(re.findall(r'\d[\d,.]*', ' '.join([o['topic']] + o['prelims']))):
        if len(digits(n)) >= 3 and digits(n) not in flat_d:
            untraced.append((o['topic'][:35], n))
print('figures not found in the source — confirm each is static knowledge:', untraced)

# O-2a design lock: the workbook must look identical every day
rc = wb['Revision Cards']
W = {'A':12,'B':18,'C':11,'D':55,'E':55,'F':58,'G':22,'H':16,'I':62,'J':55,'K':18}
design = [
    ('cards widths 20/100', (rc.column_dimensions['A'].width, rc.column_dimensions['B'].width) == (20, 100)),
    ('cards gridlines off', rc.sheet_view.showGridLines is False),
    ('master widths', all(ml.column_dimensions[c].width == w for c, w in W.items())),
    ('master freeze D2', ml.freeze_panes == 'D2'),
    ('master autofilter', ml.auto_filter.ref == f'A1:K{ml.max_row}'),
    ('header height 36', ml.row_dimensions[1].height == 36),
    ('print title row', str(ml.print_title_rows).replace('$', '') == '1:1'),
    ('Calibri 12 only', {(c.font.name, c.font.sz) for ws in wb for r in ws.iter_rows() for c in r if c.value is not None} == {('Calibri', 12)}),
    ('body wraps', all(c.alignment.wrap_text for c in ml[2])),
    ('tab colours', [wb[n].sheet_properties.tabColor.rgb[-6:] for n in wb.sheetnames] == ['1F3864', '2E75B6', '44546A', 'A6A6A6']),
]
assert not [n for n, ok in design if not ok], [n for n, ok in design if not ok]

# O-2b month split: every monthly file holds only its own month, and today's rows sit in the current month file
import glob, os
for f in glob.glob(os.path.join(os.path.dirname(XLSX), 'CA-PYQ Match Log 20??-??.xlsx')):
    ym = f[-12:-5]
    m = openpyxl.load_workbook(f)['Master Log']
    assert all(str(r[0])[:7] == ym for r in m.iter_rows(min_row=2, values_only=True) if r[0]), f'mixed months in {f}'
assert os.path.basename(XLSX) == f"CA-PYQ Match Log {today[0]['date'][:7]}.xlsx", 'XLSX must be the current month file'
print('OK', ml.max_row - 1, 'rows')
```

`SOURCE_TXT` is the cleaned newspaper text saved in I-1; append the Next IAS and Drishti text you fetched to the same file so their figures and quotes are checked too, otherwise expect them in the untraced list. The untraced-figure list is a review prompt, not a failure: Article numbers, Act years and other static facts will appear there legitimately — a scheme outlay or a survey number should not. The year-to-excerpt and note-structure assertions apply to rows written from 2026-09-23 onwards; older daily CSVs carry a single excerpt and a prose note by design.

---

## Appendix A — `ca_pyq_build.py` (copy exactly)


```python
# -*- coding: utf-8 -*-
"""CA-PYQ Match Log builder (v6).

Usage:
  python3 ca_pyq_build.py --logs day1.csv day2.csv ... --today TODAY.json \
      --out-xlsx "CA-PYQ Match Log.xlsx" --out-day-csv today_upload.csv

--logs     = the per-day logs exported from Drive as CSV (11-column schema below; header row required;
             day-sheets whose ninth header still reads 'Representative PYQ (excerpt)' are accepted).
TODAY.json = list of objects: date, topic, source, gs_area, years, papers, pyq_excerpt, match,
             note, prelims [list of str], mains [list of str, each starting with a [Tag]].
             pyq_excerpt holds every matched question, one per line; note holds the three
             tagged lines [Prelims 2027] / [Mains 2027] / [Link].
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

HEAD = ['Date', 'GS Area', 'Match', 'CA Topic / Headline', 'Prelims Recall (CSE 2027)',
        'Mains Recall (CSE 2027)', 'PYQ Years (all occurrences)', 'Paper(s)',
        'PYQ Excerpts (all, Prelims + Mains)', 'Relevance & Revision Note', 'Source']
FONT, SZ = 'Calibri', 12
NAVY, SLATE = '1F3864', '44546A'
MATCH_FILL = {'Direct': 'C6EFCE', 'Thematic': 'FFF2CC', 'Emerging': 'E7E6E6'}
MATCH_INK = {'Direct': '145A32', 'Thematic': '7D6608', 'Emerging': '3B3838'}
BAND = ['FFFFFF', 'F2F6FB']
THIN = Side(style='thin', color='BFBFBF')
BOX = Border(left=THIN, right=THIN, top=THIN, bottom=THIN)
TOP = Alignment(vertical='top', wrap_text=True)
TOPC = Alignment(vertical='top', horizontal='center', wrap_text=True)

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
        hdr = r[0]
        old = [h.replace('Representative PYQ (excerpt)', 'PYQ Excerpts (all, Prelims + Mains)') for h in hdr]
        assert old[:len(HEAD)] == HEAD, f'Unexpected header in {log_path}: {hdr}'
        rows += [(x + [''] * 11)[:11] for x in r[1:] if x and x[0].strip()]
    if today_path:
        for o in json.load(open(today_path, encoding='utf-8')):
            rows.append([o['date'], o['gs_area'], o['match'], o['topic'], bullets(o['prelims']),
                         bullets(o['mains']), o['years'], o['papers'], o['pyq_excerpt'], o['note'], o['source']])
    seen, out = set(), []
    for x in rows:                                  # de-duplicate on date + topic start
        k = (x[0], x[3][:80])
        if k in seen:
            continue
        seen.add(k); out.append(x)
    order = {id(x): i for i, x in enumerate(out)}
    out.sort(key=lambda x: (x[0], -order[id(x)]), reverse=True)   # newest date first, original order within a date
    return out

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
            date, area, match, topic, pre, mai, yrs, pap, exc, note, src = x
            card = [
                (f'#{n}  ·  {match}', topic, 'head'),
                ('Area · Source', f'{area}   ·   {src}', 'meta'),
                ('PYQ years', f'{yrs}   —   {pap}', 'years'),
                ('Prelims recall', pre, 'pre'),
                ('Mains recall', mai, 'mains'),
                ('PYQ excerpts', exc, 'pyq'),
                ('Expected 2027 Qs', note, 'note'),
            ]
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
                elif kind == 'years':
                    b.value = val; b.font = F(bold=True, color=NAVY)
                elif kind == 'pyq':
                    b.value = val; b.font = F(italic=True, color='404040')
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
    widths = {'A': 12, 'B': 18, 'C': 11, 'D': 55, 'E': 55, 'F': 58, 'G': 22, 'H': 16, 'I': 62, 'J': 55, 'K': 18}
    for col, w in widths.items():
        wl.column_dimensions[col].width = w
    wl.append(HEAD)
    for c in wl[1]:
        c.font = F(bold=True, color='FFFFFF'); c.fill = fill(NAVY); c.border = BOX
        c.alignment = Alignment(vertical='center', horizontal='center', wrap_text=True)
    wl.row_dimensions[1].height = 36
    band = {d: BAND[i % 2] for i, d in enumerate(by_date)}
    prev = None
    for x in rows:
        wl.append(x[:5] + [None] + x[6:])
        i = wl.max_row
        wl.cell(i, 6).value = mains_rich(x[5])
        for j in range(1, 12):
            c = wl.cell(i, j)
            c.font = F(); c.alignment = TOP; c.border = BOX; c.fill = fill(band[x[0]])
        for j in (1, 2, 3, 7, 8):
            wl.cell(i, j).alignment = TOPC
        wl.cell(i, 7).font = F(bold=True, color=NAVY)
        wl.cell(i, 9).font = F(italic=True, color='404040')
        m = wl.cell(i, 3)
        if x[2] in MATCH_FILL:
            m.fill = fill(MATCH_FILL[x[2]]); m.font = F(bold=True, color=MATCH_INK[x[2]])
        if prev is not None and x[0] != prev:
            for j in range(1, 12):
                wl.cell(i, j).border = Border(left=THIN, right=THIN, bottom=THIN, top=Side(style='medium', color=NAVY))
        wl.cell(i, 1).font = F(bold=(x[0] != prev))
        prev = x[0]
        wl.row_dimensions[i].height = max(est_height(v, widths[chr(65 + k)]) for k, v in enumerate(x))
    wl.freeze_panes = 'D2'
    wl.auto_filter.ref = f'A1:K{wl.max_row}'
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

    # ---------- Sheet 4: How to Use ----------
    wh = wb.create_sheet('How to Use')
    guide = [
        ('What this is', ''),
        ('', "A running log matching each day's current affairs to every UPSC CSE PYQ year in which the same theme was asked (Prelims 2011-2026 and Mains GS1-GS4 2013-2026 from your GitHub PYQ corpus). Each item carries Prelims and Mains key points to recall for CSE 2027."),
        ('Tabs', ''),
        ('Revision Cards', 'Read-first view. One card per news item, newest day first; two columns so it reads on a phone without sideways scrolling.'),
        ('Master Log', 'The same data as a filterable table. Filter Match = Direct or a GS Area; sort by PYQ Years.'),
        ('PYQ Year Frequency', 'How many logged items link to each PYQ year, and how many of those are Direct.'),
        ('Card fields', ''),
        ('#n · Match', 'Direct = a PYQ asked this exact theme. Thematic = the item is a fresh example for a related PYQ. Emerging = not asked yet; high-probability for 2027.'),
        ('PYQ years', 'Every year the theme appeared, Prelims and Mains, with the papers.'),
        ('Prelims recall', 'Testable one-line facts: Acts and years, Articles, bodies, places, numbers.'),
        ('Mains recall', 'Answer-ready points, tagged [Intro data], [Issue], [Judgment], [Committee], [Way forward], [Counterpoint], [Ethics].'),
        ('PYQ excerpts', 'Every past question matched to the item, one line per year: P = Prelims with year, GS1-GS4 = Mains with year and marks. Four years asked means four quoted questions here.'),
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
        w.writerow(HEAD); w.writerows([[sheet_safe(v) for v in x] for x in rows])

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--logs', nargs='*', default=[]); ap.add_argument('--today')
    ap.add_argument('--out-xlsx', required=True); ap.add_argument('--out-day-csv')
    ap.add_argument('--monthly-dir', help='also write one workbook per month: <dir>/CA-PYQ Match Log YYYY-MM.xlsx')
    a = ap.parse_args()
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
        assert len(chk) == len(day) + 1 and all(len(x) == 11 for x in chk), 'CSV round-trip failed'
        print('today CSV:', a.out_day_csv, len(day), 'rows,', len(open(a.out_day_csv, encoding='utf-8').read()), 'chars')
    print('workbook rows:', len(rows), '| by date:', sorted(Counter(x[0] for x in rows).items(), reverse=True),
          '| match:', dict(Counter(x[2] for x in rows)))
```


## Appendix B — PYQ corpus helpers

The loader ships in the repo — do not write your own copy. After the I-4 clone run `python3 pyq/load_pyq.py pyq` once per session (plain `python3`, from the scratchpad, not from inside the clone). It writes `mains_recs.json` (`{paper, year, text, marks}`, plus `q` such as `Q3(b)` for `pyq_db` years; papers `GS1`…`GS4` and `Essay`) and `prelims_lines.txt` (old Prelims index lines plus `YYYY Qn: stem Options: …` for 2020 onwards). It reads every year from exactly one source and stops with an assertion if a year appears twice or a `pyq_db` paper is incomplete (Prelims must be Q1-Q100; each Mains GS paper 250 marks).

Expected output: `pyq_db` years 2020-2026 with GS1 20, GS2 20, GS3 20, GS4 19, Essay 8 each; `old index 2013-2019: 552`; full-paper Prelims stems `{'2020': 100, '2021': 100, '2022': 100, '2023': 100, '2024': 100, '2025': 100, '2026': 100}`. Numbers far below this mean the clone or parse failed — fix before matching.

I-6b fallback — split the latest workbook into day logs (then upload each restored day per O-4):

```python
import openpyxl, csv, collections, os
os.makedirs('logs', exist_ok=True)
ml = openpyxl.load_workbook('prev.xlsx')['Master Log']
hdr = [c.value for c in ml[1]]
by = collections.defaultdict(list)
for r in ml.iter_rows(min_row=2, values_only=True):
    if r[0]:
        d = str(r[0])[:10]
        by[d].append([d] + ['' if v is None else str(v) for v in r[1:]])
for d, rows in by.items():
    with open(f'logs/day_{d}.csv', 'w', newline='', encoding='utf-8') as f:
        w = csv.writer(f); w.writerow(hdr); w.writerows(rows)
```

Verify an uploaded CSV when the plain CSV export comes back inline (O-4): export as `application/zip`, then —

```python
import json, base64, zipfile, io, re, html, csv
c = json.load(open(SAVED_JSON))['content']               # path printed in the tool result
z = zipfile.ZipFile(io.BytesIO(base64.b64decode(c)))
s = z.read([n for n in z.namelist() if n.endswith('.html')][0]).decode('utf-8')
tbl = []
for r in re.findall(r'<tr[^>]*>(.*?)</tr>', s, re.S):
    cells = re.findall(r'<td[^>]*>(.*?)</td>', r, re.S)
    tbl.append([html.unescape(re.sub(r'<[^>]+>', '', re.sub(r'<br\s*/?>', '\n', x))).replace('\xa0', ' ').strip() for x in cells])
tbl = [r for r in tbl if any(r)]
loc = list(csv.reader(open(LOCAL_CSV, encoding='utf-8', newline='')))
norm = lambda t: re.sub(r'\s+', ' ', t).strip()
bad = [(i, j) for i, (x, y) in enumerate(zip(tbl, loc)) for j, (p, q) in enumerate(zip(x[-len(y):], y)) if norm(p) != norm(q)]
assert len(tbl) == len(loc) and not bad, (len(tbl), len(loc), bad[:5])
```

Search helper `q.py` — `python3 q.py "label::regex" ...` (append `!` to the label for case-sensitive). Keep the printed hits: **every** hit you accept becomes its own quoted line in `pyq_excerpt`, so run the search wide enough to catch all years before deciding.

```python
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
    for r in recs:
        if rx.search(r['text']):
            print(f"  M {r['year']} {r['paper']} [{r['marks']}]: {r['text'][:150]}")
    seen = set()
    for l in plines:
        y = yr(l)
        if y and rx.search(l) and l[:80] not in seen:
            seen.add(l[:80]); print(f'  P {y}: {l[:150]}')
```

Read every hit before counting a year; regex hits are candidates, not matches. Quote every hit you keep — a year in `PYQ Years` with no quoted line, or fewer quoted lines than listed years, is a bug the VERIFY step catches.

Run-time notes from practice: run the scripts you write yourself with plain `python3` (not `-I`, which drops the script directory from the import path); use `-I` only for scripts that read downloaded data. Drive uploads always convert CSV to a Google Sheet.