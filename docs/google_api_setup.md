# Google Calendar API 認證指南

本指南將協助您選擇並設置適合的 Google Calendar API 認證方式。

## 📋 開始之前

在進行認證設置之前，請先完成 [Google Cloud 專案設置](google_cloud_setup.md)。

## 📊 認證方式比較

| 特性 | 服務帳號認證（推薦） | OAuth 認證 |
|------|------------------|------------|
| **適用場景** | 自動化部署、Docker 環境 | 個人開發、測試 |
| **使用者互動** | ❌ 無需使用者授權 | ✅ 需要瀏覽器授權 |
| **Token 管理** | ❌ 無 Token 過期問題 | ⚠️ Token 會過期需重新授權 |
| **行事曆存取** | ⚠️ 需要明確分享行事曆 | ✅ 可存取個人所有行事曆 |
| **安全性** | ✅ 服務帳號金鑰管理 | ✅ OAuth 標準流程 |
| **維護成本** | ✅ 低，設定後免維護 | ⚠️ 高，需定期重新授權 |
| **Docker 友善** | ✅ 完全支援 | ⚠️ 需要預先授權 |

### 🏆 推薦選擇

- **生產環境、Docker 部署**: 選擇 **服務帳號認證**
- **個人開發、快速測試**: 選擇 **OAuth 認證**

## 🏢 服務帳號認證（推薦）

**適用於**：生產環境、Docker 部署、自動化系統

**完整設置指南**：[服務帳號設置指南](service_account_setup.md)

**特點**：
- ✅ 無需使用者互動
- ✅ 適合自動化部署
- ✅ 長期穩定運行
- ✅ 無 Token 過期問題
- ⚠️ 需要明確分享行事曆

## 🔧 OAuth 認證設置（個人使用）

**適用於**：個人開發、快速測試、存取個人行事曆

**完整設置指南**：[OAuth 認證詳細步驟](google_api_setup.md#oauth-認證詳細步驟)

**特點**：
- ✅ 可存取個人所有行事曆
- ✅ 設置相對簡單
- ⚠️ 需要瀏覽器授權
- ⚠️ Token 會過期需重新授權

---

## OAuth 認證詳細步驟

### 步驟 1: 建立 OAuth 認證

> 💡 **前置需求**：確保已完成 [Google Cloud 專案設置](google_cloud_setup.md)

1. 在 Google Cloud Console 中，導航到「APIs & Services」→「Credentials」
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

### 步驟 2: 初次授權

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