#!/bin/bash

# PDF 提取器網站部署腳本

set -e

echo "開始部署 PDF 提取器網站..."

# 檢查 Docker 是否安裝
if ! command -v docker &> /dev/null; then
    echo "Docker 未安裝，請先安裝 Docker"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose 未安裝，請先安裝 Docker Compose"
    exit 1
fi

# 創建必要的目錄
mkdir -p uploads
mkdir -p logs

# 設置權限
chmod 755 uploads
chmod 755 logs

# 構建並啟動服務
echo "構建 Docker 鏡像..."
docker-compose build

echo "啟動服務..."
docker-compose up -d

# 等待服務啟動
echo "等待服務啟動..."
sleep 10

# 檢查服務狀態
echo "檢查服務狀態..."
docker-compose ps

# 測試服務是否正常運行
if curl -f http://localhost >/dev/null 2>&1; then
    echo "✅ 服務已成功啟動！"
    echo "🌐 網站地址: http://localhost"
else
    echo "❌ 服務啟動失敗，請檢查日誌："
    docker-compose logs
fi

echo "部署完成！"
echo ""
echo "常用命令："
echo "  查看日誌: docker-compose logs -f"
echo "  停止服務: docker-compose down"
echo "  重啟服務: docker-compose restart"
echo "  查看狀態: docker-compose ps"
