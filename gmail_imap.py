# src/gmail_imap.py
import os, imaplib, email, datetime
from dotenv import load_dotenv

load_dotenv()
USER = os.getenv("SMTP_USER")        # your Gmail address
PASS = os.getenv("SMTP_PASS")        # your Gmail App Password

def fetch_last_24h(max_n=50):
    """Fetch last 24h emails via IMAP using Gmail + App Password"""
    M = imaplib.IMAP4_SSL("imap.gmail.com")
    M.login(USER, PASS)
    M.select("INBOX")

    since = (datetime.datetime.utcnow() - datetime.timedelta(days=1)).strftime("%d-%b-%Y")
    typ, data = M.search(None, f'(SINCE "{since}")')
    ids = data[0].split()
    ids = ids[-max_n:]  # last N

    items = []
    for i in reversed(ids):
        typ, msg_data = M.fetch(i, "(RFC822)")
        raw = msg_data[0][1]
        msg = email.message_from_bytes(raw)

        subject = email.header.decode_header(msg.get("Subject", ""))[0]
        if isinstance(subject[0], bytes):
            subject = subject[0].decode(subject[1] or "utf-8", errors="ignore")
        else:
            subject = subject[0]

        from_ = msg.get("From", "")
        snippet = ""

        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()
                dispo = str(part.get("Content-Disposition"))
                if ctype == "text/plain" and "attachment" not in dispo:
                    payload = part.get_payload(decode=True)
                    if payload:
                        snippet = payload.decode("utf-8", errors="ignore")[:200].replace("\r"," ").replace("\n"," ")
                        break
        else:
            payload = msg.get_payload(decode=True)
            if payload:
                snippet = payload.decode("utf-8", errors="ignore")[:200].replace("\r"," ").replace("\n"," ")

        items.append({"from": from_, "subject": subject, "snippet": snippet})
    M.close()
    M.logout()
    return items
