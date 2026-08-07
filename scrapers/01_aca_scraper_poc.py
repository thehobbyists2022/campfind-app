#!/usr/bin/env python3
"""
ACA Summer Camp Scraper — Proof of Concept
===========================================
American Camp Association (ACA) Find a Camp 資料庫爬蟲 PoC

Target: https://find.acacamps.org/
Database: 3,919 camps, 11,170 programs, 3,555 sessions

Strategy:
  1. Submit search form via POST for each camp type
  2. Parse results HTML for camp listings
  3. Follow each camp detail page for full info
  4. Export to structured JSON

Usage:
  python3 01_aca_scraper_poc.py                # Full crawl (slow, polite)
  python3 01_aca_scraper_poc.py --dry-run       # Test 1 page only
  python3 01_aca_scraper_poc.py --state CA      # Filter by state
"""

import requests
import re
import json
import time
import sys
from urllib.parse import urljoin, urlencode
from html.parser import HTMLParser

BASE_URL = "https://find.acacamps.org"
SEARCH_URL = urljoin(BASE_URL, "/search.php")
CAMP_TYPES = ["Day", "Overnight", "Day+and+Overnight", "Family+or+Adult"]
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


# ---------------------------------------------------------------------------
# Simple HTML parser to extract camp listings from search results
# ---------------------------------------------------------------------------
class CampListParser(HTMLParser):
    """Extract camp cards from the search results page."""
    
    def __init__(self):
        super().__init__()
        self.camps = []
        self.in_camp_block = False
        self.current = {}
        self._tag_stack = []
        self._capture_text = False
        self._text_buf = []
        
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self._tag_stack.append(tag)
        
        # Detect camp result blocks — each camp is in a <div> with a data-camp-id
        if tag == "div" and "data-camp-id" in attrs:
            self.in_camp_block = True
            self.current = {"camp_id": attrs["data-camp-id"]}
            
        # Camp name link
        if tag == "a" and "class" in attrs:
            classes = attrs["class"].split()
            if "camp-name" in classes or "camp_link" in classes:
                self.current["url"] = urljoin(BASE_URL, attrs.get("href", ""))
                self._capture_text = True
                self._text_buf = []
                
        # Age range spans
        if tag == "span" and "class" in attrs:
            classes = attrs["class"].split()
            if "age-range" in classes:
                self._capture_text = True
                self._text_buf = []
                
    def handle_endtag(self, tag):
        if self._tag_stack:
            self._tag_stack.pop()
        if tag == "div" and self.in_camp_block:
            if self.current:
                self.camps.append(self.current)
            self.in_camp_block = False
            self.current = {}
        if tag in ("a", "span", "p", "div"):
            self._capture_text = False
            
    def handle_data(self, data):
        if self._capture_text:
            self._text_buf.append(data.strip())
        if self.in_camp_block and self._tag_stack[-1:] == ["p"]:
            text = data.strip()
            if "Phone:" in text:
                self.current["phone"] = text.replace("Phone:", "").strip()
            elif "Email:" in text:
                self.current["email"] = text.replace("Email:", "").strip()
                
    def _finalize_field(self, key):
        if self._text_buf:
            self.current[key] = " ".join(t for t in self._text_buf if t)
            self._text_buf = []
            self._capture_text = False


def search_camps(camp_type="Day", page=0, dry_run=False):
    """
    Submit a search to the ACA Find a Camp database.
    
    The search form uses POST with facet parameters.
    Page-based pagination via result_start parameter.
    """
    params = {
        "facets[camp_type]": camp_type.replace("+", " "),
        "result_start": page * 10,
        "search": "Search",
    }
    
    if dry_run:
        print(f"[DRY-RUN] Would POST to {SEARCH_URL}")
        print(f"  Params: {params}")
        return []
    
    print(f"  Searching {camp_type} camps (page {page + 1})...", end=" ", flush=True)
    
    try:
        resp = requests.post(SEARCH_URL, data=params, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        html = resp.text
        
        # Extract total results count
        total_match = re.search(r'(\d[\d,]*)\s+(camp|camps|program|programs)', html)
        total = total_match.group(1) if total_match else "?"
        print(f"got {len(html):,} bytes, HTML says ~{total}")
        
        # Parse camp entries using regex (more robust than HTMLParser for this site)
        camps = parse_camp_listings(html)
        print(f"  → Extracted {len(camps)} camps from page")
        return camps
        
    except requests.RequestException as e:
        print(f"ERROR: {e}")
        return []


def parse_camp_listings(html):
    """Parse camp search results using regex patterns."""
    camps = []
    
    # Pattern 1: Look for structured camp data blocks
    # ACA results page has divs with data-camp-id
    blocks = re.finditer(
        r'<div[^>]*data-camp-id=["\'](\d+)["\'][^>]*>(.*?)</div>\s*(?=<div[^>]*data-camp-id|$)',
        html, re.DOTALL
    )
    
    for block in blocks:
        camp_id = block.group(1)
        content = block.group(2)
        camp = {"camp_id": camp_id}
        
        # Camp name
        name_match = re.search(r'<a[^>]*class=["\'][^"\']*camp[^"\']*["\'][^>]*>([^<]+)', content)
        if name_match:
            camp["name"] = name_match.group(1).strip()
        
        # URL
        url_match = re.search(r'<a[^>]*href=["\']([^"\']+)["\'][^>]*class=["\'][^"\']*camp[^"\']*["\']', content)
        if url_match:
            camp["url"] = urljoin(BASE_URL, url_match.group(1))
        
        # Organization / provider
        org_match = re.search(r'class=["\']org-name["\'][^>]*>([^<]+)', content)
        if org_match:
            camp["organization"] = org_match.group(1).strip()
        
        # Location (city, state)
        loc_match = re.search(r'([A-Z][a-zA-Z\s]+),\s*([A-Z]{2})\s+\d{5}', content)
        if loc_match:
            camp["city"] = loc_match.group(1).strip()
            camp["state"] = loc_match.group(2).strip()
        
        # Phone / Email
        phone = re.search(r'Phone:\s*([\d\-\.\(\)\s]+)', content)
        if phone:
            camp["phone"] = phone.group(1).strip()
        email = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', content)
        if email:
            camp["email"] = email.group(0)
        
        # Age range
        age = re.search(r'Ages?\s*(\d+)\s*[-to]*\s*(\d*)', content, re.IGNORECASE)
        if age:
            camp["age_min"] = int(age.group(1))
            camp["age_max"] = int(age.group(2)) if age.group(2) else int(age.group(1))
        
        # Camp type
        type_match = re.search(r'(Day|Overnight|Resident|Family|Adult)', content)
        if type_match:
            camp["type"] = type_match.group(1)
        
        if "name" in camp:
            camps.append(camp)
    
    # Pattern 2: Fallback — if structured blocks don't work, try generic card pattern
    if not camps:
        cards = re.finditer(
            r'<div[^>]*class=["\'][^"\']*result-item[^"\']*["\'][^>]*>(.*?)</div>\s*</div>',
            html, re.DOTALL
        )
        for card in cards:
            content = card.group(1)
            camp = {}
            
            name = re.search(r'<h[23][^>]*>([^<]+)', content)
            if name:
                camp["name"] = name.group(1).strip()
            
            loc = re.search(r'([A-Z][a-zA-Z\s]+),\s*([A-Z]{2})\s+\d{5}', content)
            if loc:
                camp["city"] = loc.group(1).strip()
                camp["state"] = loc.group(2).strip()
            
            phone = re.search(r'Phone:\s*([\d\-\.\(\)\s]+)', content)
            if phone:
                camp["phone"] = phone.group(1).strip()
            
            if "name" in camp:
                camps.append(camp)
    
    return camps


def get_camp_detail(camp_url, dry_run=False):
    """
    Fetch a single camp's detail page for more info.
    """
    if dry_run:
        return {}
    
    if not camp_url:
        return {}
    
    try:
        resp = requests.get(camp_url, headers=HEADERS, timeout=15)
        resp.raise_for_status()
        html = resp.text
    except requests.RequestException:
        return {}
    
    detail = {}
    
    # Description
    desc = re.search(r'<div[^>]*class=["\'][^"\']*description[^"\']*["\'][^>]*>(.*?)</div>', html, re.DOTALL)
    if desc:
        detail["description"] = re.sub(r'<[^>]+>', '', desc.group(1)).strip()[:500]
    
    # Programs / sessions
    programs = re.finditer(
        r'<div[^>]*class=["\'][^"\']*program[^"\']*["\'][^>]*>(.*?)</div>',
        html, re.DOTALL
    )
    sessions = []
    for prog in programs:
        content = prog.group(1)
        session = {}
        
        s_name = re.search(r'<h\d[^>]*>([^<]+)', content)
        if s_name:
            session["name"] = s_name.group(1).strip()
        
        dates = re.search(r'(\d{1,2}/\d{1,2}/\d{4})\s*[-–to]*\s*(\d{1,2}/\d{1,2}/\d{4})', content)
        if dates:
            session["start_date"] = dates.group(1)
            session["end_date"] = dates.group(2)
        
        price = re.search(r'\$(\d[\d,.]*)', content)
        if price:
            session["price"] = price.group(1)
        
        age = re.search(r'Ages?\s*(\d+)\s*[-to]*\s*(\d*)', content, re.IGNORECASE)
        if age:
            session["age_min"] = int(age.group(1))
            session["age_max"] = int(age.group(2)) if age.group(2) else None
        
        if session:
            sessions.append(session)
    
    if sessions:
        detail["sessions"] = sessions
    
    return detail


def crawl_all(dry_run=False, state_filter=None):
    """Crawl all camp types and aggregate results."""
    all_camps = []
    seen_ids = set()
    
    for camp_type in CAMP_TYPES:
        page = 0
        while True:
            camps = search_camps(camp_type, page, dry_run)
            if not camps:
                break
            
            for camp in camps:
                cid = camp.get("camp_id", camp.get("name", ""))
                if cid not in seen_ids:
                    if state_filter and camp.get("state") != state_filter:
                        continue
                    seen_ids.add(cid)
                    
                    # Get detail page (be polite — 1 req/sec)
                    if not dry_run and camp.get("url"):
                        print(f"    Fetching detail: {camp.get('name', '?')[:40]}...")
                        detail = get_camp_detail(camp["url"])
                        camp.update(detail)
                        time.sleep(1.0)  # rate limit: 1 req/sec
                    
                    all_camps.append(camp)
            
            page += 1
            if dry_run or page >= 2:  # limit to 2 pages in dry-run
                break
            time.sleep(0.5)
    
    return all_camps


def export_json(camps, filename="aca_camps_data.json"):
    """Export camps to structured JSON."""
    output = {
        "source": "American Camp Association - Find a Camp",
        "url": "https://find.acacamps.org/",
        "total_camps": len(camps),
        "scraped_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "camps": camps
    }
    
    with open(filename, "w") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Exported {len(camps)} camps to {filename}")
    return filename


def print_stats(camps):
    """Print summary statistics of scraped data."""
    if not camps:
        print("No camps found.")
        return
    
    types = {}
    states = {}
    total_with_sessions = 0
    total_sessions = 0
    
    for c in camps:
        t = c.get("type", "Unknown")
        types[t] = types.get(t, 0) + 1
        
        s = c.get("state", "?")
        states[s] = states.get(s, 0) + 1
        
        if "sessions" in c and c["sessions"]:
            total_with_sessions += 1
            total_sessions += len(c["sessions"])
    
    print(f"\n📊 ACA Camps Summary")
    print(f"{'='*50}")
    print(f"  Total camps:       {len(camps)}")
    print(f"  By type:           {types}")
    print(f"  States covered:    {len(states)}")
    print(f"  With session data: {total_with_sessions}")
    print(f"  Total sessions:    {total_sessions}")
    print(f"  Top states:        {dict(sorted(states.items(), key=lambda x: -x[1])[:10])}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="ACA Summer Camp Scraper PoC")
    parser.add_argument("--dry-run", action="store_true", help="Test mode — only fetch 1 page")
    parser.add_argument("--state", type=str, help="Filter by state (e.g. CA)")
    parser.add_argument("--output", type=str, default="aca_camps_data.json", help="Output JSON file")
    args = parser.parse_args()
    
    print(f"{'='*60}")
    print("🎯 ACA Summer Camp Finder — Scraper PoC")
    print(f"{'='*60}")
    print(f"  Mode: {'DRY RUN (2 pages only)' if args.dry_run else 'FULL CRAWL'}")
    print(f"  State filter: {args.state or 'ALL'}")
    print(f"  Output: {args.output}")
    print(f"{'='*60}\n")
    
    camps = crawl_all(dry_run=args.dry_run, state_filter=args.state)
    
    if camps:
        print_stats(camps)
        export_json(camps, args.output)
    else:
        print("\n⚠️  No camps scraped. The site structure may have changed.")
        print("   Check https://find.acacamps.org/ and update the parser patterns.")
