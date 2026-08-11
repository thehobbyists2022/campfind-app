#!/usr/bin/env python3
"""
CampFind v30 — Fort Worth, TX Park & Recreation youth camps.

Source: official fortworthtexas.gov Park & Recreation pages (Camp Fort Worth,
Rec Leader in Training, Mobile Rec, Rising Stars). Every camp is a real Fort
Worth P&R program; R2 = the official page.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SOURCE_URL = "https://www.fortworthtexas.gov/departments/parks/services/camp"
REG = "https://anc.apm.activecommunities.com/cityoffortworth/activity/search"
PHONE = "(817) 392-5700"
COORDS = (32.7555, -97.3308)  # Fort Worth, TX city center

# (name, ageMin, ageMax, price, theme, sourceUrl, description)
CAMPS = [
    ("Camp Fort Worth", 5, 12, 65, "General",
     "https://www.fortworthtexas.gov/departments/parks/services/camp",
     "Summer day camp (June 8 - July 31, Mon-Fri 7:30am-6pm) full of challenging and "
     "creative activities for children ages 5-12, including 45 minutes of daily "
     "literacy instruction and field trips. $65 per week."),
    ("Fort Worth Rec Leader in Training (RLIT)", 13, 17, None, "General",
     "https://www.fortworthtexas.gov/departments/parks/services/rec-leader-in-training",
     "Teen leadership program for ages 13-17 providing job readiness and mentorship "
     "experience supporting Camp Fort Worth counselors."),
    ("Fort Worth Mobile Rec Summer Camp", 5, 12, 0, "General",
     "https://www.fortworthtexas.gov/departments/parks/services/Mobile-Rec-Summer-Camp",
     "Free mobile recreation summer camp bringing supervised games, activities and "
     "fun to parks across Fort Worth."),
    ("Fort Worth Rising Stars Program", 13, 17, None, "General",
     "https://www.fortworthtexas.gov/departments/parks/services/rising-stars",
     "Teen enrichment program offering skill-building, recreation and leadership "
     "opportunities."),
]


def main():
    camps = []
    for name, lo, hi, price, theme, src, desc in CAMPS:
        slug = name.lower().replace(" ", "_").replace("(", "").replace(")", "").replace(",", "")
        camps.append({
            "id": ("fortworth_" + slug)[:60],
            "name": name,
            "city": "Fort Worth",
            "state": "TX",
            "zip": "76102",
            "address": "Fort Worth Park & Recreation Department, 4200 International Plaza, Fort Worth, TX 76109",
            "lat": COORDS[0],
            "lng": COORDS[1],
            "type": "day",
            "price": price,
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
            "website": REG,
            "description": desc,
            "acaVerified": False,
            "provider": "city",
            "source": "city_recreation:official",
            "sourceUrl": src,
            "verifiedAt": "2026-08-09",
            "verificationMethod": "official_city_page",
            "unverified": False,
        })
    out = {"source": "CampFind v30 Fort Worth TX Park & Recreation youth camps (official pages)",
           "count": len(camps), "camps": camps}
    fn = os.path.join(ROOT, "app", "aca_camps_brands_v30.json")
    json.dump(out, open(fn, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"wrote {len(camps)} Fort Worth camps -> {fn}")


if __name__ == "__main__":
    main()
