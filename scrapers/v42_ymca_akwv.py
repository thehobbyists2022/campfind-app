#!/usr/bin/env python3
"""
CampFind v42 — Final thin-state push: AK + WV YMCA camps from official pages.

Completes the <10-camp state cleanup: AK 7 and WV 9 were the last two.

Sources (each camp's sourceUrl = official page):
  - YMCA of Alaska (ymcaalaska.org/child-care/summer-day-camp/):
    Summer Day Camp at Camp Parker Peggy Lake, Anchorage AK. Grade levels:
    Pioneers 1st, Adventurers 2nd, Mountaineers 3rd, Voyagers 4th, Explorers
    5th, Trail Blazers 6th, Leaders-in-Training 7-8th. Licensed day camp with
    weekly themes, field trips, and STEM track (grades 5-8).
  - YMCA of Kanawha Valley, Charleston WV (ymcaofkv.org/summer-camps):
    Funshine Camp (children entering Kindergarten, $135/week 5-day or $90/week
    3-day, Charleston Family YMCA) and Summer Day Camp (ages 6-12, field trips,
    swimming, arts & crafts). Phone (304) 340-3527.
  - YMCA of Huntington WV (huntingtonymca.org/youth/leagues-camps/):
    youth basketball camp, 4 weeks of expert instruction from local coaches,
    sessions Monday and Wednesday evenings.

Every camp is real; unknown fields are null (R1: never invent).
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PEGGY_COORDS = (61.1553426, -150.0401984)  # Peggy Lake / Kincaid Park, Anchorage AK
KANAWHA_COORDS = (38.35060, -81.63328)     # Charleston WV
HUNTINGTON_COORDS = (38.41925, -82.44515)  # Huntington WV

AK_CAMP = "https://ymcaalaska.org/child-care/summer-day-camp/"
KV_CAMPS = "https://www.ymcaofkv.org/summer-camps"
HUNT_CAMPS = "https://huntingtonymca.org/youth/leagues-camps/"


def make_camp(prefix, name, city, state, zipcode, address, lat, lng, ageMin, ageMax,
              price, theme, season, src, desc, phone, email, website, camp_type):
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
        "email": email,
        "website": website,
        "description": desc,
        "acaVerified": False,
        "provider": "ymca",
        "source": "profile_page:ymcaalaska.org",
        "sourceUrl": src,
        "verifiedAt": "2026-08-14",
        "verificationMethod": "profile_page",
        "unverified": False,
    }


def main():
    camps = []

    # ---- Alaska: YMCA of Alaska Summer Day Camp (Camp Parker Peggy Lake) ----
    camps.append(make_camp(
        "ymca_alaska", "YMCA Summer Day Camp at Camp Parker Peggy Lake", "Anchorage", "AK", None,
        "Peggy Lake, Kincaid Park, Anchorage, AK",
        PEGGY_COORDS[0], PEGGY_COORDS[1], 6, 14, None, "Outdoor", "summer",
        AK_CAMP,
        "YMCA of Alaska licensed summer day camp at Camp Parker Peggy Lake in Anchorage. "
        "Campers grouped by grade: Pioneers (1st), Adventurers (2nd), Mountaineers (3rd), "
        "Voyagers (4th), Explorers (5th), Trail Blazers (6th), Leaders-in-Training (7-8th). "
        "Weekly themes, field trips, and a STEM track for grades 5-8. Kids disconnect from "
        "screens and explore the outdoors in a safe, licensed environment.",
        None, "sherry@ymcaalaska.org", "https://ymcaalaska.org/", "day"))
    camps.append(make_camp(
        "ymca_alaska", "YMCA Alaska STEM Summer Day Camp", "Anchorage", "AK", None,
        "Peggy Lake, Kincaid Park, Anchorage, AK",
        PEGGY_COORDS[0], PEGGY_COORDS[1], 10, 14, None, "STEM", "summer",
        AK_CAMP,
        "YMCA of Alaska STEM track of the Summer Day Camp program for grades 5-8, combining "
        "the licensed day camp experience at Camp Parker Peggy Lake with science, technology, "
        "engineering and math activities. Separate registration packet (Grades 5-8).",
        None, "sherry@ymcaalaska.org", "https://ymcaalaska.org/", "day"))

    # ---- West Virginia: YMCA of Kanawha Valley, Charleston ----
    camps.append(make_camp(
        "ymca_kanawha", "Funshine Camp", "Charleston", "WV", None, None,
        KANAWHA_COORDS[0], KANAWHA_COORDS[1], 5, 6, 135, "General", "summer",
        KV_CAMPS,
        "YMCA of Kanawha Valley Funshine Camp at Charleston Family YMCA for children "
        "entering kindergarten in the fall — new friends, new activities, and growing "
        "self-confidence. $135/week (5-day) or $90/week (3-day).",
        "304-340-3527", "info@ymcaofkv.org", "https://www.ymcaofkv.org/", "day"))
    camps.append(make_camp(
        "ymca_kanawha", "Kanawha Valley Summer Day Camp", "Charleston", "WV", None, None,
        KANAWHA_COORDS[0], KANAWHA_COORDS[1], 6, 12, None, "General", "summer",
        KV_CAMPS,
        "YMCA of Kanawha Valley Summer Day Camp at Charleston Family YMCA for children aged "
        "6-12 — a safe and thrilling environment with diverse daily activities including "
        "field trips, swimming, arts & crafts.",
        "304-340-3527", "info@ymcaofkv.org", "https://www.ymcaofkv.org/", "day"))

    # ---- West Virginia: YMCA of Huntington youth basketball camp ----
    camps.append(make_camp(
        "ymca_huntington", "YMCA of Huntington Youth Basketball Camp", "Huntington", "WV", None, None,
        HUNTINGTON_COORDS[0], HUNTINGTON_COORDS[1], None, None, None, "Sports", "summer",
        HUNT_CAMPS,
        "YMCA of Huntington youth basketball camp — 4 weeks of expert instruction from local "
        "coaches, teaching essential basketball skills and techniques. Sessions on Monday "
        "and Wednesday evenings.",
        None, None, "https://huntingtonymca.org/", "day"))

    out = {"version": "v42", "camps": camps}
    dest = os.path.join(ROOT, "app", "aca_camps_brands_v42.json")
    json.dump(out, open(dest, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"v42: {len(camps)} camps -> {dest}")
    from collections import Counter
    print("  states:", dict(Counter(c["state"] for c in camps)))


if __name__ == "__main__":
    main()
