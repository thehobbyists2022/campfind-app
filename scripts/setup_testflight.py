#!/usr/bin/env python3
import os, sys, json, time, base64, urllib.request
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature
key_id = os.environ["ASC_KEY_ID"]; issuer = os.environ["ASC_ISSUER_ID"]
key_pem = os.environ["ASC_KEY"].replace("\\n", "\n")
app_id = "6806695913"
build_id = "3f1c2cf7-89cb-44ee-a937-5661a8ebe102"
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

# Try to find an existing internal group first
groups = api("GET", f"/v1/betaGroups?filter[app]={app_id}&limit=50")
gid = None
for g in groups.get("data", []):
    if g["attributes"].get("isInternalGroup"):
        gid = g["id"]; print("FOUND existing INTERNAL group:", gid, g["attributes"].get("name")); break

if not gid:
    grp = api("POST", "/v1/betaGroups", {"data":{"type":"betaGroups","attributes":{"name":"Internal Testing"},"relationships":{"app":{"data":{"type":"apps","id":app_id}}}}})
    print("POST response raw:", json.dumps(grp)[:400])
    if "__e__" in grp:
        print("CREATE INTERNAL GROUP err:", grp["__e__"], grp["b"])
    elif grp.get("data"):
        gid = grp["data"][0]["id"]
        print("INTERNAL GROUP CREATED:", gid, grp["data"][0]["attributes"].get("name"))
    else:
        # maybe POST 204 no body but created; re-list to find
        groups2 = api("GET", f"/v1/betaGroups?filter[app]={app_id}&limit=50")
        for g in groups2.get("data", []):
            if g["attributes"].get("isInternalGroup"):
                gid = g["id"]; print("Re-listed INTERNAL group:", gid); break

if gid:
    r = api("POST", f"/v1/betaGroups/{gid}/relationships/builds", {"data":[{"type":"builds","id":build_id}]})
    if "__e__" in r: print("ADD BUILD err:", r["__e__"], r["b"])
    else: print("ADD BUILD OK to group", gid)
print("DONE")
