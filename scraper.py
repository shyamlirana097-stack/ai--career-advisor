import os
import re
import time
from datetime import date
import pandas as pd
import requests
from bs4 import BeautifulSoup

CSV = "data/sources.csv"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
}

JUNK_MARKERS = [
    "captcha", "please solve", "detected malicious", "are you a robot",
    "access denied", "unusual traffic", "request unblock",
    "checking your browser", "enable javascript",
]
COST_TOPICS = {"visa", "tuition", "living"}   # these topics must contain money figures

def clean_filename(url, topic):
    domain = re.sub(r"https?://(www\.)?", "", url).split("/")[0].split(".")[0]
    return f"{topic}_{domain}.txt"

def looks_like_junk(text, topic):
    low = text.lower()
    if any(m in low for m in JUNK_MARKERS):
        return "blocked/captcha page"
    if len(text) < 800:
        return "too short (hub or JS page)"
    if topic in COST_TOPICS:
        currency_hits = len(re.findall(r"€|\$|₹|EUR|USD|CAD|AUD|INR", text))
        if currency_hits == 0:
            return "no money figures (probably a menu page)"
    return None

def scrape_page(url, retries=2):
    for attempt in range(retries + 1):
        try:
            r = requests.get(url, headers=HEADERS, timeout=60)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")
            for tag in soup(["script", "style", "nav", "footer", "header", "form"]):
                tag.decompose()
            return soup.get_text(separator="\n", strip=True)
        except requests.exceptions.Timeout:
            if attempt < retries:
                print(f"  timeout, retrying ({attempt+1})...")
                time.sleep(5)
                continue
            raise

def main():
    df = pd.read_csv(CSV)
    df["date_scraped"] = df["date_scraped"].astype(object)
    ok = junk = failed = 0
    for i, row in df.iterrows():
        if row["refresh_type"] != "weekly":
            continue   # skips 'live' (Phase 4) and 'manual' rows
        try:
            text = scrape_page(row["url"])
            problem = looks_like_junk(text, row["topic"])
            if problem:
                print(f"JUNK [{problem}] -> save manually: {row['url']}")
                junk += 1
                continue
            path = f"data/raw/{row['country']}/{clean_filename(row['url'], row['topic'])}"
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w", encoding="utf-8") as f:
                f.write(f"SOURCE: {row['url']}\nSCRAPED: {date.today()}\n\n{text}")
            df.at[i, "date_scraped"] = str(date.today())
            print(f"SUCCESS: {path}  ({len(text)} chars)")
            ok += 1
        except Exception as e:
            print(f"FAILED: {row['url']} - {e}")
            failed += 1
        time.sleep(3)
    try:
        df.to_csv(CSV, index=False)
    except PermissionError:
        print(f"CSV locked — close Excel and re-run to save {CSV}")
    print(f"\nSummary: {ok} good | {junk} junk (manual save) | {failed} failed")

if __name__ == "__main__":
    main()
