# 🔍 PDF 內容提取與分類系統

一個智能的 PDF 文件處理工具，能夠提取文字內容並自動分類為結構化的表格格式。

## ✨ 主要功能

- 📄 **智能文字提取**：從 PDF 中提取文字並保留格式
- 🎨 **字體樣式識別**：自動識別斜體、粗體等樣式
- 🏷️ **自動分類**：智能分類內容到相應欄位（標題、作者、描述等）
- 💾 **多格式輸出**：支援 Excel、CSV 格式下載
- 🌐 **Web 介面**：直觀的拖拽上傳介面
- 🔧 **HTML 格式化**：標題自動加粗(`<b></b>`)，斜體自動標記(`<i></i>`)

## 🚀 快速開始

### 方法一：本地 Docker 部署
```bash
git clone https://github.com/aaa89550/backstage.git
cd backstage
./deploy.sh
```
訪問：http://localhost

### 方法二：雲端部署
請參考 [雲端部署指南](CLOUD_DEPLOY.md)

### 方法三：本地開發
```bash
pip install -r requirements.txt
python web_app.py
```
訪問：http://localhost:5000

## 📋 系統要求

- Python 3.11+
- Docker & Docker Compose（推薦）
- 或安裝依賴：`pip install -r requirements.txt`

## 🛠️ 使用方法

1. **上傳 PDF**：拖拽或選擇 PDF 檔案
2. **自動處理**：系統自動提取和分類內容
3. **預覽結果**：在網頁上即時查看結果
4. **下載數據**：選擇 Excel 或 CSV 格式下載

## 📊 輸出欄位

| 欄位 | 說明 |
|------|------|
| filename | 檔案名稱 |
| Title | 標題（自動加粗） |
| Type | 類型 |
| Authors | 作者 |
| Translator | 翻譯者 |
| Illustrator | 插畫家 |
| Publisher | 出版社 |
| Detail | 詳細描述 |
| Year | 年份 |
| Pages | 頁數 |

## 🏗️ 專案結構

```
├── web_app.py              # Flask 主應用
├── advanced_pdf_extractor.py  # 進階 PDF 處理
├── text_processor.py       # 文字處理模組
├── templates/
│   └── index.html          # 前端介面
├── Dockerfile              # Docker 配置
├── docker-compose.yml      # 容器編排
├── requirements.txt        # Python 依賴
└── deploy.sh              # 一鍵部署腳本
```

## 📚 部署指南

- [完整部署指南](DEPLOYMENT_GUIDE.md)
- [雲端部署選項](CLOUD_DEPLOY.md)
- [快速部署說明](QUICK_DEPLOY.md)

## 🔧 開發

```bash
# 安裝依賴
pip install -r requirements.txt

# 開發模式運行
python web_app.py

# Docker 開發
docker-compose up --build
```

## 📄 授權

MIT License

## 🤝 貢獻

歡迎提交 Issues 和 Pull Requests！

---

Made with ❤️ by aaa89550
