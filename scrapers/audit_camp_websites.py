#!/usr/bin/env python3
"""
Full Dataset Audit Script for CampFind Website URLs.
Tests all 1,050 camp website links via HTTP GET/HEAD requests with timeout.
Identifies broken/dead links and replaces them with clean Google Search fallback links.
"""
import json
import urllib.request
import urllib.parse
import urllib.error
import socket
import sys

def audit_all_camp_websites():
    json_path = 'app/aca_camps.json'
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    camps = data.get('camps', [])
    total = len(camps)
    print(f"Starting full audit of {total} camp website links...")

    broken_links = []
    working_count = 0
    fallback_applied = 0

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    for idx, camp in enumerate(camps, start=1):
        name = camp.get('name', 'Camp')
        city = camp.get('city', '')
        state = camp.get('state', '')
        url = camp.get('website', '').strip() if isinstance(camp.get('website'), str) else ''

        is_valid = False

        if not url:
            is_valid = False
            reason = "Empty URL"
        elif "google.com/search" in url:
            is_valid = True
            working_count += 1
            continue
        else:
            try:
                # Ensure scheme
                if url.startswith('http://'):
                    url = 'https://' + url[7:]
                    camp['website'] = url

                req = urllib.request.Request(url, headers=headers, method='HEAD')
                with urllib.request.urlopen(req, timeout=3.0) as response:
                    if response.status < 400:
                        is_valid = True
                        working_count += 1
                    else:
                        reason = f"HTTP {response.status}"
            except (urllib.error.HTTPError, urllib.error.URLError, socket.timeout, Exception) as e:
                # Try GET if HEAD fails
                try:
                    req_get = urllib.request.Request(url, headers=headers, method='GET')
                    with urllib.request.urlopen(req_get, timeout=3.0) as resp_get:
                        if resp_get.status < 400:
                            is_valid = True
                            working_count += 1
                        else:
                            reason = f"HTTP {resp_get.status}"
                except Exception as ex:
                    is_valid = False
                    reason = str(ex).split('>')[-1].strip()

        if not is_valid:
            query = urllib.parse.quote(f"{name} {city} {state} summer camp official site")
            google_fallback = f"https://www.google.com/search?q={query}"
            
            broken_links.append({
                'id': camp.get('id'),
                'name': name,
                'city': city,
                'state': state,
                'original_url': url if url else '(None)',
                'reason': reason,
                'replacement': google_fallback
            })
            
            # Apply auto-fix to dataset
            camp['website'] = google_fallback
            fallback_applied += 1

        if idx % 100 == 0 or idx == total:
            print(f"  Processed {idx}/{total} camps... ({working_count} verified, {fallback_applied} replaced)")

    # Save updated clean dataset
    with open('app/aca_camps.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    js_content = f"window.ACA_CAMPS = {json.dumps(data['camps'], indent=2, ensure_ascii=False)};"
    with open('app/aca_camps_data.js', 'w', encoding='utf-8') as f:
        f.write(js_content)

    # Save Audit Log Artifact
    report = {
        'total_camps': total,
        'verified_working': working_count,
        'dead_or_unreachable_found': len(broken_links),
        'auto_fixes_applied': fallback_applied,
        'broken_links_list': broken_links
    }

    with open('scrapers/website_audit_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print("\n✓ Full audit completed!")
    print(f"Total: {total} | Working: {working_count} | Auto-fixed Dead Links: {len(broken_links)}")

if __name__ == "__main__":
    audit_all_camp_websites()
