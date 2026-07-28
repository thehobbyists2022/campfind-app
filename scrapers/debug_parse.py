#!/usr/bin/env python3
"""Debug: test parse_camp_profile directly."""
import requests, re, sys
sys.path.insert(0, '/root/camp-finder-project')
from importlib import util as importlib_util

spec = importlib_util.spec_from_file_location('crawler', '/root/camp-finder-project/03_aca_crawler_v2.py')
crawler = importlib_util.module_from_spec(spec)
spec.loader.exec_module(crawler)

BASE_URL = 'https://find.acacamps.org'
session = requests.Session()
session.headers.update({'User-Agent': 'Mozilla/5.0'})

# Complete full flow
session.get(BASE_URL, timeout=15)
session.post('https://find.acacamps.org/search.php', 
    data={'search':'search','facets[camp_type]':'day_camp','open[choices-made-section-content]':'true'}, timeout=15)
session.post('https://find.acacamps.org/search_results.php',
    data={'search':'search','facets[camp_type]':'day_camp','save-criteria':'yes-please'}, timeout=15)

# Fetch profile
resp = session.get('https://find.acacamps.org/camp_profile.php?camp_id=5423', timeout=15)
html = resp.text

print(f"HTML length: {len(html)}")
print(f"Has Programs section: {'Programs' in html}")

result = crawler.parse_camp_profile(html, '5423')
print(f"Programs found: {len(result.get('programs', []))}")
for p in result.get('programs', []):
    print(f"  {p.get('name')} - {p.get('type')} - {p.get('cost')}")
print(f"Camp type: {result.get('camp_type')}")
print(f"Name: {result.get('name')}")
print(f"Location: {result.get('city')}, {result.get('state')}")
print(f"Website: {result.get('website')}")
print(f"Phone: {result.get('phone')}")
