# discord_notify.py

import requests
from config import DISCORD_WEBHOOK_URL

def send_file_to_discord(filename, content):
    if not DISCORD_WEBHOOK_URL:
        print("No webhook set.")
        return

    files = {
        "file": (filename, content.encode("utf-8"), "text/markdown")
    }
    data = {
        "content": f"Weekly job report generated: `{filename}`"
    }

    resp = requests.post(DISCORD_WEBHOOK_URL, data=data, files=files, timeout=30)
    if resp.status_code >= 300:
        print("Discord error:", resp.status_code, resp.text)
