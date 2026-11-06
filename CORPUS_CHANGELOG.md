# PYQ corpus changelog

One entry per change to the PYQ corpus (`pyq_db/`, the old `*_Index.txt` files, `load_pyq.py`). Corpus changes do not bump the skill version (`skill/SKILL.md` §0). Current coverage and expected `load_pyq.py` output: `README.md`. Per-year build notes: `pyq_db/README.md`.

Entries before 6 Nov 2026 are reconstructed from git history; until v17 these changes were also logged as skill versions v11-v17 in `skill/CHANGELOG.md`.

## 2026-11-06
- `load_pyq.py` also writes `pyq_bank.json` (2,821 PYQ IDs: 1,400 Prelims 2013-2026, 182 old-index Prelims 2011-2012, 1,239 Mains) and adds `id` to `mains_recs.json`, for skill v19. Old-index line `AC Q42 (2014/2015)` skipped as a duplicate of `pyq_db` Prelims 2014/2015. `pyq_bank.json` git-ignored like the other loader outputs.
- Coverage and expected loader counts moved out of `skill/SKILL.md` into `README.md`; this changelog started. `pyq_db/README.md`: 2013 status row fixed (cells had shifted one column; Essay cell was missing).
- `5a2e367` Mains 2013 (GS1-GS4, Essay) added to `pyq_db/` from official scans; 2013 removed from the old indexes. The loader now reads no Mains year from the old indexes.
- `64ecd3a` Mains 2014 (GS1-GS4, Essay) added to `pyq_db/` from official papers; removed from the old index.

## 2026-11-03
- `19bbcb6` Mains GS4 2015 added from the official paper (2015 complete). Logged as skill v17.
- `fa114c0` Prelims 2013-2015 and Mains 2015 GS1-GS3 + Essay added from official papers. Logged as skill v16.
- `93dfa2d` 2016 (Prelims, Mains GS1-GS4, Essay) added from official scans. Logged as skill v15.
- `1436297` 2017 (Prelims, Mains GS1-GS4, Essay) added from official scans. Logged as skill v14.
- `5309090` Mains GS1 2018 added (2018 complete). Logged as skill v13.
- `6b56596` 2018 Prelims, Mains GS2-GS4 and Essay added from official scans. Logged as skill v12.
- `2be9bc7` 2019 (Prelims, Mains GS1-GS4, Essay) added from official scans. Logged as skill v11.

## 2026-10-30
- `447e950` 2020 added to `pyq_db/`; removed from the old indexes.

## 2026-10-28
- `87e3ca8` 2021 added to `pyq_db/`; removed from the old indexes.

## 2026-10-27
- `03c0293` 2022 added to `pyq_db/`; removed from the old indexes.
- `b2496b5` 2023 and 2024 added to `pyq_db/`; removed from the old indexes.

## 2026-10-25
- `bf5968b`, `0e4e43a` 2025 and 2026 papers verified and corrected; year-wise layout; one copy per year (2025-2026 only in `pyq_db/`).

## 2026-10-21
- `3f35e9f` … `d1a2f74` `pyq_db/` created with a unified schema: 2026 rebuilt, 2025 added (Prelims, Mains GS1-GS4, Essay), one CSV per paper.
