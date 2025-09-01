# src/main.py
from gmail_imap import fetch_last_24h   # if you're using IMAP
from notify import send_email_html
# from gmail_client import fetch_last_24h  # use this instead if you fixed OAuth
from nlp import summarize, classify

import csv, os, datetime as dt

def append_history(items, path="history.csv"):
    new_rows = []
    today = dt.date.today().isoformat()
    for it in items:
        new_rows.append([
            today,
            it.get("from",""),
            it.get("subject",""),
            it.get("category",""),
            it.get("priority",""),
            (it.get("summary","") or "").replace("\n"," ").strip()
        ])
    header = ["date","from","subject","category","priority","summary"]
    file_exists = os.path.exists(path)
    with open(path, "a", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        if not file_exists:
            w.writerow(header)
        w.writerows(new_rows)

def build_digest(items):
    counts = {}
    for it in items:
        counts[it["category"]] = counts.get(it["category"], 0) + 1
    lines = []
    lines.append(f"📬 Daily Email Digest ({len(items)} emails in last 24h)")
    if counts:
        lines.append("By category: " + ", ".join(f"{k}: {v}" for k,v in counts.items()))
    lines.append("")
    # Top 5 by priority
    priority_rank = {"High": 0, "Medium": 1, "Low": 2}
    top = sorted(items, key=lambda x: priority_rank.get(x["priority"], 3))[:5]
    for i, it in enumerate(top, 1):
        lines.append(f"{i}. [{it['priority']}] {it['category']} — {it['subject']}")
        lines.append(f"   {it['summary']}")
    return "\n".join(lines)

def build_html_digest(items, title="Daily Email Digest (last 24h)"):
    # Count by category
    counts = {}
    for it in items:
        counts[it["category"]] = counts.get(it["category"], 0) + 1

    # Simple inline styles for broad email client support
    css = """
      body{font-family:Arial,Helvetica,sans-serif;margin:0;padding:24px;background:#f6f7fb;}
      .card{max-width:720px;margin:0 auto;background:#ffffff;border:1px solid #e9ecf1;border-radius:12px;overflow:hidden;}
      .hdr{background:#0b5fff;color:white;padding:16px 20px;font-size:18px;font-weight:700;}
      .meta{padding:12px 20px;color:#344054;font-size:14px;border-bottom:1px solid #eef1f6;}
      .chip{display:inline-block;background:#eef2ff;color:#334155;padding:3px 10px;border-radius:16px;margin-right:8px;margin-bottom:6px;font-size:12px;}
      .item{padding:14px 20px;border-bottom:1px solid #f1f4f9;}
      .prio{font-weight:700;margin-right:6px}
      .cat{color:#475569;margin-right:8px}
      .subj{font-weight:600;color:#111827}
      .sum{color:#334155;margin-top:6px}
      .ft{padding:14px 20px;color:#6b7280;font-size:12px;}
    """

    # Top 8 by priority
    rank = {"High":0,"Medium":1,"Low":2}
    top = sorted(items, key=lambda x: rank.get(x["priority"],3))[:8]

    # Chips for counts
    chips = "".join(f'<span class="chip">{k}: {v}</span>' for k,v in counts.items())

    # Items list
    rows = []
    for it in top:
        rows.append(f"""
          <div class="item">
            <div><span class="prio">[{it['priority']}]</span>
                 <span class="cat">{it['category']}</span>
                 <span class="subj">{(it.get('subject') or '(no subject)')}</span></div>
            <div class="sum">{(it.get('summary') or '').replace('<','&lt;').replace('>','&gt;')}</div>
          </div>
        """)
    rows_html = "\n".join(rows) if rows else '<div class="item">No emails found.</div>'

    return f"""
    <html>
      <head><meta charset="utf-8"><style>{css}</style></head>
      <body>
        <div class="card">
          <div class="hdr">{title}</div>
          <div class="meta">{chips or 'No categories'}</div>
          {rows_html}
          <div class="ft">Generated automatically by Smart Inbox · {len(items)} emails scanned</div>
        </div>
      </body>
    </html>
    """


def main():
    emails = fetch_last_24h(max_n=10)
    print(f"Fetched {len(emails)} emails in last 24h:\n")

    enriched = []
    for e in emails:
        text = e.get("body_text") or e.get("snippet") or e.get("subject") or ""
        s = summarize(text)
        lab = classify(e.get("subject",""), s)
        enriched.append({
            **e,
            "summary": s,
            "category": lab["category"],
            "priority": lab["priority"]
        })

    digest = build_digest(enriched)
    print(digest)

    with open("digest.txt", "w", encoding="utf-8") as f:
        f.write(digest)
        # Save to history CSV
    append_history(enriched)
        # Build & send HTML email
    html = build_html_digest(enriched, title="📬 Daily Email Digest (last 24h)")
    send_email_html("Daily Email Digest (last 24h)", html, text_fallback=digest)    

if __name__ == "__main__":
    main()
