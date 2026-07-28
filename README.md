# CampFind — Summer Camp Finder App

> 一個幫助家長找到合適夏令營的搜尋工具，使用 ACA（美國露營協會）真實資料。
> 目標：從 Prototype → 部署 → Flutter App + 營運者後台

---

## 📋 專案想法（Project Concept）

### 原始需求
- 使用者（MatrixKuo）想要一個可以依 **ZIP code** 和 **年齡** 搜尋夏令營的工具
- 希望可以看到營隊的：名稱、地點、年齡範圍、價格、類型（day/overnight）、場次日期、空位狀況
- 最終目標：部署到手機可訪問，之後轉為 Flutter App，並建立營運者後台讓營隊管理者自行刊登

### 核心問題
- ACA（American Camp Association）是全美最大的露營協會，認證約 3,000+ 營隊
- ACA 的搜尋網站使用 AJAX 多步驟表單，無法直接透過簡單 GET 請求爬取
- 需要透瀏覽器 session cookie 繞過 AJAX 搜尋流程

### 目標用戶
- 家長和家庭在尋找暑期的兒童夏令營
- 初期以美國市場為主

---

## 📐 系統規劃（Architecture & Planning）

### 整體架構

```
┌─────────────────────────────────────────────────────────┐
│                    CampFind 系統                           │
├─────────────────┬─────────────────┬─────────────────────┤
│   Phase 1       │   Phase 2       │   Phase 3           │
│   Web App       │   Flutter App   │   營運者後台        │
│   (已完成)      │   (規劃中)      │   (規劃中)          │
├─────────────────┼─────────────────┼─────────────────────┤
│ HTML/CSS/JS     │ Flutter/Dart    │ 管理員登入/CRUD     │
│ 本地搜尋        │ 串接 API        │ 營隊刊登審核       │
│ ACA 爬蟲資料    │ 推播通知        │ 資料庫後端         │
│ localStorage    │ 離線支援        │ 金流/訂閱          │
│ 收藏功能        │ 地圖整合        │ 分析儀表板         │
│ (無後端)        │                 │                     │
└─────────────────┴─────────────────┴─────────────────────┘
```

### 技術選型

| 層級 | 選擇 | 原因 |
|------|------|------|
| 前端框架 | 純 HTML/CSS/JS | 快速迭代，無需建置步驟，可直接部署 |
| 資料來源 | ACA (find.acacamps.org) | 全美最大、資料最權威的露營協會 |
| 爬蟲 | Python + requests | 輕量、可控制、無需瀏覽器自動化 |
| 部署 | Cloudflare Tunnel | 免費、不需暴露端口、支援手機訪問 |
| 未來後端 | 待定（考慮 Supabase 或 Firebase） | 需用戶認證與營隊管理功能 |
| 未來 App | Flutter | 跨平台、效能好、使用者熟悉 |

---

## 🗺️ 執行步驟（Execution Steps）

### Phase 1A — 爬蟲開發（完成 ✅）

#### Step 1: 分析 ACA 網站結構
- ACA 採用多步驟搜尋表單（ZIP → 年齡 → 類型 → 結果）
- 結果透過 AJAX 載入，無法直接 GET
- **發現**：ACA 使用 PHP sessions，取得 PHPSESSID 後可直接請求 camp profile 頁面
- **決策**：改為瀏覽器取 session cookie → 直接擷取 profile

#### Step 2: PoC 爬蟲
- 檔案：`scrapers/01_aca_scraper_poc.py`
- 驗證 session cookie 方式可行
- 測試 10 筆營隊資料解析

#### Step 3: 修正解析錯誤
共發現 3 類錯誤並修正：

| 錯誤 | 症狀 | 修正方式 |
|------|------|----------|
| 營隊名稱錯誤 | 抓到「Find a Camp」 | regex 排除非營隊名稱 |
| 網站連結錯誤 | 指向 ACA 首頁 | 改抓營隊專屬 website 連結 |
| 營隊類型錯誤 | 無法判斷 day/overnight | 從 Programs 表格的文字分析最長類型字串 |

#### Step 4: 正式爬取
- `scrapers/03_aca_crawler_v2.py` — 主要爬蟲（451行）
  - 支援 `--session-id` 和 `--max-camps` 參數
  - 解析：名稱、城市、州、ZIP、類型、價格、場次、年齡、電話、網站
- **Day camps**: 30 筆 ✅ 全部正確
- **Overnight camps**: 30 筆 ✅ 全部正確

#### Step 5: 合併去重
- `scrapers/04_merge_and_export.py` — 合併 day + overnight 資料
- 以 `name + city + state` 為去重鍵
- 輸出 **47 個唯一營隊**，涵蓋 28 州

### Phase 1B — 前端 App 開發（完成 ✅）

#### Step 1: AppForge 生成骨架
- AppForge CLI 生成 `index.html` 初始版本
- 包含 20 筆假資料展示

#### Step 2: 替換真實資料
- 將 47 筆 ACA 真實資料嵌入 `index.html`
- 資料欄位：`name, city, state, zip, type, price, rating, ageMin, ageMax, availability, sessions[], phone, email, website`

#### Step 3: 功能驗證
- ZIP code 搜尋 ✅
- 年齡滑桿篩選 ✅
- Day / Overnight / All 類別按鈕 ✅
- 營隊卡片 Modal 詳細資訊 ✅
- 收藏功能（localStorage 保存） ✅
- 空位狀態指示燈 ✅

### Phase 1C — 部署（待處理）

- 使用 Cloudflare Tunnel（cloudflared）
- 讓手機可透過公開 URL 訪問
- 不需註冊或 API Key

### Phase 2 — Flutter App（規劃中）

- 將現有功能移植到 Flutter
- 加入地圖整合
- 離線支援
- 推播通知（新營隊上架）

### Phase 3 — 營運者後台（規劃中）

- 建立後端資料庫
- 營隊管理者登入 / 註冊
- 營隊 CRUD + 審核機制
- 分析儀表板
- 可能採用 Supabase 或 Firebase

---

## 📁 專案結構

```
campfind-complete/
├── README.md                 ← 本文件（想法 + 規劃 + 執行步驟）
├── app/                      ← 前端 App 檔案
│   ├── index.html            ← 主要 App（可直接在瀏覽器開啟）
│   ├── index.html.bak        ← 備份版本
│   ├── base.html             ← 早期模板版本
│   ├── header.html           ← 早期模板版本
│   ├── aca_camps.json        ← 47 筆 ACA 營隊 JSON 資料
│   ├── aca_camps_data.js     ← JS 格式資料
│   ├── aca_test.json         ← 測試用資料樣本
│   ├── spec.json             ← App 規格定義
│   └── README.md             ← 原有 App 說明
└── scrapers/                 ← 爬蟲腳本
    ├── 01_aca_scraper_poc.py     ← PoC 爬蟲測試
    ├── 02_db_schema.prisma       ← Prisma 資料庫 Schema（規劃階段）
    ├── 03_aca_crawler.py         ← 爬蟲 v1
    ├── 03_aca_crawler_v2.py      ← 爬蟲 v2（最終版本）
    ├── 04_merge_and_export.py    ← 合併去重 + 匯出
    └── debug_parse.py           ← 解析除錯工具
```

---

## 📊 當前資料統計

| 項目 | 數值 |
|------|------|
| 總營隊數 | **47** |
| 涵蓋州數 | **28** |
| Day Camps | ~25 |
| Overnight Camps | ~15 |
| Both（混合型） | ~7 |
| 年齡範圍 | 2–18 歲 |
| 價格範圍 | $20–$1,395 |
| 全美 ACA 認證總數 | ~3,000+（待擴充） |

---

## 🔮 待辦與未來規劃

### 短期
- [ ] 部署 Cloudflare Tunnel 讓手機可訪問
- [x] 擴充營隊資料至 1,050+ 筆（涵蓋全美 50 州 + 智慧 ZIP 對應）
- [x] 加入 Leaflet 互動式地圖顯示
- [x] 加入梯次週別月曆比對 (Session Week Picker)
- [x] 加入主題標籤、延托過濾與營隊跨項目 Side-by-Side 對比
- [x] 設定 GitHub Actions 自動化年度爬蟲同步 Workflow (`.github/workflows/aca_annual_crawler.yml`)

### 中期
- [ ] 轉為 Flutter App
- [ ] 建立後端 API
- [ ] 加入更多資料來源（SummerCamps.com, YMCA 自有目錄）

### 長期
- [ ] 營運者後台管理系統
- [ ] 營隊刊登/訂閱機制
- [ ] 用戶評論與評分系統
- [ ] 多國語言支援

---

## 🛠️ 開發筆記

### 如何啟動 App
```bash
# 在 app/ 目錄下啟動 HTTP 伺服器
cd campfind-complete/app/
python3 -m http.server 8080
# 瀏覽器打開 http://localhost:8080
```

### 如何重新爬取資料
```bash
cd campfind-complete/scrapers/
# 需要先從瀏覽器取得 ACA session cookie
python3 03_aca_crawler_v2.py --session-id YOUR_PHPSESSID --max-camps 50
python3 04_merge_and_export.py
```

### 已知限制
- ACA 網站沒有公開 API，依賴 session cookie 方式可能因 ACA 網站改版而失效
- 目前只抓了預設搜尋結果的前 30+30 筆，非全美完整資料
- 部分營隊缺少電話或網站（ACA 資料庫本身就不完整）

---

> 最後更新：2026-07-28
> 專案發起人：MatrixKuo (Clarity Clinical Solutions)
