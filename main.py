from datetime import datetime
from job_sources import get_all_jobs
from filtering import filter_jobs, is_preferred_agency
from utils import load_sent_jobs, save_sent_jobs, job_id
from discord_notify import send_file_to_discord
from dotenv import load_dotenv

load_dotenv()


def build_markdown(jobs):
    today = datetime.utcnow().strftime("%Y-%m-%d")
    lines = [f"# Weekly AWS/Terraform Job Report — {today}", ""]

    preferred = [j for j in jobs if is_preferred_agency(j)]
    others = [j for j in jobs if not is_preferred_agency(j)]

    if preferred:
        lines.append("## Preferred Agencies")
        lines.append("")
        for job in preferred:
            lines.extend(format_job(job, highlight=True))
            lines.append("")

    if others:
        lines.append("## Other Matches")
        lines.append("")
        for job in others:
            lines.extend(format_job(job))
            lines.append("")

    if not jobs:
        lines.append("_No matching jobs this week._")

    return "\n".join(lines)

def format_job(job, highlight=False):
    star = "⭐ " if highlight else ""
    title = job.get("title") or "Untitled"
    company = job.get("company") or "Unknown"
    location = job.get("location") or "Unknown"
    pay = job.get("pay") or "N/A"
    source = job.get("source") or "Unknown"
    link = job.get("link") or ""

    out = [
        f"### {star}{title} — {company}",
        f"- **Location:** {location}",
        f"- **Pay:** {pay}",
        f"- **Source:** {source}",
    ]
    if link:
        out.append(f"- **Link:** {link}")
    if job.get("experience"):
        out.append(f"- **Experience:** {job['experience']}")
    
    if job.get("description"):
        out.append(f"- **Description:** {job['description']}")

    return out

def dedupe_jobs(jobs):
    seen = set()
    unique = []

    for job in jobs:
        key = job.get("id")  or job.get("link") # stable unique identifier
        if key and key not in seen:
            seen.add(key)
            unique.append(job)

    return unique

def main():

    sent_ids = load_sent_jobs()

    jobs = get_all_jobs()
    jobs = dedupe_jobs(jobs)

    # DEBUG: Write all jobs to a markdown file before filtering
    debug_md = ["# ALL RAW JOBS (Before Filtering)\n"]

    for job in jobs:
        debug_md.append(f"## {job.get('title')}")
        debug_md.append(f"- **Source:** {job.get('source')}")
        debug_md.append(f"- **Company:** {job.get('company')}")
        debug_md.append(f"- **Location:** {job.get('location')}")
        debug_md.append(f"- **Posted:** {job.get('posted_at')}")
        debug_md.append(f"- **Experience:** {job.get('experience')}")
        debug_md.append(f"- **Link:** {job.get('link')}")
        debug_md.append(f"\n**Description:**\n{job.get('description')[:500]}...\n")
        debug_md.append("---\n")

    with open("ALL_JOBS_DEBUG.md", "w", encoding="utf-8") as f:
        f.write("\n".join(debug_md))

    
    new_jobs = filter_jobs(jobs, sent_ids)

    # DEBUG: counts after filtering
    # filtered_counts = Counter(job.get("source") for job in new_jobs)
    # print("Filtered source counts:", filtered_counts)

    for job in new_jobs:
        sent_ids.add(job_id(job))
    save_sent_jobs(sent_ids)

    today_str = datetime.utcnow().strftime("%Y_%m_%d")
    filename = f"jobs_{today_str}.md"
    md = build_markdown(new_jobs)

    with open(filename, "w", encoding="utf-8") as f:
        f.write(md)

    send_file_to_discord(filename, md)

if __name__ == "__main__":
    main()
