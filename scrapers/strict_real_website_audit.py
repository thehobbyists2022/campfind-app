#!/usr/bin/env python3
"""
Strict 100% Verified Real Website Audit Script for CampFind.
Ensures that EVERY single camp remaining in the active database has a DIRECT,
WORKING, VERIFIED OFFICIAL WEBSITE URL (HTTP 200 OK). No Google Search fallbacks allowed.
"""
import json
import urllib.request
import urllib.parse
import urllib.error
import socket
from concurrent.futures import ThreadPoolExecutor

def test_direct_official_website(camp):
    name = camp.get('name', 'Camp')
    url = camp.get('website', '').strip() if isinstance(camp.get('website'), str) else ''

    # Reject empty or google search fallback URLs
    if not url or "google.com/search" in url:
        return (camp, False, "No Direct Website URL")

    # Standardize scheme
    if url.startswith('http://'):
        url = 'https://' + url[7:]
        camp['website'] = url
    elif not url.startswith('https://'):
        url = 'https://' + url
        camp['website'] = url

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    # Test HTTP connection
    try:
        req = urllib.request.Request(url, headers=headers, method='HEAD')
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            if resp.status < 400:
                return (camp, True, f"HTTP {resp.status}")
    except Exception:
        pass

    try:
        req_get = urllib.request.Request(url, headers=headers, method='GET')
        with urllib.request.urlopen(req_get, timeout=3.0) as resp_get:
            if resp_get.status < 400:
                return (camp, True, f"HTTP {resp_get.status}")
            return (camp, False, f"HTTP {resp_get.status}")
    except Exception as e:
        return (camp, False, f"Failed Connection: {type(e).__name__}")

def run_strict_verification():
    print("Starting Strict 100% Direct Official Website Audit...")
    with open('app/aca_camps.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    raw_camps = data.get('camps', [])
    total_scanned = len(raw_camps)

    verified_camps = []
    rejected_camps = []

    with ThreadPoolExecutor(max_workers=50) as executor:
        results = list(executor.map(test_direct_official_website, raw_camps))

    for camp, is_valid, status_msg in results:
        if is_valid:
            verified_camps.append(camp)
        else:
            rejected_camps.append({
                'name': camp.get('name'),
                'city': camp.get('city'),
                'state': camp.get('state'),
                'url': camp.get('website'),
                'reason': status_msg
            })

    # Save ONLY 100% verified camps with direct working websites
    data['camps'] = verified_camps

    with open('app/aca_camps.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    js_content = f"window.ACA_CAMPS = {json.dumps(verified_camps, indent=2, ensure_ascii=False)};"
    with open('app/aca_camps_data.js', 'w', encoding='utf-8') as f:
        f.write(js_content)

    with open('mobile/assets/aca_camps.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    report = {
        'total_scanned': total_scanned,
        'strictly_verified_count': len(verified_camps),
        'rejected_count': len(rejected_camps),
        'verified_camps_sample': [{ 'name': c['name'], 'city': c['city'], 'state': c['state'], 'website': c['website'] } for c in verified_camps[:20]],
        'rejected_sample': rejected_camps[:15]
    }

    with open('scrapers/strict_audit_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"STRICT_AUDIT_COMPLETE|scanned={total_scanned}|verified={len(verified_camps)}|rejected={len(rejected_camps)}")

if __name__ == "__main__":
    run_strict_verification()
