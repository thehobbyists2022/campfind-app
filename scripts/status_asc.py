#!/usr/bin/env python3
import os, json, time, base64, urllib.request
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature
key_id = os.environ["ASC_KEY_ID"]; issuer = os.environ["ASC_ISSUER_ID"]
key_pem = os.environ["ASC_KEY"].replace("\\n", "\n")
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
def api(method, path):
    req = urllib.request.Request("https://api.appstoreconnect.apple.com"+path, headers={"Authorization": f"Bearer {TOKEN}"})
    try:
        with urllib.request.urlopen(req) as r:
            raw = r.read().decode(); return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as e:
        return {"__e__": e.code, "b": e.read().decode()[:500]}

# confirm submission exists + state
sub = api("GET", f"/v1/builds/{build_id}/betaAppReviewSubmission")
if sub.get("data"):
    d = sub["data"]
    print("SUBMISSION EXISTS:", d.get("id"), json.dumps(d.get("attributes",{})))
else:
    print("NO SUBMISSION:", sub.get("__e__"), sub.get("b",""))

# look at review submission state from the app side
st = api("GET", "/v1/betaAppReviewSubmissions?filter[build]="+build_id)
if st.get("data"):
    for x in st["data"]:
        print("SUBMISSION STATE:", json.dumps(x["attributes"]))
else:
    print("query submissions:", st.get("__e__"), st.get("b",""))
print("DONE")
