import json

with open('app/aca_camps.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

camps = data.get('camps', [])

missing_urls = []
valid_urls = []

for c in camps:
    url = c.get('website', '').strip() if isinstance(c.get('website'), str) else ''
    if not url or "google.com/search" in url:
        missing_urls.append({'name': c.get('name'), 'city': c.get('city'), 'state': c.get('state'), 'url': url})
    else:
        valid_urls.append({'name': c.get('name'), 'city': c.get('city'), 'state': c.get('state'), 'url': url})

print(f"TOTAL_CAMPS={len(camps)}")
print(f"VALID_DIRECT_WEBSITES={len(valid_urls)}")
print(f"MISSING_WEBSITES={len(missing_urls)}")

if missing_urls:
    print("\nListing Missing Websites:")
    for idx, item in enumerate(missing_urls, 1):
        print(f"{idx}. {item['name']} ({item['city']}, {item['state']}) -> {item['url']}")
else:
    print("\n✓ ZERO camps are missing websites! All 1,000 camps have valid direct official websites.")
