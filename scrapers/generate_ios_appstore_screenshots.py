import os, asyncio
from playwright.async_api import async_playwright
from PIL import Image

OUTPUT_DIR = r"C:\Users\Matrixkuo\Desktop\Antigravity\APP Design\CampFind\store_assets\ios_screenshots"
os.makedirs(OUTPUT_DIR, exist_ok=True)

HTML_TEMPLATES = [
    {
        "id": "01_search",
        "title": "5,000+ Verified Camps Across USA",
        "subtitle": "Search accredited Summer, Winter, Spring & Fall camps instantly",
        "badge": "✨ Nationwide Camp Finder",
        "content_type": "search"
    },
    {
        "id": "02_listings",
        "title": "Explore Top STEM & Nature Programs",
        "subtitle": "Accredited camps with distance matching, age & live schedule filters",
        "badge": "📍 Carlsbad & San Diego, CA (92056)",
        "content_type": "listings"
    },
    {
        "id": "03_details",
        "title": "Detailed Schedules & Extended Care",
        "subtitle": "Before & After care, shuttle buses, and weekly session rates",
        "badge": "📋 Verified Program Details",
        "content_type": "details"
    },
    {
        "id": "04_sibling",
        "title": "Smart Sibling Matching & Compare",
        "subtitle": "Coordinate schedules for children of different ages at a glance",
        "badge": "👫 Multi-Child Coordination",
        "content_type": "sibling"
    }
]

def build_html(screen):
    c_type = screen["content_type"]
    
    if c_type == "search":
        inner_content = """
        <div class="card" style="margin-bottom:20px;">
            <div class="field">
                <label>LOCATION / CITY / ZIP CODE</label>
                <div class="input-box">📍 Carlsbad, CA 92056</div>
            </div>
            <div class="field" style="margin-top:20px;">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <label>CHILD'S AGE</label>
                    <span class="pill-red">10 yrs</span>
                </div>
                <div class="slider-track"><div class="slider-bar" style="width:55%;"></div><div class="slider-thumb" style="left:55%;"></div></div>
            </div>
            <div class="field" style="margin-top:20px;">
                <label>SEASON</label>
                <div class="tags">
                    <span class="tag active">☀️ Summer Camp</span>
                    <span class="tag active">❄️ Winter Camp</span>
                    <span class="tag">🌸 Spring Break</span>
                    <span class="tag">🍂 Fall Break</span>
                </div>
            </div>
            <div class="field" style="margin-top:20px;">
                <label>CAMP THEME & ACTIVITIES</label>
                <div class="tags">
                    <span class="tag active">🤖 STEM & Robotics</span>
                    <span class="tag active">🌲 Nature & Outdoor</span>
                    <span class="tag">🎨 Arts & Crafts</span>
                    <span class="tag">⚽ Sports & Athletics</span>
                    <span class="tag">🏄 Water & Surfing</span>
                </div>
            </div>
            <div class="field" style="margin-top:20px;">
                <label>EXTENDED CARE OPTIONS</label>
                <div class="tags">
                    <span class="tag active">🌅 Before Care (7:30 AM)</span>
                    <span class="tag active">🌆 After Care (6:00 PM)</span>
                    <span class="tag">🚌 Shuttle Bus</span>
                </div>
            </div>
            <button class="btn-primary" style="margin-top:24px;">🔍 Search 5,000+ Verified Camps</button>
        </div>

        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:14px; padding:0 4px;">
            <span style="font-weight:900; font-size:30px; color:#1A1A2E;">Top Matches Nearby</span>
            <span style="font-size:24px; color:#0D9488; font-weight:800;">38 Camps Found</span>
        </div>
        
        <div class="camp-card">
            <div class="camp-header">
                <span class="badge-aca">⭐ ACA ACCREDITED</span>
                <span class="dist">2.4 miles away</span>
            </div>
            <h3 class="camp-title">iD Tech STEM & Robotics Academy</h3>
            <p class="camp-loc">📍 Carlsbad Village / La Costa Campus</p>
            <div class="camp-meta">
                <span class="meta-item">🎂 Ages 7-17</span>
                <span class="meta-item">☀️ Summer & Winter</span>
                <span class="meta-item">🌅 Extended Care</span>
            </div>
            <div class="camp-desc">Hands-on AI coding, robotics engineering, Python game dev, and LEGO robotics for all skill levels.</div>
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
                <span class="meta-item">☀️ Day Camp</span>
                <span class="meta-item">🚌 Shuttle Available</span>
            </div>
            <div class="camp-desc">Interactive physics, astronomy, chemistry lab experiments, and outdoor nature exploration.</div>
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
                <span class="meta-item">🌅 Extended Care</span>
            </div>
        </div>

        <div class="camp-card">
            <div class="camp-header">
                <span class="badge-aca">⭐ ACA ACCREDITED</span>
                <span class="dist">7.2 miles away</span>
            </div>
            <h3 class="camp-title">Coastal Surf & Ocean Adventure</h3>
            <p class="camp-loc">📍 Oceanside Pier Harbor Beach</p>
            <div class="camp-meta">
                <span class="meta-item">🎂 Ages 6-16</span>
                <span class="meta-item">🏄 Water Sports</span>
            </div>
        </div>
        """
    elif c_type == "listings":
        inner_content = """
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:18px;">
            <span style="font-weight:900; font-size:32px; color:#1A1A2E;">38 Verified Camps near 92056</span>
            <span style="font-size:24px; color:#0D9488; font-weight:800; background:#E6FAF8; padding:8px 20px; border-radius:14px;">🗺️ Map View</span>
        </div>
        
        <div class="camp-card">
            <div class="camp-header">
                <span class="badge-aca">⭐ ACA ACCREDITED</span>
                <span class="dist">2.4 miles</span>
            </div>
            <h3 class="camp-title">iD Tech STEM & Robotics Academy</h3>
            <p class="camp-loc">📍 Carlsbad Village Campus</p>
            <div class="camp-meta">
                <span class="meta-item">🎂 Ages 7-17</span>
                <span class="meta-item">☀️ Summer & Winter</span>
                <span class="meta-item">🌅 Extended Care</span>
            </div>
            <div class="camp-desc">Hands-on AI coding, robotics engineering, Python game dev, and LEGO robotics for all skill levels.</div>
        </div>
        
        <div class="camp-card">
            <div class="camp-header">
                <span class="badge-aca">⭐ ACA ACCREDITED</span>
                <span class="dist">4.1 miles</span>
            </div>
            <h3 class="camp-title">Fleet Science Discovery Camp</h3>
            <p class="camp-loc">📍 San Diego Science Pavilion</p>
            <div class="camp-meta">
                <span class="meta-item">🎂 Ages 5-14</span>
                <span class="meta-item">☀️ Day Camp</span>
                <span class="meta-item">🚌 Shuttle Available</span>
            </div>
            <div class="camp-desc">Interactive physics, astronomy, chemistry lab experiments, and outdoor nature exploration.</div>
        </div>
        
        <div class="camp-card">
            <div class="camp-header">
                <span class="badge-aca">⭐ ACA ACCREDITED</span>
                <span class="dist">5.8 miles</span>
            </div>
            <h3 class="camp-title">Play-Well TEKnologies Engineering</h3>
            <p class="camp-loc">📍 Encinitas Community Center</p>
            <div class="camp-meta">
                <span class="meta-item">🎂 Ages 5-12</span>
                <span class="meta-item">🤖 LEGO Robotics</span>
                <span class="meta-item">🌅 Extended Care</span>
            </div>
            <div class="camp-desc">Dream it, build it, wreck it! Hands-on engineering design challenges with specialized LEGO kits.</div>
        </div>

        <div class="camp-card">
            <div class="camp-header">
                <span class="badge-aca">⭐ ACA ACCREDITED</span>
                <span class="dist">7.2 miles</span>
            </div>
            <h3 class="camp-title">Coastal Surf & Ocean Adventure</h3>
            <p class="camp-loc">📍 Oceanside Pier Harbor Beach</p>
            <div class="camp-meta">
                <span class="meta-item">🎂 Ages 6-16</span>
                <span class="meta-item">🏄 Water Sports</span>
                <span class="meta-item">☀️ All Summer</span>
            </div>
            <div class="camp-desc">Professional surf coaching, ocean ecology, paddle boarding, and beach volleyball.</div>
        </div>

        <div class="camp-card">
            <div class="camp-header">
                <span class="badge-aca">⭐ ACA ACCREDITED</span>
                <span class="dist">8.5 miles</span>
            </div>
            <h3 class="camp-title">Carlsbad Art & Drama Workshop</h3>
            <p class="camp-loc">📍 Carlsbad Performing Arts Stage</p>
            <div class="camp-meta">
                <span class="meta-item">🎂 Ages 6-14</span>
                <span class="meta-item">🎨 Musical & Arts</span>
                <span class="meta-item">🌅 Extended Care</span>
            </div>
            <div class="camp-desc">Creative stage acting, costume design, watercolor painting, and end-of-session musical showcase.</div>
        </div>

        <div class="camp-card">
            <div class="camp-header">
                <span class="badge-aca">⭐ ACA ACCREDITED</span>
                <span class="dist">9.1 miles</span>
            </div>
            <h3 class="camp-title">San Diego Botanic Garden Explorers</h3>
            <p class="camp-loc">📍 Encinitas Botanical Grounds</p>
            <div class="camp-meta">
                <span class="meta-item">🎂 Ages 5-11</span>
                <span class="meta-item">🌲 Nature Study</span>
            </div>
        </div>
        """
    elif c_type == "details":
        inner_content = """
        <div class="camp-card detail-card" style="border:2.5px solid #4ECDC4; padding:32px; margin-bottom:20px;">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span class="badge-aca">⭐ ACA ACCREDITED CAMP</span>
                <span style="color:#16A34A; font-weight:800; font-size:24px; background:#DCFCE7; padding:6px 16px; border-radius:12px;">● Open for Registration</span>
            </div>
            <h2 style="font-size:42px; font-weight:900; color:#1A1A2E; margin:16px 0 6px 0;">Camp Ocean Pines & STEM Lab</h2>
            <p style="color:#64748B; font-size:26px; margin-bottom:20px;">📍 1473 Pineridge Dr, Coastal California</p>
            
            <div class="detail-grid">
                <div class="grid-box">
                    <span class="lbl">AGES</span>
                    <span class="val">7 to 16 yrs</span>
                </div>
                <div class="grid-box">
                    <span class="lbl">CAMP TYPE</span>
                    <span class="val">Day & Overnight</span>
                </div>
                <div class="grid-box">
                    <span class="lbl">SEASON</span>
                    <span class="val">Summer & Winter</span>
                </div>
                <div class="grid-box">
                    <span class="lbl">EXTENDED CARE</span>
                    <span class="val">7:30 AM - 6:00 PM</span>
                </div>
            </div>

            <div style="margin-top:20px;">
                <label style="font-weight:900; font-size:24px; color:#475569; text-transform:uppercase;">Weekly Session Dates & Availability</label>
                <div class="session-row"><span style="font-weight:800;">Week 1: June 15 – June 20</span><span class="tag-green">Available</span></div>
                <div class="session-row"><span style="font-weight:800;">Week 2: June 22 – June 27</span><span class="tag-green">Available</span></div>
                <div class="session-row"><span style="font-weight:800;">Week 3: July 06 – July 11</span><span class="tag-orange">Few Spots Left</span></div>
                <div class="session-row"><span style="font-weight:800;">Week 4: July 13 – July 18</span><span class="tag-green">Available</span></div>
                <div class="session-row"><span style="font-weight:800;">Week 5: July 20 – July 25</span><span class="tag-green">Available</span></div>
                <div class="session-row"><span style="font-weight:800;">Week 6: July 27 – Aug 01</span><span class="tag-green">Available</span></div>
                <div class="session-row"><span style="font-weight:800;">Week 7: Aug 03 – Aug 08</span><span class="tag-green">Available</span></div>
            </div>

            <div style="margin-top:22px;">
                <label style="font-weight:900; font-size:24px; color:#475569; text-transform:uppercase;">Activities & Highlights</label>
                <div class="tags" style="margin-top:10px;">
                    <span class="tag active">🌲 Forest Exploration</span>
                    <span class="tag active">🏹 Archery & Sports</span>
                    <span class="tag active">🤖 Robotics Workshop</span>
                    <span class="tag active">🎨 Pottery & Crafts</span>
                    <span class="tag active">🌊 Marine Biology</span>
                </div>
            </div>

            <div style="display:flex; gap:16px; margin-top:26px;">
                <button class="btn-primary" style="flex:1;">🌐 Visit Camp Website</button>
                <button class="btn-secondary" style="flex:1;">❤️ Save to Favorites</button>
            </div>
        </div>

        <div class="card" style="padding:24px; margin-bottom:16px;">
            <div style="font-weight:900; font-size:26px; color:#1A1A2E; margin-bottom:8px;">Parent Reviews & Ratings</div>
            <p style="font-size:22px; color:#64748B;">⭐️⭐️⭐️⭐️⭐️ <strong>4.9 / 5.0</strong> &middot; Based on 142 verified reviews. Excellent counselor-to-camper ratio (1:6) with certified ocean lifeguards.</p>
        </div>

        <div class="card" style="padding:24px; margin-bottom:16px;">
            <div style="font-weight:900; font-size:26px; color:#1A1A2E; margin-bottom:8px;">Location & Daily Shuttle</div>
            <p style="font-size:22px; color:#64748B;">📍 15 min from Carlsbad Village. Dedicated morning & afternoon air-conditioned shuttle stops at Pacific Ridge & Coastal Mall.</p>
        </div>
        """
    elif c_type == "sibling":
        inner_content = """
        <div class="card" style="margin-bottom:20px; background:#F0FDFA; border:2px solid #5EEAD4; padding:28px;">
            <div style="display:flex; align-items:center; gap:16px;">
                <span style="font-size:48px;">👫</span>
                <div>
                    <h3 style="margin:0; font-size:32px; font-weight:900; color:#0F172A;">Sibling Matching Active</h3>
                    <p style="margin:4px 0 0 0; font-size:24px; color:#0D9488; font-weight:700;">Child 1 (Age 7) &amp; Child 2 (Age 11) &middot; Same Location &amp; Sessions</p>
                </div>
            </div>
        </div>
        
        <div style="font-weight:900; font-size:32px; color:#1A1A2E; margin-bottom:16px;">Side-by-Side Comparison</div>
        
        <div class="compare-table">
            <div class="compare-col">
                <div class="compare-head" style="background:#FFF1F2;">
                    <div style="font-size:20px; color:#E11D48; font-weight:900;">OPTION A</div>
                    <div style="font-weight:900; font-size:28px; margin-top:4px;">iD Tech Robotics</div>
                </div>
                <div class="compare-row"><strong>Ages:</strong> 7 – 17 yrs</div>
                <div class="compare-row"><strong>Sibling Fit:</strong> <span style="color:#16A34A; font-weight:800;">✅ Both Fit</span></div>
                <div class="compare-row"><strong>Schedule:</strong> 8:30 AM – 5:30 PM</div>
                <div class="compare-row"><strong>Care:</strong> Before + After Care</div>
                <div class="compare-row"><strong>Shuttle:</strong> 🚌 Bus Included</div>
                <div class="compare-row"><strong>Meals:</strong> 🥪 Hot Lunch Included</div>
                <div class="compare-row"><strong>Refund:</strong> 100% Flexible</div>
                <div class="compare-row"><strong>Activities:</strong> AI, LEGO, Coding</div>
                <div class="compare-row"><strong>Cost:</strong> $$ (Mid-Range)</div>
            </div>
            <div class="compare-col">
                <div class="compare-head" style="background:#F0FDFA;">
                    <div style="font-size:20px; color:#0D9488; font-weight:900;">OPTION B</div>
                    <div style="font-weight:900; font-size:28px; margin-top:4px;">Camp Ocean Pines</div>
                </div>
                <div class="compare-row"><strong>Ages:</strong> 7 – 16 yrs</div>
                <div class="compare-row"><strong>Sibling Fit:</strong> <span style="color:#16A34A; font-weight:800;">✅ Both Fit</span></div>
                <div class="compare-row"><strong>Schedule:</strong> 9:00 AM – 4:00 PM</div>
                <div class="compare-row"><strong>Care:</strong> Extended Available</div>
                <div class="compare-row"><strong>Shuttle:</strong> ❌ Parent Drop-off</div>
                <div class="compare-row"><strong>Meals:</strong> 🍎 Bring Sack Lunch</div>
                <div class="compare-row"><strong>Refund:</strong> 14-Day Notice</div>
                <div class="compare-row"><strong>Activities:</strong> Nature, Ocean, Lab</div>
                <div class="compare-row"><strong>Cost:</strong> $$ (Mid-Range)</div>
            </div>
        </div>

        <div style="margin-top:24px; margin-bottom:16px;">
            <button class="btn-primary">📋 Export Sibling Schedule & Calendar</button>
        </div>

        <div class="card" style="padding:22px; background:#F8FAFC; margin-bottom:16px;">
            <div style="font-weight:800; font-size:24px; color:#0F172A;">💡 Coordination Tip for Parents</div>
            <p style="font-size:20px; color:#64748B; margin-top:4px;">Both camps offer matching drop-off at 8:30 AM in Carlsbad, allowing 1 single morning trip for both kids!</p>
        </div>

        <div class="card" style="padding:22px; background:#F8FAFC;">
            <div style="font-weight:800; font-size:24px; color:#0F172A;">📅 Calendar Sync Ready</div>
            <p style="font-size:20px; color:#64748B; margin-top:4px;">One-tap export directly to Apple Calendar or iCal format with automated session reminder notifications.</p>
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
                background: #F8FAFC;
                display: flex;
                flex-direction: column;
                align-items: center;
                overflow: hidden;
            }}
            .marketing-header {{
                width: 100%;
                padding: 60px 50px 24px 50px;
                text-align: center;
                background: linear-gradient(180deg, #FFFFFF 0%, #F8FAFC 100%);
            }}
            .badge-top {{
                display: inline-block;
                background: #E6FAF8;
                color: #0D9488;
                font-size: 26px;
                font-weight: 800;
                padding: 10px 26px;
                border-radius: 30px;
                margin-bottom: 14px;
                letter-spacing: 0.5px;
                border: 1px solid #99F6E4;
            }}
            .headline {{
                font-size: 60px;
                font-weight: 900;
                color: #0F172A;
                line-height: 1.15;
                letter-spacing: -1px;
                margin-bottom: 10px;
            }}
            .subheadline {{
                font-size: 30px;
                font-weight: 500;
                color: #64748B;
                line-height: 1.35;
                max-width: 1100px;
                margin: 0 auto;
            }}
            .mockup-container {{
                width: 1200px;
                flex: 1;
                background: #FFFFFF;
                border-top-left-radius: 54px;
                border-top-right-radius: 54px;
                box-shadow: 0 -15px 50px rgba(0,0,0,0.06);
                padding: 34px 36px 0 36px;
                border: 2px solid #E2E8F0;
                border-bottom: none;
                display: flex;
                flex-direction: column;
                position: relative;
            }}
            .app-nav {{
                display: flex;
                align-items: center;
                justify-content: space-between;
                margin-bottom: 18px;
                padding-bottom: 14px;
                border-bottom: 1.5px solid #F1F5F9;
            }}
            .app-title {{
                font-size: 40px;
                font-weight: 900;
                letter-spacing: -0.5px;
            }}
            .card {{
                background: #FFFFFF;
                border-radius: 26px;
                padding: 26px;
                box-shadow: 0 4px 20px rgba(0,0,0,0.03);
                border: 1.5px solid #E2E8F0;
            }}
            .field label {{
                font-size: 22px;
                font-weight: 800;
                color: #64748B;
                letter-spacing: 0.5px;
            }}
            .input-box {{
                margin-top: 8px;
                background: #F8FAFC;
                border: 2px solid #CBD5E1;
                padding: 16px 22px;
                border-radius: 20px;
                font-size: 30px;
                font-weight: 700;
                color: #0F172A;
            }}
            .pill-red {{
                background: #FEE2E2;
                color: #EF4444;
                font-size: 26px;
                font-weight: 800;
                padding: 6px 18px;
                border-radius: 20px;
            }}
            .slider-track {{
                margin-top: 14px;
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
                width: 38px;
                height: 38px;
                background: #FFFFFF;
                border: 5px solid #FF6B6B;
                border-radius: 50%;
                position: absolute;
                top: -11px;
                transform: translateX(-50%);
                box-shadow: 0 4px 10px rgba(0,0,0,0.15);
            }}
            .tags {{
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                margin-top: 10px;
            }}
            .tag {{
                background: #F1F5F9;
                color: #334155;
                font-size: 23px;
                font-weight: 700;
                padding: 10px 20px;
                border-radius: 16px;
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
                font-size: 28px;
                font-weight: 800;
                padding: 20px;
                border-radius: 22px;
                border: none;
                box-shadow: 0 8px 25px rgba(255,107,107,0.3);
            }}
            .btn-secondary {{
                background: #F1F5F9;
                color: #334155;
                font-size: 28px;
                font-weight: 800;
                padding: 20px;
                border-radius: 22px;
                border: 1.5px solid #CBD5E1;
            }}
            .camp-card {{
                background: #FFFFFF;
                border: 1.5px solid #E2E8F0;
                border-radius: 24px;
                padding: 24px;
                margin-bottom: 16px;
                box-shadow: 0 4px 16px rgba(0,0,0,0.02);
            }}
            .camp-header {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 8px;
            }}
            .badge-aca {{
                background: #FEF3C7;
                color: #92400E;
                font-size: 20px;
                font-weight: 800;
                padding: 6px 14px;
                border-radius: 12px;
            }}
            .dist {{
                font-size: 22px;
                font-weight: 800;
                color: #64748B;
            }}
            .camp-title {{
                font-size: 30px;
                font-weight: 900;
                color: #0F172A;
                margin-bottom: 6px;
            }}
            .camp-loc {{
                font-size: 22px;
                color: #64748B;
                margin-bottom: 12px;
            }}
            .camp-meta {{
                display: flex;
                gap: 10px;
                margin-bottom: 10px;
            }}
            .meta-item {{
                background: #F8FAFC;
                border: 1px solid #E2E8F0;
                padding: 6px 14px;
                border-radius: 12px;
                font-size: 20px;
                font-weight: 700;
                color: #334155;
            }}
            .camp-desc {{
                font-size: 22px;
                color: #475569;
                line-height: 1.45;
            }}
            .detail-grid {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 14px;
                margin: 18px 0;
            }}
            .grid-box {{
                background: #F8FAFC;
                padding: 16px 18px;
                border-radius: 18px;
                border: 1px solid #E2E8F0;
            }}
            .grid-box .lbl {{
                display: block;
                font-size: 19px;
                color: #64748B;
                font-weight: 800;
            }}
            .grid-box .val {{
                font-size: 24px;
                color: #0F172A;
                font-weight: 800;
                margin-top: 4px;
            }}
            .session-row {{
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 14px 18px;
                background: #F8FAFC;
                border-radius: 16px;
                margin-top: 8px;
                font-size: 22px;
                border: 1px solid #F1F5F9;
            }}
            .tag-green {{
                background: #DCFCE7;
                color: #166534;
                font-size: 19px;
                font-weight: 800;
                padding: 5px 12px;
                border-radius: 10px;
            }}
            .tag-orange {{
                background: #FFEDD5;
                color: #9A3412;
                font-size: 19px;
                font-weight: 800;
                padding: 5px 12px;
                border-radius: 10px;
            }}
            .compare-table {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 14px;
                margin-top: 12px;
            }}
            .compare-col {{
                background: #FFFFFF;
                border-radius: 22px;
                border: 1.5px solid #CBD5E1;
                overflow: hidden;
            }}
            .compare-head {{
                padding: 18px 14px;
                text-align: center;
                border-bottom: 1.5px solid #E2E8F0;
            }}
            .compare-row {{
                padding: 14px 14px;
                font-size: 20px;
                border-bottom: 1px solid #F1F5F9;
                color: #334155;
            }}
            .tab-bar {{
                position: absolute;
                bottom: 0;
                left: 0;
                right: 0;
                background: #FFFFFF;
                border-top: 1.5px solid #E2E8F0;
                padding: 22px 40px 30px 40px;
                display: flex;
                justify-content: space-around;
                align-items: center;
            }}
            .tab-item {{
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 6px;
                font-size: 22px;
                font-weight: 800;
                color: #94A3B8;
            }}
            .tab-item.active {{
                color: #FF6B6B;
            }}
            .home-bar {{
                width: 320px;
                height: 8px;
                background: #0F172A;
                border-radius: 4px;
                margin: 16px auto 4px auto;
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
                    <span style="font-size:34px;">📍</span>
                    <span class="app-title"><span style="color:#FF6B6B;">Camp</span><span style="color:#4ECDC4;">Find</span></span>
                </div>
                <div style="font-size:22px; font-weight:800; color:#64748B; background:#F1F5F9; padding:8px 18px; border-radius:14px;">
                    🇺🇸 English
                </div>
            </div>
            <div style="padding-bottom:140px;">
                {inner_content}
            </div>
            
            <div class="tab-bar">
                <div style="display:flex; justify-content:space-around; width:100%;">
                    <div class="tab-item active">
                        <span style="font-size:30px;">🔍</span>
                        <span>Search</span>
                    </div>
                    <div class="tab-item">
                        <span style="font-size:30px;">🗺️</span>
                        <span>Map</span>
                    </div>
                    <div class="tab-item">
                        <span style="font-size:30px;">⚖️</span>
                        <span>Compare</span>
                    </div>
                    <div class="tab-item">
                        <span style="font-size:30px;">❤️</span>
                        <span>Favorites</span>
                    </div>
                </div>
            </div>
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

            # Resize for iPhone 5.5" (1242x2208)
            out_5_5 = os.path.join(OUTPUT_DIR, f"0{idx}_iphone_5_5_inch_1242x2208.png")
            img.resize((1242, 2208), Image.Resampling.LANCZOS).save(out_5_5, "PNG")
            print(f"Generated: {out_5_5}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
