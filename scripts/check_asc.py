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
res = subprocess.run(["curl", "-g", "-sS", "-w", "\\nHTTP_CODE:%{http_code}", "-H", f"Authorization: Bearer {jwt}", url], capture_output=True, text=True)
print("CURL_STDOUT_BYTES:", len(res.stdout))
print("CURL_STDERR:", res.stderr[:300])
try:
    lines = res.stdout.split("\n")
    body = "\n".join(lines[:-1])
    code_line = lines[-1]
    d = json.loads(body)
except Exception as e:
    print("RAW_RESPONSE:", res.stdout[:800])
    print("PARSE_ERROR:", e)
    sys.exit(1)
print("HTTP:", code_line) if code_line.startswith("HTTP_CODE:") else None
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
