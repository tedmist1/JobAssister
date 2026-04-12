from datetime import datetime
from job_sources import get_all_jobs
from filtering import filter_jobs, is_preferred_agency
from utils import load_sent_jobs, save_sent_jobs, job_id
from discord_notify import send_file_to_discord

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
    return out

def main():
    sent_ids = load_sent_jobs()

    jobs = get_all_jobs()
    new_jobs = filter_jobs(jobs, sent_ids)

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
