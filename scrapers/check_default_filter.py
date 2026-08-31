import json

js_file = r"C:\Users\Matrixkuo\Desktop\Antigravity\APP Design\CampFind\app\aca_camps_data.js"
with open(js_file, "r", encoding="utf-8") as f:
    text = f.read()

start_idx = text.find("[")
end_idx = text.rfind("]") + 1
data = json.loads(text[start_idx:end_idx])

# Default age slider is set to 10
# Check how many camps pass ageMin <= 10 and ageMax >= 10
passed = 0
filtered_by_age = 0

for c in data:
    age_min = c.get("ageMin")
    age_max = c.get("ageMax")
    
    # Check if age=10 is out of bounds
    if age_min is not None and age_min > 10:
        filtered_by_age += 1
        continue
    if age_max is not None and age_max < 10:
        filtered_by_age += 1
        continue
        
    passed += 1

print(f"Total camps: {len(data)}")
print(f"Filtered out by default age slider (Age 10): {filtered_by_age}")
print(f"Camps remaining when default opened: {passed}")
