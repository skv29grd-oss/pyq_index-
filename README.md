# pyq_index-

UPSC CSE PYQ corpus for the ca-pyq-daily-match skill. One copy of every year.

This file is the single source for **corpus coverage** and the **expected `load_pyq.py` output**. `skill/SKILL.md` points here and does not repeat year ranges. Update this file and `CORPUS_CHANGELOG.md` in the same commit as any corpus change (no skill version bump; see `skill/SKILL.md` §0). Build notes per year: `pyq_db/README.md`.

## Coverage

| Years | Where |
|---|---|
| Prelims 2013-2026; Mains GS1-GS4 and Essay 2013-2026 | `pyq_db/<year>/<year> <paper>.csv` — official papers, except Prelims 2025-2026 and Mains 2024-2026 (web-verified) |
| Prelims 2011-2012 | `Prelims_Index.txt`, `Prelims_Index_Part2_*.txt`, `Prelims_Index_Part3_*.txt` — topic-wise, incomplete; stored text is the index wording |
| Mains (any year) from the old indexes | None. `GS1_Index.txt` … `GS4_Index.txt` remain in the repo but `load_pyq.py` reads no Mains year from them (`YRS_OLD` never matches) |
| Items with unverified year (not loaded) | `Index_year_unverified.txt` |
| Daily CA-PYQ log | `data/CA-PYQ Data YYYY-MM.csv` |

`python3 load_pyq.py .` builds `mains_recs.json` and `prelims_lines.txt` for matching.

## Expected `load_pyq.py` output

Checked on 6 Nov 2026 (commit `5a2e367`). If a run prints anything else, the corpus has changed without this file being updated: stop and check before matching.

| Paper | 2013 | 2014 | 2015 | 2016 | 2017-2026 (each year) |
|---|---|---|---|---|---|
| Mains GS1 | 30 | 25 | 20 | 20 | 20 |
| Mains GS2 | 25 | 20 | 20 | 20 | 20 |
| Mains GS3 | 28 | 20 | 20 | 20 | 20 |
| Mains GS4 | 18 | 19 | 18 | 18 | 19 |
| Mains Essay | 4 | 8 | 8 | 8 | 8 |
| Prelims full-paper stems | 100 | 100 | 100 | 100 | 100 |

- `old index Mains records: 0`
- `prelims lines: 1833`
