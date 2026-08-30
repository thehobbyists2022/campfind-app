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

def b64url(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

def jwt():
    h = b64url(json.dumps({"alg":"ES256","kid":key_id,"typ":"JWT"}).encode())
    p = b64url(json.dumps({"iss":issuer,"iat":int(time.time()),"exp":int(time.time())+1200,"aud":"appstoreconnect-v1"}).encode())
    si = f"{h}.{p}"
    der = private_key.sign(si.encode(), ec.ECDSA(hashes.SHA256()))
    r, s = decode_dss_signature(der)
    sig = b64url(r.to_bytes(32,"big") + s.to_bytes(32,"big"))
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
        return {"__error__": e.code, "body": e.read().decode()[:600]}

def get_tester(email):
    t = api("GET", f"/v1/betaTesters?filter[email]={urllib.parse.quote(email)}&limit=5")
    if t.get("data"): return t["data"][0]
    return None

def get_group(app_id, name):
    g = api("GET", f"/v1/betaGroups?filter[app]={app_id}&limit=50")
    if g.get("data"):
        for x in g["data"]:
            if x["attributes"].get("name") == name: return x
    return None

app_id = "6806695913"
print("APP:", app_id)

# tester
tester = get_tester(TESTER_EMAIL)
if not tester:
    r = api("POST", "/v1/betaTesters", {"data":{"type":"betaTesters","attributes":{"email":TESTER_EMAIL,"firstName":"Clarity","lastName":"Tester"}}})
    if "__error__" in r:
        print("CREATE TESTER err:", r["__error__"], r["body"])
        tester = get_tester(TESTER_EMAIL)  # 409 -> likely already exists
    else:
        tester = r["data"][0]
print("TESTER:", (tester.get("id") if tester else None), (tester.get("attributes",{}).get("email") if tester else None))

# group
group = get_group(app_id, "CampFind Testers")
if not group:
    r = api("POST", "/v1/betaGroups", {"data":{"type":"betaGroups","attributes":{"name":"CampFind Testers"},"relationships":{"app":{"data":{"type":"apps","id":app_id}}}}})
    if "__error__" in r:
        print("CREATE GROUP err:", r["__error__"], r["body"])
        group = get_group(app_id, "CampFind Testers")
    else:
        group = r["data"][0]
print("GROUP:", (group.get("id") if group else None), (group.get("attributes",{}).get("name") if group else None))

if tester and group:
    # add tester
    r1 = api("POST", f"/v1/betaGroups/{group['id']}/relationships/betaTesters", {"data":[{"type":"betaTesters","id":tester["id"]}]})
    print("ADD TESTER:", "OK" if "__error__" not in r1 else f"err {r1['__error__']} {r1['body']}")
    # add latest build to group
    builds = api("GET", f"/v1/builds?filter[app]={app_id}&sort=-uploadedDate&limit=1")
    if builds.get("data"):
        b = builds["data"][0]
        r2 = api("POST", f"/v1/betaGroups/{group['id']}/relationships/builds", {"data":[{"type":"builds","id":b["id"]}]})
        print("ADD BUILD:", "OK" if "__error__" not in r2 else f"err {r2['__error__']} {r2['body']}")
        print("BUILD:", b["attributes"].get("processingState"), b["id"])
    else:
        print("NO BUILD FOUND")
print("DONE")
