#!/usr/bin/env python3
"""
CampFind v17 — Poway + Solana Beach, CA Parks & Recreation summer camps.

Source: official city pages (poway.org, cityofsolanabeach.ca.gov). Real P&R
summer camps; R2 = official city page.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# (city, state, zip, coords, phone, name, ages, theme, sourceUrl, description, website)
CAMPS = [
    ("Poway", "CA", "92064", (32.9628234, -117.035864), "(858) 668-4770",
     "Lake Poway Day Camp", "5-12", "Outdoor",
     "https://poway.org/217/Lake-Poway-Day-Camp",
     "Poway Lake Poway Day Camp with weekly field trips (San Diego Zoo, Belmont Park, water parks).",
     "https://poway.org/217/Lake-Poway-Day-Camp"),
    ("Poway", "CA", "92064", (32.9628234, -117.035864), "(858) 668-4770",
     "Lake Poway Day Camp - Teen Counselor in Training", "13-17", "Outdoor",
     "https://poway.org/217/Lake-Poway-Day-Camp",
     "Lake Poway Day Camp Counselor-in-Training program for teens, 9 one-week sessions.",
     "https://poway.org/217/Lake-Poway-Day-Camp"),
    ("Solana Beach", "CA", "92075", (32.9913, -117.2712), "(858) 720-2430",
     "Solana Beach Kids Summer Day Camp", "5-11", "General",
     "https://cityofsolanabeach.ca.gov/en/parks-recreation/summer-day-camps",
     "Solana Beach Kids Summer Day Camps with after-care option.",
     "https://cityofsolanabeach.ca.gov/en/parks-recreation/summer-day-camps"),
    ("Solana Beach", "CA", "92075", (32.9913, -117.2712), "(858) 720-2430",
     "Solana Beach Summer Day Camp - Leader in Training", "12-16", "General",
     "https://cityofsolanabeach.ca.gov/en/parks-recreation/summer-day-camps",
     "Solana Beach Leader in Training program for teens 12-16.",
     "https://cityofsolanabeach.ca.gov/en/parks-recreation/summer-day-camps"),
]


def main():
    camps = []
    for city, st, zipc, coords, phone, name, ages, theme, src, desc, web in CAMPS:
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
            "website": web,
            "description": desc,
            "acaVerified": False,
            "provider": "city",
            "source": "city_recreation:official",
            "sourceUrl": src,
            "verifiedAt": "2026-08-08",
            "verificationMethod": "official_city_page",
            "unverified": False,
        })
    out = {"source": "CampFind v17 Poway + Solana Beach CA Parks & Rec summer camps (official pages)",
           "count": len(camps), "camps": camps}
    fn = os.path.join(ROOT, "app", "aca_camps_brands_v17.json")
    json.dump(out, open(fn, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"wrote {len(camps)} camps -> {fn}")


if __name__ == "__main__":
    main()
