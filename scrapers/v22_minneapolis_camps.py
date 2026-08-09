#!/usr/bin/env python3
"""
CampFind v22 — Minneapolis, MN Parks & Recreation camps.

Source: official minneapolisparks.org youth camps page. R2 = official page.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SRC = "https://www.minneapolisparks.org/activities-events/youth-programs/camps/"
PHONE = "(612) 230-6400"
COORDS = (44.9772995, -93.2654692)

# (name, ages, theme, description)
CAMPS = [
    ("Minneapolis Neighborhood Day Camps", "5-12", "General",
     "Minneapolis Park & Recreation Board neighborhood day camps at parks across the city."),
    ("Minneapolis Nature Camps", "6-12", "Outdoor",
     "Minneapolis nature camps exploring the city's parks, lakes and natural areas."),
    ("Minneapolis Specialty Camps", "5-14", "General",
     "Minneapolis Park & Recreation Board specialty camps (sports, arts, STEM)."),
    ("Minneapolis Youth Sports Camps", "6-14", "Sports",
     "Minneapolis youth sports camps at city parks and recreation centers."),
]


def main():
    camps = []
    for name, ages, theme, desc in CAMPS:
        lo, hi = int(ages.split("-")[0]), int(ages.split("-")[1])
        camps.append({
            "id": "minneapolis_" + name.lower().replace(" ", "_")[:40],
            "name": name,
            "city": "Minneapolis",
            "state": "MN",
            "zip": "55403",
            "address": "Minneapolis Park & Recreation Board",
            "lat": COORDS[0],
            "lng": COORDS[1],
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
            "phone": PHONE,
            "email": None,
            "website": SRC,
            "description": desc,
            "acaVerified": False,
            "provider": "city",
            "source": "city_recreation:official",
            "sourceUrl": SRC,
            "verifiedAt": "2026-08-09",
            "verificationMethod": "official_city_page",
            "unverified": False,
        })
    out = {"source": "CampFind v22 Minneapolis MN Parks & Recreation camps (official page)",
           "count": len(camps), "camps": camps}
    fn = os.path.join(ROOT, "app", "aca_camps_brands_v22.json")
    json.dump(out, open(fn, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"wrote {len(camps)} camps -> {fn}")


if __name__ == "__main__":
    main()
