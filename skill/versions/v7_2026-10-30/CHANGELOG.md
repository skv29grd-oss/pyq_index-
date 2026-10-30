# ca-pyq-daily-match — changelog

Archived copies of every earlier version are in `skill/versions/v<N>_<YYYY-MM-DD>/` (date = day archived).

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
