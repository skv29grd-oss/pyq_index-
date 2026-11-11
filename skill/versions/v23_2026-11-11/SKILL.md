# Daily CA → PYQ Match (UPSC CSE 2027) — full instructions

Version: **v18** (2026-11-06; rules marked v8/v9 apply from 31 Oct 2026, v10 from 1 Nov 2026; v11-v17 = corpus coverage updates; v18 = GS Area derived from the Syllabus Tag, corpus coverage moved out of the skill; v19 = PYQ IDs instead of question text from 4 Nov 2026; v20 = V&R syllabus content pool, rows pick facts by ID; v21 = V&R block is fixed syllabus theory only, never news; v22 = Topic Register, weekly High-Probability list, Emerging reserve; v23 = V&R block always carries a link). Current version number lives in `skill/VERSION`; history in `skill/CHANGELOG.md`; every earlier version in `skill/versions/`.

Triggered manually by the user ("run today's match", "run it up to today", a newspaper PDF upload, or the skill name). Never schedule it.

## 0. Skill files and versioning (read first)

| File | Role |
|---|---|
| `skill/SKILL.md` | These instructions — the single source of truth |
| `skill/ca_pyq_build.py` | Workbook + day-CSV builder (locked design). Run it from the clone; never retype it |
| `skill/verify.py` | VERIFY step |
| `skill/q.py` | PYQ regex search helper (prints PYQ IDs) |
| `skill/vr_pool.py` | V&R content pool: `status`, `add` (pool build, §6), `find` (facts for a day's rows, P-7), `show` |
| `skill/vr_cache.py` | v19 legacy: V&R block cache for reruns of 31 Oct-3 Nov 2026 only |
| `skill/syllabus.md` | Official syllabus lines (Paper \| Subject \| Topic) used for the Syllabus Tag |
| `load_pyq.py` (repo root) | Loads the PYQ corpus |
| `README.md` (repo root) | PYQ corpus coverage and the expected `load_pyq.py` output — the single source for both (not a skill file) |
| `CORPUS_CHANGELOG.md` (repo root) | One entry per PYQ corpus change (not a skill file) |
| `data/vr_pool.json` | V&R syllabus content pool: pages per syllabus line, each as 4-12 facts in Claude's words with title + URL (data, not a skill file: adding pages needs no version bump) |
| `data/vr_topics.json` | v19 legacy cache (31 Oct-3 Nov 2026 rows); not used from 4 Nov 2026 |
| `skill/VERSION` | Current version number, e.g. `7` |
| `skill/CHANGELOG.md` | One entry per version: number, date, what changed and why |
| `skill/versions/v<N>_<YYYY-MM-DD>/` | Frozen copy of version N's files, dated the day it was archived (i.e. replaced) |

**Corpus changes are not skill changes (v18).** Adding or correcting PYQ years (`pyq_db/`, old `*_Index.txt` files, `load_pyq.py`) changes no file in `skill/`. In the same commit, update the coverage table and expected counts in `README.md` and add an entry to `CORPUS_CHANGELOG.md`. Do not archive the skill or bump `skill/VERSION` for a corpus change.

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
| 2. Processing | Extract → **select ≤15 newspaper + ≤5 web items, 3-4 reserved for Emerging** → match all PYQ years → classify → recall → expected 2027 Qs → Syllabus Tag → V&R syllabus base (pool facts by ID) |
| 3. Output | Build monthly workbook (13-column locked design) → send it → push day rows to the GitHub CSV → verify |
| 4. Reply | 5-8 lines: rows per date, top Direct hits, new Emerging themes, each site's latest date, caveats |

Run checklist (tick every box before replying):

- [ ] Repo `skv29grd-oss/pyq_index-` attached with **push** access (`add_repo`, access `push`), cloned to `/home/claude/pyq_index-`; `load_pyq.py` prints the expected counts in `README.md` (§5)
- [ ] Gap check against `data/CA-PYQ Data YYYY-MM.csv`: every date from the last logged date to today with a paper on Drive is run, oldest first (I-6)
- [ ] Every page of each paper read (state page count)
- [ ] Next IAS, Drishti IAS and Vajiram & Ravi (Prelims + Mains pages) pulled for each date, or reason stated; latest posted date per site noted
- [ ] At most 15 newspaper rows + 5 web-only rows per date, of which at least 3 (aim 4) Emerging (P-0)
- [ ] Every row: `pyq_ids` — one PYQ ID per matched question, every year (v19; no question text, no years/papers fields), Match class, 3-5 Prelims + 3-4 Mains recall, three MECE note lines, a Syllabus Tag from `syllabus.md`; V&R daily facts merged into recall; newspaper rows 2-4 enriching `vr_facts` from the V&R pool via `vr_pool.py find` (P-7)
- [ ] Every figure, name and quote traceable to source text (P-5.5)
- [ ] Workbook built with `skill/ca_pyq_build.py`; `skill/verify.py` prints OK for every date run; current month's file sent
- [ ] Day rows appended to the GitHub monthly CSV (13 columns, CRLF row endings) and `data/vr_pool.json` if pages were added, in one commit; pushed, re-fetched and row-counted

---

## 1. INPUTS

| # | Input | Where | How to read it |
|---|---|---|---|
| I-1 | Newspaper (The Hindu Delhi; occasionally Indian Express) | Chat upload, or Drive `UPSC Prep/Daily Newspaper/` (folder id `1CtfjQaFlINJX_ztcrwYXmju-cHTgZq2R`). Names vary (`TH Delhi DD-MM-YYYY.pdf`, `TH-Delhi DD.MM.YYYY.pdf`, `The Hindu DD.MM.YYYY.pdf`, `IE-Delhi …`): search `parentId = '<folder>' and createdTime > '<date>'` | Upload: `Read` with `pages`. Drive PDF ≤10 MB: `download_file_content`. >10 MB: `read_file_content` (saved to a file → `fileContent`). Clean (drop lines ≤25 chars), read in ~37k-char slices; after every page is scanned, a headline pass plus `find()` on chosen stories is fine |
| I-2 | Next IAS | `nextias.com/ca/current-affairs/DD-MM-YYYY`; articles `…/DD-MM-YYYY/<slug>`; short items `…/news-in-brief-DD-MM-YYYY` | WebFetch index, then article pages for figures |
| I-3 | Drishti IAS | `drishtiias.com/current-affairs-news-analysis-editorials/news-analysis/DD-MM-YYYY` | Same |
| I-3b | Vajiram & Ravi (daily) | Prelims `vajiramandravi.com/current-affairs/upsc-prelims-current-affairs/YYYY/MM/DD/` · Mains `vajiramandravi.com/current-affairs/upsc-mains-current-affairs/YYYY/MM/DD/` | WebFetch each index for titles + URLs, then each article with a short facts-only prompt (exact figures). Use (a) to enrich rows of the same story, merged into topic and recall like Next IAS/Drishti (P-7); (b) V&R-only items with a syllabus hook become rows, Source `V&R (DD-MM-YYYY)`. Leave out facts that look like V&R typos |
| I-4 | PYQ corpus | `pyq_db/<year>/<year> <paper>.csv` and the old topic indexes; years per source in `README.md` | `python3 pyq_index-/load_pyq.py pyq_index-` from `/home/claude`; writes `mains_recs.json`, `prelims_lines.txt` and `pyq_bank.json` (every question by PYQ ID) there. Never download PYQ files from Drive. If GitHub is unreachable, stop and tell the user |
| I-6 | Past daily data | `data/CA-PYQ Data YYYY-MM.csv` in the repo (13 columns, O-1 order, header, CRLF row endings, LF inside quoted cells) | `git fetch origin main && git reset --hard origin/main` first. Count rows per Date. **Gap check:** every date from the last logged date up to today that has a paper on Drive is run this session, oldest first, each as its own date. The old Drive CSV store is retired |
| I-6b | Fallback if the CSV lacks days the user ran | Latest `CA-PYQ Match Log YYYY-MM.xlsx` (chat or Drive) | Split its Master Log by Date (§5) and append the missing dates in the same push |

**Site dates.** All three sites post late; today's page is often empty. Find each site's latest posted date and pull every date from the last logged date to that one. Web items dated D go into date D's rows (merged with that day's newspaper rows for the same story) — never under a later newspaper date. Only if date D gets no newspaper run do they go under the nearest run date, with the web date in `Source` (`Next IAS (29-10-2026)`).

PYQ coverage: see the table in `README.md` (single source; do not copy year ranges into this file). Any year read from an old topic index (not from `pyq_db/`) is topic-wise and may be incomplete; say so in the reply when a match relies on it. A new year goes into `pyq_db/<year>/` as six CSVs (or paper by paper) and is removed from the old indexes in the same commit (`YRS_OLD` in `load_pyq.py` is per Mains paper); this is a corpus change (§0).

Oversized tool results are saved to files: decode with Python, never paste into context.

## 2. PROCESSING

**P-1 Extract.** Read every page. Keep items with a syllabus hook (polity, governance, IR, economy, environment, S&T, security, society, disaster management, art & culture, Prelims-able sports/awards/places). Skip city crime, obituaries, classifieds, puzzles, club sport. 20-35 items a day. Capture a self-contained topic sentence with quotable figures and the page; write `The Hindu (Science)` etc. when the page number is not certain — never guess a page.

**P-0 Select (v8).** After extracting candidates, keep **at most 15 newspaper items and at most 5 web-only items** (combined across Drishti, Next IAS and V&R) per date. Web facts merged into a newspaper row do not count toward the 5. **Emerging reserve (v22):** first fill 3-4 of the 20 slots (newspaper or web) with the best Emerging candidates (no PYQ yet, clear syllabus hook, likely examinable: new law, institution, scheme, technology, place, index); rank them by Prelims + Mains value and syllabus spread. Then fill the remaining slots by: (1) Direct > Thematic > Emerging; (2) more PYQ years; (3) value for both Prelims and Mains; (4) syllabus spread — prefer an item on an uncovered subtopic over a second item on a covered one; web items fill subtopics the paper missed. Never relabel a Thematic item as Emerging to fill the reserve. If the day has fewer than 3 genuine Emerging candidates, keep what exists and set `"emerging_short": "<reason>"` on one row (verify requires it). Report candidates dropped and the Emerging count in the reply.

**P-2 Merge.** One row per theme per date; merge same-date web coverage. A continuation of an earlier day is a new row with "refines the DD Mon entry" in `[Link]`.

**P-3 Match all PYQ years (v19: IDs, not text).** 2-4 precise patterns per item with `python3 pyq_index-/skill/q.py 'label::regex' …` from `/home/claude` (label ending `!` = case-sensitive). Each hit starts with its PYQ ID (`P2021-001`, `M2021-GS3-07`, `M2026-GS4-03b`, `E2026-A1`; old-index Prelims 2011-2012 `P2012-MoH-Q13`). Read every hit; keep genuine matches. Put their IDs in `pyq_ids` (list). **One year → one PYQ per paper**; same year in two papers → two IDs. Never write question text, `years`, `papers` or `pyq_excerpt` for rows from 4 Nov 2026: the builder sorts the IDs (year, then Prelims, GS1-GS4, Essay), derives PYQ Years and Paper(s) from them, stores the IDs in the CSV and prints the full corpus text in the workbook (v10 full-text rule still holds there, and later corpus corrections reach old rows automatically). Emerging with no match: `pyq_ids: []` (shown as `No PYQ match in corpus`). Full text of an ID for reading: `pyq_bank.json`. Rows before 4 Nov 2026 keep their stored full text.

**P-4 Classify.** Direct = PYQ asked this exact theme/place/fact · Thematic = fresh example for a related PYQ · Emerging = not asked yet.

**P-5 CSE 2027 recall.** Prelims 3-5 facts, ≤22 words each. Mains 3-4 points, ≤25 words, each starting with `[Intro data]` `[Issue]` `[Judgment]` `[Committee]` `[Way forward]` `[Counterpoint]` or `[Ethics]`; at least one `[Way forward]`/`[Counterpoint]`. Source facts or certain static facts only; no repeats across lists.

**P-5.5 Source fidelity.** Figures exactly as printed (units, lakh/crore form, ranges). Names with year/ministry/designation. ≤1 quote per row, ≤15 words, verbatim, attributed. Topic ≤45 words. No filler. Unverifiable → leave out.

**P-6 Note — three MECE lines:** `[Prelims 2027] <MCQ stem>` / `[Mains 2027] <question> (GSn, marks)` / `[Link] <PYQ years; entry refined>`. Prelims and Mains test different buckets (Prelims: statutory basis/body · provision · place · number/threshold · status; Mains: causes · impacts · institutional design · ethics · way forward · comparison). ≤35 words each. Emerging: `[Link] first appearance — no PYQ yet`.

**P-8 Syllabus Tag (v8).** Every row gets `tag` = `Paper › Subject › Topic › Subtopic` (separator ` › `). Paper, Subject and Topic are copied exactly from one line of `skill/syllabus.md`; Subtopic is the specific concept, law or institution (short, e.g. `Air pollution — GRAP, CAQM`). Use the Mains paper when the item has Mains value; `Prelims` only for Prelims-only facts. Items on the same subtopic get the identical tag; before inventing a subtopic, check the month's CSV for an existing tag on the same theme and reuse it.

**P-8a GS Area (v18).** `gs_area` is derived from the tag, never typed freely: `<Paper> <Subject>` exactly as in the tag (e.g. `GS2 International Relations`, `GS3 Science & Technology`, `Prelims Environment`); for `Essay › Essay › …` it is `Essay`. No abbreviations (`IR`, `S&T`), no second paper, no subtopic. The allowed values are therefore exactly the Paper + Subject pairs in `skill/syllabus.md`. Rows dated before 31 Oct 2026 have no tag and keep their old free-text GS Area.

**P-7 V&R (v9).** Vajiram & Ravi is used in two separate ways.
- **Daily news facts → the row itself.** Treat V&R's daily Prelims/Mains articles exactly like Next IAS and Drishti: merge their facts on the same story into the row's topic sentence and Prelims/Mains recall (within the usual counts and word limits; replace weaker points rather than exceed them), and add `V&R (DD-MM-YYYY)` to `Source`. V&R-only stories can be rows, counting toward the 5 web items (P-0). No `vr` field from 31 Oct 2026.
- **Syllabus base → column 13 (`V&R Recall`).** Only this goes in the column, as below.

Rows of 29-30 Oct 2026 were written before v9 and keep V&R daily facts in column 13.

**Syllabus base (v20 pool; v21 fixed theory only; newspaper rows only; the only content of column 13).** Column 13 is the fixed syllabus theory of the row's topic and subtopic that the user must remember in the exam, not the news. No V&R page is fetched during a daily run unless the pool lacks the subtopic:
1. `python3 pyq_index-/skill/vr_pool.py find today_YYYY-MM-DD.json` lists, for each newspaper row's tag, the pool pages on the same syllabus line or sharing a subtopic keyword, with every fact numbered by ID (`V0002.5`). Facts marked `~` are already in the row's recall.
2. Pick 2-4 facts of **fixed syllabus theory** on the row's syllabus topic and subtopic: what the examiner expects you to know about that subtopic whatever the news is (constitutional Articles, Acts and sections, institutions and their composition and powers, concepts and classifications, landmark judgments, committees). Never news details (the event, its phases, latest figures, the ruling or controversy in the news); the row's topic and recall carry those. Skip facts marked `~` and facts the row already states. Write their IDs as `vr_facts` (e.g. news on SIR → GS2 › Polity › Salient features of the Representation of People's Act › Electoral rolls — SIR → `["V0006.1", "V0001.4", "V0001.6"]`: Article 324(1), voter qualification, CEO/DEO/ERO roles). Same tag on the same date → identical `vr_facts`.
3. MISSING (no relevant page) → search V&R once for the subtopic's theory page (`WebSearch`, `allowed_domains: ["vajiramandravi.com"]`), write the relevant pages as a pool batch for the row's syllabus line (§6 rules) and `vr_pool.py add` it, then pick. Only if V&R has nothing on it: `vr_facts: []` (column 13 says so); count these in the reply.
The builder renders column 13 from the pool: `[Syllabus base – <Subtopic>] (V&R: <page titles>)` + the facts + `V&R link: <page URL(s)>` (v23). With `vr_facts: []` it writes `Not in the V&R pool yet. Find it on V&R: <web search link restricted to vajiramandravi.com for the subtopic>`, so every newspaper row has a clickable V&R link (hyperlinked in Revision Cards and Master Log column M). Web-only rows carry no `vr_facts`, so their column 13 is blank. Rows of 31 Oct-3 Nov 2026 used `vr_topic` + `data/vr_topics.json` (v19, `vr_cache.py`), kept only for reruns of those dates.

Write each date's rows to `today_YYYY-MM-DD.json`: list of objects with `date, topic, source, gs_area` (P-8a)`, tag, pyq_ids` (P-3)`, match, note, prelims, mains` and, for newspaper rows, `vr_facts` (P-7; no `vr` field from 31 Oct 2026; no `years`, `papers`, `pyq_excerpt` or `vr_topic` from 4 Nov 2026). A `rowsYYYYMMDD.py` with an `R(...)` helper, dumped to JSON, keeps rows consistent. Save all source text used (paper, Next IAS, Drishti, V&R facts) into one `source_<dates>.txt` for VERIFY.

## 3. OUTPUT

**O-1 Schema** (13 columns, fixed order — GitHub CSV and Master Log):
`Date | GS Area | Syllabus Tag | Match | CA Topic / Headline | Prelims Recall (CSE 2027) | Mains Recall (CSE 2027) | PYQ Years (all occurrences) | Paper(s) | PYQ Excerpts (all, Prelims + Mains) | Relevance & Revision Note | Source | V&R Recall (Vajiram & Ravi)`
The builder reads older 11- and 12-column CSVs by header name.
From 4 Nov 2026 (v19) `PYQ Excerpts` holds PYQ IDs, one per line (or `No PYQ match in corpus`), and `PYQ Years` / `Paper(s)` are derived from them (`2016, 2021`; `Prelims + GS1 + GS3`; `—` when none). Earlier rows keep full question text.
`Date` = newspaper date (web date for web-only rows), never the run date.

**O-2 Build** (from `/home/claude`; copy the CSV to scratch first, oldest date first):

```
cp "pyq_index-/data/CA-PYQ Data YYYY-MM.csv" gh/base.csv
python3 pyq_index-/skill/ca_pyq_build.py --logs gh/base.csv --today today_D1.json --out-xlsx master/tmp.xlsx --out-day-csv upload_D1.csv
python3 pyq_index-/skill/ca_pyq_build.py --logs gh/base.csv upload_D1.csv --today today_D2.json \
  --out-xlsx "master/CA-PYQ Match Log.xlsx" --out-day-csv upload_D2.csv --monthly-dir /mnt/user-data/outputs
```

Run from `/home/claude` so the builder finds `pyq_bank.json` (or pass `--pyq-bank <path>`). Seven tabs, all Calibri 12: Revision Cards (phone-first, newest day first; V&R recall line when present) · Master Log · Topic Register · High-Probability (7 days) · PYQ Year Frequency · PYQ Bank · How to Use. The builder also reads every `data/CA-PYQ Data *.csv` in the clone, so the Topic Register and High-Probability tabs cover all months (each monthly file up to its own month). `--monthly-dir` writes `CA-PYQ Match Log YYYY-MM.xlsx` per month; that file is the only workbook the user reads.

**O-2a Design lock** — `skill/ca_pyq_build.py` is the source of truth; change script, `verify.py` and this table together (as a new version, §0).

| Element | Fixed value |
|---|---|
| Typeface | Calibri 12 everywhere; emphasis by weight, colour, fill |
| Palette | Navy `1F3864` · slate `44546A` · blue `2E75B6` · grey `404040` italic excerpts |
| Match colours | Direct `C6EFCE`/`145A32` · Thematic `FFF2CC`/`7D6608` · Emerging `E7E6E6`/`3B3838` |
| Date banding | `FFFFFF`/`F2F6FB`; medium navy top border on new date; bold date cell |
| Revision Cards | Columns 20/100; gridlines off; navy day banner (26) with match counts; card lines: headline · Area·Source · Syllabus (bold slate, when present) · PYQ years · Prelims recall (`F4F9F1`) · Mains recall (bold tags) · PYQ excerpts (italic) · Expected 2027 Qs · V&R recall (`FFF7E6`, when present) |
| Master Log | Widths `A:12 B:18 C:34 D:11 E:55 F:55 G:58 H:22 I:16 J:62 K:55 L:18 M:60`; Syllabus Tag in bold slate; header 36; freeze `E2`; autofilter `A1:M<last>`; landscape; header repeats |
| Master Log sub-rows (v10) | One sheet row per matched PYQ: H = year (bold navy), I = `Prelims` or `GS<n> (<marks> m)` (bold slate), J = full question (italic grey). Long item cells (E, F, G, K, L, M) merged across the item's sub-rows; A-D repeat on every sub-row (greyed after the first) so filters keep whole items. Last sub-row grows if merged text needs more height |
| Revision Cards PYQs (v10) | One card line per PYQ, labelled `Prelims <year>` / `GS<n> <year> (<marks> m)` |
| Row heights | `est_height()` — never Excel autofit |
| PYQ Bank (v19) | Every PYQ ID in the workbook's rows once: `PYQ ID · Paper · Year · Q · Marks · Full question · CA items · CA dates`; widths `A:18 B:10 C:8 D:10 E:8 F:90 G:10 H:30`; ID bold navy, question italic grey; most-matched first, then newest year; freeze `B2`; autofilter `A1:H<last>`. Rows before 4 Nov 2026 (full text, no IDs) do not appear |
| Topic Register (v22) | One row per Syllabus Tag (rows from 31 Oct 2026; untagged rows are not included) across all months: `Score · Subtopic · Syllabus (Paper › Subject › Topic) · Best match · PYQ years (all items) · PYQ papers · CA dates · CA items (newest first: date · match · headline) · Latest Prelims recall · Latest Mains recall · Syllabus base (V&R, latest)`; widths `A:8 B:30 C:34 D:11 E:22 F:14 G:16 H:62 I:55 J:58 K:55`; score = (distinct PYQ years + 1) × distinct CA dates; sorted by score, then latest date; freeze `C2`; autofilter `A1:K<last>` |
| High-Probability (7 days) (v22) | Orange banner (`C55A11`) with the week and the score rule; then the top 15 Topic Register subtopics with a CA date in the last 7 days of the log: `Rank · Score · Subtopic · Syllabus · Best match · PYQ years · CA dates (all) · This week · Latest headline · Latest [Mains 2027] question`; freeze `A3` |
| Tabs | Revision Cards `1F3864` → Master Log `2E75B6` → Topic Register `548235` → High-Probability (7 days) `C55A11` → PYQ Year Frequency `44546A` → PYQ Bank `8497B0` → How to Use `A6A6A6` |

**O-3 Deliver.** `SendUserFile` the current month's workbook (attach, one-line caption).

**O-4 Store on GitHub.** In the clone: fetch + hard reset to `origin/main`; read the month's CSV with `csv`; if its header lacks `Syllabus Tag`, insert that column (blank for old rows) after `GS Area`; assert none of the new dates exist; append rows from each `upload_YYYY-MM-DD.csv` (skip header) in date order, values unchanged; write with `csv.writer` (CRLF). New month → new `data/CA-PYQ Data YYYY-MM.csv` with the 13-column header. Commit `Add CA-PYQ rows for DD Mon YYYY (N)` with the session attribution lines; `git push origin HEAD:main`. Verify: fetch, `origin/main` is your commit, CSV rows = number of items in the monthly workbook (Master Log has more sheet rows from v10 because of PYQ sub-rows), all rows 13 fields. The CSV stays one row per item; PYQ IDs stay newline-separated in one cell. Commit `data/vr_pool.json` in the same commit when `vr_pool.py add` changed it. A rerun of an already-logged date replaces that date's rows (say so in the commit message). Never use a subagent to retype the CSV. Tell the user the Drive copy of the workbook is now theirs to replace.

**O-5 Reply** (concise): rows per date (newspaper/web) and match mix (Emerging count; `emerging_short` reason if set); candidates dropped by the cap; the week's top 5 High-Probability themes with scores; 3-5 top Direct items with PYQ years; new Emerging themes; each site's latest date; inputs not read; caveats.

## 4. VERIFY

For every date added: `python3 pyq_index-/skill/verify.py today_YYYY-MM-DD.json upload_YYYY-MM-DD.csv source_<dates>.txt` → fix until it prints `OK`. From 1 Nov 2026 (v10) it also checks every PYQ line is `P <year>:` / `GS<n> <year> (<marks>):`, none truncated or capped, and Master Log sub-rows = PYQ lines. From 31 Oct 2026 it checks the 15 + 5 cap, every tag against `syllabus.md`, GS Area = the tag's Paper + Subject (v18, P-8a), the syllabus block on newspaper rows only, identical blocks for identical tags, and (31 Oct-3 Nov reruns) each block equal to its `data/vr_topics.json` entry. From 4 Nov 2026 (v22) it also requires at least 3 Emerging rows (or `emerging_short`), each tagged item in the Topic Register with today's date and the score formula, and High-Probability ranks 1..n (≤15) in score order with a CA date this week. From 4 Nov 2026 (v20): newspaper rows have 2-4 `vr_facts` (or `[]`) that exist in the pool, come from a page on the row's syllabus line or sharing a subtopic keyword, do not repeat the row's recall, and are identical for the same tag on one date. From 4 Nov 2026 (v19) it checks `pyq_ids` (every ID in `pyq_bank.json`, no duplicates, one per year per paper, at least one for Direct/Thematic, no `years`/`papers`/`pyq_excerpt` fields), IDs (not text) in the CSV with derived PYQ Years, the Master Log text equal to the bank text, and the PYQ Bank tab. Run it from `/home/claude` (it reads `pyq_bank.json` there). The untraced-figure list is a review prompt (Act years and Articles are fine; an unsourced outlay is not).

## 5. Corpus helpers

`load_pyq.py` expected output: the "Expected `load_pyq.py` output" section of `README.md`. If the printed counts differ, stop and tell the user; do not run the match on an unexpected corpus.

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

## 6. V&R pool build (one-time, resumable)

Triggered by the user ("continue the V&R pool", "build the V&R pool"), not by a daily run. Goal: up to 8 V&R pages for every line of `skill/syllabus.md` (`vr_pool.py status` shows pages and searches per line; work on lines below 8, GS papers first, then Prelims and Essay lines).
1. For one syllabus line: 2-4 `WebSearch` calls with `allowed_domains: ["vajiramandravi.com"]`, one per main concept of the line (search results carry long page extracts; `WebFetch` a page only when its extract is thin). Do not repeat a query listed under `searched` for that line.
2. Keep only **theory pages** (v21): `vajiramandravi.com/upsc-exam/<topic>/`, `web.vajiramandravi.com/quest-upsc-notes/…`, and `vajiramandravi.com/current-affairs/<topic>/` pages that explain a fixed concept, Article, Act or institution (e.g. `article-324-of-the-constitution/`). Skip news explainers (an event, a ruling, a controversy, a phase), dated daily pages (`…/YYYY/MM/DD/`, rejected by `add`), course or test-series pages, and pages already in the pool or retired.
3. Per page write 4-12 facts of **fixed theory in your own words** (never copy V&R sentences; at most one quote, under 15 words), each ≤30 words: law + year, Article and clause, body with composition, appointment, tenure, removal and powers, concept, classification, landmark judgment, committee. No news content (`add` rejects 'recently', 'latest', 'currently', 'as of', 'ongoing', 'news' and flags years from 2025 for a check). `vr_pool.py remove <ID>` retires a page that turns out to be news. Leave out V&R typos and anything you cannot state with certainty. `subtopics` = 2-6 keywords the page covers.
4. Save as one batch per line (`{"line": "<exact syllabus line>", "queries": [...], "pages": [...]}`), run `python3 pyq_index-/skill/vr_pool.py add batch.json`, then commit `data/vr_pool.json` (`V&R pool: <line> (+N pages)`) and push after every few lines, so a cut-off session loses little.
5. End the session with `vr_pool.py status` totals and the lines still below 8.

Run your own scripts with plain `python3`; `-I` only for scripts that read downloaded data.
