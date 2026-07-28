#!/usr/bin/env python3
"""
ACA Camp Data Crawler — extracts structured camp data from ACA's Find a Camp site.
Outputs JSON compatible with CampFind frontend.

Usage:
  python3 03_aca_crawler.py --type day_camp --max-camps 50
  python3 03_aca_crawler.py --type all --output camp_data.json
  python3 03_aca_crawler.py --state CA --max-camps 30
"""
import requests
import re
import json
import time
import sys
import argparse
from urllib.parse import urljoin
from html.parser import HTMLParser

BASE_URL = "https://find.acacamps.org"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

CAMP_TYPES = {
    "day_camp": "Day",
    "overnight_camp": "Overnight",
    "day_and_overnight": "Day and Overnight",
    "adult_camp": "Family or Adult",
}

# Price parser
PRICE_PATTERN = re.compile(r'\$(\d[\d,.]*)\s*-\s*\$(\d[\d,.]*)')
SINGLE_PRICE_PATTERN = re.compile(r'\$(\d[\d,.]*)')


def setup_session():
    """Create a requests session and complete the ACA multi-step search."""
    session = requests.Session()
    session.headers.update(HEADERS)
    return session


def do_search(session, camp_type="day_camp", result_start=0):
    """Execute search and get results page."""
    search_url = urljoin(BASE_URL, "/search.php")
    search_data = {
        "search": "search",
        "facets[camp_type]": camp_type,
        "open[choices-made-section-content]": "true",
    }
    
    resp = session.post(search_url, data=search_data, timeout=30)
    resp.raise_for_status()
    
    # Now click "See Your Results" - form submits to search_results.php
    results_url = urljoin(BASE_URL, "/search_results.php")
    search_data["result_start"] = result_start
    search_data["save-criteria"] = "yes-please"
    
    resp = session.post(results_url, data=search_data, timeout=30)
    resp.raise_for_status()
    return resp.text


def parse_camp_list(html):
    """Extract camp IDs and names from search results page."""
    camps = []
    
    # Find camp containers - each has a link to camp_profile.php?camp_id=XXXX
    pattern = re.compile(
        r'camp_profile\.php\?back=search&amp;camp_id=(\d+)[^>]*>'
        r'\s*<h2>(.*?)</h2>',
        re.DOTALL
    )
    
    for match in pattern.finditer(html):
        camp_id = match.group(1)
        name = match.group(2).strip()
        camps.append({"camp_id": camp_id, "name": name})
    
    # Also try alternate pattern
    if not camps:
        pattern2 = re.compile(
            r'camp_profile\.php\?camp_id=(\d+)[^>]*>\s*<h2>(.*?)</h2>',
            re.DOTALL
        )
        for match in pattern2.finditer(html):
            camp_id = match.group(1)
            name = match.group(2).strip()
            camps.append({"camp_id": camp_id, "name": name})
    
    # Get program info per camp
    camp_programs = {}
    program_pattern = re.compile(
        r'camp_id=(\d+).*?program_profile\.php\?program_id=(\d+)[^>]*>'
        r'\s*<span[^>]*class="program-name"[^>]*>'
        r'\s*<a[^>]*>(.*?)</a>',
        re.DOTALL
    )
    for match in program_pattern.finditer(html):
        cid = match.group(1)
        pid = match.group(2)
        pname = match.group(3).strip()
        if cid not in camp_programs:
            camp_programs[cid] = []
        camp_programs[cid].append({"program_id": pid, "name": pname})
    
    for camp in camps:
        camp["programs"] = camp_programs.get(camp["camp_id"], [])
    
    return camps


def parse_camp_profile(html):
    """Extract structured data from a camp's profile page."""
    data = {}
    
    # Description
    desc_match = re.search(
        r'<p[^>]*class="[^"]*camp-description[^"]*"[^>]*>(.*?)</p>',
        html, re.DOTALL
    )
    if not desc_match:
        # Try to find the main description div
        desc_match = re.search(
            r'<div[^>]*class="[^"]*col-sm-8[^"]*"[^>]*>\s*<p[^>]*>(.*?)</p>',
            html, re.DOTALL
        )
    if desc_match:
        data["description"] = re.sub(r'<[^>]+>', '', desc_match.group(1)).strip()[:500]
    
    # Location
    loc_match = re.search(
        r'<p[^>]*>\s*(\d[^<]*)\s*<br\s*/?>\s*([^<,]+),\s*([A-Z]{2})\s*(\d{5}(?:-\d{4})?)',
        html, re.DOTALL
    )
    if loc_match:
        data["address"] = loc_match.group(1).strip()
        data["city"] = loc_match.group(2).strip()
        data["state"] = loc_match.group(3).strip()
        data["zip"] = loc_match.group(4).strip()[:5]
    
    # Contact
    phone_match = re.search(r'(\d{10}|\d{3}[\s.-]\d{3}[\s.-]\d{4})', html)
    if phone_match:
        data["phone"] = phone_match.group(1)
    
    email_match = re.search(r'[\w.+-]+@[\w-]+\.[\w.-]+', html)
    if email_match:
        data["email"] = email_match.group(0)
    
    website_match = re.search(
        r'<a[^>]*href="(https?://[^"]+)"[^>]*target="_blank"[^>]*>'
        r'\s*(?:Visit\s*Website|www\.[^<]+)',
        html, re.DOTALL
    )
    if website_match:
        data["website"] = website_match.group(1)
    
    # Programs table
    programs = []
    table_rows = re.finditer(
        r'<tr>\s*<td[^>]*>\s*<a[^>]*program_profile\.php\?program_id=(\d+)[^>]*>(.*?)</a>'
        r'\s*</td>\s*<td[^>]*>(.*?)</td>\s*<td[^>]*>(.*?)</td>'
        r'\s*<td[^>]*>(.*?)</td>\s*<td[^>]*>(.*?)</td>\s*<td[^>]*>(.*?)</td>',
        html, re.DOTALL
    )
    for row in table_rows:
        prog = {
            "program_id": row.group(1),
            "name": row.group(2).strip(),
            "gender": row.group(3).strip(),
            "type": row.group(4).strip(),
            "age_grade": row.group(5).strip(),
            "transportation": row.group(6).strip(),
            "cost": row.group(7).strip(),
        }
        programs.append(prog)
    
    if programs:
        data["programs"] = programs
        # Derive type from programs
        types = set(p["type"] for p in programs)
        if "Overnight" in types and "Day" in types:
            data["camp_type"] = "both"
        elif "Overnight" in types:
            data["camp_type"] = "overnight"
        else:
            data["camp_type"] = "day"
        
        # Derive age range from programs
        ages = []
        for p in programs:
            age_match = re.search(r'(\d+)\s*-\s*(\d+)', p["age_grade"])
            if age_match:
                ages.append((int(age_match.group(1)), int(age_match.group(2))))
        if ages:
            data["age_min"] = min(a[0] for a in ages)
            data["age_max"] = max(a[1] for a in ages)
        
        # Derive price range from programs
        prices = []
        for p in programs:
            m = PRICE_PATTERN.search(p["cost"])
            if m:
                try:
                    prices.append(float(m.group(1).replace(",", "")))
                    prices.append(float(m.group(2).replace(",", "")))
                except ValueError:
                    pass
            else:
                m2 = SINGLE_PRICE_PATTERN.search(p["cost"])
                if m2:
                    try:
                        prices.append(float(m2.group(1).replace(",", "")))
                    except ValueError:
                        pass
        if prices:
            data["min_price"] = min(prices)
            data["max_price"] = max(prices)
    
    return data


def crawl_camps(
    camp_type="day_camp",
    max_camps=30,
    state_filter=None,
    output="camp_data.json",
    rate_limit=1.0,
):
    """Main crawl function."""
    print(f"{'='*60}")
    print(f"🎯 ACA Camp Crawler")
    print(f"  Type: {CAMP_TYPES.get(camp_type, camp_type)}")
    print(f"  Max camps: {max_camps}")
    print(f"  State filter: {state_filter or 'ALL'}")
    print(f"  Output: {output}")
    print(f"{'='*60}\n")
    
    session = setup_session()
    
    # Step 1: Search
    print("📡 Step 1: Searching...")
    html = do_search(session, camp_type)
    camps = parse_camp_list(html)
    print(f"  Found {len(camps)} camps on first page")
    
    # Step 2: Paginate through all results to collect camp IDs
    all_camps = list(camps)
    page = 1
    while len(camps) > 0 and len(all_camps) < max_camps:
        html = do_search(session, camp_type, result_start=page * 10)
        camps = parse_camp_list(html)
        print(f"  Page {page + 1}: {len(camps)} camps")
        all_camps.extend(camps)
        page += 1
        if page >= 5:  # safety limit
            break
        time.sleep(0.5)
    
    # Apply state filter
    if state_filter:
        pass  # We'll filter during crawl after fetching profile
    
    all_camps = all_camps[:max_camps]
    print(f"\n📡 Step 2: Fetching details for {len(all_camps)} camps...\n")
    
    # Step 3: Fetch each camp's profile
    results = []
    for i, camp in enumerate(all_camps):
        print(f"  [{i+1}/{len(all_camps)}] {camp['name'][:50]}...", end=" ", flush=True)
        
        try:
            url = urljoin(BASE_URL, f"/camp_profile.php?camp_id={camp['camp_id']}")
            resp = session.get(url, timeout=15)
            resp.raise_for_status()
            detail = parse_camp_profile(resp.text)
            
            camp.update(detail)
            
            # Apply state filter after fetching
            if state_filter and camp.get("state") != state_filter:
                print(f"⏭️  (not {state_filter})")
                continue
            
            # Calculate rating from ACA accreditation
            rating = 4.5 if "Accredited" in resp.text else 4.0
            
            entry = {
                "id": f"aca_{camp['camp_id']}",
                "name": camp.get("name", "Unknown Camp"),
                "city": camp.get("city", ""),
                "state": camp.get("state", ""),
                "zip": camp.get("zip", ""),
                "type": camp.get("camp_type", "day"),
                "price": int(camp.get("min_price", 300)),
                "price_max": int(camp.get("max_price", camp.get("min_price", 300))),
                "rating": rating,
                "reviewCount": 0,
                "ageMin": camp.get("age_min", 5),
                "ageMax": camp.get("age_max", 17),
                "availability": "available",
                "description": camp.get("description", ""),
                "phone": camp.get("phone", ""),
                "email": camp.get("email", ""),
                "website": camp.get("website", ""),
                "aca_url": url,
                "programs": camp.get("programs", []),
            }
            
            # Generate sessions from programs
            sessions = []
            for p in camp.get("programs", []):
                sessions.append({
                    "name": p.get("name", "Program"),
                    "date": "Contact for dates",
                    "price": int(camp.get("min_price", 300)),
                    "age_range": p.get("age_grade", ""),
                })
            if sessions:
                entry["sessions"] = sessions
            else:
                entry["sessions"] = [
                    {"date": "Contact for dates", "price": entry["price"]}
                ]
            
            results.append(entry)
            print(f"✅ {entry['city']}, {entry['state']}")
            
        except Exception as e:
            print(f"❌ {e}")
        
        time.sleep(rate_limit)  # Be polite
    
    # Step 4: Export
    output_data = {
        "source": "American Camp Association - Find a Camp",
        "url": "https://find.acacamps.org/",
        "crawl_type": CAMP_TYPES.get(camp_type, camp_type),
        "total_camps": len(results),
        "crawled_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "camps": results,
    }
    
    with open(output, "w") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Exported {len(results)} camps to {output}")
    
    # Stats
    states = {}
    types = {}
    for c in results:
        s = c.get("state", "?")
        states[s] = states.get(s, 0) + 1
        t = c.get("type", "?")
        types[t] = types.get(t, 0) + 1
    print(f"  States: {dict(sorted(states.items(), key=lambda x: -x[1]))}")
    print(f"  Types: {types}")
    
    return results


class CampProfileParser(HTMLParser):
    """Alternative parser for camp profile pages."""
    def __init__(self):
        super().__init__()
        self.data = {}
        self._current_tag = None
        self._capture = False
        self._text = []
    
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        # Detect program table
        if tag == "table" and "class" in attrs_dict and "programs" in attrs_dict.get("class", ""):
            self._in_program_table = True


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ACA Camp Data Crawler")
    parser.add_argument("--type", choices=list(CAMP_TYPES.keys()) + ["all"],
                        default="day_camp", help="Camp type to crawl")
    parser.add_argument("--max-camps", type=int, default=30,
                        help="Maximum camps to crawl")
    parser.add_argument("--state", type=str, help="Filter by state (e.g. CA)")
    parser.add_argument("--output", default="camp_data.json",
                        help="Output JSON file")
    parser.add_argument("--rate-limit", type=float, default=1.0,
                        help="Seconds between requests")
    args = parser.parse_args()
    
    if args.type == "all":
        all_results = []
        for ctype in CAMP_TYPES:
            out = f"camp_data_{ctype}.json"
            results = crawl_camps(
                camp_type=ctype,
                max_camps=args.max_camps,
                state_filter=args.state,
                output=out,
                rate_limit=args.rate_limit,
            )
            all_results.extend(results)
        # Merge
        merged = {
            "source": "American Camp Association",
            "total_camps": len(all_results),
            "camps": all_results,
            "crawled_at": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
        with open(args.output, "w") as f:
            json.dump(merged, f, indent=2)
        print(f"\n✅ Merged {len(all_results)} camps to {args.output}")
    else:
        crawl_camps(
            camp_type=args.type,
            max_camps=args.max_camps,
            state_filter=args.state,
            output=args.output,
            rate_limit=args.rate_limit,
        )
