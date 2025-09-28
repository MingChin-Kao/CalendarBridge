# CalendarBridge

一個精準的行事曆同步工具，將 ICS 行事曆自動同步到 Google Calendar。支援複雜的週期事件、Docker 部署和服務帳號認證。

## ✨ 功能特色

- 🔄 **精準同步**: 支援週期事件、時區轉換和事件變更偵測
- ⚡ **增量更新**: 只同步變更的事件，避免重複處理
- 🔁 **週期事件支援**: 完整處理 RRULE、UNTIL、EXDATE 等複雜週期規則
- 🔧 **智能處理**: 自動檢測並修復重複事件問題
- 📊 **狀態追蹤**: 本地資料庫記錄同步狀態和歷史
- 🐳 **Docker 支援**: 完整的容器化部署方案
- 🔐 **雙重認證**: 支援 OAuth 和服務帳號兩種認證方式

## 🚀 快速開始

### 基本設置

```bash
# 1. 克隆專案
git clone <repository-url>
cd CalendarBridge

# 2. 建立虛擬環境
python3 -m venv venv
source venv/bin/activate

# 3. 安裝依賴
pip install -r requirements.txt

# 4. 初始化設置
python setup.py
```

### 執行同步

```bash
# 測試模式（不實際執行）
python main.py --once --dry-run

# 執行一次同步
python main.py --once

# 持續同步模式
python main.py --continuous
```

## 📖 詳細文件

### 🔧 設置與配置
- **[Google Calendar API 設置](docs/google_api_setup.md)** - OAuth 和服務帳號設置指南
- **[配置檔案說明](docs/configuration.md)** - 詳細的設定選項說明

### 🐳 部署方案
- **[Docker 部署指南](docs/deployment_guide.md)** - 完整的 Docker 部署流程
- **[服務帳號設置](docs/service_account_setup.md)** - 生產環境推薦的認證方式
- **[OAuth Docker 設置](docs/docker_oauth_setup.md)** - 使用 OAuth 的 Docker 部署方式

### 🔧 維護與故障排除
- **[故障排除指南](docs/troubleshooting.md)** - 常見問題與解決方案
- **[API 參考](docs/api_reference.md)** - 程式模組與 API 說明

## 🏗️ 專案結構

```
CalendarBridge/
├── src/                  # 核心程式碼
│   ├── parsers/         # ICS 解析器
│   ├── clients/         # Google Calendar 客戶端
│   ├── sync/            # 同步引擎
│   ├── storage/         # 資料庫存取
│   └── utils/           # 工具函數
├── config/              # 配置檔案
├── docs/                # 詳細文件
├── data/                # 本地資料庫
├── logs/                # 日誌檔案
├── main.py              # 主程式入口
├── setup.py             # 初始化腳本
├── Dockerfile           # Docker 建置檔
├── docker-compose.yml   # Docker 編排檔
└── requirements.txt     # Python 依賴
```

## 🎯 使用情境

### 個人使用
```bash
# 簡單的 OAuth 認證
python setup.py
python main.py --continuous
```

### 生產環境
```bash
# 使用服務帳號認證 + Docker
docker-compose up -d
```

## 💡 核心技術

- **週期事件處理**: 完整支援 RFC 5545 RRULE 規範，包含 UNTIL 日期處理
- **智能變更偵測**: 基於 UID + SEQUENCE + 內容指紋的三方比對
- **時區精準處理**: 完整的 VTIMEZONE 解析和夏令時間轉換
- **孤兒事件清理**: 自動檢測和清理過期的週期事件實例

## 🔐 認證方式

| 方式 | 適用場景 | 優點 | 缺點 |
|------|----------|------|------|
| **OAuth** | 個人使用、測試 | 簡單設置、存取個人行事曆 | 需定期重新授權 |
| **服務帳號** | 生產環境、自動化 | 長期穩定、Docker 友善 | 需要分享行事曆權限 |

## 📊 監控與維護

```bash
# 檢查同步狀態
python show_sync_state.py

# 查看 Google Calendar 清單
python get_calendar_list.py

# 清理資料庫
python clean_database.py
```

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！請參考 [貢獻指南](docs/contributing.md)。

## 📄 授權

MIT License - 詳見 [LICENSE](LICENSE) 檔案。

---

## 🔗 快速連結

- [📖 完整文件](docs/)
- [🐳 Docker 部署](docs/deployment_guide.md)
- [🔧 故障排除](docs/troubleshooting.md)
- [⚙️ API 參考](docs/api_reference.md)