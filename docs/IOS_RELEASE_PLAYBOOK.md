# Flutter iOS → App Store 標準上架工作流（可重用 Playbook）

> 這份是從實際成功上架（CampFind）過程中整理出的**可重用流程**。
> 之後任何 Flutter App（例：TaiwanBites）都能直接套用，避免重蹈覆轍。
> 適用條件：本機是 Windows、無 macOS，全靠 GitHub Actions（`macos-latest`）雲端出包。

---

## 0. 一次性前置準備（每個 App 首次要做一次）

### A. Apple Developer 帳號（需已付費 $99/年）
- `developer.apple.com` → **Certificates, Identifiers & Profiles → Identifiers → ＋**
- 建立 App ID：填入 **Bundle ID**（如 `com.thehobbyists.<app>`）→ 存。
- 帳戶需有 **Admin / App Manager** 角色（通常是 Account Holder）。

### B. App Store Connect 建立 App 記錄
- `appstoreconnect.apple.com` → **My Apps → ＋ → 新 App**
- 填：名稱、主要語言、Bundle ID、SKU → 建立。
- 注意：**免費 App + TestFlight 測試**不需要填協定/稅務/銀行（那是「上架販售」才要）。

### C. App Store Connect API Key（CI 上傳憑證，每帳號一次）
- `appstoreconnect.apple.com` → **Users and Access → Integrations → App Store Connect API → ＋**
- 角色勾 **App Manager** → 產生 → **下載 `.p8`**、記下 **Key ID** + **Issuer ID**。

### D. 私有簽名 repo（fastlane match 存放證書，避免「每次生成 → 撞 2 張上限」）
- 建立私有 repo，例如：`gh repo create <owner>/<app>-signing --private`
- 建立 **fine-grained PAT**：`github.com/settings/personal-access-tokens/new`
  - 選該 **私有 repo** → **Contents: Read and write** → 產生 → 複製 token。

### E. 設定 GitHub repo Secrets（Actions）
```
APP_STORE_CONNECT_KEY_ID       = <Key ID>
APP_STORE_CONNECT_ISSUER_ID    = <Issuer ID>
APP_STORE_CONNECT_PRIVATE_KEY  = <.p8 完整內容>
MATCH_GIT_TOKEN                = <fine-grained PAT>
MATCH_PASSWORD                 = <自訂強密碼，證書加密用>
```

---

## 1. 放入 2 個檔案（範本，改 3 個值）

### `.github/workflows/build_ios.yml`
```yaml
name: Build & Upload iOS to App Store Connect
on:
  push:
    branches: [ main ]
  workflow_dispatch:
permissions:
  contents: write
jobs:
  build-and-upload:
    name: Build & Upload iOS App
    runs-on: macos-latest            # 重點：Xcode 26 / iOS 26 SDK（App Store 2026 起必要求）
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: subosito/flutter-action@v2
        with: { channel: 'stable', cache: true }
      - name: git identity
        run: |
          git config --global user.email "you@gmail.com"
          git config --global user.name "you"
      - name: Ruby env
        working-directory: mobile/ios
        run: |
          gem install bundler
          bundle config path vendor/bundle
      - name: Bundle install
        working-directory: mobile/ios
        run: bundle install
      - name: fastlane match + build + upload
        working-directory: mobile/ios
        env:
          APP_STORE_CONNECT_KEY_ID: ${{ secrets.APP_STORE_CONNECT_KEY_ID }}
          APP_STORE_CONNECT_ISSUER_ID: ${{ secrets.APP_STORE_CONNECT_ISSUER_ID }}
          APP_STORE_CONNECT_KEY_CONTENT: ${{ secrets.APP_STORE_CONNECT_PRIVATE_KEY }}
          MATCH_PASSWORD: ${{ secrets.MATCH_PASSWORD }}
          MATCH_GIT_TOKEN: ${{ secrets.MATCH_GIT_TOKEN }}
        run: |
          export LANG=en_US.UTF-8
          bundle exec fastlane release
```

### `mobile/ios/fastlane/Fastfile`
```ruby
default_platform(:ios)
platform :ios do
  lane :release do
    api_key = app_store_connect_api_key(
      key_id: ENV["APP_STORE_CONNECT_KEY_ID"],
      issuer_id: ENV["APP_STORE_CONNECT_ISSUER_ID"],
      key_content: ENV["APP_STORE_CONNECT_KEY_CONTENT"],
      is_key_content_base64: false
    )
    create_keychain(name: "ci_keychain", password: "ci_password",
      default_keychain: true, unlock: true, timeout: 3600, lock_when_sleeps: false)

    match(
      type: "appstore",                       # 注意：是 appstore，不是 app_store
      api_key: api_key,
      app_identifier: "com.你的bundle.id",    # ← 改這裡
      readonly: false,
      git_url: "https://github.com/你/你的-signing.git",   # ← 改這裡（私有 repo）
      git_branch: "certificates",
      git_basic_authorization: Base64.strict_encode64("x-access-token:#{ENV['MATCH_GIT_TOKEN']}"),
      keychain_name: "ci_keychain", keychain_password: "ci_password",
      force_for_new_devices: false
    )

    sh "flutter pub get"
    sh "flutter build ios --release --no-codesign"

    profile = lane_context[SharedValues::MATCH_PROVISIONING_PROFILE_MAPPING]["com.你的bundle.id"] || "match AppStore com.你的bundle.id"
    build_app(
      workspace: "Runner.xcworkspace", scheme: "Runner", clean: true,
      export_method: "app-store",
      export_options: {
        signingStyle: "manual",
        teamID: "你的TEAMID",               # ← 改這裡
        provisioningProfiles: { "com.你的bundle.id" => profile }
      }
    )
    ipa = lane_context[SharedValues::IPA_OUTPUT_PATH]   # 用這個，勿用 build/ios/ipa glob
    raise "IPA not found" unless ipa
    upload_to_testflight(api_key: api_key, ipa: ipa, skip_waiting_for_build_processing: true)
  end
end
```

> `mobile/ios/Gemfile` 若缺，新增：
> ```ruby
> source "https://rubygems.org"
> gem "fastlane"
> gem "cocoapods"
> ```

**一定要改的 3 個值**：`app_identifier` / `provisioningProfiles` 的 bundle ID、`git_url` 的私有 repo、`teamID` 的 Apple Developer Team ID（`developer.apple.com → 你的帳號 → Membership` 可查）。

---

## 2. 檢查 Xcode 專案（iOS 簽名設定，每 App 一次）

在 `mobile/ios/Runner.xcodeproj/project.pbxproj` 的 Runner 建置區塊（Debug/Release/Profile）要有：
```
DEVELOPMENT_TEAM = <你的TeamID>;
PRODUCT_BUNDLE_IDENTIFIER = com.你的bundle.id;
CODE_SIGN_STYLE = Manual;
"CODE_SIGN_IDENTITY[sdk=iphoneos*]" = "iPhone Distribution";
PROVISIONING_PROFILE_SPECIFIER = "match AppStore com.你的bundle.id";
```
> ⚠️ 用編輯器（或 Xcode → Runner.xcodeproj → Signing & Capabilities 手動設定）改，
> **不要用 PowerShell `-replace` 寫 backreference**（會用 `$1` 誤刪 bundle id——我已踩過）。

---

## 3. 推送 → 自動出包 → 上傳 TestFlight

`git push` 到 `main` → workflow 自動觸發：
match 建證書/描述檔 → `flutter build ios` → build_app 簽名 → 出 `.ipa` → 上傳 TestFlight。
成功會在 log 看到 `fastlane.tools finished successfully 🎉`。

---

## 4. TestFlight 開放給測試員（需等 Apple 審查）

- 用 API 或 App Store Connect UI：**建測試群組 → 把 build 加進群組 → 開啟 Public Link**
- 填 **Beta App Review 資料**（聯絡人 + 測試說明）。
- ⚠️ **第一次「外部」測試**必須等 Apple 的 **Beta App Review** 通過（幾小時~一天）。
  通過前，Public Link 會顯示「不接受新測試員」，屬正常。
- 團員要「立刻」測：走 **Internal**（內部）測試群組——不需審查，但要在 App Store Connect 介面操作（API 建不出內部群組）。

---

## 5. 正式上架 App Store（販售用）

1. App Store 頁 → ＋ 新版本 → 選 build。
2. 填：出口合規（無加密選「豁免」）、內容分級問卷、App 審查資訊、**隱私政策 URL**。
3. 若 App 收集資料，補對應的 App 隱私政策與資料安全（Data Safety）問卷。
4. 點「**提交供審查**」。

---

## 我們踩過的雷（務必避開）

| 雷 | 對策 |
|---|---|
| `macos-14` → iOS 17.5 SDK → App Store 拒收 | 改用 **`macos-latest`**（Xcode 26 / iOS 26 SDK） |
| 證書每次生成 → 撞 Apple 2 張上限 | **match + 私有簽名 repo**（複用） |
| match 在「公開 repo」git auth 不穩 | 用**私有 signing repo + PAT** |
| 手動 p12：AES-256 與 macOS 不相容 / 密碼不符 | 別用手動 p12，**全靠 match** |
| `flutter build ipa`（automatic 簽名）失敗 | `flutter build ios --no-codesign` + `build_app`（manual） |
| pbxproj 用 `$1` sed 誤刪 bundle id | 用編輯器 / Xcode 改，別亂 replace |
| 找不到 ipa 路徑 | 用 `lane_context[SharedValues::IPA_OUTPUT_PATH]` |
| External 測試「不接受新測試員」 | 這是 **Beta App Review 未通過**，等審查即可 |
```
