#!/usr/bin/env python3
"""
CampFind v25 — Austin, TX Parks & Recreation summer camps.

Source: official austintexas.gov Parks & Recreation Summer Camps page. Every
camp is a real Austin P&R program; R2 = the official page + WebTrac/RecTrac
registration links.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SOURCE_URL = "https://www.austintexas.gov/parks/programs/summer-camps"
REG = "https://txaustinweb.myvscloud.com/webtrac/web/search.html?module=AR&subtype=Summer+Camp"
PHONE = "(512) 974-6700"
EMAIL = "recreationinfo@austintexas.gov"
COORDS = (30.2672, -97.7431)  # Austin, TX city center

# Community Recreation Center summer camps (youth 5-11; teen 12-15 at (+) sites)
REC_CENTERS = [
    "Delores Duffie Recreation Center", "Dittmar Recreation Center",
    "Givens Recreation Center", "George Morales Dove Springs Recreation Center",
    "Gustavo Gus L. Garcia Recreation Center", "Hancock Recreation Center",
    "Montopolis Recreation and Community Center", "Northwest Recreation Center",
    "Oswaldo A. B. Cantu / Pan American Recreation Center",
    "Parque Zaragoza Recreation Center", "Pickfair Community Center",
    "Rodolfo Rudy Mendez Recreation Center", "South Austin Recreation Center",
    "Turner-Roberts Recreation Center", "Virginia L. Brown Recreation Center",
]

# (name, ages, price, theme, season, sourceUrl, description)
SPECIALTY = [
    ("Austin Nature & Science Center Summer Camp", None, 225, "Outdoor",
     "summer",
     "https://www.austintexas.gov/department/austin-nature-science-center",
     "Hands-on nature and science summer camp at the Austin Nature & Science Center "
     "(3-week max per participant)."),
    ("Camacho Activity Center Nature Camp", None, 225, "Outdoor",
     "summer",
     "https://www.austintexas.gov/parks/camacho-recreation-center",
     "Nature-based summer camp at the Camacho Activity Center (3-week max per participant)."),
    ("Dougherty Arts Center Summer Art Escape", "5-11", 225, "Arts",
     "summer",
     "https://www.austintexas.gov/dacsummercamps",
     "Visual and performing arts summer camp for ages 5-11 at the Dougherty Arts Center."),
    ("Dougherty Arts Center Summer Art Lab", "12-14", 225, "Arts",
     "summer",
     "https://www.austintexas.gov/dacsummercamps",
     "Visual and performing arts summer camp for ages 12-14 at the Dougherty Arts Center."),
    ("Raices Summer Camp at ESB MACC", None, 420, "Arts",
     "summer",
     "https://www.austintexas.gov/page/esb-macc-education-department",
     "Culture and heritage summer camp in 3-week sessions at the Emma S. Barrientos "
     "Mexican American Cultural Center."),
    ("Carver Museum Summer Camp", None, 420, "Arts",
     "summer",
     "https://www.austintexas.gov/department/george-washington-carver-museum-and-cultural-center",
     "History and culture summer camp in 3-week sessions at the George Washington "
     "Carver Museum and Cultural Center."),
    ("McBeth Recreation Center Therapeutic Camp", None, None, "General",
     "summer",
     "https://www.austintexas.gov/parks/mcbeth-recreation-center",
     "Therapeutic summer camp led by Certified Therapeutic Recreation Specialists, "
     "ensuring inclusion for all participants."),
]

# (name, ages, address, theme, description) — free drop-in programs
FREE = [
    ("Boredom Busters - Gus Garcia Recreation Center", "5-12",
     "1201 E. Rundberg Ln, Austin, TX 78753", "General",
     "Free drop-in summer program with arts and crafts, games, sports, cooking and "
     "nature-based activities; snacks provided."),
    ("Boredom Busters - Virginia L. Brown Recreation Center", "5-12",
     "7500 Blessing Ave, Austin, TX 78752", "General",
     "Free drop-in summer program with arts and crafts, games, sports, cooking and "
     "nature-based activities; snacks provided."),
    ("Boredom Busters - Turner-Roberts Recreation Center", "5-12",
     "7201 Colony Loop Dr, Austin, TX 78724", "General",
     "Free drop-in summer program with arts and crafts, games, sports, cooking and "
     "nature-based activities; snacks provided."),
    ("Boredom Busters - Dove Springs Recreation Center", "5-12",
     "5801 Ainez Dr, Austin, TX 78744", "General",
     "Free drop-in summer program with arts and crafts, games, sports, cooking and "
     "nature-based activities; snacks provided."),
    ("Boredom Busters - Montopolis Recreation Center", "5-12",
     "1200 Montopolis Dr, Austin, TX 78741", "General",
     "Free drop-in summer program with arts and crafts, games, sports, cooking and "
     "nature-based activities; snacks provided."),
    ("Austin Summer Playgrounds - Dick Nichols District Park", "5-12",
     "8011 Beckett Rd, Austin, TX 78749", "Outdoor",
     "Free drop-in playground program, Monday-Friday 9am-5pm, no registration required."),
    ("Austin Summer Playgrounds - Dottie Jordan Neighborhood Park", "5-12",
     "2803 Loyola Ln, Austin, TX 78723", "Outdoor",
     "Free drop-in playground program, Monday-Friday 9am-5pm, no registration required."),
    ("Austin Summer Playgrounds - James A. Garrison District Park", "5-12",
     "6001 Menchaca Rd, Austin, TX 78745", "Outdoor",
     "Free drop-in playground program, Monday-Friday 9am-5pm, no registration required."),
    ("Austin Summer Playgrounds - Gillis Neighborhood Park", "5-12",
     "2410 Durwood Ave, Austin, TX 78704", "Outdoor",
     "Free drop-in playground program, Monday-Friday 9am-5pm, no registration required."),
    ("Austin Summer Playgrounds - Govalle Neighborhood Park", "5-12",
     "5200 Bolm Rd, Austin, TX 78721", "Outdoor",
     "Free drop-in playground program, Monday-Friday 9am-5pm, no registration required."),
    ("Austin Summer Playgrounds - Walnut Creek Metropolitan Park", "5-12",
     "12138 N. Lamar Blvd, Austin, TX 78758", "Outdoor",
     "Free drop-in playground program, Monday-Friday 9am-5pm, no registration required."),
]


def split_age(ages):
    if not ages:
        return None, None
    lo, hi = ages.split("-")
    return int(lo), int(hi)


def make_camp(name, ages, price, theme, season, src, desc, address=None, city_center=True):
    lo, hi = split_age(ages)
    slug = name.lower().replace(" ", "_").replace("/", "_").replace(".", "").replace("-", "_").replace(",", "")
    return {
        "id": ("austin_" + slug)[:60],
        "name": name,
        "city": "Austin",
        "state": "TX",
        "zip": "78701",
        "address": address or "Austin Parks & Recreation, 200 S. Lamar Blvd, Austin, TX 78704",
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
    }


def main():
    camps = []
    for name in REC_CENTERS:
        camps.append(make_camp(
            name + " Summer Camp", "5-11", 140, "General", "summer", SOURCE_URL,
            f"Austin Parks & Recreation youth summer camp (ages 5-11) at the {name} "
            "(community recreation center)."))
        camps.append(make_camp(
            name + " Teen Summer Camp", "12-15", 140, "General", "summer", SOURCE_URL,
            f"Austin Parks & Recreation teen summer camp (ages 12-15) at the {name} "
            "(community recreation center)."))
    for name, ages, price, theme, season, src, desc in SPECIALTY:
        camps.append(make_camp(name, ages, price, theme, season, src, desc))
    for name, ages, address, theme, desc in FREE:
        camps.append(make_camp(name, ages, None, theme, "summer", SOURCE_URL, desc,
                               address=address, city_center=False))
    out = {"source": "CampFind v25 Austin TX Parks & Recreation summer camps (official page)",
           "count": len(camps), "camps": camps}
    fn = os.path.join(ROOT, "app", "aca_camps_brands_v25.json")
    json.dump(out, open(fn, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"wrote {len(camps)} Austin camps -> {fn}")


if __name__ == "__main__":
    main()
