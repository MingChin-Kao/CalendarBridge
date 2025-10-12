# 本地部署指南

本指南說明如何在本機環境運行 CalendarBridge，適合個人開發和測試。

## 系統需求

- **Python**: 3.8 或更高版本
- **作業系統**: macOS、Linux 或 Windows
- **網路**: 需要連接網際網路以存取 ICS 來源和 Google Calendar API

## 安裝步驟

### 步驟 1: 獲取專案

```bash
# 克隆專案（如果尚未克隆）
git clone <repository-url>
cd CalendarBridge
```

### 步驟 2: 建立虛擬環境

建議使用虛擬環境以隔離專案依賴：

```bash
# 建立虛擬環境
python3 -m venv venv

# 啟動虛擬環境
# macOS/Linux:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

> 💡 啟動虛擬環境後，終端機提示符前會顯示 `(venv)`

### 步驟 3: 安裝依賴

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 步驟 4: 配置檔案設置

複製配置範本並編輯：

```bash
cp config/settings.yaml.template config/settings.yaml
```

編輯 `config/settings.yaml`：

```yaml
# ICS 行事曆設定
ics_calendar:
  url: "https://your-ics-calendar-url.ics"  # 替換為您的 ICS URL
  timezone: "Asia/Taipei"  # 時區設定

# Google Calendar 設定
google_calendar:
  auth_type: "oauth"  # 本地開發推薦使用 OAuth
  credentials_file: "config/credentials.json"
  token_file: "config/token.json"
  calendar_id: "primary"  # 主要行事曆，或指定特定行事曆 ID

# 同步設定
sync:
  interval_minutes: 5  # 同步間隔（分鐘）
  lookback_days: 30    # 回溯天數
  lookahead_days: 90   # 預先同步天數

# 日誌設定
logging:
  level: "INFO"  # DEBUG, INFO, WARNING, ERROR
  file: "logs/calendarbridge.log"
```

> 📖 更多配置選項請參考：[配置說明](../reference/configuration.md)

### 步驟 5: 設置認證

本地開發推薦使用 OAuth 認證：

#### 5.1 建立 OAuth 憑證

參考 [OAuth 認證指南](../authentication/oauth.md) 完成以下步驟：
1. 在 Google Cloud Console 建立專案
2. 啟用 Google Calendar API
3. 建立 OAuth 憑證
4. 下載 `credentials.json` 到 `config/` 目錄

#### 5.2 執行初次授權

```bash
python setup.py
```

這會：
1. 開啟瀏覽器進行授權
2. 產生 `config/token.json`
3. 測試連線

## 執行同步

### 測試模式（Dry Run）

在實際同步前，建議先測試：

```bash
python main.py --once --dry-run
```

這會：
- 讀取 ICS 行事曆
- 比對 Google Calendar
- 顯示將要執行的操作
- **不會實際修改行事曆**

### 執行一次同步

```bash
python main.py --once
```

這會執行單次同步並結束。

### 持續同步模式

```bash
python main.py
```

這會：
- 執行初次同步
- 每隔設定的時間間隔（預設 5 分鐘）自動同步
- 按 `Ctrl+C` 停止

### 指定配置檔案

```bash
python main.py --config /path/to/custom/settings.yaml
```

## 進階使用

### 查看同步狀態

```bash
python show_sync_state.py
```

這會顯示：
- 已同步的事件數量
- 最後同步時間
- 資料庫統計資訊

### 列出可用的行事曆

```bash
python get_calendar_list.py
```

這會列出您有權限存取的所有 Google Calendar。

### 清理資料庫

如果遇到同步問題，可以重置資料庫：

```bash
python clean_database.py
```

> ⚠️ **警告**：這會清除所有同步記錄，下次同步可能需要較長時間。

### 查看詳細日誌

```bash
# 即時查看日誌
tail -f logs/calendarbridge.log

# 查看最近的錯誤
grep ERROR logs/calendarbridge.log

# 使用 DEBUG 模式獲取更多資訊
# 編輯 config/settings.yaml:
# logging:
#   level: "DEBUG"
```

## 設置自動啟動

### macOS/Linux: 使用 cron

編輯 crontab：

```bash
crontab -e
```

新增以下行（每小時執行一次）：

```cron
0 * * * * cd /path/to/CalendarBridge && /path/to/venv/bin/python main.py --once
```

### macOS: 使用 launchd

建立 `~/Library/LaunchAgents/com.calendarbridge.plist`：

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.calendarbridge</string>
    <key>ProgramArguments</key>
    <array>
        <string>/path/to/venv/bin/python</string>
        <string>/path/to/CalendarBridge/main.py</string>
    </array>
    <key>StartInterval</key>
    <integer>300</integer>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
```

載入服務：

```bash
launchctl load ~/Library/LaunchAgents/com.calendarbridge.plist
```

### Windows: 使用工作排程器

1. 開啟「工作排程器」
2. 建立基本工作
3. 觸發程序：選擇執行頻率
4. 動作：啟動程式
   - 程式：`C:\path\to\venv\Scripts\python.exe`
   - 引數：`C:\path\to\CalendarBridge\main.py --once`
   - 起始於：`C:\path\to\CalendarBridge`

### Linux: 使用 systemd

建立 `/etc/systemd/system/calendarbridge.service`：

```ini
[Unit]
Description=CalendarBridge Sync Service
After=network.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/CalendarBridge
ExecStart=/path/to/venv/bin/python /path/to/CalendarBridge/main.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

啟用服務：

```bash
sudo systemctl daemon-reload
sudo systemctl enable calendarbridge
sudo systemctl start calendarbridge

# 查看狀態
sudo systemctl status calendarbridge

# 查看日誌
sudo journalctl -u calendarbridge -f
```

## 疑難排解

### 常見問題

#### Q1: 找不到 Python 或 pip

**解決方法**：
```bash
# macOS (使用 Homebrew)
brew install python3

# Ubuntu/Debian
sudo apt-get update
sudo apt-get install python3 python3-pip python3-venv

# Windows
# 從 python.org 下載並安裝 Python
```

#### Q2: 安裝依賴時出現錯誤

**解決方法**：
```bash
# 升級 pip
pip install --upgrade pip

# 清除快取重新安裝
pip cache purge
pip install -r requirements.txt --no-cache-dir

# 如果遇到編譯錯誤，可能需要安裝編譯工具
# macOS: xcode-select --install
# Ubuntu: sudo apt-get install build-essential python3-dev
```

#### Q3: OAuth 授權失敗

**解決方法**：
1. 確認 `config/credentials.json` 存在且格式正確
2. 確認已將您的 Gmail 地址加入測試使用者
3. 刪除 `config/token.json` 並重新執行 `python setup.py`
4. 參考：[OAuth 疑難排解](../authentication/oauth.md#常見問題)

#### Q4: 無法連接到 ICS URL

**解決方法**：
1. 測試 URL 是否可訪問：`curl -I <your-ics-url>`
2. 檢查防火牆設定
3. 確認 URL 格式正確（應該以 `.ics` 結尾）
4. 查看日誌檔案：`cat logs/calendarbridge.log`

#### Q5: 同步沒有更新事件

**可能原因**：
- ICS 來源沒有變更
- 事件已經是最新的（檢查 SEQUENCE 欄位）
- 時間範圍設定不正確

**解決方法**：
```bash
# 使用 DEBUG 模式查看詳細資訊
# 編輯 config/settings.yaml，設定 logging.level: "DEBUG"
python main.py --once --dry-run

# 查看同步狀態
python show_sync_state.py
```

### 取得幫助

如果問題仍未解決：

1. 查看 [疑難排解指南](../reference/troubleshooting.md)
2. 檢查日誌檔案：`logs/calendarbridge.log`
3. 提交 [GitHub Issue](https://github.com/yourusername/CalendarBridge/issues)

## 從本地遷移到 Docker

如果您想從本地部署遷移到 Docker：

1. 參考 [服務帳號設置](../authentication/service_account.md) 建立服務帳號
2. 更新 `config/settings.yaml` 使用服務帳號認證
3. 參考 [Docker 部署指南](docker.md) 進行部署

## 相關文件

- [OAuth 認證指南](../authentication/oauth.md) - OAuth 詳細設置
- [配置說明](../reference/configuration.md) - 完整配置選項
- [Docker 部署](docker.md) - 遷移到 Docker
- [疑難排解](../reference/troubleshooting.md) - 更多問題解決方案
