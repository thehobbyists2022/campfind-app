#!/usr/bin/env python3
"""
CampFind v26 — Phoenix, AZ Parks & Recreation summer camps.

Source: official phoenix.gov PHXPlays Camps + Camp Colley pages. Every camp is
a real Phoenix Parks & Recreation program; R2 = the official page + ActiveNet
registration links.
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SOURCE_URL = "https://www.phoenix.gov/administration/departments/parks/classes-programs/phxplays-camps.html"
COLLEY_URL = "https://www.phoenix.gov/administration/departments/parks/classes-programs/camp-colley-.html"
REG = "https://anc.apm.activecommunities.com/phoenix/activity/search"
PHONE = "(602) 262-6862"
COORDS = (33.4484, -112.0740)  # Phoenix, AZ city center

# (name, address, theme, description) — PHXPlays summer camps ages 6-12, $60-80/wk
SUMMER_CENTERS = [
    ("Beuf Community Center", "3435 W. Pinnacle Peak Rd, Phoenix, AZ 85027", "General",
     "Weekly summer camp with games, DIY crafts, field trips and themed activities."),
    ("Cesar Chavez Community Center", "7868 S. 35th Ave, Phoenix, AZ 85339", "General",
     "Weekly summer camp with games, DIY crafts, field trips and themed activities."),
    ("Deer Valley Community Center", "2001 W. Wahalla Ln, Phoenix, AZ 85027", "General",
     "Weekly summer camp with games, DIY crafts, field trips and themed activities."),
    ("Desert West Community Center", "6501 W. Virginia Ave, Phoenix, AZ 85035", "General",
     "Weekly summer camp with games, DIY crafts, field trips and themed activities."),
    ("Eastlake Park Community Center", "1549 E. Jefferson St, Phoenix, AZ 85034", "General",
     "Weekly summer camp with games, DIY crafts, field trips and themed activities."),
    ("Faye Gray Recreation Center", "5550 S. 20th St, Phoenix, AZ 85040", "General",
     "Weekly summer camp with games, DIY crafts, field trips and themed activities."),
    ("Longview Neighborhood Recreation Center", "4040 N. 14th St, Phoenix, AZ 85014", "General",
     "Weekly summer camp with games, DIY crafts, field trips and themed activities."),
    ("Marc Atkinson Recreation Center", "4535 N. 23rd Ave, Phoenix, AZ 85015", "General",
     "Weekly summer camp with games, DIY crafts, field trips and themed activities."),
    ("Maryvale Community Center", "4420 N. 51st Ave, Phoenix, AZ 85031", "General",
     "Weekly summer camp with games, DIY crafts, field trips and themed activities."),
    ("Muriel Smith Recreation Center", "2230 W. Roeser Rd, Phoenix, AZ 85041", "General",
     "Weekly summer camp with games, DIY crafts, field trips and themed activities."),
    ("Mountain View Community Center", "1104 E. Grovers Ave, Phoenix, AZ 85020", "General",
     "Weekly summer camp with games, DIY crafts, field trips and themed activities."),
    ("Paradise Valley Community Center", "17402 N. 40th St, Phoenix, AZ 85032", "General",
     "Weekly summer camp with games, DIY crafts, field trips and themed activities."),
    ("Pecos Community Center", "17010 S. 48th St, Phoenix, AZ 85048", "General",
     "Weekly summer camp with games, DIY crafts, field trips and themed activities."),
    ("Playa Margarita Park Community Center", "3615 W. Roeser Rd, Phoenix, AZ 85041", "General",
     "Weekly summer camp with games, DIY crafts, field trips and themed activities."),
    ("South Mountain Community Center", "212 E. Alta Vista Rd, Phoenix, AZ 85042", "General",
     "Weekly summer camp with games, DIY crafts, field trips and themed activities."),
    ("Sunnyslope Community Center", "802 E. Vogel Ave, Phoenix, AZ 85020", "General",
     "Weekly summer camp with games, DIY crafts, field trips and themed activities."),
    ("University Park Recreation Center", "1002 W. Van Buren St, Phoenix, AZ 85007", "General",
     "Weekly summer camp with games, DIY crafts, field trips and themed activities."),
    ("Washington Activity Center", "2240 W. Citrus Way, Phoenix, AZ 85015", "General",
     "Weekly summer camp with games, DIY crafts, field trips and themed activities."),
]

# Camp Colley (overnight, Happy Jack AZ) — operated by H.E.A.R.T. Center
COLLEY_COORDS = (34.7425, -111.4099)  # Happy Jack, AZ area


def make_camp(name, city, state, zipcode, address, lat, lng, ageMin, ageMax, price,
              theme, season, src, desc, camp_type="day"):
    slug = name.lower().replace(" ", "_").replace(".", "").replace("&", "and").replace(",", "")
    return {
        "id": ("phoenix_" + slug)[:60],
        "name": name,
        "city": city,
        "state": state,
        "zip": zipcode,
        "address": address,
        "lat": lat,
        "lng": lng,
        "type": camp_type,
        "price": price,
        "rating": None,
        "reviewCount": None,
        "ageMin": ageMin,
        "ageMax": ageMax,
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
    for name, addr, theme, desc in SUMMER_CENTERS:
        camps.append(make_camp(
            name + " Summer Camp", "Phoenix", "AZ", "85001", addr,
            COORDS[0], COORDS[1], 6, 12, 60, theme, "summer", SOURCE_URL,
            f"PHXPlays summer camp ({desc}) Runs Monday-Friday 7am-6pm, $60-$80/week "
            f"with daily drop-in available.", "day"))
    # Camp Colley — Adventure Camp (7-15) and Teen Leadership CIT (16-17)
    camps.append(make_camp(
        "Camp Colley Adventure Camp", "Happy Jack", "AZ", "86024",
        "Camp Colley, Mogollon Rim (Happy Jack, AZ 86024)",
        COLLEY_COORDS[0], COLLEY_COORDS[1], 7, 15, 250, "Outdoor", "summer",
        COLLEY_URL,
        "City of Phoenix overnight outdoor adventure camp on the Mogollon Rim "
        "(approximately 50 miles north of Payson, AZ). $250/camper includes "
        "transportation, meals, lodging, programming and supplies.",
        "overnight"))
    camps.append(make_camp(
        "Camp Colley Teen Leadership (CIT)", "Happy Jack", "AZ", "86024",
        "Camp Colley, Mogollon Rim (Happy Jack, AZ 86024)",
        COLLEY_COORDS[0], COLLEY_COORDS[1], 16, 17, 250, "Outdoor", "summer",
        COLLEY_URL,
        "Counselor-in-Training program at Camp Colley offering leadership training, "
        "job readiness coaching and youth mentorship experience. $250/camper.",
        "overnight"))
    out = {"source": "CampFind v26 Phoenix AZ Parks & Recreation summer camps (official pages)",
           "count": len(camps), "camps": camps}
    fn = os.path.join(ROOT, "app", "aca_camps_brands_v26.json")
    json.dump(out, open(fn, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"wrote {len(camps)} Phoenix camps -> {fn}")


if __name__ == "__main__":
    main()
