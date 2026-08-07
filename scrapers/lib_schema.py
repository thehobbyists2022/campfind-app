#!/usr/bin/env python3
"""
CampFind v2 Data Contract & Validator (Task 0).

Single source of truth for the camp record schema and validation rules.
Rules enforce the plan's iron rules R1-R4:
  R1 zero fabrication     - every field either real or null/omitted, never invented
  R2 location-level proof - acaVerified requires a verificationMethod
  R3 traceable provenance - source / sourceUrl / verifiedAt required
  R4 honest claims        - no fake phones, ratings, template descriptions
"""

import re
from urllib.parse import urlparse

# ---------------------------------------------------------------------------
# Allowed enums
# ---------------------------------------------------------------------------
VALID_TYPE = {"day", "overnight", "both"}
VALID_SEASON = {"summer", "winter", "spring", "fall"}
VALID_THEME = {"STEM", "Sports", "Arts", "Outdoor", "Academic", "General"}
VALID_VERIFICATION = {"location_listing", "profile_page", "manual"}

# ---------------------------------------------------------------------------
# USPS ZIP -> valid first-digit set per state (2-letter code)
# ---------------------------------------------------------------------------
STATE_ZIP1 = {
    "CT": {"0"}, "MA": {"0"}, "ME": {"0"}, "NH": {"0"}, "NJ": {"0"}, "RI": {"0"},
    "VT": {"0"}, "PR": {"0"},
    "NY": {"0", "1"}, "PA": {"1"}, "DE": {"1"}, "DC": {"2"}, "MD": {"2"}, "VA": {"2"},
    "WV": {"2"}, "NC": {"2"}, "SC": {"2"}, "GA": {"3"}, "FL": {"3"}, "AL": {"3"},
    "TN": {"3"}, "MS": {"3"}, "KY": {"4"}, "OH": {"4"}, "IN": {"4"}, "MI": {"4"},
    "IA": {"5"}, "MN": {"5"}, "WI": {"5"}, "SD": {"5"}, "ND": {"5"}, "MT": {"5"},
    "IL": {"6"}, "MO": {"6"}, "KS": {"6"}, "NE": {"6"},
    "LA": {"7"}, "AR": {"7"}, "OK": {"7"}, "TX": {"7"},
    "CO": {"8"}, "WY": {"8"}, "ID": {"8"}, "UT": {"8"}, "AZ": {"8"}, "NM": {"8"},
    "NV": {"8"},
    "CA": {"9"}, "OR": {"9"}, "WA": {"9"}, "AK": {"9"}, "HI": {"9"},
}
US_STATES = set(STATE_ZIP1)

# Area codes never assigned in North America (reserved/fictional).
# NOTE: 800/866/877/888/855/844 are legitimate toll-free prefixes — NOT flagged.
FAKE_AREA_CODES = {"000", "111", "123", "555", "666", "777", "999"}

DEFAULT_COORD_SENTINELS = [
    (34.0522, -118.2437),   # LA default
    (37.7749, -122.4194),   # SF default
    (37.3382, -121.8863),   # San Jose default
    (33.6846, -117.8265),   # Irvine default
    (32.7157, -117.1611),   # SD default
    (33.1959, -117.3795),   # Oceanside default
]

# Camps whose REAL geocoded location legitimately equals a sentinel value
# (e.g. a real camp at the exact city center used as a default).
LEGITIMATE_SENTINEL_COORDS = {
    "joe_&_mary_mottino_family_ymca_summer_camp": (33.1958696, -117.379483),
    "ussportscamps_oceanside_ca": (33.1958696, -117.379483),
}


# ---------------------------------------------------------------------------
# Validators (return list of violation strings; empty == OK)
# ---------------------------------------------------------------------------
def v_zip_state(c):
    z = str(c.get("zip", "") or "")
    st = c.get("state", "")
    if st not in US_STATES:
        return [f"state not in US list: {st!r}"]
    if not z:
        return []  # zip is optional (may be null when address unknown)
    if not re.fullmatch(r"\d{5}", z):
        return [f"zip not 5-digit: {z!r}"]
    if z[0] not in STATE_ZIP1[st]:
        return [f"zip first-digit {z[0]} incompatible with {st}"]
    return []


def v_phone(c):
    p = str(c.get("phone", "") or "").strip()
    if not p:
        return []
    m = re.search(r"\((\d{3})\)", p)
    if m and m.group(1) in FAKE_AREA_CODES:
        return [f"fake area code {m.group(1)} in phone {p}"]
    # fictional 555 exchange: match "555" as a standalone group in the RAW
    # string (do NOT strip hyphens — stripping splices digits like 355-5320
    # into a false "555"). e.g. "(619) 555-7258" matches; "(800) 355-5320" does not.
    if re.search(r"(?<!\d)555(?!\d)", p):
        return [f"contains 555: {p}"]
    if not re.search(r"\d{3}-\d{4}", p):
        return [f"phone not in standard format: {p}"]
    return []


def v_website(c):
    w = c.get("website", "") or ""
    if not w:
        return ["missing website"]
    try:
        p = urlparse(w)
    except Exception:
        return [f"website unparseable: {w}"]
    if p.scheme not in ("http", "https") or not p.netloc:
        return [f"website not http(s) with host: {w}"]
    if p.netloc in ("example.com", "campwebsite.org", "placeholder.com"):
        return [f"placeholder website: {w}"]
    return []


def v_coords(c):
    lat, lng = c.get("lat"), c.get("lng")
    if lat is None or lng is None:
        return ["missing lat/lng"]
    # Full US including AK (55-72N, -170--130W), HI (18-28N, -160--154W), plus contiguous
    if not (18 <= lat <= 72 and -170 <= lng <= -65):
        return [f"coords outside US bounds: ({lat},{lng})"]
    return []


def v_coord_sentinel(c):
    lat, lng = c.get("lat"), c.get("lng")
    cid = c.get("id", "")
    for slat, slng in DEFAULT_COORD_SENTINELS:
        if lat is not None and lng is not None and abs(lat - slat) < 0.001 and abs(lng - slng) < 0.001:
            if cid in LEGITIMATE_SENTINEL_COORDS:
                return []
            return [f"default/sentinel coords ({lat},{lng}) — likely ungeocoded"]
    return []


def v_aca_verified(c):
    if c.get("acaVerified") is True:
        m = c.get("verificationMethod")
        if m not in VALID_VERIFICATION:
            return ["acaVerified=true but missing/unknown verificationMethod"]
        if not c.get("sourceUrl"):
            return ["acaVerified=true but missing sourceUrl"]
    return []


def v_provenance(c):
    out = []
    if not c.get("source"):
        out.append("missing source")
    if not c.get("sourceUrl"):
        out.append("missing sourceUrl")
    if not c.get("verifiedAt"):
        out.append("missing verifiedAt")
    return out


def v_email(c):
    e = str(c.get("email", "") or "")
    if not e:
        return []
    if e in ("info@campwebsite.org", "admin@example.com") or e.endswith("@campwebsite.org"):
        return [f"placeholder email: {e}"]
    if "@" not in e or "." not in e.split("@")[-1]:
        return [f"email malformed: {e}"]
    return []


def v_description(c):
    d = str(c.get("description", "") or "")
    if not d:
        return []
    low = d.lower()
    template_markers = [
        "official summer camp program accredited by the american camp associati",
        "official aca accredited camp in",
        "premier aca accredited traditional day camp",
    ]
    for t in template_markers:
        if t in low:
            return ["template/boilerplate description"]
    return []


def v_rating(c):
    r = c.get("rating")
    if r is None:
        return []
    if not isinstance(r, (int, float)) or not (0 <= r <= 5):
        return [f"rating out of range: {r}"]
    if not c.get("reviewCount"):
        return [f"rating {r} without reviewCount (unverifiable)"]
    return []


def v_weeks(c):
    w = c.get("weeks")
    if w is None or w == []:
        return []
    if not isinstance(w, list) or not all(isinstance(x, int) for x in w):
        return [f"weeks malformed: {w}"]
    if len(w) > 10:
        return [f"implausible weeks count: {len(w)}"]
    return []


def v_enums(c):
    out = []
    for field, allowed in [("type", VALID_TYPE), ("season", VALID_SEASON), ("theme", VALID_THEME)]:
        v = c.get(field)
        if v is not None and v not in allowed:
            out.append(f"{field}={v!r} not in {sorted(allowed)}")
    return out


def v_name(c):
    if not c.get("name"):
        return ["missing name"]
    return []


# ---------------------------------------------------------------------------
# Full record validation
# ---------------------------------------------------------------------------
ALL_CHECKERS = [
    ("name", v_name),
    ("zip_state", v_zip_state),
    ("phone", v_phone),
    ("website", v_website),
    ("coords", v_coords),
    ("coord_sentinel", v_coord_sentinel),
    ("aca_verified", v_aca_verified),
    ("provenance", v_provenance),
    ("email", v_email),
    ("description", v_description),
    ("rating", v_rating),
    ("weeks", v_weeks),
    ("enums", v_enums),
]


def validate_camp(c, skip_provenance=False):
    """Return list of violation strings for one camp record."""
    out = []
    for name, fn in ALL_CHECKERS:
        if skip_provenance and name == "provenance":
            continue
        out.extend(fn(c))
    return out


def validate_all(camps, skip_provenance=False):
    """Return {index: [violations]} for a list of camps."""
    return {i: validate_camp(c, skip_provenance) for i, c in enumerate(camps)}


def violation_report(camps, label="dataset"):
    """Compact per-rule violation summary for reporting."""
    from collections import Counter
    counts = Counter()
    for i, c in enumerate(camps):
        for v in validate_camp(c):
            rule = v.split(":", 1)[0]
            counts[rule] += 1
    return counts
