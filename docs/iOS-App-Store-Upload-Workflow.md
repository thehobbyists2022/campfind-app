# iOS App Store 上架工作流（CampFind 实战经验固化版）

> **用途**：本文档是「在没有 Mac、只有 Windows/iPad、用 GitHub Actions 云端 Mac runner」的前提下，把 Flutter/React Native/Capacitor App 上架到 Apple App Store 的完整工作流。所有步骤都来自 CampFind 实际走过的路，包含了**踩过的坑、犯错点、正确做法**。
>
> **目标使用者**：其他项目（如 iCare Senior Care Companion）的 AI 助手 / DeepSeek 执行此流程时，请严格按本文档核对，避免重蹈 CampFind 的试错。

---

## 0. 前置认知（最重要，先读）

1. **你没有 Mac**：所有「签名、打包、上传」都在 **GitHub Actions 的云端 macOS runner** 上完成。你只需：
   - 一台能开浏览器的设备（Windows / iPad）登录 **App Store Connect**（网页）+ **GitHub**。
   - 不需要本机装 Xcode、不需要本机 .p12。
2. **三样东西要分清**（CampFind 最大的混乱来源）：
   - **Bundle ID**：App 的唯一标识，如 `com.campfind.app`（iOS 用）。⚠️ 与 Google Play 的 package name（Android）**不是一回事**，别混。
   - **Version（版本号）**：如 `1.1.0`，对用户显示。必须 = build 内部的 `CFBundleShortVersionString`。
   - **Build 编号**：如 `23`，递增的编译号。每次上传必须比上一次大。
3. **两个平台入口要分清**（App Store Connect 里）：
   - **TestFlight** 分页 = 测试版，上传 build 用，**不等于上架**。
   - **App Store** 分页 = 正式版发布，在这里建版本、选 build、填资料、提交审核。
4. **审核状态链**：`Prepare for Submission`（未提交）→ 点 **Add for Review** → `Waiting for Review`（已进队列）→ `In Review`（审核中）→ `Ready for Sale`（通过）。**「Prepare for Submission」= 还没提交审核，Apple 不会审。**
5. **审核时间**：通常 24–48 小时，1–3 个工作日。

---

## 1. 上架前准备（一次做对，省很多时间）

### 1.1 确认 Developer 账号主体
- 登录 `developer.apple.com`，确认你是 **Individual 还是 Organization**（公司需要 D-U-N-S 号）。
- **你的 App Store 显示名 = 注册主体名称**（个人=法定姓名，公司=公司名）。隐私政策里写的「运营主体/Developer」**必须与之一致**，否则有主体不符风险。
- CampFind 案例：Apple 用 **Clarity Clinical Solutions LLC（公司 + DUNS）** 注册，Google Play 上显示 "Wingsoar2023" 只是展示名（非法人），**不影响主体一致性**。

### 1.2 准备隐私政策（Privacy Policy）
- 需要一个**公开可访问的 URL**（如 `https://你的域名/privacy.html`）。
- 内容必须与 App 实际行为一致。CampFind 的坑：
  - 别写「不收集任何数据」却又有表单收集 → 自相矛盾。
  - 分两层写：「消费者默认不收集」+「营地主自愿提交表单时收集」。
  - 补第三方披露（表单服务商、Amazon Associates 等）。
  - 儿童隐私（COPPA）：App 面向家长而非 13 岁以下儿童时，写明「面向家长、儿童应在监护下使用」。
  - 写明法律主体（与 App Store 显示的 Developer 一致）。
- **此 URL 必须在提审时填进 App Store Connect，且可从 App 内访问**（加个「Privacy Policy」入口按钮）。

### 1.3 准备 App 图标 + 截图
- **App 图标**：1024×1024 PNG，**不能有透明通道（alpha）**，否则上传报错。
- **截图**（App Store Connect 要求）：
  - iPhone：6.7" = **1290×2796**（或 6.5" = 1242×2688，6.9" = 1320×2868）。
  - iPad：**13" = 2064×2752**（必填，若 App 支持 iPad）。**CampFind 卡过一次：忘记传 iPad 截图 → 被要求补。**
  - 至少 1 张，建议 4–6 张展示核心功能。
- 没有 Mac 也能做：Windows 上用 PIL/Python 或在线工具把 iPhone 截图 resize 到 iPad 尺寸。

### 1.4 准备 App Store Connect API Key（.p8）—— 上架必需
- 到 `appstoreconnect.apple.com` → Users and Access → **Integrations → App Store Connect API** → 生成 API Key。
- 你会得到：**Key ID**、**Issuer ID**、**.p8 文件**（私钥）。
- 这个 API Key 是「签名、上传、提交」的自动化钥匙，**非常重要**。

---

## 2. iOS 签名与证书（最大的坑区，CampFind 在此绕了很久）

### 2.1 证书核心认知
- **Distribution Certificate（分发证书）**：绑定 **Team（账号）**，**不绑定 App**。1 张可签多个 App。
- **Apple 上限 2 张** Distribution 证书/Team。
- **Provisioning Profile**：绑定 **Bundle ID + 证书**，每个 App 一张（App Store 类型）。
- 签名需要「**证书 + 匹配的私钥（.p12）**」两者。

### 2.2 CampFind 踩过的坑（务必避免）

| 坑 | 现象 | 正确做法 |
|---|---|---|
| **证书被吊销/过期** | Xcode 报 `Signing certificate is invalid ... may have been revoked or expired`；App Store 报 **ITMS-90035 Invalid Signature** | 确认在用证书是 **Active** 且没被撤。签不了 = 证书坏了，换有效的那张 |
| **signing repo 存了错误/旧证书** | match 报 `Certificate 'XXX' is not available on the Developer Portal` | 确认 match 用的 signing repo 分支里证书是对的 |
| **Runner.xcodeproj 里 profile 名写死旧的** | 报 `No profile for team 'XXX' matching 'match AppStore ... <旧ID>'` | 把 pbxproj 里 `PROVISIONING_PROFILE_SPECIFIER` 改成 match 实际生成的 profile 名 |
| **`flutter build ios --no-codesign` + 手动签名混乱** | ITMS-90035 / 签名无效 | 要么全程 automatic 签名（match + `flutter build ipa`），要么明确 manual + 正确 profile |
| **没有 Mac 手动导出 .p12** | 拿不到证书私钥 | 用 **match + API key 自动管理证书**，不需要手动 .p12 |
| **openssl -legacy 在 macOS 报错** | `pkcs12: Unrecognized flag legacy` | macOS 自带 LibreSSL 无 `-legacy`，需 `brew install openssl@3` 后用其二进制 |
| **Distribution 证书 2 张上限** | 建第 3 张报错 | 已有 2 张就复用，别新建；必要时先 Revoke 1 张空的 |

### 2.3 推荐签名方案（CampFind 最终成功这套）
**用 fastlane match + App Store Connect API key 自动管理证书**，不手动 .p12：

1. 建一个**私有 GitHub repo**（如 `xxx-signing`）存 match 证书。
2. GitHub Actions 用 `APP_STORE_CONNECT_*`（API key）、`MATCH_GIT_TOKEN`（访问 signing repo）、`MATCH_PASSWORD`（match 加密证书的密码）这些 secrets。
3. Fastfile 里：
   ```ruby
   match(
     type: "appstore",
     api_key: api_key,
     app_identifier: "你的.bundle.id",
     readonly: false,          # 首次/证书变化用 false 让 match 从 Apple 同步
     git_url: "https://github.com/你的账号/xxx-signing.git",
     git_branch: "certificates",
     git_basic_authorization: Base64.strict_encode64("x-access-token:#{ENV['MATCH_GIT_TOKEN']}"),
     keychain_name: "ci_keychain",
     keychain_password: "ci_password"
   )
   ```
4. match 会用 API key 连 Apple → **复用已有的有效 Distribution 证书**（不新建、不撞上限）→ 装进 keychain → 生成正确 profile。
5. ⚠️ **若 repo 里存了失效证书，match 会卡住** → 用新分支隔离，或先清掉错的。

### 2.4 确认「哪张证书有效」的方法（不用 Mac）
- 在 Apple 后台下载 `.cer` → 用 Python 解析 serial：
  ```python
  from cryptography import x509
  cert = x509.load_der_x509_certificate(open("distribution.cer","rb").read())
  print(hex(cert.serial_number))  # 有效证书的 serial
  ```
- 对比：signing repo 里证书的 serial vs Apple 后台有效证书的 serial。**两者要一致**。

---

## 3. GitHub Actions CI 工作流（云端打包 + 上传）

### 3.1 需要准备的 GitHub Secrets
| Secret | 说明 |
|---|---|
| `APP_STORE_CONNECT_KEY_ID` | API key 的 Key ID |
| `APP_STORE_CONNECT_ISSUER_ID` | API key 的 Issuer ID |
| `APP_STORE_CONNECT_PRIVATE_KEY` | `.p8` 文件内容（或 base64） |
| `MATCH_GIT_TOKEN` | 访问 signing repo 的 PAT |
| `MATCH_PASSWORD` | match 加密证书的密码 |

### 3.2 `build_ios.yml` 骨架（CampFind 最终成功版）
```yaml
name: Build & Upload iOS
on:
  push: { branches: [ main ] }
  workflow_dispatch:

jobs:
  build-and-upload:
    runs-on: macos-latest
    steps:
      - uses: actions/checkout@v4
      - uses: subosito/flutter-action@v2
        with: { channel: stable, cache: true }

      - name: Configure git auth for fastlane match
        run: |
          git config --global user.email "你的@email.com"
          git config --global user.name "你的账号"

      - name: Configure Ruby + bundle install
        working-directory: mobile/ios
        run: |
          gem install bundler
          bundle config path vendor/bundle
          bundle install

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

### 3.3 Fastfile（release lane，CampFind 最终成功版）
```ruby
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
    type: "appstore",
    api_key: api_key,
    app_identifier: "你的.bundle.id",
    readonly: false,
    git_url: "https://github.com/你的账号/xxx-signing.git",
    git_branch: "certificates",
    git_basic_authorization: Base64.strict_encode64("x-access-token:#{ENV['MATCH_GIT_TOKEN']}"),
    keychain_name: "ci_keychain",
    keychain_password: "ci_password"
  )

  sh "flutter pub get"
  # automatic 签名：Xcode 用 keychain 里 match 装的证书 + profile
  sh "flutter build ipa --release"

  ipa = Dir["build/ios/ipa/*.ipa"].first
  raise "IPA not found" unless ipa

  upload_to_testflight(api_key: api_key, ipa: ipa,
    skip_waiting_for_build_processing: true)
end
```

### 3.4 每次发布前要改的东西
- **递增 build 编号**：在 `pubspec.yaml` 或 Info.plist 里，`version: 1.1.0+24`（+号后递增）。**Apple 要求 build 号严格递增**，不能重复。
- **版本号保持一致**：`version: 1.1.0` 这部分 = App Store 里的 Version，必须 = `CFBundleShortVersionString`。

---

## 4. App Store Connect 网页操作（提交审核）

### 4.1 首次：建立 App 记录
- `appstoreconnect.apple.com` → My Apps → **+** → New App。
- 填：名称（如 `CampFind: Summer & Winter Camp`）、主语言、Bundle ID、SKU。

### 4.2 等 build 上传完成
- GitHub Actions 跑完 → 去 **TestFlight** 分页，看 build 状态从 `Processing` → `Complete`（可能 30 分钟~几小时）。**Processing 中不能选进 App Store 版本。**

### 4.3 建 App Store 版本 + 选 build
- 左侧 **App Store** 分页 → 版本列表 → **「+」建立新版本** → 输入版本号（如 `1.1.0`）。
- ⚠️ **版本号必须 = build 的版本号**。若 build 是 1.1.0，版本号必须填 1.1.0，不能 1.0。
- 进入版本详情 → **Build → + → 选 build**（选最新的、Complete 的那个）。

### 4.4 填必填信息（CampFind 踩坑点）
| 项 | 注意事项 |
|---|---|
| **Previews and Screenshots** | iPhone 6.7" 1290×2796 + iPad 13" 2064×2752。**iPad 截图常被漏 → 必填** |
| **Promotional text / Description / Keywords** | 填核心功能；keywords 逗号分隔 |
| **Support URL** | 填官网（如 netlify 页面） |
| **Copyright** | 填版权声明 |
| **Version** | 必须 = build 版本号 |
| **App Review Information** | Contact Info 必填；**Notes 强烈建议填功能说明**（给审核员看） |
| **App Store Version Release** | 选「Manually release」最稳（审核过了你手动上架） |
| **App Privacy（营养标签）** | 与隐私政策、代码行为**一致**。不收集就勾「不收集」；有表单收集就如实申报 |
| **Age Rating（分级）** | 按内容填（CampFind = 4+） |

### 4.5 提交审核
- 右上角 **Save**（确认无红色错误）→ **Add for Review / Submit for Review**。
- 有问卷（隐私、出口合规、内容）→ 按实际勾选。
- 成功后状态 = **Waiting for Review** → 等 1–3 天 → 邮件通知结果。

---

## 5. 常见错误速查表（CampFind 亲历）

| 错误 | 含义 | 解决 |
|---|---|---|
| `ITMS-90035: Invalid Signature` | 签名用的证书无效/失效/被吊销 | 换有效的 Distribution 证书；确认 match/repo 里证书正确 |
| `Signing certificate ... may have been revoked or expired` | 证书坏了 | 用 Python 读 .cer serial，比对 Apple 后台，换有效那张 |
| `No profile for team 'X' matching 'match AppStore ... <ID>'` | pbxproj 里 profile 名写死旧的了 | 改 `PROVISIONING_PROFILE_SPECIFIER` 为 match 实际生成的 profile 名 |
| `Certificate 'X' is not available on Developer Portal` | signing repo 里证书失效/被删 | 用新分支或清掉旧证书，让 match 重新从 Apple 同步 |
| `pkcs12: Unrecognized flag legacy` | macOS LibreSSL 无 `-legacy` | `brew install openssl@3`，用它的二进制 |
| `Must upload a screenshot for 13-inch iPad` | 缺 iPad 截图 | 补 2064×2752 截图（可用 iPhone 图 resize） |
| `version does not match build` | 版本号 ≠ build 版本号 | 版本号改成与 build 一致 |
| `Invalid Binary` 状态 | build 被 Apple 判定无效（如签名错） | 修复签名，重新上传 build，重建版本 |
| `Prepare for Submission` 卡住 | 还没点提交审核 | 填完信息后点 **Add for Review** |
| Distribution 证书 2 张上限 | 建第 3 张报错 | 复用已有的；必要时 Revoke 一张 |

---

## 6. 给执行者的最终 Checklist

- [ ] 确认 Developer 账号主体（Individual/Organization），隐私政策主体一致
- [ ] 隐私政策 URL 公开可访问，内容与代码行为一致（含第三方披露、COPPA）
- [ ] App 图标 1024×1024 无 alpha
- [ ] 截图：iPhone 6.7" 1290×2796 + iPad 13" 2064×2752
- [ ] App Store Connect API Key（Key ID / Issuer ID / .p8）就绪
- [ ] signing repo（私有）+ `MATCH_GIT_TOKEN` + `MATCH_PASSWORD` 就绪
- [ ] `pubspec.yaml` 版本号 = build 版本号，build 号递增
- [ ] `Runner.xcodeproj` 里 `PROVISIONING_PROFILE_SPECIFIER` = 正确的 match profile 名
- [ ] GitHub Actions：match + build + upload 全绿
- [ ] App Store Connect：建版本（版本号 = build 版本号）→ 选 build → 填截图/描述/隐私/分级 → Notes → Save → Add for Review
- [ ] 状态 = Waiting for Review → 等审核

---

*本文档基于 CampFind（Clarity Clinical Solutions LLC / com.campfind.app）2026 年 iOS 上架实战整理，由 AI 助手记录。*