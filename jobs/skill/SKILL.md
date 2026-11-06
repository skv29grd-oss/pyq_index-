# Job Openings Finder (B.Com / B.Tech graduates) — full instructions

Version: **v1** (2026-11-06). Current version number lives in `jobs/skill/VERSION`; history in `jobs/skill/CHANGELOG.md`; every earlier version in `jobs/skill/versions/`.

Finds open job notifications in central and state govt departments, PSUs, banks/regulators, defence entries, apprenticeships and the private sector. Checks each one against every candidate profile in `jobs/profiles/`. Keeps a running database on GitHub and sends a tracker workbook.

Triggered manually by the user ("run job search", "find jobs", "jobs for <name>", the skill name). Never schedule it unless the user asks.

## 0. Files and versioning (read first)

| File | Role |
|---|---|
| `jobs/skill/SKILL.md` | These instructions: the single source of truth |
| `jobs/skill/jobs_tool.py` | Database tool: `status`, `add`, `recheck`, `open`, `xlsx`, `verify`. Run from the repo root; never retype it |
| `jobs/skill/sources.md` | Source registry: where to look, per sector, and how reliable each source is |
| `jobs/profiles/<id>.json` | One candidate per file (data, not a skill file: editing needs no version bump) |
| `jobs/data/Jobs Log YYYY-MM.csv` | One row per job, filed by the month of `date_found` (28 columns, `COLS` in `jobs_tool.py`) |
| `jobs/data/applications.csv` | One row per job x candidate: eligibility (Yes/Check), reason, status, updated |
| `jobs/skill/VERSION` | Current version number |
| `jobs/skill/CHANGELOG.md` | One entry per version |
| `jobs/skill/versions/v<N>_<YYYY-MM-DD>/` | Frozen copy of version N, dated the day it was replaced |

**Versioning rule (every change to anything in `jobs/skill/`):**
1. Read `jobs/skill/VERSION`. That gives N. Today's date (Asia/Calcutta) gives D.
2. Copy all files in `jobs/skill/` except `versions/` into `jobs/skill/versions/v<N>_<D>/` unchanged. Second change on the same day: `_b`, `_c`, ….
3. Commit the archive on its own: `Jobs skill: archive v<N> (<D>) before update`.
4. Make the change. Write N+1 into `VERSION`, update the `Version:` line above, add a CHANGELOG entry.
5. Commit `Jobs skill v<N+1>: <summary>` and push. Never edit anything inside `versions/`.
6. Only the user decides a change to the skill. Tell them the new version number and what changed.

Profile edits and database rows are data: no archive, no version bump.

**Privacy (public repo).** Never write phone numbers, email addresses, home addresses, ID numbers or caste/category into any file in the repo. `verify` fails on `phone`/`email`/`mobile` keys in a profile. Age relaxation by category is written as a note on the job row, never stored per candidate.

## At a glance

| Stage | What happens |
|---|---|
| 1. Inputs | Repo clone · profiles · last run date · sources per sector · any files the user drops in |
| 2. Processing | Search each sector → open the official notification → extract fields → hard-filter by profile → rank → cap |
| 3. Output | `jobs_tool.py add` → `verify` → `xlsx` → send workbook → commit + push data |
| 4. Reply | 6-10 lines: new jobs per candidate, deadlines in 7 days, profile gaps blocking checks, sources that failed |

Run checklist (tick every box before replying):

- [ ] Repo `skv29grd-oss/pyq_index-` attached with **push** access (`add_repo`, access `push`) and cloned to `/home/claude/pyq_index-`; `git fetch origin main && git reset --hard origin/main` done
- [ ] `python3 jobs/skill/jobs_tool.py status` run; last `date_found` noted; profile gaps noted
- [ ] Every sector in §1 I-3 searched, or the reason it was skipped stated
- [ ] Every govt/PSU/bank/defence row opened on the **official** site (notification PDF or careers page) and marked `official_verified=Y`; aggregator-only finds left out
- [ ] Every figure (vacancies, age, %, fee, dates) taken from the notification text, not from memory or an aggregator
- [ ] Cap respected (P-6); no job with `apply_end` before today added
- [ ] `add` run, `verify` prints OK, workbook built and sent
- [ ] Data committed and pushed; re-fetched; row count checked

---

## 1. INPUTS

| # | Input | Where | Notes |
|---|---|---|---|
| I-1 | Candidate profiles | `jobs/profiles/*.json` | Fields used by eligibility: `degree`, `branch_tags`, `grad_year`, `percent_equivalent` (else `cgpa`), `dob`, `gate`, `fulltime_experience_months`, `tracks`, `preferences`. A profile with `profile_status` PENDING gets only "Check" rows |
| I-2 | Database | `jobs/data/` | `status` gives the last `date_found`. Search window = notifications published since that date, plus every notification still open (`apply_end` >= today) not yet in the log. First run: all open notifications |
| I-3 | Sources | `jobs/skill/sources.md` | Search every sector each run: Central Govt, State Govt (only states in some profile's `domicile_state`, plus all-India-open state posts), PSU (GATE and non-GATE), Bank/Financial Regulator, Defence, Apprenticeship, Private |
| I-4 | User drops (optional) | Chat upload, or Gmail job-alert mails (LinkedIn, Naukri, Indeed, Internshala) via the Gmail connector | Gmail: `search_threads` with `newer_than:7d` and the alert senders; read the mail, then open each job link |
| I-5 | New or changed profile | Resume PDF upload, LinkedIn "Save to PDF", or screenshots | LinkedIn pages refuse automated fetch: ask for a PDF or screenshots. Update the profile JSON, then `recheck` |

**Profile build rules.** Copy only what the resume states. Leave unknowns `null` and list them in `missing_inputs`. Never convert CGPA to % unless the university's rule is given (`percent_note`). `tracks` are defaults set by Claude; mark them so until the user confirms.

## 2. PROCESSING

**P-1 Search.** Per sector, use `WebSearch` with the current month and year, e.g. `NTPC recruitment November 2026`, `ESE 2027 notification`, `RBI Grade B 2026 notification`, `data analyst fresher jobs B.Tech 2026 hiring`. Use the registry in `sources.md` for official domains. Send independent searches in one turn.

**P-2 Verify on the official source.** For govt, PSU, bank, regulator and defence posts, open the official notification (PDF or careers page) with `WebFetch`. Aggregators (FreeJobAlert, SarkariResult, Jagran Josh, etc.) are for discovery only. No official page found: leave the job out and list it under "unverified leads" in the reply. Private jobs: the company careers page or the job-board posting is the source; mark `official_verified=N` unless it is the company's own site, then `Y`.

**P-3 Extract fields** (columns of `Jobs Log`):
`date_found` (today) · `sector` (one of the 7 in `SECTORS`) · `organisation` · `post` · `advt_no` · `eligible_degrees` (`;`-separated: `B.Tech;B.E.`, `B.Com`, `Any graduate`) · `eligible_branches` (`;`-separated tags matching profile `branch_tags`, e.g. `ECE;EEE`; empty = any) · `grad_years` (only when the notice restricts batches) · `min_percent` · `gate_paper` (e.g. `EC`) · `age_min`, `age_max` (General category) · `age_cutoff_date` · `experience` · `selection_mode` (GATE score / written exam / interview / merit) · `vacancies` · `pay` (pay level or CTC) · `location` · `apply_start`, `apply_end`, `exam_date` (all `YYYY-MM-DD`) · `fee` · `notification_url` · `apply_url` · `source` · `official_verified` (Y/N) · `notes` (category age relaxation, final-year students allowed, bond, etc.).

Dates unknown or "to be announced": leave empty, except `apply_end`. A rolling private post without a deadline: `apply_end` = date_found + 30 days, and note "rolling; deadline assumed".

**P-4 Eligibility** is computed by `jobs_tool.py` (`eligibility()`):
- **No**: degree, branch, graduation year, GATE paper or minimum age fails. Not written to `applications.csv`.
- **Check**: data missing (DOB, % conversion, profile pending) or age above the General limit, which may pass only with category relaxation.
- **Yes**: every rule the notice sets passes on known data.
Read the notice for rules the tool does not model (final-year allowed, nationality, physical standards, experience type). Put them in `notes`, and in the reply flag any Yes they could overturn.

**P-5 Rank** within each candidate: (1) Yes before Check; (2) closing soonest; (3) fit to `tracks` and `skills`; (4) pay; (5) location in `preferences`.

**P-6 Cap.** Per run at most 15 govt/PSU/bank/defence/apprenticeship rows plus 10 private rows across all candidates. A job relevant to two candidates is one row.

**P-7 Updates.** A corrigendum or deadline extension: `add` the job again with the same `advt_no` (or the same `notification_url`). The tool updates the row and logs the change in `notes`. Closed jobs flip to status `Closed` automatically.

## 3. OUTPUT

1. Write the run's rows to `/home/claude/jobs_rows.json` (a JSON list of objects with the P-3 keys).
2. From the repo root: `python3 jobs/skill/jobs_tool.py add /home/claude/jobs_rows.json`.
3. `python3 jobs/skill/jobs_tool.py verify`. It must print `OK`. Fix and re-run until it does.
4. `python3 jobs/skill/jobs_tool.py xlsx --out "/home/claude/Job Tracker YYYY-MM-DD.xlsx"`. Tabs: Open Jobs (nearest deadline first, eligibility per candidate), one tab per candidate (eligibility colour, reason, status), All Jobs, Profiles. Send it with `SendUserFile`.
5. `git add jobs/data jobs/profiles && git commit -m "Jobs: run YYYY-MM-DD (<n> added, <m> updated)" && git push`. Then `git fetch origin main` and check `git diff origin/main --stat` is empty.

**Status updates from the user** ("applied to NTPC ET for Shivam"): edit that row's `status` and `updated` in `applications.csv` (statuses in `STATUSES`), `verify`, commit, push. No search run needed.

## 4. REPLY

6-10 lines, no recap of steps:
- New jobs per candidate: count of Yes and Check, top 3 by rank with deadline.
- Deadlines within 7 days (from `open --days 7`).
- Profile gaps that turned rows into Check (e.g. "DOB missing for shivam-raj: 6 age checks pending").
- Sources that failed or were skipped, and unverified leads.
