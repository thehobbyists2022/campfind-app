import csv
from collections import defaultdict

def dump_breakdown():
    with open('campfind_camps_enriched.csv', 'r', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))

    missing = [r for r in rows if not r.get('Weekly Price USD (每週費用)', '').strip()]
    
    with open('scrapers/missing_camps_breakdown.txt', 'w', encoding='utf-8') as out:
        out.write(f"Total missing: {len(missing)}\n\n")

        # City Camps
        city_camps = [r for r in missing if r.get('Provider / Brand (主辦品牌)', '').strip() == 'city']
        out.write(f"=== CITY CAMPS ({len(city_camps)}) ===\n")
        by_state = defaultdict(list)
        for r in city_camps:
            by_state[r.get('State (州別)', 'Unknown')].append(r)
        
        for st in sorted(by_state.keys()):
            out.write(f"\n--- State: {st} ({len(by_state[st])} camps) ---\n")
            for c in by_state[st]:
                out.write(f"ID {c.get('Camp ID (編號)')} | {c.get('City (城市)')} | {c.get('Camp Name (營隊名稱)')} | {c.get('Official Website (官方網站)')} | Phone: {c.get('Phone (聯絡電話)')}\n")

        # ACA Camps
        aca_camps = [r for r in missing if r.get('Provider / Brand (主辦品牌)', '').strip() == 'aca']
        out.write(f"\n\n=== ACA CAMPS ({len(aca_camps)}) ===\n")
        aca_by_state = defaultdict(list)
        for r in aca_camps:
            aca_by_state[r.get('State (州別)', 'Unknown')].append(r)
        
        for st in sorted(aca_by_state.keys()):
            out.write(f"\n--- State: {st} ({len(aca_by_state[st])} camps) ---\n")
            for c in aca_by_state[st]:
                out.write(f"ID {c.get('Camp ID (編號)')} | {c.get('City (城市)')} | {c.get('Camp Name (營隊名稱)')} | {c.get('Official Website (官方網站)')} | Phone: {c.get('Phone (聯絡電話)')}\n")

        # Other Camps
        others = [r for r in missing if r.get('Provider / Brand (主辦品牌)', '').strip() not in ('city', 'aca')]
        out.write(f"\n\n=== OTHER INDEPENDENT CAMPS ({len(others)}) ===\n")
        for c in others:
            out.write(f"ID {c.get('Camp ID (編號)')} | [{c.get('State (州別)')}] {c.get('City (城市)')} | {c.get('Camp Name (營隊名稱)')} | {c.get('Official Website (官方網站)')} | Phone: {c.get('Phone (聯絡電話)')}\n")

if __name__ == '__main__':
    dump_breakdown()
    print("Exported to scrapers/missing_camps_breakdown.txt")
