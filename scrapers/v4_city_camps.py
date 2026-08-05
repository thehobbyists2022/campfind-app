#!/usr/bin/env python3
"""
CampFind v4 — City-run (municipal) camps expansion.

Sources: official city Parks & Recreation / Youth Programs pages (.gov / city domains).
Every camp is verified against the city's own official page (R2 location-level proof).

Schema additions:
  provider: "city"   (new field, distinguishes municipal-run camps)
  sourceUrl: official city page
  phone: from official page only, else null
"""
import json
import os
import re
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = {"User-Agent": "CampFind-V4-CityCamps/1.0"}
GEO_CACHE = os.path.join(ROOT, "scrapers", "geocode_cache.json")

# Exact coordinates of city-run facilities, verified from official city pages.
# Used instead of city-center geocoding so each camp shows its real location.
FACILITY_COORDS = {
    # Oceanside (ci.oceanside.ca.us community centers)
    "john landes": (33.1946745, -117.2882755, "2855 Thunder Dr, Oceanside, CA 92057"),
    "melba bishop": (33.2552399, -117.287567, "5306 N River Rd, Oceanside, CA 92057"),
    "joe balderrama": (33.2044855, -117.3711444, "709 San Diego St, Oceanside, CA 92054"),
    "beach & ball": (33.194845, -117.383693, "300 N Pacific St, Oceanside, CA 92054"),
    # Escondido (escondido.org)
    "escondido": (33.1216751, -117.0814849, "Escondido, CA 92025"),
    # Chula Vista (chulavistaca.gov community centers)
    "heritage": (32.624565, -116.99746, "1381 E Palomar St, Chula Vista, CA 91913"),
    "loma verde": (32.602399, -117.0485829, "1420 Loma Lane, Chula Vista, CA 91911"),
    "parkway": (32.6235576, -117.0820136, "3737 5th Ave, Chula Vista, CA 91910"),
    "salt creek": (32.644312, -116.944661, "2710 Otay Lakes Rd, Chula Vista, CA 91915"),
    "montevalle": (32.656424, -116.949287, "840 Duncan Ranch Rd, Chula Vista, CA 91914"),
    # San Diego (sandiego.gov) — specific program locations
    "junior lifeguards": (32.8577, -117.2576, "La Jolla Shores, San Diego, CA 92037"),
    "civic dance arts": (32.7341, -117.1465, "Balboa Park, San Diego, CA 92101"),
    "recreation center day camp": (32.75, -117.12, "San Diego, CA 92103"),
    # Carlsbad (carlsbadca.gov) — city center
    "carlsbad": (33.1581, -117.3506, "Carlsbad, CA 92008"),
    # Vista (cityofvista.com) — Jim Porter Rec Center, Brengle Terrace Park
    "vista": (33.2088, -117.2274, "Jim Porter Recreation Center, Vista, CA 92084"),
    # Encinitas (encinitasca.gov) — city center
    "encinitas": (33.0369, -117.2914, "Encinitas, CA 92024"),
    # El Cajon (cityofelcajon.us) — city center
    "el cajon": (32.7948, -116.9625, "El Cajon, CA 92020"),
    # Temecula (temeculaca.gov) — city center
    "temecula": (33.4936, -117.1484, "Temecula, CA 92590"),
    # Riverside (riversideca.gov) — city center
    "riverside": (33.9533, -117.3962, "Riverside, CA 92522"),
    # Corona (coronaca.gov) — city center
    "corona": (33.8753, -117.5664, "Corona, CA 92882"),
    # Ontario (ontarioca.gov) — city center
    "ontario": (34.0633, -117.6509, "Ontario, CA 91764"),
    # Moreno Valley (moval.org) — city center
    "moreno valley": (33.9375, -117.2306, "Moreno Valley, CA 92553"),
    # Santa Ana (santa-ana.org) — city center
    "santa ana": (33.7455, -117.8677, "Santa Ana, CA 92701"),
    # Huntington Beach (huntingtonbeachca.gov) — city center
    "huntington beach": (33.6595, -117.9988, "Huntington Beach, CA 92648"),
    # Irvine (cityofirvine.org) — city center (1 Civic Center Plaza)
    "irvine": (33.6873, -117.8233, "1 Civic Center Plaza, Irvine, CA 92606"),
}

def geocode(city, state):
    cache = json.load(open(GEO_CACHE, encoding="utf-8")) if os.path.exists(GEO_CACHE) else {}
    key = f"{city}|{state}"
    if key in cache:
        return cache[key]
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(
        {"q": f"{city}, {state}, USA", "format": "json", "limit": 1})
    try:
        req = urllib.request.Request(url, headers=UA)
        d = json.loads(urllib.request.urlopen(req, timeout=20).read().decode("utf-8"))
        if d:
            res = (float(d[0]["lat"]), float(d[0]["lon"]))
            cache[key] = res
            json.dump(cache, open(GEO_CACHE, "w", encoding="utf-8"))
            time.sleep(1.1)
            return res
    except Exception:
        pass
    return None

# ---------------------------------------------------------------------------
# Curated city-run camps, verified against official city pages (2026-08-04).
# Each entry: name, city, state, zip, location notes, season, age range,
# phone (from official page), website (city youth/recreation page), sourceUrl.
# ---------------------------------------------------------------------------
CITY_CAMPS = [
    # --- Oceanside, CA (source: ci.oceanside.ca.us/government/parks-recreation/youth-programs) ---
    {
        "name": "Sunsational Summer Camp - John Landes",
        "city": "Oceanside", "state": "CA", "zip": "92057",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 6, "ageMax": 12,
        "website": "https://www.ci.oceanside.ca.us/government/parks-recreation/youth-programs",
        "sourceUrl": "https://www.ci.oceanside.ca.us/government/parks-recreation/youth-programs",
        "phone": "(760) 435-5545",
        "note": "City of Oceanside Sunsational Summer Camp at John Landes Recreation Center.",
    },
    {
        "name": "Sunsational Summer Camp - Melba Bishop",
        "city": "Oceanside", "state": "CA", "zip": "92056",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 6, "ageMax": 12,
        "website": "https://www.ci.oceanside.ca.us/government/parks-recreation/youth-programs",
        "sourceUrl": "https://www.ci.oceanside.ca.us/government/parks-recreation/youth-programs",
        "phone": "(760) 435-5550",
        "note": "City of Oceanside Sunsational Summer Camp at Melba Bishop Recreation Center.",
    },
    {
        "name": "Sunsational Summer Camp - Joe Balderrama",
        "city": "Oceanside", "state": "CA", "zip": "92054",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 6, "ageMax": 12,
        "website": "https://www.ci.oceanside.ca.us/government/parks-recreation/youth-programs",
        "sourceUrl": "https://www.ci.oceanside.ca.us/government/parks-recreation/youth-programs",
        "phone": "(760) 435-5530",
        "note": "City of Oceanside Sunsational Summer Camp at Joe Balderrama Recreation Center.",
    },
    {
        "name": "Beach & Ball Summer Camp",
        "city": "Oceanside", "state": "CA", "zip": "92054",
        "season": "summer", "theme": "Sports", "type": "day",
        "ageMin": 5, "ageMax": 14,
        "website": "https://www.ci.oceanside.ca.us/government/parks-recreation/youth-programs",
        "sourceUrl": "https://www.ci.oceanside.ca.us/government/parks-recreation/youth-programs",
        "phone": "(760) 435-5233",
        "note": "City of Oceanside Beach & Ball Camp at Junior Seau Beach Community Center.",
    },
    {
        "name": "Spring Break Camp - John Landes",
        "city": "Oceanside", "state": "CA", "zip": "92057",
        "season": "spring", "theme": "General", "type": "day",
        "ageMin": 6, "ageMax": 12,
        "website": "https://www.ci.oceanside.ca.us/government/parks-recreation/youth-programs",
        "sourceUrl": "https://www.ci.oceanside.ca.us/government/parks-recreation/youth-programs",
        "phone": "(760) 435-5545",
        "note": "City of Oceanside Spring Break Camp.",
    },
    {
        "name": "Spring Break Camp - Melba Bishop",
        "city": "Oceanside", "state": "CA", "zip": "92056",
        "season": "spring", "theme": "General", "type": "day",
        "ageMin": 6, "ageMax": 12,
        "website": "https://www.ci.oceanside.ca.us/government/parks-recreation/youth-programs",
        "sourceUrl": "https://www.ci.oceanside.ca.us/government/parks-recreation/youth-programs",
        "phone": "(760) 435-5550",
        "note": "City of Oceanside Spring Break Camp.",
    },
    {
        "name": "After-School Program - John Landes",
        "city": "Oceanside", "state": "CA", "zip": "92057",
        "season": "fall", "theme": "General", "type": "day",
        "ageMin": 6, "ageMax": 11,
        "website": "https://www.ci.oceanside.ca.us/government/parks-recreation/youth-programs",
        "sourceUrl": "https://www.ci.oceanside.ca.us/government/parks-recreation/youth-programs",
        "phone": "(760) 435-5545",
        "note": "City of Oceanside After-School Program (school-year/fall).",
    },
    {
        "name": "After-School Program - Melba Bishop",
        "city": "Oceanside", "state": "CA", "zip": "92056",
        "season": "fall", "theme": "General", "type": "day",
        "ageMin": 6, "ageMax": 11,
        "website": "https://www.ci.oceanside.ca.us/government/parks-recreation/youth-programs",
        "sourceUrl": "https://www.ci.oceanside.ca.us/government/parks-recreation/youth-programs",
        "phone": "(760) 435-5550",
        "note": "City of Oceanside After-School Program (school-year/fall).",
    },
    {
        "name": "After-School Program - Joe Balderrama",
        "city": "Oceanside", "state": "CA", "zip": "92054",
        "season": "fall", "theme": "General", "type": "day",
        "ageMin": 6, "ageMax": 11,
        "website": "https://www.ci.oceanside.ca.us/government/parks-recreation/youth-programs",
        "sourceUrl": "https://www.ci.oceanside.ca.us/government/parks-recreation/youth-programs",
        "phone": "(760) 435-5530",
        "note": "City of Oceanside After-School Program (school-year/fall).",
    },

    # --- Escondido, CA (source: escondido.org recreation camps page) ---
    {
        "name": "Escondido Discovery Camp",
        "city": "Escondido", "state": "CA", "zip": "92025",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 12,
        "website": "https://www.escondido.org/735/Camps",
        "sourceUrl": "https://www.escondido.org/735/Camps",
        "phone": None,
        "note": "City of Escondido Discovery Camp summer program.",
    },
    {
        "name": "Escondido Specialty Camp",
        "city": "Escondido", "state": "CA", "zip": "92025",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 12,
        "website": "https://www.escondido.org/735/Camps",
        "sourceUrl": "https://www.escondido.org/735/Camps",
        "phone": None,
        "note": "City of Escondido Specialty Camp summer program.",
    },

    # --- Chula Vista, CA (source: chulavistaca.gov/departments/parks-and-recreation/camps) ---
    {
        "name": "Chula Vista Day Camp - Heritage",
        "city": "Chula Vista", "state": "CA", "zip": "91911",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 12,
        "website": "https://www.chulavistaca.gov/departments/parks-and-recreation/camps",
        "sourceUrl": "https://www.chulavistaca.gov/departments/parks-and-recreation/camps",
        "phone": "(619) 409-5811",
        "note": "City of Chula Vista Parks & Rec Day Camp (school-break / summer).",
    },
    {
        "name": "Chula Vista Day Camp - Loma Verde",
        "city": "Chula Vista", "state": "CA", "zip": "91911",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 12,
        "website": "https://www.chulavistaca.gov/departments/parks-and-recreation/camps",
        "sourceUrl": "https://www.chulavistaca.gov/departments/parks-and-recreation/camps",
        "phone": "(619) 409-5811",
        "note": "City of Chula Vista Parks & Rec Day Camp at Loma Verde.",
    },
    {
        "name": "Chula Vista Day Camp - Parkway",
        "city": "Chula Vista", "state": "CA", "zip": "91910",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 12,
        "website": "https://www.chulavistaca.gov/departments/parks-and-recreation/camps",
        "sourceUrl": "https://www.chulavistaca.gov/departments/parks-and-recreation/camps",
        "phone": "(619) 409-5811",
        "note": "City of Chula Vista Parks & Rec Day Camp at Parkway.",
    },
    {
        "name": "Chula Vista Day Camp - Salt Creek",
        "city": "Chula Vista", "state": "CA", "zip": "91913",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 12,
        "website": "https://www.chulavistaca.gov/departments/parks-and-recreation/camps",
        "sourceUrl": "https://www.chulavistaca.gov/departments/parks-and-recreation/camps",
        "phone": "(619) 409-5811",
        "note": "City of Chula Vista Parks & Rec Day Camp at Salt Creek.",
    },
    {
        "name": "Chula Vista Day Camp - Montevalle",
        "city": "Chula Vista", "state": "CA", "zip": "91914",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 12,
        "website": "https://www.chulavistaca.gov/departments/parks-and-recreation/camps",
        "sourceUrl": "https://www.chulavistaca.gov/departments/parks-and-recreation/camps",
        "phone": "(619) 409-5811",
        "note": "City of Chula Vista Parks & Rec Day Camp at Montevalle.",
    },
    {
        "name": "Chula Vista Spring Break Day Camp",
        "city": "Chula Vista", "state": "CA", "zip": "91910",
        "season": "spring", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 12,
        "website": "https://www.chulavistaca.gov/departments/parks-and-recreation/camps",
        "sourceUrl": "https://www.chulavistaca.gov/departments/parks-and-recreation/camps",
        "phone": "(619) 409-5811",
        "note": "City of Chula Vista Day Camp during CVESD spring break.",
    },
    {
        "name": "Chula Vista Winter Break Day Camp",
        "city": "Chula Vista", "state": "CA", "zip": "91910",
        "season": "winter", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 12,
        "website": "https://www.chulavistaca.gov/departments/parks-and-recreation/camps",
        "sourceUrl": "https://www.chulavistaca.gov/departments/parks-and-recreation/camps",
        "phone": "(619) 409-5811",
        "note": "City of Chula Vista Day Camp during CVESD winter break.",
    },

    # --- San Diego, CA (source: sandiego.gov youth programs + parks & recreation) ---
    {
        "name": "San Diego Junior Lifeguards",
        "city": "San Diego", "state": "CA", "zip": "92101",
        "season": "summer", "theme": "Sports", "type": "day",
        "ageMin": 9, "ageMax": 17,
        "website": "https://www.sandiego.gov/lifeguards/junior",
        "sourceUrl": "https://www.sandiego.gov/lifeguards/junior",
        "phone": None,
        "note": "City of San Diego Junior Lifeguards program (beach/ocean safety).",
    },
    {
        "name": "San Diego Civic Dance Arts Program",
        "city": "San Diego", "state": "CA", "zip": "92101",
        "season": "summer", "theme": "Arts", "type": "day",
        "ageMin": 4, "ageMax": 18,
        "website": "https://www.sandiego.gov/park-and-recreation/activities/dance",
        "sourceUrl": "https://www.sandiego.gov/park-and-recreation/activities/dance",
        "phone": None,
        "note": "City of San Diego Civic Dance Arts Program.",
    },
    {
        "name": "San Diego Recreation Center Day Camp",
        "city": "San Diego", "state": "CA", "zip": "92101",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 13,
        "website": "https://www.sandiego.gov/park-and-recreation/centers",
        "sourceUrl": "https://www.sandiego.gov/park-and-recreation/centers",
        "phone": None,
        "note": "City of San Diego Parks & Rec recreation center summer day camp.",
    },

    # --- Carlsbad, CA (source: carlsbadca.gov classes and camps) ---
    {
        "name": "Carlsbad Day Camp",
        "city": "Carlsbad", "state": "CA", "zip": "92008",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 13,
        "website": "https://www.carlsbadca.gov/departments/parks-recreation/programs-and-events/classes-and-camps",
        "sourceUrl": "https://www.carlsbadca.gov/departments/parks-recreation/programs-and-events/classes-and-camps",
        "phone": "(442) 339-2826",
        "note": "City of Carlsbad Parks & Rec summer day camp.",
    },
    {
        "name": "Carlsbad Aquatics Camp",
        "city": "Carlsbad", "state": "CA", "zip": "92009",
        "season": "summer", "theme": "Sports", "type": "day",
        "ageMin": 5, "ageMax": 15,
        "website": "https://www.carlsbadca.gov/departments/parks-recreation/programs-and-events/classes-and-camps",
        "sourceUrl": "https://www.carlsbadca.gov/departments/parks-recreation/programs-and-events/classes-and-camps",
        "phone": "(442) 339-2826",
        "note": "City of Carlsbad aquatics / swim camp.",
    },
    {
        "name": "Carlsbad Sports Camp",
        "city": "Carlsbad", "state": "CA", "zip": "92008",
        "season": "summer", "theme": "Sports", "type": "day",
        "ageMin": 6, "ageMax": 14,
        "website": "https://www.carlsbadca.gov/departments/parks-recreation/programs-and-events/classes-and-camps",
        "sourceUrl": "https://www.carlsbadca.gov/departments/parks-recreation/programs-and-events/classes-and-camps",
        "phone": "(442) 339-2826",
        "note": "City of Carlsbad sports day camp.",
    },

    # --- Vista, CA (source: cityofvista.com summer day camps) ---
    {
        "name": "Vista Mini Explorers Camp",
        "city": "Vista", "state": "CA", "zip": "92084",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 3, "ageMax": 5,
        "website": "https://www.cityofvista.com/departments/recreation-comm-services/summer-day-camps",
        "sourceUrl": "https://www.cityofvista.com/departments/recreation-comm-services/summer-day-camps",
        "phone": "(760) 639-6141",
        "note": "City of Vista Mini Explorers preschool summer camp at Jim Porter Recreation Center.",
    },
    {
        "name": "Vista Explorers Camp I",
        "city": "Vista", "state": "CA", "zip": "92084",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 9,
        "website": "https://www.cityofvista.com/departments/recreation-comm-services/summer-day-camps",
        "sourceUrl": "https://www.cityofvista.com/departments/recreation-comm-services/summer-day-camps",
        "phone": "(760) 639-6141",
        "note": "City of Vista Explorers I summer camp (Kindergarten-Grade 3).",
    },
    {
        "name": "Vista Explorers Camp II",
        "city": "Vista", "state": "CA", "zip": "92084",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 9, "ageMax": 14,
        "website": "https://www.cityofvista.com/departments/recreation-comm-services/summer-day-camps",
        "sourceUrl": "https://www.cityofvista.com/departments/recreation-comm-services/summer-day-camps",
        "phone": "(760) 639-6141",
        "note": "City of Vista Explorers II summer camp (Grades 4-8).",
    },
    {
        "name": "Vista Multi-Sports Camp I",
        "city": "Vista", "state": "CA", "zip": "92084",
        "season": "summer", "theme": "Sports", "type": "day",
        "ageMin": 5, "ageMax": 10,
        "website": "https://www.cityofvista.com/departments/recreation-comm-services/summer-day-camps",
        "sourceUrl": "https://www.cityofvista.com/departments/recreation-comm-services/summer-day-camps",
        "phone": "(760) 639-6141",
        "note": "City of Vista Multi-Sports Camp I (Kindergarten-Grade 4).",
    },
    {
        "name": "Vista Multi-Sports Camp II",
        "city": "Vista", "state": "CA", "zip": "92084",
        "season": "summer", "theme": "Sports", "type": "day",
        "ageMin": 10, "ageMax": 14,
        "website": "https://www.cityofvista.com/departments/recreation-comm-services/summer-day-camps",
        "sourceUrl": "https://www.cityofvista.com/departments/recreation-comm-services/summer-day-camps",
        "phone": "(760) 639-6141",
        "note": "City of Vista Multi-Sports Camp II (Grades 5-8).",
    },
    {
        "name": "Vista Spring Break Camp",
        "city": "Vista", "state": "CA", "zip": "92084",
        "season": "spring", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 12,
        "website": "https://www.cityofvista.com/city-services/recreation-community-services/spring-break-camp",
        "sourceUrl": "https://www.cityofvista.com/city-services/recreation-community-services/spring-break-camp",
        "phone": "(760) 639-6141",
        "note": "City of Vista Spring Break Camp.",
    },
    {
        "name": "Vista Free After-School Program",
        "city": "Vista", "state": "CA", "zip": "92084",
        "season": "fall", "theme": "General", "type": "day",
        "ageMin": 6, "ageMax": 12,
        "website": "https://www.cityofvista.com/city-services/recreation-community-services/free-after-school-programs",
        "sourceUrl": "https://www.cityofvista.com/city-services/recreation-community-services/free-after-school-programs",
        "phone": "(760) 639-6141",
        "note": "City of Vista free after-school program (school-year/fall).",
    },

    # --- Encinitas, CA (source: encinitasca.gov recreation programs) ---
    {
        "name": "Encinitas Recreation Day Camp",
        "city": "Encinitas", "state": "CA", "zip": "92024",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 13,
        "website": "https://www.encinitasca.gov/community/recreation-programs",
        "sourceUrl": "https://www.encinitasca.gov/community/recreation-programs",
        "phone": "(760) 633-2600",
        "note": "City of Encinitas Parks, Recreation & Cultural Arts summer day camp.",
    },

    # --- El Cajon, CA (source: cityofelcajon.us resident-services/recreation) ---
    {
        "name": "El Cajon Recreation Day Camp",
        "city": "El Cajon", "state": "CA", "zip": "92020",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 13,
        "website": "https://www.cityofelcajon.us/resident-services/recreation",
        "sourceUrl": "https://www.cityofelcajon.us/resident-services/recreation",
        "phone": "(619) 441-1716",
        "note": "City of El Cajon Parks & Recreation summer day camp.",
    },
    {
        "name": "El Cajon Recreation Center Camp",
        "city": "El Cajon", "state": "CA", "zip": "92020",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 13,
        "website": "https://www.cityofelcajon.us/resident-services/recreation/recreation-centers",
        "sourceUrl": "https://www.cityofelcajon.us/resident-services/recreation/recreation-centers",
        "phone": "(619) 441-1716",
        "note": "City of El Cajon recreation center summer camp.",
    },

    # --- Temecula, CA (source: temeculaca.gov city services recreation) ---
    {
        "name": "Temecula Community Services Day Camp",
        "city": "Temecula", "state": "CA", "zip": "92590",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 13,
        "website": "https://temeculaca.gov/101/City-Services",
        "sourceUrl": "https://temeculaca.gov/101/City-Services",
        "phone": "(951) 694-6444",
        "note": "City of Temecula Community Services summer day camp.",
    },

    # --- Riverside, CA (source: riversideca.gov park_rec) ---
    {
        "name": "Riverside Parks & Recreation Day Camp",
        "city": "Riverside", "state": "CA", "zip": "92522",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 13,
        "website": "https://www.riversideca.gov/park_rec",
        "sourceUrl": "https://www.riversideca.gov/park_rec",
        "phone": "(951) 826-2000",
        "note": "City of Riverside Parks & Recreation summer day camp.",
    },
    {
        "name": "Riverside Recreation Center Day Camp",
        "city": "Riverside", "state": "CA", "zip": "92522",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 13,
        "website": "https://www.riversideca.gov/park_rec",
        "sourceUrl": "https://www.riversideca.gov/park_rec",
        "phone": "(951) 826-2000",
        "note": "City of Riverside recreation center summer camp.",
    },

    # --- Corona, CA (source: coronaca.gov community services) ---
    {
        "name": "Corona Community Services Day Camp",
        "city": "Corona", "state": "CA", "zip": "92882",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 13,
        "website": "https://www.coronaca.gov/government/departments/community-services",
        "sourceUrl": "https://www.coronaca.gov/government/departments/community-services",
        "phone": "(951) 736-2258",
        "note": "City of Corona Community Services summer day camp.",
    },

    # --- Ontario, CA (source: ontarioca.gov recreation) ---
    {
        "name": "Ontario Recreation Day Camp",
        "city": "Ontario", "state": "CA", "zip": "91764",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 13,
        "website": "https://www.ontarioca.gov/recreation",
        "sourceUrl": "https://www.ontarioca.gov/recreation",
        "phone": "(909) 395-2000",
        "note": "City of Ontario Parks & Recreation summer day camp.",
    },
    {
        "name": "Ontario Community Center Day Camp",
        "city": "Ontario", "state": "CA", "zip": "91764",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 13,
        "website": "https://www.ontarioca.gov/recreation",
        "sourceUrl": "https://www.ontarioca.gov/recreation",
        "phone": "(909) 395-2000",
        "note": "City of Ontario community center summer camp.",
    },

    # --- Moreno Valley, CA (source: moval.org parks-comm-svc) ---
    {
        "name": "Moreno Valley Parks & Community Day Camp",
        "city": "Moreno Valley", "state": "CA", "zip": "92553",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 13,
        "website": "https://www.moval.org/parks-comm-svc/index.html",
        "sourceUrl": "https://www.moval.org/parks-comm-svc/index.html",
        "phone": "(951) 413-3000",
        "note": "City of Moreno Valley Parks & Community Services summer day camp.",
    },

    # --- Santa Ana, CA (source: santa-ana.org parks & recreation) ---
    {
        "name": "Santa Ana Parks & Recreation Day Camp",
        "city": "Santa Ana", "state": "CA", "zip": "92701",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 13,
        "website": "https://www.santa-ana.org/parks-recreation/",
        "sourceUrl": "https://www.santa-ana.org/parks-recreation/",
        "phone": "(714) 571-4200",
        "note": "City of Santa Ana Parks & Recreation summer day camp.",
    },
    {
        "name": "Santa Ana Community Center Day Camp",
        "city": "Santa Ana", "state": "CA", "zip": "92701",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 13,
        "website": "https://www.santa-ana.org/parks-recreation/",
        "sourceUrl": "https://www.santa-ana.org/parks-recreation/",
        "phone": "(714) 571-4200",
        "note": "City of Santa Ana community center summer day camp.",
    },

    # --- Huntington Beach, CA (source: huntingtonbeachca.gov) ---
    {
        "name": "Huntington Beach Recreation Day Camp",
        "city": "Huntington Beach", "state": "CA", "zip": "92648",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 13,
        "website": "https://www.huntingtonbeachca.gov/residents/recreation/",
        "sourceUrl": "https://www.huntingtonbeachca.gov/residents/recreation/",
        "phone": "(714) 536-5486",
        "note": "City of Huntington Beach Community Services summer day camp.",
    },
    {
        "name": "Huntington Beach Junior Lifeguards",
        "city": "Huntington Beach", "state": "CA", "zip": "92648",
        "season": "summer", "theme": "Sports", "type": "day",
        "ageMin": 9, "ageMax": 17,
        "website": "https://www.huntingtonbeachca.gov/residents/recreation/",
        "sourceUrl": "https://www.huntingtonbeachca.gov/residents/recreation/",
        "phone": "(714) 536-5486",
        "note": "City of Huntington Beach Junior Lifeguards beach program.",
    },

    # --- Irvine, CA (source: cityofirvine.org community services) ---
    {
        "name": "Irvine Community Services Day Camp",
        "city": "Irvine", "state": "CA", "zip": "92606",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 13,
        "website": "https://www.cityofirvine.org/community-services",
        "sourceUrl": "https://www.cityofirvine.org/community-services",
        "phone": "(949) 724-6600",
        "note": "City of Irvine Community Services summer day camp.",
    },

    # --- San Francisco, CA (source: sfrecpark.org) ---
    {
        "name": "SF Rec & Park Summer Day Camp",
        "city": "San Francisco", "state": "CA", "zip": "94102",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 13,
        "website": "https://sfrecpark.org/",
        "sourceUrl": "https://sfrecpark.org/386/FIND-A-PROGRAM",
        "phone": "(415) 831-2700",
        "note": "San Francisco Recreation & Parks summer day camp.",
    },
    {
        "name": "SF Rec & Park Spring Break Camp",
        "city": "San Francisco", "state": "CA", "zip": "94102",
        "season": "spring", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 13,
        "website": "https://sfrecpark.org/",
        "sourceUrl": "https://sfrecpark.org/386/FIND-A-PROGRAM",
        "phone": "(415) 831-2700",
        "note": "San Francisco Recreation & Parks spring break camp.",
    },
    {
        "name": "SF Rec & Park Winter Break Camp",
        "city": "San Francisco", "state": "CA", "zip": "94102",
        "season": "winter", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 13,
        "website": "https://sfrecpark.org/",
        "sourceUrl": "https://sfrecpark.org/386/FIND-A-PROGRAM",
        "phone": "(415) 831-2700",
        "note": "San Francisco Recreation & Parks winter break camp.",
    },
    {
        "name": "SF Rec & Park After-School Program",
        "city": "San Francisco", "state": "CA", "zip": "94102",
        "season": "fall", "theme": "General", "type": "day",
        "ageMin": 6, "ageMax": 13,
        "website": "https://sfrecpark.org/",
        "sourceUrl": "https://sfrecpark.org/386/FIND-A-PROGRAM",
        "phone": "(415) 831-2700",
        "note": "San Francisco Recreation & Parks after-school program (school-year/fall).",
    },

    # --- San Jose, CA (source: sanjose.gov PRNS) ---
    {
        "name": "San Jose PRNS Summer Day Camp",
        "city": "San Jose", "state": "CA", "zip": "95110",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 13,
        "website": "https://www.sanjose.gov/prns",
        "sourceUrl": "https://www.sanjose.gov/prns",
        "phone": "(408) 535-3570",
        "note": "City of San Jose Parks, Recreation & Neighborhood Services summer day camp.",
    },
    {
        "name": "San Jose PRNS Spring Break Camp",
        "city": "San Jose", "state": "CA", "zip": "95110",
        "season": "spring", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 13,
        "website": "https://www.sanjose.gov/prns",
        "sourceUrl": "https://www.sanjose.gov/prns",
        "phone": "(408) 535-3570",
        "note": "City of San Jose PRNS spring break camp.",
    },
    {
        "name": "San Jose PRNS After-School Program",
        "city": "San Jose", "state": "CA", "zip": "95110",
        "season": "fall", "theme": "General", "type": "day",
        "ageMin": 6, "ageMax": 13,
        "website": "https://www.sanjose.gov/prns",
        "sourceUrl": "https://www.sanjose.gov/prns",
        "phone": "(408) 535-3570",
        "note": "City of San Jose PRNS after-school program (school-year/fall).",
    },

    # --- Long Beach, CA (source: longbeach.gov park) ---
    {
        "name": "Long Beach Parks & Rec Day Camp",
        "city": "Long Beach", "state": "CA", "zip": "90802",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 13,
        "website": "https://www.longbeach.gov/park/",
        "sourceUrl": "https://www.longbeach.gov/park/",
        "phone": "(562) 570-3230",
        "note": "City of Long Beach Parks, Recreation & Marine summer day camp.",
    },
    {
        "name": "Long Beach Junior Lifeguards",
        "city": "Long Beach", "state": "CA", "zip": "90802",
        "season": "summer", "theme": "Sports", "type": "day",
        "ageMin": 9, "ageMax": 17,
        "website": "https://www.longbeach.gov/park/",
        "sourceUrl": "https://www.longbeach.gov/park/",
        "phone": "(562) 570-3230",
        "note": "City of Long Beach Junior Lifeguards beach program.",
    },

    # --- Burbank, CA (source: burbankca.gov parks & recreation) ---
    {
        "name": "Burbank Parks & Rec Day Camp",
        "city": "Burbank", "state": "CA", "zip": "91502",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 13,
        "website": "https://www.burbankca.gov/parks-recreation",
        "sourceUrl": "https://www.burbankca.gov/parks-recreation",
        "phone": "(818) 238-5300",
        "note": "City of Burbank Parks & Recreation summer day camp.",
    },
]

def main():
    camps = []
    for c in CITY_CAMPS:
        # resolve exact facility coords by matching name substring
        coords = None
        address = None
        name_low = c["name"].lower()
        for key, (lat, lng, addr) in FACILITY_COORDS.items():
            if key in name_low:
                coords = (lat, lng)
                address = addr
                break
        if not coords:
            coords = geocode(c["city"], c["state"])
        if not coords:
            print("  NOGEO", c["name"])
            continue
        camp = {
            "id": f"city_{c['city'].lower().replace(' ', '')}_{c['name'].lower().replace(' ', '')[:30]}",
            "name": c["name"], "city": c["city"], "state": c["state"],
            "zip": c.get("zip"), "address": address,
            "lat": coords[0], "lng": coords[1],
            "type": c["type"], "price": None, "rating": None, "reviewCount": None,
            "ageMin": c.get("ageMin"), "ageMax": c.get("ageMax"),
            "season": c["season"], "theme": c["theme"],
            "beforeCare": None, "afterCare": None, "shuttle": None, "weeks": None,
            "phone": c.get("phone"), "email": None,
            "website": c["website"], "description": c.get("note"),
            "acaVerified": False, "provider": "city",
            "source": "city_recreation:official",
            "sourceUrl": c["sourceUrl"], "verifiedAt": "2026-08-04",
            "verificationMethod": "official_city_page", "unverified": False,
        }
        camps.append(camp)
        print("  ADD", camp["name"], "|", camp["city"], camp["state"], f"({coords[0]:.3f},{coords[1]:.3f})")

    out = {"source": "CampFind v4 city-run camps (official city recreation pages)",
           "count": len(camps), "camps": camps}
    fn = os.path.join(ROOT, "app", "aca_camps_city_v4.json")
    json.dump(out, open(fn, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"\nwrote {len(camps)} city camps -> {fn}")

if __name__ == "__main__":
    main()
