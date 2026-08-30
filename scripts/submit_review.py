#!/usr/bin/env python3
import os, io, json, time, base64, urllib.request
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
        return {"__e__": e.code, "b": e.read().decode()[:600]}

# latest build
b = api("GET", f"/v1/builds?filter[app]={app_id}&sort=-uploadedDate&limit=1")
if not b.get("data"): print("no build", b.get("__e__"), b.get("b","")); sys.exit(1)
bid = b["data"][0]["id"]
print("LATEST BUILD:", bid, "| processing:", b["data"][0]["attributes"].get("processingState"))

# does it already have a submission?
sub = api("GET", f"/v1/builds/{bid}/betaAppReviewSubmission")
if sub.get("data"):
    print("ALREADY SUBMITTED:", json.dumps(sub["data"][0]["attributes"]))
else:
    # ensure Beta App Description exists
    desc = api("GET", f"/v1/betaAppLocalizations?filter[app]={app_id}")
    if not desc.get("data"):
        d = api("POST", "/v1/betaAppLocalizations", {"data":{"type":"betaAppLocalizations","attributes":{"locale":"en-US","description":"CampFind helps families discover accredited summer and winter camps. This beta is for testing camp search, filters, favorites and detail views.","feedbackEmail":"clarityclinicalsolutions@gmail.com","marketingUrl":""},"relationships":{"app":{"data":{"type":"apps","id":app_id}}}}})
        print("SET DESC:", "OK" if "__e__" not in d else f"err {d['__e__']} {d['b']}")
    r = api("POST", "/v1/betaAppReviewSubmissions", {"data":{"type":"betaAppReviewSubmissions","relationships":{"build":{"data":{"type":"builds","id":bid}}}}})
    if "__e__" in r: print("SUBMIT err:", r["__e__"], r["b"])
    elif r.get("data"): print("SUBMITTED:", r["data"][0]["id"], json.dumps(r["data"][0]["attributes"]))
    else:
        # re-fetch (POST may 204 then show on GET)
        sub2 = api("GET", f"/v1/builds/{bid}/betaAppReviewSubmission")
        print("SUBMIT response:", json.dumps(sub2)[:300])
print("DONE")
