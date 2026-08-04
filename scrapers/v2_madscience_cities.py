#!/usr/bin/env python3
"""Authoritative Mad Science franchise -> city map (v2, evidence-based).

Evidence rules (R1/R2):
  - Franchise EXISTS iff its subdomain appears in official
    madscience.org/sitemap.xml (verified 2026-08-02).
  - City mapping is CONSERVATIVE: (a) subdomain name when it literally names
    a city, (b) the franchise's own homepage footer address, or (c) the
    franchise homepage <title> city. No speculative service areas.
"""
import json
import os

# subdomain -> (claim_cities, state, evidence_note)
# claim_cities = set of camp-claimed cities that this franchise evidences.
FRANCHISES = {
    "austin":              (["Austin"], "TX", "subdomain name"),
    "centrallosangeles":   (["Los Angeles"], "CA", "subdomain name"),
    "centralva":           (["Glen Allen", "Richmond"], "VA", "footer addr Glen Allen VA 23059 + serving Richmond"),
    "cfl":                 (["Orlando"], "FL", "footer addr Orlando FL 32854"),
    "charlotte":           (["Charlotte"], "NC", "subdomain name"),
    "chicago":             (["Chicago"], "IL", "subdomain name"),
    "colorado":            (["Denver"], "CO", "homepage title 'Mad Science of Colorado | Denver, CO'"),
    "connecticut":         (["Stratford"], "CT", "footer addr Stratford CT 06614"),
    "dc":                  (["Silver Spring", "Washington"], "MD", "footer addr Silver Spring MD 20904"),
    "detroit":             (["Detroit"], "MI", "subdomain name + title"),
    "dfw":                 (["Dallas", "Fort Worth", "Farmers Branch"], "TX", "DFW metro + footer addr Farmers Branch TX 75006"),
    "greatersaltlake":     (["Salt Lake City"], "UT", "subdomain name"),
    "greatertampabay":     (["Tampa"], "FL", "subdomain name"),
    "hamptonroads":        (["Chesapeake", "Norfolk"], "VA", "footer addr Chesapeake VA 23320"),
    "houston":             (["Houston"], "TX", "subdomain name"),
    "kansascity":          (["Kansas City"], "KS", "subdomain name"),
    "longisland":          (["East Meadow", "Long Island"], "NY", "footer addr East Meadow NY 11554"),
    "milwaukee":           (["Milwaukee"], "WI", "subdomain name + title"),
    "nephoenix":           (["Phoenix"], "AZ", "subdomain name (NE Phoenix)"),
    "newyorkcity":         (["New York"], "NY", "subdomain name"),
    "norfolk":             (["Norfolk"], "VA", "subdomain name"),
    "northeastnj":         (["Fair Lawn"], "NJ", "footer addr Fair Lawn NJ 07410"),
    "northeastohio":       (["North Canton", "Canton"], "OH", "footer addr North Canton OH 44720"),
    "northillinois":       (["Wheeling"], "IL", "footer addr Wheeling IL 60090"),
    "okc":                 (["Oklahoma City", "Edmond"], "OK", "subdomain name + footer addr Edmond OK 73013"),
    "palmbeachbroward":    (["Jupiter", "West Palm Beach"], "FL", "footer addr Jupiter FL 33458"),
    "pittsburgh":          (["Pittsburgh"], "PA", "subdomain name"),
    "sacramento":          (["Sacramento"], "CA", "subdomain name"),
    "sandiego":            (["San Diego"], "CA", "subdomain name"),
    "snoking":             (["Snohomish"], "WA", "subdomain name (Sno-King, WA)"),
    "southernmass":        (["Fall River"], "MA", "footer addr Fall River MA 02720"),
    "stlouis":             (["St. Louis"], "MO", "subdomain name"),
    "thebayarea":          (["San Francisco"], "CA", "subdomain name (SF Bay Area)"),
    "triad":               (["Raleigh"], "NC", "footer addr Raleigh NC 27636"),
    "triangle":            (["Raleigh"], "NC", "footer addr Raleigh NC 27636"),
    "westnewengland":      (["Indian Orchard", "Springfield"], "MA", "footer addr Indian Orchard MA 01151"),
    "westorangecounty":    (["Santa Ana"], "CA", "footer addr Santa Ana CA 92704"),
    "wnj":                 (["Pennington"], "NJ", "footer addr Pennington NJ 08534"),
}


def main():
    franchises = []
    for sub, (cities, state, note) in sorted(FRANCHISES.items()):
        franchises.append({
            "subdomain": sub,
            "city": cities[0],
            "state": state,
            "service_cities": cities[1:],
            "evidence": note,
            "sourceUrl": f"https://{sub}.madscience.org/",
        })
    data = {
        "source": "madscience.org/sitemap.xml + franchise homepage footer/title",
        "verifiedAt": "2026-08-02",
        "method": "subdomain in official sitemap; city from subdomain name or official homepage address",
        "franchises": franchises,
    }
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "v2_madscience_cities.json")
    json.dump(data, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"wrote {len(franchises)} franchises -> {out}")


if __name__ == "__main__":
    main()
