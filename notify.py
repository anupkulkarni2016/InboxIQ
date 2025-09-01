# src/notify.py
import os
import smtplib
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

def _get_mail_config():
    """Read mail settings from .env and do basic sanity checks."""
    cfg = {
        "enabled": os.getenv("EMAIL_ENABLED", "false").lower() == "true",
        "server":  os.getenv("SMTP_SERVER", "smtp.gmail.com").strip(),
        "port":    int(os.getenv("SMTP_PORT", "465")),
        "user":    os.getenv("SMTP_USER", "").strip(),
        "pass":    os.getenv("SMTP_PASS", "").strip(),
        "to":      os.getenv("EMAIL_TO", "").strip(),
    }
    if not cfg["to"]:
        cfg["to"] = cfg["user"]
    return cfg

def send_email(subject: str, body: str):
    """Send a plain-text email."""
    cfg = _get_mail_config()
    if not cfg["enabled"]:
        print("Email disabled; skipping.")
        return

    print(f"[MAIL] server={cfg['server']} port={cfg['port']} user={cfg['user']}")

    msg = MIMEText(body, _charset="utf-8")
    msg["Subject"] = subject
    msg["From"] = cfg["user"]
    msg["To"] = cfg["to"]

    # Try implicit SSL (e.g., Gmail 465), then STARTTLS (587)
    try:
        with smtplib.SMTP_SSL(cfg["server"], cfg["port"], timeout=20) as s:
            s.login(cfg["user"], cfg["pass"])
            s.send_message(msg)
        print(f"✅ Digest emailed to {cfg['to']} via SSL")
        return
    except (socket.gaierror, OSError, smtplib.SMTPException) as e:
        print(f"[MAIL] SSL failed: {e}. Trying STARTTLS on 587...")

    try:
        with smtplib.SMTP(cfg["server"], 587, timeout=20) as s:
            s.ehlo()
            s.starttls()
            s.login(cfg["user"], cfg["pass"])
            s.send_message(msg)
        print(f"✅ Digest emailed to {cfg['to']} via STARTTLS")
    except Exception as e:
        print(f"❌ Email failed over both SSL and STARTTLS: {e}")

def send_email_html(subject: str, html_body: str, text_fallback: str = ""):
    """Send an HTML email with a plain-text fallback."""
    cfg = _get_mail_config()
    if not cfg["enabled"]:
        print("Email disabled; skipping.")
        return

    print(f"[MAIL HTML] server={cfg['server']} port={cfg['port']} user={cfg['user']}")

    if not text_fallback:
        text_fallback = "Your daily email digest is attached as HTML."

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = cfg["user"]
    msg["To"] = cfg["to"]

    # Attach plain-text part first, then HTML part
    msg.attach(MIMEText(text_fallback, "plain", _charset="utf-8"))
    msg.attach(MIMEText(html_body, "html", _charset="utf-8"))

    # Try implicit SSL then STARTTLS
    try:
        with smtplib.SMTP_SSL(cfg["server"], cfg["port"], timeout=20) as s:
            s.login(cfg["user"], cfg["pass"])
            s.send_message(msg)
        print(f"✅ HTML digest emailed to {cfg['to']} via SSL")
        return
    except (socket.gaierror, OSError, smtplib.SMTPException) as e:
        print(f"[MAIL HTML] SSL failed: {e}. Trying STARTTLS on 587...")

    try:
        with smtplib.SMTP(cfg["server"], 587, timeout=20) as s:
            s.ehlo()
            s.starttls()
            s.login(cfg["user"], cfg["pass"])
            s.send_message(msg)
        print(f"✅ HTML digest emailed to {cfg['to']} via STARTTLS")
    except Exception as e:
        print(f"❌ HTML email failed over both SSL and STARTTLS: {e}")
