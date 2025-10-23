#!/bin/bash
# 07173热搜爬虫启动脚本

# 切换到脚本所在目录
cd "$(dirname "$0")"

echo "================================"
echo "07173热搜爬虫启动脚本"
echo "================================"

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 python3，请先安装Python 3.7+"
    exit 1
fi

# 检查依赖
if ! python3 -c "import requests" 2>/dev/null; then
    echo "正在安装依赖..."
    pip3 install -r requirements.txt
fi

# 创建必要的目录
mkdir -p data logs

# 启动定时爬虫
echo "启动定时爬虫（每小时运行一次）..."
echo "按 Ctrl+C 停止"
echo ""

python3 scheduler.py

echo ""
echo "爬虫已停止"
