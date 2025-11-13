# CalendarBridge Dockerfile
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    tzdata \
    && rm -rf /var/lib/apt/lists/*

# 設定時區
ENV TZ=Asia/Taipei

# 複製依賴檔案
COPY requirements.txt .

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製程式碼
COPY src/ src/
COPY tools/ tools/
COPY main.py .

# 複製配置檔案（不包含敏感資料）
COPY config/settings.yaml config/

# 創建必要目錄
RUN mkdir -p data logs config

# 設定環境變數
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 健康檢查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.path.append('/app'); from src.utils.config import load_config; load_config('config/settings.yaml')" || exit 1

# 暴露埠（如果需要 web 介面）
# EXPOSE 8080

# 啟動命令
CMD ["python", "main.py"]