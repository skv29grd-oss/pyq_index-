#!/usr/bin/env python3
"""Job-openings database tool (jobs/ in skv29grd-oss/pyq_index-).

Run from the repo root:
  python3 jobs/skill/jobs_tool.py status
  python3 jobs/skill/jobs_tool.py add rows.json        # append/update jobs, create application rows
  python3 jobs/skill/jobs_tool.py recheck              # re-run eligibility after a profile change
  python3 jobs/skill/jobs_tool.py open [--days 15]     # open jobs, nearest deadline first
  python3 jobs/skill/jobs_tool.py xlsx [--out FILE]    # build the tracker workbook
  python3 jobs/skill/jobs_tool.py verify               # checks before every push

Data (all CSV: header row, CRLF row endings, UTF-8):
  jobs/data/Jobs Log YYYY-MM.csv  one row per job, month = date_found
  jobs/data/applications.csv      one row per (job, candidate) with eligibility and status
  jobs/profiles/<id>.json         one candidate per file
"""
import csv, glob, hashlib, json, os, re, sys
from datetime import date, datetime

ROOT = os.getcwd()
JOBS = os.path.join(ROOT, "jobs")
DATA = os.path.join(JOBS, "data")
PROF = os.path.join(JOBS, "profiles")
APPS = os.path.join(DATA, "applications.csv")

COLS = ["job_id", "date_found", "sector", "organisation", "post", "advt_no",
        "eligible_degrees", "eligible_branches", "grad_years", "min_percent",
        "gate_paper", "age_min", "age_max", "age_cutoff_date", "experience",
        "selection_mode", "vacancies", "pay", "location", "apply_start",
        "apply_end", "exam_date", "fee", "notification_url", "apply_url",
        "source", "official_verified", "notes"]
REQUIRED = ["date_found", "sector", "organisation", "post", "eligible_degrees",
            "apply_end", "notification_url", "source", "official_verified"]
SECTORS = ["Central Govt", "State Govt", "PSU", "Bank/Financial Regulator",
           "Defence", "Apprenticeship", "Private"]
APP_COLS = ["job_id", "candidate_id", "eligibility", "reason", "status", "updated"]
STATUSES = ["New", "To apply", "Applied", "Admit card", "Exam taken", "Interview",
            "Selected", "Rejected", "Skipped", "Closed"]
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def today():
    return date.today()


def d(s):
    return datetime.strptime(s, "%Y-%m-%d").date() if s and DATE_RE.match(s) else None


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")[:40]


def make_id(r):
    """organisation + advt no; without an advt no, post + hash of the notification URL.
    The deadline is never part of the ID, so a corrigendum updates the same row."""
    if r.get("advt_no"):
        return slug(r["organisation"]) + "--" + slug(r["advt_no"])
    h = hashlib.sha1(r["notification_url"].encode()).hexdigest()[:8]
    return slug(r["organisation"]) + "--" + slug(r.get("post", ""))[:30] + "-" + h


# ---------- storage ----------
def read_csv(path):
    if not os.path.exists(path):
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(path, cols, rows):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\r\n")
        w.writeheader()
        for r in rows:
            w.writerow({c: r.get(c, "") for c in cols})


def month_files():
    return sorted(glob.glob(os.path.join(DATA, "Jobs Log *.csv")))


def load_jobs():
    out = []
    for p in month_files():
        for r in read_csv(p):
            r["_file"] = p
            out.append(r)
    return out


def load_profiles():
    ps = {}
    for p in sorted(glob.glob(os.path.join(PROF, "*.json"))):
        with open(p, encoding="utf-8") as f:
            j = json.load(f)
        ps[j["id"]] = j
    return ps


# ---------- eligibility ----------
def norm_degree(s):
    s = (s or "").lower().replace(" ", "").replace(".", "")
    if not s:
        return None
    if "anygraduate" in s or s in ("graduate", "anydegree", "graduation"):
        return "any"
    if "btech" in s or s in ("be",) or "be/" in s or "/be" in s or "engineering" in s:
        return "btech"
    if "bcom" in s or "commerce" in s:
        return "bcom"
    return s


def split(s):
    return [x.strip() for x in re.split(r"[;|]", s or "") if x.strip()]


def eligibility(job, p):
    """Return (Yes|Check|No, reason). No = a hard rule fails; Check = data missing."""
    checks, nos = [], []
    cdeg = norm_degree(p.get("degree"))
    if not cdeg:
        return "Check", "profile pending (degree unknown)"
    jdegs = {norm_degree(x) for x in split(job.get("eligible_degrees"))}
    if "any" not in jdegs and cdeg not in jdegs:
        nos.append("degree " + (p.get("degree") or "") + " not in " + job.get("eligible_degrees", ""))
    branches = split(job.get("eligible_branches"))
    if branches and cdeg == "btech" and "any" not in jdegs and not any(b.lower() == "any" for b in branches):
        tags = [t.lower() for t in p.get("branch_tags", [])] + [(p.get("branch") or "").lower()]
        if not any(b.lower() in tags or any(b.lower() in t for t in tags if t) for b in branches):
            nos.append("branch not in " + job["eligible_branches"])
    gy = split(job.get("grad_years"))
    if gy and p.get("grad_year") and str(p["grad_year"]) not in gy:
        nos.append("graduation year %s not in %s" % (p["grad_year"], job["grad_years"]))
    if job.get("gate_paper"):
        g = p.get("gate") or {}
        if not g:
            nos.append("needs GATE %s score" % job["gate_paper"])
        elif str(g.get("paper", "")).upper() not in [x.upper() for x in split(job["gate_paper"])]:
            nos.append("GATE paper %s needed" % job["gate_paper"])
    if job.get("min_percent"):
        pct = p.get("percent_equivalent")
        if pct is None:
            checks.append("min %s%%: CGPA %s/%s, conversion unknown" % (job["min_percent"], p.get("cgpa"), p.get("cgpa_scale")))
        elif float(pct) < float(job["min_percent"]):
            nos.append("marks %s%% below %s%%" % (pct, job["min_percent"]))
    if job.get("age_max") or job.get("age_min"):
        dob, cut = d(p.get("dob")), d(job.get("age_cutoff_date"))
        if not dob or not cut:
            checks.append("age %s-%s on %s: DOB missing" % (job.get("age_min") or "?", job.get("age_max") or "?", job.get("age_cutoff_date") or "?"))
        else:
            age = cut.year - dob.year - ((cut.month, cut.day) < (dob.month, dob.day))
            if job.get("age_max") and age > int(job["age_max"]):
                checks.append("age %d over General limit %s: Yes only with category relaxation" % (age, job["age_max"]))
            if job.get("age_min") and age < int(job["age_min"]):
                nos.append("age %d under %s" % (age, job["age_min"]))
    if job.get("experience") and p.get("fulltime_experience_months") in (0, None):
        if re.search(r"\d", job["experience"]) and not re.search(r"\b0\b|fresher", job["experience"].lower()):
            checks.append("experience asked: " + job["experience"])
    if nos:
        return "No", "; ".join(nos)
    if checks:
        return "Check", "; ".join(checks)
    return "Yes", "meets degree/branch/year rules"


# ---------- commands ----------
def cmd_status():
    ps, jobs, apps = load_profiles(), load_jobs(), read_csv(APPS)
    print("profiles:", len(ps))
    for pid, p in ps.items():
        miss = p.get("missing_inputs") or []
        print("  %s | %s %s | grad %s | missing: %s" % (pid, p.get("degree"), p.get("branch"), p.get("grad_year"), "; ".join(miss) or "none"))
    t = today()
    open_ = [j for j in jobs if d(j["apply_end"]) and d(j["apply_end"]) >= t]
    print("jobs: %d total, %d open (apply_end >= %s), files: %s" % (len(jobs), len(open_), t, [os.path.basename(f) for f in month_files()]))
    print("applications:", len(apps))
    last = max((j["date_found"] for j in jobs), default=None)
    print("last date_found:", last)


def apply_rows(jobs, ps, apps):
    """Create/refresh application rows for every job x candidate. Keeps status."""
    idx = {(a["job_id"], a["candidate_id"]): a for a in apps}
    stamp = today().isoformat()
    for j in jobs:
        for pid, p in ps.items():
            el, why = eligibility(j, p)
            a = idx.get((j["job_id"], pid))
            if a:
                if (a["eligibility"], a["reason"]) != (el, why):
                    a["eligibility"], a["reason"], a["updated"] = el, why, stamp
            elif el != "No":
                a = {"job_id": j["job_id"], "candidate_id": pid, "eligibility": el,
                     "reason": why, "status": "New", "updated": stamp}
                apps.append(a)
                idx[(j["job_id"], pid)] = a
            closed = d(j["apply_end"]) and d(j["apply_end"]) < today()
            if a and closed and a["status"] in ("New", "To apply"):
                a["status"], a["updated"] = "Closed", stamp
    return apps


def save_jobs(jobs):
    by = {}
    for j in jobs:
        p = j.get("_file") or os.path.join(DATA, "Jobs Log %s.csv" % j["date_found"][:7])
        j["_file"] = p
        by.setdefault(p, []).append(j)
    for p, rows in by.items():
        write_csv(p, COLS, rows)


def cmd_add(path):
    with open(path, encoding="utf-8") as f:
        new = json.load(f)
    jobs, ps, apps = load_jobs(), load_profiles(), read_csv(APPS)
    byid = {j["job_id"]: j for j in jobs}
    added = updated = 0
    for r in new:
        r = {k: ("" if v is None else str(v)) for k, v in r.items()}
        miss = [c for c in REQUIRED if not r.get(c)]
        if miss:
            sys.exit("row %r missing %s" % (r.get("post"), miss))
        r["job_id"] = r.get("job_id") or make_id(r)
        if r["job_id"] in byid:
            old = byid[r["job_id"]]
            ch = [c for c in COLS if r.get(c) and r[c] != old.get(c) and c not in ("job_id", "date_found")]
            for c in ch:
                old[c] = r[c]
            if ch:
                old["notes"] = (old.get("notes", "") + " | updated %s: %s" % (today(), ",".join(ch))).strip(" |")
                updated += 1
        else:
            jobs.append(r)
            byid[r["job_id"]] = r
            added += 1
    save_jobs(jobs)
    write_csv(APPS, APP_COLS, apply_rows(jobs, ps, apps))
    print("added %d, updated %d, jobs now %d" % (added, updated, len(jobs)))


def cmd_recheck():
    jobs, ps, apps = load_jobs(), load_profiles(), read_csv(APPS)
    write_csv(APPS, APP_COLS, apply_rows(jobs, ps, apps))
    print("rechecked %d jobs x %d profiles" % (len(jobs), len(ps)))


def cmd_open(days=None):
    t = today()
    rows = [j for j in load_jobs() if d(j["apply_end"]) and d(j["apply_end"]) >= t]
    if days:
        rows = [j for j in rows if (d(j["apply_end"]) - t).days <= days]
    rows.sort(key=lambda j: j["apply_end"])
    apps = read_csv(APPS)
    for j in rows:
        who = ["%s:%s" % (a["candidate_id"], a["eligibility"]) for a in apps if a["job_id"] == j["job_id"]]
        print("%s | %-24s | %s | %s | %s" % (j["apply_end"], j["organisation"][:24], j["post"][:50], j["sector"], ", ".join(who) or "-"))


def cmd_verify():
    errs = []
    seen = set()
    for p in month_files():
        with open(p, "rb") as f:
            raw = f.read()
        if b"\r\n" not in raw:
            errs.append("%s: no CRLF row endings" % os.path.basename(p))
        rows = read_csv(p)
        if rows and list(rows[0].keys()) != COLS:
            errs.append("%s: header differs from COLS" % os.path.basename(p))
        m = re.search(r"(\d{4}-\d{2})\.csv$", p).group(1)
        for r in rows:
            tag = "%s %s" % (os.path.basename(p), r.get("job_id"))
            if r["job_id"] in seen:
                errs.append(tag + ": duplicate job_id")
            seen.add(r["job_id"])
            if not r["date_found"].startswith(m):
                errs.append(tag + ": date_found not in file month")
            for c in REQUIRED:
                if not r.get(c):
                    errs.append(tag + ": empty " + c)
            for c in ("date_found", "apply_start", "apply_end", "exam_date", "age_cutoff_date"):
                if r.get(c) and not DATE_RE.match(r[c]):
                    errs.append(tag + ": %s not YYYY-MM-DD" % c)
            if r["sector"] not in SECTORS:
                errs.append(tag + ": sector %r not in %s" % (r["sector"], SECTORS))
            if r["official_verified"] not in ("Y", "N"):
                errs.append(tag + ": official_verified must be Y or N")
            if r["sector"] != "Private" and r["official_verified"] != "Y":
                errs.append(tag + ": govt/PSU row not verified on the official site")
            if not r["notification_url"].startswith("http"):
                errs.append(tag + ": notification_url not a URL")
    ps = load_profiles()
    for a in read_csv(APPS):
        if a["job_id"] not in seen:
            errs.append("applications: unknown job_id " + a["job_id"])
        if a["candidate_id"] not in ps:
            errs.append("applications: unknown candidate " + a["candidate_id"])
        if a["status"] not in STATUSES:
            errs.append("applications: bad status %r" % a["status"])
    for pid, p in ps.items():
        for k in ("phone", "email", "mobile"):
            if p.get(k):
                errs.append("profile %s: %s must not be stored (public repo)" % (pid, k))
    print("\n".join(errs) if errs else "OK: %d jobs, %d profiles" % (len(seen), len(ps)))
    return not errs


def cmd_xlsx(out):
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter
    jobs, ps, apps = load_jobs(), load_profiles(), read_csv(APPS)
    t = today()
    byid = {j["job_id"]: j for j in jobs}
    wb = Workbook()
    head = Font(bold=True, color="FFFFFF", size=12)
    fill = PatternFill("solid", fgColor="1F4E78")
    body = Font(size=12)
    wrap = Alignment(wrap_text=True, vertical="top")
    colour = {"Yes": "C6EFCE", "Check": "FFEB9C", "No": "FFC7CE"}

    def sheet(ws, cols, rows, widths, link_cols=(), el_col=None):
        ws.append(cols)
        for c in ws[1]:
            c.font, c.fill, c.alignment = head, fill, wrap
        for r in rows:
            ws.append(r)
        for i, w in enumerate(widths, 1):
            ws.column_dimensions[get_column_letter(i)].width = w
        for row in ws.iter_rows(min_row=2):
            for c in row:
                c.font, c.alignment = body, wrap
            for li in link_cols:
                c = row[li]
                if c.value and str(c.value).startswith("http"):
                    c.hyperlink, c.font = c.value, Font(size=12, color="0563C1", underline="single")
            if el_col is not None and row[el_col].value in colour:
                row[el_col].fill = PatternFill("solid", fgColor=colour[row[el_col].value])
        ws.freeze_panes = "A2"
        ws.auto_filter.ref = ws.dimensions

    open_ = sorted([j for j in jobs if d(j["apply_end"]) and d(j["apply_end"]) >= t], key=lambda j: j["apply_end"])
    ws = wb.active
    ws.title = "Open Jobs"
    sheet(ws, ["Apply by", "Days left", "Sector", "Organisation", "Post", "Eligible", "Selection", "Pay", "Location", "Candidates (eligibility)", "Notification", "Apply"],
          [[j["apply_end"], (d(j["apply_end"]) - t).days, j["sector"], j["organisation"], j["post"], j["eligible_degrees"] + (" | " + j["eligible_branches"] if j["eligible_branches"] else ""),
            j["selection_mode"], j["pay"], j["location"],
            "\n".join("%s: %s" % (a["candidate_id"], a["eligibility"]) for a in apps if a["job_id"] == j["job_id"]),
            j["notification_url"], j["apply_url"]] for j in open_],
          [12, 8, 14, 26, 34, 28, 22, 18, 16, 26, 30, 30], link_cols=(10, 11))
    for pid, p in ps.items():
        ws = wb.create_sheet(pid[:31])
        rows = []
        for a in apps:
            if a["candidate_id"] != pid or a["job_id"] not in byid:
                continue
            j = byid[a["job_id"]]
            rows.append([j["apply_end"], j["sector"], j["organisation"], j["post"], a["eligibility"], a["reason"], a["status"], a["updated"], j["notification_url"]])
        rows.sort(key=lambda r: (r[6] in ("Closed", "Skipped", "Rejected"), r[0]))
        sheet(ws, ["Apply by", "Sector", "Organisation", "Post", "Eligibility", "Reason", "Status", "Updated", "Notification"], rows,
              [12, 14, 26, 34, 11, 40, 12, 12, 30], link_cols=(8,), el_col=4)
    ws = wb.create_sheet("All Jobs")
    sheet(ws, COLS, [[j.get(c, "") for c in COLS] for j in sorted(jobs, key=lambda j: j["date_found"], reverse=True)],
          [22] * len(COLS), link_cols=(COLS.index("notification_url"), COLS.index("apply_url")))
    ws = wb.create_sheet("Profiles")
    keys = ["id", "name", "degree", "branch", "institute", "grad_year", "cgpa", "percent_equivalent", "dob", "domicile_state", "gate", "missing_inputs"]
    sheet(ws, keys, [[json.dumps(p.get(k), ensure_ascii=False) if isinstance(p.get(k), (list, dict)) else p.get(k) for k in keys] for p in ps.values()], [18] * len(keys))
    wb.save(out)
    print("saved", out, "| open:", len(open_), "| tabs:", wb.sheetnames)


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        sys.exit(__doc__)
    c = a[0]
    if c == "status":
        cmd_status()
    elif c == "add":
        cmd_add(a[1])
    elif c == "recheck":
        cmd_recheck()
    elif c == "open":
        cmd_open(int(a[a.index("--days") + 1]) if "--days" in a else None)
    elif c == "verify":
        sys.exit(0 if cmd_verify() else 1)
    elif c == "xlsx":
        cmd_xlsx(a[a.index("--out") + 1] if "--out" in a else "Job Tracker %s.xlsx" % today().isoformat())
    else:
        sys.exit(__doc__)
