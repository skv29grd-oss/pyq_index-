# ca-pyq-daily-match — changelog

Archived copies of every earlier version are in `skill/versions/v<N>_<YYYY-MM-DD>/` (date = day archived).

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
