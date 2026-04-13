from config import KEYWORDS, LOCATIONS, PAY_FILTER, PREFERRED_AGENCIES
from utils import is_recent

def matches_keywords(job):
    text = (job.get("title", "") + " " + job.get("description", "")).lower()
    return any(kw.lower() in text for kw in KEYWORDS)

def matches_location(job):
    loc = (job.get("location") or "").lower()
    return any(city.lower() in loc for city in LOCATIONS)

def matches_pay(job):
    pay = job.get("pay")
    if not pay:
        return False
    try:
        pay_val = float(pay)
    except Exception:
        return False

    # If the pay is more than $500, assume salary. Else hourly
    if pay_val > 500:
        return pay_val >= PAY_FILTER["salary_minimum"]
    
    return pay_val >= PAY_FILTER["hourly_minimum"]

def is_preferred_agency(job):
    company = (job.get("company") or "").lower()
    return any(a.lower() in company for a in PREFERRED_AGENCIES)

def filter_jobs(jobs, sent_ids):
    filtered = []
    for job in jobs:
        if not is_recent(job):
            continue
        if job.get("link") in sent_ids:
            continue
        if not matches_keywords(job):
            continue
        if not matches_location(job):
            continue
        if not matches_pay(job):
            continue
        filtered.append(job)
    return filtered
