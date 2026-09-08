import os, asyncio
from playwright.async_api import async_playwright
from PIL import Image

OUTPUT_DIR = r"C:\Users\Matrixkuo\Desktop\Antigravity\APP Design\CampFind\store_assets\ios_screenshots"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(os.path.join(OUTPUT_DIR, "raw"), exist_ok=True)

# 4 Marketing Screens HTML definitions
HTML_TEMPLATES = [
    {
        "id": "01_search",
        "title": "5,000+ Camps Across USA",
        "subtitle": "Search verified Summer, Winter & Spring camps instantly",
        "badge": "✨ 5,000+ Verified ACA Camps",
        "content_type": "search"
    },
    {
        "id": "02_listings",
        "title": "Explore Top STEM & Nature Camps",
        "subtitle": "Accredited programs with distance, age & schedule filters",
        "badge": "📍 Carlsbad & San Diego, CA (92056)",
        "content_type": "listings"
    },
    {
        "id": "03_details",
        "title": "Detailed Schedules & Extended Care",
        "subtitle": "Before/After care, shuttle bus, and weekly session dates",
        "badge": "📋 Verified Program Details",
        "content_type": "details"
    },
    {
        "id": "04_sibling",
        "title": "Smart Sibling Matching & Compare",
        "subtitle": "Coordinate schedules for children of different ages at a glance",
        "badge": "👫 Multi-Child Coordination Mode",
        "content_type": "sibling"
    }
]

def build_html(screen):
    c_type = screen["content_type"]
    
    if c_type == "search":
        inner_content = """
        <div class="card">
            <div class="field">
                <label>LOCATION / CITY / ZIP CODE</label>
                <div class="input-box">📍 Carlsbad, CA 92056</div>
            </div>
            <div class="field" style="margin-top:16px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <label>CHILD'S AGE</label>
                    <span class="pill-red">10 yrs</span>
                </div>
                <div class="slider-track"><div class="slider-bar" style="width:55%;"></div><div class="slider-thumb" style="left:55%;"></div></div>
            </div>
            <div class="field" style="margin-top:16px;">
                <label>SEASON</label>
                <div class="tags">
                    <span class="tag active">☀️ Summer Camp</span>
                    <span class="tag active">❄️ Winter Camp</span>
                    <span class="tag">🌸 Spring Break</span>
                </div>
            </div>
            <div class="field" style="margin-top:16px;">
                <label>CAMP THEME & ACTIVITIES</label>
                <div class="tags">
                    <span class="tag active">🤖 STEM & Robotics</span>
                    <span class="tag active">🌲 Nature & Outdoor</span>
                    <span class="tag">🎨 Arts & Drama</span>
                    <span class="tag">⚽ Sports & Athletics</span>
                </div>
            </div>
            <div class="field" style="margin-top:16px;">
                <label>EXTENDED CARE</label>
                <div class="tags">
                    <span class="tag active">🌅 Before Care (7:30 AM)</span>
                    <span class="tag active">🌆 After Care (6:00 PM)</span>
                    <span class="tag">🚌 Shuttle Bus</span>
                </div>
            </div>
            <button class="btn-primary" style="margin-top:20px;">🔍 Search 5,000+ Verified Camps</button>
        </div>
        """
    elif c_type == "listings":
        inner_content = """
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:12px; padding:0 4px;">
            <span style="font-weight:800; font-size:1.1rem; color:#1A1A2E;">Found 38 Camps near 92056</span>
            <span style="font-size:0.85rem; color:#4ECDC4; font-weight:700;">🗺️ Map View</span>
        </div>
        <div class="camp-card">
            <div class="camp-header">
                <span class="badge-aca">⭐ ACA ACCREDITED</span>
                <span class="dist">2.4 miles away</span>
            </div>
            <h3 class="camp-title">iD Tech STEM & Robotics Camp</h3>
            <p class="camp-loc">📍 Carlsbad Village / La Costa Campus</p>
            <div class="camp-meta">
                <span class="meta-item">🎂 Ages 7-17</span>
                <span class="meta-item">☀️ Summer & Winter</span>
                <span class="meta-item">🌅 Extended Care</span>
            </div>
            <div class="camp-desc">Hands-on AI coding, robotics engineering, Python game dev, and LEGO EV3 robotics for all skill levels.</div>
        </div>
        <div class="camp-card">
            <div class="camp-header">
                <span class="badge-aca">⭐ ACA ACCREDITED</span>
                <span class="dist">4.1 miles away</span>
            </div>
            <h3 class="camp-title">Fleet Science Center Discovery Camp</h3>
            <p class="camp-loc">📍 San Diego Science Pavilion</p>
            <div class="camp-meta">
                <span class="meta-item">🎂 Ages 5-14</span>
                <span class="meta-item">☀️ Summer Day Camp</span>
                <span class="meta-item">🚌 Shuttle Available</span>
            </div>
            <div class="camp-desc">Interactive physics, astronomy, chemistry lab experiments, and outdoor exploration.</div>
        </div>
        <div class="camp-card">
            <div class="camp-header">
                <span class="badge-aca">⭐ ACA ACCREDITED</span>
                <span class="dist">5.8 miles away</span>
            </div>
            <h3 class="camp-title">Play-Well TEKnologies Engineering</h3>
            <p class="camp-loc">📍 Encinitas Community Center</p>
            <div class="camp-meta">
                <span class="meta-item">🎂 Ages 5-12</span>
                <span class="meta-item">🤖 LEGO Robotics</span>
            </div>
        </div>
        """
    elif c_type == "details":
        inner_content = """
        <div class="camp-card detail-card" style="box-shadow: 0 10px 30px rgba(0,0,0,0.1); border:2px solid #4ECDC4;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span class="badge-aca">⭐ ACA ACCREDITED CAMP</span>
                <span style="color:#2ecc71; font-weight:800; font-size:0.9rem;">● Open for Enrollment</span>
            </div>
            <h2 style="font-size:1.45rem; font-weight:900; color:#1A1A2E; margin:10px 0 4px 0;">Camp Ocean Pines & STEM Lab</h2>
            <p style="color:#666; font-size:0.9rem; margin-bottom:14px;">📍 1473 Pineridge Dr, Cambria & Coastal CA</p>
            
            <div class="detail-grid">
                <div class="grid-box">
                    <span class="lbl">AGES</span>
                    <span class="val">7 to 16 yrs</span>
                </div>
                <div class="grid-box">
                    <span class="lbl">TYPE</span>
                    <span class="val">Day & Overnight</span>
                </div>
                <div class="grid-box">
                    <span class="lbl">SEASON</span>
                    <span class="val">Summer / Winter</span>
                </div>
                <div class="grid-box">
                    <span class="lbl">EXTENDED CARE</span>
                    <span class="val">7:30 AM - 6 PM</span>
                </div>
            </div>

            <div style="margin-top:16px;">
                <label style="font-weight:800; font-size:0.8rem; color:#888; text-transform:uppercase;">Weekly Sessions Schedule</label>
                <div class="session-row"><span style="font-weight:700;">Week 1: June 15 - June 20</span><span class="tag-green">Available</span></div>
                <div class="session-row"><span style="font-weight:700;">Week 2: June 22 - June 27</span><span class="tag-green">Available</span></div>
                <div class="session-row"><span style="font-weight:700;">Week 3: July 06 - July 11</span><span class="tag-orange">Few Spots</span></div>
                <div class="session-row"><span style="font-weight:700;">Week 4: July 13 - July 18</span><span class="tag-green">Available</span></div>
            </div>

            <div style="display:flex; gap:10px; margin-top:20px;">
                <button class="btn-primary" style="flex:1;">🌐 Visit Official Website</button>
                <button class="btn-secondary" style="flex:1;">❤️ Save to Favorites</button>
            </div>
        </div>
        """
    elif c_type == "sibling":
        inner_content = """
        <div class="card" style="margin-bottom:14px; background:#F8FDFA; border:1.5px solid #4ECDC4;">
            <div style="display:flex; align-items:center; gap:8px;">
                <span style="font-size:1.3rem;">👫</span>
                <div>
                    <h3 style="margin:0; font-size:1.05rem; font-weight:800; color:#1A1A2E;">Multi-Child Sibling Match Active</h3>
                    <p style="margin:2px 0 0 0; font-size:0.8rem; color:#666;">Child 1 (Age 7) & Child 2 (Age 11) &middot; Same Location & Weeks</p>
                </div>
            </div>
        </div>
        
        <div style="font-weight:800; font-size:1.05rem; color:#1A1A2E; margin-bottom:10px;">Side-by-Side Comparison (2 Camps)</div>
        
        <div class="compare-table">
            <div class="compare-col">
                <div class="compare-head" style="background:#FFF0F0;">
                    <div style="font-size:0.75rem; color:#FF6B6B; font-weight:800;">OPTION A</div>
                    <div style="font-weight:800; font-size:0.95rem;">iD Tech Robotics</div>
                </div>
                <div class="compare-row"><strong>Ages:</strong> 7 - 17 yrs</div>
                <div class="compare-row"><strong>Sibling Match:</strong> ✅ Both fit</div>
                <div class="compare-row"><strong>Care:</strong> Before + After</div>
                <div class="compare-row"><strong>Price:</strong> $$ (Mid-Range)</div>
                <div class="compare-row"><strong>Shuttle:</strong> 🚌 Included</div>
            </div>
            <div class="compare-col">
                <div class="compare-head" style="background:#F0FCFA;">
                    <div style="font-size:0.75rem; color:#4ECDC4; font-weight:800;">OPTION B</div>
                    <div style="font-weight:800; font-size:0.95rem;">Camp Ocean Pines</div>
                </div>
                <div class="compare-row"><strong>Ages:</strong> 7 - 16 yrs</div>
                <div class="compare-row"><strong>Sibling Match:</strong> ✅ Both fit</div>
                <div class="compare-row"><strong>Care:</strong> Full Day (8am-6pm)</div>
                <div class="compare-row"><strong>Price:</strong> $$ (Mid-Range)</div>
                <div class="compare-row"><strong>Shuttle:</strong> ❌ Drop-off only</div>
            </div>
        </div>
        """

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            * {{ box-sizing: border-box; margin:0; padding:0; font-family: -apple-system, BlinkMacSystemFont, "SF Pro Display", "SF Pro Text", "Segoe UI", Roboto, Helvetica, Arial, sans-serif; }}
            body {{
                width: 1290px;
                height: 2796px;
                background: #F4F6F9;
                display: flex;
                flex-direction: column;
                align-items: center;
                overflow: hidden;
                position: relative;
            }}
            .marketing-header {{
                width: 100%;
                padding: 130px 80px 40px 80px;
                text-align: center;
                background: linear-gradient(180deg, #FFFFFF 0%, #F4F6F9 100%);
            }}
            .badge-top {{
                display: inline-block;
                background: #EBF8F7;
                color: #2BA89E;
                font-size: 28px;
                font-weight: 800;
                padding: 12px 28px;
                border-radius: 30px;
                margin-bottom: 24px;
                letter-spacing: 0.5px;
            }}
            .headline {{
                font-size: 64px;
                font-weight: 900;
                color: #1A1A2E;
                line-height: 1.15;
                letter-spacing: -1px;
                margin-bottom: 18px;
            }}
            .subheadline {{
                font-size: 34px;
                font-weight: 500;
                color: #6C7A89;
                line-height: 1.35;
                max-width: 1050px;
                margin: 0 auto;
            }}
            .mockup-container {{
                width: 1130px;
                flex: 1;
                background: #FFFFFF;
                border-top-left-radius: 60px;
                border-top-right-radius: 60px;
                box-shadow: 0 -15px 50px rgba(0,0,0,0.08);
                padding: 50px 45px 0 45px;
                border: 2px solid #E5E9F0;
                border-bottom: none;
                display: flex;
                flex-direction: column;
            }}
            .app-nav {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 30px;
                padding-bottom: 20px;
                border-bottom: 1px solid #ECEFF4;
            }}
            .app-title {{
                font-size: 42px;
                font-weight: 900;
                letter-spacing: -0.5px;
            }}
            .card {{
                background: #FFFFFF;
                border-radius: 28px;
                padding: 30px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.04);
                border: 1.5px solid #ECEFF4;
            }}
            .field label {{
                font-size: 24px;
                font-weight: 800;
                color: #8A9BA8;
                letter-spacing: 0.5px;
            }}
            .input-box {{
                margin-top: 10px;
                background: #F8FAFC;
                border: 2px solid #D8E2EC;
                padding: 22px 26px;
                border-radius: 20px;
                font-size: 32px;
                font-weight: 700;
                color: #1A1A2E;
            }}
            .pill-red {{
                background: #FFE8E8;
                color: #FF5252;
                font-size: 26px;
                font-weight: 800;
                padding: 6px 18px;
                border-radius: 20px;
            }}
            .slider-track {{
                margin-top: 16px;
                height: 16px;
                background: #E2E8F0;
                border-radius: 10px;
                position: relative;
            }}
            .slider-bar {{
                height: 100%;
                background: #FF6B6B;
                border-radius: 10px;
            }}
            .slider-thumb {{
                width: 36px;
                height: 36px;
                background: #FFFFFF;
                border: 5px solid #FF6B6B;
                border-radius: 50%;
                position: absolute;
                top: -10px;
                transform: translateX(-50%);
                box-shadow: 0 4px 10px rgba(0,0,0,0.15);
            }}
            .tags {{
                display: flex;
                flex-wrap: wrap;
                gap: 12px;
                margin-top: 12px;
            }}
            .tag {{
                background: #F1F5F9;
                color: #475569;
                font-size: 26px;
                font-weight: 700;
                padding: 14px 24px;
                border-radius: 18px;
            }}
            .tag.active {{
                background: #E6FAF8;
                color: #0D9488;
                border: 1.5px solid #99F6E4;
            }}
            .btn-primary {{
                width: 100%;
                background: linear-gradient(135deg, #FF6B6B, #FF8E53);
                color: white;
                font-size: 32px;
                font-weight: 800;
                padding: 24px;
                border-radius: 24px;
                border: none;
                box-shadow: 0 8px 25px rgba(255,107,107,0.35);
            }}
            .btn-secondary {{
                background: #F1F5F9;
                color: #334155;
                font-size: 30px;
                font-weight: 800;
                padding: 22px;
                border-radius: 22px;
                border: none;
            }}
            .camp-card {{
                background: #FFFFFF;
                border: 1.5px solid #ECEFF4;
                border-radius: 26px;
                padding: 28px;
                margin-bottom: 22px;
                box-shadow: 0 4px 16px rgba(0,0,0,0.03);
            }}
            .camp-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 12px;
            }}
            .badge-aca {{
                background: #FEF3C7;
                color: #92400E;
                font-size: 22px;
                font-weight: 800;
                padding: 6px 16px;
                border-radius: 12px;
            }}
            .dist {{
                font-size: 24px;
                font-weight: 700;
                color: #64748B;
            }}
            .camp-title {{
                font-size: 34px;
                font-weight: 900;
                color: #0F172A;
                margin-bottom: 6px;
            }}
            .camp-loc {{
                font-size: 24px;
                color: #64748B;
                margin-bottom: 16px;
            }}
            .camp-meta {{
                display: flex;
                gap: 12px;
                margin-bottom: 14px;
            }}
            .meta-item {{
                background: #F8FAFC;
                border: 1px solid #E2E8F0;
                padding: 8px 18px;
                border-radius: 14px;
                font-size: 22px;
                font-weight: 700;
                color: #334155;
            }}
            .camp-desc {{
                font-size: 24px;
                color: #475569;
                line-height: 1.4;
            }}
            .detail-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 16px;
                margin: 20px 0;
            }}
            .grid-box {{
                background: #F8FAFC;
                padding: 18px 22px;
                border-radius: 18px;
                border: 1px solid #E2E8F0;
            }}
            .grid-box .lbl {{
                display: block;
                font-size: 20px;
                color: #64748B;
                font-weight: 800;
            }}
            .grid-box .val {{
                font-size: 26px;
                color: #0F172A;
                font-weight: 800;
                margin-top: 4px;
            }}
            .session-row {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 16px 20px;
                background: #F8FAFC;
                border-radius: 16px;
                margin-top: 10px;
                font-size: 24px;
            }}
            .tag-green {{
                background: #DCFCE7;
                color: #166534;
                font-size: 20px;
                font-weight: 800;
                padding: 6px 14px;
                border-radius: 10px;
            }}
            .tag-orange {{
                background: #FFEDD5;
                color: #9A3412;
                font-size: 20px;
                font-weight: 800;
                padding: 6px 14px;
                border-radius: 10px;
            }}
            .compare-table {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 16px;
                margin-top: 14px;
            }}
            .compare-col {{
                background: #FFFFFF;
                border-radius: 22px;
                border: 1.5px solid #E2E8F0;
                overflow: hidden;
            }}
            .compare-head {{
                padding: 20px 16px;
                text-align: center;
                border-bottom: 1.5px solid #E2E8F0;
            }}
            .compare-row {{
                padding: 18px 16px;
                font-size: 22px;
                border-bottom: 1px solid #F1F5F9;
                color: #334155;
            }}
        </style>
    </head>
    <body>
        <div class="marketing-header">
            <div class="badge-top">{screen["badge"]}</div>
            <h1 class="headline">{screen["title"]}</h1>
            <p class="subheadline">{screen["subtitle"]}</p>
        </div>
        
        <div class="mockup-container">
            <div class="app-nav">
                <div style="display:flex; align-items:center; gap:12px;">
                    <span style="font-size:36px;">📍</span>
                    <span class="app-title"><span style="color:#FF6B6B;">Camp</span><span style="color:#4ECDC4;">Find</span></span>
                </div>
                <div style="font-size:24px; font-weight:800; color:#64748B; background:#F1F5F9; padding:10px 20px; border-radius:16px;">
                    🇺🇸 English
                </div>
            </div>
            {inner_content}
        </div>
    </body>
    </html>
    """
    return html

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page(viewport={"width": 1290, "height": 2796}, device_scale_factor=1)
        
        for idx, screen in enumerate(HTML_TEMPLATES, 1):
            html = build_html(screen)
            await page.set_content(html)
            await page.wait_for_timeout(300)
            
            # Save iPhone 6.7" (1290x2796)
            out_6_7 = os.path.join(OUTPUT_DIR, f"0{idx}_iphone_6_7_inch_1290x2796.png")
            await page.screenshot(path=out_6_7)
            print(f"Generated: {out_6_7}")
            
            # Resize for iPhone 6.5" (1242x2688)
            img = Image.open(out_6_7)
            out_6_5 = os.path.join(OUTPUT_DIR, f"0{idx}_iphone_6_5_inch_1242x2688.png")
            img.resize((1242, 2688), Image.Resampling.LANCZOS).save(out_6_5, "PNG")
            print(f"Generated: {out_6_5}")
            
            # Resize for iPad 13" (2048x2732)
            out_ipad = os.path.join(OUTPUT_DIR, f"0{idx}_ipad_13inch_2048x2732.png")
            img.resize((2048, 2732), Image.Resampling.LANCZOS).save(out_ipad, "PNG")
            print(f"Generated: {out_ipad}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
