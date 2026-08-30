#!/usr/bin/env python3
import os, sys, json, time, base64, urllib.request, urllib.parse
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature
key_id = os.environ["ASC_KEY_ID"]; issuer = os.environ["ASC_ISSUER_ID"]
key_pem = os.environ["ASC_KEY"].replace("\\n", "\n")
app_id = "6806695913"
email = "clarityclinicalsolutions@gmail.com"
pk = serialization.load_pem_private_key(key_pem.encode(), password=None)
def b64u(d): return base64.urlsafe_b64encode(d).rstrip(b"=").decode()
def jwt():
    h = b64u(json.dumps({"alg":"ES256","kid":key_id,"typ":"JWT"}).encode())
    p = b64u(json.dumps({"iss":issuer,"iat":int(time.time()),"exp":int(time.time())+1200,"aud":"appstoreconnect-v1"}).encode())
    si = f"{h}.{p}"; der = pk.sign(si.encode(), ec.ECDSA(hashes.SHA256()))
    r,s = decode_dss_signature(der); sig = b64u(r.to_bytes(32,"big")+s.to_bytes(32,"big"))
    return f"{si}.{sig}"
TOKEN = jwt()
def api(method, path, body=None):
    url = "https://api.appstoreconnect.apple.com"+path
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers={"Authorization":f"Bearer {TOKEN}","Content-Type":"application/json"})
    try:
        with urllib.request.urlopen(req) as r:
            raw = r.read().decode(); return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        return {"__e__": e.code, "b": e.read().decode()[:500]}

# list all beta groups (with isInternalGroup + builds relationships)
groups = api("GET", f"/v1/betaGroups?filter[app]={app_id}&limit=50&include=builds,betaTesters")
print("=== ALL BETA GROUPS ===")
for g in groups.get("data", []):
    a = g["attributes"]
    print(" -", g["id"], a.get("name"), "| internal:", a.get("isInternalGroup"), "| builds:", len(g.get("relationships",{}).get("builds",{}).get("data",[])), "| testers:", len(g.get("relationships",{}).get("betaTesters",{}).get("data",[])))

# check betaTesters (team users see internal automatically; external testers listed here)
bt = api("GET", f"/v1/betaTesters?filter[email]={urllib.parse.quote(email)}&limit=5")
print("BETA TESTER (by email):", bt.get("data",[{}])[0].get("id") if bt.get("data") else "none")

# any existing INTERNAL group?
internal = [g for g in groups.get("data",[]) if g["attributes"].get("isInternalGroup")]
print("INTERNAL GROUPS:", [(g["id"], g["attributes"].get("name")) for g in internal])

# list builds usable
b = api("GET", f"/v1/builds?filter[app]={app_id}&sort=-uploadedDate&limit=3")
print("=== BUILDS ===")
for x in b.get("data", []):
    print(" -", x["id"], x["attributes"].get("shortVersion"), "("+str(x["attributes"].get("buildNumber"))+")", x["attributes"].get("processingState"))
print("DONE")
