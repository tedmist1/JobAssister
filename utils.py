import json
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path
from config import SENT_JOBS_FILE, DAYS_BACK

def load_sent_jobs():
    path = Path(SENT_JOBS_FILE)
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

def save_sent_jobs(sent_ids):
    with open(SENT_JOBS_FILE, "w", encoding="utf-8") as f:
        json.dump(sorted(list(sent_ids)), f)

def job_id(job):
    link = job.get("link")
    if link:
        return link
    return f"{job.get('title','')}::{job.get('company','')}"

def parse_date(date_str):
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str.replace("Z", ""))
    except Exception:
        return None

def is_recent(job):
    posted = job.get("posted_at")
    if not posted:
        return False

    try:
        dt = datetime.fromisoformat(posted.replace("Z", "+00:00"))
    except:
        return False

    # Make dt naive so it matches datetime.utcnow()
    dt = dt.replace(tzinfo=None)

    now = datetime.utcnow()
    return dt >= now - timedelta(days=DAYS_BACK)


def extract_years_experience(text):
    if not text:
        return None

    # catches: "3+ years", "3 years", "3 yrs", "3-5 years"
    match = re.search(r'(\d+)\s*(\+|to|-)?\s*(\d+)?\s*(years|yrs)(\sof experience)?', text.lower())
    if match:
        return match.group(0)
    return 