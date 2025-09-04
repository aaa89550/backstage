# 🚀 PDF 提取器 - 快速部署指南

恭喜！您的 PDF 提取器現在已經準備好部署了！

## 📋 部署選項

### 1. 本地 Docker 部署（推薦）

```bash
# 1. 克隆或下載專案到您的伺服器
git clone <your-repo> pdf-extractor
cd pdf-extractor

# 2. 執行部署腳本
./deploy.sh
```

部署完成後訪問：http://localhost

### 2. Heroku 雲端部署

```bash
# 1. 安裝 Heroku CLI
# 2. 登入 Heroku
heroku login

# 3. 創建應用
heroku create your-pdf-extractor-app

# 4. 部署
git add .
git commit -m "Deploy PDF extractor"
git push heroku main

# 5. 開啟應用
heroku open
```

### 3. Railway 雲端部署

1. 登入 [Railway](https://railway.app)
2. 點擊 "Deploy from GitHub repo"
3. 選擇您的專案
4. Railway 會自動部署

### 4. DigitalOcean App Platform

1. 登入 [DigitalOcean](https://cloud.digitalocean.com)
2. 創建新的 App
3. 連接您的 GitHub 倉庫
4. 選擇自動部署

## 🔧 本地開發模式

```bash
# 安裝依賴
pip install -r requirements.txt

# 啟動開發伺服器
python web_app.py
```

訪問：http://localhost:5000

## 📁 檔案結構

```
pdf-extractor/
├── web_app.py              # Flask 主程式
├── advanced_pdf_extractor.py  # PDF 處理核心
├── text_processor.py       # 文字處理模組
├── templates/
│   └── index.html          # 前端介面
├── requirements.txt        # Python 依賴
├── Dockerfile             # Docker 配置
├── docker-compose.yml     # Docker 編排
├── nginx.conf            # Nginx 配置
├── deploy.sh             # 部署腳本
└── Procfile              # Heroku 配置
```

## 🌐 環境設定

複製 `.env.example` 為 `.env` 並修改設定：

```bash
cp .env.example .env
# 編輯 .env 檔案設定您的配置
```

## 🛠️ 常用指令

```bash
# Docker 相關
docker-compose up -d        # 啟動服務
docker-compose down         # 停止服務
docker-compose logs -f      # 查看日誌
docker-compose restart      # 重啟服務

# Heroku 相關
heroku logs --tail          # 查看日誌
heroku restart             # 重啟應用
heroku config:set VAR=value # 設定環境變數
```

## 🔐 生產環境安全

1. **設定 SECRET_KEY**：
   ```bash
   export SECRET_KEY="your-random-secret-key"
   ```

2. **啟用 HTTPS**：
   - 修改 `nginx.conf` 中的 SSL 設定
   - 添加 SSL 憑證

3. **設定防火牆**：
   ```bash
   ufw allow 80
   ufw allow 443
   ufw enable
   ```

## 📊 監控與維護

- **健康檢查**：訪問 `/health` 端點
- **日誌查看**：`docker-compose logs pdf-extractor`
- **資源監控**：`docker stats`

## 🆘 故障排除

### 常見問題

1. **上傳失敗**：檢查文件大小限制（預設 16MB）
2. **記憶體不足**：增加 Docker 記憶體限制
3. **端口衝突**：修改 `docker-compose.yml` 中的端口

### 日誌查看

```bash
# 查看應用日誌
docker-compose logs pdf-extractor

# 查看 nginx 日誌
docker-compose logs nginx

# 即時日誌
docker-compose logs -f
```

## 📞 支援

如果遇到任何問題，請檢查：
1. 所有依賴是否正確安裝
2. 端口是否可用
3. 防火牆設定
4. 日誌錯誤訊息

---

🎉 **恭喜！您的 PDF 提取器已準備好為世界服務！** 🎉
