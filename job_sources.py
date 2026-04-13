import os
import requests
from utils import parse_date, extract_years_experience

from config import KEYWORDS, LOCATIONS

def normalize_job(title, company, location, pay, description, link, source, posted_at, experience):
    return {
        "title": title,
        "company": company,
        "location": location,
        "pay": pay,
        "description": description,
        "link": link,
        "source": source,
        "posted_at": posted_at,
        "experience": experience
    }

def query_adzuna():
    APP_ID = os.getenv("ADZUNA_APP_ID")
    APP_KEY = os.getenv("ADZUNA_APP_KEY")
    if not APP_ID or not APP_KEY:
            return []

    results = []
    base_url = "https://api.adzuna.com/v1/api/jobs/us/search/1"

    for kw in KEYWORDS:
        for loc in LOCATIONS:
            params = {
                "app_id": APP_ID,
                "app_key": APP_KEY,
                "results_per_page": 50,
                "what": kw,
                "where": loc,
                "content-type": "application/json"
            }
            r = requests.get(base_url, params=params, timeout=15)
            if r.status_code != 200:
                continue

            
            for job in r.json().get("results", []):

                job_description = job.get("description")

                results.append(normalize_job(
                    title=job.get("title"),
                    company=job.get("company", {}).get("display_name"),
                    location=job.get("location", {}).get("display_name"),
                    pay=job.get("salary_min"),
                    description=job_description,
                    link=job.get("redirect_url"),
                    source="Adzuna",
                    posted_at=job.get("created"),
                    experience=extract_years_experience(job_description)
                ))
    return results

# =========================
# USAJOBS
# =========================

def query_usajobs():
    API_KEY = os.getenv("USAJOBS_API_KEY")
    EMAIL = os.getenv("USAJOBS_EMAIL")
    if not API_KEY or not EMAIL:
        return []

    results = []
    base_url = "https://data.usajobs.gov/api/search"

    headers = {
        "User-Agent": EMAIL,
        "Authorization-Key": API_KEY
    }

    for kw in KEYWORDS:
        params = {"Keyword": kw, "ResultsPerPage": 50}
        r = requests.get(base_url, headers=headers, params=params, timeout=15)
        if r.status_code != 200:
            continue

        for job in r.json().get("SearchResult", {}).get("SearchResultItems", []):
            item = job.get("MatchedObjectDescriptor", {})
            pay_info = item.get("PositionRemuneration", [{}])[0]

            job_description=item.get("UserArea", {}).get("Details", {}).get("JobSummary")
            results.append(normalize_job(
                title=item.get("PositionTitle"),
                company=item.get("OrganizationName"),
                location=item.get("PositionLocationDisplay"),
                pay=pay_info.get("MinimumRange"),
                description=job_description,
                link=item.get("ApplyURI", [""])[0],
                source="USAJobs",
                posted_at=item.get("PublicationStartDate"),
                experience=extract_years_experience(job_description)
            ))
    return results

# =========================
# STUBS FOR FUTURE SOURCES
# =========================

def query_ziprecruiter():
    return []

def query_dice():
    return []

def get_all_jobs():
    jobs = []
    jobs += query_adzuna()
    jobs += query_usajobs()
    jobs += query_ziprecruiter()
    jobs += query_dice()
    return jobs