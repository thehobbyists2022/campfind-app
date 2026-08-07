#!/usr/bin/env python3
"""
CampFind v6 — brand expansion: US Baseball Academy + Bach to Rock (+ VOSJ JCC).

Sources (all official, verified live 2026-08-06):
  - US Baseball Academy: official app API (app.usbaseballacademy.com/backend/api/v1/camps)
    -> every camp with city/address/zip + dates. R2 = the API record.
  - Bach to Rock: official sitemap -> per-school pages that embed JSON-LD
    (name, address, phone, zip, geo). R2 = the school URL itself.
  - Valley of the Sun JCC: official camp pages with JSON-LD (Shemesh already in
    dataset; Kochavim added).

Every generated camp:
  - real city/state/zip/address from the brand's own page/API (R1, R2)
  - website = brand official domain
  - sourceUrl = evidence (official location page or API record)
  - phone from official page only, else null (R1)
  - season = summer (both are summer-camp brands)
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
UA_JSON = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36", "Accept": "application/json"}

STATE_SET = {"AL","AK","AZ","AR","CA","CO","CT","DE","FL","GA","HI","ID","IL","IN","IA","KS","KY","LA","ME","MD","MA","MI","MN","MS","MO","MT","NE","NV","NH","NJ","NM","NY","NC","ND","OH","OK","OR","PA","RI","SC","SD","TN","TX","UT","VT","VA","WA","WV","WI","WY","DC"}


def fetch(url, headers=None, force=False):
    name = re.sub(r"[^a-zA-Z0-9]+", "_", url).strip("_") + ".html"
    path = os.path.join(CACHE, name)
    if os.path.exists(path) and not force:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    os.makedirs(CACHE, exist_ok=True)
    try:
        req = urllib.request.Request(url, headers=headers or UA)
        r = urllib.request.urlopen(req, timeout=25)
        body = r.read().decode("utf-8", "replace")
        with open(path, "w", encoding="utf-8") as f:
            f.write(body)
        time.sleep(1.1)
        return body
    except Exception as e:
        print("  fetch ERR", url, e, flush=True)
        return None


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "", s.lower())


# ---------------------------------------------------------------------------
# US Baseball Academy (official API)
# ---------------------------------------------------------------------------
def build_usbaseball():
    url = "https://app.usbaseballacademy.com/backend/api/v1/camps"
    t = fetch(url, headers=UA_JSON, force=True)
    if not t:
        print("US Baseball: API fetch failed", flush=True)
        return []
    try:
        data = json.loads(t)["data"]
    except Exception as e:
        print("US Baseball: API parse failed", e, flush=True)
        return []
    camps = []
    seen = set()
    for st, blk in data.items():
        for c in blk.get("camps", []):
            loc = c.get("location") or {}
            city = (loc.get("city") or c.get("city") or "").strip()
            zipcode = (loc.get("zipcode") or "").strip()
            address = (loc.get("address") or "").strip()
            if not city or st not in STATE_SET:
                continue
            key = (slugify(city), st)
            if key in seen:
                continue
            seen.add(key)
            name = re.sub(r"^SUMMER CAMP[^\w]*", "", c.get("site_name") or "").strip() or f"US Baseball Academy {city}"
            # clean emoji
            name = re.sub(r"[\U0001F300-\U0001FAFF]", "", name).strip()
            if len(zipcode) == 4:
                zipcode = "0" + zipcode
            # derive slug suffix for id uniqueness
            camps.append({
                "id": f"usbaseball_{slugify(city)}_{st.lower()}",
                "name": name,
                "city": city,
                "state": st,
                "zip": zipcode or None,
                "address": address or None,
                "lat": None,
                "lng": None,
                "type": "day",
                "price": None,
                "rating": None,
                "reviewCount": None,
                "ageMin": None,
                "ageMax": None,
                "season": "summer",
                "theme": "Sports",
                "beforeCare": None,
                "afterCare": None,
                "shuttle": None,
                "weeks": None,
                "phone": None,
                "email": None,
                "website": "https://usbaseballacademy.com",
                "description": "US Baseball Academy baseball camp.",
                "acaVerified": False,
                "source": "franchise_locator:usbaseballacademy.com",
                "sourceUrl": url,
                "verifiedAt": "2026-08-06",
                "verificationMethod": "location_listing",
                "unverified": False,
            })
    print(f"US Baseball: {len(camps)} camps", flush=True)
    return camps


# ---------------------------------------------------------------------------
# Bach to Rock (per-school JSON-LD)
# ---------------------------------------------------------------------------
BTR_EXCLUDE = {"about","adult-music-lessons","baby-toddler-music-classes","bachapalooza","band-camps",
        "bass-lessons","beginner-dj-lessons","beginner-drum-lessons","beginner-piano-lessons",
        "beginner-singing-lessons","beginner-ukulele-lessons","birthday-parties-for-kids","blog",
        "brass-lessons","battle-of-the-bands","contact","cookie-policy","corporate-parties",
        "dj-battle","dj-birthday-party","dj-camps","dj-lessons","dj-mixing-lessons","dj-scratching-lessons",
        "dj-showcase","dj-workshops","drum-lessons","events","glee-lessons","group-music-lessons",
        "guitar-lessons","in-person-music-lessons","join-a-band","locations","locations-browse",
        "music-camps-for-kids","music-education","music-education-for-kids","music-lessons",
        "music-parties","online-music-lessons","original-music","piano-lessons","preschool-music-classes",
        "private-music-lessons","record-a-demo-camp","rewards","singing-camps","songwriting-classes",
        "string-lessons","themed-workshops","ukulele-lessons","voice-lessons","woodwind-lessons",
        "youth-music-lessons","franchise-news","privacy-policy","terms-of-use","sign-up","wall-of-fame",
        "myb2r","testimonials","rent-a-studio","gift-certificates","news","press",
        "beginner-guitar-lessons","music-lessons-for-kids","music-production-camps",
        "music-production-classes","music-production-workshops","party-songlist",
        "piano-lessons-for-kids","reviews-testimonials","singing-lessons","songwriting-workshops","wait-list"}


def btr_ldjson(html):
    for m in re.finditer(r'<script[^>]*application/ld\+json[^>]*>(.*?)</script>', html, re.S):
        raw = re.sub(r"[\x00-\x1f]", "", m.group(1))
        try:
            d = json.loads(raw)
        except Exception:
            continue
        if isinstance(d, dict) and d.get("@type") == "LocalBusiness" and isinstance(d.get("address"), dict):
            return d
    return None


def build_bachtorock():
    # gather school slugs from official sitemap
    slugs = set()
    for i in range(1, 5):
        t = fetch(f"https://www.bachtorock.com/page-sitemap{i}.xml")
        if not t:
            continue
        for l in re.findall(r"<loc>(.*?)</loc>", t):
            m = re.match(r"https://www\.bachtorock\.com/([a-z0-9\-]+)/?$", l)
            if m:
                slug = m.group(1)
                if slug in BTR_EXCLUDE or len(slug) < 3:
                    continue
                slugs.add(slug)
    print(f"Bach to Rock: {len(slugs)} candidate school slugs", flush=True)

    camps = []
    for slug in sorted(slugs):
        url = f"https://www.bachtorock.com/{slug}/"
        html = fetch(url)
        if not html:
            continue
        d = btr_ldjson(html)
        if not d:
            print("  NO LDJSON", slug, flush=True)
            continue
        a = d["address"]
        region = (a.get("addressRegion") or "").strip()
        locality = (a.get("addressLocality") or "").strip()
        zipcode = re.sub(r"[\ufeff\s]", "", (a.get("postalCode") or "")).strip()
        street = (a.get("streetAddress") or "").strip()
        name = d.get("name") or f"Bach to Rock {locality}"
        if region not in STATE_SET or not locality:
            continue
        phone = d.get("telephone") or None
        if phone:
            digits = re.sub(r"[^0-9]", "", phone)
            if len(digits) == 10:
                phone = f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
            else:
                phone = None
        camps.append({
            "id": f"bachtorock_{slug}",
            "name": name,
            "city": locality,
            "state": region,
            "zip": zipcode or None,
            "address": street or None,
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
            "phone": phone,
            "email": None,
            "website": "https://www.bachtorock.com",
            "description": "Bach to Rock music school & camps (guitar, drums, piano, vocals).",
            "acaVerified": False,
            "source": "franchise_locator:bachtorock.com",
            "sourceUrl": url,
            "verifiedAt": "2026-08-06",
            "verificationMethod": "location_listing",
            "unverified": False,
        })
    print(f"Bach to Rock: {len(camps)} schools", flush=True)
    return camps


# ---------------------------------------------------------------------------
# Valley of the Sun JCC (specific camp pages with JSON-LD)
# ---------------------------------------------------------------------------
def build_vosj():
    entries = [
        ("Camp Kochavim", "https://valleyofthesunj.org/kids-family/camps/kochavim/"),
    ]
    camps = []
    for cname, url in entries:
        html = fetch(url)
        if not html:
            continue
        d = btr_ldjson(html)  # LocalBusiness JSON-LD reused
        if not d:
            continue
        a = d["address"]
        region = (a.get("addressRegion") or "").strip()
        if region == "Arizona":
            region = "AZ"
        locality = (a.get("addressLocality") or "").strip()
        zipcode = re.sub(r"[\ufeff\s]", "", (a.get("postalCode") or "")).strip()
        street = (a.get("streetAddress") or "").strip()
        if region not in STATE_SET:
            continue
        phone = d.get("telephone") or None
        if phone:
            digits = re.sub(r"[^0-9]", "", phone)
            if len(digits) == 10:
                phone = f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
            else:
                phone = None
        camps.append({
            "id": f"vosj_{slugify(cname)}",
            "name": cname,
            "city": locality,
            "state": region,
            "zip": zipcode or None,
            "address": street or None,
            "lat": None,
            "lng": None,
            "type": "day",
            "price": None,
            "rating": None,
            "reviewCount": None,
            "ageMin": None,
            "ageMax": None,
            "season": "summer",
            "theme": "General",
            "beforeCare": None,
            "afterCare": None,
            "shuttle": None,
            "weeks": None,
            "phone": phone,
            "email": None,
            "website": "https://valleyofthesunj.org",
            "description": f"{cname} at Valley of the Sun J.",
            "acaVerified": False,
            "source": "profile_page:valleyofthesunj.org",
            "sourceUrl": url,
            "verifiedAt": "2026-08-06",
            "verificationMethod": "profile_page",
            "unverified": False,
        })
    print(f"Valley of the Sun JCC: {len(camps)} camps", flush=True)
    return camps


# ---------------------------------------------------------------------------
# Geocode missing coords
# ---------------------------------------------------------------------------
def geocode_all(camps):
    cache_path = os.path.join(ROOT, "scrapers", "geocode_cache.json")
    cache = {}
    if os.path.exists(cache_path):
        cache = json.load(open(cache_path, encoding="utf-8"))
    fixed = 0
    for c in camps:
        if c.get("lat") and c.get("lng"):
            continue
        key = f"{c['city']}|{c['state']}|{c['zip'] or ''}"
        ck = f"{c['city']}|{c['state']}"
        if ck in cache:
            c["lat"], c["lng"] = cache[ck][0], cache[ck][1]
            fixed += 1
            continue
        query = f"{c['city']}, {c['state']}, USA"
        query = query.replace("-", " ")
        # compound city labels like "Mishawaka-Osceola" -> use first real city
        if query.count(",") > 1:
            first = query.split(",")[0]
            parts = first.split(" ")
            # keep just the first city token for geocode
            query = f"{parts[0]}, {c['state']}, USA"
        url = "https://nominatim.openstreetmap.org/search?" + "q=" + urllib.parse.quote(query) + "&format=json&limit=1"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "CampFind-v6/1.0"})
            data = json.loads(urllib.request.urlopen(req, timeout=20).read().decode("utf-8"))
            if data:
                res = (float(data[0]["lat"]), float(data[0]["lon"]))
                c["lat"], c["lng"] = res[0], res[1]
                cache[ck] = res
                json.dump(cache, open(cache_path, "w", encoding="utf-8"), ensure_ascii=False)
                fixed += 1
                time.sleep(1.1)
        except Exception as e:
            print("  GEO ERR", c["city"], e, flush=True)
    print(f"geocoded {fixed} camps", flush=True)
    return camps


def main():
    camps = []
    camps += build_usbaseball()
    camps += build_bachtorock()
    camps += build_vosj()
    geocode_all(camps)
    out = {"source": "CampFind v6 brand expansion (US Baseball Academy + Bach to Rock + VOSJ JCC official sources)",
           "count": len(camps), "camps": camps}
    fn = os.path.join(ROOT, "app", "aca_camps_brands_v6.json")
    json.dump(out, open(fn, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"\nwrote {len(camps)} brand camps -> {fn}", flush=True)


if __name__ == "__main__":
    main()
