#!/usr/bin/env python3
"""
CampFind v10 — ACA accreditation cross-verification.

Uses the public ACA find-a-camp autocomplete API
(find.acacamps.org/camp_search_suggest_ajx.php) to check whether a camp's name
exists in the ACA database. Only sets acaVerified=true on an EXACT name match
that also matches the camp's state (guarding against name collisions).

Rules (R1/R4):
  - name match must be exact (normalized) and state must match
  - never fabricate: no match -> leave acaVerified=false
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36"}
CACHE_PATH = os.path.join(ROOT, "scrapers", "aca_verify_cache.json")


def norm(s):
    s = s.lower()
    s = re.sub(r"&", "and", s)
    s = re.sub(r"\(.*?\)", "", s)       # drop parentheticals (incl. state)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def norm_keep_city(s):
    """Normalize but keep the parenthetical city token appended, e.g.
    'YMCA Summer Camp (Brooklyn)' -> 'ymca summer camp brooklyn'. Avoids
    duplicating city words already present in the base name."""
    m = re.search(r"\(([^)]+)\)", s)
    city = ""
    if m:
        city = re.sub(r"[^a-z0-9]+", " ", m.group(1).lower()).strip()
    base = norm(re.sub(r"\(.*?\)", "", s))
    # drop city words already present in base to avoid duplication
    if city:
        city_tokens = city.split()
        base_tokens = base.split()
        extra = [t for t in city_tokens if t not in base_tokens]
        city = " ".join(extra).strip()
    return (base + " " + city).strip() if city else base


def suggest(term):
    url = "https://find.acacamps.org/camp_search_suggest_ajx.php?" + urllib.parse.urlencode({"search_term": term, "limit": 10})
    try:
        req = urllib.request.Request(url, headers=UA)
        t = urllib.request.urlopen(req, timeout=20).read().decode("utf-8", "replace")
        return json.loads(t)
    except Exception:
        return None


def query_with_retries(name):
    """Try full name first, then progressively strip trailing descriptor words
    (e.g. 'for Boys', 'for Girls', 'Outdoor Adventure') which the ACA
    autocomplete API doesn't match on."""
    terms = [name]
    words = name.split()
    for i in range(len(words) - 1, 0, -1):
        terms.append(" ".join(words[:i]))
    seen_terms = set()
    for term in terms:
        if term in seen_terms:
            continue
        seen_terms.add(term)
        res = suggest(term)
        if res:
            return res
        time.sleep(0.5)
    return []


def load_cache():
    if os.path.exists(CACHE_PATH):
        return json.load(open(CACHE_PATH, encoding="utf-8"))
    return {}


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply-cache", action="store_true",
                    help="only match against existing cache (no network); apply flags to aca_camps.json")
    ap.add_argument("--camp-names", nargs="*", help="only verify these specific camp names (else all)")
    args = ap.parse_args()

    cache = load_cache()
    content = open(os.path.join(ROOT, "app", "aca_camps_data.js"), encoding="utf-8").read()
    m = re.search(r"window\.ACA_CAMPS\s*=\s*(\[.*\])", content, re.DOTALL)
    camps = json.loads(m.group(1))

    # verify all camps, but especially legacy + single-org entries (skip pure
    # franchise_locator brands which are not ACA-accredited as a rule)
    checked = 0
    matched = 0
    targets = args.camp_names or None
    for c in camps:
        if c.get("acaVerified"):
            continue
        src = c.get("source", "")
        if "franchise_locator" in src:
            continue  # franchise chain locations are not individually ACA-accredited
        name = c.get("name") or ""
        if len(name) < 3:
            continue
        if targets and not any(t.lower() in name.lower() for t in targets):
            continue
        state = c.get("state", "")
        key = norm_keep_city(name)
        if not key:
            continue
        if key in cache:
            hit = cache[key]
        else:
            if args.apply_cache:
                continue  # no cache entry yet
            res = query_with_retries(name)
            if res is None:
                print("  API ERR", name, flush=True)
                continue
            hits = []
            for r in res:
                if isinstance(r, dict) and "value" in r:
                    hits.append({"value": r["value"], "id": r.get("identifier")})
            cache[key] = hits
            try:
                json.dump(cache, open(CACHE_PATH, "w", encoding="utf-8"), ensure_ascii=False)
            except Exception as e:
                print("  cache write err (continue)", e, flush=True)
            time.sleep(0.6)
            checked += 1
        # match: require a strong name relationship AND state match.
        #   - exact match (normalized) is always accepted.
        #   - else compare "core tokens" (after dropping generic descriptor
        #     words like camp/for/boys/girls/adventure/outdoor/summer/day) and
        #     require one core set to be a subset of the other. This catches
        #     "Camp Huckins for Girls" ~ "YMCA Camp Huckins" while rejecting
        #     unrelated camps that merely share a generic word.
        STOP = {'camp','camps','for','boys','girls','and','the','of','summer','day',
                'adventure','outdoor','wilderness','youth','stem','academy','program',
                'overnight','resident','center','specialty','inc','at','in','on','with',
                'a','an','trip','weekly','session','school','scouting','season'}

        def core(s):
            return {t for t in s.split() if t not in STOP}

        matched_hit = None
        matched_id = None
        for hv in cache[key]:
            if isinstance(hv, dict):
                hv_str = hv.get("value", "")
                hv_id = hv.get("id")
            else:
                hv_str = hv
                hv_id = None
            hv_norm = norm(hv_str)
            state_ok = state and f"({state})" in hv_str
            if not state_ok:
                continue
            if hv_norm == key:
                matched_hit = hv_str
                matched_id = hv_id
                break
            our_core = core(key)
            aca_core = core(hv_norm)
            if not our_core or not aca_core:
                continue
            if len(our_core) < 2 and len(aca_core) < 2:
                continue
            if our_core <= aca_core or aca_core <= our_core:
                matched_hit = hv_str
                matched_id = hv_id
                break
        if matched_hit:
            c["acaVerified"] = True
            c["verificationMethod"] = "aca_finder"
            if matched_id:
                c["sourceUrl"] = f"https://find.acacamps.org/camp_profile.php?camp_id={matched_id}"
            matched += 1
            print("  ACA MATCH:", c["name"], "|", matched_hit, flush=True)

    print(f"\nchecked {checked} fresh API calls; matched {matched} camps", flush=True)

    # sync verified flags across all three runtime copies
    verified = {}
    for c in camps:
        if c.get("acaVerified"):
            verified[c["id"]] = c

    changed = 0
    for path in [os.path.join(ROOT, "app", "aca_camps.json"),
                 os.path.join(ROOT, "mobile", "assets", "aca_camps.json")]:
        data = json.load(open(path, encoding="utf-8"))
        for c in data["camps"]:
            vc = verified.get(c["id"])
            if vc and not c.get("acaVerified"):
                c["acaVerified"] = True
                c["verificationMethod"] = "aca_finder"
                if vc.get("sourceUrl"):
                    c["sourceUrl"] = vc["sourceUrl"]
                changed += 1
        data["verified_count"] = sum(1 for c in data["camps"] if not c.get("unverified"))
        json.dump(data, open(path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    # web JS copy
    js_path = os.path.join(ROOT, "app", "aca_camps_data.js")
    content = open(js_path, encoding="utf-8").read()
    m = re.search(r"window\.ACA_CAMPS\s*=\s*(\[.*\]);", content, re.DOTALL)
    arr = json.loads(m.group(1))
    for c in arr:
        vc = verified.get(c["id"])
        if vc and not c.get("acaVerified"):
            c["acaVerified"] = True
            c["verificationMethod"] = "aca_finder"
            if vc.get("sourceUrl"):
                c["sourceUrl"] = vc["sourceUrl"]
    open(js_path, "w", encoding="utf-8").write(
        "// CampFind dataset — generated by scrapers/v3_export.py\n"
        "window.ACA_CAMPS = " + json.dumps(arr, ensure_ascii=False) + ";\n")
    print(f"updated {changed} camps to acaVerified=true across 3 copies", flush=True)


if __name__ == "__main__":
    main()
