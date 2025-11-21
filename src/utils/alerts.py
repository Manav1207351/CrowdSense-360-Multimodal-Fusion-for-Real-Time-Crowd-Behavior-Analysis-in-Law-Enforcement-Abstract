# src/utils/alerts.py
import requests, json, os
from pathlib import Path

def post_alert_http(endpoint, payload, api_key=None, image_path=None):
    headers = {}
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    files = {}
    if image_path and Path(image_path).exists():
        files["image"] = open(image_path, "rb")
    try:
        r = requests.post(endpoint, json=payload, headers=headers, files=files if files else None, timeout=8)
        return r.status_code == 200
    except Exception as e:
        print("post_alert_http failed:", e)
        return False
