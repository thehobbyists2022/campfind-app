import json
import csv
import os

INPUT_JSON = os.path.join(os.path.dirname(__file__), 'app', 'aca_camps.json')
OUTPUT_CSV = os.path.join(os.path.dirname(__file__), 'campfind_all_camps.csv')

def export_camps():
    with open(INPUT_JSON, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    camps = data.get('camps', [])
    print(f"Total camps to export: {len(camps)}")

    fields = [
        ('id', 'Camp ID (編號)'),
        ('name', 'Camp Name (營隊名稱)'),
        ('provider', 'Provider / Brand (主辦品牌)'),
        ('website', 'Official Website (官方網站)'),
        ('sourceUrl', 'Source URL (資料來源網址)'),
        ('city', 'City (城市)'),
        ('state', 'State (州別)'),
        ('zip', 'ZIP Code (郵遞區號)'),
        ('address', 'Street Address (詳細地址)'),
        ('lat', 'Latitude (緯度)'),
        ('lng', 'Longitude (經度)'),
        ('type', 'Camp Type (類型: day/overnight)'),
        ('season', 'Season (季節: summer/winter/spring)'),
        ('theme', 'Theme (主題類型)'),
        ('ageMin', 'Min Age (最低年齡)'),
        ('ageMax', 'Max Age (最高年齡)'),
        ('price', 'Weekly Price USD (每週費用)'),
        ('priceNote', 'Price Note (收費備註)'),
        ('beforeCare', 'Before Care (早托: True/False)'),
        ('afterCare', 'After Care (延托: True/False)'),
        ('shuttle', 'Shuttle Bus (接送校車: True/False)'),
        ('weeks', 'Available Weeks (開放週別梯次)'),
        ('phone', 'Phone (聯絡電話)'),
        ('email', 'Email (電子信箱)'),
        ('description', 'Description (營隊簡介)'),
        ('rating', 'Rating (評分)'),
        ('reviewCount', 'Review Count (評論數)'),
        ('acaVerified', 'ACA Verified (ACA認證)'),
        ('missingFields', 'Missing Fields to Enrich (待爬蟲補齊欄位)')
    ]

    header_keys = [k for k, _ in fields]
    header_labels = [label for _, label in fields]

    critical_check_fields = [
        'phone', 'email', 'address', 'zip', 'price', 'ageMin', 'ageMax',
        'beforeCare', 'afterCare', 'shuttle', 'weeks', 'description'
    ]

    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(header_labels)

        for c in camps:
            # Calculate missing fields for LLM crawler targeting
            missing = []
            for cf in critical_check_fields:
                val = c.get(cf)
                if val is None or val == '' or val == []:
                    missing.append(cf)

            row = []
            for k in header_keys:
                if k == 'missingFields':
                    row.append(', '.join(missing) if missing else 'Complete')
                elif k == 'weeks':
                    val = c.get(k)
                    row.append(','.join(map(str, val)) if isinstance(val, list) else str(val or ''))
                else:
                    val = c.get(k)
                    row.append('' if val is None else str(val))
            writer.writerow(row)

    print(f"Successfully generated CSV at: {OUTPUT_CSV}")

if __name__ == '__main__':
    export_camps()
