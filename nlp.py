from transformers import pipeline # type: ignore

# Lightweight pretrained models for CPU inference
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
classifier = pipeline("zero-shot-classification", model="valhalla/distilbart-mnli-12-1")

LABELS = ["Urgent", "Work", "Finance", "Newsletter", "Promo", "Personal"]

def summarize(text: str) -> str:
    text = (text or "").strip()
    if not text:
        return "No content."
    # Summarize, limit text length for speed
    out = summarizer(text[:3000], max_length=60, min_length=15, do_sample=False)
    return out[0]["summary_text"].strip()

def classify(subject: str, summary: str) -> dict:
    text = f"Subject: {subject}\n\n{summary}"
    res = classifier(text, candidate_labels=LABELS)
    category = res["labels"][0]
    priority = "High" if category in ("Urgent","Finance") else "Medium"
    return {"category": category, "priority": priority}
