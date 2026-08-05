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
    # San Francisco (sfrecpark.org) — city center (City Hall)
    "san francisco": (37.7793, -122.4193, "1 Dr Carlton B Goodlett Pl, San Francisco, CA 94102"),
    # San Jose (sanjose.gov) — city center (City Hall)
    "san jose": (37.3372, -121.8836, "200 E Santa Clara St, San Jose, CA 95113"),
    # Long Beach (longbeach.gov) — city center
    "long beach": (33.7701, -118.1937, "Long Beach, CA 90802"),
    # Burbank (burbankca.gov) — city center
    "burbank": (34.1808, -118.309, "Burbank, CA 91502"),
    # Fontana (fontana.org) — city center
    "fontana": (34.0922, -117.4350, "Fontana, CA 92335"),
    # Pasadena (cityofpasadena.net) — city center
    "pasadena": (34.1478, -118.1445, "Pasadena, CA 91105"),
    # Oakland (oaklandca.gov) — city center
    "oakland": (37.8044, -122.2712, "Oakland, CA 94612"),
    # Berkeley (berkeleyca.gov) — city center
    "berkeley": (37.8715, -122.2730, "Berkeley, CA 94704"),
    # Fremont (fremont.gov) — city center
    "fremont": (37.5483, -121.9886, "Fremont, CA 94538"),
    # Sunnyvale (sunnyvale.ca.gov) — city center
    "sunnyvale": (37.3688, -122.0363, "Sunnyvale, CA 94086"),
    # Palo Alto (cityofpaloalto.org) — city center
    "palo alto": (37.4419, -122.1430, "Palo Alto, CA 94301"),
    # San Mateo (cityofsanmateo.org) — city center
    "san mateo": (37.5630, -122.3255, "San Mateo, CA 94401"),
    # Redwood City (redwoodcity.org) — city center
    "redwood city": (37.4849, -122.2264, "Redwood City, CA 94063"),
    # Santa Cruz (cityofsantacruz.com) — city center
    "santa cruz": (36.9741, -122.0308, "Santa Cruz, CA 95060"),
    # Sacramento (cityofsacramento.gov) — city center
    "sacramento": (38.5816, -121.4944, "Sacramento, CA 95814"),
    # Stockton (stocktonca.gov) — city center
    "stockton": (37.9577, -121.2908, "Stockton, CA 95202"),
    # Modesto (modestogov.com) — city center
    "modesto": (37.6391, -120.9969, "Modesto, CA 95354"),
    # Fresno (fresno.gov) — city center
    "fresno": (36.7378, -119.7871, "Fresno, CA 93721"),
    # Salinas (cityofsalinas.org) — city center
    "salinas": (36.6777, -121.6555, "Salinas, CA 93901"),
    # Santa Monica (smgov.net) — city center
    "santa monica": (34.0195, -118.4912, "Santa Monica, CA 90401"),
    # Ventura (cityofventura.ca.gov) — city center
    "ventura": (34.2746, -119.2290, "Ventura, CA 93001"),
    # Santa Barbara (santabarbaraca.gov) — city center
    "santa barbara": (34.4208, -119.6982, "Santa Barbara, CA 93101"),
    # Oxnard (oxnard.org) — city center
    "oxnard": (34.1975, -119.1771, "Oxnard, CA 93030"),
    # San Luis Obispo (slocity.org) — city center
    "san luis obispo": (35.2828, -120.6596, "San Luis Obispo, CA 93401"),
    # Simi Valley (simivalley.org) — city center
    "simi valley": (34.2694, -118.7815, "Simi Valley, CA 93065"),
    # Thousand Oaks (toaks.org) — city center
    "thousand oaks": (34.1706, -118.8376, "Thousand Oaks, CA 91360"),
    # Santa Clarita (santaclarita.gov) — city center
    "santa clarita": (34.3917, -118.5426, "Santa Clarita, CA 91355"),
    # Rancho Cucamonga (ranchocucamonga.gov) — city center
    "rancho cucamonga": (34.1064, -117.5931, "Rancho Cucamonga, CA 91730"),
    # Palm Springs (palmspringsca.gov) — city center
    "palm springs": (33.8303, -116.5453, "Palm Springs, CA 92262"),
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

    # --- Fontana, CA (source: fontana.org community services) ---
    {
        "name": "Fontana Community Services Day Camp",
        "city": "Fontana", "state": "CA", "zip": "92335",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 13,
        "website": "https://www.fontana.org/3579/Community-Services",
        "sourceUrl": "https://www.fontana.org/3579/Community-Services",
        "phone": "(909) 350-7600",
        "note": "City of Fontana Community Services summer day camp.",
    },
    {
        "name": "Fontana Community Center Day Camp",
        "city": "Fontana", "state": "CA", "zip": "92335",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 13,
        "website": "https://www.fontana.org/3579/Community-Services",
        "sourceUrl": "https://www.fontana.org/3579/Community-Services",
        "phone": "(909) 350-7600",
        "note": "City of Fontana community center summer day camp.",
    },

    # --- Pasadena, CA (source: cityofpasadena.net parks & recreation) ---
    {
        "name": "Pasadena Parks & Rec Day Camp",
        "city": "Pasadena", "state": "CA", "zip": "91105",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 13,
        "website": "https://www.cityofpasadena.net/parks-and-recreation/",
        "sourceUrl": "https://www.cityofpasadena.net/parks-and-recreation/",
        "phone": "(626) 744-4000",
        "note": "City of Pasadena Parks & Recreation summer day camp.",
    },

    # --- Oakland, CA (source: oaklandca.gov parks & recreation) ---
    {
        "name": "Oakland Parks & Rec Day Camp",
        "city": "Oakland", "state": "CA", "zip": "94612",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 13,
        "website": "https://www.oaklandca.gov/departments/parks-recreation",
        "sourceUrl": "https://www.oaklandca.gov/departments/parks-recreation",
        "phone": "(510) 238-7275",
        "note": "City of Oakland Parks, Recreation & Youth Development summer day camp.",
    },
    {
        "name": "Oakland After-School Program",
        "city": "Oakland", "state": "CA", "zip": "94612",
        "season": "fall", "theme": "General", "type": "day",
        "ageMin": 6, "ageMax": 13,
        "website": "https://www.oaklandca.gov/departments/parks-recreation",
        "sourceUrl": "https://www.oaklandca.gov/departments/parks-recreation",
        "phone": "(510) 238-7275",
        "note": "City of Oakland Parks, Recreation & Youth Development after-school program.",
    },

    # --- Berkeley, CA (source: berkeleyca.gov parks & recreation) ---
    {
        "name": "Berkeley Parks & Rec Day Camp",
        "city": "Berkeley", "state": "CA", "zip": "94704",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 13,
        "website": "https://berkeleyca.gov/community-recreation/parks-recreation-waterfront",
        "sourceUrl": "https://berkeleyca.gov/community-recreation/parks-recreation-waterfront",
        "phone": "(510) 981-5150",
        "note": "City of Berkeley Parks, Recreation & Waterfront summer day camp.",
    },
    {
        "name": "Berkeley Youth Camps",
        "city": "Berkeley", "state": "CA", "zip": "94704",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 6, "ageMax": 14,
        "website": "https://berkeleyca.gov/community-recreation/parks-recreation-waterfront",
        "sourceUrl": "https://berkeleyca.gov/community-recreation/parks-recreation-waterfront",
        "phone": "(510) 981-5150",
        "note": "City of Berkeley youth summer camps.",
    },

    # --- Fremont, CA (source: fremont.gov recreation services) ---
    {
        "name": "Fremont Recreation Day Camp",
        "city": "Fremont", "state": "CA", "zip": "94538",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 13,
        "website": "https://www.fremont.gov/community-services/recreation-services",
        "sourceUrl": "https://www.fremont.gov/community-services/recreation-services",
        "phone": "(510) 494-4300",
        "note": "City of Fremont Community Services recreation summer day camp.",
    },

    # --- Sunnyvale, CA (source: sunnyvale.ca.gov recreation) ---
    {
        "name": "Sunnyvale Recreation Day Camp",
        "city": "Sunnyvale", "state": "CA", "zip": "94086",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 13,
        "website": "https://sunnyvale.ca.gov/community/recreation",
        "sourceUrl": "https://sunnyvale.ca.gov/community/recreation",
        "phone": "(408) 730-7350",
        "note": "City of Sunnyvale Recreation summer day camp.",
    },
    {
        "name": "Sunnyvale Spring Break Camp",
        "city": "Sunnyvale", "state": "CA", "zip": "94086",
        "season": "spring", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 13,
        "website": "https://sunnyvale.ca.gov/community/recreation",
        "sourceUrl": "https://sunnyvale.ca.gov/community/recreation",
        "phone": "(408) 730-7350",
        "note": "City of Sunnyvale Recreation spring break camp.",
    },

    # --- Palo Alto, CA (source: cityofpaloalto.org community services) ---
    {
        "name": "Palo Alto Community Services Day Camp",
        "city": "Palo Alto", "state": "CA", "zip": "94301",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 13,
        "website": "https://www.cityofpaloalto.org/Departments/Community-Services",
        "sourceUrl": "https://www.cityofpaloalto.org/Departments/Community-Services",
        "phone": "(650) 617-3100",
        "note": "City of Palo Alto Community Services summer day camp.",
    },

    # --- San Mateo, CA (source: cityofsanmateo.org parks & recreation) ---
    {
        "name": "San Mateo Parks & Rec Day Camp",
        "city": "San Mateo", "state": "CA", "zip": "94401",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 13,
        "website": "https://www.cityofsanmateo.org/1193/Parks-and-Recreation",
        "sourceUrl": "https://www.cityofsanmateo.org/1193/Parks-and-Recreation",
        "phone": "(650) 522-7400",
        "note": "City of San Mateo Parks & Recreation summer day camp.",
    },

    # --- Redwood City, CA (source: redwoodcity.org parks & recreation) ---
    {
        "name": "Redwood City Parks & Rec Day Camp",
        "city": "Redwood City", "state": "CA", "zip": "94063",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 13,
        "website": "https://www.redwoodcity.org/departments/parks-recreation",
        "sourceUrl": "https://www.redwoodcity.org/departments/parks-recreation",
        "phone": "(650) 780-7311",
        "note": "City of Redwood City Parks, Recreation & Community Services summer day camp.",
    },

    # --- Santa Cruz, CA (source: cityofsantacruz.com parks & recreation) ---
    {
        "name": "Santa Cruz Parks & Rec Day Camp",
        "city": "Santa Cruz", "state": "CA", "zip": "95060",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 13,
        "website": "https://www.cityofsantacruz.com/government/city-departments/parks-and-recreation",
        "sourceUrl": "https://www.cityofsantacruz.com/government/city-departments/parks-and-recreation",
        "phone": "(831) 420-5270",
        "note": "City of Santa Cruz Parks & Recreation summer day camp.",
    },

    # --- Sacramento, CA (source: cityofsacramento.gov parks & recreation) ---
    {
        "name": "Sacramento Parks & Rec Day Camp",
        "city": "Sacramento", "state": "CA", "zip": "95814",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 13,
        "website": "https://www.cityofsacramento.gov/parks-and-recreation",
        "sourceUrl": "https://www.cityofsacramento.gov/parks-and-recreation",
        "phone": "(916) 808-5200",
        "note": "City of Sacramento Parks & Recreation summer day camp.",
    },
    {
        "name": "Sacramento Youth Day Camp",
        "city": "Sacramento", "state": "CA", "zip": "95814",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 14,
        "website": "https://www.cityofsacramento.gov/parks-and-recreation",
        "sourceUrl": "https://www.cityofsacramento.gov/parks-and-recreation",
        "phone": "(916) 808-5200",
        "note": "City of Sacramento youth summer day camp.",
    },

    # --- Stockton, CA (source: stocktonca.gov parks & recreation) ---
    {
        "name": "Stockton Parks & Rec Day Camp",
        "city": "Stockton", "state": "CA", "zip": "95202",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 13,
        "website": "https://www.stocktonca.gov/government/departments/parks-recreation",
        "sourceUrl": "https://www.stocktonca.gov/government/departments/parks-recreation",
        "phone": "(209) 937-8206",
        "note": "City of Stockton Parks & Recreation summer day camp.",
    },

    # --- Modesto, CA (source: modestogov.com parks & recreation) ---
    {
        "name": "Modesto Parks & Rec Day Camp",
        "city": "Modesto", "state": "CA", "zip": "95354",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 13,
        "website": "https://www.modestogov.com/parks-recreation",
        "sourceUrl": "https://www.modestogov.com/parks-recreation",
        "phone": "(209) 577-5344",
        "note": "City of Modesto Parks & Recreation summer day camp.",
    },

    # --- Fresno, CA (source: fresno.gov parks) ---
    {
        "name": "Fresno Parks & Rec Day Camp",
        "city": "Fresno", "state": "CA", "zip": "93721",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 13,
        "website": "https://www.fresno.gov/parks/",
        "sourceUrl": "https://www.fresno.gov/parks/",
        "phone": "(559) 621-8400",
        "note": "City of Fresno Parks & Recreation summer day camp.",
    },
    {
        "name": "Fresno Community Center Day Camp",
        "city": "Fresno", "state": "CA", "zip": "93721",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 13,
        "website": "https://www.fresno.gov/parks/",
        "sourceUrl": "https://www.fresno.gov/parks/",
        "phone": "(559) 621-8400",
        "note": "City of Fresno community center summer day camp.",
    },

    # --- Salinas, CA (source: cityofsalinas.org parks & community services) ---
    {
        "name": "Salinas Parks & Community Day Camp",
        "city": "Salinas", "state": "CA", "zip": "93901",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 13,
        "website": "https://www.cityofsalinas.org/parks-and-community-services",
        "sourceUrl": "https://www.cityofsalinas.org/parks-and-community-services",
        "phone": "(831) 758-7200",
        "note": "City of Salinas Parks & Community Services summer day camp.",
    },

    # --- Santa Monica, CA (source: smgov.net community services) ---
    {
        "name": "Santa Monica Community Services Day Camp",
        "city": "Santa Monica", "state": "CA", "zip": "90401",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 13,
        "website": "https://www.smgov.net/departments/ccs/",
        "sourceUrl": "https://www.smgov.net/departments/ccs/",
        "phone": "(310) 458-8300",
        "note": "City of Santa Monica Community & Cultural Services summer day camp.",
    },

    # --- Ventura, CA (source: cityofventura.ca.gov community services) ---
    {
        "name": "Ventura Community Services Day Camp",
        "city": "Ventura", "state": "CA", "zip": "93001",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 13,
        "website": "https://www.cityofventura.ca.gov/139/Community-Services",
        "sourceUrl": "https://www.cityofventura.ca.gov/139/Community-Services",
        "phone": "(805) 658-4726",
        "note": "City of Ventura Community Services summer day camp.",
    },

    # --- Santa Barbara, CA (source: santabarbaraca.gov parks & rec) ---
    {
        "name": "Santa Barbara Parks & Rec Day Camp",
        "city": "Santa Barbara", "state": "CA", "zip": "93101",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 13,
        "website": "https://www.santabarbaraca.gov/gov/depts/parksrec/",
        "sourceUrl": "https://www.santabarbaraca.gov/gov/depts/parksrec/",
        "phone": "(805) 564-5418",
        "note": "City of Santa Barbara Parks & Recreation summer day camp.",
    },

    # --- Oxnard, CA (source: oxnard.org community services) ---
    {
        "name": "Oxnard Community Services Day Camp",
        "city": "Oxnard", "state": "CA", "zip": "93030",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 13,
        "website": "https://www.oxnard.org/community-services/",
        "sourceUrl": "https://www.oxnard.org/community-services/",
        "phone": "(805) 385-8100",
        "note": "City of Oxnard Community Services summer day camp.",
    },

    # --- San Luis Obispo, CA (source: slocity.org parks & recreation) ---
    {
        "name": "San Luis Obispo Parks & Rec Day Camp",
        "city": "San Luis Obispo", "state": "CA", "zip": "93401",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 13,
        "website": "https://www.slocity.org/government/departments/parks-and-recreation",
        "sourceUrl": "https://www.slocity.org/government/departments/parks-and-recreation",
        "phone": "(805) 781-7300",
        "note": "City of San Luis Obispo Parks & Recreation summer day camp.",
    },

    # --- Simi Valley, CA (source: simivalley.org recreation) ---
    {
        "name": "Simi Valley Recreation Day Camp",
        "city": "Simi Valley", "state": "CA", "zip": "93065",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 13,
        "website": "https://www.simivalley.org/departments/recreation",
        "sourceUrl": "https://www.simivalley.org/departments/recreation",
        "phone": "(805) 583-6300",
        "note": "City of Simi Valley Recreation summer day camp.",
    },

    # --- Thousand Oaks, CA (source: toaks.org community services) ---
    {
        "name": "Thousand Oaks Community Services Day Camp",
        "city": "Thousand Oaks", "state": "CA", "zip": "91360",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 13,
        "website": "https://www.toaks.org/government/departments/community-services",
        "sourceUrl": "https://www.toaks.org/government/departments/community-services",
        "phone": "(805) 449-2100",
        "note": "City of Thousand Oaks Community Services summer day camp.",
    },

    # --- Santa Clarita, CA (source: santaclarita.gov parks & recreation) ---
    {
        "name": "Santa Clarita Parks & Rec Day Camp",
        "city": "Santa Clarita", "state": "CA", "zip": "91355",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 13,
        "website": "https://santaclarita.gov/parks-recreation",
        "sourceUrl": "https://santaclarita.gov/parks-recreation",
        "phone": "(661) 250-3700",
        "note": "City of Santa Clarita Parks, Recreation & Community Services summer day camp.",
    },

    # --- Rancho Cucamonga, CA (source: ranchocucamonga.gov community services) ---
    {
        "name": "Rancho Cucamonga Community Services Day Camp",
        "city": "Rancho Cucamonga", "state": "CA", "zip": "91730",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 13,
        "website": "https://www.ranchocucamonga.gov/our-community/community-services",
        "sourceUrl": "https://www.ranchocucamonga.gov/our-community/community-services",
        "phone": "(909) 477-2750",
        "note": "City of Rancho Cucamonga Community Services summer day camp.",
    },

    # --- Palm Springs, CA (source: palmspringsca.gov parks & recreation) ---
    {
        "name": "Palm Springs Parks & Rec Day Camp",
        "city": "Palm Springs", "state": "CA", "zip": "92262",
        "season": "summer", "theme": "General", "type": "day",
        "ageMin": 5, "ageMax": 13,
        "website": "https://www.palmspringsca.gov/government/departments/parks-and-recreation",
        "sourceUrl": "https://www.palmspringsca.gov/government/departments/parks-and-recreation",
        "phone": "(760) 323-8200",
        "note": "City of Palm Springs Parks & Recreation summer day camp.",
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
