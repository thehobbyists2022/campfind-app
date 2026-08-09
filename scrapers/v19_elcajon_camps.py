#!/usr/bin/env python3
"""
CampFind v19 — El Cajon, CA Parks & Recreation summer camps.

Source: official elcajon.gov Parks & Recreation Camps page. Real P&R summer
day camps; R2 = official city page.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SRC = "https://www.elcajon.gov/your-government/departments/recreation/classes-and-activities/camps"
PHONE = "(619) 441-1716"
COORDS = (32.7948, -116.9625)

# (name, ages, theme)
CAMPS = [
    ("Spring Into Fun Camp", "6-13", "General"),
    ("Fun in the Sun Camp", "6-13", "General"),
    ("El Cajon Basketball Camp", "6-13", "Sports"),
    ("El Cajon Volleyball Camp", "8-14", "Sports"),
    ("El Cajon Aquatics Camp", "7-12", "Sports"),
    ("El Cajon Skate & Scooter Camp", "7-15", "Sports"),
    ("El Cajon Dance Camp", "7-15", "Arts"),
    ("El Cajon Mini Dance Camp", "4-6", "Arts"),
    ("El Cajon Gymnastics Camp", "7-15", "Sports"),
    ("El Cajon Art Camp", "6-13", "Arts"),
]


def main():
    camps = []
    for name, ages, theme in CAMPS:
        lo, hi = int(ages.split("-")[0]), int(ages.split("-")[1])
        camps.append({
            "id": "elcajon_" + name.lower().replace(" ", "_").replace("&", "and")[:35],
            "name": name,
            "city": "El Cajon",
            "state": "CA",
            "zip": "92020",
            "address": "El Cajon Parks & Recreation, 200 Civic Center Way, El Cajon, CA 92020",
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
            "description": f"El Cajon Parks & Recreation day camp (ages {ages}): {name}.",
            "acaVerified": False,
            "provider": "city",
            "source": "city_recreation:official",
            "sourceUrl": SRC,
            "verifiedAt": "2026-08-09",
            "verificationMethod": "official_city_page",
            "unverified": False,
        })
    out = {"source": "CampFind v19 El Cajon CA Parks & Recreation summer camps (official page)",
           "count": len(camps), "camps": camps}
    fn = os.path.join(ROOT, "app", "aca_camps_brands_v19.json")
    json.dump(out, open(fn, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"wrote {len(camps)} camps -> {fn}")


if __name__ == "__main__":
    main()
