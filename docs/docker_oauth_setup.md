# Docker 環境中的 OAuth 設置指南

本指南說明如何在 Docker 環境中使用 OAuth 認證。

> 📝 **建議**：對於 Docker 部署，我們強烈建議使用 [服務帳號認證](service_account_setup.md)，因為它更適合自動化環境。

## 📋 前置需求

在開始之前，請確保已完成：
- [Google Cloud 專案設置](google_cloud_setup.md)
- [OAuth 認證設置](google_api_setup.md#oauth-認證詳細步驟)

## 方案：預先授權 + Docker 持久化存儲

### 步驟 1: 本地完成 OAuth 授權

在 Docker 部署之前，必須先在本地環境完成 OAuth 授權：

```bash
# 確保已有 credentials.json
ls config/credentials.json

# 執行初次授權
python setup.py

# 確認產生 token.json
ls config/token.json
```

> ⚠️ **重要**：`token.json` 檔案將在 Docker 容器中使用，請勿刪除。

### 步驟 2: 配置 Docker 部署
**Dockerfile 配置**：

```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安裝依賴
COPY requirements.txt .
RUN pip install -r requirements.txt

# 複製應用程式檔案
COPY src/ src/
COPY main.py .
COPY config/settings.yaml config/
COPY config/credentials.json config/

# 重要：不要複製 token.json，它將通過 volume 掛載
# COPY config/token.json config/  # 勿啟用這一行

CMD ["python", "main.py"]
```

### 步驟 3: Docker Compose 配置

**docker-compose.yml 配置**：

```yaml
# docker-compose.yml
version: '3.8'

services:
  calendarbridge:
    build: .
    volumes:
      # OAuth 認證檔案掛載
      - ./config/token.json:/app/config/token.json:ro  # 唯讀掛載
      # 數據持久化
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - TZ=Asia/Taipei
    restart: unless-stopped
    # 選擇性：資源限制
    deploy:
      resources:
        limits:
          memory: 256M
          cpus: '0.5'
```

> 📝 **說明**：
> - `token.json` 使用 `:ro` 唯讀掛載，防止意外修改
> - `data` 和 `logs` 目錄用於持久化存儲應用程式數據

### 步驟 4: 部署應用程式

```bash
# 構建並啟動容器
docker compose up -d

# 檢查運行狀態
docker compose ps

# 查看日誌
docker compose logs -f calendarbridge
```

## 🔄 Token 管理與維護

### 自動重新授權腳本

當 OAuth Token 過期時，使用以下腳本重新授權：

```bash
#!/bin/bash
# renew_oauth_token.sh

echo "🔄 重新授權 OAuth Token..."

# 停止容器
docker compose stop calendarbridge

# 刪除舊的 token
rm -f config/token.json

# 重新授權
echo "⚙️ 正在重新授權..."
python setup.py

# 重啟容器
echo "🚀 重啟容器..."
docker compose start calendarbridge

echo "✅ OAuth Token 更新完成！"
```

使用方式：
```bash
# 設置執行權限
chmod +x renew_oauth_token.sh

# 執行重新授權
./renew_oauth_token.sh
```

### Token 過期檢測

監控 Token 狀態：

```bash
# 檢查應用程式日誌
docker compose logs calendarbridge | grep -i "auth\|token\|error"

# 檢查容器狀態
docker compose ps
```

## 📊 優缺點分析

### 優點
- ✅ 使用標準 OAuth 機制
- ✅ 可存取個人所有行事曆
- ✅ token.json 持久化保存
- ✅ 設置相對簡單

### 缺點
- ❌ 需要定期手動重新授權（通常每年一次）
- ❌ Token 失效時服務會自動停止
- ❌ 不適合完全自動化的生產環境

## 🔍 常見問題

### Q1: 容器啟動後即退出
**可能原因**：
- `token.json` 檔案不存在或损壞
- 認證失敗

**解決方法**：
```bash
# 檢查日誌
docker compose logs calendarbridge

# 重新授權
./renew_oauth_token.sh
```

### Q2: Token 過期後如何恢復？
**解決方法**：
使用上面提供的 `renew_oauth_token.sh` 腳本。

### Q3: 無法存取某些行事曆
**可能原因**：
- OAuth 權限範圍不足
- 行事曆設定為私人

**解決方法**：
重新執行 OAuth 授權，確保選擇正確的權限範圍。

## 🔗 相關文件

- [認證方式選擇指南](google_api_setup.md) - 選擇適合的認證方式
- [服務帳號設置](service_account_setup.md) - 推薦的 Docker 認證方式
- [部署指南](deployment_guide.md) - 完整部署說明
- [故障排除指南](troubleshooting.md) - 更多問題解決方案