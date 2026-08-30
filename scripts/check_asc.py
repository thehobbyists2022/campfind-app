#!/usr/bin/env python3
import os, json, sys, time, subprocess

key_id = os.environ["ASC_KEY_ID"]
issuer = os.environ["ASC_ISSUER_ID"]
key = os.environ["ASC_KEY"].replace("\\n", "\n")

with open("authkey.p8", "w") as f:
    f.write(key)

def b64url(b):
    import base64
    return base64.urlsafe_b64encode(b).rstrip(b"=").decode()

header = b64url(json.dumps({"alg": "ES256", "kid": key_id, "typ": "JWT"}).encode())
payload = b64url(json.dumps({"iss": issuer, "iat": int(time.time()), "exp": int(time.time()) + 1200, "aud": "appstoreconnect-v1"}).encode())
signing_input = f"{header}.{payload}"
sig = subprocess.run(
    ["openssl", "dgst", "-sha256", "-sign", "authkey.p8", "-binary"],
    input=signing_input.encode(), capture_output=True)
sig = b64url(sig.stdout)
jwt = f"{signing_input}.{sig}"

url = "https://api.appstoreconnect.apple.com/v1/builds?sort=-uploadedDate&limit=10&fields[build]=version,shortVersion,buildNumber,uploadedDate,processingState,exportComplianceState,buildState"
res = subprocess.run(["curl", "-sS", "-H", f"Authorization: Bearer {jwt}", url], capture_output=True, text=True)
d = json.loads(res.stdout)
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
