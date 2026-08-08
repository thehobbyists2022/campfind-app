#!/usr/bin/env python3
"""
CampFind v13 — fill under-represented states with real ACA-listed camps.

Adds 6 real overnight camps (verified in the ACA find-a-camp database, R2) to
states with <10 entries: AK, ME, VT, HI. sourceUrl = ACA camp profile;
website = camp's official site; acaVerified reflects ACA accreditation status
(Camp Kushtaka is listed but not currently accredited -> false).
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CAMPS = [
    {
        "name": "Camp Kushtaka", "city": "Cooper Landing", "state": "AK",
        "zip": "99572", "address": "Snug Harbor Rd, Cooper Landing, AK 99572",
        "lat": 60.4899, "lng": -149.8227,
        "website": "https://www.salvationarmy.org",
        "acaCampId": 4325, "acaVerified": False,
        "description": "Salvation Army camp at Trestle Glen, Cooper Landing, Alaska.",
    },
    {
        "name": "Camp Caribou for Boys", "city": "Winslow", "state": "ME",
        "zip": "04901", "address": "1 Caribou Way, Winslow, ME 04901",
        "lat": 44.5384, "lng": -69.6201,
        "website": "https://www.campcaribou.com",
        "acaCampId": 2435, "acaVerified": True,
        "description": "Traditional boys summer camp in Winslow, Maine.",
    },
    {
        "name": "Camp Androscoggin", "city": "Wayne", "state": "ME",
        "zip": "04284", "address": "126 Leadbetter Rd, Wayne, ME 04284",
        "lat": 44.3488, "lng": -70.0508,
        "website": "https://www.campandro.com",
        "acaCampId": 912, "acaVerified": True,
        "description": "Boys summer camp on Lake Androscoggin, Wayne, Maine.",
    },
    {
        "name": "YMCA Camp Abnaki", "city": "North Hero", "state": "VT",
        "zip": "05474", "address": "1252 Abnaki Rd, North Hero, VT 05474",
        "lat": 44.8277, "lng": -73.3075,
        "website": "https://www.campabnaki.org",
        "acaCampId": 401, "acaVerified": True,
        "description": "YMCA boys & girls summer camp on Lake Champlain, Vermont.",
    },
    {
        "name": "Camp Downer", "city": "Sharon", "state": "VT",
        "zip": "05065", "address": "1535 Downer Rd, Sharon, VT 05065",
        "lat": 43.8123, "lng": -72.4363,
        "website": "https://www.campdowner.com",
        "acaCampId": 2438, "acaVerified": True,
        "description": "Girls overnight summer camp in the Green Mountains, Vermont.",
    },
    {
        "name": "Camp Mokuleia", "city": "Waialua", "state": "HI",
        "zip": "96791", "address": "68-729 Farrington Hwy, Waialua, HI 96791",
        "lat": 21.5786, "lng": -158.1708,
        "website": "https://www.campmokuleia.com",
        "acaCampId": 2771, "acaVerified": True,
        "description": "YMCA beachside camp on Oahu's North Shore, Hawaii.",
    },
]


def main():
    camps = []
    for c in CAMPS:
        camps.append({
            "id": f"real_{c['name'].lower().replace(' ', '_')}",
            "name": c["name"],
            "city": c["city"],
            "state": c["state"],
            "zip": c["zip"],
            "address": c["address"],
            "lat": c["lat"],
            "lng": c["lng"],
            "type": "overnight",
            "price": None,
            "rating": None,
            "reviewCount": None,
            "ageMin": None,
            "ageMax": None,
            "season": "summer",
            "theme": "Outdoor",
            "beforeCare": None,
            "afterCare": None,
            "shuttle": None,
            "weeks": None,
            "phone": None,
            "email": None,
            "website": c["website"],
            "description": c["description"],
            "acaVerified": c["acaVerified"],
            "source": "aca_finder",
            "sourceUrl": f"https://find.acacamps.org/camp_profile.php?camp_id={c['acaCampId']}",
            "verifiedAt": "2026-08-06",
            "verificationMethod": "aca_finder",
            "unverified": False,
        })
    out = {"source": "CampFind v13 under-represented-state real camps (ACA-verified)",
           "count": len(camps), "camps": camps}
    fn = os.path.join(ROOT, "app", "aca_camps_brands_v13.json")
    json.dump(out, open(fn, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"wrote {len(camps)} camps -> {fn}")
    for c in camps:
        print("  ", c["name"], c["city"], c["state"], "acaVerified=", c["acaVerified"])


if __name__ == "__main__":
    main()
