#!/usr/bin/env python3
"""
CampFind v4 — City-run (municipal) camps expansion.

Sources: official city Parks & Recreation / Youth Programs pages (.gov / city domains).
Every camp is verified against the city's own official page (R2 location-level proof).

Schema additions:
  provider: "city"   (new field, distinguishes municipal-run camps)
  sourceUrl: official city page
  phone: from official page only, else null
"""
import json
import os
import re
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = {"User-Agent": "CampFind-V4-CityCamps/1.0"}
GEO_CACHE = os.path.join(ROOT, "scrapers", "geocode_cache.json")

def geocode(city, state):
    cache = json.load(open(GEO_CACHE, encoding="utf-8")) if os.path.exists(GEO_CACHE) else {}
    key = f"{city}|{state}"
    if key in cache:
        return cache[key]
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(
        {"q": f"{city}, {state}, USA", "format": "json", "limit": 1})
    try:
        req = urllib.request.Request(url, headers=UA)
        d = json.loads(urllib.request.urlopen(req, timeout=20).read().decode("utf-8"))
        if d:
            res = (float(d[0]["lat"]), float(d[0]["lon"]))
            cache[key] = res
            json.dump(cache, open(GEO_CACHE, "w", encoding="utf-8"))
            time.sleep(1.1)
            return res
    except Exception:
        pass
    return None

# ---------------------------------------------------------------------------
# Curated city-run camps, verified against official city pages (2026-08-04).
# Each entry: name, city, state, zip, location notes, season, age range,
# phone (from official page), website (city youth/recreation page), sourceUrl.
# ---------------------------------------------------------------------------
CITY_CAMPS = [
    # --- Oceanside, CA (source: ci.oceanside.ca.us/government/parks-recreation/youth-programs) ---
    {
        "name": "Sunsational Summer Camp - John Landes",
        "city": "Oceanside", "state": "CA", "zip": "92057",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 6, "ageMax": 12,
        "website": "https://www.ci.oceanside.ca.us/government/parks-recreation/youth-programs",
        "sourceUrl": "https://www.ci.oceanside.ca.us/government/parks-recreation/youth-programs",
        "phone": "(760) 435-5545",
        "note": "City of Oceanside Sunsational Summer Camp at John Landes Recreation Center.",
    },
    {
        "name": "Sunsational Summer Camp - Melba Bishop",
        "city": "Oceanside", "state": "CA", "zip": "92056",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 6, "ageMax": 12,
        "website": "https://www.ci.oceanside.ca.us/government/parks-recreation/youth-programs",
        "sourceUrl": "https://www.ci.oceanside.ca.us/government/parks-recreation/youth-programs",
        "phone": "(760) 435-5550",
        "note": "City of Oceanside Sunsational Summer Camp at Melba Bishop Recreation Center.",
    },
    {
        "name": "Sunsational Summer Camp - Joe Balderrama",
        "city": "Oceanside", "state": "CA", "zip": "92054",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 6, "ageMax": 12,
        "website": "https://www.ci.oceanside.ca.us/government/parks-recreation/youth-programs",
        "sourceUrl": "https://www.ci.oceanside.ca.us/government/parks-recreation/youth-programs",
        "phone": "(760) 435-5530",
        "note": "City of Oceanside Sunsational Summer Camp at Joe Balderrama Recreation Center.",
    },
    {
        "name": "Beach & Ball Summer Camp",
        "city": "Oceanside", "state": "CA", "zip": "92054",
        "season": "summer", "theme": "Sports", "type": "day",
        "ageMin": 5, "ageMax": 14,
        "website": "https://www.ci.oceanside.ca.us/government/parks-recreation/youth-programs",
        "sourceUrl": "https://www.ci.oceanside.ca.us/government/parks-recreation/youth-programs",
        "phone": "(760) 435-5233",
        "note": "City of Oceanside Beach & Ball Camp at Junior Seau Beach Community Center.",
    },
    {
        "name": "Spring Break Camp - John Landes",
        "city": "Oceanside", "state": "CA", "zip": "92057",
        "season": "spring", "theme": "General", "type": "day",
        "ageMin": 6, "ageMax": 12,
        "website": "https://www.ci.oceanside.ca.us/government/parks-recreation/youth-programs",
        "sourceUrl": "https://www.ci.oceanside.ca.us/government/parks-recreation/youth-programs",
        "phone": "(760) 435-5545",
        "note": "City of Oceanside Spring Break Camp.",
    },
    {
        "name": "Spring Break Camp - Melba Bishop",
        "city": "Oceanside", "state": "CA", "zip": "92056",
        "season": "spring", "theme": "General", "type": "day",
        "ageMin": 6, "ageMax": 12,
        "website": "https://www.ci.oceanside.ca.us/government/parks-recreation/youth-programs",
        "sourceUrl": "https://www.ci.oceanside.ca.us/government/parks-recreation/youth-programs",
        "phone": "(760) 435-5550",
        "note": "City of Oceanside Spring Break Camp.",
    },
    {
        "name": "After-School Program - John Landes",
        "city": "Oceanside", "state": "CA", "zip": "92057",
        "season": "fall", "theme": "General", "type": "day",
        "ageMin": 6, "ageMax": 11,
        "website": "https://www.ci.oceanside.ca.us/government/parks-recreation/youth-programs",
        "sourceUrl": "https://www.ci.oceanside.ca.us/government/parks-recreation/youth-programs",
        "phone": "(760) 435-5545",
        "note": "City of Oceanside After-School Program (school-year/fall).",
    },
    {
        "name": "After-School Program - Melba Bishop",
        "city": "Oceanside", "state": "CA", "zip": "92056",
        "season": "fall", "theme": "General", "type": "day",
        "ageMin": 6, "ageMax": 11,
        "website": "https://www.ci.oceanside.ca.us/government/parks-recreation/youth-programs",
        "sourceUrl": "https://www.ci.oceanside.ca.us/government/parks-recreation/youth-programs",
        "phone": "(760) 435-5550",
        "note": "City of Oceanside After-School Program (school-year/fall).",
    },
    {
        "name": "After-School Program - Joe Balderrama",
        "city": "Oceanside", "state": "CA", "zip": "92054",
        "season": "fall", "theme": "General", "type": "day",
        "ageMin": 6, "ageMax": 11,
        "website": "https://www.ci.oceanside.ca.us/government/parks-recreation/youth-programs",
        "sourceUrl": "https://www.ci.oceanside.ca.us/government/parks-recreation/youth-programs",
        "phone": "(760) 435-5530",
        "note": "City of Oceanside After-School Program (school-year/fall).",
    },

    # --- Escondido, CA (source: escondido.org recreation camps page) ---
    {
        "name": "Escondido Discovery Camp",
        "city": "Escondido", "state": "CA", "zip": "92025",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 12,
        "website": "https://www.escondido.org/735/Camps",
        "sourceUrl": "https://www.escondido.org/735/Camps",
        "phone": None,
        "note": "City of Escondido Discovery Camp summer program.",
    },
    {
        "name": "Escondido Specialty Camp",
        "city": "Escondido", "state": "CA", "zip": "92025",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 12,
        "website": "https://www.escondido.org/735/Camps",
        "sourceUrl": "https://www.escondido.org/735/Camps",
        "phone": None,
        "note": "City of Escondido Specialty Camp summer program.",
    },
]

def main():
    camps = []
    for c in CITY_CAMPS:
        coords = geocode(c["city"], c["state"])
        if not coords:
            print("  NOGEO", c["name"])
            continue
        camp = {
            "id": f"city_{c['city'].lower().replace(' ', '')}_{c['name'].lower().replace(' ', '')[:30]}",
            "name": c["name"], "city": c["city"], "state": c["state"],
            "zip": c.get("zip"), "address": None,
            "lat": coords[0], "lng": coords[1],
            "type": c["type"], "price": None, "rating": None, "reviewCount": None,
            "ageMin": c.get("ageMin"), "ageMax": c.get("ageMax"),
            "season": c["season"], "theme": c["theme"],
            "beforeCare": None, "afterCare": None, "shuttle": None, "weeks": None,
            "phone": c.get("phone"), "email": None,
            "website": c["website"], "description": c.get("note"),
            "acaVerified": False, "provider": "city",
            "source": "city_recreation:official",
            "sourceUrl": c["sourceUrl"], "verifiedAt": "2026-08-04",
            "verificationMethod": "official_city_page", "unverified": False,
        }
        camps.append(camp)
        print("  ADD", camp["name"], "|", camp["city"], camp["state"], f"({coords[0]:.3f},{coords[1]:.3f})")

    out = {"source": "CampFind v4 city-run camps (official city recreation pages)",
           "count": len(camps), "camps": camps}
    fn = os.path.join(ROOT, "app", "aca_camps_city_v4.json")
    json.dump(out, open(fn, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"\nwrote {len(camps)} city camps -> {fn}")

if __name__ == "__main__":
    main()
