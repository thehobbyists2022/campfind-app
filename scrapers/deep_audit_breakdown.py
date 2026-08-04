#!/usr/bin/env python3
"""
Comprehensive Deep Audit Script for All 1,050 Camp Websites.
Tests DNS resolution, HTTP status, timeouts, and classifies each camp website into 4 distinct categories:
  1. Working Direct Official Website (HTTP 200 OK)
  2. Failed / Unresolvable / Broken Domain (Connection Refused / 404 / 500 / GAIErr)
  3. Timeout / No Response (>2.0s socket timeout)
  4. Google Search Landing Page
"""
import json
import socket
import urllib.request
import urllib.parse
import urllib.error
from concurrent.futures import ThreadPoolExecutor

def test_camp_website_deep(camp):
    name = camp.get('name', 'Camp')
    city = camp.get('city', '')
    state = camp.get('state', '')
    url = camp.get('website', '').strip() if isinstance(camp.get('website'), str) else ''

    if not url:
        return {
            'id': camp.get('id'),
            'name': name,
            'city': city,
            'state': state,
            'url': '(Empty)',
            'category': 'FAILED_BROKEN',
            'detail': 'Missing URL'
        }

    if "google.com/search" in url:
        return {
            'id': camp.get('id'),
            'name': name,
            'city': city,
            'state': state,
            'url': url,
            'category': 'GOOGLE_SEARCH',
            'detail': 'Google Search Fallback'
        }

    # Ensure HTTPS
    if url.startswith('http://'):
        url = 'https://' + url[7:]
    elif not url.startswith('https://'):
        url = 'https://' + url

    domain = url.replace('https://', '').split('/')[0].split(':')[0]

    # Step 1: Fast DNS Lookup
    try:
        socket.setdefaulttimeout(2.0)
        socket.gethostbyname(domain)
    except socket.timeout:
        return {
            'id': camp.get('id'),
            'name': name,
            'city': city,
            'state': state,
            'url': url,
            'category': 'TIMEOUT',
            'detail': 'DNS Timeout (>2.0s)'
        }
    except Exception as e:
        return {
            'id': camp.get('id'),
            'name': name,
            'city': city,
            'state': state,
            'url': url,
            'category': 'FAILED_BROKEN',
            'detail': f"Unresolvable Domain ({type(e).__name__})"
        }

    # Step 2: HTTP Request Check
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        req = urllib.request.Request(url, headers=headers, method='HEAD')
        with urllib.request.urlopen(req, timeout=2.0) as resp:
            if resp.status < 400:
                return {
                    'id': camp.get('id'),
                    'name': name,
                    'city': city,
                    'state': state,
                    'url': url,
                    'category': 'WORKING_DIRECT',
                    'detail': f"HTTP {resp.status} OK"
                }
    except Exception:
        pass

    try:
        req_get = urllib.request.Request(url, headers=headers, method='GET')
        with urllib.request.urlopen(req_get, timeout=2.5) as resp_get:
            if resp_get.status < 400:
                return {
                    'id': camp.get('id'),
                    'name': name,
                    'city': city,
                    'state': state,
                    'url': url,
                    'category': 'WORKING_DIRECT',
                    'detail': f"HTTP {resp_get.status} OK"
                }
            else:
                return {
                    'id': camp.get('id'),
                    'name': name,
                    'city': city,
                    'state': state,
                    'url': url,
                    'category': 'FAILED_BROKEN',
                    'detail': f"HTTP {resp_get.status} Error"
                }
    except socket.timeout:
        return {
            'id': camp.get('id'),
            'name': name,
            'city': city,
            'state': state,
            'url': url,
            'category': 'TIMEOUT',
            'detail': 'HTTP Connection Timeout (>2.5s)'
        }
    except Exception as e:
        return {
            'id': camp.get('id'),
            'name': name,
            'city': city,
            'state': state,
            'url': url,
            'category': 'FAILED_BROKEN',
            'detail': f"Connection Error ({type(e).__name__})"
        }

def run_deep_audit():
    with open('app/aca_camps.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    camps = data.get('camps', [])
    total = len(camps)
    print(f"Executing Deep 1,050 Audit across 50 parallel threads...")

    working_list = []
    failed_list = []
    timeout_list = []
    google_list = []

    with ThreadPoolExecutor(max_workers=50) as executor:
        results = list(executor.map(test_camp_website_deep, camps))

    for item in results:
        cat = item['category']
        if cat == 'WORKING_DIRECT':
            working_list.append(item)
        elif cat == 'FAILED_BROKEN':
            failed_list.append(item)
        elif cat == 'TIMEOUT':
            timeout_list.append(item)
        elif cat == 'GOOGLE_SEARCH':
            google_list.append(item)

    report = {
        'total_camps_scanned': total,
        'summary': {
            'working_direct_websites': len(working_list),
            'failed_broken_websites': len(failed_list),
            'timeout_no_response_websites': len(timeout_list),
            'google_search_fallbacks': len(google_list)
        },
        'working_direct_sample': working_list[:20],
        'failed_sample': failed_list[:20],
        'timeout_sample': timeout_list[:20],
        'google_sample': google_list[:20]
    }

    with open('scrapers/deep_audit_1050_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"DEEP_AUDIT_RESULT|total={total}|working={len(working_list)}|failed={len(failed_list)}|timeout={len(timeout_list)}|google={len(google_list)}")

if __name__ == "__main__":
    run_deep_audit()
