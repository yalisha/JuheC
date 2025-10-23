#!/bin/bash
# Ubuntu服务器自动部署脚本

set -e  # 遇到错误立即退出

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}07173热搜爬虫 - Ubuntu服务器部署${NC}"
echo -e "${GREEN}================================${NC}"
echo ""

# 检查是否为root或有sudo权限
if [[ $EUID -ne 0 ]] && ! sudo -n true 2>/dev/null; then
    echo -e "${RED}错误: 需要sudo权限来安装系统服务${NC}"
    echo "请使用以下命令运行："
    echo "  sudo bash deploy.sh"
    exit 1
fi

# 获取当前目录的绝对路径
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo -e "${YELLOW}项目目录: ${SCRIPT_DIR}${NC}"

# 1. 检查Python环境
echo ""
echo -e "${GREEN}[1/6] 检查Python环境...${NC}"
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
    echo "✓ Python版本: $PYTHON_VERSION"
else
    echo -e "${RED}✗ 未找到Python3，正在安装...${NC}"
    sudo apt update
    sudo apt install -y python3 python3-pip
fi

# 2. 安装依赖
echo ""
echo -e "${GREEN}[2/6] 安装Python依赖...${NC}"
if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
    pip3 install -r "$SCRIPT_DIR/requirements.txt" --quiet
    echo "✓ 依赖安装完成"
else
    echo -e "${RED}✗ 未找到requirements.txt${NC}"
    exit 1
fi

# 3. 创建必要的目录
echo ""
echo -e "${GREEN}[3/6] 创建数据和日志目录...${NC}"
mkdir -p "$SCRIPT_DIR/data"
mkdir -p "$SCRIPT_DIR/logs"
echo "✓ 目录创建完成"

# 4. 测试运行
echo ""
echo -e "${GREEN}[4/6] 测试运行爬虫...${NC}"
cd "$SCRIPT_DIR"
if timeout 60 python3 scheduler.py --once > /tmp/crawler_test.log 2>&1; then
    echo "✓ 测试运行成功"
    # 显示抓取结果
    if [ -f "$SCRIPT_DIR/data/latest.json" ]; then
        PLATFORM_COUNT=$(python3 -c "import json; data=json.load(open('data/latest.json')); print(len(data['platforms']))")
        echo "  成功抓取 $PLATFORM_COUNT 个平台的数据"
    fi
else
    echo -e "${RED}✗ 测试运行失败，查看日志:${NC}"
    tail -20 /tmp/crawler_test.log
    exit 1
fi

# 5. 创建systemd服务
echo ""
echo -e "${GREEN}[5/6] 创建systemd服务...${NC}"

# 获取当前用户（如果是sudo运行，获取实际用户）
CURRENT_USER=${SUDO_USER:-$USER}

# 创建服务文件
SERVICE_FILE="/etc/systemd/system/hotsearch-crawler.service"
sudo tee "$SERVICE_FILE" > /dev/null <<EOF
[Unit]
Description=07173 Hot Search Crawler
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$CURRENT_USER
WorkingDirectory=$SCRIPT_DIR
ExecStart=/usr/bin/python3 $SCRIPT_DIR/scheduler.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# 环境变量
Environment="PYTHONUNBUFFERED=1"

# 安全设置
NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
EOF

echo "✓ 服务文件已创建: $SERVICE_FILE"

# 6. 启用并启动服务
echo ""
echo -e "${GREEN}[6/6] 启用并启动服务...${NC}"
sudo systemctl daemon-reload
sudo systemctl enable hotsearch-crawler.service
sudo systemctl start hotsearch-crawler.service

# 等待服务启动
sleep 2

# 检查服务状态
if sudo systemctl is-active --quiet hotsearch-crawler.service; then
    echo -e "${GREEN}✓ 服务已成功启动${NC}"
else
    echo -e "${RED}✗ 服务启动失败${NC}"
    sudo systemctl status hotsearch-crawler.service
    exit 1
fi

# 部署完成
echo ""
echo -e "${GREEN}================================${NC}"
echo -e "${GREEN}部署完成！${NC}"
echo -e "${GREEN}================================${NC}"
echo ""
echo "服务管理命令："
echo "  查看状态: sudo systemctl status hotsearch-crawler"
echo "  启动服务: sudo systemctl start hotsearch-crawler"
echo "  停止服务: sudo systemctl stop hotsearch-crawler"
echo "  重启服务: sudo systemctl restart hotsearch-crawler"
echo "  查看日志: sudo journalctl -u hotsearch-crawler -f"
echo "  禁用服务: sudo systemctl disable hotsearch-crawler"
echo ""
echo "数据文件位置："
echo "  最新数据: $SCRIPT_DIR/data/latest.json"
echo "  历史数据: $SCRIPT_DIR/data/hotsearch_*.json"
echo "  日志文件: $SCRIPT_DIR/logs/crawler_*.log"
echo ""
echo "查看数据："
echo "  python3 $SCRIPT_DIR/view_data.py"
echo ""
