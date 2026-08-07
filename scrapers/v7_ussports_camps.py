#!/usr/bin/env python3
"""
CampFind v7 — US Sports Camps full destination expansion.

Source: official sitemap (ussportscamps.com/sitemap.xml) -> every
/destinations/{state}/{city} slug = a real camp destination. The v3 expansion
capped at ~350; this adds the full set (1,100+ US destinations).

R2 = the destination URL itself; R1 = only city/state from the brand's own
sitemap, everything else null/False.
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

STATE_FULL = {"alabama":"AL","alaska":"AK","arizona":"AZ","arkansas":"AR","california":"CA",
 "colorado":"CO","connecticut":"CT","delaware":"DE","florida":"FL","georgia":"GA","hawaii":"HI",
 "idaho":"ID","illinois":"IL","indiana":"IN","iowa":"IA","kansas":"KS","kentucky":"KY",
 "louisiana":"LA","maine":"ME","maryland":"MD","massachusetts":"MA","michigan":"MI","minnesota":"MN",
 "mississippi":"MS","missouri":"MO","montana":"MT","nebraska":"NE","nevada":"NV","new-hampshire":"NH",
 "new-jersey":"NJ","new-mexico":"NM","new-york":"NY","north-carolina":"NC","north-dakota":"ND",
 "ohio":"OH","oklahoma":"OK","oregon":"OR","pennsylvania":"PA","rhode-island":"RI",
 "south-carolina":"SC","south-dakota":"SD","tennessee":"TN","texas":"TX","utah":"UT","vermont":"VT",
 "virginia":"VA","washington":"WA","west-virginia":"WV","wisconsin":"WI","wyoming":"WY"}

# "St. Petersburg" -> "St. Petersburg"; normalize known title-case artifacts
CITY_FIX = {
    "Arlington Height": "Arlington Heights",
    "St. Petersburg": "St. Petersburg",
    "Mt. Pleasant": "Mt. Pleasant",
    "Fort Collins": "Fort Collins",
    "New York City": "New York",
    "San Luis Obispo": "San Luis Obispo",
    "Kansas City": "Kansas City",
    "St. Louis": "St. Louis",
    "El Paso": "El Paso",
    "Las Vegas": "Las Vegas",
    "Salt Lake City": "Salt Lake City",
    "New Orleans": "New Orleans",
    "Virginia Beach": "Virginia Beach",
    "Port Washington": "Port Washington",
}


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def fetch(url):
    name = re.sub(r"[^a-zA-Z0-9]+", "_", url).strip("_") + ".html"
    path = os.path.join(CACHE, name)
    if os.path.exists(path):
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


def geocode_all(camps):
    cache_path = os.path.join(ROOT, "scrapers", "geocode_cache.json")
    cache = {}
    if os.path.exists(cache_path):
        cache = json.load(open(cache_path, encoding="utf-8"))
    fixed = 0
    for c in camps:
        if c.get("lat") and c.get("lng"):
            continue
        ck = f"{c['city']}|{c['state']}"
        if ck in cache:
            c["lat"], c["lng"] = cache[ck][0], cache[ck][1]
            fixed += 1
            continue
        query = f"{c['city']}, {c['state']}, USA"
        url = "https://nominatim.openstreetmap.org/search?" + "q=" + urllib.parse.quote(query) + "&format=json&limit=1"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "CampFind-v7/1.0"})
            data = json.loads(urllib.request.urlopen(req, timeout=20).read().decode("utf-8"))
            if data:
                res = (float(data[0]["lat"]), float(data[0]["lon"]))
                c["lat"], c["lng"] = res[0], res[1]
                cache[ck] = res
                json.dump(cache, open(cache_path, "w", encoding="utf-8"), ensure_ascii=False)
                fixed += 1
                time.sleep(1.1)
        except Exception as e:
            print("  GEO ERR", c["city"], e, flush=True)
    print(f"geocoded {fixed} camps", flush=True)
    return camps


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--geocode", action="store_true", help="geocode (slow); else just generate list")
    args = ap.parse_args()

    # fetch sitemap index (may list sub-sitemaps)
    t = fetch("https://www.ussportscamps.com/sitemap.xml")
    if not t:
        print("sitemap fetch failed", flush=True)
        sys.exit(1)
    locs = [l.strip() for l in re.findall(r"<loc>(.*?)</loc>", t)]
    # sitemap index -> sub-sitemaps
    all_locs = []
    for l in locs:
        if l.endswith(".xml") and "destination" in l:
            sub = fetch(l)
            if sub:
                all_locs.extend(re.findall(r"<loc>(.*?)</loc>", sub))
    if not all_locs:
        all_locs = locs

    dests = []
    seen = set()
    for u in all_locs:
        m = re.match(r"https://www\.ussportscamps\.com/destinations/([a-z\-]+)/([a-z0-9\-]+)$", u)
        if m and m.group(1) in STATE_FULL:
            city = m.group(2).replace("-", " ").title()
            city = CITY_FIX.get(city, city)
            st = STATE_FULL[m.group(1)]
            key = (slugify(city), st)
            if key in seen:
                continue
            seen.add(key)
            dests.append((city, st, u))
    print(f"US Sports Camps destinations: {len(dests)}", flush=True)

    # existing ussc camps (dedupe)
    existing = set()
    src_path = os.path.join(ROOT, "app", "aca_camps.json")
    if os.path.exists(src_path):
        d = json.load(open(src_path, encoding="utf-8"))["camps"]
        for c in d:
            if "ussportscamps" in c.get("source", ""):
                existing.add((slugify(c["city"]), (c.get("state") or "").upper()))
    # also consider previously-generated v7 list
    v7_path = os.path.join(ROOT, "app", "aca_camps_brands_v7.json")
    if os.path.exists(v7_path):
        v7 = json.load(open(v7_path, encoding="utf-8"))["camps"]
        for c in v7:
            existing.add((slugify(c["city"]), c["state"]))
    print(f"existing ussc in dataset: {len(existing)}", flush=True)

    camps = []
    for city, st, url in dests:
        key = (slugify(city), st)
        if key in existing:
            continue
        existing.add(key)
        camps.append({
            "id": f"ussportscamps_{slugify(city)}_{st.lower()}",
            "name": f"US Sports Camps {city}",
            "city": city,
            "state": st,
            "zip": None,
            "address": None,
            "lat": None,
            "lng": None,
            "type": "day",
            "price": None,
            "rating": None,
            "reviewCount": None,
            "ageMin": None,
            "ageMax": None,
            "beforeCare": None,
            "afterCare": None,
            "shuttle": None,
            "weeks": None,
            "phone": None,
            "email": None,
            "website": "https://www.ussportscamps.com",
            "description": None,
            "season": "summer",
            "acaVerified": False,
            "source": "franchise_locator:ussportscamps.com",
            "sourceUrl": url,
            "verifiedAt": "2026-08-06",
            "verificationMethod": "location_listing",
            "unverified": False,
        })
    print(f"new US Sports Camps to add: {len(camps)}", flush=True)

    if args.geocode:
        geocode_all(camps)
    else:
        # backfill coords from existing cache where possible
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

    out = {"source": "CampFind v7 US Sports Camps full destination expansion (official sitemap)",
           "count": len(camps), "camps": camps}
    fn = os.path.join(ROOT, "app", "aca_camps_brands_v7.json")
    json.dump(out, open(fn, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"wrote {len(camps)} new US Sports Camps -> {fn}", flush=True)


if __name__ == "__main__":
    main()
