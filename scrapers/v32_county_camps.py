#!/usr/bin/env python3
"""
CampFind v32 — Real county/city seasonal camps (official pages).

Sources (each camp's sourceUrl = the official page where it was verified):
  - LA County Parks (parks.lacounty.gov/esteam/):
    ESTEAM Summer Camp — 8-week summer camp, ages 6-11, environment/science/
    tech/engineering/arts/math blend, weekly field trips, multiple LA County parks.
  - LA County Parks (parks.lacounty.gov/everybody-plays-summer-adventures/):
    Every Body Plays: Summer Adventures — FREE, June 15 - Aug 7, ages 7-17,
    weekday activities incl. field trips (official page states "AGES 8-17" banner,
    "youth ages 7-17" in body; we use the body range 7-17).
  - Whittier CA (whittierprcs.org/recreation/youth-services/summer-day-camp):
    Summer Day Camp — all-day recreation program at City of Whittier facilities,
    crafts/games/field trips, registration opens April 13.

Every camp is a real program; unknown fields are null (R1: never invent).
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

LA_ESTEAM_SRC = "https://parks.lacounty.gov/esteam/"
LA_EBP_SRC = "https://parks.lacounty.gov/everybody-plays-summer-adventures/"
LA_REG = ("https://anc.apm.activecommunities.com/losangelescounty/activity/"
          "search?onlineSiteId=0&locale=en-US&activity_select_param=2&viewMode=list")
LA_COORDS = (34.0536909, -118.242766)  # Los Angeles city center (geocode cache)

WHITTIER_SRC = "https://www.whittierprcs.org/recreation/youth-services/summer-day-camp"
WHITTIER_REG = "https://secure.rec1.com/CA/city-of-whittier-ca/catalog"
WHITTIER_COORDS = (33.9796, -118.0327)  # Whittier city center


def make_camp(prefix, name, city, state, zipcode, address, lat, lng, ageMin, ageMax,
              price, theme, season, src, desc, phone, reg, camp_type="day"):
    slug = name.lower().replace(" ", "_").replace(".", "").replace("&", "and").replace(",", "").replace("'", "")
    return {
        "id": (prefix + "_" + slug)[:60],
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
        "phone": phone,
        "email": None,
        "website": reg,
        "description": desc,
        "acaVerified": False,
        "provider": "city",
        "source": "city_recreation:official",
        "sourceUrl": src,
        "verifiedAt": "2026-08-10",
        "verificationMethod": "official_city_page",
        "unverified": False,
    }


def main():
    camps = []

    # LA County ESTEAM Summer Camp
    camps.append(make_camp(
        "lacounty", "LA County ESTEAM Summer Camp", "Los Angeles", "CA", "90012",
        "Multiple LA County Parks (county-wide)",
        LA_COORDS[0], LA_COORDS[1], 6, 11, None, "STEM", "summer",
        LA_ESTEAM_SRC,
        "LA County Parks 8-week summer camp blending Environment, Science, Technology, "
        "Engineering, Arts and Mathematics for youth ages 6-11, with hands-on projects, "
        "weekly field trips (Natural History Museum, California Science Center, Santa Fe "
        "Dam, Day at the Marina) offered at select LA County parks.",
        None, LA_REG))

    # LA County Every Body Plays: Summer Adventures (FREE)
    camps.append(make_camp(
        "lacounty", "Every Body Plays Summer Adventures", "Los Angeles", "CA", "90012",
        "Multiple LA County Parks (county-wide)",
        LA_COORDS[0], LA_COORDS[1], 7, 17, 0, "General", "summer",
        LA_EBP_SRC,
        "FREE LA County Parks summer program (June 15 - August 7) for youth ages 7-17 "
        "with weekday activities including field trips, recreation and enrichment.",
        None, LA_REG))

    # Whittier Summer Day Camp
    camps.append(make_camp(
        "whittier", "Whittier Summer Day Camp", "Whittier", "CA", "90601",
        "City of Whittier facilities (Whittier Community Center)",
        WHITTIER_COORDS[0], WHITTIER_COORDS[1], None, None, None, "General", "summer",
        WHITTIER_SRC,
        "All-day summer recreation program hosted at City of Whittier facilities with "
        "activities, crafts, games and field trips (registration opens April 13).",
        None, WHITTIER_REG))

    out = {"source": "CampFind v32 county/city seasonal camps (official LA County + Whittier pages)",
           "count": len(camps), "camps": camps}
    fn = os.path.join(ROOT, "app", "aca_camps_brands_v32.json")
    json.dump(out, open(fn, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"wrote {len(camps)} camps -> {fn}")


if __name__ == "__main__":
    main()
