import os

KEYWORDS = [
    "AWS", "Terraform", "Cloud", "DevOps", "Python",
    "Infrastructure", "Landing Zone", "Control Tower"
]

LOCATIONS = ["San Diego", "Remote", "Remote-US"]

PAY_FILTER = {
    "hourly_minimum": 60,     # $90/hr minimum for contract roles
    "salary_minimum": 80000
}

PREFERRED_AGENCIES = [
    "CRB Workforce", "Insight Global", "Motion Recruitment",
    "TEKsystems", "Apex Systems", "Randstad", "Robert Half"
]

DAYS_BACK = 7  # Only consider jobs posted in last N days

# Discord webhook is stored as an environment variable
import os
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# File for tracking previously sent jobs
SENT_JOBS_FILE = "sent_jobs.json"


GREENHOUSE_COMPANIES = [
    "twilio",
    "stripe",
    "datadog",
    "snowflake",
    "cloudflare",
    "hashicorp",
    "aws",
    "microsoft",
    "google",
]

LEVER_COMPANIES = [
    "netflix",
    "robinhood",
    "brex",
    "ramp",
    "openai",
    "scaleai",
    "databricks",
]