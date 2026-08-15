#!/usr/bin/env python3
"""
CampFind v40 — More thin-state real camps (AK/ME/WV/MS) from official pages.

Continues v38's thin-state coverage push. The blocked city sites (Sioux Falls
SD, Anchorage AK portal, Portland ME) are bypassed with official camp pages
that ARE crawlable, plus the Gulfport MS municipal program found via search.

Sources (each camp's sourceUrl = official page):
  - Camp Fire Alaska — Camp Fireweed (campfireak.org/our-programs/summer-camps/camp-fireweed/):
    day camp on Alaska Pacific University campus, Anchorage; weekly Jun 1 - Aug 14, 2026;
    swimming/boating/archery; 7:30am-5:30pm.
  - Camp Fire Alaska — Camp K (campfireak.org/our-programs/summer-camps/camp-k/):
    overnight camp on Kenai Lake, Cooper Landing AK (Chugach National Forest);
    ages 6-17, 5 days/4 nights sessions; longest-running all-gender overnight camp in AK.
  - Camp Fire Alaska — Summer Adventure (campfireak.org/our-programs/summer-camps/summer-adventure/):
    licensed day camp at Anchorage/Eagle River elementary schools; $415/week
    ($330 for Juneteenth/4th-of-July/Aug 3 weeks); weekly field trips to Camp Fireweed.
  - Camp Chewonki (camp.chewonki.org): overnight camp in Wiscasset ME, grades 3-8
    (approx ages 8-14), full session + Maine wilderness trips; ACA-accredited (acacamps.org link).
  - Camp Alleghany for Girls (campalleghany.com): all-girls overnight camp in
    Greenbrier County WV (Camp Alleghany Rd, Caldwell WV 24925); since 1922.
  - City of Gulfport MS — Summer Day Camp (gulfport-ms.gov/government/summer_camp.php):
    one of MS's largest municipal summer camp programs; 4 sites (Harrison Central
    Elementary ages 5-8; Bel-Aire Elementary 5-12; Herbert Wilson Center 5-12;
    Three Rivers Elementary 5-12); free lunch; MS Dept of Health licensed;
    phone 228-868-5881 / summercamp@gulfport-ms.gov.

Every camp is real; unknown fields are null (R1: never invent).
"""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CO = {
    'fireweed': (61.1915342, -149.8007868),   # Alaska Pacific University, Anchorage
    'campk': (60.4898309, -149.8328412),      # Cooper Landing AK (Kenai Lake)
    'summeradv': (61.2163129, -149.894852),   # Anchorage city center
    'chewonki': (43.9417784, -69.71744),      # 485 Chewonki Neck Rd, Wiscasset ME
    'alleghany': (37.7806772, -80.3939618),   # Caldwell WV
    'gulfport_harrison': (30.3674198, -89.0928155),
    'gulfport_belaire': (30.4408057, -89.0878197),
    'gulfport_wilson': (30.3882882, -89.0507988),
    'gulfport_threerivers': (30.4838164, -89.0685029),
}

CFA_FIREWEED = "https://campfireak.org/our-programs/summer-camps/camp-fireweed/"
CFA_CAMPK = "https://campfireak.org/our-programs/summer-camps/camp-k/"
CFA_ADV = "https://campfireak.org/our-programs/summer-camps/summer-adventure/"
CHEWONKI = "https://camp.chewonki.org"
ALLEGHANY = "https://www.campalleghany.com/"
GULFPORT = "https://www.gulfport-ms.gov/government/summer_camp.php"


def make_camp(prefix, name, city, state, zipcode, address, lat, lng, ageMin, ageMax,
              price, theme, season, src, desc, phone, email, website, camp_type,
              source, method):
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
        "provider": "camp",
        "source": source,
        "sourceUrl": src,
        "verifiedAt": "2026-08-14",
        "verificationMethod": method,
        "unverified": False,
    }


def main():
    camps = []

    # ---- Alaska: Camp Fire Alaska (3 camps) ----
    camps.append(make_camp(
        "campfire", "Camp Fireweed", "Anchorage", "AK", "99508",
        "Alaska Pacific University campus, 4101 University Dr, Anchorage, AK 99508",
        CO['fireweed'][0], CO['fireweed'][1], None, None, None, "Outdoor", "summer",
        CFA_FIREWEED,
        "Camp Fire Alaska day camp on the Alaska Pacific University campus in Anchorage, "
        "offered weekly June 1 - August 14, 2026 (no camp June 19 or July 3). Campers swim "
        "1-2 days/week with certified lifeguards, explore University Lake by canoe and kayak, "
        "and get archery instruction at the camp's shooting range. Hours 7:30am-5:30pm.",
        None, "campfire@campfireak.org", "https://campfireak.org/", "day",
        "profile_page:campfireak.org", "profile_page"))

    camps.append(make_camp(
        "campfire", "Camp K", "Cooper Landing", "AK", "99572",
        "Kenai Lake, Cooper Landing, AK 99572 (160-acre campus in Chugach National Forest)",
        CO['campk'][0], CO['campk'][1], 6, 17, None, "Outdoor", "summer",
        CFA_CAMPK,
        "Alaska's longest-running all-gender overnight camp on the shores of Kenai Lake in "
        "Cooper Landing, a two-hour bus ride from Anchorage. 160-acre campus within the "
        "Chugach National Forest. Traditional camp sessions ages 6-17, 5 days/4 nights; "
        "transportation and camp t-shirt included.",
        None, "campfire@campfireak.org", "https://campfireak.org/", "overnight",
        "profile_page:campfireak.org", "profile_page"))

    camps.append(make_camp(
        "campfire", "Camp Fire Summer Adventure", "Anchorage", "AK", None, None,
        CO['summeradv'][0], CO['summeradv'][1], None, None, 415, "General", "summer",
        CFA_ADV,
        "Camp Fire Alaska licensed day camp running all day at elementary schools in "
        "Anchorage and Eagle River, weekly through the summer (no camp June 19 or July 3). "
        "$415/week ($330/week for the Juneteenth, 4th-of-July and Aug 3 weeks). Weekly field "
        "trips to Camp Fireweed for all campers; add-on field trips every Wednesday. "
        "Peanut-free. Hours 7:30am-5:50pm.",
        None, "campfire@campfireak.org", "https://campfireak.org/", "day",
        "profile_page:campfireak.org", "profile_page"))

    # ---- Maine: Camp Chewonki ----
    camps.append(make_camp(
        "chewonki", "Camp Chewonki", "Wiscasset", "ME", "04578",
        "485 Chewonki Neck Rd, Wiscasset, ME 04578",
        CO['chewonki'][0], CO['chewonki'][1], 8, 14, None, "Outdoor", "summer",
        CHEWONKI,
        "Overnight camp on Chewonki Neck in Wiscasset, Maine for campers in grades 3-8 "
        "(ages approx 8-14), with full-session programs plus Maine wilderness trips "
        "(Appalachian Trail backpacking, Northwoods canoeing, coast kayaking). ACA-accredited "
        "camp (acacamps.org member).",
        None, None, "https://camp.chewonki.org", "overnight",
        "profile_page:chewonki.org", "profile_page"))

    # ---- West Virginia: Camp Alleghany for Girls ----
    camps.append(make_camp(
        "alleghany", "Camp Alleghany for Girls", "Caldwell", "WV", "24925",
        "Camp Alleghany Road, Caldwell, WV 24925",
        CO['alleghany'][0], CO['alleghany'][1], 6, 16, None, "Outdoor", "summer",
        ALLEGHANY,
        "All-girls overnight summer camp in Greenbrier County, West Virginia, centered on "
        "girls since 1922. Programs focus on building healthy self-esteem, independence and "
        "confidence, with mother-daughter weekends and short stays for younger girls.",
        None, None, "https://www.campalleghany.com/", "overnight",
        "profile_page:campalleghany.com", "profile_page"))

    # ---- Mississippi: Gulfport Summer Day Camp (4 sites) ----
    gulf_sites = [
        ("Harrison Central Elementary", "Harrison", 5, 8),
        ("Bel-Aire Elementary", "Belaire", 5, 12),
        ("Herbert Wilson Center", "Wilson", 5, 12),
        ("Three Rivers Elementary", "ThreeRivers", 5, 12),
    ]
    for label, key, amin, amax in gulf_sites:
        camps.append(make_camp(
            "gulfport", f"Gulfport Summer Day Camp - {label}", "Gulfport", "MS", None, None,
            CO[f'gulfport_{key.lower()}'][0], CO[f'gulfport_{key.lower()}'][1],
            amin, amax, None, "General", "summer",
            GULFPORT,
            f"City of Gulfport Department of Leisure Services Summer Day Camp at {label} — "
            "one of Mississippi's largest municipal summer camp programs, with weekly "
            "activities promoting learning, creativity, teamwork and healthy lifestyles. "
            "Free lunch served daily through the summer lunch program; fully licensed by "
            "the MS State Department of Health. Non-refundable registration fee required.",
            "228-868-5881", "summercamp@gulfport-ms.gov", "https://www.gulfport-ms.gov/", "day",
            "city_recreation:official", "official_city_page"))

    out = {"version": "v40", "camps": camps}
    dest = os.path.join(ROOT, "app", "aca_camps_brands_v40.json")
    json.dump(out, open(dest, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"v40: {len(camps)} camps -> {dest}")
    from collections import Counter
    print("  states:", dict(Counter(c["state"] for c in camps)))


if __name__ == "__main__":
    main()
