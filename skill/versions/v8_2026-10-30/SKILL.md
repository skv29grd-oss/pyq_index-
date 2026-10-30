# Daily CA → PYQ Match (UPSC CSE 2027) — full instructions

Version: **v8** (2026-10-30; rules marked v8 apply to newspaper dates from 31 Oct 2026). Current version number lives in `skill/VERSION`; history in `skill/CHANGELOG.md`; every earlier version in `skill/versions/`.

Triggered manually by the user ("run today's match", "run it up to today", a newspaper PDF upload, or the skill name). Never schedule it.

## 0. Skill files and versioning (read first)

| File | Role |
|---|---|
| `skill/SKILL.md` | These instructions — the single source of truth |
| `skill/ca_pyq_build.py` | Workbook + day-CSV builder (locked design). Run it from the clone; never retype it |
| `skill/verify.py` | VERIFY step |
| `skill/q.py` | PYQ regex search helper |
| `skill/syllabus.md` | Official syllabus lines (Paper \| Subject \| Topic) used for the Syllabus Tag |
| `load_pyq.py` (repo root) | Loads the PYQ corpus |
| `skill/VERSION` | Current version number, e.g. `7` |
| `skill/CHANGELOG.md` | One entry per version: number, date, what changed and why |
| `skill/versions/v<N>_<YYYY-MM-DD>/` | Frozen copy of version N's files, dated the day it was archived (i.e. replaced) |

**Versioning rule (mandatory, every change to anything in `skill/`):**
1. Read `skill/VERSION` → N. Today's date → D (Asia/Calcutta).
2. Copy **all** current files of the skill (`SKILL.md`, `ca_pyq_build.py`, `verify.py`, `q.py`, plus any other file in `skill/` except `versions/`) into `skill/versions/v<N>_<D>/` unchanged. If that folder already exists (second change on the same day), use `v<N>_<D>_b`, `_c`, ….
3. Commit that archive on its own: `Archive skill v<N> (<D>) before update`.
4. Make the change, write N+1 into `skill/VERSION`, update the `Version:` line at the top of this file, and add a CHANGELOG entry (`## v<N+1> — <D>` + bullets).
5. Commit `Skill v<N+1>: <summary>` and push. Never edit or delete anything inside `skill/versions/`.
6. Only the user decides a change to the skill; tell them the new version number and what changed.

The pointer skill in the user's Claude settings stays short and does not change between versions.

## At a glance

| Stage | What happens |
|---|---|
| 1. Inputs | Paper (Drive) · Next IAS + Drishti + Vajiram & Ravi (web) · PYQ corpus and monthly data CSV (GitHub) · gap check |
| 2. Processing | Extract → **select ≤15 newspaper + ≤5 web items** → match all PYQ years → classify → recall → expected 2027 Qs → Syllabus Tag → V&R recall (CA + syllabus base) |
| 3. Output | Build monthly workbook (13-column locked design) → send it → push day rows to the GitHub CSV → verify |
| 4. Reply | 5-8 lines: rows per date, top Direct hits, new Emerging themes, each site's latest date, caveats |

Run checklist (tick every box before replying):

- [ ] Repo `skv29grd-oss/pyq_index-` attached with **push** access (`add_repo`, access `push`), cloned to `/home/claude/pyq_index-`; `load_pyq.py` prints the expected counts (§5)
- [ ] Gap check against `data/CA-PYQ Data YYYY-MM.csv`: every date from the last logged date to today with a paper on Drive is run, oldest first (I-6)
- [ ] Every page of each paper read (state page count)
- [ ] Next IAS, Drishti IAS and Vajiram & Ravi (Prelims + Mains pages) pulled for each date, or reason stated; latest posted date per site noted
- [ ] At most 15 newspaper rows + 5 web-only rows per date (P-0)
- [ ] Every row: all PYQ years, **one quoted question per year listed**, Match class, 3-5 Prelims + 3-4 Mains recall, three MECE note lines, a Syllabus Tag from `syllabus.md`, a `vr` field; newspaper rows also a `vr_topic` (same tag → identical block)
- [ ] Every figure, name and quote traceable to source text (P-5.5)
- [ ] Workbook built with `skill/ca_pyq_build.py`; `skill/verify.py` prints OK for every date run; current month's file sent
- [ ] Day rows appended to the GitHub monthly CSV (13 columns, CRLF row endings), committed, pushed, re-fetched and row-counted

---

## 1. INPUTS

| # | Input | Where | How to read it |
|---|---|---|---|
| I-1 | Newspaper (The Hindu Delhi; occasionally Indian Express) | Chat upload, or Drive `UPSC Prep/Daily Newspaper/` (folder id `1CtfjQaFlINJX_ztcrwYXmju-cHTgZq2R`). Names vary (`TH Delhi DD-MM-YYYY.pdf`, `TH-Delhi DD.MM.YYYY.pdf`, `The Hindu DD.MM.YYYY.pdf`, `IE-Delhi …`): search `parentId = '<folder>' and createdTime > '<date>'` | Upload: `Read` with `pages`. Drive PDF ≤10 MB: `download_file_content`. >10 MB: `read_file_content` (saved to a file → `fileContent`). Clean (drop lines ≤25 chars), read in ~37k-char slices; after every page is scanned, a headline pass plus `find()` on chosen stories is fine |
| I-2 | Next IAS | `nextias.com/ca/current-affairs/DD-MM-YYYY`; articles `…/DD-MM-YYYY/<slug>`; short items `…/news-in-brief-DD-MM-YYYY` | WebFetch index, then article pages for figures |
| I-3 | Drishti IAS | `drishtiias.com/current-affairs-news-analysis-editorials/news-analysis/DD-MM-YYYY` | Same |
| I-3b | Vajiram & Ravi | Prelims `vajiramandravi.com/current-affairs/upsc-prelims-current-affairs/YYYY/MM/DD/` · Mains `vajiramandravi.com/current-affairs/upsc-mains-current-affairs/YYYY/MM/DD/` | WebFetch each index for titles + URLs, then each article with a short facts-only prompt (exact figures). Use (a) for V&R recall (P-7) on rows of the same story; (b) V&R-only items with a syllabus hook become rows, Source `V&R (DD-MM-YYYY)`. Leave out facts that look like V&R typos |
| I-4 | PYQ corpus | `pyq_db/<year>/<year> <paper>.csv` (2020-2026); old indexes for Prelims 2011-2019, Mains 2013-2019 | `python3 pyq_index-/load_pyq.py pyq_index-` from `/home/claude`. Never download PYQ files from Drive. If GitHub is unreachable, stop and tell the user |
| I-6 | Past daily data | `data/CA-PYQ Data YYYY-MM.csv` in the repo (12 columns, header, CRLF row endings, LF inside quoted cells) | `git fetch origin main && git reset --hard origin/main` first. Count rows per Date. **Gap check:** every date from the last logged date up to today that has a paper on Drive is run this session, oldest first, each as its own date. The old Drive CSV store is retired |
| I-6b | Fallback if the CSV lacks days the user ran | Latest `CA-PYQ Match Log YYYY-MM.xlsx` (chat or Drive) | Split its Master Log by Date (§5) and append the missing dates in the same push |

**Site dates.** All three sites post late; today's page is often empty. Find each site's latest posted date and pull every date from the last logged date to that one. Web items dated D go into date D's rows (merged with that day's newspaper rows for the same story) — never under a later newspaper date. Only if date D gets no newspaper run do they go under the nearest run date, with the web date in `Source` (`Next IAS (29-10-2026)`).

PYQ coverage: 2020-2026 full papers in `pyq_db/`; 2013-2019 Mains from topic indexes (GS4 case studies index-only → `[partial]`; no Essay before 2020); Prelims 2011-2019 topic-wise, incomplete. A new year goes into `pyq_db/<year>/` as six CSVs and is removed from the old indexes in the same commit (`YRS_OLD` in `load_pyq.py` narrowed).

Oversized tool results are saved to files: decode with Python, never paste into context.

## 2. PROCESSING

**P-1 Extract.** Read every page. Keep items with a syllabus hook (polity, governance, IR, economy, environment, S&T, security, society, disaster management, art & culture, Prelims-able sports/awards/places). Skip city crime, obituaries, classifieds, puzzles, club sport. 20-35 items a day. Capture a self-contained topic sentence with quotable figures and the page; write `The Hindu (Science)` etc. when the page number is not certain — never guess a page.

**P-0 Select (v8).** After extracting candidates, keep **at most 15 newspaper items and at most 5 web-only items** (combined across Drishti, Next IAS and V&R) per date. Web facts merged into a newspaper row do not count toward the 5. Rank by: (1) Direct > Thematic > Emerging; (2) more PYQ years; (3) value for both Prelims and Mains; (4) syllabus spread — prefer an item on an uncovered subtopic over a second item on a covered one; web items fill subtopics the paper missed. Report the number of candidates dropped in the reply.

**P-2 Merge.** One row per theme per date; merge same-date web coverage. A continuation of an earlier day is a new row with "refines the DD Mon entry" in `[Link]`.

**P-3 Match all PYQ years.** 2-4 precise patterns per item with `skill/q.py` (copy it next to `mains_recs.json`; label ending `!` = case-sensitive). Read every hit; keep genuine matches. List every year ascending with papers. Quote every match in `pyq_excerpt`, one per line, ascending (`P <year>:` / `GS<n> <year> (<marks>):`), cap eight then `+N more`. **One year → one quoted question**; same year in two papers → two lines; never summarise. Full text: filter `mains_recs.json` by year/paper/substring; `prelims_lines.txt` by its key (`Env Q59 (2016)`, `2022 Q44:`).

**P-4 Classify.** Direct = PYQ asked this exact theme/place/fact · Thematic = fresh example for a related PYQ · Emerging = not asked yet.

**P-5 CSE 2027 recall.** Prelims 3-5 facts, ≤22 words each. Mains 3-4 points, ≤25 words, each starting with `[Intro data]` `[Issue]` `[Judgment]` `[Committee]` `[Way forward]` `[Counterpoint]` or `[Ethics]`; at least one `[Way forward]`/`[Counterpoint]`. Source facts or certain static facts only; no repeats across lists.

**P-5.5 Source fidelity.** Figures exactly as printed (units, lakh/crore form, ranges). Names with year/ministry/designation. ≤1 quote per row, ≤15 words, verbatim, attributed. Topic ≤45 words. No filler. Unverifiable → leave out.

**P-6 Note — three MECE lines:** `[Prelims 2027] <MCQ stem>` / `[Mains 2027] <question> (GSn, marks)` / `[Link] <PYQ years; entry refined>`. Prelims and Mains test different buckets (Prelims: statutory basis/body · provision · place · number/threshold · status; Mains: causes · impacts · institutional design · ethics · way forward · comparison). ≤35 words each. Emerging: `[Link] first appearance — no PYQ yet`.

**P-8 Syllabus Tag (v8).** Every row gets `tag` = `Paper › Subject › Topic › Subtopic` (separator ` › `). Paper, Subject and Topic are copied exactly from one line of `skill/syllabus.md`; Subtopic is the specific concept, law or institution (short, e.g. `Air pollution — GRAP, CAQM`). Use the Mains paper when the item has Mains value; `Prelims` only for Prelims-only facts. Items on the same subtopic get the identical tag; before inventing a subtopic, check the month's CSV for an existing tag on the same theme and reuse it.

**P-7 V&R recall (column 13).** Two blocks in one cell. **[CA]** If V&R covered the same story that date (Prelims or Mains page): 2-4 facts, ≤25 words each, from the V&R article, preferring what the paper and other sites lack (outlay, components, legal section, origin year, mechanism); figures as V&R prints them. Not covered → `vr: []` (builder writes `Not covered by V&R (DD-MM-YYYY)`). V&R not yet posted for that date → `vr: "V&R has not posted DD-MM-YYYY yet"`. Never borrow an article on a different story. Rows before 29 Oct 2026 keep the column blank unless the user asks for a backfill.

**[Syllabus base] (v8, newspaper rows only).** For each distinct tag on a newspaper row, find V&R's page on that exact syllabus subtopic: `WebSearch` with `allowed_domains: ["vajiramandravi.com"]` and the subtopic words; prefer `vajiramandravi.com/upsc-exam/<topic>/` pages, else a V&R explainer on the same subtopic. Fetch it with a facts-only prompt and write `vr_topic = {"page": "<page title>", "facts": [2-4 lines, ≤25 words each]}` — core static knowledge (law + year, body, constitutional provision, concept, standard, key data) not already in the row's Prelims/Mains recall. Keep only current figures; if the page shows a superseded target, give the current one and mark the old one `(earlier target)`. Never borrow a page on a different subtopic; if none exists, `vr_topic = {"page": "", "facts": []}` (builder writes `No V&R topic page found`). **Same tag → identical `vr_topic`** within the day; if the month's CSV already has a `[Syllabus base – <same subtopic>]` block, reuse it word for word. Web-only rows carry no `vr_topic`.

Write each date's rows to `today_YYYY-MM-DD.json`: list of objects with `date, topic, source, gs_area, tag, years, papers, pyq_excerpt, match, note, prelims, mains, vr` and, for newspaper rows, `vr_topic`. A `rowsYYYYMMDD.py` with an `R(...)` helper, dumped to JSON, keeps rows consistent. Save all source text used (paper, Next IAS, Drishti, V&R facts) into one `source_<dates>.txt` for VERIFY.

## 3. OUTPUT

**O-1 Schema** (13 columns, fixed order — GitHub CSV and Master Log):
`Date | GS Area | Syllabus Tag | Match | CA Topic / Headline | Prelims Recall (CSE 2027) | Mains Recall (CSE 2027) | PYQ Years (all occurrences) | Paper(s) | PYQ Excerpts (all, Prelims + Mains) | Relevance & Revision Note | Source | V&R Recall (Vajiram & Ravi)`
The builder reads older 11- and 12-column CSVs by header name.
`Date` = newspaper date (web date for web-only rows), never the run date.

**O-2 Build** (from `/home/claude`; copy the CSV to scratch first, oldest date first):

```
cp "pyq_index-/data/CA-PYQ Data YYYY-MM.csv" gh/base.csv
python3 pyq_index-/skill/ca_pyq_build.py --logs gh/base.csv --today today_D1.json --out-xlsx master/tmp.xlsx --out-day-csv upload_D1.csv
python3 pyq_index-/skill/ca_pyq_build.py --logs gh/base.csv upload_D1.csv --today today_D2.json \
  --out-xlsx "master/CA-PYQ Match Log.xlsx" --out-day-csv upload_D2.csv --monthly-dir /mnt/user-data/outputs
```

Four tabs, all Calibri 12: Revision Cards (phone-first, newest day first; V&R recall line when present) · Master Log · PYQ Year Frequency · How to Use. `--monthly-dir` writes `CA-PYQ Match Log YYYY-MM.xlsx` per month; that file is the only workbook the user reads.

**O-2a Design lock** — `skill/ca_pyq_build.py` is the source of truth; change script, `verify.py` and this table together (as a new version, §0).

| Element | Fixed value |
|---|---|
| Typeface | Calibri 12 everywhere; emphasis by weight, colour, fill |
| Palette | Navy `1F3864` · slate `44546A` · blue `2E75B6` · grey `404040` italic excerpts |
| Match colours | Direct `C6EFCE`/`145A32` · Thematic `FFF2CC`/`7D6608` · Emerging `E7E6E6`/`3B3838` |
| Date banding | `FFFFFF`/`F2F6FB`; medium navy top border on new date; bold date cell |
| Revision Cards | Columns 20/100; gridlines off; navy day banner (26) with match counts; card lines: headline · Area·Source · Syllabus (bold slate, when present) · PYQ years · Prelims recall (`F4F9F1`) · Mains recall (bold tags) · PYQ excerpts (italic) · Expected 2027 Qs · V&R recall (`FFF7E6`, when present) |
| Master Log | Widths `A:12 B:18 C:34 D:11 E:55 F:55 G:58 H:22 I:16 J:62 K:55 L:18 M:60`; Syllabus Tag in bold slate; header 36; freeze `E2`; autofilter `A1:M<last>`; landscape; header repeats |
| Row heights | `est_height()` — never Excel autofit |
| Tabs | Revision Cards `1F3864` → Master Log `2E75B6` → PYQ Year Frequency `44546A` → How to Use `A6A6A6` |

**O-3 Deliver.** `SendUserFile` the current month's workbook (attach, one-line caption).

**O-4 Store on GitHub.** In the clone: fetch + hard reset to `origin/main`; read the month's CSV with `csv`; if its header lacks `Syllabus Tag`, insert that column (blank for old rows) after `GS Area`; assert none of the new dates exist; append rows from each `upload_YYYY-MM-DD.csv` (skip header) in date order, values unchanged; write with `csv.writer` (CRLF). New month → new `data/CA-PYQ Data YYYY-MM.csv` with the 13-column header. Commit `Add CA-PYQ rows for DD Mon YYYY (N)` with the session attribution lines; `git push origin HEAD:main`. Verify: fetch, `origin/main` is your commit, CSV rows = monthly workbook Master Log rows, all rows 13 fields. Never use a subagent to retype the CSV. Tell the user the Drive copy of the workbook is now theirs to replace.

**O-5 Reply** (concise): rows per date (newspaper/web) and match mix; candidates dropped by the cap; 3-5 top Direct items with PYQ years; new Emerging themes; each site's latest date; inputs not read; caveats.

## 4. VERIFY

For every date added: `python3 pyq_index-/skill/verify.py today_YYYY-MM-DD.json upload_YYYY-MM-DD.csv source_<dates>.txt` → fix until it prints `OK`. From 31 Oct 2026 it also checks the 15 + 5 cap, every tag against `syllabus.md`, the syllabus block on newspaper rows only, and identical blocks for identical tags. The untraced-figure list is a review prompt (Act years and Articles are fine; an unsourced outlay is not).

## 5. Corpus helpers

`load_pyq.py` expected output: `pyq_db` 2020-2026 with GS1 20, GS2 20, GS3 20, GS4 19, Essay 8 each; `old index 2013-2019: 552`; Prelims stems 100 for each of 2020-2026.

I-6b split of a workbook into day CSVs:

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

Run your own scripts with plain `python3`; `-I` only for scripts that read downloaded data.
