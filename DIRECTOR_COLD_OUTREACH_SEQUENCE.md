# CampFind 營隊負責人 B2B 合作開發信件庫 (Director Cold Outreach Sequence)

本開發信件序列專為寄送給 CampFind 資料庫中的 **5,012 位營隊負責人 (Camp Directors)** 設計。
文案採用美國商業開發中轉換率最高的 **3-Touch Sequence（三階段漸進式開發法）**，旨在：
1. **建立信任**：告知其營地已被收錄，邀請免費核對資訊（降低防備心）。
2. **激發付費慾望**：介紹 **$99/年 官方認證夥伴 (Verified Partner)** 權益，導流至 `https://campfind-app.netlify.app/claim.html`。
3. **創造緊迫感**：釋出 **$299/季 地區唯一精選贊助位 (Featured Sponsor)**，促成即時線上刷卡。

---

## 郵件一：免費收錄通知與認領邀請 (Initial Inclusion Notice)
> **發信時機**：Day 1  
> **目標**：取得最高開信率 (Open Rate > 45%)，促使負責人點擊認領連結。  
> **動態變數**：`{{camp_name}}`, `{{city}}`, `{{state}}`, `{{director_name}}`

### Email 1 範本:
```text
Subject: Action Needed: {{camp_name}} listing in CampFind 2026 Directory

Hi {{director_name}},

I hope you’re having a productive planning season for Summer 2026!

I’m reaching out from CampFind (https://campfind-app.netlify.app), a national summer and seasonal camp discovery platform used by thousands of parents across the US.

As part of our 2026 directory update, we have indexed {{camp_name}} in our {{city}}, {{state}} regional directory so local families can discover your sessions, location, and age offerings.

Because thousands of parents in {{city}} are actively planning their summer schedules right now, we want to ensure your profile is 100% accurate.

Could you take 60 seconds to review your listing and confirm your 2026 tuition and open seats?

👉 Verify or Claim your listing here: 
https://campfind-app.netlify.app/claim.html?camp={{camp_name_encoded}}

There is zero cost to claim your free basic listing. If you need to update registration links or session dates, simply submit the form and our team will update it within 24 hours.

Best regards,

CampFind Partnerships Team
Clarity Clinical Solutions LLC
support@campfind.org | https://campfind-app.netlify.app

---
To opt out of future directory notices, reply with "unsubscribe".
```

---

## 郵件二：家長流量與官方藍勾勾夥伴升級 (Value & Social Proof)
> **發信時機**：Day 4（若負責人未回覆或未認領）  
> **目標**：介紹 **$99/年 Verified Partner** 方案，強調家長直接報名點擊率提升 4 倍。

### Email 2 範本:
```text
Subject: Drive direct registrations for {{camp_name}} this summer

Hi {{director_name}},

Following up on my previous note regarding {{camp_name}}'s profile on CampFind.

As local parents in {{city}} compare camps for their kids, profiles with our blue **"Verified Partner"** trust badge receive over 4x more clicks to their official registration pages.

For active camp organizers, we offer the **CampFind Verified Partner** status ($99/year — 100% tax-deductible promotional expense):

What you receive:
🛡️ Official "Verified Partner" trust badge on search results and map pins
🔗 Direct, prominent "Register on Official Website" button linking straight to your enrollment portal
📞 Priority director contact card (direct phone, email, and real-time open seats alert)
⚡ Updates anytime your sessions sell out or add new weeks

You can activate your Verified Partner status directly via our secure Stripe portal:
👉 https://campfind-app.netlify.app/claim.html?camp={{camp_name_encoded}}

If you prefer an invoice (Net 30) for your organization's accounting, just reply to this email with your preferred billing details.

Warmly,

CampFind Director Relations
Clarity Clinical Solutions LLC
https://campfind-app.netlify.app/claim.html

---
To opt out of future directory notices, reply with "unsubscribe".
```

---

## 郵件三：地區精選贊助位限額釋出 (Scarcity & Top Placement)
> **發信時機**：Day 8  
> **目標**：針對有行銷預算的品牌營隊，推廣 **$299/季 Featured Sponsor**。

### Email 3 範本:
```text
Subject: Exclusive featured placement in {{city}} for {{camp_name}}

Hi {{director_name}},

Camp registrations in {{state}} are starting to accelerate as parents finalize their June & July schedules.

We are currently reserving the **Top Pinned "Featured Sponsor"** placement for the {{city}} region on CampFind. 

As the Featured Sponsor ($299/quarter):
⭐ Your camp is pinned to the very top of search results and map views in {{city}}
📈 Guaranteed 5x higher impression volume than standard listings
📢 Dedicated Director Spotlight feature

Because we limit featured spots to ensure high ROI for our partners, this placement is available on a first-come, first-served basis.

If you’d like {{camp_name}} to claim the top spot in {{city}}, you can secure it here today:
👉 https://campfind-app.netlify.app/claim.html?camp={{camp_name_encoded}}

Happy to answer any questions or set up a corporate invoice if needed!

Best,

CampFind Partnerships Team
Clarity Clinical Solutions LLC
```
