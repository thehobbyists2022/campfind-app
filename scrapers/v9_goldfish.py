#!/usr/bin/env python3
"""
CampFind v9 — Goldfish Swim School location expansion.

Source: official sitemap (goldfishswimschool.com/sitemap.xml) -> per-school
pages that embed JSON-LD (name, address, phone, zip). R2 = the school URL
itself; R1 = every field read from the official page.

Goldfish Swim School runs youth swimming programs (lessons + summer camps) at
locations across the US.
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "scrapers", "v5_cache")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"}

STATE_ABBR = {"alabama":"AL","alaska":"AK","arizona":"AZ","arkansas":"AR","california":"CA",
 "colorado":"CO","connecticut":"CT","delaware":"DE","florida":"FL","georgia":"GA","hawaii":"HI",
 "idaho":"ID","illinois":"IL","indiana":"IN","iowa":"IA","kansas":"KS","kentucky":"KY",
 "louisiana":"LA","maine":"ME","maryland":"MD","massachusetts":"MA","michigan":"MI","minnesota":"MN",
 "mississippi":"MS","missouri":"MO","montana":"MT","nebraska":"NE","nevada":"NV","new-hampshire":"NH",
 "new-jersey":"NJ","new-mexico":"NM","new-york":"NY","north-carolina":"NC","north-dakota":"ND",
 "ohio":"OH","oklahoma":"OK","oregon":"OR","pennsylvania":"PA","rhode-island":"RI",
 "south-carolina":"SC","south-dakota":"SD","tennessee":"TN","texas":"TX","utah":"UT","vermont":"VT",
 "virginia":"VA","washington":"WA","west-virginia":"WV","wisconsin":"WI","wyoming":"WY",
 # full names from JSON-LD
 "alabama":"AL","alaska":"AK","arizona":"AZ","arkansas":"AR","california":"CA","colorado":"CO",
 "connecticut":"CT","delaware":"DE","florida":"FL","georgia":"GA","hawaii":"HI","idaho":"ID",
 "illinois":"IL","indiana":"IN","iowa":"IA","kansas":"KS","kentucky":"KY","louisiana":"LA",
 "maine":"ME","maryland":"MD","massachusetts":"MA","michigan":"MI","minnesota":"MN",
 "mississippi":"MS","missouri":"MO","montana":"MT","nebraska":"NE","nevada":"NV",
 "new hampshire":"NH","new jersey":"NJ","new mexico":"NM","new york":"NY","north carolina":"NC",
 "north dakota":"ND","ohio":"OH","oklahoma":"OK","oregon":"OR","pennsylvania":"PA",
 "rhode island":"RI","south carolina":"SC","south dakota":"SD","tennessee":"TN","texas":"TX",
 "utah":"UT","vermont":"VT","virginia":"VA","washington":"WA","west virginia":"WV",
 "wisconsin":"WI","wyoming":"WY"}
US_STATES = set(STATE_ABBR.values())
NON_US = {"canada","ontario","alberta","british columbia","quebec","manitoba"}  # region full-name markers

EXCLUDE_SLUGS = {"accessibility-statement","activities","blog","locations","about","contact","jobs",
    "franchis","privacy","terms","faq","programs","events","gift","careers","our-story","ownership",
    "accessibility","blog-page","find-a-school","swim-lessons","summer-camps","pricing","reviews",
    "scholarships","special-needs","safety","the-goldfish-difference","why-goldfish","news"}


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def fetch(url, force=False):
    name = re.sub(r"[^a-zA-Z0-9]+", "_", url).strip("_") + ".html"
    path = os.path.join(CACHE, name)
    if os.path.exists(path) and not force:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    os.makedirs(CACHE, exist_ok=True)
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=25)
        body = r.read().decode("utf-8", "replace")
        with open(path, "w", encoding="utf-8") as f:
            f.write(body)
        time.sleep(1.1)
        return body
    except Exception as e:
        print("  fetch ERR", url, e, flush=True)
        return None


def extract_addr(html):
    """Return dict with address/name/phone from JSON-LD. Prefer the entry that
    has a 10-digit US phone; fall back to any entry with an address."""
    best = None
    for m in re.finditer(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', html, re.S):
        raw = re.sub(r"[\x00-\x1f]", "", m.group(1))
        try:
            d = json.loads(raw)
        except Exception:
            continue
        items = d if isinstance(d, list) else [d]
        for it in items:
            if isinstance(it, dict) and isinstance(it.get("address"), dict):
                a = it["address"]
                if a.get("addressRegion") and a.get("addressLocality"):
                    rec = {"address": a, "name": it.get("name"), "phone": it.get("telephone")}
                    if rec["phone"]:
                        digits = re.sub(r"[^0-9]", "", rec["phone"])
                        if len(digits) == 10:
                            return rec  # clean US phone -> best
                    if best is None:
                        best = rec
    return best


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--geocode", action="store_true", help="geocode (slow); else generate list + backfill cache only")
    args = ap.parse_args()

    t = fetch("https://www.goldfishswimschool.com/sitemap.xml")
    if not t:
        print("sitemap fetch failed", flush=True)
        sys.exit(1)
    locs = [l.strip() for l in re.findall(r"<loc>(.*?)</loc>", t)]
    slugs = set()
    for l in locs:
        m = re.match(r"https://(?:www\.)?goldfishswimschool\.com/([a-z0-9\-]+)/?$", l)
        if m:
            slug = m.group(1)
            if slug in EXCLUDE_SLUGS:
                continue
            if slug.startswith(("blog", "locations")):
                continue
            slugs.add(slug)
    print(f"Goldfish candidate location slugs: {len(slugs)}", flush=True)

    camps = []
    for slug in sorted(slugs):
        url = f"https://www.goldfishswimschool.com/{slug}/"
        html = fetch(url)
        if not html:
            continue
        info = extract_addr(html)
        if not info:
            print("  NO ADDR", slug, flush=True)
            continue
        a = info["address"]
        locality = (a.get("addressLocality") or "").strip()
        region_full = (a.get("addressRegion") or "").strip()
        region = STATE_ABBR.get(region_full.lower()) or region_full
        if region not in US_STATES:
            continue  # non-US (Canada etc.)
        if region_full.lower() in NON_US:
            continue
        zipcode = re.sub(r"[\ufeff\s]", "", (a.get("postalCode") or "")).strip()
        street = (a.get("streetAddress") or "").strip()
        if not locality:
            continue
        phone = info.get("phone") or None
        if phone:
            digits = re.sub(r"[^0-9]", "", phone)
            if len(digits) == 11 and digits.startswith("1"):
                digits = digits[1:]
            if len(digits) == 10:
                phone = f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
            else:
                phone = None
        name = f"Goldfish Swim School {locality}"
        camps.append({
            "id": f"goldfish_{slug}",
            "name": name,
            "city": locality,
            "state": region,
            "zip": zipcode or None,
            "address": street or None,
            "lat": None,
            "lng": None,
            "type": "day",
            "price": None,
            "rating": None,
            "reviewCount": None,
            "ageMin": None,
            "ageMax": None,
            "season": "summer",
            "theme": "Sports",
            "beforeCare": None,
            "afterCare": None,
            "shuttle": None,
            "weeks": None,
            "phone": phone,
            "email": None,
            "website": "https://www.goldfishswimschool.com",
            "description": "Goldfish Swim School swim lessons & summer camp.",
            "acaVerified": False,
            "source": "franchise_locator:goldfishswimschool.com",
            "sourceUrl": url,
            "verifiedAt": "2026-08-06",
            "verificationMethod": "location_listing",
            "unverified": False,
        })
        print("  ADD", name, locality, region, flush=True)

    print(f"Goldfish: {len(camps)} camps", flush=True)

    # backfill coords from cache
    cache_path = os.path.join(ROOT, "scrapers", "geocode_cache.json")
    cache = {}
    if os.path.exists(cache_path):
        cache = json.load(open(cache_path, encoding="utf-8"))
    for c in camps:
        ck = f"{c['city']}|{c['state']}"
        if ck in cache:
            c["lat"], c["lng"] = cache[ck][0], cache[ck][1]
    nocoord = sum(1 for c in camps if not c["lat"])
    print(f"backfilled from cache; still missing coords: {nocoord}", flush=True)

    if args.geocode:
        for c in camps:
            if c.get("lat") and c.get("lng"):
                continue
            ck = f"{c['city']}|{c['state']}"
            query = f"{c['city']}, {c['state']}, USA"
            url = "https://nominatim.openstreetmap.org/search?" + "q=" + urllib.parse.quote(query) + "&format=json&limit=1"
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "CampFind-v9/1.0"})
                data = json.loads(urllib.request.urlopen(req, timeout=20).read().decode("utf-8"))
                if data:
                    res = (float(data[0]["lat"]), float(data[0]["lon"]))
                    c["lat"], c["lng"] = res[0], res[1]
                    cache[ck] = res
                    json.dump(cache, open(cache_path, "w", encoding="utf-8"), ensure_ascii=False)
                    time.sleep(1.1)
            except Exception as e:
                print("  GEO ERR", c["city"], e, flush=True)

    out = {"source": "CampFind v9 Goldfish Swim School location expansion (official sitemap)",
           "count": len(camps), "camps": camps}
    fn = os.path.join(ROOT, "app", "aca_camps_brands_v9.json")
    json.dump(out, open(fn, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"\nwrote {len(camps)} Goldfish camps -> {fn}", flush=True)


if __name__ == "__main__":
    main()
