#!/usr/bin/env python3
"""
ACA Find-a-Camp crawler — American Camp Association accredited camp database.

The ACA finder (https://find.acacamps.org/) is server-side PHP: each camp has a
session-free profile at camp_profile.php?camp_id=N. Enumerating camp_id 1..MAX_ID
yields the full accredited-camp directory with name, street address, city, state,
zip, phone, email, website, and program type.

v44 used this to reach the 5,000-camp milestone: 5,427 valid profiles were
extracted; 138 were selected (thin states first, then round-robin across all 51
states) to hit exactly 5,000 total.

Usage:
    python3 scrapers/aca_finder_crawl.py [max_id]   # writes JSONL to stdout-ish

Output is a JSONL stream: {"camp_id": N, "name": ..., "location": ...,
"phone": ..., "email": ..., "website": ..., "type": ...}

NOTE: 8 parallel workers. Be polite to the server (this is a public directory
crawl, one request per camp). Re-run only when you need a fresh snapshot.
"""
import json
import re
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = "https://find.acacamps.org/camp_profile.php?camp_id={}"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
DEFAULT_MAX = 5900
WORKERS = 8


def fetch(camp_id, timeout=30):
    req = urllib.request.Request(BASE.format(camp_id), headers={"User-Agent": UA})
    return urllib.request.urlopen(req, timeout=timeout).read().decode("utf-8", "ignore")


def parse_profile(html, camp_id):
    """Extract name/location/phone/email/website/type from a profile page."""
    if "Oops" in html[:3000]:
        return None
    m = re.search(r"<title>([^<]+?)\s*\|", html)
    if not m:
        return None
    name = m.group(1).strip()
    loc = None
    lm = re.search(r"Location\s*(.*?)(?:View Map)", html, re.S)
    if lm:
        t = re.sub(r"<[^>]+>", " ", lm.group(1))
        t = re.sub(r"\s+", " ", t).strip()
        if t:
            loc = t
    phone = re.search(r"(\d{3}[-.)\s]\d{3}[-.)\s]\d{4})", html)
    email = re.search(r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})", html)
    web = re.search(r'href="(https?://(?!find\.acacamps|www\.acacamps)[^"]+)"', html)
    tm = re.search(r"Type:\s*([A-Za-z &]+)", html)
    return {
        "camp_id": camp_id,
        "name": name,
        "location": loc,
        "phone": phone.group(1) if phone else None,
        "email": email.group(1) if email else None,
        "website": web.group(1) if web else None,
        "type": tm.group(1).strip() if tm else None,
    }


def work(camp_id):
    for attempt in range(3):
        try:
            return parse_profile(fetch(camp_id), camp_id)
        except Exception:
            time.sleep(1 + attempt)
    return None


def main():
    max_id = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_MAX
    done = valid = 0
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=WORKERS) as ex:
        futs = {ex.submit(work, cid): cid for cid in range(1, max_id + 1)}
        for fut in as_completed(futs):
            try:
                p = fut.result()
            except Exception:
                p = None
            if p:
                valid += 1
                print(json.dumps(p, ensure_ascii=False), flush=True)
            done += 1
            if done % 500 == 0:
                el = time.time() - t0
                print(f"# progress: done={done} valid={valid} elapsed={el:.0f}s rate={done/el:.1f}/s",
                      file=sys.stderr, flush=True)
    print(f"# DONE: {done} fetched, {valid} valid", file=sys.stderr)


if __name__ == "__main__":
    main()
