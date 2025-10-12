# Google Cloud 專案設置指南

本指南說明如何建立和配置 Google Cloud 專案，為 CalendarBridge 使用 Google Calendar API 做準備。

## 📋 前置需求

- Google 帳號
- 網路瀏覽器

## 🚀 設置步驟

### 步驟 1: 建立 Google Cloud 專案

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 點擊頁面上方的專案下拉選單
3. 點擊「新增專案」按鈕
4. 填寫專案資訊：
   - **專案名稱**: `CalendarBridge`（或您偏好的名稱）
   - **組織**: 保持預設值
   - **位置**: 保持預設值
5. 點擊「建立」按鈕
6. 等待專案建立完成（通常需要幾秒鐘）
7. **重要**: 記下專案 ID，稍後設置服務帳號時會用到

> 💡 **專案 ID 與專案名稱不同**：專案 ID 是系統自動生成的唯一識別碼，格式通常為 `project-name-123456`

### 步驟 2: 啟用 Google Calendar API

1. 確保已選擇正確的專案（查看頁面上方的專案名稱）
2. 在左側導航欄中，點擊「APIs & Services」→「Library」
3. 在搜尋框中輸入「Google Calendar API」
4. 點擊搜尋結果中的「Google Calendar API」
5. 點擊「啟用」按鈕
6. 等待 API 啟用完成

### 步驟 3: 驗證設置

完成上述步驟後，您應該能看到：
- 在「APIs & Services」→「Enabled APIs」中看到 Google Calendar API
- 專案儀表板顯示您的專案資訊

## ✅ 後續步驟

專案設置完成後，請根據您的使用情境選擇認證方式：

### 🏢 生產環境 / Docker 部署（推薦）
繼續閱讀 [服務帳號設置指南](service_account_setup.md)

### 🔧 個人開發 / 測試環境
繼續閱讀 [OAuth 認證設置](google_api_setup.md#🔧-oauth-認證設置個人使用)

## 🔍 常見問題

### Q: 我需要啟用計費嗎？
A: 對於 CalendarBridge 的基本使用，Google Calendar API 在免費額度內通常已足夠。如果您的使用量超過免費額度，才需要設置計費帳戶。

### Q: 可以在現有專案中使用嗎？
A: 可以，您可以在現有的 Google Cloud 專案中啟用 Google Calendar API，只要確保該專案有足夠的權限。

### Q: 如何找到我的專案 ID？
A: 在 Google Cloud Console 的儀表板上方，專案名稱旁邊會顯示專案 ID，或者在「專案設定」頁面中可以找到。

## 🔗 相關文件

- [認證方式選擇指南](google_api_setup.md)
- [服務帳號設置指南](service_account_setup.md)
- [部署指南](deployment_guide.md)