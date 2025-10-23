#!/bin/bash
# 服务管理脚本

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

SERVICE_NAME="hotsearch-crawler"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 显示帮助信息
show_help() {
    echo -e "${GREEN}07173热搜爬虫 - 服务管理工具${NC}"
    echo ""
    echo "用法: $0 [命令]"
    echo ""
    echo "命令："
    echo "  status    查看服务状态"
    echo "  start     启动服务"
    echo "  stop      停止服务"
    echo "  restart   重启服务"
    echo "  logs      查看实时日志"
    echo "  logs-app  查看应用日志"
    echo "  enable    设置开机自启"
    echo "  disable   禁用开机自启"
    echo "  data      查看数据摘要"
    echo "  clean     清理旧数据（保留最近7天）"
    echo "  test      测试运行一次"
    echo "  uninstall 卸载服务"
    echo ""
}

# 检查服务是否存在
check_service() {
    if ! systemctl list-unit-files | grep -q "$SERVICE_NAME.service"; then
        echo -e "${RED}错误: 服务未安装${NC}"
        echo "请先运行: sudo bash deploy.sh"
        exit 1
    fi
}

# 查看状态
status() {
    check_service
    echo -e "${BLUE}=== 服务状态 ===${NC}"
    sudo systemctl status $SERVICE_NAME.service --no-pager
    echo ""

    # 显示数据信息
    if [ -f "$SCRIPT_DIR/data/latest.json" ]; then
        echo -e "${BLUE}=== 最新数据 ===${NC}"
        python3 -c "
import json
from datetime import datetime

with open('$SCRIPT_DIR/data/latest.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

crawl_time = data['crawl_time']
platform_count = len(data['platforms'])
total_items = sum(len(info['data']) for info in data['platforms'].values())

print(f'抓取时间: {crawl_time}')
print(f'平台数量: {platform_count}')
print(f'热搜总数: {total_items}')
"
    fi
}

# 启动服务
start() {
    check_service
    echo -e "${GREEN}启动服务...${NC}"
    sudo systemctl start $SERVICE_NAME.service
    sleep 1
    if sudo systemctl is-active --quiet $SERVICE_NAME.service; then
        echo -e "${GREEN}✓ 服务已启动${NC}"
    else
        echo -e "${RED}✗ 服务启动失败${NC}"
        sudo systemctl status $SERVICE_NAME.service --no-pager
    fi
}

# 停止服务
stop() {
    check_service
    echo -e "${YELLOW}停止服务...${NC}"
    sudo systemctl stop $SERVICE_NAME.service
    sleep 1
    if sudo systemctl is-active --quiet $SERVICE_NAME.service; then
        echo -e "${RED}✗ 服务仍在运行${NC}"
    else
        echo -e "${GREEN}✓ 服务已停止${NC}"
    fi
}

# 重启服务
restart() {
    check_service
    echo -e "${YELLOW}重启服务...${NC}"
    sudo systemctl restart $SERVICE_NAME.service
    sleep 1
    if sudo systemctl is-active --quiet $SERVICE_NAME.service; then
        echo -e "${GREEN}✓ 服务已重启${NC}"
    else
        echo -e "${RED}✗ 服务重启失败${NC}"
        sudo systemctl status $SERVICE_NAME.service --no-pager
    fi
}

# 查看系统日志
logs() {
    check_service
    echo -e "${BLUE}查看实时日志 (Ctrl+C 退出)${NC}"
    sudo journalctl -u $SERVICE_NAME.service -f
}

# 查看应用日志
logs_app() {
    LOG_FILE=$(ls -t "$SCRIPT_DIR/logs/crawler_"*.log 2>/dev/null | head -1)
    if [ -n "$LOG_FILE" ]; then
        echo -e "${BLUE}查看应用日志: $LOG_FILE${NC}"
        tail -50 "$LOG_FILE"
        echo ""
        echo "实时查看: tail -f $LOG_FILE"
    else
        echo -e "${RED}未找到日志文件${NC}"
    fi
}

# 启用开机自启
enable() {
    check_service
    echo -e "${GREEN}设置开机自启...${NC}"
    sudo systemctl enable $SERVICE_NAME.service
    echo -e "${GREEN}✓ 已设置开机自启${NC}"
}

# 禁用开机自启
disable() {
    check_service
    echo -e "${YELLOW}禁用开机自启...${NC}"
    sudo systemctl disable $SERVICE_NAME.service
    echo -e "${GREEN}✓ 已禁用开机自启${NC}"
}

# 查看数据
data() {
    if [ -f "$SCRIPT_DIR/data/latest.json" ]; then
        cd "$SCRIPT_DIR"
        python3 view_data.py
    else
        echo -e "${RED}未找到数据文件${NC}"
    fi
}

# 清理旧数据
clean() {
    echo -e "${YELLOW}清理7天前的历史数据...${NC}"

    # 统计文件数量
    OLD_COUNT=$(find "$SCRIPT_DIR/data" -name "hotsearch_*.json" -mtime +7 2>/dev/null | wc -l)

    if [ "$OLD_COUNT" -gt 0 ]; then
        echo "找到 $OLD_COUNT 个旧文件"
        read -p "确认删除？(y/N) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            find "$SCRIPT_DIR/data" -name "hotsearch_*.json" -mtime +7 -delete
            echo -e "${GREEN}✓ 清理完成${NC}"
        else
            echo "已取消"
        fi
    else
        echo "没有需要清理的文件"
    fi

    # 显示当前数据统计
    TOTAL_FILES=$(find "$SCRIPT_DIR/data" -name "hotsearch_*.json" 2>/dev/null | wc -l)
    TOTAL_SIZE=$(du -sh "$SCRIPT_DIR/data" 2>/dev/null | cut -f1)
    echo ""
    echo "当前数据: $TOTAL_FILES 个文件，总大小 $TOTAL_SIZE"
}

# 测试运行
test() {
    echo -e "${GREEN}测试运行爬虫...${NC}"
    cd "$SCRIPT_DIR"
    python3 scheduler.py --once
}

# 卸载服务
uninstall() {
    echo -e "${RED}=== 卸载服务 ===${NC}"
    echo "这将："
    echo "  1. 停止并禁用systemd服务"
    echo "  2. 删除服务配置文件"
    echo "  3. 保留数据和日志文件"
    echo ""
    read -p "确认卸载？(y/N) " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if systemctl list-unit-files | grep -q "$SERVICE_NAME.service"; then
            sudo systemctl stop $SERVICE_NAME.service 2>/dev/null || true
            sudo systemctl disable $SERVICE_NAME.service 2>/dev/null || true
            sudo rm -f "/etc/systemd/system/$SERVICE_NAME.service"
            sudo systemctl daemon-reload
            echo -e "${GREEN}✓ 服务已卸载${NC}"
            echo ""
            echo "数据文件保留在: $SCRIPT_DIR/data"
            echo "日志文件保留在: $SCRIPT_DIR/logs"
        else
            echo -e "${YELLOW}服务未安装${NC}"
        fi
    else
        echo "已取消"
    fi
}

# 主逻辑
case "${1:-help}" in
    status)
        status
        ;;
    start)
        start
        ;;
    stop)
        stop
        ;;
    restart)
        restart
        ;;
    logs)
        logs
        ;;
    logs-app)
        logs_app
        ;;
    enable)
        enable
        ;;
    disable)
        disable
        ;;
    data)
        data
        ;;
    clean)
        clean
        ;;
    test)
        test
        ;;
    uninstall)
        uninstall
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo -e "${RED}未知命令: $1${NC}"
        echo ""
        show_help
        exit 1
        ;;
esac
