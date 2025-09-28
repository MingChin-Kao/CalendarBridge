# CalendarBridge 服務帳號設置

## 什麼是服務帳號？
服務帳號是 Google Cloud 為應用程式提供的身份認證方式，不需要用戶互動。

## 設置步驟

### 1. 創建服務帳號
1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 選擇您的專案
3. 導航到 "IAM & Admin" → "Service Accounts"
4. 點擊 "CREATE SERVICE ACCOUNT"
5. 輸入名稱，如 "calendarbridge-service"
6. 點擊 "CREATE AND CONTINUE"

### 2. 下載金鑰檔案
1. 在服務帳號列表中，點擊剛創建的服務帳號
2. 切換到 "KEYS" 標籤
3. 點擊 "ADD KEY" → "Create new key"
4. 選擇 "JSON" 格式
5. 下載並保存為 `config/service_account.json`

### 3. 啟用 Google Calendar API
1. 在 Google Cloud Console 中，導航到 "APIs & Services" → "Library"
2. 搜尋 "Google Calendar API"
3. 點擊並啟用

### 4. 分享行事曆給服務帳號
1. 打開 Google Calendar
2. 在左側找到目標行事曆，點擊設定 (⚙️)
3. 選擇 "Settings and sharing"
4. 在 "Share with specific people" 中添加服務帳號的 email
   (格式：service-account-name@project-id.iam.gserviceaccount.com)
5. 權限設置為 "Make changes and manage sharing"

### 5. 配置應用程式
修改 `config/settings.yaml`:
```yaml
google_calendar:
  auth_type: "service_account"  # 新增
  service_account_file: "config/service_account.json"  # 新增
  calendar_id: "your-calendar-id"
```

## 優點
- 無需用戶互動
- 適合自動化和 Docker 環境
- 金鑰長期有效
- 安全性高

## 缺點
- 需要手動分享行事曆
- 服務帳號無法存取個人預設行事曆