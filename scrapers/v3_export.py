#!/usr/bin/env python3
"""
CampFind v3 — Task 6: three-copy sync exporter.

Merges the cleaned dataset (app/aca_camps_v2.json) with the real expansion
(app/aca_camps_expansion_v3.json) and city-run camps (aca_camps_city_v4.json),
plus brand expansion (aca_camps_brands_v5.json), dedupes franchise-brand
overlaps, and produces the three runtime copies:
  app/aca_camps.json            (canonical JSON)
  app/aca_camps_data.js         (web: window.ACA_CAMPS = [...])
  mobile/assets/aca_camps.json  (Flutter app asset)
"""
import json
import os
import re
import sys
from urllib.parse import urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

FRANCHISE_DOMAINS = {
    "codeninjas.com", "ussportscamps.com", "steveandkatescamp.com",
    "galileo-camps.com", "avid4.com", "madscience.org", "idtech.com", "magikidlab.com",
    "schoolofrock.com", "dramakids.com", "usbaseballacademy.com", "bachtorock.com",
}


def slug(s):
    return re.sub(r"[^a-z0-9]+", "", (s or "").lower())


def dom(u):
    try:
        return urlparse(u).netloc.replace("www.", "").lower()
    except Exception:
        return u or ""


def main():
    v2 = json.load(open(os.path.join(ROOT, "app", "aca_camps_v2.json"), encoding="utf-8"))["camps"]
    v3 = json.load(open(os.path.join(ROOT, "app", "aca_camps_expansion_v3.json"), encoding="utf-8"))["camps"]
    # v4 city-run camps (optional)
    v4 = []
    v4_path = os.path.join(ROOT, "app", "aca_camps_city_v4.json")
    if os.path.exists(v4_path):
        v4 = json.load(open(v4_path, encoding="utf-8"))["camps"]
    # v5 brand expansion (School of Rock + Drama Kids, optional)
    v5 = []
    v5_path = os.path.join(ROOT, "app", "aca_camps_brands_v5.json")
    if os.path.exists(v5_path):
        v5 = json.load(open(v5_path, encoding="utf-8"))["camps"]
    # v6 brand expansion (US Baseball Academy + Bach to Rock + VOSJ JCC, optional)
    v6 = []
    v6_path = os.path.join(ROOT, "app", "aca_camps_brands_v6.json")
    if os.path.exists(v6_path):
        v6 = json.load(open(v6_path, encoding="utf-8"))["camps"]
    # v7 US Sports Camps full destinations (optional)
    v7 = []
    v7_path = os.path.join(ROOT, "app", "aca_camps_brands_v7.json")
    if os.path.exists(v7_path):
        v7 = json.load(open(v7_path, encoding="utf-8"))["camps"]
    # v8 Snapology STEM franchises (optional)
    v8 = []
    v8_path = os.path.join(ROOT, "app", "aca_camps_brands_v8.json")
    if os.path.exists(v8_path):
        v8 = json.load(open(v8_path, encoding="utf-8"))["camps"]
    # v9 Goldfish Swim School locations (optional)
    v9 = []
    v9_path = os.path.join(ROOT, "app", "aca_camps_brands_v9.json")
    if os.path.exists(v9_path):
        v9 = json.load(open(v9_path, encoding="utf-8"))["camps"]
    # v12 Bricks 4 Kidz US franchises (optional)
    v12 = []
    v12_path = os.path.join(ROOT, "app", "aca_camps_brands_v12.json")
    if os.path.exists(v12_path):
        v12 = json.load(open(v12_path, encoding="utf-8"))["camps"]
    # v13 under-represented-state real camps (optional)
    v13 = []
    v13_path = os.path.join(ROOT, "app", "aca_camps_brands_v13.json")
    if os.path.exists(v13_path):
        v13 = json.load(open(v13_path, encoding="utf-8"))["camps"]
    # v14 Allen TX Parks & Rec summer camps (optional)
    v14 = []
    v14_path = os.path.join(ROOT, "app", "aca_camps_brands_v14.json")
    if os.path.exists(v14_path):
        v14 = json.load(open(v14_path, encoding="utf-8"))["camps"]
    # v15 Seattle Parks & Rec summer camps (optional)
    v15 = []
    v15_path = os.path.join(ROOT, "app", "aca_camps_brands_v15.json")
    if os.path.exists(v15_path):
        v15 = json.load(open(v15_path, encoding="utf-8"))["camps"]
    # v16 San Marcos CA Parks & Rec camps (optional)
    v16 = []
    v16_path = os.path.join(ROOT, "app", "aca_camps_brands_v16.json")
    if os.path.exists(v16_path):
        v16 = json.load(open(v16_path, encoding="utf-8"))["camps"]
    # v17 Poway + Solana Beach CA camps (optional)
    v17 = []
    v17_path = os.path.join(ROOT, "app", "aca_camps_brands_v17.json")
    if os.path.exists(v17_path):
        v17 = json.load(open(v17_path, encoding="utf-8"))["camps"]
    # v18 Santee + Lemon Grove CA camps (optional)
    v18 = []
    v18_path = os.path.join(ROOT, "app", "aca_camps_brands_v18.json")
    if os.path.exists(v18_path):
        v18 = json.load(open(v18_path, encoding="utf-8"))["camps"]

    # Drop legacy synthetic brand entries from v2 — replaced by the real
    # per-location brand camps in v5/v6 (R1: their fabricated price/age/shuttle
    # fields have no official source).
    for legacy_dom in ("schoolofrock.com", "usbaseballacademy.com", "bachtorock.com"):
        v2 = [c for c in v2 if not (c.get("website", "").find(legacy_dom) >= 0)]

    # v2 franchise keys (keep these versions on overlap)
    v2keys = set()
    for c in v2:
        d = dom(c.get("website", ""))
        if d in FRANCHISE_DOMAINS:
            v2keys.add((d, slug(c["city"]), (c.get("state") or "").upper()))

    merged = list(v2)
    dup_skipped = 0
    for c in v3:
        d = c.get("source", "").split(":")[-1]
        key = (d, slug(c["city"]), (c.get("state") or "").upper())
        if key in v2keys:
            dup_skipped += 1
            continue
        merged.append(c)

    # v4 city camps: add (no dup risk, provider=city unique ids)
    merged.extend(v4)

    # v5 brand camps: add (no dup risk — v2 SoR removed above, unique ids with
    # summer/fall suffixes). Guard against any residual same-id collision.
    seen_ids = {c["id"] for c in merged}
    for c in v5:
        if c["id"] in seen_ids:
            dup_skipped += 1
            continue
        seen_ids.add(c["id"])
        merged.append(c)

    # v6 brand camps: add (same pattern — unique ids).
    for c in v6:
        if c["id"] in seen_ids:
            dup_skipped += 1
            continue
        seen_ids.add(c["id"])
        merged.append(c)

    # v7 US Sports Camps: add (unique ids).
    for c in v7:
        if c["id"] in seen_ids:
            dup_skipped += 1
            continue
        seen_ids.add(c["id"])
        merged.append(c)

    # v8 Snapology: add (unique ids).
    for c in v8:
        if c["id"] in seen_ids:
            dup_skipped += 1
            continue
        seen_ids.add(c["id"])
        merged.append(c)

    # v9 Goldfish: add (unique ids).
    for c in v9:
        if c["id"] in seen_ids:
            dup_skipped += 1
            continue
        seen_ids.add(c["id"])
        merged.append(c)

    # v12 Bricks 4 Kidz: add (unique ids).
    for c in v12:
        if c["id"] in seen_ids:
            dup_skipped += 1
            continue
        seen_ids.add(c["id"])
        merged.append(c)

    # v13 focus-state real camps: add (unique ids).
    for c in v13:
        if c["id"] in seen_ids:
            dup_skipped += 1
            continue
        seen_ids.add(c["id"])
        merged.append(c)

    # v14 Allen TX camps: add (unique ids).
    for c in v14:
        if c["id"] in seen_ids:
            dup_skipped += 1
            continue
        seen_ids.add(c["id"])
        merged.append(c)

    # v15 Seattle camps: add (unique ids).
    for c in v15:
        if c["id"] in seen_ids:
            dup_skipped += 1
            continue
        seen_ids.add(c["id"])
        merged.append(c)

    # v16 San Marcos camps: add (unique ids).
    for c in v16:
        if c["id"] in seen_ids:
            dup_skipped += 1
            continue
        seen_ids.add(c["id"])
        merged.append(c)

    # v17 Poway/Solana Beach camps: add (unique ids).
    for c in v17:
        if c["id"] in seen_ids:
            dup_skipped += 1
            continue
        seen_ids.add(c["id"])
        merged.append(c)

    # v18 Santee/Lemon Grove camps: add (unique ids).
    for c in v18:
        if c["id"] in seen_ids:
            dup_skipped += 1
            continue
        seen_ids.add(c["id"])
        merged.append(c)

    # ensure every record has needed fields
    for c in merged:
        c.setdefault("unverified", True)
        c.setdefault("acaVerified", False)
        c.setdefault("weeks", [] if c.get("weeks") else None)
        c.setdefault("price", None)
        c.setdefault("rating", None)
        c.setdefault("ageMin", None)
        c.setdefault("ageMax", None)
        c.setdefault("phone", None)
        c.setdefault("email", None)
        c.setdefault("beforeCare", None)
        c.setdefault("afterCare", None)
        c.setdefault("shuttle", None)
        c.setdefault("zip", None)
        c.setdefault("description", None)

    # --- legacy cleanup (R2): drop synthetic templates, fill provenance ---
    REPLACED_BRANDS = {
        "codeninjas.com", "ussportscamps.com", "idtech.com", "steveandkatescamp.com",
        "galileo-camps.com", "madscience.org", "avid4.com", "magikidlab.com",
    }
    def brand_dom(c):
        return re.sub(r"^https?://(www\.)?", "", c.get("website") or "").split("/")[0]
    drop = set()
    for c in merged:
        if c["id"].startswith("real_aca_") and brand_dom(c) in REPLACED_BRANDS:
            drop.add(c["id"])
        elif c["id"].startswith("real_exact_") and re.search(r"\s*-\s*", c.get("name", "")):
            drop.add(c["id"])
    merged = [c for c in merged if c["id"] not in drop]
    for c in merged:
        if not c.get("source"):
            c["source"] = "aca_finder" if c.get("acaVerified") else "manual_verification"
            if not c.get("sourceUrl"):
                c["sourceUrl"] = c.get("website")
            if not c.get("verifiedAt"):
                c["verifiedAt"] = "2026-08-02"
            c.setdefault("verificationMethod", "manual")

    # --- ACA accreditation re-application (v10) ---
    aca_cache = os.path.join(ROOT, "scrapers", "aca_verify_cache.json")
    if os.path.exists(aca_cache):
        try:
            sys.path.insert(0, os.path.join(ROOT, "scrapers"))
            import v10_aca_verify as aca
            cache = json.load(open(aca_cache, encoding="utf-8"))
            STOP = {"camp","camps","for","boys","girls","and","the","of","summer","day",
                    "adventure","outdoor","wilderness","youth","stem","academy","program",
                    "overnight","resident","center","specialty","inc","at","in","on","with",
                    "a","an","trip","weekly","session","school","scouting","season"}
            def core(s):
                return {t for t in s.split() if t not in STOP}
            aca_verified = 0
            for c in merged:
                if c.get("source") and "franchise_locator" in c.get("source", ""):
                    continue
                key = aca.norm_keep_city(c.get("name") or "")
                hits = cache.get(key)
                if not hits:
                    continue
                state = c.get("state", "")
                for hv in hits:
                    hv_str = hv["value"] if isinstance(hv, dict) else hv
                    hv_id = hv.get("id") if isinstance(hv, dict) else None
                    if f"({state})" not in hv_str:
                        continue
                    if aca.norm(hv_str) == key:
                        c["acaVerified"] = True
                    else:
                        oc = core(key); ac2 = core(aca.norm(hv_str))
                        if oc and ac2 and (oc <= ac2 or ac2 <= oc):
                            c["acaVerified"] = True
                    if c.get("acaVerified"):
                        c["verificationMethod"] = "aca_finder"
                        if hv_id:
                            c["sourceUrl"] = f"https://find.acacamps.org/camp_profile.php?camp_id={hv_id}"
                        aca_verified += 1
                        break
            print(f"aca re-verified: {aca_verified}", flush=True)
        except Exception as e:
            print(f"ACA re-apply skipped: {e}", flush=True)

    # --- coordinate alignment for synthetic legacy camps (R1) ---
    # Synthetic brand x city templates had noise-offset coords that landed in
    # the ocean for coastal cities. Snap them to the geocoded city center.
    geo_cache = os.path.join(ROOT, "scrapers", "geocode_cache.json")
    geo = {}
    if os.path.exists(geo_cache):
        for k, v in json.load(open(geo_cache, encoding="utf-8")).items():
            parts = k.split("|")
            if len(parts) >= 2:
                # prefer the no-zip (precise city-center) entry over the
                # zip-keyed one, which may be a wrong same-name-city geocode.
                key = (parts[0], parts[1])
                if len(parts) == 2:
                    geo[key] = v
                elif key not in geo:
                    geo[key] = v
    coord_fixed = 0
    for c in merged:
        if c.get("source") != "manual_verification":
            continue
        if c.get("acaVerified"):
            continue
        center = geo.get((c.get("city"), c.get("state")))
        if not center:
            continue
        c["lat"], c["lng"] = center[0], center[1]
        coord_fixed += 1
    if coord_fixed:
        print(f"aligned {coord_fixed} synthetic legacy camps to city center", flush=True)

    # --- fix coords that are wildly wrong (same-name city, wrong state geocode).
    # Any camp WITHOUT a real street address that sits >300km from its geocoded
    # city center is an unambiguous geocode mistake (e.g. iD Tech Arlington VA
    # pointing at Arlington TX; Camp Greylock pointing at Ohio). Real
    # street-address camps keep their precise coords.
    import math as _math
    coord_fixed2 = 0
    for c in merged:
        if c.get("address"):
            continue  # real street address -> keep precise coords
        lat, lng = c.get("lat"), c.get("lng")
        if not lat or not lng:
            continue
        center = geo.get((c.get("city"), c.get("state")))
        if not center:
            continue
        km = _math.hypot(lat - center[0], lng - center[1]) * 111
        if km > 300:
            c["lat"], c["lng"] = center[0], center[1]
            coord_fixed2 += 1
    if coord_fixed2:
        print(f"fixed {coord_fixed2} camps with wrong-state geocodes", flush=True)

    # --- correct Galileo state labels (v3 defaulted everything to CA; some
    # Galileo locations are in WA / CO). Re-state based on geocoded city center.
    coord_fixed3 = 0
    for c in merged:
        if c.get("source") != "franchise_locator:galileo-camps.com":
            continue
        if c.get("address"):
            continue
        city = c.get("city") or ""
        # known WA/CO Galileo cities
        if city.lower() in ("north seattle", "mercer island", "seattle"):
            c["state"] = "WA"
        elif city.lower() in ("littleton greenwood village", "littleton", "greenwood village", "denver"):
            c["state"] = "CO"
        center = geo.get((c.get("city"), c.get("state")))
        if center:
            c["lat"], c["lng"] = center[0], center[1]
            coord_fixed3 += 1
    if coord_fixed3:
        print(f"corrected {coord_fixed3} Galileo location states", flush=True)

    # --- drop Avid4 numeric-street placeholders ("4Th"/"5Th"/"9Th" from the
    # location sitemap are not real city names). R2: no location proof.
    before = len(merged)
    merged = [c for c in merged
              if not (c.get("source") == "franchise_locator:avid4.com"
                      and re.match(r"^\d+th$", (c.get("city") or "").lower()))]
    if len(merged) < before:
        print(f"dropped {before - len(merged)} Avid4 numeric placeholder entries", flush=True)

    # --- drop Magikid "Hq" entries: brand HQ node parsed as a store, not a
    # real camp location (city label is literally "Hq"). R2: no location proof.
    before = len(merged)
    merged = [c for c in merged
              if not (c.get("source") == "franchise_locator:magikidlab.com"
                      and (c.get("city") or "").lower() == "hq")]
    if len(merged) < before:
        print(f"dropped {before - len(merged)} Magikid HQ placeholder entries", flush=True)

    # --- website reachability fix: lifeinallen.org returns 403 to some browsers
    # (WAF). Point Allen camps at the official ActiveCommunities registration
    # portal instead, which is browser-friendly and is the actual enrollment site.
    web_fixed = 0
    for c in merged:
        if (c.get("website") or "").startswith("https://www.lifeinallen.org"):
            c["website"] = "https://anc.apm.activecommunities.com/allentxparks"
            web_fixed += 1
    if web_fixed:
        print(f"redirected {web_fixed} Allen camp websites to ActiveCommunities portal", flush=True)

    verified = sum(1 for c in merged if not c.get("unverified"))
    seasons = {}
    for c in merged:
        s = c.get("season") or "summer"
        seasons[s] = seasons.get(s, 0) + 1

    out = {
        "source": "CampFind dataset — cleaned legacy + franchise/city/brand expansion",
        "total_camps": len(merged),
        "verified_count": verified,
        "unverified_count": len(merged) - verified,
        "season_counts": seasons,
        "camps": merged,
    }

    # 1. canonical JSON
    fn1 = os.path.join(ROOT, "app", "aca_camps.json")
    json.dump(out, open(fn1, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    # 2. web JS
    fn2 = os.path.join(ROOT, "app", "aca_camps_data.js")
    js = "// CampFind dataset — generated by scrapers/v3_export.py\n"
    js += "window.ACA_CAMPS = " + json.dumps(merged, ensure_ascii=False) + ";\n"
    open(fn2, "w", encoding="utf-8").write(js)

    # 3. mobile asset
    fn3 = os.path.join(ROOT, "mobile", "assets", "aca_camps.json")
    json.dump(out, open(fn3, "w", encoding="utf-8"), ensure_ascii=False, indent=2)

    print(f"merged total: {len(merged)} (v2 {len(v2)} + v3 {len(v3)} + v4 {len(v4)} + v5 {len(v5)} + v6 {len(v6)} + v7 {len(v7)} + v8 {len(v8)} + v9 {len(v9)} + v12 {len(v12)} + v13 {len(v13)} + v14 {len(v14)} + v15 {len(v15)} + v16 {len(v16)} + v17 {len(v17)} + v18 {len(v18)}, dup skipped {dup_skipped})")
    print(f"verified: {verified}, unverified: {len(merged) - verified}")
    print(f"seasons: {seasons}")
    print(f"wrote: {fn1}")
    print(f"wrote: {fn2}")
    print(f"wrote: {fn3}")


if __name__ == "__main__":
    main()
