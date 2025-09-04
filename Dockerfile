# 使用官方 Python 鏡像
FROM python:3.11-slim

# 設置工作目錄
WORKDIR /app

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# 複製依賴文件
COPY requirements.txt .

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製應用代碼
COPY . .

# 創建上傳目錄
RUN mkdir -p uploads

# 設置環境變量
ENV FLASK_APP=web_app.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# 暴露端口
EXPOSE 5000

# 創建非 root 用戶
RUN useradd --create-home --shell /bin/bash app \
    && chown -R app:app /app
USER app

# 啟動命令
CMD ["python", "web_app.py"]
