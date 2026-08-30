#!/usr/bin/env python3
import os, sys, json, time, base64, urllib.request, urllib.parse

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature

key_id = os.environ["ASC_KEY_ID"]
issuer = os.environ["ASC_ISSUER_ID"]
key_pem = os.environ["ASC_KEY"].replace("\\n", "\n")
TESTER_EMAIL = os.environ.get("TESTER_EMAIL", "clarityclinicalsolutions@gmail.com")

private_key = serialization.load_pem_private_key(key_pem.encode(), password=None)

def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def jwt():
    h = b64url(json.dumps({"alg": "ES256", "kid": key_id, "typ": "JWT"}).encode())
    p = b64url(json.dumps({"iss": issuer, "iat": int(time.time()), "exp": int(time.time()) + 1200, "aud": "appstoreconnect-v1"}).encode())
    si = f"{h}.{p}"
    der = private_key.sign(si.encode(), ec.ECDSA(hashes.SHA256()))
    r, s = decode_dss_signature(der)
    sig = b64url(r.to_bytes(32, "big") + s.to_bytes(32, "big"))
    return f"{si}.{sig}"

TOKEN = jwt()

def api(method, path, body=None):
    url = "https://api.appstoreconnect.apple.com" + path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method,
        headers={"Authorization": f"Bearer {TOKEN}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            raw = r.read().decode()
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        print(f"API {method} {path} -> HTTP {e.code}: {e.read().decode()[:600]}")
        return None

# 1. find app by bundle id
apps = api("GET", "/v1/apps?filter[bundleId]=com.campfind.app&limit=5")
if not apps or not apps.get("data"):
    print("APP NOT FOUND for com.campfind.app"); sys.exit(1)
app_id = apps["data"][0]["id"]
print("APP_ID:", app_id, "| name:", apps["data"][0]["attributes"].get("name"))

# 2. existing beta groups for app
groups = api("GET", f"/v1/betaGroups?filter[app]={app_id}&limit=20")
if groups and groups.get("data"):
    print("EXISTING BETA GROUPS:", [g["attributes"].get("name") for g in groups["data"]])
else:
    print("NO BETA GROUPS yet")

# 3. does tester exist
t = api("GET", f"/v1/betaTesters?filter[email]={urllib.parse.quote(TESTER_EMAIL)}&limit=5")
tester_id = None
if t and t.get("data"):
    tester_id = t["data"][0]["id"]
    print("TESTER EXISTS:", tester_id, t["data"][0]["attributes"].get("email"))
else:
    nt = api("POST", "/v1/betaTesters", {"data": {"type": "betaTesters", "attributes": {
        "email": TESTER_EMAIL, "firstName": "Clarity", "lastName": "Tester"}}})
    if nt and nt.get("data"):
        tester_id = nt["data"][0]["id"]
        print("TESTER CREATED:", tester_id)
    else:
        print("COULD NOT CREATE TESTER (may need to be a team user for internal groups)")
        print("Try listing testers or check roles.")

# 4. create a beta group (external) named CampFind Testers
grp = api("POST", "/v1/betaGroups", {"data": {"type": "betaGroups", "attributes": {"name": "CampFind Testers"}, "relationships": {"app": {"data": {"type": "apps", "id": app_id}}}}})
group_id = None
if grp and grp.get("data"):
    group_id = grp["data"][0]["id"]
    print("BETA GROUP CREATED:", group_id, grp["data"][0]["attributes"].get("name"))
    if tester_id:
        # add tester to group
        r1 = api("POST", f"/v1/betaGroups/{group_id}/relationships/betaTesters",
                 {"data": [{"type": "betaTesters", "id": tester_id}]})
        print("ADD TESTER to group:", "OK" if r1 is not None else "FAILED")
        # add latest build to group
        builds = api("GET", f"/v1/builds?filter[app]={app_id}&sort=-uploadedDate&limit=1")
        if builds and builds.get("data"):
            build_id = builds["data"][0]["id"]
            print("LATEST BUILD ID:", build_id, builds["data"][0]["attributes"].get("processingState"))
            r2 = api("POST", f"/v1/betaGroups/{group_id}/relationships/builds",
                     {"data": [{"type": "builds", "id": build_id}]})
            print("ADD BUILD to group:", "OK" if r2 is not None else "FAILED")
print("DONE")
