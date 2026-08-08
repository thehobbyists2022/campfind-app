#!/usr/bin/env python3
"""
CampFind v16 — San Marcos, CA Parks & Recreation camps.

Source: official City of San Marcos (sanmarcosca.gov) Parks & Recreation
Kids Activities pages. Every camp is a real San Marcos P&R program; R2 = the
official city page.

San Marcos previously had only 3 brand-franchise entries and no city camps.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SM_COORDS = (33.1434, -117.1661)  # San Marcos, CA city center
PHONE = "(760) 744-9000"
EMAIL = "parks@san-marcos.net"

# (name, ages, theme, sourceUrl, description)
CAMPS = [
    ("San Marcos Adventure Day Camp",
     "5-11", "General",
     "https://www.sanmarcosca.gov/Parks-Recreation/Kids-Activities/Adventure-Day-Camp",
     "San Marcos Parks & Recreation Adventure Day Camp for campers in grades K-6, Mon-Fri 7:30am-5:30pm."),
    ("San Marcos Woodland Park Swim Camp",
     "6-12", "Sports",
     "https://www.sanmarcosca.gov/Parks-Recreation/Kids-Activities/Adventure-Day-Camp",
     "San Marcos Woodland Park swim camp for youth."),
    ("San Marcos Summer Specialty Camps",
     "5-14", "General",
     "https://www.sanmarcosca.gov/Parks-Recreation/Kids-Activities/Camps-Classes",
     "San Marcos Parks & Recreation summer specialty camps & classes (see recreation guide)."),
    ("San Marcos Youth Sports Camps",
     "5-14", "Sports",
     "https://www.sanmarcosca.gov/Parks-Recreation/Kids-Activities/Youth-Sports",
     "San Marcos youth sports leagues and camps."),
]


def main():
    camps = []
    for name, ages, theme, src, desc in CAMPS:
        lo = int(ages.split("-")[0])
        hi = int(ages.split("-")[1])
        camps.append({
            "id": "sanmarcos_" + name.lower().replace(" ", "_").replace("&", "and")[:40],
            "name": name,
            "city": "San Marcos",
            "state": "CA",
            "zip": "92069",
            "address": "San Marcos Parks & Recreation, 1 Civic Center Dr, San Marcos, CA 92069",
            "lat": SM_COORDS[0],
            "lng": SM_COORDS[1],
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
            "email": EMAIL,
            "website": "https://www.sanmarcosca.gov/Parks-Recreation/Kids-Activities/Adventure-Day-Camp",
            "description": desc,
            "acaVerified": False,
            "provider": "city",
            "source": "city_recreation:official",
            "sourceUrl": src,
            "verifiedAt": "2026-08-08",
            "verificationMethod": "official_city_page",
            "unverified": False,
        })
    out = {"source": "CampFind v16 San Marcos CA Parks & Recreation camps (official city pages)",
           "count": len(camps), "camps": camps}
    fn = os.path.join(ROOT, "app", "aca_camps_brands_v16.json")
    json.dump(out, open(fn, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"wrote {len(camps)} San Marcos camps -> {fn}")


if __name__ == "__main__":
    main()
