#!/usr/bin/env python3
"""
Enhance Camp Titles for Maximum Clarity in Comparison Table.
Appends explicit distinction badges (e.g., Day Camp vs Overnight, Shuttle vs Standard)
so every entry in the side-by-side comparison has a clear, unique, intuitive title!
"""
import json

def enhance_titles():
    with open('app/aca_camps.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    camps = data.get('camps', [])
    seen_titles = {}

    for c in camps:
        raw_name = c.get('name', 'Summer Camp')
        
        # Clean up repeated words like 'Summer Camp Summer Camp'
        clean_name = raw_name.replace("Summer Camp Summer Camp", "Summer Camp").replace("Lab Adventure & STEM Camp", "STEM Academy")

        ctype = (c.get('type') or 'Day Camp').capitalize()
        shuttle_str = " (w/ Shuttle Bus)" if c.get('shuttle') else ""

        # Make unique and descriptive title if duplicates exist
        key = f"{clean_name}_{c.get('city')}"
        if key not in seen_titles:
            seen_titles[key] = 1
            c['name'] = clean_name
        else:
            seen_titles[key] += 1
            idx = seen_titles[key]
            if ctype == 'Overnight':
                c['name'] = f"{clean_name} - Overnight Resident Program"
            elif c.get('shuttle'):
                c['name'] = f"{clean_name} - Day Camp (Shuttle Included)"
            elif c.get('price', 0) < 550:
                c['name'] = f"{clean_name} - Economy Day Program"
            else:
                c['name'] = f"{clean_name} - Track {idx}"

    data['camps'] = camps

    with open('app/aca_camps.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    js_content = f"// CampFind Enhanced Title Dataset\nwindow.ACA_CAMPS = {json.dumps(camps, indent=2, ensure_ascii=False)};\n"
    with open('app/aca_camps_data.js', 'w', encoding='utf-8') as f:
        f.write(js_content)

    with open('mobile/assets/aca_camps.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print("Successfully enhanced camp titles for side-by-side comparison clarity!")

if __name__ == "__main__":
    enhance_titles()
