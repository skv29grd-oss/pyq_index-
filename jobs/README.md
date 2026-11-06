# jobs/ — Job Openings Finder

Separate from the PYQ corpus and the ca-pyq-daily-match skill: nothing here is read by `load_pyq.py` or `skill/`.

- `skill/` — instructions (`SKILL.md`), tool (`jobs_tool.py`), source registry, VERSION, CHANGELOG, `versions/`
- `profiles/` — one candidate per JSON file (no contact details: this repo is public)
- `data/Jobs Log YYYY-MM.csv` — job database, one row per notification
- `data/applications.csv` — eligibility and application status per job and candidate

Start: `python3 jobs/skill/jobs_tool.py status` from the repo root.
