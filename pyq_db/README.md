# pyq_db: unified PYQ records (revamp)

One CSV per paper: `Prelims YYYY.csv`, `Mains GS1 YYYY.csv` ... `Mains GS4 YYYY.csv`, `Essay Paper YYYY.csv`. `build_db.py` builds them from the raw paper files. Same 16 columns in every file.

`id, exam, year, paper, qno, part, section, marks, word_limit, subject, topic, stem, options, answer, source, quality_flag`

- `id`: `P2026-001` (Prelims), `M2026-GS2-04` (Mains; GS4 sub-parts `M2026-GS4-01a`), `E2026-A1` (Essay).
- `quality_flag` (semicolon list): `untagged` (subject/topic not yet assigned), `answer_missing` (no key in source), `options_count_N`, `marks_missing`, `case_study`, `ocr_partial`.
- Rebuild order: 2026, 2025, 2024 ... 2011. Older indexes (`*_Index.txt`) stay until a year is rebuilt.

## Status
| Year | Prelims | Mains GS1-4 | Essay | Notes |
|---|---|---|---|---|
| 2026 | 100/100 | 20/20/20/19 (GS4: 13 Sec A parts + 6 case studies) | 8 topics | answers and subject/topic tags pending |
| 2025 | 100/100 (answers pending) | GS1–GS4 done (GS4: 13 Sec A parts + 6 case studies, 250 marks) | 8 topics (done) | Year complete except answer key and subject/topic tags |
| 2024 and earlier | old index | old index | missing | pending |

`import_gs_text.py <transcript> <GSn> <year> <source>` imports a bilingual transcribed Mains paper into `Mains GSn YEAR.csv` (flag `transcribed`).
`import_prelims_text.py <transcript.md> <year> <source>` imports a bilingual Prelims transcript (`#### Qn.` / `**English:**`); tables are flattened to `[col / col]` rows. `import_gs4_text.py <transcript> <year> <source>` imports GS4.
