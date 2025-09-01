import os, getpass, re
TPL = """EMAIL_ENABLED=true
SMTP_SERVER={server}
SMTP_PORT={port}
SMTP_USER={user}
SMTP_PASS={app}
EMAIL_TO={to}
HF_HOME=
TELEGRAM_ENABLED=false
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
"""

def prompt(default, label, secret=False):
    v = getpass.getpass(label+": ") if secret else input(label+f" [{default}]: ")
    return v.strip() or default

def main():
    print("=== Smart Inbox Setup Wizard ===")
    if os.path.exists(".env"):
        print(".env already exists. Aborting.")
        return
    user = input("Your Gmail address: ").strip()
    while not re.match(r".+@.+\..+", user):
        user = input("Enter a valid email: ").strip()
    app = getpass.getpass("Your 16-char Gmail App Password (no spaces): ").strip()
    server = prompt("smtp.gmail.com", "SMTP server")
    port = prompt("465", "SMTP port")
    to = prompt(user, "Send digest to")
    with open(".env", "w", encoding="utf-8") as f:
        f.write(TPL.format(server=server, port=port, user=user, app=app, to=to))
    print("Wrote .env — you're ready. Run: python src/main.py")

if __name__ == "__main__":
    main()
