# PDF 擷取與分類網站部署指南

本指南提供多種部署方案，從簡單的本地部署到雲端生產環境。

## 🚀 部署選項

### 1. 本地部署（最簡單）
### 2. Docker 容器部署
### 3. 雲端平台部署
### 4. 生產環境部署

---

## 📋 部署前準備

### 系統需求
- Python 3.8+
- 8GB+ RAM（處理大型 PDF）
- 2GB+ 硬碟空間

### 依賴項檢查
```bash
# 檢查 Python 版本
python3 --version

# 檢查 pip
pip3 --version
```

---

## 🏠 方案 1：本地部署

### 步驟 1：環境設置
```bash
# 克隆或下載項目
git clone <your-repo-url>
cd backstage

# 創建虛擬環境
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 安裝依賴
pip install -r requirements.txt
```

### 步驟 2：啟動服務
```bash
# 開發模式
python web_app.py

# 或指定端口
python -c "
import sys
sys.path.append('.')
from web_app import app
app.run(host='0.0.0.0', port=8080, debug=False)
"
```

### 步驟 3：訪問網站
- 本地訪問：http://localhost:5002
- 網路訪問：http://your-ip:5002

---

## 🐳 方案 2：Docker 容器部署

### 優點
- 環境一致性
- 易於擴展
- 跨平台兼容

### 文件準備
我將為您創建 Dockerfile 和相關配置文件。

---

## ☁️ 方案 3：雲端平台部署

### 3.1 Heroku 部署
- 免費額度可用
- 簡單易用
- 自動 HTTPS

### 3.2 Google Cloud Run
- 按使用付費
- 自動擴展
- 高可用性

### 3.3 AWS EC2
- 完全控制
- 可自定義配置
- 適合大流量

### 3.4 DigitalOcean App Platform
- 簡單部署
- 合理價格
- 良好性能

---

## 🏭 方案 4：生產環境部署

### 使用 Gunicorn + Nginx
- 高性能
- 負載均衡
- 適合生產環境

---

## 🔒 安全設置

### 環境變量
```bash
# 創建 .env 文件
SECRET_KEY=your-secret-key-here
FLASK_ENV=production
MAX_CONTENT_LENGTH=50MB
UPLOAD_FOLDER=./uploads
```

### 防火牆設置
```bash
# Ubuntu/Debian
sudo ufw allow 80
sudo ufw allow 443
sudo ufw allow 22
sudo ufw enable
```

---

## 📊 監控與日誌

### 日誌配置
- 訪問日誌
- 錯誤日誌
- 性能監控

### 備份策略
- 定期備份上傳的文件
- 數據庫備份（如果使用）
- 配置文件備份

---

## 🔧 故障排除

### 常見問題
1. **端口被佔用**
2. **記憶體不足**
3. **PDF 處理失敗**
4. **文件上傳限制**

### 解決方案
詳細的故障排除步驟和解決方案。

---

## 📞 支援與維護

### 更新流程
```bash
# 停止服務
sudo systemctl stop pdf-extractor

# 更新代碼
git pull origin main

# 重新安裝依賴
pip install -r requirements.txt

# 重啟服務
sudo systemctl start pdf-extractor
```

### 性能優化
- 文件大小限制
- 並發處理數量
- 記憶體使用優化
- 快取策略

---

## 📈 擴展選項

### 添加功能
- 用戶認證
- 批量處理隊列
- API 接口
- 數據分析儀表板

### 整合第三方服務
- 雲端存儲（AWS S3, Google Cloud Storage）
- 數據庫（PostgreSQL, MongoDB）
- 通知服務（Email, Slack）
