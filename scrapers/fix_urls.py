#!/usr/bin/env python3
import json
import re

# Update aca_camps_data.js
with open('app/aca_camps_data.js', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('"http://', '"https://')

with open('app/aca_camps_data.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated aca_camps_data.js URLs to HTTPS")

# Update aca_camps.json
with open('app/aca_camps.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

for c in data.get('camps', []):
    url = c.get('website', '')
    if url.startswith('http://'):
        c['website'] = 'https://' + url[7:]

with open('app/aca_camps.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print("Updated aca_camps.json URLs to HTTPS")
