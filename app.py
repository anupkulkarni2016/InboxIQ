# app.py — Smart Inbox Dashboard (Trends + Filters)
import os
import pandas as pd
import streamlit as st

st.set_page_config(page_title="Smart Inbox Dashboard", layout="wide")
st.title("📬 Smart Inbox AI Dashboard")

@st.cache_data
def load_history(path="history.csv"):
    if not os.path.exists(path):
        return None
    df = pd.read_csv(path)
    # normalize
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.date
    for col in ["from", "subject", "category", "priority", "summary"]:
        if col in df.columns:
            df[col] = df[col].astype(str)
    return df

df = load_history()
if df is None or df.empty:
    st.warning("No history yet. Run `python src/main.py` at least once to generate history.csv.")
    st.stop()

# ------------------ Sidebar Filters ------------------
with st.sidebar:
    st.header("Filters")
    dates = sorted(df["date"].dropna().unique())
    start_default = dates[0] if dates else None
    end_default = dates[-1] if dates else None
    date_range = st.date_input("Date range", value=(start_default, end_default))
    cats = sorted(df["category"].dropna().unique())
    sel_cats = st.multiselect("Categories", cats, default=cats)
    prios = ["High","Medium","Low"]
    sel_prios = st.multiselect("Priority", prios, default=prios)
    q = st.text_input("Search (subject/summary contains)")

# Apply filters
f = df.copy()
if isinstance(date_range, tuple) and len(date_range) == 2:
    start, end = date_range
    if start and end:
        f = f[(f["date"] >= start) & (f["date"] <= end)]
if sel_cats:
    f = f[f["category"].isin(sel_cats)]
if sel_prios:
    f = f[f["priority"].isin(sel_prios)]
if q:
    ql = q.lower()
    f = f[f["subject"].str.lower().str.contains(ql) | f["summary"].str.lower().str.contains(ql)]

# ------------------ KPI Row ------------------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Emails (filtered)", len(f))
c2.metric("Days covered", f["date"].nunique())
c3.metric("Top category", f["category"].value_counts().idxmax() if not f.empty else "—")
c4.metric("High priority", (f["priority"] == "High").sum())

st.divider()

# ------------------ Trends ------------------
colA, colB = st.columns(2, vertical_alignment="top")

# Emails per day
daily = f.groupby("date").size().rename("emails").reset_index()
with colA:
    st.subheader("📈 Emails per day")
    if daily.empty:
        st.info("No data in this date range.")
    else:
        st.line_chart(daily.set_index("date"))

# Categories over time (stacked area via pivot)
cat_daily = f.pivot_table(index="date", columns="category", values="subject", aggfunc="count", fill_value=0)
with colB:
    st.subheader("📊 Categories over time")
    if cat_daily.empty:
        st.info("No data in this date range.")
    else:
        st.area_chart(cat_daily)

st.divider()

# ------------------ Top senders ------------------
senders = (
    f.assign(sender=f["from"].str.replace(r"<.*?>", "", regex=True).str.strip())
     .groupby("sender").size().sort_values(ascending=False).head(10)
     .rename("count").reset_index()
)
st.subheader("🏷️ Top senders (filtered)")
if senders.empty:
    st.info("No senders to show.")
else:
    st.bar_chart(senders.set_index("sender"))

# ------------------ Table + Download ------------------
st.subheader("🧾 Recent emails (filtered)")
st.dataframe(
    f.sort_values(["date"], ascending=[False]).loc[:, ["date","from","subject","category","priority","summary"]].head(200),
    use_container_width=True,
)

st.download_button(
    "⬇️ Download filtered CSV",
    data=f.to_csv(index=False).encode("utf-8"),
    file_name="smart_inbox_filtered.csv",
    mime="text/csv",
)
