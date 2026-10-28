# pyq_db: unified PYQ records (revamp)

One folder per year, one CSV per paper, named year-first so files sort year-wise:

```
pyq_db/2026/2026 Prelims GS1.csv
pyq_db/2026/2026 Mains GS1.csv ... 2026 Mains GS4.csv
pyq_db/2026/2026 Mains Essay.csv
pyq_db/2025/... (same six files)
pyq_db/2024/, pyq_db/2023/, pyq_db/2022/, pyq_db/2021/ (same six files)
```

Same 16 columns in every file:

`id, exam, year, paper, qno, part, section, marks, word_limit, subject, topic, stem, options, answer, source, quality_flag`

- `id`: `P2026-001` (Prelims), `M2026-GS2-04` (Mains), GS4 Section A parts `M2026-GS4-03b` (Q3 part b), case studies `M2026-GS4-07`, Essay `E2026-A1` … `E2026-B4`.
- Prelims numbering follows **Series/Set A** in every year (2024 Set A order differs from the PW book's order; the official Set A booklet was used).
- `subject`, `topic` and `answer` are left blank for now (to be added later).
- `quality_flag` (semicolon list): `official_verified` (transcribed from UPSC's own question-paper scan: OCR, then checked against the page images), `web_verified` (wording checked against published copies of the paper, see below), `transcribed`, `case_study`, `untagged`, `answer_missing`.

## Status

| Year | Prelims GS1 | Mains GS1 / GS2 / GS3 | Mains GS4 | Essay | Verified |
|---|---|---|---|---|---|
| 2026 | 100 Qs, 200 marks | 20 / 20 / 20, 250 each | 13 parts (Q1–Q6) + 6 case studies (Q7–Q12), 250 | 8 topics | yes (25 Oct 2026) |
| 2025 | 100 Qs, 200 marks | 20 / 20 / 20, 250 each | 13 parts (Q1–Q6) + 6 case studies (Q7–Q12), 250 | 8 topics | yes (25 Oct 2026) |
| 2024 | 100 Qs, 200 marks (official Set A scan) | 20 / 20 / 20, 250 each (web, majority of 2–3 copies) | 13 parts (Q1–Q6) + 6 case studies (Q7–Q12), 250 (web) | 8 topics (web) | yes (27 Oct 2026) |
| 2023 | 100 Qs, 200 marks (official Set A scan) | 20 / 20 / 20, 250 each (official scan) | 13 parts (Q1–Q6) + 6 case studies (Q7–Q12), 250 (official scan) | 8 topics (official scan) | yes (27 Oct 2026) |
| 2022 | 100 Qs, 200 marks (official Set A scan) | 20 / 20 / 20, 250 each (official scan) | 13 parts (Q1–Q6, Q5(b) = five 30-word short notes) + 6 case studies (Q7–Q12), 250 (official scan) | 8 topics (official scan) | yes (27 Oct 2026) |
| 2021 | 100 Qs, 200 marks (official Set A scan) | 20 / 20 / 20, 250 each (official scan) | 13 parts (Q1–Q6, Q3 = three quotations) + 6 case studies (Q7–Q12), 250 (official scan) | 8 topics (official scan) | yes (28 Oct 2026) |
| 2020 and earlier | old index | old index | old index (no case-study text) | missing | pending |

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

## How 2023 and 2024 were built (27 Oct 2026)

- **Official scans (user-supplied):** Prelims 2023 GS-I Set A (XDTG-F-GST), Prelims 2024 GS-I Set A (KSPC-P-GSPO), Mains 2023 GS1–GS4 and Essay. Pages OCR'd (tesseract, English column/lines only), then every table, quote mark, symbol and doubtful word checked against the page image. Flag `official_verified`.
- **Mains 2024 (no official scan yet):** GS1 – Anantam IAS + IASGyan; GS2 – IASGyan + upscsociology + Anantam; GS3 – Anantam + Drishti (OCR of the paper) + ClearIAS; GS4 – Understand UPSC (full paper) + NextIAS; Essay – Lukmaan IAS + IASGyan + ClearIAS. Majority wording kept, Section/question order and marks from the same sources. Flag `web_verified`. Replace with the official scan when available.
- Known 2024 Mains disputes kept as printed by the majority: GS2 Q5 "pros and cons of merging" (two copies omit "of").
- Wording kept as printed in the official paper, even where it looks wrong: GS1 2023 Q8 "loosing", GS4 2023 Q12 "duh".
- Prelims 2024 vs the PW book copy (old index): questions renumbered to the official Set A order (book Q51 = Set A Q1, book Q1 "Delimitation Commissions" = Set A Q71); book typos corrected to the official text, e.g. "(b) 1 and 2 only" (CDS), Statement-I/II option text, Set A Q9 option (d) "None", Q46 option (b) "3 and 4 only", Q31 "a by-product of weapons development", Q7 "reasons for weathering of rocks".

## How 2021 was built (28 Oct 2026)

- **Official scans (user-supplied):** Prelims 2021 GS-I Series A (BXC-U-FTHI), Mains 2021 GS1 (HXS-G-GSU), GS2 (HXS-G-GSB), GS3 (HXS-G-GST), GS4 (HXS-G-GSF) and Essay (HXS-G-ESSY). Scanned images with no text layer: 200 dpi render, tesseract OCR of the English text (Prelims column-by-column; GS4 filtered by word confidence to drop the Hindi), then question order, numbering, option letters and every doubtful token checked against the page images. Flag `official_verified`.
- Numbering follows the paper: GS2 Q9 is the Africa question (Q1–Q8 on p2, Q9–Q14 on p3); GS3 Q7–Q11 are the AQG, earthquake, money-laundering, cyber-attack and V-shaped-recovery questions. Marks: GS1–GS3 Q1–10 = 10 each, Q11–20 = 15 each; GS4 Q1–Q6 parts = 10 each, case studies Q7–Q12 = 20 each; Essay 8 × 125.
- Wording kept as printed even where it looks wrong: GS4 Q7 "relentness", "irrepairable"; Q12 "loose his temper", "publically"; Q10 "56342" (no separators) and "1.35 billion" (printed 1·35).
- GS4 Q3(a)–(c) carry the paper's instruction line ("What does each of the following quotations mean to you?") in each part, as in 2022. Case-study stems include their sub-questions inline.
- Prelims fixes made from the images: Q37 pair table written as `[Historical place — Well-known for]`; comma spacing in digit lists; OCR-garbled options in Q61 and Q81.
- 2021 removed from the old indexes the same day: 84 Prelims lines (index counts recomputed; one shared `(2019/2021)` entry kept as `(2019)`) and 73 Mains records (GS1 20, GS2 18, GS3 20, GS4 15). The old index never held the full 2021 papers.

## How 2022 was built (27 Oct 2026)

- **Official scans (user-supplied):** Prelims 2022 GS-I Series A (T.B.C. VGYH-U-FGT, 48 pages), Mains 2022 GS1 (CRNA-X-GSU), GS2, GS3 (CRNA-X-GST), GS4 (CRNA-X-GSF) and Essay (CRNA-X-ESSY). English text OCR'd (tesseract; Prelims column-by-column), then question order, numbering, option letters, tables and every doubtful token checked against the page images. Flag `official_verified`.
- Prelims fixes made from the images: Q29 "longest day"; Q32 "Web 3.0" (printed 3·0); Q44 PM2.5 / PM10 and µg/m³; statement/option digits misread by OCR (8→3, l→1). Pair-table headers written as `[Column — Column]`.
- GS4 2022 Q3(a)–(c) carry the paper's instruction line ("What does each of the following quotations mean to you?") in each part; Q5(b) is one 10-mark row (`word_limit` = `30 each`).
- 2022 removed from the old indexes the same day: 71 Prelims lines (index counts recomputed) and 76 Mains records (GS1 20, GS2 20, GS3 21, GS4 15 — the old index had mis-dated items, e.g. a 2021 Bhakti question tagged 2022).

**Single copy rule:** each year exists in one place only. 2025 and 2026 live only here; their records were removed from the old `*_Index.txt` files and the raw 2026 text files were deleted (still in git history). 2023, 2024 and then 2022 were likewise removed from the old indexes on 27 Oct 2026. 2021 was moved the same way on 28 Oct 2026. The old indexes now cover Prelims 2011-2020 and Mains 2013-2020. `load_pyq.py` (repo root) reads each year from exactly one source and fails if a year appears twice.

## Scripts

- `import_gs_text.py <transcript> <GSn> <year> <source>` → `YEAR/YEAR Mains GSn.csv` (flag `transcribed`).
- `import_gs4_text.py <transcript> <year> <source>` → `YEAR/YEAR Mains GS4.csv`.
- `import_prelims_text.py <transcript.md> <year> <source>` → `YEAR/YEAR Prelims GS1.csv`.
