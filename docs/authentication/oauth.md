# OAuth 認證設置指南

本指南提供完整的 OAuth 認證設置步驟，適合個人開發和快速測試。

## 什麼是 OAuth 認證？

OAuth 2.0 是一種授權協議，讓應用程式可以在獲得使用者同意後存取其 Google Calendar 資料。

### 優點
- ✅ 可存取個人所有行事曆
- ✅ 設置相對簡單
- ✅ 適合快速測試和開發
- ✅ 無需手動分享行事曆

### 缺點
- ⚠️ 需要瀏覽器互動完成授權
- ⚠️ Token 可能過期需重新授權
- ⚠️ 不適合完全自動化的環境

## 前置需求

在開始設置之前，請確保已完成 [Google Cloud 專案設置](overview.md#開始之前google-cloud-專案設置)。

## 設置步驟

### 步驟 1: 配置 OAuth 同意畫面

首次建立 OAuth 憑證前，需要先配置 OAuth 同意畫面：

1. 在 [Google Cloud Console](https://console.cloud.google.com/) 中，導航到「APIs & Services」→「OAuth consent screen」
2. 選擇使用者類型：
   - **外部（External）**：任何 Google 帳號都可以使用（推薦）
   - **內部（Internal）**：僅限組織內部使用（需要 Google Workspace）
3. 點擊「建立」
4. 填寫應用程式資訊：
   - **應用程式名稱**：`CalendarBridge`
   - **使用者支援電子郵件**：選擇您的電子郵件
   - **應用程式標誌**：可選，可留空
   - **應用程式首頁**：可選，可留空
   - **應用程式隱私權政策連結**：可選，可留空
   - **應用程式服務條款連結**：可選，可留空
   - **已授權網域**：可留空
   - **開發人員聯絡資訊**：填入您的電子郵件
5. 點擊「儲存並繼續」

### 步驟 2: 設定範圍（Scopes）

1. 在「Scopes」頁面，點擊「ADD OR REMOVE SCOPES」
2. 在搜尋框中輸入「calendar」
3. 勾選以下範圍：
   - `https://www.googleapis.com/auth/calendar` - 完整行事曆存取權限
   - 或 `https://www.googleapis.com/auth/calendar.events` - 僅事件存取權限（較安全）
4. 點擊「UPDATE」
5. 點擊「儲存並繼續」

> 💡 **範圍說明**：
> - `calendar`: 完整的行事曆存取權限，包括建立、修改、刪除行事曆和事件
> - `calendar.events`: 僅能管理事件，無法建立或刪除行事曆

### 步驟 3: 新增測試使用者

如果選擇「外部」使用者類型，應用程式會處於「測試」狀態，需要新增測試使用者：

1. 在「Test users」頁面，點擊「+ ADD USERS」
2. 輸入您的 Gmail 地址（將用於授權的帳號）
3. 點擊「儲存」
4. 點擊「儲存並繼續」
5. 在摘要頁面確認資訊，點擊「返回儀表板」

> ⚠️ **重要**：在測試模式下，只有列表中的測試使用者可以授權應用程式。如果您想讓其他人使用，需要將應用程式發布到生產環境（或將他們加入測試使用者）。

### 步驟 4: 建立 OAuth 憑證

1. 導航到「APIs & Services」→「Credentials」
2. 點擊「+ CREATE CREDENTIALS」
3. 選擇「OAuth client ID」
4. 應用程式類型選擇「**Desktop app**」（桌面應用程式）
5. 名稱輸入「CalendarBridge」（或您喜歡的名稱）
6. 點擊「CREATE」

### 步驟 5: 下載憑證檔案

1. 在彈出的對話框中，點擊「DOWNLOAD JSON」
2. 或在憑證列表中，點擊剛建立的 OAuth 客戶端右側的下載圖示
3. 將下載的 JSON 檔案重新命名為 `credentials.json`
4. 移動到專案的 `config/` 目錄

```bash
# 將下載的憑證檔案移到正確位置
mv ~/Downloads/client_secret_*.json config/credentials.json
```

> ⚠️ **安全提醒**：`credentials.json` 包含敏感資訊，請妥善保管，勿提交到版本控制系統。

### 步驟 6: 配置應用程式

編輯 `config/settings.yaml` 檔案：

```yaml
google_calendar:
  auth_type: "oauth"  # 設定認證類型為 OAuth
  credentials_file: "config/credentials.json"  # OAuth 憑證檔案路徑
  token_file: "config/token.json"  # Token 儲存路徑
  calendar_id: "primary"  # 使用主要行事曆，或指定特定行事曆 ID
```

> 💡 **行事曆 ID 說明**：
> - `primary`: 您的主要 Google Calendar
> - 特定 ID: 如 `abc123@group.calendar.google.com`（可在行事曆設定中找到）

### 步驟 7: 初次授權

執行授權流程：

```bash
# 使用設置腳本（推薦）
python setup.py

# 或手動執行認證
python -c "
from src.clients.google_calendar import GoogleCalendarClient
from src.utils.config import load_config
config = load_config('config/settings.yaml')
client = GoogleCalendarClient(config.google_calendar)
client.authenticate()
print('✅ 認證成功！')
"
```

這會執行以下操作：

1. **開啟瀏覽器**：自動開啟預設瀏覽器
2. **登入 Google**：使用您的 Google 帳號登入
3. **授權應用程式**：
   - 您會看到「Google 尚未驗證此應用程式」的警告（正常現象）
   - 點擊「繼續」（可能需要點擊「進階」→「前往 CalendarBridge（不安全）」）
   - 查看應用程式請求的權限
   - 點擊「允許」授予權限
4. **完成授權**：瀏覽器會顯示「授權流程已完成」
5. **產生 Token**：`config/token.json` 會自動建立

> 💡 **為什麼會出現「未驗證」警告？**
>
> 這是因為您的應用程式處於測試模式，尚未通過 Google 的驗證程序。這對個人使用是正常的，不影響功能。如果要移除此警告，需要提交應用程式進行 Google 審核（但對個人使用並非必要）。

### 步驟 8: 測試認證

執行以下指令測試認證是否成功：

```bash
python -c "
from src.clients.google_calendar import GoogleCalendarClient
from src.utils.config import load_config
config = load_config('config/settings.yaml')
client = GoogleCalendarClient(config.google_calendar)
client.authenticate()
cal_info = client.get_calendar_info()
print(f'✅ 成功連接到行事曆: {cal_info.get(\"summary\", \"未知\")}')
"
```

如果設置正確，您應該會看到類似以下的輸出：

```
✅ 成功連接到行事曆: 您的行事曆名稱
```

## 常見問題

### Q1: 出現「access_blocked」錯誤

**原因**：應用程式處於測試模式，但您的帳號不在測試使用者清單中。

**解決方法**：
1. 前往 Google Cloud Console
2. 導航到「APIs & Services」→「OAuth consent screen」
3. 在「Test users」區域新增您的 Gmail 地址
4. 刪除 `config/token.json` 並重新執行授權

### Q2: 出現「redirect_uri_mismatch」錯誤

**原因**：OAuth 客戶端類型設定錯誤。

**解決方法**：
1. 確認您建立的是「Desktop app」類型
2. 如果不是，刪除現有的 OAuth 客戶端並重新建立
3. 重新下載 `credentials.json`

### Q3: Token 過期怎麼辦？

**解決方法**：
```bash
# 刪除舊的 token 並重新授權
rm config/token.json
python setup.py
```

OAuth token 通常會自動更新，但如果出現問題，刪除並重新授權是最簡單的方法。

### Q4: 能否在無頭環境（無 GUI）使用 OAuth？

**答案**：可以，但需要額外配置。

**解決方法**：
1. 在有 GUI 的環境中完成初次授權
2. 將產生的 `config/token.json` 複製到無頭環境
3. Token 會自動更新，只要不刪除就可以持續使用

> 💡 **更好的選擇**：如果您需要在無頭環境運行，建議使用[服務帳號認證](service_account.md)。

### Q5: 如何存取其他行事曆？

**解決方法**：

1. 先列出您有權限存取的所有行事曆：
   ```bash
   python get_calendar_list.py
   ```

2. 找到目標行事曆的 ID

3. 更新 `config/settings.yaml`：
   ```yaml
   google_calendar:
     calendar_id: "your-calendar-id@group.calendar.google.com"
   ```

### Q6: 可以同時同步多個行事曆嗎？

**答案**：目前版本一次只能同步到一個行事曆。如果需要同步到多個行事曆，您需要：

1. 準備多個配置檔案（每個指向不同的行事曆）
2. 執行多個 CalendarBridge 實例

或者，您可以在 Google Calendar 中建立一個共用行事曆，然後將事件同步到該行事曆。

## 安全性考量

### 檔案保護

確保以下檔案不會提交到版本控制：

```bash
# .gitignore
config/credentials.json
config/token.json
```

### 權限管理

- OAuth token 具有您授予的所有權限
- 定期檢查授權的應用程式清單：[Google 帳戶安全性](https://myaccount.google.com/permissions)
- 如果不再使用，撤銷應用程式的存取權限

### 最佳實踐

1. **不要分享憑證檔案**：`credentials.json` 和 `token.json` 包含敏感資訊
2. **使用環境變數**：在生產環境考慮使用環境變數儲存檔案路徑
3. **定期輪換**：如果懷疑憑證洩漏，立即在 Google Cloud Console 刪除並重新建立

## 與服務帳號認證的比較

| 特性 | OAuth | 服務帳號 |
|------|-------|---------|
| 設置複雜度 | 簡單 | 中等 |
| 授權流程 | 需要瀏覽器 | 無需授權 |
| Token 管理 | 自動更新 | 無 Token |
| 行事曆存取 | 所有個人行事曆 | 需明確分享 |
| Docker 友善 | 需要預先授權 | 完全支援 |
| 適用場景 | 個人開發測試 | 生產環境 |

如果您需要在生產環境或 Docker 中部署，建議改用[服務帳號認證](service_account.md)。

## 相關文件

- [認證方式概覽](overview.md) - 認證方式比較與選擇
- [服務帳號設置](service_account.md) - 另一種認證方式
- [本地部署指南](../deployment/local.md) - 使用 OAuth 的本地部署
- [疑難排解](../reference/troubleshooting.md) - 更多問題解決方案
