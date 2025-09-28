# 故障排除指南

本指南涵蓋常見問題的診斷和解決方法。

## 🚨 常見問題

### 1. 認證相關問題

#### OAuth 認證失敗
```
錯誤: invalid_grant
```

**原因**: Refresh token 已過期或失效

**解決方法**:
```bash
# 刪除舊的 token 並重新授權
rm config/token.json
python setup.py
```

#### 服務帳號認證失敗
```
錯誤: Service account file not found
```

**解決方法**:
```bash
# 檢查檔案是否存在
ls -la config/service_account.json

# 如果不存在，請重新下載服務帳號金鑰
# 並放置到 config/service_account.json
```

#### Calendar not found
```
錯誤: Calendar not found or access denied
```

**原因**: 
- 行事曆 ID 錯誤
- 服務帳號沒有行事曆存取權限

**解決方法**:
```bash
# 列出可用的行事曆
python get_calendar_list.py

# 確認服務帳號已被分享目標行事曆
# 權限至少為 "Make changes and manage sharing"
```

### 2. 同步相關問題

#### 重複事件問題
```
症狀: 同一個事件在 Google Calendar 中出現多次
```

**診斷**:
```bash
# 檢查資料庫狀態
python show_sync_state.py

# 檢查是否有孤兒記錄
python -c "
from src.storage.database import SyncDatabase
from src.utils.config import load_config
config = load_config('config/settings.yaml')
db = SyncDatabase(config.database)
with db._get_connection() as conn:
    cursor = conn.execute('SELECT COUNT(*) FROM event_mappings')
    mappings = cursor.fetchone()[0]
    cursor = conn.execute('SELECT COUNT(*) FROM event_snapshots')
    snapshots = cursor.fetchone()[0]
    print(f'映射: {mappings}, 快照: {snapshots}')
    if mappings != snapshots:
        print('⚠️ 資料不一致，建議清理資料庫')
"
```

**解決方法**:
```bash
# 清理資料庫並重新同步
python clean_database.py
python main.py --once --force
```

#### 週期事件不結束問題
```
症狀: 週期事件在 ICS 中已結束，但 Google Calendar 中仍繼續
```

**診斷**:
查看 ICS 中的 RRULE 是否包含 UNTIL 或 COUNT：
```bash
python -c "
from src.parsers.ics_parser import ICSParser
from src.utils.config import load_config
config = load_config('config/settings.yaml')
parser = ICSParser(config.source, config.processing)
ics_content = parser.fetch_ics_content()
events, _ = parser.parse_ics_content(ics_content)
for event in events:
    if event.is_recurring():
        print(f'{event.summary}: {event.rrule}')
"
```

**解決方法**: 系統現已自動處理 UNTIL 日期，重新同步即可。

### 3. 效能相關問題

#### 同步速度慢
```
症狀: 同步過程耗時過長
```

**優化設定**:
```yaml
sync:
  max_events_per_batch: 50  # 減少批次大小
  lookahead_days: 180       # 減少範圍
  interval_minutes: 60      # 降低同步頻率

logging:
  level: "WARNING"          # 減少日誌輸出
```

#### 記憶體使用過高
```
症狀: 程式佔用大量記憶體
```

**解決方法**:
```yaml
# 減少同步範圍
sync:
  lookahead_days: 90
  lookbehind_days: 7
  max_events_per_batch: 25

# 清理舊資料
database:
  backup_count: 2
```

### 4. ICS 解析問題

#### 時區解析錯誤
```
錯誤: 'datetime.date' object has no attribute 'tzinfo'
```

**說明**: 某些 ICS 事件的時間格式有問題，但不影響整體同步。

**檢查**:
```bash
# 查看哪些事件解析失敗
grep "Failed to parse event" logs/calendarbridge.log
```

#### RRULE 轉換失敗
```
錯誤: Failed to convert RRULE
```

**解決方法**: 系統會自動跳過無法轉換的週期規則，將事件作為單次事件處理。

### 5. 網路相關問題

#### ICS 下載超時
```
錯誤: Request timeout
```

**解決方法**:
```yaml
source:
  timeout: 120     # 增加超時時間
  retry_count: 5   # 增加重試次數
```

#### SSL 憑證問題
```
錯誤: SSL certificate verification failed
```

**解決方法**:
```bash
# 檢查 ICS URL 的 SSL 憑證
curl -I "your-ics-url"

# 如果是內部系統的自簽憑證，可以在程式中添加例外處理
```

## 🔍 診斷工具

### 檢查工具腳本

```bash
# 檢查同步狀態
python show_sync_state.py

# 檢查 Google Calendar 清單
python get_calendar_list.py

# 測試 ICS 解析
python -c "
from src.parsers.ics_parser import ICSParser
from src.utils.config import load_config
config = load_config('config/settings.yaml')
parser = ICSParser(config.source, config.processing)
print('正在測試 ICS 解析...')
try:
    content = parser.fetch_ics_content()
    events, modified = parser.parse_ics_content(content)
    print(f'✅ 成功解析 {len(events)} 個主事件和 {len(modified)} 個修改實例')
except Exception as e:
    print(f'❌ 解析失敗: {e}')
"
```

### 日誌分析

```bash
# 查看最近的錯誤
tail -n 100 logs/calendarbridge.log | grep ERROR

# 統計事件處理情況
grep "Sync completed successfully" logs/calendarbridge.log | tail -5

# 查看認證相關日誌
grep -E "(authentication|OAuth|refresh)" logs/calendarbridge.log | tail -10

# 檢查週期事件處理
grep -E "(recurring|RRULE|UNTIL)" logs/calendarbridge.log | tail -10
```

### 資料庫檢查

```bash
# 檢查資料庫統計
python -c "
from src.storage.database import SyncDatabase
from src.utils.config import load_config
config = load_config('config/settings.yaml')
db = SyncDatabase(config.database)
stats = db.get_database_stats()
for key, value in stats.items():
    print(f'{key}: {value}')
"

# 檢查最近的同步歷史
python -c "
from src.storage.database import SyncDatabase
from src.utils.config import load_config
config = load_config('config/settings.yaml')
db = SyncDatabase(config.database)
history = db.get_sync_history(5)
for record in history:
    print(f'{record[\"sync_started_at\"]} - {record[\"status\"]} - {record[\"events_processed\"]} events')
"
```

## 🔧 維護操作

### 清理操作

```bash
# 完全重置資料庫
python clean_database.py

# 重新完整同步
python main.py --once --force

# 清理過期的日誌檔案
find logs/ -name "*.log.*" -mtime +30 -delete
```

### 備份操作

```bash
# 備份資料庫
cp data/sync_state.db data/sync_state.db.$(date +%Y%m%d_%H%M%S)

# 備份配置
tar -czf config_backup_$(date +%Y%m%d).tar.gz config/

# 備份日誌
tar -czf logs_backup_$(date +%Y%m%d).tar.gz logs/
```

### 升級操作

```bash
# 停止同步服務
# 如果是 systemd 服務: sudo systemctl stop calendarbridge
# 如果是 Docker: docker-compose stop

# 備份當前版本
cp -r /path/to/calendar /path/to/calendar.backup

# 更新程式碼
git pull

# 重新安裝依賴（如果 requirements.txt 有變更）
pip install -r requirements.txt

# 重啟服務
# systemd: sudo systemctl start calendarbridge
# Docker: docker-compose up -d
```

## 🚨 緊急處理

### 服務停止運作

1. **檢查程序狀態**
```bash
ps aux | grep calendar
```

2. **檢查最近日誌**
```bash
tail -50 logs/calendarbridge.log
```

3. **測試基本功能**
```bash
python main.py --once --dry-run
```

### 大量重複事件

1. **停止同步**
2. **清理資料庫**
```bash
python clean_database.py
```
3. **手動清理 Google Calendar 中的重複事件**
4. **重新執行同步**
```bash
python main.py --once --force
```

### token 過期在生產環境

#### OAuth 方式
```bash
# 臨時解決：在有 GUI 的機器上重新授權
python setup.py
# 然後將 config/token.json 複製到生產環境
```

#### 建議：切換到服務帳號
請參考 [服務帳號設置指南](service_account_setup.md)

## 📞 獲得幫助

1. **查看日誌檔案**: `logs/calendarbridge.log`
2. **檢查 GitHub Issues**: 搜尋類似問題
3. **建立新 Issue**: 包含錯誤日誌和配置資訊（移除敏感資料）

### 回報問題時請提供

- 錯誤訊息和完整的 stack trace
- 相關的日誌片段
- 配置檔案內容（移除敏感資訊）
- 作業系統和 Python 版本
- 問題重現步驟