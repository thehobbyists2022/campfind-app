#!/usr/bin/env python3
"""
CampFind v2 — geocode camps that carry sentinel/default coordinates.
Uses Nominatim (OSM) with rate limiting + cache. Sets lat/lng from real
city+state+zip. Skips already-fine coordinates.
"""
import json
import os
import re
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = {"User-Agent": "CampFind-Geocoder/2.0 (contact: parent-friendly directory)"}
CACHE = os.path.join(ROOT, "scrapers", "geocode_cache.json")

SENTINELS = {
    (34.0522, -118.2437), (37.7749, -122.4194), (37.3382, -121.8863),
    (33.6846, -117.8265), (32.7157, -117.1611), (33.1959, -117.3795),
}

def load_cache():
    if os.path.exists(CACHE):
        return json.load(open(CACHE, encoding="utf-8"))
    return {}

def save_cache(cache):
    json.dump(cache, open(CACHE, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

def geocode(city, state, zipcode):
    cache = load_cache()
    key = f"{city}|{state}|{zipcode}"
    if key in cache:
        return cache[key], cache
    query = f"{city}, {state} {zipcode}, USA" if zipcode else f"{city}, {state}, USA"
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(
        {"q": query, "format": "json", "limit": 1})
    try:
        req = urllib.request.Request(url, headers=UA)
        data = json.loads(urllib.request.urlopen(req, timeout=20).read().decode("utf-8"))
        if data:
            lat = float(data[0]["lat"]); lng = float(data[0]["lon"])
            cache[key] = (lat, lng)
            save_cache(cache)
            return (lat, lng), cache
    except Exception as e:
        pass
    time.sleep(1.1)
    return None, cache

def main():
    fn = os.path.join(ROOT, "app", "aca_camps_v2.json")
    data = json.load(open(fn, encoding="utf-8"))
    camps = data["camps"]
    fixed = 0
    skipped = 0
    for c in camps:
        lat, lng = c.get("lat"), c.get("lng")
        if lat is not None and lng is not None and (round(lat, 4), round(lng, 4)) not in SENTINELS:
            skipped += 1
            continue
        res, _ = geocode(c.get("city", ""), c.get("state", ""), c.get("zip", ""))
        if res:
            c["lat"], c["lng"] = res[0], res[1]
            fixed += 1
            print(f"  fixed {c['name'][:40]:40s} {c['city']}, {c['state']} -> {res[0]:.4f},{res[1]:.4f}")
        else:
            print(f"  NOGEO {c['name'][:40]:40s} {c['city']}, {c['state']} {c.get('zip','')}")
        time.sleep(1.1)
    json.dump(data, open(fn, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"\ngeocoded {fixed}, kept {skipped} existing coords")


if __name__ == "__main__":
    main()
