#!/usr/bin/env python3
import os, sys, json, time, base64, urllib.request, urllib.parse

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature

key_id = os.environ["ASC_KEY_ID"]; issuer = os.environ["ASC_ISSUER_ID"]
key_pem = os.environ["ASC_KEY"].replace("\\n", "\n")
email = os.environ.get("TESTER_EMAIL", "clarityclinicalsolutions@gmail.com")
app_id = "6806695913"

pk = serialization.load_pem_private_key(key_pem.encode(), password=None)
def b64u(d): return base64.urlsafe_b64encode(d).rstrip(b"=").decode()
def jwt():
    h = b64u(json.dumps({"alg":"ES256","kid":key_id,"typ":"JWT"}).encode())
    p = b64u(json.dumps({"iss":issuer,"iat":int(time.time()),"exp":int(time.time())+1200,"aud":"appstoreconnect-v1"}).encode())
    si = f"{h}.{p}"
    der = pk.sign(si.encode(), ec.ECDSA(hashes.SHA256()))
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

# 1. is the email a team user?
users = api("GET", f"/v1/users?filter[username]={urllib.parse.quote(email)}&limit=5")
if users.get("data"):
    u = users["data"][0]
    print("TEAM USER:", u["attributes"].get("username"), "| roles:", u["attributes"].get("roles"))
else:
    print("NOT A TEAM USER (external)")

# 2. groups for app
groups = api("GET", f"/v1/betaGroups?filter[app]={app_id}&limit=50")
for g in groups.get("data", []):
    a = g["attributes"]
    print("GROUP:", g["id"], a.get("name"), "| publicLinkEnabled:", a.get("publicLinkEnabled"), "| publicLink:", a.get("publicLink"), "| betaReviewState:", a.get("betaReviewState"))

# 3. add latest build to the FIRST group
gid = groups["data"][0]["id"] if groups.get("data") else None
if gid:
    builds = api("GET", f"/v1/builds?filter[app]={app_id}&sort=-uploadedDate&limit=1")
    if builds.get("data"):
        b = builds["data"][0]
        print("BUILD:", b["attributes"].get("shortVersion"), "(" + str(b["attributes"].get("buildNumber")) + ")", "| processing:", b["attributes"].get("processingState"))
        r = api("POST", f"/v1/betaGroups/{gid}/relationships/builds", {"data":[{"type":"builds","id":b["id"]}]})
        if "__e__" in r: print("ADD BUILD err:", r["__e__"], r["b"])
        else: print("ADD BUILD OK -> group", gid)
    else:
        print("NO BUILD")
print("DONE")
