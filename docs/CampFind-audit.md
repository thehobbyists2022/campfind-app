# CampFind 安全與真實性審計報告

- **專案**: CampFind — Summer & Winter Camp Finder
- **位置**: `C:\Users\Matrixkuo\Desktop\Antigravity\APP Design\CampFind`
- **審計者**: opencode（依 `ai-generated-code-security-auditor` + `reality-checker` 方法論）
- **審計模式**: 本地靜態掃描（未上傳任何資料）
- **日期**: 2026-08-19
- **狀態**: NEEDS WORK（尚未達到 production-ready）

---

## 執行摘要

CampFind 是一個多端點專案：**web App**（`app/`，Vanilla HTML/JS + Leaflet，Phase 1 主要產品）、**Flutter Android App**（`mobile/`，Phase 2 未完成）、以及 **Python 爬蟲**（`scrapers/`，從外部 ACA 網站抓取營隊資料）。

審計發現 **1 個 CRITICAL（簽章密碼硬編碼）、1 個 HIGH（假付款）、多個 MEDIUM（XSS、缺 CSP、明碼流量、Firebase 未接）**。其中簽章與假付款問題已於本報告撰寫時由 opencode 協助改進（見「已執行的修正」）。

---

## 🔴 CRITICAL — 簽章金鑰密碼硬編碼且極弱

**位置**: `mobile/android/app/build.gradle.kts`

```kotlin
storePassword = "123456"
keyPassword = "123456"
```

- 這是 **Google Play 正式 release 簽章**
- 密碼為 `123456`（極弱），且**硬編碼在原始碼**中
- 風險: 任何人取得 repo / keystore 檔即可偽造 App 更新，劫持使用者

**修正（已執行）**:
- 密碼從 `build.gradle.kts` 移出，改讀 `key.properties`（已被 `.gitignore` 排除）
- 建立 `mobile/android/key.properties`（佔位符 `CHANGE_ME_...`）

**⚠️ 待辦（使用者必須親自完成，屬金鑰安全操作）**:
1. 用 Android Studio 產生**新的 keystore**，設定強密碼
2. 更新 `key.properties` 指向新檔與新密碼
3. 刪除舊的 `mobile/upload-keystore.jks`
4. 在 Google Play Console 上傳新的 upload key
5. **務必在正式上架前完成**（上架後金鑰不可更換）

---

## 🟠 HIGH — 假付款（Vibe Coding 典型）— ✅ 已移除

**原位置**: `mobile/lib/widgets/paywall_modal.dart:203-212`（檔案現已刪除）

原「Unlock Pro」按鈕的 `onPressed` 沒有真實付款，點下去就直接「解鎖」：
```dart
onPressed: () {
  // Trigger In-App Purchase / Free Trial
  Navigator.pop(context, true);
  ScaffoldMessenger.of(context).showSnackBar(
    const SnackBar(content: Text('🎉 Pro Features Unlocked! ...')),
  );
},
```

- **原問題**: 沒有呼叫任何真實付款（無 RevenueCat、無 Google Play Billing）；若上架 Google Play = **商店條款違規**

**修正（已執行）**:
- 因目前不向顧客收費，已將**整個付費設計移除**：
  1. 刪除 `mobile/lib/widgets/paywall_modal.dart`
  2. `home_screen.dart` 移除 `_isProUser`、`_openPaywall()`、`PRO` 標籤與付款 gate
  3. Sibling Mode 改為**免費開放**（不再有收費門檻）
- 備份: `home_screen.dart.bak-20260819-164239`、`paywall_modal.dart.bak-20260819-164239`
- **後續**: `pubspec.yaml` 中的 `purchases_flutter` 依賴已無用途，可於下次建置前一併移除（本次未動 pubspec 以免中斷建置）

---

## 🟠 HIGH — Stored XSS（web App）

**位置**: `app/index.html` — 4 個 `innerHTML` 插入點（`campGrid` L1268、map popup、`compareTable`、`modalBody` L1468）

**機制**:
- `aca_camps_data.js`（3.8MB）由**外部爬蟲** `scrapers/v3_export.py` 生成 → 資料**不受信任**
- 資料欄位（`name`/`city`/`state`/`description`/`phone`/`theme`/`type` 等）被直接插入 `innerHTML` 且**未轉義**
- 攻擊者污染任一個 camp 的 `description`/`name`（例如嵌入 `<img src=x onerror=alert(1)>`）即觸發 stored XSS

**修正（已執行）**:
- 新增 `escapeHtml()` 工具函數，套用至所有 4 個 innerHTML 插入點的資料欄位
- 包含 grid、map popup、compare table、details modal

---

## 🟠 MEDIUM — 缺少 CSP（Content Security Policy）

**問題**: 無安全標頭設定，一旦 XSS 存在即無止血層。

**修正（已執行）**:
- 新增 `app/_headers`（Netlify 安全標頭 + CSP）
- 在 `index.html` `<head>` 加入 CSP `<meta>` tag（跨主機防禦）
- 同時設置 `X-Content-Type-Options`、`X-Frame-Options: DENY`、`Referrer-Policy`、`Permissions-Policy`

---

## 🟡 MEDIUM — 其他觀察

1. **`usesCleartextTraffic="true"`**（`mobile/.../AndroidManifest.xml:30`）— 允許明文 HTTP。建議改為 `false` 並全面使用 HTTPS。
2. **Firebase 未實際接入** — `mobile/pubspec.yaml` 宣告 Firebase（auth/firestore/messaging）但 Dart 程式碼**全未 import/初始化**，且**無 `google-services.json`**。功能未完成，若無意使用應自依賴移除。
3. **Google Maps 未實際接入** — 與 Firebase 相同，宣告但未實作。
4. **RevenueCat 未實際接入** — 與假付款問題相關。

---

## 🟢 良好面

- web App 與爬蟲**未發現硬編碼 API key / token**
- `getSafeWebsiteUrl()` 有強制 https 的 scheme 白名單
- no-cache 標頭已設定
- `tel:` 連結經 `escapeHtml` 處理
- `mobile/.gitignore` 已正確排除金鑰檔（`*.jks`、`key.properties`）

---

## 已執行的修正清單

| # | 檔案 | 修正 |
|---|------|------|
| 1 | `mobile/android/app/build.gradle.kts` | 移除硬編碼簽章密碼，改讀 `key.properties` |
| 2 | `mobile/android/key.properties` | 新增（佔位符，已 gitignore） |
| 3 | `app/index.html` | 新增 `escapeHtml()` + 套用至所有 innerHTML |
| 4 | `app/index.html` | 新增 CSP `<meta>` tag |
| 5 | `app/_headers` | 新增安全標頭 + CSP（Netlify） |
| 6 | `mobile/lib/widgets/paywall_modal.dart` | **刪除**（移除假付款設計） |
| 7 | `mobile/lib/screens/home_screen.dart` | 移除 `_isProUser` / `_openPaywall` / PRO 標籤 / 付款 gate，Sibling Mode 免費開放 |
| 8 | `mobile/.../AndroidManifest.xml` | 移除未使用的 `ACCESS_FINE_LOCATION`、`ACCESS_COARSE_LOCATION`、`CALL_PHONE` 權限（保留 INTERNET） |

**備份**:
- `app/index-auditbackup-20260819-124655.html`
- `mobile/lib/screens/home_screen.dart.bak-20260819-164239`
- `mobile/lib/widgets/paywall_modal.dart.bak-20260819-164239`
- `mobile/android/app/src/main/AndroidManifest.xml.bak-20260819-164239`

---

## 追蹤事項（尚未完成）

- [ ] 使用者輪換 Google Play 簽章金鑰（見 CRITICAL）
- [ ] 關閉 `usesCleartextTraffic`（`AndroidManifest.xml` 仍為 `true`）
- [ ] 自 `pubspec.yaml` 移除不再使用的 `purchases_flutter` 依賴（收費設計已刪除）
- [ ] 決定 Firebase / Google Maps 是否保留並實作，否則自依賴移除
- [ ] 用瀏覽器實際驗證 web App 在加 CSP 後功能正常（Leaflet 地圖、比較、「查看詳情」modal）
- [ ] 對 `scrapers/` 爬蟲本身做獨立審計（資料來源可信度、API 用量）

---

*本報告僅為靜態程式碼審計，未執行實機建置與運行測試。CSP 與 XSS 修正需在實際部署環境做功能回歸測試。*
