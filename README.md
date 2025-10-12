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

### 📋 開始前準備

在開始使用 CalendarBridge 之前，請先選擇適合的部署方式：

| 部署方式 | 適用場景 | 推薦程度 |
|---------|----------|----------|
| **🐳 Docker + 服務帳號** | 生產環境、自動化部署 | ⭐⭐⭐⭐⭐ |
| **🔧 本地 + OAuth** | 個人開發、測試 | ⭐⭐⭐ |

---

### 🏆 方案一：Docker 部署（推薦）

**適合**：生產環境、長期穩定運行、自動化部署

```bash
# 1. 克隆專案
git clone <repository-url>
cd CalendarBridge

# 2. 設置認證（詳見下方連結）
# - 完成 Google Cloud 專案設置
# - 設置服務帳號認證
# - 分享目標行事曆給服務帳號

# 3. 配置應用程式
cp config/settings.yaml.template config/settings.yaml
# 編輯 config/settings.yaml，填入 ICS URL 和 Calendar ID

# 4. 啟動服務
docker compose up -d
```

**🔗 完整設置指南**：
1. [認證方式概覽](docs/authentication/overview.md)
2. [服務帳號認證設置](docs/authentication/service_account.md)
3. [Docker 部署指南](docs/deployment/docker.md)

---

### 🔧 方案二：本地開發

**適合**：個人測試、開發環境、快速驗證

```bash
# 1. 克隆專案並設置環境
git clone <repository-url>
cd CalendarBridge
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. 配置檔案
cp config/settings.yaml.template config/settings.yaml
# 編輯 config/settings.yaml，填入 ICS URL

# 3. 設置 OAuth 認證
python setup.py

# 4. 執行同步
python main.py --once --dry-run  # 測試模式
python main.py --once            # 執行一次
python main.py                   # 持續同步
```

**🔗 設置指南**：
- [OAuth 認證設置](docs/authentication/oauth.md)

## 📖 詳細文件

### 🚀 快速開始
- **[文件導覽](docs/README.md)** - 從這裡開始，找到您需要的文件
- **[快速開始指南](docs/quickstart.md)** - 5 分鐘快速上手

### 🔐 認證設置
- **[認證方式概覽](docs/authentication/overview.md)** - Google Cloud 設置與認證方式比較
- **[服務帳號設置](docs/authentication/service_account.md)** - 生產環境推薦 ⭐
- **[OAuth 認證設置](docs/authentication/oauth.md)** - 個人開發使用

### 🐳 部署方案
- **[本地部署指南](docs/deployment/local.md)** - 在本機運行
- **[Docker 部署指南](docs/deployment/docker.md)** - 容器化部署 ⭐

### ⚙️ 參考資料
- **[配置檔案說明](docs/reference/configuration.md)** - 詳細的設定選項說明
- **[疑難排解指南](docs/reference/troubleshooting.md)** - 常見問題與解決方案

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

### 🏢 生產環境（推薦）
```bash
# 使用服務帳號認證 + Docker
docker compose up -d
```
- ✅ 長期穩定運行
- ✅ 無需定期重新授權
- ✅ 完全自動化

### 👨‍💻 個人開發
```bash
# OAuth 認證 + 本地運行
python setup.py
python main.py
```
- ✅ 快速設置
- ✅ 存取個人所有行事曆
- ⚠️ 需定期重新授權

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

### 📚 文檔導航
- [📖 文件導覽](docs/README.md) - 完整文件目錄
- [🚀 快速開始](docs/quickstart.md) - 5 分鐘上手指南
- [🔐 認證概覽](docs/authentication/overview.md) - 選擇認證方式
- [🐳 Docker 部署](docs/deployment/docker.md) - 生產環境部署

### 🛠️ 工具與維護
- [🔧 疑難排解](docs/reference/troubleshooting.md)
- [📝 配置說明](docs/reference/configuration.md)