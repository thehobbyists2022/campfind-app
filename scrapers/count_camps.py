import json
import os

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
js_file = os.path.join(ROOT_DIR, "app", "aca_camps_data.js")
with open(js_file, "r", encoding="utf-8") as f:
    text = f.read()

# Remove 'window.ACA_CAMPS =' at start
start_idx = text.find("[")
end_idx = text.rfind("]") + 1
json_str = text[start_idx:end_idx]

data = json.loads(json_str)

print(f"Total camps in aca_camps_data.js: {len(data)}")

# Let's count unique IDs
unique_ids = set(c["id"] for c in data)
print(f"Unique IDs count: {len(unique_ids)}")

# Let's check season filter breakdown if any
seasons = {}
for c in data:
    s = c.get("season", "unknown")
    seasons[s] = seasons.get(s, 0) + 1
print("Season breakdown:", seasons)
