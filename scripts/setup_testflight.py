#!/usr/bin/env python3
import os, sys, json, time, base64, urllib.request
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature
key_id = os.environ["ASC_KEY_ID"]; issuer = os.environ["ASC_ISSUER_ID"]
key_pem = os.environ["ASC_KEY"].replace("\\n", "\n")
app_id = "6806695913"
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

# App info
app = api("GET", f"/v1/apps/{app_id}")
if app.get("data"):
    a = app["data"][0]["attributes"]
    print("APP:", a.get("name"), "| bundleId:", a.get("bundleId"), "| sku:", a.get("sku"), "| primaryLocale:", a.get("primaryLocale"))
else:
    print("app err", app.get("__e__"), app.get("b"))

# Latest build full state (include beta build state)
b = api("GET", f"/v1/builds?filter[app]={app_id}&sort=-uploadedDate&limit=1&fields[build]=version,shortVersion,buildNumber,processingState,buildState,betaBuildState,expirationDate,uploadedDate")
if b.get("data"):
    x = b["data"][0]
    print("BUILD:", x["id"])
    print("  shortVersion:", x["attributes"].get("shortVersion"))
    print("  buildNumber:", x["attributes"].get("buildNumber"))
    print("  processingState:", x["attributes"].get("processingState"))
    print("  buildState:", x["attributes"].get("buildState"))
    print("  betaBuildState:", x["attributes"].get("betaBuildState"))
    print("  expirationDate:", x["attributes"].get("expirationDate"))

# App Store version state (does the app have an App Store presence yet?)
ver = api("GET", f"/v1/appStoreVersions?filter[app]={app_id}&limit=5")
print("APP STORE VERSIONS:", len(ver.get("data",[])) if ver.get("data") else 0)
for v in ver.get("data", []):
    print("  version:", v["attributes"].get("versionString"), "| state:", v["attributes"].get("appStoreState"))
print("DONE")
