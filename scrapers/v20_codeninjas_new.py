#!/usr/bin/env python3
"""
CampFind v20 — new Code Ninjas franchise locations.

Source: official codeninjas.com sitemap (location slugs). The v3 expansion
covered the original set; new franchise locations have since opened. R2 = the
official sitemap location URL.
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

STATE_FULL = {"alabama":"AL","alaska":"AK","arizona":"AZ","arkansas":"AR","california":"CA","colorado":"CO","connecticut":"CT","delaware":"DE","florida":"FL","georgia":"GA","hawaii":"HI","idaho":"ID","illinois":"IL","indiana":"IN","iowa":"IA","kansas":"KS","kentucky":"KY","louisiana":"LA","maine":"ME","maryland":"MD","massachusetts":"MA","michigan":"MI","minnesota":"MN","mississippi":"MS","missouri":"MO","montana":"MT","nebraska":"NE","nevada":"NV","new-hampshire":"NH","new-jersey":"NJ","new-mexico":"NM","new-york":"NY","north-carolina":"NC","north-dakota":"ND","ohio":"OH","oklahoma":"OK","oregon":"OR","pennsylvania":"PA","rhode-island":"RI","south-carolina":"SC","south-dakota":"SD","tennessee":"TN","texas":"TX","utah":"UT","vermont":"VT","virginia":"VA","washington":"WA","west-virginia":"WV","wisconsin":"WI","wyoming":"WY"}

# Exclude test/placeholder locations
EXCLUDE = {"test center uk"}


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "", s.lower())


def main():
    t = urllib.request.urlopen(urllib.request.Request("https://www.codeninjas.com/sitemap.xml", headers=UA), timeout=25).read().decode("utf-8", "replace")
    locs = set(re.findall(r"<loc>(.*?)</loc>", t))
    cn_locs = {}
    for u in locs:
        m = re.match(r"https://www\.codeninjas\.com/([a-z]{2})-([a-z0-9\-]+?)(?:/|$)", u)
        if m and m.group(1).upper() in STATE_FULL.values():
            city = m.group(2).replace("-", " ").title()
            st = m.group(1).upper()
            if city.lower() in EXCLUDE:
                continue
            cn_locs.setdefault((city, st), u)

    # existing codeninjas
    src = os.path.join(ROOT, "app", "aca_camps.json")
    d = json.load(open(src, encoding="utf-8"))["camps"]
    existing = set((c["city"], c["state"]) for c in d if "codeninjas" in c.get("source", ""))
    new = sorted(set(cn_locs) - existing)
    print(f"Code Ninjas new locations to add: {len(new)}", flush=True)

    # geocode cache
    geo = {}
    gc = os.path.join(ROOT, "scrapers", "geocode_cache.json")
    if os.path.exists(gc):
        for k, v in json.load(open(gc, encoding="utf-8")).items():
            p = k.split("|")
            if len(p) >= 2:
                geo.setdefault((p[0], p[1]), v)

    camps = []
    for city, st in new:
        c = {
            "id": f"codeninjas_{slugify(city)}_{st.lower()}",
            "name": f"Code Ninjas {city}",
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
            "website": "https://www.codeninjas.com",
            "description": None,
            "season": "summer",
            "acaVerified": False,
            "source": "franchise_locator:codeninjas.com",
            "sourceUrl": cn_locs[(city, st)],
            "verifiedAt": "2026-08-09",
            "verificationMethod": "location_listing",
            "unverified": False,
        }
        if (city, st) in geo:
            c["lat"], c["lng"] = geo[(city, st)][0], geo[(city, st)][1]
        camps.append(c)
        print(f"  ADD {city}, {st}", flush=True)

    out = {"source": "CampFind v20 new Code Ninjas franchise locations (official sitemap)",
           "count": len(camps), "camps": camps}
    fn = os.path.join(ROOT, "app", "aca_camps_brands_v20.json")
    json.dump(out, open(fn, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"wrote {len(camps)} camps -> {fn}", flush=True)


if __name__ == "__main__":
    main()
