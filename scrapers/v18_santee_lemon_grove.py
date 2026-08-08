#!/usr/bin/env python3
"""
CampFind v18 — Santee + Lemon Grove, CA Parks & Recreation summer camps.

Source: official city pages (cityofsanteeca.gov, lemongrove.ca.gov). Real P&R
summer camps; R2 = official city page.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (city, state, zip, coords, phone, name, ages, theme, sourceUrl, description)
CAMPS = [
    ("Santee", "CA", "92071", (32.8384, -116.9739), "(619) 258-4100",
     "Santee Summer Day Camp", "5-12", "General",
     "https://www.cityofsanteeca.gov/our-community/parks-recreation/summer-camps",
     "Santee Summer Day Camp for youth, weekly summer sessions."),
    ("Santee", "CA", "92071", (32.8384, -116.9739), "(619) 258-4100",
     "Santee Summer SanTeen Camp", "12-16", "General",
     "https://www.cityofsanteeca.gov/our-community/parks-recreation/summer-camps",
     "Santee Summer SanTeen Camp for teens."),
    ("Santee", "CA", "92071", (32.8384, -116.9739), "(619) 258-4100",
     "Santee Jr Camp Leader Program", "14-17", "General",
     "https://www.cityofsanteeca.gov/our-community/parks-recreation/summer-camps",
     "Santee Jr Camp Leader program — teens complete mandatory training week then assist camp staff."),
    ("Santee", "CA", "92071", (32.8384, -116.9739), "(619) 258-4100",
     "Santee Specialty Camps", "5-14", "General",
     "https://www.cityofsanteeca.gov/our-community/parks-recreation/summer-camps",
     "Santee summer specialty camps (sports, STEM, arts)."),
    ("Lemon Grove", "CA", "91945", (32.7426, -117.0314), "(619) 825-3800",
     "Lemon Grove Day Camp", "5-12", "General",
     "https://www.lemongrove.ca.gov/parks-events/day-camp/",
     "Lemon Grove summer day camp — play, learn and grow."),
]


def main():
    camps = []
    for city, st, zipc, coords, phone, name, ages, theme, src, desc in CAMPS:
        lo, hi = int(ages.split("-")[0]), int(ages.split("-")[1])
        camps.append({
            "id": f"{city.lower().replace(' ','_')}_{name.lower().replace(' ','_').replace('-','_')[:35]}",
            "name": name,
            "city": city,
            "state": st,
            "zip": zipc,
            "address": f"{city} Parks & Recreation",
            "lat": coords[0],
            "lng": coords[1],
            "type": "day",
            "price": None,
            "rating": None,
            "reviewCount": None,
            "ageMin": lo,
            "ageMax": hi,
            "season": "summer",
            "theme": theme,
            "beforeCare": None,
            "afterCare": None,
            "shuttle": None,
            "weeks": None,
            "phone": phone,
            "email": None,
            "website": src,
            "description": desc,
            "acaVerified": False,
            "provider": "city",
            "source": "city_recreation:official",
            "sourceUrl": src,
            "verifiedAt": "2026-08-08",
            "verificationMethod": "official_city_page",
            "unverified": False,
        })
    out = {"source": "CampFind v18 Santee + Lemon Grove CA Parks & Rec summer camps (official pages)",
           "count": len(camps), "camps": camps}
    fn = os.path.join(ROOT, "app", "aca_camps_brands_v18.json")
    json.dump(out, open(fn, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"wrote {len(camps)} camps -> {fn}")


if __name__ == "__main__":
    main()
