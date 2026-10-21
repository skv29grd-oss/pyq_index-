# pyq_db: unified PYQ records (revamp)

One CSV per year: `YYYY.csv`, built by `build_db.py` from the raw paper files. Same 16 columns for Prelims, Mains and Essay.

`id, exam, year, paper, qno, part, section, marks, word_limit, subject, topic, stem, options, answer, source, quality_flag`

- `id`: `P2026-001` (Prelims), `M2026-GS2-04` (Mains; GS4 sub-parts `M2026-GS4-01a`), `E2026-A1` (Essay).
- `quality_flag` (semicolon list): `untagged` (subject/topic not yet assigned), `answer_missing` (no key in source), `options_count_N`, `marks_missing`, `case_study`, `ocr_partial`.
- Rebuild order: 2026, 2025, 2024 ... 2011. Older indexes (`*_Index.txt`) stay until a year is rebuilt.

## Status
| Year | Prelims | Mains GS1-4 | Essay | Notes |
|---|---|---|---|---|
| 2026 | 100/100 | 20/20/20/19 (GS4: 13 Sec A parts + 6 case studies) | 8 topics | answers and subject/topic tags pending |
| 2025 | old index | old index (GS Mains 2025 incomplete) | 8 topics (done, `Essay Paper 2025.csv`) | needs Mains GS1-4 papers; Prelims to convert |
| 2024 and earlier | old index | old index | missing | pending |
