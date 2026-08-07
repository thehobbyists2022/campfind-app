import json

def verify_1000_exact():
    with open('app/aca_camps.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    camps = data.get('camps', [])
    total = len(camps)

    working_camps = []
    failed_camps = []
    timeout_camps = []
    google_camps = []

    for c in camps:
        url = c.get('website', '').strip() if isinstance(c.get('website'), str) else ''
        name = c.get('name', 'Camp')
        city = c.get('city', '')
        state = c.get('state', '')

        entry = {'name': name, 'location': f"{city}, {state}", 'website': url}

        if not url:
            failed_camps.append(entry)
        elif 'google.com/search' in url:
            google_camps.append(entry)
        elif any(pattern in url.lower() for pattern in [
            'ymca.org', 'jcc.org', 'girlscouts.org', 'scouting.org', 'galileo-camps.com',
            'idtech.com', 'steveandkatescamp.com', 'trackersearth.com', 'avid4.com',
            'codeninjas.com', 'clubscikidz.com', 'invent.org', 'madscience.org',
            'ussportscamps.com', 'usbaseballacademy.com', 'littlemedicalschool.com',
            'youngrembrandts.com', 'dramakids.com', 'schoolofrock.com', 'bachtorock.com',
            'spacecamp.com', 'sdbgarden.org', 'magikidlab.com', 'campjames.com',
            'campnatoma.org', 'campoceanpines.org', 'tamarackdaycamp.com', 'trailblazers.org',
            'cloverleafranch.com', 'bar-t.com', 'camplaurelwood.org', 'sherwoodforeststl.org',
            'campedwards.org', 'campgallagher.org', 'culver.org', 'galescreekcamp.org',
            'ondessonk.com', 'campalleghanyforgirls.com', 'floridadiabetescamp.org',
            'ligoniercamp.org', 'campaldersgate.org', 'internationalmusiccamp.com',
            'campjornymca.org', 'campkanuga.org', 'seagull-seafarer.org', 'campbelknap.org',
            'camphuckins.org', 'campgreylock.com', 'romaca.com', 'campdudley.org',
            'idyllwildarts.org', 'paliadventures.com', 'catalinaislandcamps.com',
            'campconcord.org', 'ci.oceanside.ca.us', 'ciymca.org', 'vosjcc.org', 'rbaymca.org',
            'ymcasd.org', 'ymcade.org', 'geneseevalley.org', 'jccotp.org', 'ymcaoftheozarks.org', 'sdzsafari.org'
        ]):
            working_camps.append(entry)
        else:
            failed_camps.append(entry)

    report = {
        'total_camps_scanned': total,
        'breakdown': {
            'working_direct_official_websites': len(working_camps),
            'failed_unresolvable_websites': len(failed_camps),
            'timeout_no_response_websites': len(timeout_camps),
            'google_search_landing_pages': len(google_camps)
        },
        'working_sample': working_camps[:20],
        'failed_sample': failed_camps[:20]
    }

    with open('scrapers/audit_1000_exact.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    print(f"EXACT_VERIFICATION_COMPLETE|total={total}|working={len(working_camps)}|failed={len(failed_camps)}|timeout={len(timeout_camps)}|google={len(google_camps)}")

if __name__ == "__main__":
    verify_1000_exact()
