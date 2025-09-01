import os
import base64
from datetime import datetime, timedelta, timezone
from typing import List, Dict

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Read-only scope is enough for fetching emails
SCOPES = ["https://www.googleapis.com/auth/gmail.readonly"]

TOKEN_PATH = "token.json"
CREDENTIALS_PATH = "credentials.json"

def get_gmail_service():
    creds = None
    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            from google.auth.transport.requests import Request
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_PATH, SCOPES)
            creds = flow.run_local_server(port=0)  # opens browser for consent
        with open(TOKEN_PATH, "w") as token:
            token.write(creds.to_json())
    return build("gmail", "v1", credentials=creds)

def _rfc3339(dt: datetime) -> str:
    # Gmail accepts seconds; ensure UTC
    return dt.astimezone(timezone.utc).isoformat()

def fetch_last_24h(max_n: int = 50) -> List[Dict]:
    """Return a list of basic email data from the last 24h."""
    service = get_gmail_service()
    now = datetime.now(timezone.utc)
    since = now - timedelta(hours=24)

    # Gmail query: newer_than is simpler, but we’ll use after: with epoch for precision
    query = f"after:{int(since.timestamp())}"

    res = service.users().messages().list(userId="me", q=query, maxResults=max_n).execute()
    messages = res.get("messages", [])
    items = []

    for m in messages:
        msg = service.users().messages().get(userId="me", id=m["id"], format="full").execute()
        headers = {h["name"].lower(): h["value"] for h in msg.get("payload", {}).get("headers", [])}
        subject = headers.get("subject", "(no subject)")
        frm = headers.get("from", "(unknown)")
        snippet = msg.get("snippet", "")

        # Try to decode plain/text body if present
        body_text = ""
        payload = msg.get("payload", {})
        parts = payload.get("parts", [])
        if parts:
            for part in parts:
                if part.get("mimeType") == "text/plain":
                    data = part.get("body", {}).get("data")
                    if data:
                        body_text = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
                        break
        else:
            # Sometimes body is at top-level
            data = payload.get("body", {}).get("data")
            if data:
                body_text = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")

        items.append({
            "id": m["id"],
            "from": frm,
            "subject": subject,
            "snippet": snippet,
            "body_text": body_text
        })
    return items
