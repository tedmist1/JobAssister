# discord_notify.py

import requests
from config import DISCORD_WEBHOOK_URL

def send_file_to_discord(filename, content):
    if not DISCORD_WEBHOOK_URL:
        print("No webhook set.")
        return

    MENTION_USER_ID = os.getenv("DISCORD_USER_ID")
    files = {
        "file": (filename, content.encode("utf-8"), "text/markdown")
    }
    data = {
        "content": f"<@{MENTION_USER_ID}> Weekly job report generated: `{filename}`"
    }
    
    143599694810054657

    resp = requests.post(DISCORD_WEBHOOK_URL, data=data, files=files, timeout=30)
    if resp.status_code >= 300:
        print("Discord error:", resp.status_code, resp.text)
