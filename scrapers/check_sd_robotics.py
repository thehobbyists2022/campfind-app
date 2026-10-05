import csv
import sys

def check_sd():
    with open('campfind_camps_enriched.csv', 'r', encoding='utf-8-sig') as f:
        rows = list(csv.DictReader(f))

    sd_cities = ['san diego', 'oceanside', 'la jolla', 'carlsbad', 'chula vista', 'poway', 'escondido', 'encinitas', 'san marcos', 'sorrento valley', 'del mar']

    matches = []
    for r in rows:
        city = r.get('City (城市)', '').lower()
        st = r.get('State (州別)', '').strip().upper()
        if st == 'CA' and any(k in city for k in sd_cities):
            matches.append(r)

    print(f"Total camps in San Diego County in CSV: {len(matches)}")

    robot_camps = []
    for r in matches:
        text = f"{r.get('Camp Name (營隊名稱)', '')} {r.get('Description (營隊簡介)', '')} {r.get('Theme (主題類型)', '')} {r.get('Provider / Brand (主辦品牌)', '')}".lower()
        if 'robot' in text:
            robot_camps.append(r)

    print(f"\nCamps explicitly mentioning 'robot' in SD county: {len(robot_camps)}")
    for r in robot_camps:
        print(f"  - [{r.get('City (城市)')}] {r.get('Camp Name (營隊名稱)')} | Brand: {r.get('Provider / Brand (主辦品牌)')} | Theme: {r.get('Theme (主題類型)')} | ID: {r.get('Camp ID (編號)')}")

    # STEM / Tech camps
    tech_camps = []
    for r in matches:
        text = f"{r.get('Camp Name (營隊名稱)', '')} {r.get('Description (營隊簡介)', '')} {r.get('Theme (主題類型)', '')} {r.get('Provider / Brand (主辦品牌)', '')}".lower()
        if any(k in text for k in ['code', 'stem', 'tech', 'science', 'lego', 'snapology']):
            tech_camps.append(r)

    print(f"\nCamps with STEM / Coding / Tech in SD county: {len(tech_camps)}")
    for r in tech_camps:
        print(f"  - [{r.get('City (城市)')}] {r.get('Camp Name (營隊名稱)')} | Brand: {r.get('Provider / Brand (主辦品牌)')} | Theme: {r.get('Theme (主題類型)')} | ID: {r.get('Camp ID (編號)')}")

if __name__ == '__main__':
    check_sd()
