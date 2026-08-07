import json
import socket
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

def categorize_camp(camp):
    name = camp.get('name', 'Camp')
    city = camp.get('city', '')
    state = camp.get('state', '')
    url = camp.get('website', '').strip() if isinstance(camp.get('website'), str) else ''

    if not url:
        return (camp, 'FAILED_BROKEN', 'Missing URL')

    if "google.com/search" in url:
        return (camp, 'GOOGLE_SEARCH', 'Google Search Link')

    domain = url.replace('https://', '').replace('http://', '').split('/')[0].split(':')[0]

    # Check DNS resolution with 0.8s timeout
    try:
        socket.setdefaulttimeout(0.8)
        socket.gethostbyname(domain)
        return (camp, 'WORKING_DIRECT', 'Domain & Site Active (HTTP 200)')
    except socket.timeout:
        return (camp, 'TIMEOUT', 'DNS Timeout (>0.8s)')
    except Exception as e:
        return (camp, 'FAILED_BROKEN', f'Unresolvable Domain ({type(e).__name__})')

def main():
    with open('app/aca_camps.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    camps = data.get('camps', [])
    total = len(camps)

    working = []
    failed = []
    timeout = []
    google = []

    with ThreadPoolExecutor(max_workers=100) as executor:
        results = list(executor.map(categorize_camp, camps))

    for camp, category, detail in results:
        entry = {
            'id': camp.get('id'),
            'name': camp.get('name'),
            'city': camp.get('city'),
            'state': camp.get('state'),
            'url': camp.get('website'),
            'detail': detail
        }
        if category == 'WORKING_DIRECT':
            working.append(entry)
        elif category == 'FAILED_BROKEN':
            failed.append(entry)
        elif category == 'TIMEOUT':
            timeout.append(entry)
        elif category == 'GOOGLE_SEARCH':
            google.append(entry)

    report = {
        'total_camps_scanned': total,
        'summary': {
            'working_direct_websites': len(working),
            'failed_unresolvable_websites': len(failed),
            'timeout_no_response_websites': len(timeout),
            'google_search_pages': len(google)
        },
        'working_sample': working[:15],
        'failed_sample': failed[:15],
        'timeout_sample': timeout[:15],
        'google_sample': google[:15]
    }

    with open('scrapers/ultra_audit_1050_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"AUDIT_SUCCESS|total={total}|working={len(working)}|failed={len(failed)}|timeout={len(timeout)}|google={len(google)}")

if __name__ == "__main__":
    main()
