#!/usr/bin/env python3
"""
CampFind v23 — Baltimore, MD Recreation & Parks summer camps.

Source: official baltimorecity.gov/bcrp/summer-camp page. Real BCRP summer
camps; R2 = official city page.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SRC = "https://www.baltimorecity.gov/bcrp/summer-camp"
PHONE = "(410) 396-7900"
COORDS = (39.2904, -76.6122)

# (name, ages, theme, description)
CAMPS = [
    ("B'More Summer Fun Camp", "6-12", "General",
     "Games, nature exploration, STEM, sports, crafts, 7 swim days and a theme park trip."),
    ("Camp Baltimore", "6-12", "General",
     "Affordable summer fun with sports, swimming, nature outings and field trips."),
    ("Baltimore Travel Summer Camp", "8-14", "General",
     "Weekly trips, 7 swim days, theme park visit and educational/adventure trips."),
    ("Camp Belonging Summer Camp", "6-17", "General",
     "Inclusive camp for youth with disabilities featuring adaptive activities."),
    ("Carrie Murray Nature Center Camp", "6-12", "Outdoor",
     "Outdoor exploration, wildlife encounters, hiking, art and nature activities."),
    ("Baltimore Beauty Camp", "10-16", "Arts",
     "Two-week beauty camp building confidence through hair styling, nail design and skincare."),
    ("Baltimore Aviation Camp", "10-16", "STEM",
     "Two-week camp on flight, aircraft, drones, space and airport operations."),
    ("Baltimore STEM Camp - Circuit Threads", "8-14", "STEM",
     "E-textile explorations camp."),
    ("Baltimore Python Coding Camp", "10-16", "STEM",
     "One-week coding camp teaching Python and game development with Pygame."),
    ("Baltimore Robotics Camp - SPIKE Essential", "8-14", "STEM",
     "Robotics education with LEGO SPIKE Essential kits."),
    ("Girls Summer Basketball Camp", "8-17", "Sports",
     "Four-week camp on shooting, dribbling, defense, teamwork and fundamentals."),
    ("Boys Summer Basketball Camp", "8-17", "Sports",
     "Four-week camp on shooting, dribbling, defense, teamwork and fundamentals."),
    ("Baltimore Volleyball Camp", "12-17", "Sports",
     "Four-day high-intensity volleyball camp for competitive athletes."),
    ("Baltimore Golf Camp", "8-15", "Sports",
     "Half-day golf camp teaching putting, chipping and driving."),
    ("Baltimore All-Star Tennis Camp", "6-17", "Sports",
     "Eight-week program teaching tennis fundamentals for all skill levels."),
    ("Baltimore Swim & Fitness Camp", "8-14", "Sports",
     "Learn to swim, build endurance and stay active in a safe aquatic environment."),
]


def main():
    camps = []
    for name, ages, theme, desc in CAMPS:
        lo, hi = int(ages.split("-")[0]), int(ages.split("-")[1])
        camps.append({
            "id": "baltimore_" + name.lower().replace(" ", "_").replace("'", "").replace("&", "and")[:35],
            "name": name,
            "city": "Baltimore",
            "state": "MD",
            "zip": "21202",
            "address": "Baltimore City Recreation & Parks, 100 N. Holliday St, Baltimore, MD 21202",
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
            "description": f"Baltimore City Recreation & Parks summer camp: {desc}",
            "acaVerified": False,
            "provider": "city",
            "source": "city_recreation:official",
            "sourceUrl": SRC,
            "verifiedAt": "2026-08-09",
            "verificationMethod": "official_city_page",
            "unverified": False,
        })
    out = {"source": "CampFind v23 Baltimore MD Recreation & Parks summer camps (official page)",
           "count": len(camps), "camps": camps}
    fn = os.path.join(ROOT, "app", "aca_camps_brands_v23.json")
    json.dump(out, open(fn, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"wrote {len(camps)} camps -> {fn}")


if __name__ == "__main__":
    main()
