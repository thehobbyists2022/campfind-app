#!/usr/bin/env python3
import json
import socket
import urllib.parse
from concurrent.futures import ThreadPoolExecutor

def check_domain(camp):
    url = camp.get('website', '').strip() if isinstance(camp.get('website'), str) else ''
    name = camp.get('name', 'Camp')
    city = camp.get('city', '')
    state = camp.get('state', '')

    if not url or "google.com/search" in url:
        return (camp, True, "OK")

    clean_url = url.replace("https://", "").replace("http://", "").split("/")[0].split(":")[0]

    try:
        # Fast DNS lookup with 1.2 second timeout
        socket.setdefaulttimeout(1.2)
        socket.gethostbyname(clean_url)
        return (camp, True, "OK")
    except Exception as e:
        return (camp, False, f"DNS / Domain Unresolvable ({type(e).__name__})")

def main():
    with open('app/aca_camps.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    camps = data.get('camps', [])
    total = len(camps)

    dead_camps = []
    working_count = 0

    with ThreadPoolExecutor(max_workers=100) as executor:
        results = list(executor.map(check_domain, camps))

    for camp, is_valid, reason in results:
        if is_valid:
            working_count += 1
        else:
            name = camp.get('name', 'Camp')
            city = camp.get('city', '')
            state = camp.get('state', '')
            orig_url = camp.get('website', '')
            query = urllib.parse.quote(f"{name} {city} {state} summer camp official site")
            fallback_url = f"https://www.google.com/search?q={query}"

            dead_camps.append({
                'id': camp.get('id'),
                'name': name,
                'location': f"{city}, {state}",
                'original_url': orig_url,
                'reason': reason,
                'replaced_with': fallback_url
            })
            # Apply instant auto-fix to dataset
            camp['website'] = fallback_url

    # Save fixed dataset
    with open('app/aca_camps.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    js_content = f"window.ACA_CAMPS = {json.dumps(data['camps'], indent=2, ensure_ascii=False)};"
    with open('app/aca_camps_data.js', 'w', encoding='utf-8') as f:
        f.write(js_content)

    report = {
        'total_camps_scanned': total,
        'working_websites': working_count,
        'dead_websites_found': len(dead_camps),
        'dead_websites_details': dead_camps
    }

    with open('scrapers/audit_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"AUDIT_COMPLETE|total={total}|working={working_count}|dead={len(dead_camps)}")

if __name__ == "__main__":
    main()
