# Google Calendar API 設置指南

本指南將協助您設置 Google Calendar API，包含 OAuth 和服務帳號兩種認證方式。

## 🔧 OAuth 認證設置（個人使用）

### 步驟 1: 建立 Google Cloud 專案

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 點擊專案下拉選單，選擇「新增專案」
3. 輸入專案名稱（例如：「CalendarBridge」）
4. 記下專案 ID，稍後會用到

### 步驟 2: 啟用 Google Calendar API

1. 在 Google Cloud Console 中，確保已選擇正確的專案
2. 導航到「APIs & Services」→「Library」
3. 搜尋「Google Calendar API」
4. 點擊「Google Calendar API」
5. 點擊「啟用」按鈕

### 步驟 3: 建立 OAuth 認證

1. 導航到「APIs & Services」→「Credentials」
2. 點擊「+ CREATE CREDENTIALS」
3. 選擇「OAuth 2.0 Client IDs」
4. 如果是第一次建立，需要先配置 OAuth 同意畫面：
   - 點擊「CONFIGURE CONSENT SCREEN」
   - 選擇「外部」（External）
   - 填寫應用程式名稱：「CalendarBridge」
   - 填寫使用者支援電子郵件
   - 填寫開發人員聯絡資訊
   - 點擊「儲存並繼續」
   - 在範圍頁面直接點擊「儲存並繼續」
   - 在測試使用者頁面可以新增您的 Gmail 地址
   - 點擊「儲存並繼續」

5. 回到建立 OAuth 客戶端：
   - 應用程式類型選擇「桌面應用程式」
   - 名稱輸入「CalendarBridge」
   - 點擊「建立」

6. 下載認證檔案：
   - 點擊下載圖示下載 JSON 檔案
   - 將檔案重新命名為 `credentials.json`
   - 移動到專案的 `config/` 目錄

```bash
# 將下載的認證檔案移到正確位置
mv ~/Downloads/client_secret_*.json config/credentials.json
```

### 步驟 4: 初次授權

```bash
# 執行設置腳本
python setup.py

# 或手動執行認證
python -c "
from src.clients.google_calendar import GoogleCalendarClient
from src.utils.config import load_config
config = load_config('config/settings.yaml')
client = GoogleCalendarClient(config.google_calendar)
client.authenticate()
print('認證成功！')
"
```

這會開啟瀏覽器，要求您：
1. 登入 Google 帳號
2. 授權應用程式存取您的 Google Calendar
3. 完成後會自動產生 `config/token.json`

## 🏢 服務帳號認證設置（生產環境推薦）

服務帳號適合自動化和 Docker 環境，無需使用者互動。

### 步驟 1: 建立服務帳號

1. 在 Google Cloud Console 中，導航到「IAM & Admin」→「Service Accounts」
2. 點擊「+ CREATE SERVICE ACCOUNT」
3. 填寫服務帳號詳情：
   - 服務帳號名稱：`calendarbridge-service`
   - 服務帳號 ID：會自動產生
   - 描述：`CalendarBridge Service Account`
4. 點擊「CREATE AND CONTINUE」
5. 跳過權限設定（點擊「CONTINUE」）
6. 點擊「DONE」

### 步驟 2: 建立服務帳號金鑰

1. 在服務帳號列表中，點擊剛建立的服務帳號
2. 切換到「KEYS」標籤
3. 點擊「ADD KEY」→「Create new key」
4. 選擇「JSON」格式
5. 點擊「CREATE」
6. JSON 金鑰檔案會自動下載
7. 將檔案重新命名並移到專案目錄：

```bash
mv ~/Downloads/your-project-*.json config/service_account.json
```

### 步驟 3: 分享行事曆給服務帳號

由於服務帳號無法存取您的個人行事曆，需要明確分享：

1. 開啟 [Google Calendar](https://calendar.google.com/)
2. 在左側行事曆列表中，找到要同步的目標行事曆
3. 點擊行事曆旁的三點選單 → 「設定與共用」
4. 在「與特定人員共用」區域：
   - 點擊「新增人員」
   - 輸入服務帳號的電子郵件地址
     （格式：`calendarbridge-service@your-project-id.iam.gserviceaccount.com`）
   - 權限選擇「進行變更和管理共用設定」
   - 點擊「傳送」

### 步驟 4: 取得行事曆 ID

1. 在 Google Calendar 中，點擊目標行事曆的設定
2. 向下捲動找到「行事曆 ID」
3. 複製行事曆 ID（類似：`abc123@group.calendar.google.com`）

### 步驟 5: 配置應用程式

修改 `config/settings.yaml`：

```yaml
google_calendar:
  auth_type: "service_account"
  service_account_file: "config/service_account.json"
  calendar_id: "your-calendar-id@group.calendar.google.com"
```

### 步驟 6: 測試服務帳號認證

```bash
python -c "
from src.clients.google_calendar import GoogleCalendarClient
from src.utils.config import load_config
config = load_config('config/settings.yaml')
client = GoogleCalendarClient(config.google_calendar)
client.authenticate()
cal_info = client.get_calendar_info()
print(f'成功連接到行事曆: {cal_info.get(\"summary\", \"Unknown\")}')
"
```

## 🔍 疑難排解

### OAuth 常見問題

1. **「access_blocked」錯誤**
   - 確保 OAuth 同意畫面已正確配置
   - 檢查是否已將您的 Gmail 地址加入測試使用者

2. **「redirect_uri_mismatch」錯誤**
   - 確保選擇的是「桌面應用程式」類型

3. **Token 過期**
   - 刪除 `config/token.json` 並重新執行認證

### 服務帳號常見問題

1. **「Calendar not found」錯誤**
   - 確認行事曆 ID 正確
   - 確認已將行事曆分享給服務帳號

2. **「Permission denied」錯誤**
   - 確認服務帳號的權限為「進行變更和管理共用設定」
   - 確認服務帳號 JSON 檔案路徑正確

3. **找不到服務帳號電子郵件**
   - 在 Google Cloud Console 的服務帳號頁面可以找到完整的電子郵件地址

## 🔒 安全性考量

### OAuth
- Token 檔案包含敏感資訊，請勿提交到版本控制
- 定期檢查授權的應用程式清單

### 服務帳號
- JSON 金鑰檔案具有完整存取權限，請妥善保管
- 考慮使用環境變數或密碼管理工具
- 定期輪換服務帳號金鑰

### 建議
- 將 `config/*.json` 加入 `.gitignore`
- 在生產環境使用環境變數或 Docker secrets
- 僅授予必要的最小權限