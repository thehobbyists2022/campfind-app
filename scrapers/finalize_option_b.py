#!/usr/bin/env python3
import json
import subprocess

def finalize_option_b():
    subprocess.run(["python", "scrapers/05_expand_and_enrich_camps.py"], check=True)
    subprocess.run(["python", "scrapers/clean_synthetic_urls.py"], check=True)

    with open("app/aca_camps.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    with open("mobile/assets/aca_camps.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Option B Dataset Finalized: {len(data['camps'])} Camps ready for production launch!")

if __name__ == "__main__":
    finalize_option_b()
