# 快速開始指南

這份指南將幫助您快速部署 CalendarBridge。我們推薦使用 **Docker + 服務帳號** 方案，這是最穩定、維護成本最低的部署方式。

## 推薦方案：Docker + 服務帳號 ⭐

一次設置，長期穩定運行，無需定期維護。

**時間**: 約 10-15 分鐘
**難度**: ⭐⭐☆☆☆

### 為什麼選擇這個方案？

- ✅ **完全自動化**：設置後無需人工介入
- ✅ **長期穩定**：無 Token 過期問題
- ✅ **易於管理**：Docker 容器化部署
- ✅ **生產就緒**：適合 24/7 運行

---

## 快速部署步驟

### 步驟 1: 準備環境

```bash
# 確認已安裝 Docker
docker --version
docker compose version

# 如果尚未安裝：
# macOS: brew install --cask docker
# Linux: curl -fsSL https://get.docker.com -o get-docker.sh && sudo sh get-docker.sh
# Windows: 下載 Docker Desktop from docker.com

# 克隆專案
git clone <repository-url>
cd CalendarBridge
```

### 步驟 2: 設置 Google 服務帳號

這是最重要的步驟，請仔細跟隨：

#### 2.1 建立 Google Cloud 專案

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 點擊頁面上方的專案下拉選單
3. 點擊「新增專案」
4. 專案名稱：`CalendarBridge`
5. 點擊「建立」並**記下專案 ID**（稍後會用到）

#### 2.2 啟用 Calendar API

1. 確保已選擇剛建立的專案
2. 在左側選單：「APIs & Services」→「Library」
3. 搜尋「Google Calendar API」
4. 點擊進入並按「啟用」

#### 2.3 建立服務帳號

1. 在左側選單：「IAM & Admin」→「Service Accounts」
2. 點擊「**+ CREATE SERVICE ACCOUNT**」
3. 填寫資訊：
   - 服務帳號名稱：`calendarbridge-service`
   - 服務帳號 ID：自動生成
   - 描述：`CalendarBridge 服務帳號`
4. 點擊「CREATE AND CONTINUE」
5. 在權限頁面直接點擊「CONTINUE」（跳過）
6. 點擊「DONE」

#### 2.4 下載金鑰檔案

1. 在服務帳號列表中，**點擊剛建立的服務帳號名稱**
2. 切換到「**KEYS**」標籤
3. 點擊「ADD KEY」→「Create new key」
4. 選擇「JSON」格式
5. 點擊「CREATE」

金鑰檔案會自動下載到您的下載資料夾。

```bash
# 將下載的金鑰檔案移到專案目錄
mv ~/Downloads/calendarbridge-*.json config/service_account.json

# 確認檔案已移動成功
ls -la config/service_account.json
```

> ⚠️ **重要**：此檔案包含敏感資訊，請妥善保管，勿分享或提交到版本控制。

#### 2.5 取得服務帳號電子郵件地址

在 Google Cloud Console 的服務帳號頁面，您會看到類似這樣的電子郵件地址：

```
calendarbridge-service@your-project-id.iam.gserviceaccount.com
```

**複製這個完整的電子郵件地址**，下一步會用到。

#### 2.6 分享行事曆給服務帳號

1. 開啟 [Google Calendar](https://calendar.google.com/)
2. 在左側找到要同步的**目標行事曆**
3. 點擊行事曆名稱旁的「**⋮**」（三點選單）
4. 選擇「**設定與共用**」
5. 向下捲動到「**與特定人員共用**」區域
6. 點擊「**新增人員**」
7. 在電子郵件欄位貼上步驟 2.5 複製的服務帳號電子郵件地址
8. 權限選擇：「**進行變更和管理共用設定**」
9. 點擊「**傳送**」

#### 2.7 取得行事曆 ID

1. 在同一個設定頁面繼續向下捲動
2. 找到「**整合行事曆**」區域
3. 複製「**行事曆 ID**」

行事曆 ID 格式類似：`abc123def@group.calendar.google.com`

**保存這個 ID**，下一步會用到。

> 📖 **需要更詳細的步驟？** 請參考：[服務帳號設置指南](authentication/service_account.md)

### 步驟 3: 配置應用程式

```bash
# 複製配置範本
cp config/settings.yaml.template config/settings.yaml

# 使用您喜歡的編輯器開啟
nano config/settings.yaml
# 或
vim config/settings.yaml
```

編輯以下內容：

```yaml
# ICS 行事曆來源
ics_calendar:
  url: "https://your-ics-calendar-url.ics"  # ⚠️ 替換為您的 ICS URL
  timezone: "Asia/Taipei"  # 根據您的時區調整

# Google Calendar 設定
google_calendar:
  auth_type: "service_account"  # 使用服務帳號認證
  service_account_file: "config/service_account.json"
  calendar_id: "abc123def@group.calendar.google.com"  # ⚠️ 替換為步驟 2.7 的行事曆 ID

# 同步設定
sync:
  interval_minutes: 30  # 每 30 分鐘同步一次
  lookback_days: 30    # 同步過去 30 天的事件
  lookahead_days: 90   # 同步未來 90 天的事件

# 日誌設定
logging:
  level: "INFO"
  file: "logs/calendarbridge.log"
```

> 💡 **提示**：確保替換了以下兩個值：
> - `ics_calendar.url` - 您的 ICS 行事曆 URL
> - `google_calendar.calendar_id` - 步驟 2.7 取得的行事曆 ID

### 步驟 4: 啟動服務

```bash
# 啟動 Docker 容器（背景運行）
docker compose up -d

# 查看日誌（確認運行正常）
docker compose logs -f
```

如果設置正確，您應該會看到類似以下的日誌：

```
calendarbridge  | INFO - Starting CalendarBridge...
calendarbridge  | INFO - 成功連接到 Google Calendar
calendarbridge  | INFO - 開始同步...
calendarbridge  | INFO - 從 ICS 讀取到 45 個事件
calendarbridge  | INFO - 同步完成：新增 5 個事件，更新 2 個事件，刪除 0 個事件
calendarbridge  | INFO - 下次同步時間: 5 分鐘後
```

按 `Ctrl+C` 可以退出日誌查看（容器會繼續在背景運行）。

### 步驟 5: 驗證同步結果

#### 方法 1: 檢查 Google Calendar

1. 開啟您的 [Google Calendar](https://calendar.google.com/)
2. 查看目標行事曆
3. 確認事件已正確同步

#### 方法 2: 檢查容器狀態

```bash
# 查看容器運行狀態
docker compose ps

# 應該顯示類似：
# NAME              STATUS          PORTS
# calendarbridge    Up 2 minutes
```

#### 方法 3: 查看同步統計

```bash
# 執行狀態檢查腳本
docker compose exec calendarbridge python show_sync_state.py
```

---

## 🎉 完成！

恭喜！您的 CalendarBridge 現在已經開始自動同步了。

### 日常使用

服務會自動在背景運行，每 5 分鐘同步一次，無需任何操作。

常用命令：

```bash
# 查看即時日誌
docker compose logs -f

# 查看最近 100 行日誌
docker compose logs --tail 100

# 重啟服務
docker compose restart

# 停止服務
docker compose stop

# 啟動服務
docker compose start

# 完全停止並移除容器
docker compose down
```

### 系統重啟後

Docker Compose 設定了 `restart: unless-stopped`，所以系統重啟後容器會自動啟動，無需手動操作。

### 更新配置

如果需要修改同步間隔或其他設定：

```bash
# 編輯配置檔案
nano config/settings.yaml

# 重啟服務以套用變更
docker compose restart

# 查看日誌確認
docker compose logs -f
```

---

## 其他部署方案

### 方案二：本地開發（適合測試）

如果您只是想快速測試功能，可以選擇本地部署：

**時間**: 約 5 分鐘
**難度**: ⭐☆☆☆☆
**推薦用途**: 功能測試、開發環境

#### 快速步驟

```bash
# 1. 準備環境
git clone <repository-url>
cd CalendarBridge
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. 配置
cp config/settings.yaml.template config/settings.yaml
# 編輯 settings.yaml，使用 OAuth 認證

# 3. 授權
python setup.py

# 4. 執行
python main.py --once --dry-run  # 測試模式
python main.py --once            # 執行一次
python main.py                   # 持續運行
```

> 📖 詳細步驟：[本地部署指南](deployment/local.md)

---

## 常見問題

### Q: 出現 "Calendar not found" 錯誤

**原因**：服務帳號沒有行事曆的存取權限

**解決方法**：
1. 確認已將行事曆分享給服務帳號（步驟 2.6）
2. 確認行事曆 ID 正確（步驟 2.7）
3. 確認權限為「進行變更和管理共用設定」

### Q: 出現 "Permission denied" 錯誤

**原因**：金鑰檔案問題或權限不足

**解決方法**：
```bash
# 檢查金鑰檔案是否存在
ls -la config/service_account.json

# 檢查 settings.yaml 中的路徑設定
grep service_account_file config/settings.yaml

# 查看詳細錯誤日誌
docker compose logs --tail 50
```

### Q: 容器啟動後立即退出

**解決方法**：
```bash
# 查看詳細錯誤訊息
docker compose logs

# 常見原因：
# - 配置檔案格式錯誤（YAML 語法）
# - 金鑰檔案路徑錯誤
# - ICS URL 無法訪問
```

### Q: ICS URL 無法訪問

**解決方法**：
```bash
# 測試 URL 是否可訪問
curl -I https://your-ics-url.ics

# 如果在 Docker 容器內無法訪問外部網路，檢查網路設定
docker compose exec calendarbridge curl -I https://google.com
```

### Q: 如何查看服務帳號的電子郵件地址？

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 選擇您的專案
3. 導航到「IAM & Admin」→「Service Accounts」
4. 在列表中找到您的服務帳號
5. 電子郵件地址會顯示在「Email」欄位

### Q: 同步沒有更新事件

**可能原因**：
- ICS 來源沒有變更
- 事件已經是最新的
- 時間範圍超出設定

**解決方法**：
```bash
# 啟用 DEBUG 模式查看詳細資訊
# 編輯 config/settings.yaml
# logging:
#   level: "DEBUG"

# 重啟服務
docker compose restart

# 查看詳細日誌
docker compose logs -f
```

---

## 下一步

完成快速開始後，您可以：

- 📖 深入了解 [配置選項](reference/configuration.md)
- 🔐 了解 [認證方式的差異](authentication/overview.md)
- 🐳 學習 [進階 Docker 部署技巧](deployment/docker.md)
- 🛠️ 查看 [完整疑難排解指南](reference/troubleshooting.md)

## 需要幫助？

- 📚 查看 [完整文件](README.md)
- 💬 提交 [GitHub Issue](https://github.com/yourusername/CalendarBridge/issues)
- 🔍 搜尋 [常見問題](reference/troubleshooting.md)
