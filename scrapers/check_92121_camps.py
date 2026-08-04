import json

with open('app/aca_camps.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

camps = data.get('camps', [])

camps_92121 = [c for c in camps if c.get('zip', '').startswith('92121')]
camps_921 = [c for c in camps if c.get('zip', '').startswith('921')]

print(f"Exact 92121 Camps count: {len(camps_92121)}")
for idx, c in enumerate(camps_92121, 1):
    print(f"  {idx}. {c['name']} ({c['city']}, {c['state']} {c['zip']})")

print(f"\nLocal 921xx (San Diego Area) Camps count: {len(camps_921)}")
for idx, c in enumerate(camps_921, 1):
    print(f"  {idx}. {c['name']} ({c['city']}, {c['state']} {c['zip']})")
