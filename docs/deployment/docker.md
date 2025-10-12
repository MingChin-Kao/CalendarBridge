# Docker 部署指南

本指南說明如何使用 Docker 部署 CalendarBridge，適合生產環境和長期穩定運行。

## 為什麼選擇 Docker？

- ✅ 環境一致性：開發和生產環境完全相同
- ✅ 易於部署：一個命令完成部署
- ✅ 資源隔離：獨立的運行環境
- ✅ 易於維護：簡化更新和回滾
- ✅ 持續運行：自動重啟和錯誤恢復

## 系統需求

- **Docker**: 20.10 或更高版本
- **Docker Compose**: 2.0 或更高版本
- **作業系統**: Linux、macOS 或 Windows（支援 Docker Desktop）

### 安裝 Docker

```bash
# macOS（使用 Homebrew）
brew install --cask docker

# Ubuntu/Debian
sudo apt-get update
sudo apt-get install docker.io docker-compose-v2

# 或使用官方安裝腳本
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
```

驗證安裝：
```bash
docker --version
docker compose version
```

## 部署方案選擇

Docker 部署支援兩種認證方式：

| 方案 | 推薦度 | 適用場景 | 維護成本 |
|------|-------|---------|---------|
| **服務帳號認證** | ⭐⭐⭐⭐⭐ | 生產環境、自動化部署 | 低 |
| **OAuth 認證** | ⭐⭐⭐ | 個人使用、測試環境 | 中（需定期重新授權） |

> 💡 **建議**：對於 Docker 部署，強烈推薦使用服務帳號認證，因為它更適合自動化環境。

---

## 方案一：服務帳號認證（推薦）

這是生產環境的最佳選擇，完全自動化，無需人工介入。

### 步驟 1: 準備服務帳號

按照 [服務帳號設置指南](../authentication/service_account.md) 完成以下步驟：

1. 建立 Google Cloud 專案
2. 啟用 Google Calendar API
3. 建立服務帳號並下載金鑰
4. 將金鑰檔案儲存為 `config/service_account.json`
5. 分享行事曆給服務帳號

### 步驟 2: 配置檔案

複製並編輯配置範本：

```bash
cp config/settings.yaml.template config/settings.yaml
```

編輯 `config/settings.yaml`：

```yaml
# ICS 行事曆來源
ics_calendar:
  url: "https://your-ics-calendar-url.ics"  # 替換為您的 ICS URL
  timezone: "Asia/Taipei"

# Google Calendar 設定
google_calendar:
  auth_type: "service_account"  # 使用服務帳號認證
  service_account_file: "config/service_account.json"
  calendar_id: "your-calendar-id@group.calendar.google.com"  # 替換為您的行事曆 ID

# 同步設定
sync:
  interval_minutes: 5  # 同步間隔（分鐘）
  lookback_days: 30    # 回溯天數
  lookahead_days: 90   # 預先同步天數

# 日誌設定
logging:
  level: "INFO"
  file: "logs/calendarbridge.log"
```

> 📝 **取得行事曆 ID**：
> 1. 開啟 [Google Calendar](https://calendar.google.com/)
> 2. 點擊目標行事曆的設定
> 3. 在「整合行事曆」區域找到「行事曆 ID」

### 步驟 3: 驗證檔案結構

確認以下檔案已準備好：

```bash
CalendarBridge/
├── config/
│   ├── settings.yaml                 # ✅ 已配置
│   └── service_account.json          # ✅ 已下載
├── docker-compose.yml                # ✅ 已存在
└── Dockerfile                        # ✅ 已存在
```

檢查檔案：
```bash
ls -la config/settings.yaml config/service_account.json
```

### 步驟 4: 部署

```bash
# 啟動服務
docker compose up -d

# 查看運行狀態
docker compose ps

# 查看日誌（確認同步正常）
docker compose logs -f
```

如果一切正常，您應該會看到類似以下的日誌：

```
calendarbridge  | INFO - 成功連接到 Google Calendar
calendarbridge  | INFO - 開始同步...
calendarbridge  | INFO - 同步完成：新增 5 個事件，更新 2 個事件
```

### 步驟 5: 驗證同步

```bash
# 檢查容器狀態
docker compose ps

# 查看最近的同步日誌
docker compose logs --tail 50

# 檢查資料庫（可選）
docker compose exec calendarbridge python show_sync_state.py
```

### 優點

- ✅ 完全自動化，無需使用者互動
- ✅ 金鑰長期有效，無 Token 過期問題
- ✅ 適合 24/7 運行
- ✅ 維護成本極低

---

## 方案二：OAuth 認證

適合個人使用或測試環境，但需要定期重新授權。

### 步驟 1: 本地完成 OAuth 授權

Docker 容器無法開啟瀏覽器，因此需要先在本地完成授權：

```bash
# 確保已有 credentials.json
ls config/credentials.json

# 如果沒有，請參考 OAuth 認證指南創建
# 參考：../authentication/oauth.md

# 執行初次授權
python setup.py

# 確認產生 token.json
ls config/token.json
```

### 步驟 2: 配置檔案

編輯 `config/settings.yaml`：

```yaml
ics_calendar:
  url: "https://your-ics-calendar-url.ics"

google_calendar:
  auth_type: "oauth"  # 使用 OAuth 認證
  credentials_file: "config/credentials.json"
  token_file: "config/token.json"
  calendar_id: "primary"  # 或指定特定行事曆 ID

sync:
  interval_minutes: 5
```

### 步驟 3: 修改 docker-compose.yml

確保 `docker-compose.yml` 包含 OAuth 相關的 volume 掛載：

```yaml
version: '3.8'

services:
  calendarbridge:
    build: .
    volumes:
      # OAuth 認證檔案掛載
      - ./config/credentials.json:/app/config/credentials.json:ro
      - ./config/token.json:/app/config/token.json
      # 數據持久化
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - TZ=Asia/Taipei
    restart: unless-stopped
```

> 📝 **注意**：`token.json` 不要使用 `:ro`（唯讀），因為 token 可能需要自動更新。

### 步驟 4: 部署

```bash
# 啟動服務
docker compose up -d

# 查看日誌
docker compose logs -f
```

### 步驟 5: Token 維護

當 OAuth Token 過期時，執行以下步驟：

```bash
# 停止容器
docker compose stop

# 刪除舊的 token
rm config/token.json

# 重新授權
python setup.py

# 重啟容器
docker compose start

# 查看日誌確認
docker compose logs -f
```

#### 自動化腳本

創建 `scripts/renew_oauth_token.sh`：

```bash
#!/bin/bash
set -e

echo "🔄 重新授權 OAuth Token..."

# 停止容器
docker compose stop calendarbridge

# 刪除舊的 token
rm -f config/token.json

# 重新授權
echo "⚙️ 正在重新授權（將開啟瀏覽器）..."
python setup.py

# 確認 token 已建立
if [ -f "config/token.json" ]; then
    echo "✅ Token 建立成功"
else
    echo "❌ Token 建立失敗"
    exit 1
fi

# 重啟容器
echo "🚀 重啟容器..."
docker compose start calendarbridge

echo "✅ OAuth Token 更新完成！"
```

使用方式：

```bash
chmod +x scripts/renew_oauth_token.sh
./scripts/renew_oauth_token.sh
```

### 優點與缺點

**優點**：
- ✅ 可存取個人所有行事曆
- ✅ 設置相對簡單
- ✅ 使用個人 Google 帳號

**缺點**：
- ⚠️ 需要定期重新授權（通常每年一次）
- ⚠️ Token 失效時服務會停止
- ⚠️ 不適合完全自動化的環境

---

## 常用 Docker 命令

### 查看狀態

```bash
# 查看容器狀態
docker compose ps

# 查看容器詳細資訊
docker compose ps -a

# 查看資源使用情況
docker stats calendarbridge
```

### 日誌管理

```bash
# 即時查看日誌
docker compose logs -f

# 查看最近 100 行日誌
docker compose logs --tail 100

# 只查看錯誤日誌
docker compose logs | grep ERROR

# 按時間戳排序
docker compose logs -t
```

### 容器管理

```bash
# 停止服務
docker compose stop

# 啟動服務
docker compose start

# 重啟服務
docker compose restart

# 完全停止並移除容器
docker compose down

# 停止並移除容器和 volume
docker compose down -v
```

### 進入容器

```bash
# 進入容器 shell
docker compose exec calendarbridge /bin/bash

# 執行 Python 指令
docker compose exec calendarbridge python show_sync_state.py

# 查看行事曆列表
docker compose exec calendarbridge python get_calendar_list.py
```

---

## 更新部署

### 更新應用程式

```bash
# 停止服務
docker compose stop

# 更新程式碼
git pull

# 重建映像
docker compose build --no-cache

# 重啟服務
docker compose up -d

# 查看日誌確認
docker compose logs -f
```

### 更新配置

```bash
# 修改配置檔案
nano config/settings.yaml

# 重啟服務以套用變更
docker compose restart

# 查看日誌確認
docker compose logs -f
```

### 回滾版本

```bash
# 回到之前的版本
git checkout <previous-commit>

# 重建映像
docker compose build

# 重啟服務
docker compose up -d
```

---

## 監控與維護

### 健康檢查

Docker Compose 包含內建的健康檢查：

```bash
# 查看健康狀態
docker inspect calendarbridge | grep -A 10 Health

# 如果容器不健康，查看日誌
docker compose logs --tail 100
```

### 定期維護

建議定期執行以下維護任務：

```bash
# 每週：查看日誌，確認無錯誤
docker compose logs --tail 500 | grep -i error

# 每月：檢查磁碟空間
du -sh data/ logs/

# 每季：清理舊日誌
find logs/ -name "*.log" -mtime +90 -delete

# 定期：備份資料庫
cp data/sync_state.db data/sync_state.db.backup.$(date +%Y%m%d)
```

### 資料備份

```bash
# 備份配置和資料
tar -czf calendarbridge-backup-$(date +%Y%m%d).tar.gz \
  config/ data/ logs/

# 恢復備份
tar -xzf calendarbridge-backup-YYYYMMDD.tar.gz
```

### 監控腳本

創建 `scripts/monitor.sh`：

```bash
#!/bin/bash

# 檢查容器是否運行
if ! docker compose ps | grep -q "Up"; then
    echo "❌ 容器未運行"
    docker compose up -d
    exit 1
fi

# 檢查最近是否有錯誤
ERRORS=$(docker compose logs --since 1h | grep -i error | wc -l)
if [ "$ERRORS" -gt 0 ]; then
    echo "⚠️  發現 $ERRORS 個錯誤"
    docker compose logs --tail 20 | grep -i error
fi

echo "✅ 系統正常運行"
```

設置 cron 定期執行：

```bash
# 每小時檢查一次
0 * * * * cd /path/to/CalendarBridge && ./scripts/monitor.sh
```

---

## 效能調優

### 資源限制

修改 `docker-compose.yml`：

```yaml
services:
  calendarbridge:
    # ... 其他設定 ...
    deploy:
      resources:
        limits:
          memory: 512M      # 記憶體限制
          cpus: '1.0'       # CPU 限制
        reservations:
          memory: 256M      # 保證最小記憶體
          cpus: '0.5'       # 保證最小 CPU
```

### 同步頻率優化

根據需求調整 `config/settings.yaml`：

```yaml
sync:
  interval_minutes: 15  # 降低同步頻率以節省資源
  lookback_days: 7      # 減少回溯範圍
  lookahead_days: 30    # 減少預先同步範圍
```

### 日誌優化

```yaml
logging:
  level: "WARNING"  # 只記錄警告和錯誤，減少 I/O
  file: "logs/calendarbridge.log"
```

---

## 疑難排解

### 容器無法啟動

**檢查方法**：
```bash
# 查看詳細錯誤
docker compose logs

# 檢查配置檔案
docker compose config

# 檢查檔案權限
ls -la config/
```

**常見原因**：
- 配置檔案格式錯誤
- 認證檔案缺失
- 權限問題

### 認證失敗

**服務帳號認證**：
```bash
# 檢查金鑰檔案是否存在
docker compose exec calendarbridge ls -la config/service_account.json

# 測試認證
docker compose exec calendarbridge python -c "
from src.clients.google_calendar import GoogleCalendarClient
from src.utils.config import load_config
config = load_config('config/settings.yaml')
client = GoogleCalendarClient(config.google_calendar)
client.authenticate()
print('✅ 認證成功')
"
```

**OAuth 認證**：
```bash
# 檢查 token 是否存在
ls -la config/token.json

# 如果過期，重新授權
./scripts/renew_oauth_token.sh
```

### 同步沒有更新

**檢查步驟**：

1. **確認 ICS 來源可訪問**：
   ```bash
   curl -I https://your-ics-url.ics
   ```

2. **查看詳細日誌**：
   ```bash
   # 臨時啟用 DEBUG 模式
   # 修改 config/settings.yaml: logging.level: "DEBUG"
   docker compose restart
   docker compose logs -f
   ```

3. **檢查同步狀態**：
   ```bash
   docker compose exec calendarbridge python show_sync_state.py
   ```

### 容器意外重啟

```bash
# 查看容器退出原因
docker compose ps -a

# 查看最近的日誌
docker compose logs --tail 200

# 檢查系統資源
docker stats

# 增加記憶體限制（如果是 OOM）
# 修改 docker-compose.yml 中的 memory 設定
```

### 磁碟空間不足

```bash
# 查看磁碟使用
df -h

# 清理 Docker 系統
docker system prune -a

# 清理舊日誌
find logs/ -name "*.log" -mtime +30 -delete

# 壓縮舊日誌
gzip logs/*.log
```

---

## 安全性考量

### 保護敏感檔案

確保以下檔案不會洩漏：

```bash
# .gitignore
config/service_account.json
config/credentials.json
config/token.json
config/settings.yaml
data/
logs/
```

### 使用 Docker Secrets（進階）

對於更高的安全性，可以使用 Docker Secrets：

```yaml
version: '3.8'

services:
  calendarbridge:
    # ... 其他設定 ...
    secrets:
      - service_account
    environment:
      - SERVICE_ACCOUNT_FILE=/run/secrets/service_account

secrets:
  service_account:
    file: ./config/service_account.json
```

### 網路隔離

```yaml
services:
  calendarbridge:
    networks:
      - internal

networks:
  internal:
    driver: bridge
```

---

## 從本地遷移到 Docker

如果您已經在本地運行 CalendarBridge：

1. **備份現有資料**：
   ```bash
   cp -r data/ data.backup/
   cp -r config/ config.backup/
   ```

2. **準備 Docker 配置**：
   - 確認 `docker-compose.yml` 正確
   - 確認 volume 掛載路徑

3. **遷移認證檔案**：
   - 服務帳號：確保 `config/service_account.json` 存在
   - OAuth：確保 `config/token.json` 存在

4. **啟動 Docker**：
   ```bash
   docker compose up -d
   ```

5. **驗證**：
   ```bash
   docker compose logs -f
   python show_sync_state.py  # 在本地執行比對
   ```

---

## 相關文件

- [服務帳號設置](../authentication/service_account.md) - 推薦的認證方式
- [OAuth 認證](../authentication/oauth.md) - 另一種認證方式
- [配置說明](../reference/configuration.md) - 完整配置選項
- [疑難排解](../reference/troubleshooting.md) - 更多問題解決方案
