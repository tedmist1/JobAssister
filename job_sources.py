import os
import requests
from utils import parse_date, extract_years_experience

from config import KEYWORDS, LOCATIONS, GREENHOUSE_COMPANIES, LEVER_COMPANIES

def normalize_job(title, company, location, pay, description, link, source, posted_at, id):

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
        "id": id
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
                # print("ID:", job.get("id"))
                # print("SNIPPET:", job.get("description"))
                # print("FULL:", (full_description or "")[:400])
                # print("LEN FULL:", len(full_description or ""))


                # fall back to snippet if detail failed
                description = full_description or job.get("description") or ""

                location = job.get("location", {}).get("display_name")
                if location and "," in location:
                    location = location.split(",")[0].strip()

                link = job.get("redirect_url")

                results.append(normalize_job(
                    id=job_id,
                    title=job.get("title"),
                    company=job.get("company", {}).get("display_name"),
                    location=location,
                    pay=job.get("salary_min"),
                    description=description,
                    link=link,
                    source="Adzuna",
                    posted_at=job.get("created")
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
                id=job.get("MatchedObjectId"),
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


def query_indeed():
    results = []
    base_url = "https://indeed-indeed.p.rapidapi.com/search"  # unofficial API

    headers = {
        "X-RapidAPI-Key": os.getenv("RAPIDAPI_KEY"),
        "X-RapidAPI-Host": "indeed-indeed.p.rapidapi.com"
    }

    for kw in KEYWORDS:
        for loc in LOCATIONS:
            params = {
                "query": kw,
                "location": loc,
                "page": 1
            }

            r = requests.get(base_url, headers=headers, params=params, timeout=15)
            if r.status_code != 200:
                continue

            for job in r.json().get("data", []):
                description = job.get("description") or ""
                job_id = job.get("jobkey")

                location = job.get("location")
                if location and "," in location:
                    location = location.split(",")[0].strip()

                results.append(normalize_job(
                    id=job_id,
                    title=job.get("title"),
                    company=job.get("company"),
                    location=location,
                    pay=job.get("salary"),
                    description=description,
                    link=job.get("url"),
                    source="Indeed",
                    posted_at=job.get("date"),
                    experience=extract_years_experience(description)
                ))

    return results

def query_greenhouse():
    results = []

    for company in GREENHOUSE_COMPANIES:
        url = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs"

        try:
            r = requests.get(url, timeout=15)
            if r.status_code != 200:
                continue
        except:
            continue

        for job in r.json().get("jobs", []):
            description = job.get("content") or ""
            job_id = job.get("id")

            location = job.get("location", {}).get("name")
            if location and "," in location:
                location = location.split(",")[0].strip()

            results.append(normalize_job(
                id=job_id,
                title=job.get("title"),
                company=company.capitalize(),
                location=location,
                pay=None,
                description=description,
                link=job.get("absolute_url"),
                source="Greenhouse",
                posted_at=job.get("updated_at"),
                experience=extract_years_experience(description)
            ))

    return results

def query_lever():
    results = []

    for company in LEVER_COMPANIES:
        url = f"https://api.lever.co/v0/postings/{company}?mode=json"

        try:
            r = requests.get(url, timeout=15)
            if r.status_code != 200:
                continue
        except:
            continue

        for job in r.json():
            description = job.get("description") or ""
            job_id = job.get("id")

            location = job.get("categories", {}).get("location")
            if location and "," in location:
                location = location.split(",")[0].strip()

            results.append(normalize_job(
                id=job_id,
                title=job.get("text"),
                company=company.capitalize(),
                location=location,
                pay=None,
                description=description,
                link=job.get("hostedUrl"),
                source="Lever",
                posted_at=job.get("createdAt"),
                experience=extract_years_experience(description)
            ))

    return results


def query_linkedin_proxy():
    # LinkedIn jobs come from ATS systems
    return query_greenhouse() + query_lever()


# =========================
# STUBS FOR FUTURE SOURCES
# =========================


def get_all_jobs():
    jobs = []
    jobs += query_adzuna()
    jobs += query_usajobs()
    jobs += query_linkedin_proxy()
    jobs += query_indeed()
    return jobs