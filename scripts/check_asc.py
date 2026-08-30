#!/usr/bin/env python3
import os, sys, json, time, base64, urllib.request, urllib.parse

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature

key_id = os.environ["ASC_KEY_ID"]
issuer = os.environ["ASC_ISSUER_ID"]
key_pem = os.environ["ASC_KEY"].replace("\\n", "\n")

private_key = serialization.load_pem_private_key(key_pem.encode(), password=None)

def b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()

header = b64url(json.dumps({"alg": "ES256", "kid": key_id, "typ": "JWT"}).encode())
payload = b64url(json.dumps({
    "iss": issuer, "iat": int(time.time()), "exp": int(time.time()) + 1200, "aud": "appstoreconnect-v1"
}).encode())
signing_input = f"{header}.{payload}"

der = private_key.sign(signing_input.encode(), ec.ECDSA(hashes.SHA256()))
r, s = decode_dss_signature(der)
raw_sig = r.to_bytes(32, "big") + s.to_bytes(32, "big")
signature = b64url(raw_sig)
jwt = f"{signing_input}.{signature}"

url = ("https://api.appstoreconnect.apple.com/v1/builds"
       "?sort=-uploadedDate&limit=10")
req = urllib.request.Request(url, headers={"Authorization": f"Bearer {jwt}"})
try:
    with urllib.request.urlopen(req) as resp:
        d = json.load(resp)
except urllib.error.HTTPError as e:
    print("HTTP", e.code, e.read().decode()[:600])
    sys.exit(1)

if "errors" in d:
    print("API ERRORS:", json.dumps(d["errors"])[:600])
    sys.exit(0)

print("LATEST BUILDS:")
for b in d.get("data", []):
    a = b["attributes"]
    print(" -", a.get("shortVersion"), "(" + str(a.get("buildNumber")) + ")",
          "| processing:", a.get("processingState"),
          "| buildState:", a.get("buildState"),
          "| exportCompliance:", a.get("exportComplianceState"),
          "| uploaded:", a.get("uploadedDate"))
print("TOTAL:", d.get("meta", {}).get("paging", {}).get("total"))
