# ca-pyq-daily-match — changelog

Archived copies of every earlier version are in `skill/versions/v<N>_<YYYY-MM-DD>/` (date = day archived).

## v17 — 2026-11-03
- PYQ corpus: Mains GS4 2015 added from the official paper (2015 now complete); GS4 2015 removed from old index; coverage lines and expected counts updated (old index Mains 2013-2014: 179).

## v16 — 2026-11-03
- PYQ corpus: Prelims 2013, 2014, 2015 and Mains 2015 GS1-GS3 + Essay added to `pyq_db/` from official papers; removed from old indexes. Mains GS4 2015 stays in the old index (not supplied). Coverage lines and expected counts updated (old index 193).

## v15 — 2026-11-03
- PYQ corpus: 2016 (Prelims, Mains GS1-GS4, Essay) added to `pyq_db/` from official scans; 2016 removed from old indexes; coverage lines and expected counts updated (old index 2013-2015: 253; GS4 2016 has 18 rows).

## v14 — 2026-11-03
- PYQ corpus: 2017 (Prelims, Mains GS1-GS4, Essay) added to `pyq_db/` from official scans; 2017 removed from old indexes; coverage lines and expected counts updated (old index 2013-2016: 326).

## v13 — 2026-11-03
- PYQ corpus: Mains GS1 2018 added from the official scan, so 2018 is complete in `pyq_db/`; coverage lines and expected count updated (old index 2013-2017: 405).

## v12 — 2026-11-03
- PYQ corpus: 2018 Prelims, Mains GS2-GS4 and Essay added to `pyq_db/` from official scans; Mains GS1 2018 not yet supplied (stays in old index). `load_pyq.py` moves years per paper; coverage lines and expected counts updated (old index 425).

## v11 — 2026-11-03
- PYQ corpus: 2019 added to `pyq_db/` from official scans (Prelims + Mains GS1-GS4 + Essay); 2019 removed from old indexes. Coverage lines and `load_pyq.py` expected counts updated (full papers 2019-2026; old index 2013-2018: 477).

## v10 — 2026-11-02
- PYQ excerpts are quoted in full (no 210-character truncation, no eight-question `+N more` cap), as the user found incomplete question texts.
- Master Log: one sheet sub-row per matched PYQ (year, paper, full question) under each item; long item cells merged across sub-rows; Date, GS Area, Syllabus Tag, Match repeated (greyed) for filtering. Revision Cards: one line per PYQ.
- GitHub CSV schema unchanged (one row per item). verify.py checks PYQ line format, no truncation/cap and sub-row count from 1 Nov 2026.
- 1-2 Nov 2026 rows rerun under v10.

## v9 — 2026-10-30
- V&R daily news facts are now merged into each row's topic and Prelims/Mains recall, like Next IAS and Drishti (V&R named in Source); the `vr` field is dropped from 31 Oct 2026.
- Column 13 `V&R Recall` holds only the [Syllabus base] block (newspaper rows; blank for web-only rows).
- verify.py rejects a `vr` field on rows from 31 Oct 2026. Rows of 29-30 Oct keep their old V&R text.

## v8 — 2026-10-30
- Selection cap: at most 15 newspaper items + 5 web-only items (Drishti, Next IAS, V&R combined) per date, ranked by match class, PYQ years, Prelims+Mains value and syllabus spread.
- New column 3 `Syllabus Tag` (Paper › Subject › Topic › Subtopic), topics fixed by new `skill/syllabus.md`; Master Log now 13 columns, freeze E2, autofilter A:M.
- V&R column now has two blocks: [CA] (daily V&R facts) and, for newspaper items only, [Syllabus base] from V&R's page on the exact syllabus subtopic; identical for items sharing a tag.
- Builder reads CSVs by header name (11/12/13 columns); verify.py enforces the v8 rules from 31 Oct 2026.
- Data CSV migrated to 13 columns (Syllabus Tag blank for rows before 31 Oct 2026).

## v7 — 2026-10-30
- Skill moved to GitHub (`skill/`); the Claude-settings skill is now a short pointer to this folder.
- Versioning rule: before any change, archive all current skill files to `skill/versions/v<N>_<date>/`, then bump `VERSION` and log here.
- Vajiram & Ravi added as a daily source (Prelims + Mains pages); V&R-only items can become rows.
- New 12th column `V&R Recall (Vajiram & Ravi)` and a V&R recall card line; widths/autofilter extended to L.
- Data store is the GitHub monthly CSV `data/CA-PYQ Data YYYY-MM.csv` (Drive CSV store retired); rows pushed with git.
- Mandatory gap check: all missing dates up to today run oldest first; web items go under their own date.
- Build, verify and search scripts are files in the repo instead of text to copy.

## v6 — archived 2026-10-30
- Drive-era skill: 11-column schema, Drive CSV store, Hindu + Next IAS + Drishti. See `versions/v6_2026-10-30/`.
