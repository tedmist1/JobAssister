import os
import requests
from utils import parse_date, extract_years_experience

from config import KEYWORDS, LOCATIONS

def normalize_job(title, company, location, pay, description, link, source, posted_at, job_id):

    experience = extract_years_experience(description)
    return {
        "title": title,
        "company": company,
        "location": location,
        "pay": pay,
        "description": description,
        "link": link,
        "source": source,
        "posted_at": posted_at,
        "experience": experience,
        "id": job_id
    }

def query_adzuna():
    APP_ID = os.getenv("ADZUNA_APP_ID")
    APP_KEY = os.getenv("ADZUNA_APP_KEY")
    if not APP_ID or not APP_KEY:
        return []

    results = []
    search_url = "https://api.adzuna.com/v1/api/jobs/us/search/1"
    detail_url_base = "https://api.adzuna.com/v1/api/jobs/us/"

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

            r = requests.get(search_url, params=params, timeout=15)
            if r.status_code != 200:
                continue

            for job in r.json().get("results", []):
                job_id = job.get("id")  # <-- only this

                full_description = None
                if job_id:
                    detail_params = {
                        "app_id": APP_ID,
                        "app_key": APP_KEY,
                        "content-type": "application/json"
                    }
                    detail_url = f"{detail_url_base}{job_id}"

                    try:
                        detail_resp = requests.get(detail_url, params=detail_params, timeout=10)
                        if detail_resp.status_code == 200:
                            full_description = detail_resp.json().get("description")
                    except Exception:
                        pass

                # DEBUG PRINTS
                print("ID:", job.get("id"))
                print("SNIPPET:", job.get("description"))
                print("FULL:", (full_description or "")[:400])
                print("LEN FULL:", len(full_description or ""))


                # fall back to snippet if detail failed
                description = full_description or job.get("description") or ""

                location = job.get("location", {}).get("display_name")
                if location and "," in location:
                    location = location.split(",")[0].strip()

                link = job.get("redirect_url")

                results.append(normalize_job(
                    title=job.get("title"),
                    company=job.get("company", {}).get("display_name"),
                    location=location,
                    pay=job.get("salary_min"),
                    description=description,
                    link=link,
                    source="Adzuna",
                    posted_at=job.get("created"),
                    id=job.get("MatchedObhectId")
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
            results.append(normalize_job(
                title=item.get("PositionTitle"),
                company=item.get("OrganizationName"),
                location=item.get("PositionLocationDisplay"),
                pay=pay_info.get("MinimumRange"),
                description=item.get("UserArea", {}).get("Details", {}).get("JobSummary"),
                link=item.get("ApplyURI", [""])[0],
                source="USAJobs",
                posted_at=item.get("PublicationStartDate")
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