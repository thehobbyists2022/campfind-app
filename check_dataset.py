import json
import re

with open('app/aca_camps_data.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Find window.ACA_CAMPS = [...]
match = re.search(r'window\.ACA_CAMPS\s*=\s*(\[.*\])', content, re.DOTALL)
if match:
    json_str = match.group(1)
    camps = json.loads(json_str)
    print(f"Total Camps Loaded: {len(camps)}")

    ca_camps = [c for c in camps if c.get('state') == 'CA']
    print(f"Total CA Camps: {len(ca_camps)}")

    zip_92056_camps = [c for c in camps if '92056' in str(c.get('zip', '')) or '920' in str(c.get('zip', '')) or 'Oceanside' in str(c.get('city', ''))]
    print(f"Exact 92056 / 920 / Oceanside Camps: {len(zip_92056_camps)}")

    zips = [c.get('zip', '') for c in ca_camps]
    print("\nSample CA ZIPs in dataset:", zips[:15])
else:
    print("Could not find window.ACA_CAMPS array")
