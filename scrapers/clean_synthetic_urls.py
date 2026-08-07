#!/usr/bin/env python3
import json
import urllib.parse

# 1. Update aca_camps.json
with open('app/aca_camps.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

synthetic_domains = [
    'adventurelaketahoe.org', 'horizonseattle.org', 'winterwondersdenver.org',
    'example.com', 'testcamp.org', 'localhost'
]

fixed_count = 0
for c in data.get('camps', []):
    url = c.get('website', '')
    name = c.get('name', 'Camp')
    city = c.get('city', '')
    state = c.get('state', '')

    # Check if domain is synthetic or empty or invalid
    if not url or any(domain in url.lower() for domain in synthetic_domains):
        query = urllib.parse.quote(f"{name} {city} {state} summer camp official site")
        c['website'] = f"https://www.google.com/search?q={query}"
        fixed_count += 1

with open('app/aca_camps.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

# 2. Update aca_camps_data.js
js_content = f"window.ACA_CAMPS = {json.dumps(data['camps'], indent=2, ensure_ascii=False)};"
with open('app/aca_camps_data.js', 'w', encoding='utf-8') as f:
    f.write(js_content)

print(f"Cleaned and fixed {fixed_count} synthetic website URLs across dataset.")
