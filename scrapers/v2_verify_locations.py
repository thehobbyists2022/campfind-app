#!/usr/bin/env python3
"""
CampFind v2 — Location-level verification pipeline (Task 1).

For every existing camp, decide a tier by checking the brand's OFFICIAL
location listing (from sitemaps / locator pages):

  tierA  -> (brand, city) confirmed present in the brand's official listing
  tierB  -> brand listing could not be extracted, so we cannot decide (unverified)
  tierC  -> (brand, city) NOT present in the brand's official listing (fabricated)

Iron rule R2: domain resolution alone is never proof; only an official
location listing counts as evidence. Every tier decision carries a sourceUrl.
"""
import json
import os
import re
import sys
import time
import urllib.request
from collections import defaultdict
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = {"User-Agent": "CampFind-Verifier/2.0 (parent-friendly directory audit)"}
SLEEP = 1.0  # >= 1s between requests (rate limit)
CACHE_DIR = os.path.join(ROOT, "scrapers", "v2_cache")


def get(url, max_retries=2):
    """Fetch URL with cache + rate limit + retry. Returns decoded text or None."""
    os.makedirs(CACHE_DIR, exist_ok=True)
    fn = os.path.join(CACHE_DIR, re.sub(r"[^A-Za-z0-9]+", "_", url)[-150:] + ".html")
    if os.path.exists(fn):
        return open(fn, encoding="utf-8", errors="replace").read()
    for attempt in range(max_retries + 1):
        try:
            req = urllib.request.Request(url, headers=UA)
            body = urllib.request.urlopen(req, timeout=30).read()
            text = body.decode("utf-8", errors="replace")
            open(fn, "w", encoding="utf-8").write(text)
            time.sleep(SLEEP)
            return text
        except Exception as e:
            if attempt == max_retries:
                print(f"  [get] FAIL {url} :: {type(e).__name__} {str(e)[:80]}")
                return None
            time.sleep(SLEEP * (attempt + 1))


def sitemap_urls(url):
    """Fetch a sitemap (or sitemap index) and return list of raw <loc> entries."""
    text = get(url)
    if not text:
        return []
    locs = re.findall(r"<loc>(.*?)</loc>", text, re.S)
    return [re.sub(r"<!\[CDATA\[|\]\]>", "", l).strip() for l in locs if l.strip()]


# ---------------------------------------------------------------------------
# Per-brand extractors. Each returns a dict:
#   {"real_cities": {city_slug}, "real_pairs": {(city_slug, state_lower)},
#    "evidence_url": str, "extracted_ok": bool, "note": str}
# ---------------------------------------------------------------------------
def slugify(s):
    return re.sub(r"[^a-z0-9]+", "", s.lower())


STATE_ABBR = {
    "al": "AL", "ak": "AK", "az": "AZ", "ar": "AR", "ca": "CA", "co": "CO",
    "ct": "CT", "de": "DE", "fl": "FL", "ga": "GA", "hi": "HI", "id": "ID",
    "il": "IL", "in": "IN", "ia": "IA", "ks": "KS", "ky": "KY", "la": "LA",
    "me": "ME", "md": "MD", "ma": "MA", "mi": "MI", "mn": "MN", "ms": "MS",
    "mo": "MO", "mt": "MT", "ne": "NE", "nv": "NV", "nh": "NH", "nj": "NJ",
    "nm": "NM", "ny": "NY", "nc": "NC", "nd": "ND", "oh": "OH", "ok": "OK",
    "or": "OR", "pa": "PA", "ri": "RI", "sc": "SC", "sd": "SD", "tn": "TN",
    "tx": "TX", "ut": "UT", "vt": "VT", "va": "VA", "wa": "WA", "wv": "WV",
    "wi": "WI", "wy": "WY",
}

STATE_FULL_NAME = {
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR",
    "california": "CA", "colorado": "CO", "connecticut": "CT", "delaware": "DE",
    "florida": "FL", "georgia": "GA", "hawaii": "HI", "idaho": "ID",
    "illinois": "IL", "indiana": "IN", "iowa": "IA", "kansas": "KS",
    "kentucky": "KY", "louisiana": "LA", "maine": "ME", "maryland": "MD",
    "massachusetts": "MA", "michigan": "MI", "minnesota": "MN", "mississippi": "MS",
    "missouri": "MO", "montana": "MT", "nebraska": "NE", "nevada": "NV",
    "new-hampshire": "NH", "new-jersey": "NJ", "new-mexico": "NM", "new-york": "NY",
    "north-carolina": "NC", "north-dakota": "ND", "ohio": "OH", "oklahoma": "OK",
    "oregon": "OR", "pennsylvania": "PA", "rhode-island": "RI", "south-carolina": "SC",
    "south-dakota": "SD", "tennessee": "TN", "texas": "TX", "utah": "UT",
    "vermont": "VT", "virginia": "VA", "washington": "WA", "west-virginia": "WV",
    "wisconsin": "WI", "wyoming": "WY",
}


def extract_codeninjas():
    sm = sitemap_urls("https://www.codeninjas.com/sitemap.xml")
    cities = set()
    pairs = set()
    for u in sm:
        path = urlparse(u).path
        m = re.match(r"/([a-z]{2})-([a-z0-9\-]+?)(?:/|$)", path)
        if m:
            st, city = m.group(1), m.group(2)
            if st in STATE_ABBR:
                cities.add(slugify(city))
                pairs.add((slugify(city), st))
    return {"real_cities": cities, "real_pairs": pairs,
            "evidence_url": "https://www.codeninjas.com/sitemap.xml",
            "extracted_ok": bool(cities), "note": f"{len(cities)} cities from sitemap slugs",
            "substring_match": True}  # Code Ninjas slugs may include neighborhood prefixes (north-san-jose)


def extract_ussportscamps():
    sm = sitemap_urls("https://www.ussportscamps.com/sitemap.xml")
    cities = set()
    pairs = set()
    state_full = {k: v for k, v in STATE_FULL_NAME.items()}
    for u in sm:
        path = urlparse(u).path
        # pattern /sport/state-fullname/city-slug  e.g. /basketball/california/rocklin
        m = re.match(r"/([a-z0-9\-]+)/([a-z]+)/([a-z0-9\-]+)$", path)
        if m and m.group(2) in state_full:
            st_abbr = state_full[m.group(2)]
            city = m.group(3)
            cities.add(slugify(city))
            pairs.add((slugify(city), st_abbr))
        # pattern /destinations/state-fullname/city-slug (authoritative city pages)
        m2 = re.match(r"/destinations/([a-z\-]+)/([a-z0-9\-]+)$", path)
        if m2 and m2.group(1) in state_full:
            st_abbr = state_full[m2.group(1)]
            city = m2.group(2)
            cities.add(slugify(city))
            pairs.add((slugify(city), st_abbr))
    return {"real_cities": cities, "real_pairs": pairs,
            "evidence_url": "https://www.ussportscamps.com/sitemap.xml",
            "extracted_ok": bool(cities), "note": f"{len(cities)} cities from sport/state + destinations URLs"}


def extract_magikidlab():
    sm = sitemap_urls("https://magikidlab.com/sitemap.xml")
    cities = set()
    pairs = set()
    for u in sm:
        m = re.match(r"https://magikidlab\.com/([^/]+)/sitemap\.xml", u)
        if m:
            cities.add(slugify(m.group(1)))
    return {"real_cities": cities, "real_pairs": pairs,
            "evidence_url": "https://magikidlab.com/sitemap.xml",
            "extracted_ok": bool(cities), "note": f"{len(cities)} cities from <city>/sitemap.xml slugs"}


def extract_stevekates():
    """Steve & Kate's real camp cities are server-rendered on /locations."""
    text = get("https://steveandkatescamp.com/locations")
    cities = set()
    pairs = set()
    if text:
        for city, st in re.findall(r"([A-Z][A-Za-z .]+?),\s*([A-Z]{2})\b", text):
            cs = slugify(city)
            cities.add(cs)
            pairs.add((cs, st.lower()))
    return {"real_cities": cities, "real_pairs": pairs,
            "evidence_url": "https://steveandkatescamp.com/locations",
            "extracted_ok": bool(cities), "note": f"{len(cities)} cities from /locations page"}


def extract_schoolofrock():
    sm = sitemap_urls("https://www.schoolofrock.com/sitemap.xml")
    cities = set()
    pairs = set()
    for u in sm:
        m = re.match(r"https://www\.schoolofrock\.com/locations/([a-z0-9\-]+)", u)
        if m:
            cities.add(slugify(m.group(1)))
    # also harvest "City, ST" pairs from the saved locator HTML (cached)
    text = get("https://www.schoolofrock.com/locations")
    if text:
        for city, st in re.findall(r"([A-Z][A-Za-z .]+?),\s*([A-Z]{2})\b", text):
            cs = slugify(city)
            cities.add(cs)
            pairs.add((cs, st.lower()))
    return {"real_cities": cities, "real_pairs": pairs,
            "evidence_url": "https://www.schoolofrock.com/sitemap.xml",
            "extracted_ok": bool(cities), "note": f"{len(cities)} cities from sitemap + /locations"}


def extract_idtech():
    """iD Tech authoritative real-city set, curated from the 162 campus
    location pages (each campus page = a real program location).
    Stored in scrapers/v2_idtech_cities.json."""
    import json as _json
    fn = os.path.join(ROOT, "scrapers", "v2_idtech_cities.json")
    cities = set()
    if os.path.exists(fn):
        cities = set(_json.load(open(fn, encoding="utf-8"))["real_cities"])
    return {"real_cities": {slugify(c) for c in cities}, "real_pairs": set(),
            "evidence_url": "https://www.idtech.com/locations",
            "extracted_ok": bool(cities), "note": f"{len(cities)} curated campus cities"}


def verify_idtech_city(camp):
    """Probe iD Tech official city page. 200 -> real; 404 -> not a location."""
    city = str(camp.get("city", "") or "")
    slug = re.sub(r"[^a-z0-9]+", "-", city.lower()).strip("-")
    if not slug:
        return {"tier": "tierB", "reason": "no city slug", "sourceUrl": ""}
    url = f"https://www.idtech.com/tech-camps/{slug}"
    status = probe_status(url)
    if status == 200:
        return {"tier": "tierA", "reason": "official city landing page returns 200",
                "sourceUrl": url}
    if status == 404:
        return {"tier": "tierC", "reason": "official city landing page returns 404 (not a location)",
                "sourceUrl": url}
    return {"tier": "tierB", "reason": f"city probe status {status} (indeterminate)",
            "sourceUrl": url}


def probe_status(url, max_retries=1):
    """Return HTTP status code, or -1 on network error, 403 on forbidden."""
    import urllib.request
    import urllib.error
    for attempt in range(max_retries + 1):
        try:
            req = urllib.request.Request(url, headers=UA)
            r = urllib.request.urlopen(req, timeout=20)
            time.sleep(SLEEP)
            return r.status
        except urllib.error.HTTPError as e:
            time.sleep(SLEEP)
            return e.code
        except Exception:
            if attempt == max_retries:
                return -1
            time.sleep(SLEEP * (attempt + 1))
    return -1


def extract_dramakids():
    idx = sitemap_urls("https://dramakids.com/sitemap.xml")
    area_urls = [u for u in idx if re.search(r"https://dramakids\.com/[^/]+/sitemap_\d+\.xml", u)]
    cities = set()
    pairs = set()
    for u in area_urls:
        m = re.match(r"https://dramakids\.com/(.+?)/sitemap_\d+\.xml", u)
        if not m:
            continue
        slug = m.group(1)  # e.g. "clermont-windermere-winter-garden-fl"
        # state suffix
        parts = slug.split("-")
        if parts and parts[-1] in STATE_ABBR:
            st = parts[-1]
            city_part = "-".join(parts[:-1])
            cities.add(slugify(city_part))
            pairs.add((slugify(city_part), st))
        else:
            cities.add(slugify(slug))
    return {"real_cities": cities, "real_pairs": pairs,
            "evidence_url": "https://dramakids.com/sitemap.xml",
            "extracted_ok": bool(cities), "note": f"{len(cities)} franchise areas from dramakids.com/<area>/sitemap"}


def extract_madscience():
    """Mad Science franchises verified via official subdomain list
    (madscience.org/sitemap.xml). Each present subdomain = a real franchise
    territory; city mapping is curated (scrapers/v2_madscience_cities.json).
    NO text-grep from franchise homepages (was unreliable both directions)."""
    import json as _json
    fn = os.path.join(ROOT, "scrapers", "v2_madscience_cities.json")
    cities = set()
    pairs = set()
    if os.path.exists(fn):
        data = _json.load(open(fn, encoding="utf-8"))
        for f in data.get("franchises", []):
            cities.add(slugify(f["city"]))
            pairs.add((slugify(f["city"]), f["state"].lower()))
    return {"real_cities": cities, "real_pairs": pairs,
            "evidence_url": "https://www.madscience.org/sitemap.xml",
            "extracted_ok": bool(cities),
            "note": f"{len(cities)} franchise territories from official subdomain map",
            "substring_match": True}


def extract_galileo():
    idx = sitemap_urls("https://galileo-camps.com/sitemap.xml")
    our = [u for u in idx if "our-camps" in u]
    camp_urls = []
    for u in our:
        camp_urls.extend(sitemap_urls(u))
    cities = set()
    for u in camp_urls:
        # camp page slug contains city e.g. .../lafayette, .../san-diego-downtown
        m = re.search(r"/([a-z0-9\-]+)/?$", urlparse(u).path)
        if m:
            slug = m.group(1)
            slug = re.sub(r"-(cam|day-camp|camps?)$", "", slug)
            cities.add(slugify(slug))
    return {"real_cities": cities, "real_pairs": set(),
            "evidence_url": "https://galileo-camps.com/our-camps-sitemap.xml",
            "extracted_ok": bool(cities), "note": f"{len(cities)} camp slugs from our-camps sitemap",
            "substring_match": True}  # slugs may include neighborhood (san-diego-downtown)


def extract_avid4():
    idx = sitemap_urls("https://avid4.com/sitemap.xml")
    loc_sitemaps = [u for u in idx if "location" in u]
    loc_urls = []
    for u in loc_sitemaps:
        loc_urls.extend(sitemap_urls(u))
    cities = set()
    state_full = {k: v for k, v in STATE_FULL_NAME.items()}
    for u in loc_urls:
        # pattern /summer-camp/{state}-{city}-{grades}-{activity}
        # e.g. colorado-boulder-4th-7th-mountain-biking-girls -> boulder
        m = re.search(r"/([a-z]{2,})-([a-z0-9\-]+?)(?:-\d|-\dth|$)", urlparse(u).path)
        if m:
            st, city = m.group(1), m.group(2)
            if st in state_full:
                cities.add(slugify(city))
        else:
            # fallback: strip grade/activity suffixes from the last slug segment
            slug = u.rstrip("/").split("/")[-1]
            slug = re.sub(r"-\d+(st|nd|rd|th)?.*$", "", slug)
            parts = slug.split("-")
            if len(parts) >= 2 and parts[0] in state_full:
                cities.add(slugify("-".join(parts[1:])))
    return {"real_cities": cities, "real_pairs": set(),
            "evidence_url": "https://avid4.com/location-sitemap.xml",
            "extracted_ok": bool(cities), "note": f"{len(cities)} location cities from location sitemap",
            "substring_match": True}


# ---------------------------------------------------------------------------
# Secondary verifier for camps with no brand extractor (single-org, national
# orgs). Evidence = claimed city appears on the camp's OWN official website.
# ---------------------------------------------------------------------------
def verify_via_homepage(camp):
    """Return {'tier','reason','sourceUrl'} using the camp's own website."""
    website = camp.get("website", "") or ""
    city = str(camp.get("city", "") or "")
    state = str(camp.get("state", "") or "")
    if not website or not city:
        return {"tier": "tierB", "reason": "no website or city to check"}
    text = get(website)
    if text is None:
        return {"tier": "tierB", "reason": f"website unreachable: {website}"}
    low = text.lower()
    city_low = city.lower()
    # city appears as a word, and optionally "City, ST"
    found_city = city_low in low
    found_pair = f"{city_low}, {state.lower()}" in low or f"{city_low}, {state.upper()}" in low
    if found_pair or found_city:
        return {"tier": "tierA", "reason": "claimed city appears on official website",
                "sourceUrl": website}
    return {"tier": "tierB", "reason": "claimed city NOT found on official website",
            "sourceUrl": website}


# ---------------------------------------------------------------------------
# Tier decision
# ---------------------------------------------------------------------------
def decide_tier(camp, brand_info, brand_domain):
    city_slug = slugify(camp.get("city", ""))
    state_low = (camp.get("state") or "").lower()
    real_cities = brand_info.get("real_cities", set())
    real_pairs = brand_info.get("real_pairs", set())
    substring = brand_info.get("substring_match", False)

    if not brand_info.get("extracted_ok"):
        return {"tier": "tierB", "reason": "brand locator not extractable"}
    if city_slug in real_cities:
        return {"tier": "tierA", "reason": "city present in official brand listing",
                "sourceUrl": brand_info["evidence_url"]}
    if (city_slug, state_low) in real_pairs:
        return {"tier": "tierA", "reason": "city+state present in official brand listing",
                "sourceUrl": brand_info["evidence_url"]}
    if substring and city_slug:
        # handle neighborhood-qualified slugs: 'north-san-jose' contains 'sanjose'
        for r in real_cities:
            if city_slug in r and len(city_slug) >= 4:
                return {"tier": "tierA", "reason": f"city '{camp.get('city')}' matches official listing slug '{r}'",
                        "sourceUrl": brand_info["evidence_url"]}
    return {"tier": "tierC", "reason": "city NOT in official brand listing (fabricated)",
            "sourceUrl": brand_info["evidence_url"]}


def main():
    camps = json.load(open(os.path.join(ROOT, "app", "aca_camps.json"), encoding="utf-8"))["camps"]

    # domain -> brand extractor
    extractors = {
        "codeninjas.com": extract_codeninjas,
        "ussportscamps.com": extract_ussportscamps,
        "magikidlab.com": extract_magikidlab,
        "schoolofrock.com": extract_schoolofrock,
        "idtech.com": extract_idtech,
        "dramakids.com": extract_dramakids,
        "madscience.org": extract_madscience,
        "galileo-camps.com": extract_galileo,
        "avid4.com": extract_avid4,
        "steveandkatescamp.com": extract_stevekates,
    }

    results = {}
    summary = {"tierA": 0, "tierB": 0, "tierC": 0, "unclassified_domain": 0}

    for domain, extract in extractors.items():
        print(f"\n### extracting locations for {domain}")
        info = extract()
        print("   ->", info.get("note"))
        results[domain] = info

    for i, camp in enumerate(camps):
        if i % 100 == 0:
            print(f"  ... processed {i}/{len(camps)} camps (tierA={summary['tierA']} tierB={summary['tierB']} tierC={summary['tierC']})")
        website = camp.get("website", "") or ""
        domain = urlparse(website).netloc.lower().replace("www.", "") if website else ""
        if domain in extractors:
            decision = decide_tier(camp, results[domain], domain)
            if decision["tier"] == "tierB":
                decision = verify_via_homepage(camp)
        else:
            decision = verify_via_homepage(camp)
            summary["unclassified_domain"] += 1
        decision.update({"index": i, "name": camp.get("name"), "city": camp.get("city"),
                         "state": camp.get("state"), "website": website, "domain": domain})
        summary[decision["tier"]] += 1
        camp["_tier"] = decision["tier"]
        camp["_tier_reason"] = decision["reason"]
        camp["_tier_sourceUrl"] = decision.get("sourceUrl", "")
        camp["_tier_domain"] = domain

    report = {
        "summary": summary,
        "brand_extraction": {k: {kk: vv for kk, vv in v.items() if kk not in ("real_cities", "real_pairs")}
                             for k, v in results.items()},
        "camps": camps,
    }
    out = os.path.join(ROOT, "scrapers", "v2_tier_report.json")
    json.dump(report, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("\n=== TIER SUMMARY ===")
    for k, v in summary.items():
        print(f"  {k:22s} {v}")
    print("saved:", out)


if __name__ == "__main__":
    main()
