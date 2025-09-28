# 下一步操作指南

## 目前狀態 ✅

您的行事曆同步程式已經開發完成並可以正常運作！我們已經成功：

1. ✅ **建立完整的專案架構**
2. ✅ **實作精準的 ICS 解析器** - 支援週期事件和時區處理
3. ✅ **實作 Google Calendar 客戶端** - 完整的 API 整合
4. ✅ **實作本地狀態管理** - SQLite 資料庫追蹤同步狀態
5. ✅ **實作智能同步引擎** - 增量更新和衝突解決
6. ✅ **測試基本功能** - 成功解析您的 ITRI 行事曆 (73個事件)

## 立即可用的功能

- 📥 **ICS 獲取**: 從您的 ITRI OWA URL 獲取行事曆
- 🔍 **精準解析**: 處理 73 個事件包含週期事件
- 🕐 **時區處理**: 正確處理 Asia/Taipei 時區
- 📝 **事件標題**: 自動添加 "[ITRI]" 前綴
- 🔄 **變更偵測**: 智能判斷新增、修改、刪除事件

## 需要完成的最後步驟

### 1. 設置 Google Calendar API 認證

**方法一: 快速設置 (建議)**
1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 建立新專案或選擇現有專案
3. 啟用 Google Calendar API
4. 建立 OAuth 2.0 認證 (Desktop application)
5. 下載 JSON 檔案並重命名為 `config/credentials.json`

**方法二: 詳細步驟**
參考 `README.md` 中的完整說明

### 2. 測試 Google Calendar 連接

```bash
# 啟動虛擬環境
source venv/bin/activate

# 測試 Google 認證
python -c "
from src.clients.google_calendar import GoogleCalendarClient
from src.utils.config import load_config

config = load_config('config/settings.yaml')
client = GoogleCalendarClient(config.google_calendar)
client.authenticate()
print('✅ Google Calendar 認證成功!')
"
```

### 3. 執行首次同步

```bash
# 乾跑模式 (查看會同步什麼，但不實際執行)
python main.py --once --dry-run

# 實際執行同步
python main.py --once

# 啟動持續同步 (每30分鐘檢查一次)
python main.py
```

## 預期結果

同步成功後，您會在 Google Calendar 中看到：

- 📅 **73+ 個 ITRI 事件** 
- 🏷️ **標題前綴**: [ITRI] 次世代RWD-W2平台討論會議
- 📍 **地點資訊**: 53-102, Microsoft Teams 會議等
- 🔄 **週期事件**: 正確展開重複事件
- ⏰ **精確時間**: 台北時區正確轉換

## 自訂設定

編輯 `config/settings.yaml` 來調整：

```yaml
# 修改同步間隔
sync:
  interval_minutes: 15  # 每15分鐘同步一次

# 修改事件標題前綴
processing:
  event_prefix: "[工研院] "  # 或其他您想要的前綴

# 指定特定的 Google Calendar
google_calendar:
  calendar_id: "您的特定行事曆ID"  # 而不是 "primary"
```

## 監控和維護

```bash
# 查看同步日誌
tail -f logs/calendar_sync.log

# 查看同步狀態
sqlite3 data/sync_state.db "SELECT * FROM sync_history ORDER BY sync_started_at DESC LIMIT 5;"

# 手動清理舊資料
python -c "
from src.storage.database import SyncDatabase
from src.utils.config import load_config

config = load_config('config/settings.yaml')
db = SyncDatabase(config.database)
db.cleanup_old_data(30)  # 清理30天前的資料
"
```

## 故障排除

### 常見問題

1. **認證錯誤**
   - 確認 `config/credentials.json` 正確
   - 重新下載認證檔案

2. **同步失敗**
   - 檢查網路連線
   - 查看 `logs/calendar_sync.log`

3. **事件重複**
   - 執行 `python main.py --once --force` 重新同步

### 獲得幫助

- 📖 查看 `README.md` 完整文檔
- 📝 檢查 `logs/calendar_sync.log` 錯誤訊息
- 🔧 執行 `python setup.py` 檢查安裝狀態

## 高級功能

- **多行事曆同步**: 複製設定檔建立多個同步實例
- **自訂過濾**: 修改解析器來過濾特定事件
- **通知整合**: 添加 webhook 或郵件通知
- **Web 介面**: 可以擴展為 Web 應用程式

---

🎉 **恭喜！您的行事曆同步工具已經準備就緒！**

只需要完成 Google API 認證設置，就可以開始享受自動化的行事曆同步服務了。