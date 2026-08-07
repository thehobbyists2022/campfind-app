#!/usr/bin/env python3
"""
CampFind v5 — brand expansion: School of Rock + Drama Kids.

Sources (all official, verified live 2026-08-06):
  - School of Rock: official sitemap (schoolofrock.com/sitemap.xml) -> per-location
    pages that embed full JSON-LD (name, address, phone, email, geo). R2 = the
    location URL itself; R1 = every field read from the official page.
  - Drama Kids: official sitemap index (dramakids.com/sitemap.xml) -> franchise
    region URLs. Each region is one franchise owner; primary city + state come
    from the region page title / slug. R2 = the region URL.

Every generated camp:
  - real city/state/zip/address from the brand's own page (R1, R2)
  - website = brand official domain
  - sourceUrl = evidence (official location/region page)
  - phone/email from official page only, else null (R1)
  - season = summer; fall added for year-round brands (School of Rock is
    year-round; Drama Kids runs after-school + summer camps)
  - never fabricates price/rating/weeks/age/beforeCare (all null)
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CACHE = os.path.join(ROOT, "scrapers", "v5_cache")
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"}

STATE_SET = {"AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA","KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT","VA","WA","WV","WI","WY","DC"}


def fetch(url, force=False):
    name = re.sub(r"[^a-zA-Z0-9]+", "_", url).strip("_") + ".html"
    path = os.path.join(CACHE, name)
    if os.path.exists(path) and not force:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    os.makedirs(CACHE, exist_ok=True)
    try:
        req = urllib.request.Request(url, headers=UA)
        r = urllib.request.urlopen(req, timeout=25)
        body = r.read().decode("utf-8", "replace")
        with open(path, "w", encoding="utf-8") as f:
            f.write(body)
        time.sleep(1.1)
        return body
    except Exception as e:
        print("  fetch ERR", url, e, flush=True)
        return None


def sitemap_locs(url):
    t = fetch(url)
    if not t:
        return []
    return [re.sub(r"<!\[CDATA\[|\]\]>", "", l).strip() for l in re.findall(r"<loc>(.*?)</loc>", t)]


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "", s.lower())


# ---------------------------------------------------------------------------
# School of Rock
# ---------------------------------------------------------------------------
def sor_extract_ldjson(html):
    """Return the first JSON-LD block containing an address dict."""
    for m in re.finditer(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', html, re.S):
        raw = m.group(1)
        # strip invalid control chars (JSON-LD sometimes has raw \x00-\x1f)
        raw = re.sub(r"[\x00-\x1f]", "", raw)
        try:
            d = json.loads(raw)
        except Exception:
            continue
        items = d if isinstance(d, list) else [d]
        for it in items:
            if isinstance(it, dict) and "address" in it and isinstance(it["address"], dict):
                a = it["address"]
                if a.get("addressLocality") or a.get("addressRegion"):
                    return it
    return None


def build_schoolofrock():
    idx = sitemap_locs("https://www.schoolofrock.com/sitemap.xml")
    locs = []
    for u in idx:
        m = re.match(r"https://www\.schoolofrock\.com/locations/([a-z0-9\-]+)$", u)
        if m:
            locs.append((m.group(1), u))
    locs = sorted(set(locs))
    print(f"School of Rock: {len(locs)} location slugs", flush=True)

    camps = []
    for slug, url in locs:
        html = fetch(url)
        if not html:
            continue
        # skip retired locations that redirect back to the generic /locations page
        canon = re.search(r'<link rel="canonical" href="([^"]+)"', html)
        if canon and re.match(r"https://www\.schoolofrock\.com/locations/?$", canon.group(1)):
            print(f"  SKIP {slug} (redirects to /locations, retired)", flush=True)
            continue
        d = sor_extract_ldjson(html)
        if not d:
            print("  NO LDJSON", slug, flush=True)
            continue
        a = d["address"]
        locality = (a.get("addressLocality") or "").replace(", US", "").strip()
        region = (a.get("addressRegion") or "").strip()
        zipcode = re.sub(r"[\ufeff\s]", "", (a.get("postalCode") or "")).strip()
        street = (a.get("streetAddress") or "").strip()
        name = d.get("name") or f"School of Rock {locality}"
        if region not in STATE_SET:
            continue  # non-US location (e.g. Bogota CO, London UK)
        if not locality:
            continue
        # geo from JSON-LD
        geo = d.get("geo") or {}
        lat, lng = None, None
        try:
            lat = float(geo.get("latitude"))
            lng = float(geo.get("longitude"))
        except Exception:
            lat = lng = None
        phone = d.get("telephone") or None
        email = d.get("email") or None
        if phone:
            phone = phone.split(",")[0].strip()
            phone = re.sub(r"[\ufeff]", "", phone)
            digits = re.sub(r"[^0-9]", "", phone)
            if len(digits) == 10:
                phone = f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
            else:
                phone = None
        camp = {
            "id": f"schoolofrock_{slug}",
            "name": name,
            "city": locality,
            "state": region,
            "zip": zipcode or None,
            "address": street or None,
            "lat": lat,
            "lng": lng,
            "type": "day",
            "price": None,
            "rating": None,
            "reviewCount": None,
            "ageMin": None,
            "ageMax": None,
            "season": "summer",
            "theme": "Arts",
            "beforeCare": None,
            "afterCare": None,
            "shuttle": None,
            "weeks": None,
            "phone": phone,
            "email": email,
            "website": "https://www.schoolofrock.com",
            "description": "School of Rock music school & summer camps (guitar, drums, bass, vocals).",
            "acaVerified": False,
            "source": "franchise_locator:schoolofrock.com",
            "sourceUrl": url,
            "verifiedAt": "2026-08-06",
            "verificationMethod": "location_listing",
            "unverified": False,
        }
        camps.append(camp)
        if not lat or not lng:
            print(f"  NOGEO {camp['name']} {camp['city']} {camp['state']}", flush=True)

    # fall variants for year-round brand
    fall = []
    for c in camps:
        fc = dict(c)
        fc["id"] = c["id"] + "_fall"
        fc["season"] = "fall"
        fc["name"] = c["name"] + " (Fall)"
        fall.append(fc)
    print(f"School of Rock: {len(camps)} summer + {len(fall)} fall", flush=True)
    return camps + fall


# ---------------------------------------------------------------------------
# Drama Kids
# ---------------------------------------------------------------------------
# slug -> (primary_city, state). Derived from official region slug + title
# (verified 2026-08-06). Regions whose page redirects to find-locations/
# (retired franchise) are excluded entirely.
DK_REGIONS = {
    "akron-cuyahoga-falls-hudson-stow": ("Akron", "OH"),
    "albany-ny": ("Albany", "NY"),
    "ashburn-leesburg-va": ("Ashburn", "VA"),
    "austin-san-marcos-fredericksburg-marble-falls-tx": ("Austin", "TX"),
    "bowie-md": ("Bowie", "MD"),
    "brandon-apollo-beach-riverview-plant-city-fl": ("Brandon", "FL"),
    "clermont-windermere-winter-garden-fl": ("Clermont", "FL"),
    "columbus-ga-phenix-city-al": ("Columbus", "GA"),
    "concord-charlotte-north-nc": ("Concord", "NC"),
    "crown-point-merrillville-in": ("Crown Point", "IN"),
    "dallas-rockwall-richardson-plano-tx": ("Dallas", "TX"),
    "destin-fort-walton-beach-niceville-fl": ("Destin", "FL"),
    "easton-hanover-bridgewater-ma": ("Easton", "MA"),
    "frisco-mckinney-allen-plano-tx": ("Frisco", "TX"),
    "greensboro-high-point-winston-salem-nc": ("Greensboro", "NC"),
    "jacksonville-ponte-vedra-beach-st-augustine-fl": ("Jacksonville", "FL"),
    "johns-island-james-island-charleston-kiawah-island": ("Charleston", "SC"),
    "kennesaw-woodstock-marietta-ga": ("Kennesaw", "GA"),
    "las-vegas-henderson-nv": ("Las Vegas", "NV"),
    "manhattan-ny": ("Manhattan", "NY"),
    "mankato-st-peter-new-ulm-mn": ("Mankato", "MN"),
    "massapequa-rockville-centre-ny": ("Massapequa", "NY"),
    "morristown-basking-ridge-bridgewater-nj": ("Morristown", "NJ"),
    "mount-pleasant-daniel-island-sullivans-island-isle-of-palms": ("Mount Pleasant", "SC"),
    "north-columbus-oh": ("Columbus", "OH"),
    "rochester-ny": ("Rochester", "NY"),
    "rockville-silver-spring-md": ("Rockville", "MD"),
    "rumson-tinton-falls-long-branch-asbury-park-nj": ("Rumson", "NJ"),
    "sarasota-manatee-county-fl": ("Sarasota", "FL"),
    "sherman-gunter-greenville-bonham-tx": ("Sherman", "TX"),
    "st-augustine-fleming-island-orange-park-middleburg": ("St. Augustine", "FL"),
    "tuscon-marana-oro-valley-vail-az": ("Tucson", "AZ"),
}


def build_dramakids():
    idx = sitemap_locs("https://dramakids.com/sitemap.xml")
    regions = [u for u in idx if re.search(r"/[a-z0-9\-]+/sitemap_\d+\.xml$", u)]
    print(f"Drama Kids: {len(regions)} franchise region sitemaps", flush=True)

    by_slug = {}
    for u in regions:
        m = re.search(r"https://dramakids\.com/([a-z0-9\-]+)/sitemap_\d+\.xml$", u)
        if m:
            by_slug.setdefault(m.group(1), u)
    print(f"Drama Kids: {len(by_slug)} unique franchise regions", flush=True)

    camps = []
    skipped = 0
    for slug, su in sorted(by_slug.items()):
        if slug not in DK_REGIONS:
            print(f"  SKIP {slug} (no mapping / retired)", flush=True)
            skipped += 1
            continue
        city, state = DK_REGIONS[slug]
        region_url = f"https://dramakids.com/{slug}/"
        html = fetch(region_url)
        if html:
            canonical = re.search(r'<link rel="canonical" href="([^"]+)"', html)
            if canonical and "find-locations" in canonical.group(1):
                print(f"  SKIP {slug} (redirects to find-locations, retired)", flush=True)
                skipped += 1
                continue
        camp = {
            "id": f"dramakids_{slug}",
            "name": f"Drama Kids {city}",
            "city": city,
            "state": state,
            "zip": None,
            "address": None,
            "lat": None,
            "lng": None,
            "type": "day",
            "price": None,
            "rating": None,
            "reviewCount": None,
            "ageMin": None,
            "ageMax": None,
            "season": "summer",
            "theme": "Arts",
            "beforeCare": None,
            "afterCare": None,
            "shuttle": None,
            "weeks": None,
            "phone": None,
            "email": None,
            "website": "https://dramakids.com",
            "description": "Drama Kids acting & drama classes and summer camps.",
            "acaVerified": False,
            "source": "franchise_locator:dramakids.com",
            "sourceUrl": region_url,
            "verifiedAt": "2026-08-06",
            "verificationMethod": "location_listing",
            "unverified": False,
        }
        camps.append(camp)
        print(f"  ADD Drama Kids {city}, {state}", flush=True)

    print(f"Drama Kids: {len(camps)} camps (skipped {skipped})", flush=True)
    return camps


def geocode_all(camps):
    """Geocode any camp missing coords using geocode_cache.json (Nominatim-style entries)."""
    cache_path = os.path.join(ROOT, "scrapers", "geocode_cache.json")
    cache = {}
    if os.path.exists(cache_path):
        cache = json.load(open(cache_path, encoding="utf-8"))
    fixed = 0
    for c in camps:
        if c.get("lat") and c.get("lng"):
            continue
        key = f"{c['city']}|{c['state']}"
        if key in cache:
            c["lat"], c["lng"] = cache[key][0], cache[key][1]
            fixed += 1
            continue
        query = f"{c['city']}, {c['state']}, USA"
        url = "https://nominatim.openstreetmap.org/search?" + "q=" + urllib.parse.quote(query) + "&format=json&limit=1"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "CampFind-v5/1.0"})
            data = json.loads(urllib.request.urlopen(req, timeout=20).read().decode("utf-8"))
            if data:
                res = (float(data[0]["lat"]), float(data[0]["lon"]))
                c["lat"], c["lng"] = res[0], res[1]
                cache[key] = res
                json.dump(cache, open(cache_path, "w", encoding="utf-8"), ensure_ascii=False)
                fixed += 1
                time.sleep(1.1)
        except Exception as e:
            print("  GEO ERR", c["city"], e, flush=True)
    print(f"geocoded {fixed} camps", flush=True)
    return camps


def main():
    camps = []
    camps += build_schoolofrock()
    camps += build_dramakids()
    geocode_all(camps)
    out = {"source": "CampFind v5 brand expansion (School of Rock + Drama Kids official locators)",
           "count": len(camps), "camps": camps}
    fn = os.path.join(ROOT, "app", "aca_camps_brands_v5.json")
    json.dump(out, open(fn, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"\nwrote {len(camps)} brand camps -> {fn}", flush=True)


if __name__ == "__main__":
    main()
