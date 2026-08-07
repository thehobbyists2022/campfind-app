#!/usr/bin/env python3
"""
ACA Camp Data Crawler v2 — uses browser session cookie.
Extracts structured camp data from ACA's search results and camp profiles.
Exports JSON compatible with CampFind frontend.

Usage:
  python3 03_aca_crawler_v2.py --session-id PHPSESSID --max-camps 50
  python3 03_aca_crawler_v2.py --max-camps 30 --output camp_data.json
"""
import requests
import re
import json
import time
import sys
from urllib.parse import urljoin

BASE_URL = "https://find.acacamps.org"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def create_session(php_session_id):
    """Create a requests session with the given PHP session ID."""
    session = requests.Session()
    session.headers.update(HEADERS)
    if php_session_id:
        session.cookies.set("PHPSESSID", php_session_id)
    return session


def get_search_results(session, camp_type="day_camp", page=0):
    """Get search results page."""
    params = {
        "facets[camp_type]": camp_type,
        "search": "search",
        "save-criteria": "yes-please",
    }
    if page > 0:
        params["result_start"] = page * 10
    
    resp = session.post(
        urljoin(BASE_URL, "/search_results.php"),
        data=params,
        timeout=30,
    )
    resp.raise_for_status()
    return resp.text


def parse_camp_ids(html):
    """Extract camp IDs from search results page."""
    camps = []
    # Pattern: camp_id=1234"><h2>Camp Name</h2>
    for m in re.finditer(r'camp_id[=%](\d+)[^>]*>\s*<h2[^>]*>(.*?)</h2>', html, re.DOTALL):
        camps.append({
            "camp_id": m.group(1),
            "name": m.group(2).strip(),
        })
    return camps


def fetch_camp_profile(session, camp_id):
    """Fetch and parse a camp's profile page."""
    url = urljoin(BASE_URL, f"/camp_profile.php?camp_id={camp_id}")
    resp = session.get(url, timeout=15)
    resp.raise_for_status()
    return parse_camp_profile(resp.text, camp_id)


def parse_camp_profile(html, camp_id):
    """Extract structured data from a camp profile page."""
    data = {"camp_id": camp_id, "aca_url": urljoin(BASE_URL, f"/camp_profile.php?camp_id={camp_id}")}
    
    # Camp name — skip the nav "Find a Camp" h1, get the actual camp name
    names = re.findall(r'<h1[^>]*>(.*?)</h1>', html, re.DOTALL)
    for n in names:
        n = n.strip()
        if n.lower() not in ("find a camp", "programs"):
            data["name"] = n
            break
    
    # Description (try multiple patterns)
    for pattern in [
        r'<p[^>]*class="[^"]*camp-description[^"]*"[^>]*>(.*?)</p>',
        r'<div[^>]*class="[^"]*col-sm-8[^"]*"[^>]*>\s*<p[^>]*>(.*?)</p>',
    ]:
        m = re.search(pattern, html, re.DOTALL)
        if m:
            desc = re.sub(r'<[^>]+>', '', m.group(1)).strip()
            # Clean up whitespace
            desc = re.sub(r'\s+', ' ', desc)
            data["description"] = desc[:500]
            break
    
    # Location (address, city, state, zip)
    # Structure: <h3>Location</h3><address><p>ADDRESS<br>CITY,&nbsp;ST&nbsp;ZIP<br>...</p></address>
    loc_section = re.search(
        r'<h3[^>]*>Location\s*</h3>\s*<address[^>]*>\s*<p[^>]*>\s*(.*?)</p>\s*</address>',
        html, re.DOTALL | re.IGNORECASE
    )
    if loc_section:
        loc_text = loc_section.group(1).strip()
        # Split on <br> to get address line and city/state/zip line
        parts = re.split(r'<br\s*/?>', loc_text)
        
        if len(parts) >= 1:
            data["address"] = re.sub(r'<[^>]+>', '', parts[0]).strip()
        
        if len(parts) >= 2:
            city_line = re.sub(r'<[^>]+>', '', parts[1]).strip()
            # Decode &nbsp; to space
            city_line = city_line.replace('&nbsp;', ' ')
            # Format: "Brooklyn, NY 11225-3783" or "City, ST ZIP"
            m = re.search(r'([A-Za-z][\w\s.]+?),\s*([A-Z]{2})\s*(\d{5}(?:-\d{4})?)', city_line)
            if m:
                data["city"] = m.group(1).strip()
                data["state"] = m.group(2).strip()
                data["zip"] = m.group(3).strip()
            else:
                # Try without zip
                m2 = re.search(r'([A-Za-z][\w\s.]+?),\s*([A-Z]{2})', city_line)
                if m2:
                    data["city"] = m2.group(1).strip()
                    data["state"] = m2.group(2).strip()
    else:
        # Fallback: try search results snippet format: (Brooklyn, NY)
        m2 = re.search(r'\(([A-Za-z][\w\s.]+),\s*([A-Z]{2})\)', html)
        if m2:
            data["city"] = m2.group(1).strip()
            data["state"] = m2.group(2).strip()
    
    # Phone — look in Contact section
    contact_section = re.search(
        r'<h3[^>]*>Contact\s*</h3>(.*?)</div>\s*<div',
        html, re.DOTALL | re.IGNORECASE
    )
    if contact_section:
        contact_html = contact_section.group(1)
        m = re.search(r'(\d{3}[-.\s]?\d{3}[-.\s]?\d{4})', contact_html)
        if m:
            data["phone"] = m.group(1).strip()
    
    # Email
    m = re.search(r'([\w.+-]+@[\w-]+\.[\w.-]+)', html)
    if m:
        data["email"] = m.group(0).strip()
    
    # Website — look in contact section only
    if contact_section:
        contact_html = contact_section.group(1)
        m = re.search(r'<a[^>]*href="(https?://[^"]+)"[^>]*>', contact_html)
        if m:
            url = m.group(1)
            # Skip ACA's own links
            if "acacamps.org" not in url:
                data["website"] = url
    
    # Programs table
    programs = []
    # Find programs table
    table_section = re.search(
        r'<h\d[^>]*>\s*Programs?\s*</h\d>.*?<table[^>]*>(.*?)</table>',
        html, re.DOTALL
    )
    if table_section:
        table_html = table_section.group(1)
        # Find all rows (skip header row)
        rows = re.findall(r'<tr[^>]*>(.*?)</tr>', table_html, re.DOTALL)
        for row_html in rows:
            # Skip header row
            if '<th' in row_html:
                continue
            # Extract all td cells (handle empty ones)
            cells = re.findall(r'<td[^>]*>(.*?)</td>', row_html, re.DOTALL)
            if len(cells) >= 3:
                prog = {
                    "name": re.sub(r'<[^>]+>', '', cells[0]).strip() if cells[0].strip() else "",
                    "gender": re.sub(r'<[^>]+>', '', cells[1]).strip() if len(cells) > 1 and cells[1].strip() else "",
                    "type": re.sub(r'<[^>]+>', '', cells[2]).strip() if len(cells) > 2 and cells[2].strip() else "",
                    "age_grade": re.sub(r'<[^>]+>', '', cells[3]).strip() if len(cells) > 3 and cells[3].strip() else "",
                    "transportation": re.sub(r'<[^>]+>', '', cells[4]).strip() if len(cells) > 4 and cells[4].strip() else "",
                    "cost": re.sub(r'<[^>]+>', '', cells[5]).strip() if len(cells) > 5 and cells[5].strip() else "",
                }
                # Extract program_id from links in name cell
                pid_m = re.search(r'program_id[=%](\d+)', cells[0])
                if pid_m:
                    prog["program_id"] = pid_m.group(1)
                    prog["name"] = re.sub(r'<[^>]+>', '', cells[0]).strip()
                if prog["name"]:
                    programs.append(prog)
    
    data["programs"] = programs
    
    # Derive camp type from programs
    types = set(p.get("type", "").strip() for p in programs)
    if "Overnight" in types or "Resident" in types:
        if "Day" in types:
            data["camp_type"] = "both"
        else:
            data["camp_type"] = "overnight"
    elif "Day" in types:
        data["camp_type"] = "day"
    else:
        # Try the search context — if no programs table, check page for keywords
        if "overnight" in html.lower() or "resident" in html.lower():
            data["camp_type"] = "overnight"
        else:
            data["camp_type"] = "day"
    
    # Derive age range
    ages = []
    for p in programs:
        for pattern in [
            r'(\d+)\s*[–\-to]+\s*(\d+)\s*(?:years?|yrs?|yr)',
            r'(\d+)\s*[–\-to]+\s*(\d+)(?:\s|$)',
            r'Ages?\s*(\d+)\s*[–\-to]+\s*(\d+)',
        ]:
            m = re.search(pattern, p.get("age_grade", ""), re.IGNORECASE)
            if m:
                ages.append((int(m.group(1)), int(m.group(2))))
                break
    
    # Also check standalone age mentions
    if not ages:
        for pattern in [
            r'(\d+)\s*[–\-]\s*(\d+)\s*years?',
            r'(\d+)\s*-\s*(\d+)\s*y',
        ]:
            m = re.search(pattern, html, re.IGNORECASE)
            if m:
                ages.append((int(m.group(1)), int(m.group(2))))
                break
    
    if ages:
        data["age_min"] = min(a[0] for a in ages)
        data["age_max"] = max(a[1] for a in ages)
    else:
        data["age_min"] = 5
        data["age_max"] = 17
    
    # Derive price range
    prices = []
    for p in programs:
        cost = p.get("cost", "")
        # Range: $100 - $200
        m = re.search(r'\$(\d[\d,.]*)\s*[–\-]\s*\$(\d[\d,.]*)', cost)
        if m:
            try:
                prices.extend([float(m.group(1).replace(",", "")),
                               float(m.group(2).replace(",", ""))])
            except ValueError:
                pass
        else:
            # Single price: $100
            m2 = re.search(r'\$(\d[\d,.]*)', cost)
            if m2:
                try:
                    prices.append(float(m2.group(1).replace(",", "")))
                except ValueError:
                    pass
    
    if prices:
        data["min_price"] = int(min(prices))
        data["max_price"] = int(max(prices))
    else:
        data["min_price"] = 300
        data["max_price"] = 800
    
    # ACA Accredited?
    data["accredited"] = "Accredited" in html
    
    return data


def scrape_camps(php_session_id=None, max_camps=50, camp_type="day_camp", 
                 state_filter=None, output="camp_data.json", rate_limit=1.0):
    """Main scrape function."""
    print(f"{'='*60}")
    print(f"🎯 ACA Camp Crawler v2")
    print(f"  Using session: {'Yes' if php_session_id else 'No (will create new)'}")
    print(f"  Type: {camp_type}")
    print(f"  Max camps: {max_camps}")
    print(f"  State: {state_filter or 'ALL'}")
    print(f"  Output: {output}")
    print(f"{'='*60}")
    
    session = create_session(php_session_id)
    
    # Step 1: First, initialize session by visiting home page
    if not php_session_id:
        print("\n📡 Step 0: Initializing session...")
        resp = session.get(BASE_URL, timeout=30)
        resp.raise_for_status()
        
        # Submit initial search
        search_data = {
            "search": "search",
            "facets[camp_type]": camp_type,
            "open[choices-made-section-content]": "true",
        }
        resp = session.post(urljoin(BASE_URL, "/search.php"), data=search_data, timeout=30)
        resp.raise_for_status()
        print(f"  Session initialized: {session.cookies.get('PHPSESSID', 'N/A')}")
    
    # Step 2: Get search results
    print(f"\n📡 Step 1: Getting search results...")
    html = get_search_results(session, camp_type)
    all_camps = parse_camp_ids(html)
    print(f"  Page 1: {len(all_camps)} camps")
    
    # Step 3: Paginate
    page = 1
    while len(all_camps) < max_camps:
        html = get_search_results(session, camp_type, page=page)
        camps = parse_camp_ids(html)
        if not camps:
            break
        print(f"  Page {page + 1}: {len(camps)} camps")
        all_camps.extend(camps)
        page += 1
        if page > 10:
            break
        time.sleep(0.3)
    
    all_camps = all_camps[:max_camps]
    print(f"\n  Total camps found: {len(all_camps)}")
    
    # Step 4: Fetch individual profiles
    print(f"\n📡 Step 2: Fetching camp profiles...")
    results = []
    for i, camp in enumerate(all_camps):
        cid = camp["camp_id"]
        name = camp.get("name", "?")
        print(f"  [{i+1}/{len(all_camps)}] {name[:45]:45s}...", end=" ", flush=True)
        
        try:
            profile = fetch_camp_profile(session, cid)
            
            # Apply state filter
            if state_filter and profile.get("state", "") != state_filter:
                print(f"⏭️  skip ({profile.get('state', '?')})")
                continue
            
            # Transform to CampFind format
            entry = {
                "id": f"aca_{cid}",
                "name": profile.get("name", name),
                "city": profile.get("city", ""),
                "state": profile.get("state", ""),
                "zip": profile.get("zip", ""),
                "type": profile.get("camp_type", "day"),
                "price": profile.get("min_price", 300),
                "price_max": profile.get("max_price", 800),
                "rating": 4.5 if profile.get("accredited") else 4.0,
                "reviewCount": 0,
                "ageMin": profile.get("age_min", 5),
                "ageMax": profile.get("age_max", 17),
                "availability": "available",
                "description": profile.get("description", "")[:200],
                "phone": profile.get("phone", ""),
                "email": profile.get("email", ""),
                "website": profile.get("website", ""),
                "aca_url": profile.get("aca_url", ""),
                "accredited": profile.get("accredited", False),
                "sessions": [],
            }
            
            # Generate sessions from programs
            for p in profile.get("programs", []):
                # Calculate session price from program cost
                cost = p.get("cost", "")
                price_m = re.search(r'\$(\d[\d,.]*)', cost)
                session_price = int(float(price_m.group(1).replace(",", ""))) if price_m else entry["price"]
                
                entry["sessions"].append({
                    "name": p.get("name", "Program"),
                    "date": "Contact for dates",
                    "price": session_price,
                    "age_range": p.get("age_grade", ""),
                    "gender": p.get("gender", ""),
                })
            
            if not entry["sessions"]:
                entry["sessions"].append({
                    "name": "Contact for info",
                    "date": "Contact for dates",
                    "price": entry["price"],
                })
            
            results.append(entry)
            loc = f"{entry['city']}, {entry['state']}" if entry['city'] else "loc unknown"
            print(f"✅ {loc}")
            
        except Exception as e:
            print(f"❌ {e}")
        
        time.sleep(rate_limit)
    
    # Step 5: Export
    output_data = {
        "source": "American Camp Association - Find a Camp",
        "url": "https://find.acacamps.org/",
        "crawl_type": camp_type,
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
    print(f"  States: {dict(sorted(states.items(), key=lambda x: -x[1])[:10])}")
    print(f"  Types: {types}")
    
    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="ACA Camp Data Crawler v2")
    parser.add_argument("--session-id", help="PHP Session ID from browser")
    parser.add_argument("--max-camps", type=int, default=50)
    parser.add_argument("--type", default="day_camp",
                        choices=["day_camp", "overnight_camp", "day_and_overnight", "adult_camp"])
    parser.add_argument("--state", help="Filter by state code (e.g. CA)")
    parser.add_argument("--output", default="aca_camp_data.json")
    parser.add_argument("--rate-limit", type=float, default=1.0)
    args = parser.parse_args()
    
    scrape_camps(
        php_session_id=args.session_id,
        max_camps=args.max_camps,
        camp_type=args.type,
        state_filter=args.state,
        output=args.output,
        rate_limit=args.rate_limit,
    )
