#!/usr/bin/env python3
import os, json, time, base64, urllib.request
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature
key_id = os.environ["ASC_KEY_ID"]; issuer = os.environ["ASC_ISSUER_ID"]
key_pem = os.environ["ASC_KEY"].replace("\\n", "\n")
app_id = os.environ.get("APP_ID", "6806695913")
pk = serialization.load_pem_private_key(key_pem.encode(), password=None)
def b64u(d): return base64.urlsafe_b64encode(d).rstrip(b"=").decode()
def jwt():
    h = b64u(json.dumps({"alg":"ES256","kid":key_id,"typ":"JWT"}).encode())
    p = b64u(json.dumps({"iss":issuer,"iat":int(time.time()),"exp":int(time.time())+1200,"aud":"appstoreconnect-v1"}).encode())
    si = f"{h}.{p}"; der = pk.sign(si.encode(), ec.ECDSA(hashes.SHA256()))
    r,s = decode_dss_signature(der); sig = b64u(r.to_bytes(32,"big")+s.to_bytes(32,"big"))
    return f"{si}.{sig}"
TOKEN = jwt()
def api(method, path):
    req = urllib.request.Request("https://api.appstoreconnect.apple.com"+path,
        headers={"Authorization": f"Bearer {TOKEN}"})
    try:
        with urllib.request.urlopen(req) as r:
            raw = r.read().decode(); return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        return {"__e__": e.code, "b": e.read().decode()[:500]}

# build beta state
b = api("GET", f"/v1/builds?filter[app]={app_id}&sort=-uploadedDate&limit=1")
if b.get("data"):
    x = b["data"][0]
    print("BUILD:", x["id"])
    for k in ["shortVersion","buildNumber","processingState","buildState","expirationDate","uploadedDate","betaBuildState","betaReviewState"]:
        print("  ", k, ":", x["attributes"].get(k))
    # beta review submission relationship
    if "relationships" in x and "betaAppReviewSubmission" in x["relationships"]:
        sub = api("GET", "/v1/builds/"+x["id"]+"/betaAppReviewSubmission")
        if sub.get("data"):
            print("  betaAppReviewSubmission:", json.dumps(sub["data"][0]["attributes"]))
        else:
            print("  betaAppReviewSubmission: none", sub.get("__e__"), sub.get("b",""))
        break
else:
    print("no build", b.get("__e__"), b.get("b",""))
# beta review details
det = api("GET", f"/v1/betaAppReviewDetails?filter[app]={app_id}")
if det.get("data"):
    print("BETA REVIEW DETAILS:", json.dumps(det["data"][0]["attributes"]))
# beta groups
grp = api("GET", f"/v1/betaGroups?filter[app]={app_id}&limit=20")
for g in grp.get("data", []):
    print("GROUP:", g["attributes"].get("name"), "| internal:", g["attributes"].get("isInternalGroup"), "| publicLink:", g["attributes"].get("publicLink"))
print("DONE")
