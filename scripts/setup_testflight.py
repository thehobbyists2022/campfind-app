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
det = api("GET", f"/v1/betaAppReviewDetails?filter[app]={app_id}")
if det.get("data"):
    print("BETA REVIEW DETAILS:", json.dumps(det["data"][0]["attributes"]))
else:
    print("none:", det.get("__e__"), det.get("b",""))
print("DONE")
