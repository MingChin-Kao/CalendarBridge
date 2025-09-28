# Docker 環境中的 OAuth 設置

## 方案：預先授權 + 持久化存儲

### 步驟 1: 本地完成授權
在部署前，在本地環境完成授權：
```bash
# 在本地執行授權
python setup.py
# 這會產生 config/token.json
```

### 步驟 2: 設計 Docker 部署
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src/ src/
COPY main.py .
COPY config/settings.yaml config/
COPY config/credentials.json config/

# 不要複製 token.json - 通過 volume 掛載

CMD ["python", "main.py", "--continuous"]
```

### 步驟 3: Docker Compose 配置
```yaml
# docker-compose.yml
version: '3.8'
services:
  calendarbridge:
    build: .
    volumes:
      - ./config/token.json:/app/config/token.json
      - ./data:/app/data
      - ./logs:/app/logs
    environment:
      - TZ=Asia/Taipei
    restart: unless-stopped
```

### 步驟 4: 自動重新授權腳本
```bash
#!/bin/bash
# renew_auth.sh
docker-compose stop calendarbridge
rm -f config/token.json
python setup.py  # 重新授權
docker-compose start calendarbridge
```

## 優點
- 使用現有的 OAuth 機制
- token.json 持久化保存
- 相對簡單

## 缺點
- 需要定期手動重新授權
- token 失效時服務會停止