#!/usr/bin/env python3
"""
Live HTTP Verification Audit for 1,000 Genuine Real US Camps.
Tests every single camp URL for live HTTP connection.
"""
import json
import urllib.request
import urllib.parse
import urllib.error
import socket
from concurrent.futures import ThreadPoolExecutor

def test_single_url(camp):
    url = camp.get('website', '').strip()
    name = camp.get('name', 'Camp')
    
    if not url or "google.com/search" in url:
        return (camp, "GOOGLE_SEARCH", "Google Search Link")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        req = urllib.request.Request(url, headers=headers, method='HEAD')
        with urllib.request.urlopen(req, timeout=3.0) as resp:
            if resp.status < 400:
                return (camp, "WORKING_DIRECT", f"HTTP {resp.status} OK")
    except Exception:
        pass

    try:
        req_get = urllib.request.Request(url, headers=headers, method='GET')
        with urllib.request.urlopen(req_get, timeout=3.0) as resp_get:
            if resp_get.status < 400:
                return (camp, "WORKING_DIRECT", f"HTTP {resp_get.status} OK")
            return (camp, "FAILED_BROKEN", f"HTTP {resp_get.status}")
    except socket.timeout:
        return (camp, "TIMEOUT", "Timeout (>3.0s)")
    except Exception as e:
        return (camp, "FAILED_BROKEN", str(e))

def main():
    print("Testing all 1,000 real camps with live HTTP requests across 50 threads...")
    with open('app/aca_camps.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    camps = data.get('camps', [])
    total = len(camps)

    working = []
    failed = []
    timeout = []
    google = []

    with ThreadPoolExecutor(max_workers=50) as executor:
        results = list(executor.map(test_single_url, camps))

    for camp, status, msg in results:
        entry = {
            'id': camp.get('id'),
            'name': camp.get('name'),
            'city': camp.get('city'),
            'state': camp.get('state'),
            'url': camp.get('website'),
            'status': msg
        }
        if status == "WORKING_DIRECT":
            working.append(entry)
        elif status == "FAILED_BROKEN":
            failed.append(entry)
        elif status == "TIMEOUT":
            timeout.append(entry)
        elif status == "GOOGLE_SEARCH":
            google.append(entry)

    report = {
        'total_camps_tested': total,
        'summary': {
            'working_direct_official_websites': len(working),
            'failed_broken_websites': len(failed),
            'timeout_no_response_websites': len(timeout),
            'google_search_pages': len(google)
        },
        'working_sample': working[:20],
        'failed_sample': failed[:20]
    }

    with open('scrapers/final_1000_audit_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"\n========================================================")
    print(f"LIVE 1,000 AUDIT COMPLETE:")
    print(f"  🟢 1. Working Direct Official Websites: {len(working)} ({round(len(working)/total*100, 1)}%)")
    print(f"  🔴 2. Failed / Broken Websites:        {len(failed)} ({round(len(failed)/total*100, 1)}%)")
    print(f"  🟡 3. Timeout / No Response:          {len(timeout)} ({round(len(timeout)/total*100, 1)}%)")
    print(f"  🔍 4. Google Search Landing Pages:    {len(google)} ({round(len(google)/total*100, 1)}%)")
    print(f"========================================================\n")

if __name__ == "__main__":
    main()
