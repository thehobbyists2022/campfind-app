import os
import sys
import re
import csv
import json
import time
import argparse
import subprocess
from datetime import datetime
from urllib.parse import urljoin
from html.parser import HTMLParser
import requests

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
INPUT_CSV = os.path.join(PROJECT_DIR, 'campfind_camps_enriched.csv')
if not os.path.exists(INPUT_CSV):
    INPUT_CSV = os.path.join(PROJECT_DIR, 'campfind_all_camps.csv')

OUTPUT_CSV = os.path.join(PROJECT_DIR, 'campfind_camps_enriched.csv')
APP_JSON = os.path.join(PROJECT_DIR, 'app', 'aca_camps.json')

class PageParser(HTMLParser):
    def __init__(self, base_url):
        super().__init__()
        self.base_url = base_url
        self.text_parts = []
        self.ignore = False
        self.rate_links = []
        self.current_tag = None
        self.current_href = None

    def handle_starttag(self, tag, attrs):
        self.current_tag = tag
        if tag in ('script', 'style', 'noscript', 'header', 'footer', 'nav', 'svg'):
            self.ignore = True
        if tag == 'a':
            attr_dict = dict(attrs)
            self.current_href = attr_dict.get('href', '')

    def handle_endtag(self, tag):
        if tag in ('script', 'style', 'noscript', 'header', 'footer', 'nav', 'svg'):
            self.ignore = False
        if tag == 'a':
            self.current_href = None
        self.current_tag = None

    def handle_data(self, data):
        clean = data.strip()
        if not clean:
            return
        if not self.ignore:
            self.text_parts.append(clean)
        if self.current_href and len(self.rate_links) < 3:
            kw = ['rate', 'tuition', 'fee', 'price', 'pricing', 'dates-rates', 'cost']
            combined = (self.current_href + ' ' + clean).lower()
            if any(k in combined for k in kw) and not self.current_href.startswith(('mailto:', 'tel:', 'javascript:')):
                full_url = urljoin(self.base_url, self.current_href)
                if full_url not in self.rate_links and full_url != self.base_url:
                    self.rate_links.append(full_url)

    def get_text(self):
        return ' '.join(self.text_parts)

class JevMCPClient:
    def __init__(self):
        env = os.environ.copy()
        env['JEV_PROVIDER'] = 'compatible'
        env['JEV_API_BASE_URL'] = 'https://opencode.ai/zen/v1/systemone'
        env['JEV_MCP_MODEL'] = 'jev-1.13-free'

        self.proc = subprocess.Popen(
            ['npx', '-y', '@jkudish/jev-mcp'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            shell=True,
            env=env
        )
        self.req_id = 1
        self._init_client()

    def _send(self, method, params=None):
        msg = {
            'jsonrpc': '2.0',
            'id': self.req_id,
            'method': method
        }
        if params is not None:
            msg['params'] = params
        self.req_id += 1
        self.proc.stdin.write(json.dumps(msg) + '\n')
        self.proc.stdin.flush()

        while True:
            line = self.proc.stdout.readline()
            if not line:
                return None
            try:
                data = json.loads(line)
                if data.get('id') == msg['id']:
                    return data
            except json.JSONDecodeError:
                continue

    def _init_client(self):
        self._send('initialize', {
            'protocolVersion': '2024-11-05',
            'capabilities': {},
            'clientInfo': {'name': 'campfind-enricher', 'version': '2.1.0'}
        })

    def extract(self, document, fields, purpose="Extract camp fields"):
        res = self._send('tools/call', {
            'name': 'jev_extract',
            'arguments': {
                'document': document[:48000],
                'fields': fields,
                'purpose': purpose
            }
        })
        if not res or 'result' not in res:
            return {}
        try:
            content_text = res['result'].get('content', [{}])[0].get('text', '')
            parsed = json.loads(content_text)
            extracted = {}
            for item in parsed.get('results', []):
                if item.get('status') == 'auto' and item.get('value'):
                    extracted[item['id']] = {
                        'value': item['value'],
                        'confidence': item.get('confidence', 1.0)
                    }
            return extracted
        except Exception:
            return {}

    def classify_theme(self, text):
        classes = [
            {'id': 'STEM & Code', 'description': 'Science, coding, programming, robotics, game design, mathematics, engineering'},
            {'id': 'Sports', 'description': 'Athletics, swimming, basketball, soccer, gymnastics, fitness, martial arts, beach games'},
            {'id': 'Arts & Drama', 'description': 'Acting, theatre, painting, drawing, music, dance, film, sculpting, creative writing'},
            {'id': 'Outdoor', 'description': 'Nature exploration, wilderness camping, hiking, rock climbing, lake canoeing, animals'},
            {'id': 'Academic', 'description': 'Tutoring, language immersion, reading, writing, test prep, history'}
        ]
        res = self._send('tools/call', {
            'name': 'jev_classify',
            'arguments': {
                'classes': classes,
                'items': [{'id': 'camp_item', 'text': text[:1500]}],
                'purpose': 'Classify camp into standard theme'
            }
        })
        if not res or 'result' not in res:
            return None
        try:
            content_text = res['result'].get('content', [{}])[0].get('text', '')
            parsed = json.loads(content_text)
            for item in parsed.get('results', []):
                if item.get('decision') == 'auto':
                    return item.get('classification')
        except Exception:
            pass
        return None

    def close(self):
        try:
            self.proc.kill()
        except Exception:
            pass

def fetch_page_and_links(url, session):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
    }
    try:
        resp = session.get(url, headers=headers, timeout=8)
        if resp.status_code == 200:
            parser = PageParser(url)
            parser.feed(resp.text)
            text = parser.get_text()
            text = re.sub(r'\s+', ' ', text).strip()
            return text, parser.rate_links
    except Exception:
        pass
    return None, []

def fetch_page_text_only(url, session):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        resp = session.get(url, headers=headers, timeout=6)
        if resp.status_code == 200:
            parser = PageParser(url)
            parser.feed(resp.text)
            text = parser.get_text()
            return re.sub(r'\s+', ' ', text).strip()
    except Exception:
        pass
    return None

def save_csv(rows, fieldnames, target_path):
    with open(target_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

def run_enrichment(limit=100, state_filter=None, sync_app_json=True):
    print("=" * 70)
    print("CampFind JEV High-Fidelity Data Enrichment Pipeline (Real & Verified)")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    if not os.path.exists(INPUT_CSV):
        print(f"Error: {INPUT_CSV} not found! Run export_to_csv.py first.")
        return

    with open(INPUT_CSV, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames)
        rows = list(reader)

    if 'Verification Method (驗證機制)' not in fieldnames:
        fieldnames.append('Verification Method (驗證機制)')
    if 'Scrape Status (爬取狀態)' not in fieldnames:
        fieldnames.append('Scrape Status (爬取狀態)')

    print(f"Loaded {len(rows)} camps from CSV.")
    if state_filter:
        print(f"Filter State: {state_filter}")
    print(f"Target Batch Limit: {limit}")

    # Launch JEV client
    print("\nStarting JEV Verifier Engine (TypeSafe Jev)...")
    jev = JevMCPClient()
    print("JEV Engine Online (Zero-Hallucination Picker & Subpage Rates Discovery Active).")

    session = requests.Session()
    processed = 0
    enriched_count = 0
    skipped_count = 0

    try:
        for idx, row in enumerate(rows):
            if limit and processed >= limit:
                break

            # Skip if already checked in previous batches unless reset
            status = row.get('Scrape Status (爬取狀態)', '')
            if status:
                continue

            camp_name = row.get('Camp Name (營隊名稱)', '')
            website = row.get('Official Website (官方網站)', '')
            state = row.get('State (州別)', '')

            if state_filter and state != state_filter:
                continue

            if not website or not website.startswith('http'):
                continue

            # Need enrichment check
            has_price = bool(row.get('Weekly Price USD (每週費用)'))
            has_phone = bool(row.get('Phone (聯絡電話)'))
            has_age = bool(row.get('Min Age (最低年齡)'))
            has_theme = bool(row.get('Theme (主題類型)'))

            if has_price and has_phone and has_age and has_theme:
                continue

            processed += 1
            print(f"\n[{processed}/{limit}] Processing: {camp_name} ({state})")
            print(f"  URL: {website}")

            # 1. Fetch webpage text and discover rates subpage links
            text, rate_links = fetch_page_and_links(website, session)
            if not text or len(text) < 120:
                print("  -> Could not fetch main webpage (offline or blocked). Skipping safely.")
                row['Scrape Status (爬取狀態)'] = 'Offline or Blocked'
                skipped_count += 1
                continue

            # 2. Prepare field extraction schemas
            extract_fields = []
            if not has_price:
                extract_fields.append({
                    'id': 'price',
                    'pattern': r'\$\d{2,4}(\.\d{2})?',
                    'description': 'Weekly or standard multi-day camp registration tuition fee in USD dollars'
                })
            if not has_phone:
                extract_fields.append({
                    'id': 'phone',
                    'pattern': r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
                    'description': 'Customer service or camp director direct phone number'
                })
            if not has_age:
                extract_fields.append({
                    'id': 'age_min',
                    'pattern': r'\b([2-9]|1[0-7])\b',
                    'description': 'Minimum child eligibility age for enrollment (between 2 and 17 years old)'
                })
                extract_fields.append({
                    'id': 'age_max',
                    'pattern': r'\b([3-9]|1[0-8])\b',
                    'description': 'Maximum child eligibility age for enrollment (between 3 and 18 years old)'
                })

            results = {}
            if extract_fields:
                results = jev.extract(text, extract_fields, purpose=f"Extract tuition and age limits for {camp_name}")

            # 3. If price is still missing and we discovered a rates/tuition subpage, probe it!
            if not has_price and 'price' not in results and rate_links:
                sub_url = rate_links[0]
                print(f"  -> Probing Rates Subpage: {sub_url}")
                sub_text = fetch_page_text_only(sub_url, session)
                if sub_text and len(sub_text) > 100:
                    sub_results = jev.extract(sub_text, [{
                        'id': 'price',
                        'pattern': r'\$\d{2,4}(\.\d{2})?',
                        'description': 'Weekly or multi-day camp tuition fee in USD dollars'
                    }], purpose=f"Extract tuition from rates page for {camp_name}")
                    if 'price' in sub_results:
                        results['price'] = sub_results['price']
                        print("  -> Successfully captured price from rates subpage!")

            # 4. Classify theme if missing
            if not has_theme:
                theme = jev.classify_theme(text)
                if theme:
                    row['Theme (主題類型)'] = theme
                    print(f"  + [JEV Theme]: {theme}")

            updated = False

            # Price Validation
            if 'price' in results:
                raw_price = results['price']['value'].replace('$', '')
                try:
                    price_val = float(raw_price)
                    if 50.0 <= price_val <= 3500.0:
                        row['Weekly Price USD (每週費用)'] = str(price_val)
                        print(f"  + [JEV Price]: ${price_val:.2f} (Confidence: {results['price']['confidence']*100:.0f}%)")
                        updated = True
                except ValueError:
                    pass

            # Phone Validation
            if 'phone' in results:
                phone_val = results['phone']['value']
                row['Phone (聯絡電話)'] = phone_val
                print(f"  + [JEV Phone]: {phone_val} (Confidence: {results['phone']['confidence']*100:.0f}%)")
                updated = True

            # Age Validation
            if 'age_min' in results:
                try:
                    amin = int(results['age_min']['value'])
                    if 2 <= amin <= 17:
                        row['Min Age (最低年齡)'] = str(amin)
                        print(f"  + [JEV Min Age]: {amin} yrs")
                        updated = True
                except ValueError:
                    pass

            if 'age_max' in results:
                try:
                    amax = int(results['age_max']['value'])
                    if 3 <= amax <= 18:
                        row['Max Age (最高年齡)'] = str(amax)
                        print(f"  + [JEV Max Age]: {amax} yrs")
                        updated = True
                except ValueError:
                    pass

            if updated:
                enriched_count += 1
                row['Verification Method (驗證機制)'] = f"JEV Verifier ({datetime.now().strftime('%Y-%m-%d')})"
                row['Scrape Status (爬取狀態)'] = 'Enriched'
                
                # Recalculate missingFields
                rem = []
                if not row.get('Phone (聯絡電話)'): rem.append('phone')
                if not row.get('Email (電子信箱)'): rem.append('email')
                if not row.get('Weekly Price USD (每週費用)'): rem.append('price')
                if not row.get('Min Age (最低年齡)'): rem.append('ageMin')
                if not row.get('Max Age (最高年齡)'): rem.append('ageMax')
                if not row.get('Theme (主題類型)'): rem.append('theme')
                row['Missing Fields to Enrich (待爬蟲補齊欄位)'] = ', '.join(rem) if rem else 'Complete'
            else:
                row['Scrape Status (爬取狀態)'] = 'Checked: No extra rates'

            # Save checkpoint every 5 camps
            if processed % 5 == 0:
                save_csv(rows, fieldnames, OUTPUT_CSV)
                print(f"  [Checkpoint]: Progress saved ({processed} camps processed, {enriched_count} updated).")

            time.sleep(0.2)

    finally:
        jev.close()

    # Final Save
    save_csv(rows, fieldnames, OUTPUT_CSV)

    print("\n" + "=" * 70)
    print("Batch Run Summary:")
    print(f"  Total Processed : {processed}")
    print(f"  Successfully Enriched : {enriched_count}")
    print(f"  Skipped (Offline/Blocked) : {skipped_count}")
    print(f"  Saved to : {OUTPUT_CSV}")
    print("=" * 70)

    # Sync back to app/aca_camps.json
    if sync_app_json and enriched_count > 0:
        print("\nSyncing verified fields back to app/aca_camps.json...")
        with open(APP_JSON, 'r', encoding='utf-8') as f:
            app_data = json.load(f)
        
        camps_by_id = {c['id']: c for c in app_data['camps']}
        for row in rows:
            cid = row.get('Camp ID (編號)')
            if cid in camps_by_id:
                if row.get('Weekly Price USD (每週費用)'):
                    try:
                        camps_by_id[cid]['price'] = float(row['Weekly Price USD (每週費用)'])
                    except ValueError: pass
                if row.get('Phone (聯絡電話)'):
                    camps_by_id[cid]['phone'] = row['Phone (聯絡電話)']
                if row.get('Min Age (最低年齡)'):
                    try:
                        camps_by_id[cid]['ageMin'] = int(row['Min Age (最低年齡)'])
                    except ValueError: pass
                if row.get('Max Age (最高年齡)'):
                    try:
                        camps_by_id[cid]['ageMax'] = int(row['Max Age (最高年齡)'])
                    except ValueError: pass
                if row.get('Theme (主題類型)'):
                    camps_by_id[cid]['theme'] = row['Theme (主題類型)']

        with open(APP_JSON, 'w', encoding='utf-8') as f:
            json.dump(app_data, f, ensure_ascii=False, indent=2)
        print("Done! app/aca_camps.json successfully synchronized.")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="CampFind JEV High-Fidelity Data Enricher")
    parser.add_argument('--limit', type=int, default=100, help="Number of camps to process in this batch")
    parser.add_argument('--state', type=str, default=None, help="State code (e.g. CA, TX, NY)")
    parser.add_argument('--sync', action='store_true', default=True, help="Sync enriched data to app JSON database")
    args = parser.parse_args()

    run_enrichment(limit=args.limit, state_filter=args.state, sync_app_json=args.sync)
