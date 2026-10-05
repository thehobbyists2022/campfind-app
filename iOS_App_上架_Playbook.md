# iOS App 上架完整 Playbook（適用同 LLC 所有 App）

> 來源：TaiwanBite Master 實際成功案例（2026-09）
> 適用對象：Clarity Clinical Solutions LLC（Team ID: `VNTPT66236`）
> 技術：React/Vite PWA → Capacitor → GitHub Actions → TestFlight / App Store

---

## Part 0｜核心觀念：Distribution 證書可共用

| 項目 | 綁定對象 | 可否跨 App 共用 |
|------|---------|----------------|
| **Apple Distribution 證書 (.p12)** | Team（LLC） | ✅ **可共用**（一張簽無限多 App） |
| **Provisioning Profile** | App（bundle ID） | ❌ 每個 App 各一張 |
| **App ID** | App（bundle ID） | ❌ 每個 App 各一組 |
| **App Store Connect 記錄** | App | ❌ 每個 App 各一筆 |

**結論**：同一間 LLC 的所有 App，**共用同一張 Distribution `.p12` + 密碼**，只需為每個新 App 建立「新 App ID + 新 Profile + 新 ASC 記錄」。

**本 LLC 目前可用的共用證書**：
- **TONY KUO** 證書，serial `3ECABF8711CA579C6C9BFD351BEAE8BB`
- 對應 `.p12` 密碼：`TaiwanBite2026!P12Secure`（**務必保存**）
- ⚠️ 不要用 API Key 那張（serial `1006FD15...`，那是 CampFind 的）

---

## Part 1｜每個新 App 的前置準備（一次性）

### 1.1 Apple Developer
1. `developer.apple.com` → **Identifiers → ＋** 建立 App ID
   - App Type: App
   - Bundle ID: **Explicit**，例如 `com.clarityclinicalsolutions.<appname>`
2. **Certificates**：**不用新建**（沿用 TONY KUO 那張共用證書）
3. **Profiles → ＋ → Distribution → App Store Connect**：
   - 選該 App 的 App ID
   - **勾選 TONY KUO 證書**（serial 3ECABF87...）
   - Profile Name：`<AppName> AppStore`
   - 下載 `.mobileprovision`

### 1.2 App Store Connect
1. `appstoreconnect.apple.com` → **My Apps → ＋ New App**
   - Platform: iOS
   - Name / Primary Language / Bundle ID（選剛建的）/ SKU
   - User Access: Full Access

### 1.3 共用金鑰（若已有可跳過）
- **Distribution `.p12` + 密碼**：沿用 TaiwanBite 的（TONY KUO 那張）
- **App Store Connect API Key (.p8)**：可沿用同一支（Key ID / Issuer ID / .p8）

---

## Part 2｜Capacitor 專案設定（Vite/React PWA）

```bash
npm install @capacitor/core @capacitor/cli @capacitor/ios
```

`capacitor.config.ts`：
```ts
import type { CapacitorConfig } from '@capacitor/cli';
const config: CapacitorConfig = {
  appId: 'com.clarityclinicalsolutions.<appname>',  // ← 改
  appName: '<App 顯示名稱>',                          // ← 改
  webDir: 'dist',
  server: { androidScheme: 'https', iosScheme: 'capacitor' },
};
export default config;
```

```bash
npx cap add ios      # 產生 ios/ 平台
npm run build        # 產出 dist/
npx cap sync ios     # 同步 web 資源到原生
```

### Xcode 簽名設定（`ios/App/App.xcodeproj/project.pbxproj`）
Debug 與 Release 兩個 buildSettings 都要有：
```
CODE_SIGN_STYLE = Manual;
DEVELOPMENT_TEAM = VNTPT66236;
CODE_SIGN_IDENTITY = "iPhone Distribution";
PRODUCT_BUNDLE_IDENTIFIER = com.clarityclinicalsolutions.<appname>;
PROVISIONING_PROFILE_SPECIFIER = "<AppName> AppStore";
```

### 共享 scheme（避免 CI 報 scheme not found）
建立 `ios/App/App.xcodeproj/xcshareddata/xcschemes/App.xcscheme`，
其中 `BlueprintIdentifier` 必須等於 **PBXNativeTarget 的 ID**（不是 build config 的 ID）。
查法：`project.pbxproj` 裡 `PBXNativeTarget` 那段的 ID（如 `504EC3031FED79650016851F`）。

### ExportOptions.plist（`ios/ExportOptions.plist`）
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>method</key>
    <string>app-store-connect</string>
    <key>teamID</key>
    <string>VNTPT66236</string>
    <key>signingStyle</key>
    <string>manual</string>
    <key>uploadSymbols</key>
    <true/>
    <key>provisioningProfiles</key>
    <dict>
        <key>com.clarityclinicalsolutions.<appname></key>
        <string><AppName> AppStore</string>
    </dict>
</dict>
</plist>
```
> ⚠️ **不要**加 `destination` 這個 key（會讓 export 報錯）。

---

## Part 3｜GitHub Actions Workflow（`.github/workflows/build_ios.yml`）

```yaml
name: Build & Upload iOS to App Store Connect
on:
  push: { branches: [ main ] }
  workflow_dispatch:

jobs:
  build-and-upload:
    runs-on: macos-latest        # ★ 必須（避免 Xcode 15 export segfault）
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with: { node-version: '22', cache: 'npm' }   # ★ Capacitor 需 Node >= 22

      - name: Install Apple Certificate & Provisioning Profile
        env:
          BUILD_CERTIFICATE_BASE64: ${{ secrets.APPLE_CERT_P12_BASE64 }}
          P12_PASSWORD: ${{ secrets.APPLE_CERT_PASSWORD }}
          BUILD_PROVISION_PROFILE_BASE64: ${{ secrets.APPLE_PROVISIONING_PROFILE_BASE64 }}
          KEYCHAIN_PASSWORD: "ci_build_keychain_password"
        run: |
          KEYCHAIN_PATH=$RUNNER_TEMP/app-signing.keychain-db
          security create-keychain -p "$KEYCHAIN_PASSWORD" $KEYCHAIN_PATH
          security set-keychain-settings -lut 21600 $KEYCHAIN_PATH
          security unlock-keychain -p "$KEYCHAIN_PASSWORD" $KEYCHAIN_PATH
          CERTIFICATE_PATH=$RUNNER_TEMP/build_certificate.p12
          echo "$BUILD_CERTIFICATE_BASE64" | base64 --decode > $CERTIFICATE_PATH
          security import $CERTIFICATE_PATH -P "$P12_PASSWORD" -A -t cert -f pkcs12 -k $KEYCHAIN_PATH
          security list-keychains -d user -s $KEYCHAIN_PATH $(security list-keychains -d user | sed -e 's/"//g')
          security set-key-partition-list -S apple-tool:,apple:,codesign: -s -k "$KEYCHAIN_PASSWORD" $KEYCHAIN_PATH
          mkdir -p ~/Library/MobileDevice/Provisioning\ Profiles
          PROFILE_PATH=~/Library/MobileDevice/Provisioning\ Profiles/app_store.mobileprovision
          echo "$BUILD_PROVISION_PROFILE_BASE64" | base64 --decode > "$PROFILE_PATH"

      - run: npm ci
      - run: npm run build
      - run: npx cap sync ios

      - name: Archive iOS App
        working-directory: ios/App
        run: |
          xcodebuild archive \
            -project App.xcodeproj -scheme App -configuration Release \
            -archivePath "$RUNNER_TEMP/App.xcarchive" \
            -destination 'generic/platform=iOS' \
            CODE_SIGN_STYLE=Manual DEVELOPMENT_TEAM=VNTPT66236 \
            CODE_SIGN_IDENTITY="iPhone Distribution" \
            PROVISIONING_PROFILE_SPECIFIER="<AppName> AppStore"

      - name: Export iOS IPA
        working-directory: ios
        run: |
          xcodebuild -exportArchive \
            -archivePath "$RUNNER_TEMP/App.xcarchive" \
            -exportPath "$RUNNER_TEMP/ipa" \
            -exportOptionsPlist ExportOptions.plist

      - name: Upload IPA to App Store Connect
        env:
          APP_STORE_CONNECT_KEY_ID: ${{ secrets.APP_STORE_CONNECT_KEY_ID }}
          APP_STORE_CONNECT_ISSUER_ID: ${{ secrets.APP_STORE_CONNECT_ISSUER_ID }}
          APP_STORE_CONNECT_PRIVATE_KEY: ${{ secrets.APP_STORE_CONNECT_PRIVATE_KEY }}
        run: |
          mkdir -p ~/.appstoreconnect/private_keys
          echo "$APP_STORE_CONNECT_PRIVATE_KEY" > ~/.appstoreconnect/private_keys/AuthKey_${APP_STORE_CONNECT_KEY_ID}.p8
          IPA_FILE=$(find "$RUNNER_TEMP/ipa" -name "*.ipa" | head -n 1)
          xcrun altool --upload-app --type ios --file "$IPA_FILE" --apiKey "$APP_STORE_CONNECT_KEY_ID" --apiIssuer "$APP_STORE_CONNECT_ISSUER_ID"
```

### GitHub Secrets（每個 App repo 各設一次）
| Secret | 值 | 是否共用 |
|--------|-----|---------|
| `APPLE_CERT_P12_BASE64` | TONY KUO `.p12` 的 base64 | ✅ 共用 |
| `APPLE_CERT_PASSWORD` | `TaiwanBite2026!P12Secure` | ✅ 共用 |
| `APPLE_PROVISIONING_PROFILE_BASE64` | 該 App 的 `.mobileprovision` base64 | ❌ 各 App |
| `APP_STORE_CONNECT_KEY_ID` | API Key ID | ✅ 共用 |
| `APP_STORE_CONNECT_ISSUER_ID` | Issuer ID | ✅ 共用 |
| `APP_STORE_CONNECT_PRIVATE_KEY` | `.p8` 內容 | ✅ 共用 |

---

## Part 4｜踩雷清單（全部實際遇過）

| # | 問題 | 症狀 | 解法 |
|---|------|------|------|
| 1 | Node 版本太舊 | `The Capacitor CLI requires NodeJS >=22.0.0` | workflow 用 Node 22 |
| 2 | `.p12` 格式不相容 | `MAC verification failed during PKCS12 import` | 用 openssl `-legacy` 產生（PBE-SHA1-3DES/RC2，非 PBES2/AES） |
| 3 | Profile 與證書不匹配 | `profile doesn't include signing certificate` | Profile 必須綁「與 `.p12` 同一張」證書 |
| 4 | ExportOptions 有 `destination` | `expected one of {upload, export}` | 移除 `destination` |
| 5 | 缺 provisioningProfiles | `requires a provisioning profile` | 在 ExportOptions 加 bundle ID → profile name 對應 |
| 6 | method 舊值 | `app-store is deprecated` + segfault | 用 `app-store-connect` |
| 7 | Xcode 15 export 崩潰 | `Segmentation fault: 11` | 用 `macos-latest` |
| 8 | 缺共享 scheme | `scheme 'App' not found` | 建立 `xcshareddata/xcschemes/App.xcscheme`（target ID 要對） |
| 9 | 版本未遞增 | App Store 拒收重複 build | 每次改 `CURRENT_PROJECT_VERSION` |

### Windows 產生 Apple 相容 `.p12`（無 Mac）
```powershell
$os = "C:\Program Files\Git\mingw64\bin\openssl.exe"   # ★ 用 mingw64 版才有 legacy provider
# 1. 產私鑰 + CSR
& $os genrsa -out twb_private.key 2048
& $os req -new -key twb_private.key -out twb.csr -subj "/C=TW/O=Clarity Clinical Solutions LLC/CN=Clarity Clinical Solutions LLC"
# 2. 上傳 twb.csr 到 Apple → 下載 .cer
# 3. 合成 legacy .p12（Apple 相容）
& $os pkcs12 -export -legacy -out app.p12 -inkey twb_private.key -in distribution.cer -password pass:"TaiwanBite2026!P12Secure"
# 4. 轉 base64 給 GitHub secret
[Convert]::ToBase64String([IO.File]::ReadAllBytes("app.p12"))
```

---

## Part 5｜可直接給 AI 的提示詞範本

> 我要把一個 **React/Vite PWA** 打包成 **iOS App** 上架 App Store，使用 **Capacitor**，CI 用 **GitHub Actions**，簽名用 **.p12 + provisioning profile（存在 GitHub secrets）**，不使用 fastlane match。
>
> 公司/Team：**Clarity Clinical Solutions LLC**，Team ID **VNTPT66236**。
> 共用 Distribution 證書：**TONY KUO 那張**（serial `3ECABF87...`），`.p12` 密碼 `TaiwanBite2026!P12Secure`（若我沒提供，請提醒我）。
>
> 新 App 資料：
> - App 名稱：`<填>`
> - Bundle ID：`com.clarityclinicalsolutions.<填>`
> - App Store Connect SKU：`<填>`
>
> 請幫我完成：
> 1. `capacitor.config.ts`（appId/appName/webDir）
> 2. `npx cap add ios` 後的 `project.pbxproj` 簽名設定（Manual、Team、bundle id、profile specifier）
> 3. `ios/ExportOptions.plist`（method=app-store-connect、teamID、signingStyle=manual、provisioningProfiles 對應，**不要** destination）
> 4. 共享 scheme `App.xcscheme`
> 5. `.github/workflows/build_ios.yml`（Node 22、macos-latest、security import、npm ci/build、cap sync、xcodebuild archive、exportArchive、xcrun altool）
> 6. 告訴我需要在 Apple Developer 建哪些（App ID + Profile）、在 App Store Connect 建什麼、以及要加哪些 GitHub secrets。
>
> 請參考我提供的踩雷清單，避免：Node 太舊、.p12 非 legacy 格式、profile 與證書不匹配、ExportOptions 的 destination/provisioningProfiles 問題、macos-14 segfault、缺 scheme。
