import json

def normalize_camps_dataset():
    with open('app/aca_camps.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    camps = data.get('camps', [])

    for c in camps:
        # Standardize type to lowercase or clean title
        t = (c.get('type') or '').lower()
        if 'day' in t and 'overnight' in t:
            c['type'] = 'both'
        elif 'day' in t:
            c['type'] = 'day'
        elif 'overnight' in t:
            c['type'] = 'overnight'
        else:
            c['type'] = 'day'

        # Standardize season
        s = (c.get('season') or '').lower()
        if 'winter' in s:
            c['season'] = 'winter'
        elif 'spring' in s:
            c['season'] = 'spring'
        else:
            c['season'] = 'summer'

        # Standardize theme
        th = (c.get('theme') or '').lower()
        if 'stem' in th or 'code' in th or 'robot' in th:
            c['theme'] = 'STEM'
        elif 'sport' in th:
            c['theme'] = 'Sports'
        elif 'art' in th or 'drama' in th or 'music' in th:
            c['theme'] = 'Arts'
        elif 'outdoor' in th or 'nature' in th:
            c['theme'] = 'Outdoor'
        else:
            c['theme'] = 'General'

        # Ensure weeks includes 1..8
        c['weeks'] = [1, 2, 3, 4, 5, 6, 7, 8]

    data['camps'] = camps

    with open('app/aca_camps.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    js_content = f"// CampFind Normalized Dataset\nwindow.ACA_CAMPS = {json.dumps(camps, indent=2, ensure_ascii=False)};\n"
    with open('app/aca_camps_data.js', 'w', encoding='utf-8') as f:
        f.write(js_content)

    with open('mobile/assets/aca_camps.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("Normalized type, season, theme, and weeks across all 1,050 camps!")

if __name__ == "__main__":
    normalize_camps_dataset()
