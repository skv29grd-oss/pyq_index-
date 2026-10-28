# pyq_index-

UPSC CSE PYQ corpus for the ca-pyq-daily-match skill. One copy of every year:

| Years | Where |
|---|---|
| 2021, 2022, 2023, 2024 | `pyq_db/<year>/<year> <paper>.csv` — official papers (Mains 2024: web-verified) |
| 2025, 2026 | `pyq_db/<year>/<year> <paper>.csv` — web-verified |
| Prelims 2011-2020 | `Prelims_Index.txt`, `Prelims_Index_Part2_*.txt`, `Prelims_Index_Part3_*.txt` |
| Mains GS1-GS4 2013-2020 | `GS1_Index.txt` … `GS4_Index.txt` (GS4 case studies: topic index only) |
| Daily CA-PYQ log | `data/CA-PYQ Data YYYY-MM.csv` |

`python3 load_pyq.py .` builds `mains_recs.json` and `prelims_lines.txt` for matching.
