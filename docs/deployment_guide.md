# CalendarBridge 部署指南

## 📋 部署前準備

在開始部署前，請確保您已經準備好以下檔案：

### 必要檔案
- `config/settings.yaml` - 主要配置檔案（從 `config/settings.yaml.template` 複製並修改）
- 認證檔案（選擇其中一種）：
  - **服務帳號方式**：`config/service_account.json`
  - **OAuth 方式**：`config/token.json`

### 相關文件
- [Google API 設定指南](google_api_setup.md) - 設定 Google Calendar API 和 OAuth 憑證
- [服務帳號設定指南](service_account_setup.md) - 設定服務帳號認證（推薦）
- [Docker OAuth 設定指南](docker_oauth_setup.md) - OAuth 認證設定
- [配置說明](configuration.md) - 詳細配置選項說明
- [故障排除指南](troubleshooting.md) - 常見問題解決方案

---

## 🚀 Docker 部署方案

### 方案 1：服務帳號認證（推薦）

#### 準備工作
1. 按照 [服務帳號設定指南](service_account_setup.md) 設置服務帳號
2. 下載 `service_account.json` 到 `config/` 目錄
3. 複製並編輯配置檔案：
```bash
cp config/settings.yaml.template config/settings.yaml
```

#### 配置
編輯 `config/settings.yaml`：
```yaml
source:
  url: "your-ics-calendar-url"  # 填入您的 ICS URL

google_calendar:
  auth_type: "service_account"
  service_account_file: "config/service_account.json"
  calendar_id: "your-calendar-id@group.calendar.google.com"  # 填入您的 Calendar ID
  # Calendar ID 取得方式：
  # 1. 開啟 Google Calendar (calendar.google.com)
  # 2. 在左側找到目標行事曆，點擊三個點選單
  # 3. 選擇「設定和共用」
  # 4. 在「整合日曆」區塊中找到「日曆 ID」
```

#### 部署
```bash
# 修改 docker-compose.yml，啟用服務帳號掛載
# 註解掉 OAuth 相關的 volume
# 啟用 service_account.json volume

docker compose up -d
```

#### 優點
- ✅ 無需用戶互動
- ✅ 適合自動化部署
- ✅ 長期穩定運行
- ✅ 無 token 過期問題

---

### 方案 2：OAuth 預先授權

#### 準備工作
```bash
# 在本地完成授權
python setup.py
# 確保產生 config/token.json
```

#### 部署
```bash
# 使用預設的 docker-compose.yml
docker compose up -d
```

#### 維護
當 token 過期時：
```bash
# 停止服務
docker compose stop

# 重新授權
rm config/token.json
python setup.py

# 重啟服務
docker compose start
```

#### 優點
- ✅ 使用個人 Google 帳號
- ✅ 可存取個人預設行事曆

#### 缺點
- ❌ 需要定期手動重新授權
- ❌ token 過期時服務會停止

---

## 🔧 故障排除

### 常見問題

#### 1. 認證失敗
```bash
# 檢查認證狀態
docker compose exec calendarbridge python check_auth_status.py

# 查看日誌
docker compose logs calendarbridge
```

#### 2. Token 過期
```bash
# OAuth 方式：重新授權
docker compose stop
rm config/token.json
python setup.py
docker compose start

# 服務帳號方式：檢查金鑰檔案
ls -la config/service_account.json
```

#### 3. 行事曆權限問題
- 確保服務帳號已被分享目標行事曆
- 權限至少為 "Make changes and manage sharing"

### 監控

#### 健康檢查
```bash
# 檢查容器狀態
docker compose ps

# 檢查健康狀態
docker inspect calendarbridge | grep Health -A 10
```

#### 日誌監控
```bash
# 即時日誌
docker compose logs -f calendarbridge

# 查看最近日誌
docker compose logs --tail 100 calendarbridge
```

### 資料備份
```bash
# 備份資料庫
cp data/sync_state.db data/sync_state.db.backup

# 備份設定
tar -czf calendarbridge-backup.tar.gz config/ data/
```

---

## 🔄 更新部署

```bash
# 停止服務
docker compose stop

# 更新程式碼
git pull

# 重建映像
docker compose build

# 重啟服務
docker compose up -d

# 檢查狀態
docker compose logs -f calendarbridge
```

---

## 📊 效能調優

### 資源配置
修改 `docker-compose.yml` 中的資源限制：
```yaml
deploy:
  resources:
    limits:
      memory: 512M  # 增加記憶體
      cpus: '1.0'   # 增加 CPU
```

### 同步頻率
修改 `config/settings.yaml`：
```yaml
sync:
  interval_minutes: 15  # 減少同步間隔
```

### 日誌級別
```yaml
logging:
  level: "WARNING"  # 減少日誌輸出
```