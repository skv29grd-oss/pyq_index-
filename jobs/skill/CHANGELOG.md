# job-openings-finder — changelog

Archived copies of every earlier version are in `jobs/skill/versions/v<N>_<YYYY-MM-DD>/` (date = day archived).

## v1 — 2026-11-06
- First version. Sectors: Central Govt, State Govt, PSU, Bank/Financial Regulator, Defence, Apprenticeship, Private.
- `jobs_tool.py`: `status`, `add` (dedup by organisation + advt no, or notification URL; corrigenda update the same row), `recheck`, `open`, `xlsx` (Open Jobs, one tab per candidate, All Jobs, Profiles), `verify` (columns, dates, official verification for govt rows, no contact details in profiles).
- Eligibility: Yes / Check / No from degree, branch, graduation year, GATE paper, minimum %, age and experience.
- Database seeded with two profiles: shivam-raj (from resume) and satyam-sagar (pending; LinkedIn could not be fetched).
- Defaults used because the 27 design inputs were not answered: manual trigger, cap 15 govt + 10 private per run, official-source verification, GitHub CSV store + workbook sent in chat.
