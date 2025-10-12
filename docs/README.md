# CalendarBridge 文件

歡迎使用 CalendarBridge！本文件將幫助您快速上手並深入了解系統功能。

## 🚀 快速開始

如果您是第一次使用，建議從這裡開始：
- [快速開始指南](quickstart.md) - 5 分鐘快速設置並運行

## 📚 文件導覽

### 認證設置
選擇適合您的認證方式並完成設置：

1. **[認證方式概覽](authentication/overview.md)** - 開始之前必讀
   - Google Cloud 專案設置
   - OAuth vs 服務帳號比較
   - 選擇適合您的認證方式

2. **[OAuth 認證](authentication/oauth.md)** - 適合個人開發和測試
   - 完整的 OAuth 設置步驟
   - 適合本地開發環境

3. **[服務帳號認證](authentication/service_account.md)** - 適合生產環境
   - 服務帳號創建與配置
   - 適合 Docker 和自動化部署

### 部署指南
根據您的使用場景選擇部署方式：

- **[本地部署](deployment/local.md)** - 在本機運行
- **[Docker 部署](deployment/docker.md)** - 使用 Docker 容器運行

### 參考資料
深入了解配置和疑難排解：

- **[配置說明](reference/configuration.md)** - 完整的配置選項說明
- **[疑難排解](reference/troubleshooting.md)** - 常見問題與解決方案

## 🎯 常見使用場景

### 我想在本機測試
1. 閱讀 [快速開始指南](quickstart.md)
2. 設置 [OAuth 認證](authentication/oauth.md)
3. 參考 [本地部署](deployment/local.md)

### 我想部署到生產環境
1. 閱讀 [認證方式概覽](authentication/overview.md)
2. 設置 [服務帳號認證](authentication/service_account.md)
3. 參考 [Docker 部署](deployment/docker.md)

### 我遇到問題了
1. 查看 [疑難排解](reference/troubleshooting.md)
2. 檢查 [配置說明](reference/configuration.md)

## 💡 需要幫助？

如果您在文件中找不到答案，可以：
- 查看 [GitHub Issues](https://github.com/yourusername/CalendarBridge/issues)
- 提交新的 Issue

## 📝 文件結構

```
docs/
├── README.md                      # 📖 本文件（導覽頁）
├── quickstart.md                  # 🚀 快速開始
├── authentication/                # 🔐 認證相關
│   ├── overview.md               # 認證概覽與選擇
│   ├── oauth.md                  # OAuth 設置
│   └── service_account.md        # 服務帳號設置
├── deployment/                    # 🚀 部署相關
│   ├── local.md                  # 本地部署
│   └── docker.md                 # Docker 部署
└── reference/                     # 📚 參考資料
    ├── configuration.md          # 配置說明
    └── troubleshooting.md        # 疑難排解
```
