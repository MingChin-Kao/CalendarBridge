# Calendar Sync Tool

一個精準的行事曆同步工具，將公司 ICS 行事曆同步到 Google Calendar。

## 功能特色

- ✅ **精準同步**: 支援週期事件、時區轉換和事件變更偵測
- ✅ **增量更新**: 只同步變更的事件，避免重複處理
- ✅ **週期事件支援**: 完整處理 RRULE、EXDATE 等複雜週期規則
- ✅ **衝突解決**: 智能處理事件衝突和重複
- ✅ **狀態追蹤**: 本地資料庫記錄同步狀態和歷史
- ✅ **錯誤處理**: 完整的重試機制和錯誤記錄

## 快速開始

### 1. 安裝依賴

```bash
# 建立虛擬環境
python3 -m venv venv
source venv/bin/activate

# 安裝套件
pip install -r requirements.txt
```

### 2. 設置 Google Calendar API

#### 步驟 1: 建立 Google Cloud 專案

1. 前往 [Google Cloud Console](https://console.cloud.google.com/)
2. 建立新專案或選擇現有專案
3. 啟用 Google Calendar API:
   - 在側邊欄選擇 "APIs & Services" > "Library"
   - 搜尋 "Google Calendar API"
   - 點擊啟用

#### 步驟 2: 建立認證

1. 在 Google Cloud Console 中，前往 "APIs & Services" > "Credentials"
2. 點擊 "Create Credentials" > "OAuth 2.0 Client IDs"
3. 選擇 "Desktop application"
4. 輸入名稱 (例如: "Calendar Sync Tool")
5. 下載 JSON 認證檔案

#### 步驟 3: 設置認證檔案

```bash
# 將下載的認證檔案移到專案目錄
cp ~/Downloads/credentials.json config/credentials.json
```

### 3. 設定檔案

編輯 `config/settings.yaml`，確認以下設定：

```yaml
source:
  url: "你的_ICS_URL"

google_calendar:
  calendar_id: "primary"  # 或指定特定行事曆 ID
  credentials_file: "config/credentials.json"
```

### 4. 執行同步

```bash
# 測試基本功能
python test_basic.py

# 執行一次性同步 (乾跑模式)
python main.py --once --dry-run

# 執行一次性同步
python main.py --once

# 啟動持續同步
python main.py
```

## 使用說明

### 命令行選項

```bash
python main.py [選項]

選項:
  --config, -c     設定檔案路徑 (預設: config/settings.yaml)
  --once          執行一次同步後退出
  --force         強制完整同步 (忽略快取)
  --dry-run       顯示將要同步的內容但不實際執行
```

### 設定說明

主要設定檔案 `config/settings.yaml`:

```yaml
# 來源 ICS 設定
source:
  url: "你的_ICS_URL"
  timeout: 30
  retry_count: 3

# Google Calendar 設定
google_calendar:
  calendar_id: "primary"  # 或特定行事曆 ID
  credentials_file: "config/credentials.json"

# 同步設定
sync:
  interval_minutes: 30    # 同步間隔
  lookahead_days: 365     # 向前同步天數
  lookbehind_days: 30     # 向後同步天數
  enable_delete: true     # 是否刪除來源已移除的事件

# 事件處理
processing:
  timezone: "Asia/Taipei"
  event_prefix: "[ITRI] "  # 事件標題前綴
  description_suffix: "\\n\\n--- 由 Calendar Sync 工具同步 ---"
```

## 專案結構

```
calendar-sync/
├── venv/                 # 虛擬環境
├── src/
│   ├── parsers/         # ICS 解析器
│   │   └── ics_parser.py
│   ├── clients/         # Google API 客戶端
│   │   └── google_calendar.py
│   ├── sync/            # 同步引擎
│   │   └── engine.py
│   ├── storage/         # 狀態管理
│   │   └── database.py
│   └── utils/           # 工具函數
│       ├── config.py
│       └── logger.py
├── config/
│   ├── settings.yaml    # 主要配置
│   └── credentials.json # Google API 認證 (需要自行建立)
├── data/                # 本地資料庫
├── logs/                # 日誌檔案
├── main.py              # 主程式
├── test_basic.py        # 基本測試
└── requirements.txt     # 套件依賴
```

## 技術特色

### 精準週期事件處理

- 完整支援 RFC 5545 RRULE 規範
- 處理 EXDATE (排除日期) 和修改實例
- 正確展開複雜的週期規則

### 智能變更偵測

- 基於 UID + SEQUENCE + 內容指紋
- 增量同步，避免重複處理
- 三方比對 (源檔案 vs 本地快照 vs Google Calendar)

### 時區精準處理

- 完整的 VTIMEZONE 解析
- 自動處理夏令時間轉換
- 跨時區事件正確同步

### 狀態管理

- SQLite 本地資料庫
- 完整的同步歷史記錄
- 事件映射關係追蹤

## 故障排除

### 常見問題

1. **認證失敗**
   - 確認 `config/credentials.json` 檔案存在且正確
   - 檢查 Google Calendar API 是否已啟用

2. **ICS 獲取失敗**
   - 確認 ICS URL 可以正常存取
   - 檢查網路連線和防火牆設定

3. **事件解析錯誤**
   - 檢查日誌檔案 `logs/calendar_sync.log`
   - 某些格式錯誤的事件會被跳過但不影響整體同步

### 日誌查看

```bash
# 查看最新日誌
tail -f logs/calendar_sync.log

# 查看錯誤日誌
grep ERROR logs/calendar_sync.log
```

## 安全性

- Google API 認證資訊安全存儲
- 僅請求必要的 Calendar API 權限
- 本地資料庫僅存儲同步狀態，不含敏感資訊

## 授權

MIT License