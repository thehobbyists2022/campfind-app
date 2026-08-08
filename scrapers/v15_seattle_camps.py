#!/usr/bin/env python3
"""
CampFind v15 — Seattle Parks & Recreation summer camps.

Source: official seattle.gov Parks & Recreation camp pages (2026 season).
Every camp is a real Seattle P&R program; R2 = the official page + ActiveCommunities
registration link.

Adds Seattle TX-style city camps for Seattle, WA so searches return real local
summer camps instead of only synthetic brand templates.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SEATTLE_PHONE = "(206) 684-4075"
EMAIL = "ParksBSC@seattle.gov"
REG = "https://anc.apm.activecommunities.com/seattle/activity/search"

# (name, park/address, lat, lng, age, price, theme, sourceUrl, note)
CAMPS = [
    ("Carkeek Park EarthKeepers Camp", "Carkeek Park, 950 NW Carkeek Park Rd, Seattle, WA 98177",
     47.7119, -122.3744, "6-12", "$400/week",
     "Outdoor",
     "https://www.seattle.gov/parks/parks/discovery-park/discovery-park-camps",
     "Weekly nature camp at Carkeek Park, new themes each week."),
    ("Discovery Park Nature Adventure Trek", "Discovery Park, 3801 Discovery Park Blvd, Seattle, WA 98199",
     47.6614, -122.4063, "6-12", "$420/week",
     "Outdoor",
     "https://www.seattle.gov/parks/parks/discovery-park/discovery-park-camps",
     "Nature adventure trek at Discovery Park, weekly June-Aug."),
    ("Seattle Parks Activity Camp", "Seattle Parks & Recreation, 100 Dexter Ave N, Seattle, WA 98109",
     47.6303, -122.3437, "3-18", None,
     "General",
     "https://www.seattle.gov/parks/childcare/camps",
     "Citywide Activity Camps, ages 3-18."),
    ("Seattle School-Age Care Summer Day Camp", "Seattle Parks & Recreation, 100 Dexter Ave N, Seattle, WA 98109",
     47.6303, -122.3437, "5-12", None,
     "General",
     "https://www.seattle.gov/parks/childcare/camps",
     "Licensed childcare summer day camps, ages 5-12."),
    ("Seattle Specialized Programs Day Camp", "Seattle Parks & Recreation, 100 Dexter Ave N, Seattle, WA 98109",
     47.6303, -122.3437, "4-21", None,
     "General",
     "https://www.seattle.gov/parks/childcare/camps",
     "Day camps for people with disabilities, ages 4-21."),
    ("Green Lake Small Craft Center Camp", "Green Lake Small Craft Center, 5900 W Green Lake Way N, Seattle, WA 98103",
     47.6812, -122.3285, "9-16", None,
     "Sports",
     "https://www.seattle.gov/parks/childcare/camps",
     "Rowing, sailing and paddling camps at Green Lake."),
    ("Mt. Baker Rowing & Sailing Center Camp", "Mt. Baker Rowing & Sailing Center, 3805 Lake Washington Blvd S, Seattle, WA 98118",
     47.5825, -122.2771, "9-16", None,
     "Sports",
     "https://www.seattle.gov/parks/childcare/camps",
     "Rowing and sailing camps on Lake Washington."),
    ("Camp Long Nature & Adventure Camp", "Camp Long, 5200 35th Ave SW, Seattle, WA 98126",
     47.5705, -122.3534, "7-14", None,
     "Outdoor",
     "https://www.seattle.gov/parks/parks/camp-long/camp-long-environmental-learning-center/camp-long-nature-and-adventure-camps",
     "Nature and adventure camps at Camp Long."),
    ("Magnuson Park Summer Camps", "Magnuson Park, 7400 Sand Point Way NE, Seattle, WA 98115",
     47.6814, -122.2550, "6-16", None,
     "Outdoor",
     "https://www.seattle.gov/parks/parks/magnuson-park/camps",
     "Partner-led summer camps at Magnuson Park (sailing, tennis, mountaineering)."),
]


def main():
    camps = []
    for name, addr, lat, lng, age, price, theme, src, note in CAMPS:
        camps.append({
            "id": "seattle_" + name.lower().replace(" ", "_").replace("&", "and")[:40],
            "name": name,
            "city": "Seattle",
            "state": "WA",
            "zip": "98109",
            "address": addr,
            "lat": lat,
            "lng": lng,
            "type": "day",
            "price": None,
            "rating": None,
            "reviewCount": None,
            "ageMin": None,
            "ageMax": None,
            "season": "summer",
            "theme": theme,
            "beforeCare": None,
            "afterCare": None,
            "shuttle": None,
            "weeks": None,
            "phone": SEATTLE_PHONE,
            "email": EMAIL,
            "website": "https://www.seattle.gov/parks/childcare/camps",
            "description": note,
            "acaVerified": False,
            "provider": "city",
            "source": "city_recreation:official",
            "sourceUrl": src,
            "verifiedAt": "2026-08-08",
            "verificationMethod": "official_city_page",
            "unverified": False,
        })
    out = {"source": "CampFind v15 Seattle Parks & Recreation summer camps (official seattle.gov pages)",
           "count": len(camps), "camps": camps}
    fn = os.path.join(ROOT, "app", "aca_camps_brands_v15.json")
    json.dump(out, open(fn, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"wrote {len(camps)} Seattle camps -> {fn}")


if __name__ == "__main__":
    main()
