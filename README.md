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

### 推薦部署方式

我們推薦使用 **Docker + 服務帳號** 方案，這是最穩定、維護成本最低的部署方式。

```bash
# 1. 克隆專案
git clone https://github.com/MingChin-Kao/CalendarBridge.git
cd CalendarBridge

# 2. 按照快速開始指南完成設置
# 詳見: docs/quickstart.md

# 3. 啟動服務
docker compose up -d
```

**時間**: 約 10-15 分鐘
**難度**: ⭐⭐☆☆☆

### 🎯 完整設置指南

📖 **請查看 [快速開始指南](docs/quickstart.md)**，包含：

- ✅ Docker + 服務帳號設置（推薦）
- ✅ Google Cloud 專案建立
- ✅ 服務帳號配置
- ✅ 行事曆分享設置
- ✅ 常見問題排解

### 其他部署方式

| 部署方式 | 適用場景 | 推薦程度 | 文件連結 |
|---------|----------|----------|---------|
| **🐳 Docker + 服務帳號** | 生產環境、自動化部署 | ⭐⭐⭐⭐⭐ | [快速開始](docs/quickstart.md) |
| **🔧 本地 + OAuth** | 個人開發、測試 | ⭐⭐⭐ | [本地部署](docs/deployment/local.md) |

## 📖 文件導覽

### 快速導覽
- **[🚀 快速開始指南](docs/quickstart.md)** - 10 分鐘快速部署（從這裡開始！）
- **[📚 文件目錄](docs/README.md)** - 完整文件導覽

### 認證設置
- **[認證方式概覽](docs/authentication/overview.md)** - Google Cloud 設置與認證方式比較
- **[服務帳號設置](docs/authentication/service_account.md)** - 生產環境推薦 ⭐
- **[OAuth 認證設置](docs/authentication/oauth.md)** - 個人開發使用

### 部署方案
- **[本地部署指南](docs/deployment/local.md)** - 在本機運行
- **[Docker 部署指南](docs/deployment/docker.md)** - 容器化部署 ⭐

### 參考資料
- **[配置檔案說明](docs/reference/configuration.md)** - 詳細的設定選項說明
- **[疑難排解指南](docs/reference/troubleshooting.md)** - 常見問題與解決方案

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

## 💡 核心技術

- **週期事件處理**: 完整支援 RFC 5545 RRULE 規範，包含 UNTIL 日期處理
- **智能變更偵測**: 基於 UID + SEQUENCE + 內容指紋的三方比對
- **時區精準處理**: 完整的 VTIMEZONE 解析和夏令時間轉換
- **孤兒事件清理**: 自動檢測和清理過期的週期事件實例

## 🔐 認證方式比較

| 方式 | 適用場景 | 優點 | 缺點 |
|------|----------|------|------|
| **服務帳號** | 生產環境、自動化 | 長期穩定、Docker 友善、無需人工介入 | 需要分享行事曆權限 |
| **OAuth** | 個人使用、測試 | 簡單設置、存取個人行事曆 | 需定期重新授權 |

> 💡 **推薦**：生產環境請使用服務帳號認證

## 📊 監控與維護

```bash
# 檢查同步狀態
docker compose exec calendarbridge python show_sync_state.py

# 查看日誌
docker compose logs -f

# 重啟服務
docker compose restart
```

更多維護命令請參考：[Docker 部署指南](docs/deployment/docker.md)

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

## 📄 授權

MIT License - 詳見 [LICENSE](LICENSE) 檔案。

---

## 需要幫助？

- 📖 查看 [快速開始指南](docs/quickstart.md)
- 📚 瀏覽 [完整文件](docs/README.md)
- 🔧 參考 [疑難排解](docs/reference/troubleshooting.md)
- 💬 提交 [GitHub Issue](https://github.com/MingChin-Kao/CalendarBridge/issues)
