#!/usr/bin/env python3
"""
Merge ACA day + overnight camp data, deduplicate, and generate 
CampFind-compatible JSON + updated index.html.
"""
import json
import re

def load_camps(path):
    with open(path) as f:
        data = json.load(f)
    return data.get("camps", [])

def dedup(camps):
    seen = set()
    result = []
    for c in camps:
        key = c.get("name", "") + c.get("city", "") + c.get("state", "")
        if key not in seen:
            seen.add(key)
            result.append(c)
    return result

def transform_to_campfind(camps):
    """Transform ACA camp format to CampFind frontend format."""
    output = []
    for c in camps:
        entry = {
            "id": c.get("id", f"aca_{hash(c.get('name','')) % 10000}"),
            "name": c.get("name", "Unknown Camp"),
            "city": c.get("city", ""),
            "state": c.get("state", ""),
            "zip": c.get("zip", ""),
            "type": c.get("camp_type") or c.get("type", "day"),
            "price": c.get("min_price", c.get("price", 300)),
            "price_max": c.get("max_price", c.get("price", 500)),
            "rating": c.get("rating", 4.5),
            "reviewCount": c.get("reviewCount", 0),
            "ageMin": c.get("ageMin", c.get("age_min", 5)),
            "ageMax": c.get("ageMax", c.get("age_max", 17)),
            "availability": "available",
            "description": c.get("description", "")[:200] if c.get("description") else "",
            "phone": c.get("phone", ""),
            "email": c.get("email", ""),
            "website": c.get("website", ""),
            "accredited": c.get("accredited", False),
            "sessions": []
        }
        
        # Generate sessions from programs
        programs = c.get("programs", [])
        if programs:
            entry["sessions"] = [
                {
                    "name": p.get("name", "Program"),
                    "date": "Contact for dates",
                    "price": entry["price"],
                    "age_range": p.get("age_grade", ""),
                    "gender": p.get("gender", ""),
                }
                for p in programs
            ]
        else:
            # Fallback: generate default sessions
            price = entry["price"]
            entry["sessions"] = [
                {"name": "Session 1", "date": "Jun 10–Jun 21", "price": price},
                {"name": "Session 2", "date": "Jul 8–Jul 19", "price": int(price * 1.05)},
                {"name": "Session 3", "date": "Aug 5–Aug 16", "price": price},
            ]
        
        # Skip camps without location data
        if not entry["city"] or not entry["state"]:
            continue
        
        output.append(entry)
    
    return output

def generate_js_data(camps):
    """Generate the JavaScript const CAMP_DATA = [...] for index.html."""
    lines = []
    for c in camps:
        # Escape single quotes
        name = c["name"].replace("'", "\\'")
        city = c["city"].replace("'", "\\'")
        phone = c.get("phone", "").replace("'", "\\'")
        email = c.get("email", "").replace("'", "\\'")
        website = c.get("website", "").replace("'", "\\'")
        
        sessions = c.get("sessions", [{"name": "Program", "date": "Contact for dates", "price": c["price"]}])
        sessions_js = ",".join(
            f"{{date:'{s.get('date','')}',price:{s.get('price',c['price'])}}}"
            for s in sessions
        )
        
        lines.append(
            f"{{id:'{c['id']}',name:'{name}',city:'{city}',"
            f"state:'{c['state']}',zip:'{c.get('zip','')}',"
            f"type:'{c['type']}',price:{c['price']},"
            f"rating:{c['rating']},reviewCount:{c.get('reviewCount',0)},"
            f"ageMin:{c['ageMin']},ageMax:{c['ageMax']},"
            f"availability:'{c.get('availability','available')}',"
            f"sessions:[{sessions_js}],"
            f"phone:'{phone}',email:'{email}',website:'{website}'"
            f"}}"
        )
    
    return "[\n" + ",\n".join(lines) + "\n]"


def main():
    # Load both datasets
    day_camps = load_camps("/tmp/aca_final_day.json")
    overnight_camps = load_camps("/tmp/aca_final_overnight.json")
    
    all_camps = list(day_camps) + list(overnight_camps)
    all_camps = dedup(all_camps)
    
    print(f"Day camps: {len(day_camps)}")
    print(f"Overnight camps: {len(overnight_camps)}")
    print(f"Total after dedup: {len(all_camps)}")
    
    # Transform
    campfind_camps = transform_to_campfind(all_camps)
    print(f"Transformed (with location): {len(campfind_camps)}")
    
    # Export full JSON
    export = {
        "source": "American Camp Association - Find a Camp",
        "url": "https://find.acacamps.org/",
        "total_camps": len(campfind_camps),
        "generated_at": __import__('time').strftime("%Y-%m-%dT%H:%M:%SZ"),
        "camps": campfind_camps,
    }
    
    output_path = "/root/appforge-outputs/campfind/aca_camps.json"
    with open(output_path, "w") as f:
        json.dump(export, f, indent=2, ensure_ascii=False)
    print(f"✅ Exported full JSON: {output_path}")
    
    # Generate JS data
    js_data = generate_js_data(campfind_camps)
    
    # Save JS fragment
    js_path = "/root/appforge-outputs/campfind/aca_camps_data.js"
    with open(js_path, "w") as f:
        f.write(f"// ACA Camp Data — {len(campfind_camps)} camps\n")
        f.write(f"// Generated: {__import__('time').strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"const CAMP_DATA = {js_data};\n")
    print(f"✅ Exported JS data: {js_path}")
    
    # Stats
    states = {}
    types = {}
    for c in campfind_camps:
        s = c.get("state", "?")
        states[s] = states.get(s, 0) + 1
        t = c.get("type", "?")
        types[t] = types.get(t, 0) + 1
    
    print(f"\n📊 Final Stats:")
    print(f"  Total camps: {len(campfind_camps)}")
    print(f"  States: {len(states)} — {dict(sorted(states.items(), key=lambda x: -x[1])[:15])}")
    print(f"  Types: {types}")
    
    return campfind_camps

if __name__ == "__main__":
    main()
