#!/usr/bin/env python3
"""
CampFind v2 — Task 2: tiered cleanup of the existing dataset.

Decisions:
  tierA  (270) -> keep, clean fabricated fields, add provenance
  tierB  (493) -> split:
      * single-org REAL camps (verified manually) -> promote to tierA
      * national orgs (YMCA/JCC/Scouts/franchise brands w/ unverifiable
        specific location) -> keep but mark `unverified: true` (UI will show
        "Unverified — confirm with provider"). NOT bulk-deleted (avoids
        deleting real YMCA/JCC/Girl Scouts camps, per plan).
  tierC  (297) -> remove, log with reason to v2_removed_camps.json

Output: app/aca_camps_v2.json (cleaned), scrapers/v2_removed_camps.json
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- single-org camps manually verified as REAL (known authentic camps) ---
# (website_domain, camp_name_substring) -> promoted to tierA
MANUAL_REAL = [
    ("ymcasd.org", "Camp Marston"),
    ("ymcaoftheozarks.org", ""),          # YMCA of the Ozarks Camp Sunnen
    ("campalleghanyforgirls.com", ""),
    ("seagull-seafarer.org", ""),
    ("catalinaislandcamps.com", ""),
    ("sdzsafari.org", ""),                # SD Zoo Safari Park (Escondido-area camps)
    ("ymcade.org", "Western Family"),
    ("bar-t.com", ""),
    ("internationalmusiccamp.com", ""),
    ("campgreylock.com", ""),
    ("romaca.com", ""),
    ("ciymca.org", "Ventura"),
    ("sdbgarden.org", ""),
    ("camphuckins.org", ""),
    ("floridadiabetescamp.org", ""),
    ("campdudley.org", ""),
    ("outpostsummercamps.com", ""),
    ("sdice.com", ""),
    ("trailblazers.org", ""),
    ("tamarackdaycamp.com", ""),
    ("geneseevalley.org", ""),
    ("vosjcc.org", ""),
    ("rbaymca.org", ""),
    ("jccotp.org", ""),
    ("cloverleafranch.com", ""),
    ("campnatoma.org", ""),
    ("campoceanpines.org", ""),
    ("paliadventures.com", ""),
]

# national org / franchise domains that stay as UNVERIFIED (not deleted)
UNVERIFIED_DOMAINS = {
    "ymca.org", "jcc.org", "girlscouts.org", "scouting.org", "clubscikidz.com",
    "littlemedicalschool.com", "usbaseballacademy.com", "bachtorock.com",
    "youngrembrandts.com", "trackersearth.com", "invent.org", "chulavistaca.gov",
}

FAKE_EMAIL = {"info@campwebsite.org", "admin@example.com"}


def clean_camp(c):
    """Null out fabricated fields. Keep honest fields only.

    G2 directive (2026-08-02): phones and emails in this dataset were all
    AI-generated and none verified against official sources. Zero fabrication
    (R1) => null ALL phones and ALL emails. Parents reach the camp via the
    verified official website link. Any future re-added contact data must be
    extracted from the camp's own official pages.
    """
    out = dict(c)
    # phone: NOTHING verified against official pages -> null all
    out["phone"] = None
    # email: NOTHING verified against official pages -> null all
    out["email"] = None
    # rating/reviewCount: no verified source -> null
    if not out.get("reviewCount"):
        out["rating"] = None
        out["reviewCount"] = None
    # description: drop template/boilerplate, keep specific ones
    desc = str(out.get("description") or "")
    low = desc.lower()
    if ("accredited by the american camp associati" in low or
        "official aca accredited camp in" in low or
        "official summer camp program" in low or
        "premier aca accredited" in low):
        out["description"] = None
    # acaVerified: cannot claim without find.acacamps.org proof
    out["acaVerified"] = False
    # remove tier internals (re-added by exporter)
    for k in ("_tier", "_tier_reason", "_tier_sourceUrl", "_tier_domain"):
        out.pop(k, None)
    return out


def main():
    report = json.load(open(os.path.join(ROOT, "scrapers", "v2_tier_report.json"), encoding="utf-8"))
    camps = report["camps"]

    kept = []
    removed = []
    manual_promoted = []

    for c in camps:
        tier = c.get("_tier")
        if tier == "tierC":
            removed.append({
                "id": c.get("id"), "name": c.get("name"), "city": c.get("city"),
                "state": c.get("state"), "website": c.get("website"),
                "reason": c.get("_tier_reason"), "sourceUrl": c.get("_tier_sourceUrl"),
            })
            continue
        if tier == "tierB":
            domain = c.get("_tier_domain", "")
            # manual-real single orgs
            matched_manual = False
            for d, sub in MANUAL_REAL:
                if d == domain and (not sub or sub.lower() in (c.get("name") or "").lower()):
                    matched_manual = True
                    break
            if matched_manual:
                c["unverified"] = False
                c["verificationMethod"] = "manual"
                c["verifiedAt"] = "2026-08-02"
                manual_promoted.append(c["name"])
                kept.append(c)
            elif domain in UNVERIFIED_DOMAINS:
                c["unverified"] = True
                c["verificationMethod"] = None
                kept.append(c)
            else:
                # other tierB (unknown) -> keep but unverified
                c["unverified"] = True
                c["verificationMethod"] = None
                kept.append(c)
            continue
        # tierA
        c["unverified"] = False
        if not c.get("verificationMethod"):
            c["verificationMethod"] = c.get("_tier_reason", "official_listing") if "official" in c.get("_tier_reason", "") else "location_listing"
        if not c.get("verifiedAt"):
            c["verifiedAt"] = "2026-08-02"
        kept.append(c)

    # clean fields for all kept
    kept = [clean_camp(c) for c in kept]

    # summary
    print(f"kept: {len(kept)}  (tierA {sum(1 for c in kept if not c['unverified'])} verified, "
          f"{sum(1 for c in kept if c['unverified'])} unverified)")
    print(f"removed (tierC): {len(removed)}")
    print(f"manual-promoted from tierB: {len(manual_promoted)}")

    # write outputs
    out_data = {
        "source": "CampFind v2 cleaned dataset",
        "total_camps": len(kept),
        "verified_count": sum(1 for c in kept if not c["unverified"]),
        "unverified_count": sum(1 for c in kept if c["unverified"]),
        "removed_count": len(removed),
        "camps": kept,
    }
    out1 = os.path.join(ROOT, "app", "aca_camps_v2.json")
    json.dump(out_data, open(out1, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    out2 = os.path.join(ROOT, "scrapers", "v2_removed_camps.json")
    json.dump({"removed_count": len(removed), "camps": removed},
              open(out2, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("wrote:", out1)
    print("wrote:", out2)


if __name__ == "__main__":
    main()
