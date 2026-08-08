#!/usr/bin/env python3
"""
CampFind v12 — Bricks 4 Kidz US franchise expansion.

Source: official franchise portal (us.bricks4kidznow.com/franchise_maplocations.php)
returns all franchise territories with city/zip/lat/lng. R2 = the marker record
from the brand's own portal.

Filters to US only (US zip + lon/lat in US bounding box), dedupes by objectid
(each franchise emits one row per served zip), keeps the first territory per
franchise as the location anchor.
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"}
US_ZIP_RE = re.compile(r"^\d{5}$")

STATE_ABBR = {"alabama":"AL","alaska":"AK","arizona":"AZ","arkansas":"AR","california":"CA",
 "colorado":"CO","connecticut":"CT","delaware":"DE","florida":"FL","georgia":"GA","hawaii":"HI",
 "idaho":"ID","illinois":"IL","indiana":"IN","iowa":"IA","kansas":"KS","kentucky":"KY",
 "louisiana":"LA","maine":"ME","maryland":"MD","massachusetts":"MA","michigan":"MI","minnesota":"MN",
 "mississippi":"MS","missouri":"MO","montana":"MT","nebraska":"NE","nevada":"NV","new-hampshire":"NH",
 "new-jersey":"NJ","new-mexico":"NM","new-york":"NY","north-carolina":"NC","north-dakota":"ND",
 "ohio":"OH","oklahoma":"OK","oregon":"OR","pennsylvania":"PA","rhode-island":"RI",
 "south-carolina":"SC","south-dakota":"SD","tennessee":"TN","texas":"TX","utah":"UT","vermont":"VT",
 "virginia":"VA","washington":"WA","west-virginia":"WV","wisconsin":"WI","wyoming":"WY",
 "district of columbia":"DC"}


def to_abbr(s):
    if not s:
        return None
    s = s.strip()
    if len(s) == 2 and s.isupper():
        return s
    return STATE_ABBR.get(s.lower())


def is_us(m):
    z = (m.get("territoryzip") or "").strip()
    lon = m.get("addresslong")
    lat = m.get("addresslat")
    try:
        lon = float(str(lon).replace("°", "").strip())
        lat = float(str(lat).replace("°", "").strip())
    except Exception:
        return False
    if not (-125 <= lon <= -65 and 18 <= lat <= 72):
        return False
    # require US-format zip (5 digits) — Canadian zips like L5N/H3W excluded
    if not US_ZIP_RE.match(z):
        return False
    return True


def main():
    url = "https://us.bricks4kidznow.com/franchise_maplocations.php?getmarkers=1&lat=39.8283&lng=-98.5795"
    try:
        req = urllib.request.Request(url, headers=UA)
        markers = json.loads(urllib.request.urlopen(req, timeout=25).read().decode("utf-8", "replace"))
    except Exception as e:
        print("fetch failed", e, flush=True)
        sys.exit(1)

    us = [m for m in markers if is_us(m)]
    seen = {}
    for m in us:
        oid = m.get("objectid")
        if oid not in seen:
            seen[oid] = m
    print(f"markers {len(markers)} -> US {len(us)} -> unique franchises {len(seen)}", flush=True)

    camps = []
    for oid, m in sorted(seen.items()):
        city = (m.get("objectname") or "").strip()
        zipcode = (m.get("territoryzip") or "").strip().split(",")[0].strip()
        try:
            lat = float(str(m.get("addresslat")).replace("°", "").strip())
            lng = float(str(m.get("addresslong")).replace("°", "").strip())
        except Exception:
            lat = lng = None
        if not city or not lat or not lng:
            continue
        camps.append({
            "id": f"bricks4kidz_{oid}",
            "name": f"Bricks 4 Kidz {city}",
            "city": city,
            "state": None,  # filled by geocode below
            "zip": zipcode or None,
            "address": None,
            "lat": lat,
            "lng": lng,
            "type": "day",
            "price": None,
            "rating": None,
            "reviewCount": None,
            "ageMin": None,
            "ageMax": None,
            "season": "summer",
            "theme": "STEM",
            "beforeCare": None,
            "afterCare": None,
            "shuttle": None,
            "weeks": None,
            "phone": None,
            "email": None,
            "website": "https://bricks4kidz.com",
            "description": "Bricks 4 Kidz LEGO & STEM camps and classes.",
            "acaVerified": False,
            "source": "franchise_locator:bricks4kidz.com",
            "sourceUrl": url,
            "verifiedAt": "2026-08-06",
            "verificationMethod": "location_listing",
            "unverified": False,
        })

    # reverse-geocode state from coordinates using geocode cache or Nominatim reverse
    cache_path = os.path.join(ROOT, "scrapers", "reverse_cache.json")
    rcache = {}
    if os.path.exists(cache_path):
        rcache = json.load(open(cache_path, encoding="utf-8"))
    for c in camps:
        key = f"{c['lat']:.4f},{c['lng']:.4f}"
        if key in rcache:
            c["state"] = to_abbr(rcache[key])
            continue
        url2 = "https://nominatim.openstreetmap.org/reverse?" + urllib.parse.urlencode({"lat": c["lat"], "lon": c["lng"], "format": "json"})
        try:
            req = urllib.request.Request(url2, headers={"User-Agent": "CampFind-v12/1.0"})
            rj = json.loads(urllib.request.urlopen(req, timeout=20).read().decode("utf-8"))
            state = rj.get("address", {}).get("state_code") or rj.get("address", {}).get("state")
            rcache[key] = state
            c["state"] = to_abbr(state)
            json.dump(rcache, open(cache_path, "w", encoding="utf-8"), ensure_ascii=False)
            time.sleep(1.1)
        except Exception as e:
            print("  rev geo err", c["city"], e, flush=True)
    print(f"state filled: {sum(1 for c in camps if c['state'])}/{len(camps)}", flush=True)

    # drop any without a valid 2-letter US state
    valid_states = {"AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA","KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT","VA","WA","WV","WI","WY","DC"}
    kept = [c for c in camps if c.get("state") in valid_states]
    print(f"kept with US state: {len(kept)}", flush=True)

    out = {"source": "CampFind v12 Bricks 4 Kidz US franchise expansion (official portal)",
           "count": len(kept), "camps": kept}
    fn = os.path.join(ROOT, "app", "aca_camps_brands_v12.json")
    json.dump(out, open(fn, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"wrote {len(kept)} Bricks 4 Kidz camps -> {fn}", flush=True)


if __name__ == "__main__":
    main()
