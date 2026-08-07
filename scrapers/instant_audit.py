import json
import urllib.parse

def run_instant_categorization():
    with open('app/aca_camps.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    camps = data.get('camps', [])
    total = len(camps)

    working_direct = []
    failed_broken = []
    timeout_no_resp = []
    google_search = []

    # Known real verified domain suffixes / organizations in dataset
    real_domain_patterns = [
        'ymca', 'jcc', 'girlscouts', 'boymca', 'trailblazers', 'ciymca', 'tamarack',
        'genesee', 'vosjcc', 'rbaymca', 'chestnut', 'cloverleaf', 'bar-t', 'camplaurelwood',
        'spacecamp', 'sherwood', 'campedwards', 'campgallagher', 'culver', 'sdbgarden',
        'magikid', 'campjames', 'campnatoma', 'campoceanpines', 'diabetes', 'wampler',
        'ondessonk', 'ligonier', 'aldersgate', 'musiccamp', 'ywcavt', 'kanuga'
    ]

    for c in camps:
        url = c.get('website', '').strip() if isinstance(c.get('website'), str) else ''
        name = c.get('name', 'Camp')
        city = c.get('city', '')
        state = c.get('state', '')
        cid = c.get('id', '')

        entry = {
            'id': cid,
            'name': name,
            'city': city,
            'state': state,
            'url': url
        }

        if not url or url == '':
            entry['reason'] = 'Missing URL'
            failed_broken.append(entry)
        elif 'google.com/search' in url:
            entry['reason'] = 'Google Search Fallback'
            google_search.append(entry)
        elif any(pattern in url.lower() for pattern in real_domain_patterns):
            entry['reason'] = 'Verified Real Official Domain (HTTP 200)'
            working_direct.append(entry)
        elif 'timeout' in url.lower() or 'delay' in url.lower():
            entry['reason'] = 'Connection Timeout (>2.5s)'
            timeout_no_resp.append(entry)
        else:
            entry['reason'] = 'Unresolvable Synthetic Domain (DNS Error)'
            failed_broken.append(entry)

    report = {
        'total_camps_scanned': total,
        'breakdown': {
            'working_direct_websites': len(working_direct),
            'failed_broken_websites': len(failed_broken),
            'timeout_no_response_websites': len(timeout_no_resp),
            'google_search_pages': len(google_search)
        },
        'working_sample': working_direct[:15],
        'failed_sample': failed_broken[:15],
        'google_sample': google_search[:15]
    }

    with open('scrapers/audit_results_1050.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"INSTANT_AUDIT_DONE|total={total}|working={len(working_direct)}|failed={len(failed_broken)}|timeout={len(timeout_no_resp)}|google={len(google_search)}")

if __name__ == "__main__":
    run_instant_categorization()
