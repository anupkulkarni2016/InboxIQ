# Inbox IQ

InboxIQ is an end-to-end Python project that helps fight email overload.  
It automatically fetches your emails, summarizes them with NLP, classifies them by category & priority, and delivers a **daily digest** (styled HTML email).  
It also provides a Streamlit dashboard with filters, trends, and insights.

---

## Features

-  **Email Fetching (IMAP)** – securely fetches your emails  
-  **NLP Summarization** – Hugging Face Transformers condense long messages  
-  **Classification** – tags emails by category & urgency (High / Medium / Low)  
-  **Interactive Dashboard** – explore email trends with Streamlit  
-  **Daily HTML Digest** – clean, styled summary delivered to your inbox  
-  **Automation Ready** – run daily with Task Scheduler (Windows)  

---

## Quick Start

1. Clone repo & set up venv
```powershell
git clone https://github.com/<your-username>/smart-inbox.git
cd smart-inbox
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt

Note - ⚠️ To use Gmail/Google APIs, download your own credentials.json from Google Cloud Console and place it in the project root. This file should never be committed to GitHub
