# 配置檔案說明

本文件詳細說明 `config/settings.yaml` 中的所有配置選項。

## 📁 配置檔案結構

```yaml
# ICS 資料來源設定
source:
  url: "your-ics-url"
  timeout: 30
  retry_count: 3
  user_agent: "CalendarBridge/1.0"

# Google Calendar 設定
google_calendar:
  auth_type: "oauth"  # 或 "service_account"
  calendar_id: "primary"
  credentials_file: "config/credentials.json"
  token_file: "config/token.json"
  service_account_file: "config/service_account.json"
  application_name: "CalendarBridge"

# 同步設定
sync:
  interval_minutes: 30
  max_events_per_batch: 100
  lookahead_days: 365
  lookbehind_days: 30
  enable_delete: true
  conflict_resolution: "latest"

# 事件處理設定
processing:
  timezone: "Asia/Taipei"
  event_prefix: ""
  description_suffix: "\n\n--- 由 CalendarBridge 同步 ---"

# 資料庫設定
database:
  path: "data/sync_state.db"
  backup_count: 5

# 日誌設定
logging:
  level: "INFO"
  file: "logs/calendarbridge.log"
  max_size_mb: 10
  backup_count: 5
  console: true
```

## 🔧 詳細說明

### Source（資料來源）

| 參數 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `url` | string | - | **必填**。ICS 檔案的 URL |
| `timeout` | int | 30 | HTTP 請求超時時間（秒） |
| `retry_count` | int | 3 | 失敗重試次數 |
| `user_agent` | string | "CalendarBridge/1.0" | HTTP User-Agent 標頭 |

**範例：**
```yaml
source:
  url: "https://example.com/calendar.ics"
  timeout: 60  # 對於慢速連線增加超時時間
  retry_count: 5  # 增加重試次數
```

### Google Calendar

| 參數 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `auth_type` | string | "oauth" | 認證類型：`"oauth"` 或 `"service_account"` |
| `calendar_id` | string | "primary" | 目標行事曆 ID，`"primary"` 為主要行事曆 |
| `credentials_file` | string | "config/credentials.json" | OAuth 認證檔案路徑 |
| `token_file` | string | "config/token.json" | OAuth token 存放路徑 |
| `service_account_file` | string | "config/service_account.json" | 服務帳號金鑰檔案路徑 |
| `application_name` | string | "CalendarBridge" | 應用程式名稱 |

**OAuth 設定範例：**
```yaml
google_calendar:
  auth_type: "oauth"
  calendar_id: "primary"
  credentials_file: "config/credentials.json"
  token_file: "config/token.json"
```

**服務帳號設定範例：**
```yaml
google_calendar:
  auth_type: "service_account"
  calendar_id: "abc123@group.calendar.google.com"
  service_account_file: "config/service_account.json"
```

### Sync（同步設定）

| 參數 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `interval_minutes` | int | 30 | 持續模式下的同步間隔（分鐘） |
| `max_events_per_batch` | int | 100 | 每批次處理的最大事件數 |
| `lookahead_days` | int | 365 | 向前同步天數 |
| `lookbehind_days` | int | 30 | 向後同步天數 |
| `enable_delete` | bool | true | 是否刪除來源中已移除的事件 |
| `conflict_resolution` | string | "latest" | 衝突解決策略 |

**效能調整範例：**
```yaml
sync:
  interval_minutes: 15  # 更頻繁的同步
  max_events_per_batch: 50  # 減少批次大小以避免 API 限制
  lookahead_days: 180  # 減少範圍以提高效能
  lookbehind_days: 7   # 減少向後查找範圍
```

**安全模式範例：**
```yaml
sync:
  enable_delete: false  # 不刪除事件，只新增和更新
  conflict_resolution: "keep_existing"  # 保持現有事件
```

### Processing（事件處理）

| 參數 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `timezone` | string | "Asia/Taipei" | 預設時區 |
| `event_prefix` | string | "" | 事件標題前綴 |
| `description_suffix` | string | "" | 事件描述後綴 |

**自訂處理範例：**
```yaml
processing:
  timezone: "UTC"  # 使用 UTC 時區
  event_prefix: "[公司] "  # 自訂前綴
  description_suffix: "\n\n📅 此事件由自動同步系統建立"
```

### Database（資料庫設定）

| 參數 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `path` | string | "data/sync_state.db" | SQLite 資料庫檔案路徑 |
| `backup_count` | int | 5 | 保留的備份數量 |

### Logging（日誌設定）

| 參數 | 類型 | 預設值 | 說明 |
|------|------|--------|------|
| `level` | string | "INFO" | 日誌級別：`DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `file` | string | "logs/calendarbridge.log" | 日誌檔案路徑 |
| `max_size_mb` | int | 10 | 單個日誌檔案最大大小（MB） |
| `backup_count` | int | 5 | 保留的日誌檔案數量 |
| `console` | bool | true | 是否同時輸出到控制台 |

**調試模式範例：**
```yaml
logging:
  level: "DEBUG"  # 詳細日誌
  console: true
  max_size_mb: 50  # 增加檔案大小限制
```

**生產模式範例：**
```yaml
logging:
  level: "WARNING"  # 只記錄警告和錯誤
  console: false    # 不輸出到控制台
  max_size_mb: 5    # 較小的檔案大小
```

## 🌍 環境變數支援

配置可以通過環境變數覆蓋：

```bash
# 設定 ICS URL
export CALENDAR_SYNC_SOURCE_URL="https://example.com/calendar.ics"

# 設定 Google Calendar ID
export CALENDAR_SYNC_GOOGLE_CALENDAR_ID="abc123@group.calendar.google.com"

# 設定認證類型
export CALENDAR_SYNC_GOOGLE_AUTH_TYPE="service_account"

# 設定同步間隔
export CALENDAR_SYNC_SYNC_INTERVAL_MINUTES="15"
```

環境變數命名規則：`CALENDAR_SYNC_` + `區塊名稱_` + `參數名稱`（全大寫，用底線分隔）

## 📝 配置範本

### 基本個人使用
```yaml
source:
  url: "your-ics-url-here"

google_calendar:
  auth_type: "oauth"
  calendar_id: "primary"

sync:
  interval_minutes: 30
  enable_delete: true

processing:
  timezone: "Asia/Taipei"
  event_prefix: "[同步] "

logging:
  level: "INFO"
  console: true
```

### 生產環境
```yaml
source:
  url: "${ICS_URL}"
  timeout: 60
  retry_count: 5

google_calendar:
  auth_type: "service_account"
  calendar_id: "${CALENDAR_ID}"
  service_account_file: "config/service_account.json"

sync:
  interval_minutes: 15
  max_events_per_batch: 50
  enable_delete: true

processing:
  timezone: "Asia/Taipei"
  event_prefix: ""

database:
  path: "/app/data/sync_state.db"

logging:
  level: "WARNING"
  file: "/app/logs/calendarbridge.log"
  console: false
```

### 測試環境
```yaml
source:
  url: "your-test-ics-url"

google_calendar:
  auth_type: "oauth"
  calendar_id: "test-calendar-id"

sync:
  interval_minutes: 60
  lookahead_days: 30
  lookbehind_days: 7
  enable_delete: false  # 測試時不刪除

processing:
  timezone: "Asia/Taipei"
  event_prefix: "[測試] "

logging:
  level: "DEBUG"
  console: true
```

## 🔍 驗證配置

使用內建工具驗證配置：

```bash
# 驗證配置檔案語法
python -c "from src.utils.config import load_config; print('配置有效!' if load_config('config/settings.yaml') else '配置無效')"

# 測試 Google Calendar 連線
python -c "
from src.clients.google_calendar import GoogleCalendarClient
from src.utils.config import load_config
config = load_config('config/settings.yaml')
client = GoogleCalendarClient(config.google_calendar)
client.authenticate()
print('Google Calendar 連線成功!')
"

# 測試 ICS 來源
python -c "
from src.parsers.ics_parser import ICSParser
from src.utils.config import load_config
config = load_config('config/settings.yaml')
parser = ICSParser(config.source, config.processing)
content = parser.fetch_ics_content()
print(f'成功獲取 ICS 內容，大小: {len(content)} bytes')
"
```