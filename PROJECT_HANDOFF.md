# CampFind — 專案進度總結與 Project Handoff 報告
> **版本**：v1.0.0  
> **日期**：2026年7月29日  
> **專案目標**：從現有高效能 Web Prototype 推進為全功能、可上架 App Store & Google Play 的商業級夏令營/冬令營搜尋 App。

---

## 📌 一、專案總覽 (Executive Summary)

**CampFind** 是一款專為家長設計的智慧夏令營與冬令營搜尋平台，解決家長在為孩子規劃假期活動時「資訊分散、篩選困難、時間梯次衝突、手足安排繁瑣」的痛點。

### 核心價值主張 (Value Proposition)
1. **權威真實數據**：整合全美最大的美國露營協會 (ACA, American Camp Association) 認證資料，並擴充至全美 50 州 1,050+ 筆營隊資訊。
2. **極致家長體驗**：支援 ZIP Code 距離比對、年齡滑桿、早/晚延托 (Before/After Care)、接送巴士 (Shuttle)、多孩子 (Sibling) 手拉手排程比對、梯次週別月曆。
3. **四季全天候搜尋**：涵蓋暑期夏令營 (Summer Camps)、寒假滑雪/STEM 冬令營 (Winter Camps) 與春假營隊 (Spring Break Camps)。

---

## 🛠️ 二、目前開發進度總結 (Phase 1 Progress & Accomplishments)

目前 Phase 1（Web Prototype / 數據管線 / 核心功能驗證）已 **100% 完成**，具備可直接在瀏覽器與手機端順暢運行的全功能 Web App。

### 1. 前端功能模組 (Web App UI/UX)
- 📱 **流暢響應式設計**：純 Vanilla HTML5/CSS3/JavaScript 開發，零前端編譯依賴，支援手機與桌面瀏覽器。
- 🔒 **Passcode 存取控制**：內建 `passcodeOverlay` 密碼鎖，適合早期閉門測試與展演。
- 🔍 **智慧搜尋與地圖**：
  - 支持 ZIP Code (例如 `92056`, `90210`, `10001`)、城市與州別模糊搜尋。
  - 整合 **Leaflet 互動式地圖**，在地圖與清單視角 (List/Map View) 無縫切換，並自動對應經緯度 Pin。
- 🎯 **多維度進階篩選器**：
  - **年齡滑桿** (2 ~ 18 歲) & **手足模式 (Sibling Mode)**（同步比對兩位不同年齡孩子的共同營隊）。
  - **季節切換** (Summer / Winter / Spring / All Seasons)。
  - **營隊類型** (Day Camp / Overnight / Both)。
  - **主題標籤** (STEM & Code / Sports / Arts & Drama / Outdoor / Academic)。
  - **梯次週別 (Session Week Picker)** (Week 1 ~ Week 8 精準比對)。
  - **延托與接送** (Before Care / After Care / Shuttle Bus)。
- ⚖️ **Side-by-Side 營隊跨項目對比**：支援選取 2~3 個營隊，展開詳細規格與價格比對 Modal。
- ❤️ **離線收藏功能**：基於 `localStorage` 本地保存收藏清單。
- 🌐 **多國語言支援 (i18n)**：可動態切換 English / 繁體中文 / 簡體中文 / 西班牙文介面。

### 2. 數據庫與爬蟲管線 (Data Pipeline & Automation)
- 📊 **數據庫規模**：目前包含 **1,050 筆** 全美營隊數據（包含加州 312 筆、聖地牙哥/Oceanside 92056 周邊 33 筆精準地圖點）。
- 🐍 **Python 爬蟲腳本鏈**：
  - `scrapers/01_aca_scraper_poc.py`：ACA 網站 Session Cookie 繞過驗證。
  - `scrapers/03_aca_crawler_v2.py`：ACA 多步驟表單解析與資料擷取。
  - `scrapers/04_merge_and_export.py`：自動數據去重與格式化。
  - `scrapers/05_expand_and_enrich_camps.py`：全美經緯度 Geocoding、四季屬性與延托資料補全。
- 🤖 **GitHub Actions 自動化**：
  - `.github/workflows/aca_annual_crawler.yml`：定時觸發爬蟲同步更新數據。
- 🗄️ **生產級資料庫 Schema**：
  - `scrapers/02_db_schema.prisma`：完整的 PostgreSQL + PostGIS 30-mile 幾何距離查詢 Schema（包含 User, Child, Camp, Session, Review, Claim Listing, Registration, Scraper Log 等 15+ 模型）。

---

## 📂 三、專案資產與程式碼目錄交接 (Codebase Inventory)

```
CampFind/
├── README.md                      # 專案原始說明與理念
├── PROJECT_HANDOFF.md             # 本交接文檔 (最新)
├── check_dataset.py               # 數據集結構與統計驗證工具
├── app/                           # Web App 前端主程式
│   ├── index.html                 # 前端核心頁面 (包含 UI, i18n, Map, Filters, Modal)
│   ├── aca_camps_data.js          # 1,050 筆營隊 JavaScript 前置加載數據
│   ├── aca_camps.json             # 1,050 筆營隊 完整 JSON 格式數據
│   ├── spec.json                  # 應用程式 Feature 規格檔
│   └── README.md                  # App 目錄使用說明
├── scrapers/                      # 爬蟲與數據處理工具鏈
│   ├── 01_aca_scraper_poc.py      # PoC 爬蟲測試
│   ├── 02_db_schema.prisma        # 全功能 Prisma DB Schema (PostgreSQL + PostGIS)
│   ├── 03_aca_crawler_v2.py       # 主力 ACA 爬蟲腳本
│   ├── 04_merge_and_export.py     # 數據合併去重
│   ├── 05_expand_and_enrich_camps.py # 全美地圖座標與四季屬性擴充工具
│   └── debug_parse.py            # HTML 數據解析 Debug 工具
└── .github/
    └── workflows/
        └── aca_annual_crawler.yml # GitHub Actions 自動化爬蟲更新流
```

---

## 🚀 四、APP 化與上架推進路線圖 (Path to App Store & Commercial Launch)

為了將 CampFind 正式推出至 **Apple App Store** 和 **Google Play Store**，建議採取以下 4 個階段推進：

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      CampFind 商業上架推進路線圖                          │
├───────────────────┬───────────────────┬────────────────┬────────────────┤
│ Phase 2           │ Phase 3           │ Phase 4        │ Phase 5        │
│ Mobile App 開發   │ 後端 API 與 DB     │ 營運者管理後台 │ 商業化與上架   │
├───────────────────┼───────────────────┼────────────────┼────────────────┤
│ Flutter / RN      │ Supabase / Node   │ Provider Claim │ Apple / Google │
│ 原生 Google Maps  │ PostGIS 幾何查詢  │ 營隊主更新名額 │ IAP 訂閱/廣告  │
│ 日曆同步 (iCal)   │ Auth (Google/Apple│ 早鳥優惠發布   │ 隱私政策/條款  │
│ Push Notifications│ REST/GraphQL API  │ Leads 諮詢接單 │ 移除 Preview 鎖│
└───────────────────┴───────────────────┴────────────────┴────────────────┘
```

### 階段 2：跨平台 Mobile App 開發 (Flutter / React Native)
- **建議技術選型**：**Flutter** (Dart) 或 **React Native (Expo)**。
  - *推薦 Flutter*：渲染效能極佳，地圖與卡片滑動流暢，能完美呈現極致美感的微動畫。
- **App 原生獨特功能**：
  1. 🗺️ **原生 Google Maps / Apple Maps 整合**：聚類標籤 (Clustering Pins) 與導航。
  2. 📅 **家長日曆同步 (Calendar Integration)**：一鍵把選定的營隊梯次 (Session) 寫入 iOS Calendar / Google Calendar。
  3. 🔔 **推播通知 (Push Notifications)**：熱門營隊釋出空位或早鳥優惠提醒 (Firebase Cloud Messaging)。
  4. 📶 **離線使用與快取**：本地 SQLite/Hive 快取，離線瀏覽已收藏營隊。

### 階段 3：雲端後端與資料庫建置 (Backend & Database)
- **建議技術選型**：**Supabase** (代管 PostgreSQL + PostGIS) 或 **Firebase**。
  - 直接將 `scrapers/02_db_schema.prisma` 部署至 Supabase。
  - **核心 API 模組**：
    - `POST /api/v1/auth`: 家長 Google/Apple 第三方登入。
    - `GET /api/v1/camps/search`: 支援 `lat`, `lng`, `radius_miles`, `age`, `season`, `week`, `care_options` 的 PostGIS 空間查詢。
    - `POST /api/v1/user/favorites`: 跨裝置同步收藏。
    - `POST /api/v1/user/children`: 紀錄手足資料（年齡、興趣、排程）。

### 階段 4：營運者 / 營隊主管理後台 (Camp Director Portal)
- 建立 Web 管理面板（例如使用 Next.js 或 React Admin）：
  - **Camp Claim 機制**：營隊主經身份審核後認領自己的營隊。
  - **即時庫存更新 (Real-time Availability)**：營隊主可自行修改梯次剩餘名額 (Open / Almost Full / Waitlist / Full)。
  - **早鳥與優惠券發布**：發布獨家折扣吸引家長直接下單或諮詢。

### 階段 5：商業化模式與上架合規審查 (Store Compliance & Monetization)
1. **商業模式 (Monetization Models)**：
   - **B2C 家長端 (Freemium / Pro 訂閱)**：免費搜尋；Pro 會員享有「熱門營隊名額即時推播」、「手足排程智慧最佳化」、「專屬折扣碼」。
   - **B2B 營隊端 (Sponsored Ads & Featured Listing)**：營隊付費刊登首頁精選、搜尋優先置頂、Leads 諮詢導流。
2. **App Store & Google Play 上架準備**：
   - 🔒 移除前置 `passcodeOverlay` 密碼鎖，改為正式應用主頁。
   - 📜 準備 **Privacy Policy (隱私權政策)** 與 **Terms of Service (服務條款)**（包含 COPPA 兒童隱私合規聲明）。
   - 🆔 集成 Apple Sign-in (iOS 強制要求) 與 App In-Purchase (IAP) 訂閱機制。
   - 🛡️ 完善 Data Safety / App Privacy 填報與帳號註銷 (Account Deletion) 功能。

---

## 📋 五、立即執行的下一步行動清單 (Immediate Action Checklist)

- [ ] **Step 1: 確定 Mobile App 技術選型**（推薦 Flutter 或 React Native），初始化 App 專案骨架。
- [ ] **Step 2: 建立 Supabase / PostgreSQL 資料庫**，套用 `scrapers/02_db_schema.prisma` 結構並匯入 `app/aca_camps.json` 1,050 筆數據。
- [ ] **Step 3: 封裝 RESTful / GraphQL API 接口**（包含距離查詢、多條件過濾）。
- [ ] **Step 4: 移動端 UI 移植**（將現有 `index.html` 之設計語言、卡片 Modal、手足模式、週別 Picker 轉為原生地圖與元件）。
- [ ] **Step 5: 集成 Firebase Push Notification & 蘋果/谷歌登入**。
- [ ] **Step 6: 部署 Camp Director 認領與編輯後台**。
- [ ] **Step 7: 進行 iOS / Android 雙平台打包與 Store 上架測試**。

---
*本報告由 Antigravity 團隊生成，專案可隨時交接給開發團隊或 AI 代理人繼續執行 Phase 2 移動端開發。*
