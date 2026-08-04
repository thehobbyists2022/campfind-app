import json

with open('app/aca_camps.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

camps = data.get('camps', [])

for zip_code in ['91910', '91911', '91913', '919']:
    matches = [c for c in camps if c.get('zip', '').startswith(zip_code)]
    print(f"\nZIP {zip_code} Camps count: {len(matches)}")
    for idx, c in enumerate(matches, 1):
        print(f"  {idx}. {c['name']} ({c['city']}, {c['state']} {c['zip']}) -> {c['website']}")
