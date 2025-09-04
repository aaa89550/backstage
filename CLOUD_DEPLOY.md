# 🌐 雲端部署 - 永久在線方案

由於 Codespace 關閉後服務會停止，建議使用以下雲端部署方案：

## 🚀 免費雲端部署選項

### 1. Railway（推薦 - 最簡單）
```bash
# 1. 推送代碼到 GitHub
git add .
git commit -m "準備部署到 Railway"
git push origin main

# 2. 訪問 https://railway.app
# 3. 使用 GitHub 登入
# 4. 點擊 "Deploy from GitHub repo"
# 5. 選擇您的倉庫
# 6. Railway 會自動偵測並部署
```

**Railway 優點：**
- ✅ 完全免費（每月 $5 額度）
- ✅ 自動偵測 Dockerfile
- ✅ 自動 HTTPS
- ✅ 永久在線

### 2. Render（免費方案）
```bash
# 1. 推送代碼到 GitHub
git push origin main

# 2. 訪問 https://render.com
# 3. 連接 GitHub 倉庫
# 4. 選擇 "Web Service"
# 5. 配置：
#    - Build Command: docker build -t app .
#    - Start Command: python web_app.py
```

### 3. Heroku（有限免費）
```bash
# 1. 安裝 Heroku CLI
# 2. 登入並創建應用
heroku create your-pdf-extractor

# 3. 部署
git push heroku main

# 4. 開啟應用
heroku open
```

## 💰 付費但穩定的選項

### 1. DigitalOcean App Platform
- 月費約 $5-12
- 高穩定性
- 自動擴展

### 2. AWS/Google Cloud
- 按使用量計費
- 企業級穩定性

## 🏠 自架伺服器選項

### 1. VPS 伺服器
```bash
# 在您的 VPS 上：
git clone <your-repo>
cd pdf-extractor
./deploy.sh
```

### 2. 家用電腦 + Ngrok
```bash
# 在家用電腦上運行：
docker-compose up -d

# 使用 ngrok 公開訪問：
ngrok http 80
```

## 📋 推薦的快速部署步驟

1. **立即部署到 Railway**：
   - 最快 5 分鐘完成
   - 完全免費
   - 永久在線

2. **備用選項**：
   - Render（如果 Railway 有問題）
   - DigitalOcean（如果需要更多控制）

## 🔗 需要幫助？

選擇一個方案，我可以協助您完成部署！
