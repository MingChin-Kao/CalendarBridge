# CalendarBridge 服務帳號設置指南

本指南提供完整的服務帳號設置步驟，適合生產環境和自動化部署。

## 📊 什麼是服務帳號？

服務帳號是 Google Cloud 為應用程式提供的身份認證方式，不需要用戶互動。

### 優點
- ✅ 無需使用者互動
- ✅ 適合自動化和 Docker 環境
- ✅ 金鑰長期有效，無 Token 過期問題
- ✅ 安全性高

### 缺點
- ⚠️ 需要手動分享行事曆
- ⚠️ 服務帳號無法存取個人預設行事曆

## 📋 前置需求

在開始設置之前，請確保已完成 [Google Cloud 專案設置](overview.md#開始之前google-cloud-專案設置)。

## 🚀 設置步驟

### 步驟 1: 建立服務帳號
1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 確保已選擇正確的專案（查看頁面上方的專案名稱）
3. 在左側導航欄中，點擊「IAM & Admin」→「Service Accounts」
4. 點擊「+ CREATE SERVICE ACCOUNT」按鈕
5. 填寫服務帳號資訊：
   - **服務帳號名稱**：`calendarbridge-service`（或您喜歡的名稱）
   - **服務帳號 ID**：系統會自動生成
   - **描述**：`CalendarBridge 服務帳號`
6. 點擊「CREATE AND CONTINUE」
7. 在權限設定頁面，直接點擊「CONTINUE」（跳過權限設定）
8. 點擊「DONE」完成服務帳號建立

### 步驟 2: 建立服務帳號金鑰
1. 在服務帳號列表中，點擊剛建立的服務帳號名稱
2. 在服務帳號詳情頁面，切換到「KEYS」標籤
3. 點擊「ADD KEY」→「Create new key」
4. 選擇「JSON」格式
5. 點擊「CREATE」
6. JSON 金鑰檔案會自動下載到您的下載資料夾
7. 將檔案移動到專案目錄並重新命名：

```bash
# 將下載的金鑰檔案移到正確位置
mv ~/Downloads/your-project-name-*.json config/service_account.json
```

> ⚠️ **安全提醒**：金鑰檔案包含敏感資訊，請妥善保管，勿提交到版本控制系統。


### 步驟 3: 分享行事曆給服務帳號
由於服務帳號無法直接存取您的個人行事曆，需要明確分享給服務帳號：

1. 開啟 [Google Calendar](https://calendar.google.com/)
2. 在左側行事曆列表中，找到要同步的目標行事曆
3. 點擊行事曆名稱旁的**三點選單** (⋮) → 選擇「設定與共用」
4. 在「與特定人員共用」區域：
   - 點擊「新增人員」
   - 在電子郵件欄位輸入服務帳號的電子郵件地址
   - 權限選擇「**進行變更和管理共用設定**」
   - 點擊「傳送」

> 📝 **服務帳號電子郵件格式**：
> `calendarbridge-service@your-project-id.iam.gserviceaccount.com`
>
> 您可以在 Google Cloud Console 的服務帳號頁面找到完整的電子郵件地址。

### 步驟 4: 取得行事曆 ID

1. 在 Google Calendar 中，點擊目標行事曆的設定（在上一步驟的共用頁面）
2. 向下捲動找到「**整合行事曆**」區域
3. 複製「**行事曆 ID**」（格式類似：`abc123def@group.calendar.google.com`）

> 📝 **備註**：行事曆 ID 通常以 `@group.calendar.google.com` 結尾，這是正常的。

### 步驟 5: 配置應用程式
編輯 `config/settings.yaml` 檔案：

```yaml
google_calendar:
  auth_type: "service_account"  # 設定認證類型
  service_account_file: "config/service_account.json"  # 金鑰檔案路徑
  calendar_id: "your-calendar-id@group.calendar.google.com"  # 替換為實際的行事曆 ID
```

> ⚠️ **重要**：請將 `your-calendar-id@group.calendar.google.com` 替換為上一步驟取得的實際行事曆 ID。

### 步驟 6: 測試服務帳號認證

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

## 🔍 常見問題

### Q1: 認證失敗，出現 "Calendar not found" 錯誤
**解決方法**：
- 確認行事曆 ID 正確
- 確認已將行事曆分享給服務帳號
- 檢查服務帳號電子郵件地址是否正確

### Q2: 出現 "Permission denied" 錯誤
**解決方法**：
- 確認服務帳號的權限為「進行變更和管理共用設定」
- 確認 `service_account.json` 檔案路徑正確
- 檢查檔案權限，確保應用程式可以讀取

### Q3: 找不到服務帳號的電子郵件地址
**解決方法**：
1. 前往 Google Cloud Console
2. 導航到 "IAM & Admin" → "Service Accounts"
3. 在服務帳號列表中找到您的服務帳號
4. 電子郵件地址會顯示在 "Email" 欄位

## 🔒 安全性考量

### 金鑰檔案管理
- 金鑰檔案包含敏感資訊，請妥善保管
- 將 `config/service_account.json` 加入 `.gitignore`
- 在生產環境中考慮使用環境變數或 Docker secrets

### 權限控制
- 僅授予必要的最小權限
- 定期輪換服務帳號金鑰
- 監控服務帳號的使用情況

## 🔗 相關文件

- [認證方式概覽](overview.md) - Google Cloud 專案設置與認證方式比較
- [OAuth 認證設置](oauth.md) - 另一種認證方式
- [Docker 部署指南](../deployment/docker.md) - Docker 部署說明
- [疑難排解](../reference/troubleshooting.md) - 更多問題解決方案