# pyq_db: unified PYQ records (revamp)

One folder per year, one CSV per paper, named year-first so files sort year-wise:

```
pyq_db/2026/2026 Prelims GS1.csv
pyq_db/2026/2026 Mains GS1.csv ... 2026 Mains GS4.csv
pyq_db/2026/2026 Mains Essay.csv
pyq_db/2025/... (same six files)
```

Same 16 columns in every file:

`id, exam, year, paper, qno, part, section, marks, word_limit, subject, topic, stem, options, answer, source, quality_flag`

- `id`: `P2026-001` (Prelims), `M2026-GS2-04` (Mains), GS4 Section A parts `M2026-GS4-03b` (Q3 part b), case studies `M2026-GS4-07`, Essay `E2026-A1` … `E2026-B4`.
- Prelims numbering follows **Series/Set A** in both years.
- `subject`, `topic` and `answer` are left blank for now (to be added later).
- `quality_flag` (semicolon list): `web_verified` (wording checked against published copies of the paper, see below), `transcribed`, `case_study`, `untagged`, `answer_missing`.

## Status

| Year | Prelims GS1 | Mains GS1 / GS2 / GS3 | Mains GS4 | Essay | Verified |
|---|---|---|---|---|---|
| 2026 | 100 Qs, 200 marks | 20 / 20 / 20, 250 each | 13 parts (Q1–Q6) + 6 case studies (Q7–Q12), 250 | 8 topics | yes (25 Oct 2026) |
| 2025 | 100 Qs, 200 marks | 20 / 20 / 20, 250 each | 13 parts (Q1–Q6) + 6 case studies (Q7–Q12), 250 | 8 topics | yes (25 Oct 2026) |
| 2024 and earlier | old index | old index | old index (no case-study text) | missing | pending |

## How 2025 and 2026 were verified (25 Oct 2026)

UPSC's own PDFs are scanned images, so every question was compared word by word against published copies of the paper; where sources disagreed, the majority wording was kept.

- Prelims 2025: ThinqIAS (Series A, all 100 incl. options) and the PW book index; Q98–Q100 confirmed on upscsociology.in.
- Prelims 2026: The IAS Hub (Set D, all 100) and ThinqIAS / Vajiram per-question pages (Set A) for every disagreement.
- Mains 2025 GS1–GS4 and Essay: Anantam IAS (all questions), plus Understand UPSC and SuperKalam for GS4 Q11.
- Mains 2026 GS1–GS3: LegacyIAS and Vajiram & Ravi. GS4: Insights, LegacyIAS and ForumIAS. Essay: Insights.

Corrections made:

- **P2025** Q38, Q64 LaTeX removed; Q98–Q100 paraphrased stems replaced with the official wording.
- **GS4 2025** Q3(a)–(c) invented lead-in replaced with the paper's instruction line; Q8 dashes restored.
- **P2026** Q8, Q10, Q34 options corrected; Q62/Q63 swapped back to Set A order; Q67 List I order and option (d) restored.
- **GS3 2026** Q5 "farmers"; Q9 stray page header "3 KVMS-G-GSC" removed and "Intermediatory" as printed; Q15 "Why it is being considered"; Q19 "J & K".
- **GS4 2026** renumbered from 1(a)–(h)/2(a)–(e) to Q1–Q6 and case studies Q7–Q12; Q3(a) Ambedkar wording, Q7 (Sujatha, recommendations, tumor), Q8, Q9, Q10, Q11, Q12 wording corrected.

Kept as printed (not errors in this file): GS4 2025 Q11 (MGNREGA) gives no percentage for the "remaining period" wage; three independent copies print it that way.

**Single copy rule:** each year exists in one place only. 2025 and 2026 live only here; their records were removed from the old `*_Index.txt` files and the raw 2026 text files were deleted (still in git history). The old indexes now cover Prelims 2011-2024 and Mains 2013-2024. `load_pyq.py` (repo root) reads each year from exactly one source and fails if a year appears twice.

## Scripts

- `import_gs_text.py <transcript> <GSn> <year> <source>` → `YEAR/YEAR Mains GSn.csv` (flag `transcribed`).
- `import_gs4_text.py <transcript> <year> <source>` → `YEAR/YEAR Mains GS4.csv`.
- `import_prelims_text.py <transcript.md> <year> <source>` → `YEAR/YEAR Prelims GS1.csv`.
