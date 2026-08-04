import json
import socket
import urllib.parse

def run_super_fast_audit():
    with open('app/aca_camps.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    camps = data.get('camps', [])
    total = len(camps)

    dead_links = []
    working_count = 0

    socket.setdefaulttimeout(0.3)

    for c in camps:
        url = c.get('website', '').strip() if isinstance(c.get('website'), str) else ''
        name = c.get('name', 'Camp')
        city = c.get('city', '')
        state = c.get('state', '')

        if not url:
            is_valid = False
            reason = "Missing URL"
        elif "google.com/search" in url:
            is_valid = True
            working_count += 1
            continue
        else:
            domain = url.replace("https://", "").replace("http://", "").split("/")[0].split(":")[0]
            try:
                socket.gethostbyname(domain)
                is_valid = True
                working_count += 1
            except Exception as e:
                is_valid = False
                reason = f"Unresolvable Domain ({domain})"

        if not is_valid:
            query = urllib.parse.quote(f"{name} {city} {state} summer camp official site")
            fallback_url = f"https://www.google.com/search?q={query}"

            dead_links.append({
                'id': c.get('id'),
                'name': name,
                'location': f"{city}, {state}",
                'original_url': url,
                'reason': reason,
                'fixed_url': fallback_url
            })
            c['website'] = fallback_url

    # Save fixed datasets
    with open('app/aca_camps.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    js_content = f"window.ACA_CAMPS = {json.dumps(data['camps'], indent=2, ensure_ascii=False)};"
    with open('app/aca_camps_data.js', 'w', encoding='utf-8') as f:
        f.write(js_content)

    report = {
        'total_camps': total,
        'working_websites': working_count,
        'dead_websites_found': len(dead_links),
        'dead_links': dead_links
    }

    with open('scrapers/audit_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"DONE! Total: {total}, Working: {working_count}, Dead/Fixed: {len(dead_links)}")

if __name__ == "__main__":
    run_super_fast_audit()
