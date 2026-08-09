#!/usr/bin/env python3
"""
CampFind v21 — new Snapology franchise locations.

Source: official snapology.com franchise_sites sitemap. R2 = the franchise URL.
"""
import json
import os
import re
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"}

US_STATES = {"alabama","alaska","arizona","arkansas","california","colorado","connecticut","delaware","florida","georgia","hawaii","idaho","illinois","indiana","iowa","kansas","kentucky","louisiana","maine","maryland","massachusetts","michigan","minnesota","mississippi","missouri","montana","nebraska","nevada","new-hampshire","new-jersey","new-mexico","new-york","north-carolina","north-dakota","ohio","oklahoma","oregon","pennsylvania","rhode-island","south-carolina","south-dakota","tennessee","texas","utah","vermont","virginia","washington","west-virginia","wisconsin","wyoming"}
STATE_ABBR = {"alabama":"AL","alaska":"AK","arizona":"AZ","arkansas":"AR","california":"CA","colorado":"CO","connecticut":"CT","delaware":"DE","florida":"FL","georgia":"GA","hawaii":"HI","idaho":"ID","illinois":"IL","indiana":"IN","iowa":"IA","kansas":"KS","kentucky":"KY","louisiana":"LA","maine":"ME","maryland":"MD","massachusetts":"MA","michigan":"MI","minnesota":"MN","mississippi":"MS","missouri":"MO","montana":"MT","nebraska":"NE","nevada":"NV","new-hampshire":"NH","new-jersey":"NJ","new-mexico":"NM","new-york":"NY","north-carolina":"NC","north-dakota":"ND","ohio":"OH","oklahoma":"OK","oregon":"OR","pennsylvania":"PA","rhode-island":"RI","south-carolina":"SC","south-dakota":"SD","tennessee":"TN","texas":"TX","utah":"UT","vermont":"VT","virginia":"VA","washington":"WA","west-virginia":"WV","wisconsin":"WI","wyoming":"WY"}

# fix spliced city labels -> geocodable city
CITY_FIX = {
    "colorado-springs-north": "Colorado Springs",
}


def main():
    t = urllib.request.urlopen(urllib.request.Request("https://www.snapology.com/franchise_sites-sitemap.xml", headers=UA), timeout=25).read().decode("utf-8", "replace")
    bases = set()
    for l in re.findall(r"<loc>(.*?)</loc>", t):
        m = re.match(r"https://www\.snapology\.com/([a-z0-9\-]+)/(?:camps|programs|/?)$", l)
        if m:
            bases.add(m.group(1))
    us_slugs = [s for s in bases if s.split("-")[0] in US_STATES]

    src = os.path.join(ROOT, "app", "aca_camps.json")
    d = json.load(open(src, encoding="utf-8"))["camps"]
    existing = set(c["id"].replace("snapology_", "") for c in d if "snapology" in c.get("source", ""))
    new_slugs = sorted(s for s in us_slugs if s not in existing)
    print(f"Snapology new locations: {len(new_slugs)}", flush=True)

    geo = {}
    gc = os.path.join(ROOT, "scrapers", "geocode_cache.json")
    if os.path.exists(gc):
        for k, v in json.load(open(gc, encoding="utf-8")).items():
            p = k.split("|")
            if len(p) >= 2:
                geo.setdefault((p[0], p[1]), v)

    camps = []
    for slug in new_slugs:
        state_word = slug.split("-")[0]
        city = " ".join(slug.split("-")[1:]).title()
        city = CITY_FIX.get(slug, city)
        st = STATE_ABBR[state_word]
        coords = geo.get((city, st))
        camps.append({
            "id": f"snapology_{slug}",
            "name": f"Snapology {city}",
            "city": city,
            "state": st,
            "zip": None,
            "address": None,
            "lat": coords[0] if coords else None,
            "lng": coords[1] if coords else None,
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
            "website": "https://www.snapology.com",
            "description": "Snapology STEM, robotics & LEGO camps.",
            "acaVerified": False,
            "source": "franchise_locator:snapology.com",
            "sourceUrl": f"https://www.snapology.com/{slug}/",
            "verifiedAt": "2026-08-09",
            "verificationMethod": "location_listing",
            "unverified": False,
        })
        print(f"  ADD {city}, {st}", flush=True)
    out = {"source": "CampFind v21 new Snapology franchise locations (official sitemap)",
           "count": len(camps), "camps": camps}
    fn = os.path.join(ROOT, "app", "aca_camps_brands_v21.json")
    json.dump(out, open(fn, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"wrote {len(camps)} camps -> {fn}", flush=True)


if __name__ == "__main__":
    main()
