#!/usr/bin/env python3
"""
CampFind v24 — Houston, TX Parks & Recreation youth camps & programs.

Source: official HPARD page (houstontx.gov/parks/youthsports-recreation.html).
Every program is a real Houston Parks and Recreation Department offering; R2 =
the official page + ActiveNet registration link.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SOURCE_URL = "https://www.houstontx.gov/parks/youthsports-recreation.html"
PHONE = "(832) 394-8805"
REG = "https://anc.apm.activecommunities.com/houstonparks/activity/search"
COORDS = (29.7604, -95.3698)  # Houston, TX city center

# (name, ageMin, ageMax, price(number|null), theme, season, sourceUrl, description)
CAMPS = [
    ("Houston Summer Enrichment Program (SEP)", 6, 13, 30,
     "General", "summer", SOURCE_URL,
     "9-week day camp at 33 community centers citywide ($30 per child, per week; "
     "fee exemptions available), with arts and crafts, nutrition education, fitness, "
     "nature exploration, recycling awareness and bird watching."),
    ("Houston After-School Enrichment Program (AEP)", 6, 13, None,
     "General", "fall", SOURCE_URL,
     "Free of charge; recreational and cultural enrichment program at select HPARD "
     "community centers, including arts and crafts, nutrition education, fitness, "
     "nature exploration and sports."),
    ("Opening Doors Teen Mentor Program", 14, 17, 30,
     "General", "summer", SOURCE_URL,
     "8-week summer program ($30 per week; exemptions available; includes Jr. "
     "Lifeguard program) giving teens community service projects, mentoring, resume "
     "building, certifications and college prep."),
    ("Houston Soccer for Success", 5, 14, None,
     "Sports", "fall", SOURCE_URL,
     "Free after-school soccer program in partnership with the U.S. Soccer Foundation, "
     "with trained mentors and family engagement, meeting 3x/week for 60-90 minute sessions."),
    ("H-Town Soccer Academy", 6, 18, 250,
     "Sports", "fall", SOURCE_URL,
     "Competitive youth soccer club program ($250-$315 per season depending on age "
     "group; uniforms not included) providing an affordable, inclusive path from "
     "recreational play to elite development."),
    ("Houston Youth Basketball Program", 9, 14, None,
     "Sports", "summer", SOURCE_URL,
     "Free recreational league teaching throwing, catching, dribbling, shooting, "
     "defense, agility and fitness; meets 2x/week with an end-of-season tournament."),
    ("Astros Jr. RBI League", 4, 18, None,
     "Sports", "spring", SOURCE_URL,
     "Free Jr. RBI baseball, softball and T-ball league in partnership with the "
     "Houston Astros."),
    ("Instructional Jr. RBI - Fun At Bat", 6, 13, None,
     "Sports", "spring", SOURCE_URL,
     "Free instructional baseball skills program held at 36 community centers for "
     "registered After-School Enrichment Program participants."),
    ("Houston Youth Flag Football", 9, 14, None,
     "Sports", "fall", SOURCE_URL,
     "Free recreational league teaching throwing, catching, defense, flag pulling, "
     "agility and fitness; meets 2x/week with an end-of-season tournament."),
    ("First Tee of Greater Houston", 7, 18, None,
     "Sports", "summer", "https://firstteegreaterhouston.org/",
     "Youth golf program (program fees set by First Tee of Greater Houston) teaching "
     "character development, healthy habits and life skills through the game of golf."),
    ("Houston Youth Tennis Program", 5, 17, None,
     "Sports", "summer", "https://www.houstontx.gov/parks/youthtennis.html",
     "Youth tennis instruction and play at HPARD tennis facilities (see ActiveNet "
     "registration for fees and locations)."),
    ("Houston Youth Skateboarding Program", 6, 17, None,
     "Sports", "summer", "https://www.houstontx.gov/parks/skateparks.html",
     "Youth skateboarding instruction and open skate at HPARD skateparks (see "
     "ActiveNet registration for fees and locations)."),
]


def main():
    camps = []
    for name, lo, hi, price, theme, season, src, desc in CAMPS:
        camps.append({
            "id": "houston_" + name.lower().replace(" ", "_").replace("(", "").replace(")", "").replace("/", "_")[:40],
            "name": name,
            "city": "Houston",
            "state": "TX",
            "zip": "77002",
            "address": "Houston Parks & Recreation Department, 2999 S. Wayside Dr, Houston, TX 77023",
            "lat": COORDS[0],
            "lng": COORDS[1],
            "type": "day",
            "price": price,
            "rating": None,
            "reviewCount": None,
            "ageMin": lo,
            "ageMax": hi,
            "season": season,
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
    out = {"source": "CampFind v24 Houston TX Parks & Recreation youth camps (official page)",
           "count": len(camps), "camps": camps}
    fn = os.path.join(ROOT, "app", "aca_camps_brands_v24.json")
    json.dump(out, open(fn, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"wrote {len(camps)} Houston camps -> {fn}")


if __name__ == "__main__":
    main()
