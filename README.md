# 07173 热搜爬虫系统

基于 07173.com 热搜榜的自动化爬虫系统，支持多平台热搜数据抓取和定时运行。

## 功能特点

- ✅ 支持17个主流平台热搜数据抓取
- ⏰ 每小时自动运行（可自定义间隔）
- 💾 数据持久化存储（JSON格式）
- 📊 完整的日志记录
- 🔄 失败重试机制
- 🛡️ 优雅的错误处理和信号处理

## 支持的平台

- 哔哩哔哩、抖音、微博、知乎、百度
- 少数派、IT之家、澎湃新闻、今日头条、36氪
- 稀土掘金、腾讯新闻、网易新闻
- 英雄联盟、原神、微信读书、贴吧

## 项目结构

```
热点爬取/
├── crawler.py          # 爬虫核心模块
├── scheduler.py        # 定时调度器
├── config.json         # 配置文件
├── requirements.txt    # Python依赖
├── run.sh             # 启动脚本
├── README.md          # 本文档
├── data/              # 数据存储目录
│   ├── latest.json    # 最新数据
│   └── hotsearch_*.json  # 历史数据
└── logs/              # 日志目录
    └── crawler_*.log  # 按月分割的日志
```

## 快速开始

### 本地使用

#### 1. 安装依赖

```bash
pip3 install -r requirements.txt
```

或者手动安装：
```bash
pip3 install requests schedule
```

#### 2. 运行方式

#### 方式一：使用启动脚本（推荐）

```bash
./run.sh
```

#### 方式二：单次运行

```bash
# 运行一次爬虫
python3 crawler.py

# 或使用调度器的单次模式
python3 scheduler.py --once
```

#### 方式三：定时运行

```bash
# 每小时运行一次（默认）
python3 scheduler.py

# 自定义间隔（例如每2小时）
python3 scheduler.py --interval 2
```

### Ubuntu 服务器部署 🚀

#### 快速部署（3分钟）

**1. 上传项目到服务器**

```bash
# 在本地执行
rsync -avz --exclude 'data/*' --exclude 'logs/*' \
  "/path/to/热点爬取/" user@your-server:/home/user/hotsearch/
```

**2. SSH登录并一键部署**

```bash
# 登录服务器
ssh user@your-server

# 进入目录
cd hotsearch

# 一键部署（自动安装依赖、创建systemd服务、启动运行）
sudo bash deploy.sh
```

**3. 验证运行**

```bash
# 查看服务状态
./manage.sh status

# 查看实时日志
./manage.sh logs

# 查看数据
./manage.sh data
```

#### 服务管理

```bash
./manage.sh status      # 查看状态
./manage.sh start       # 启动服务
./manage.sh stop        # 停止服务
./manage.sh restart     # 重启服务
./manage.sh logs        # 查看实时日志
./manage.sh data        # 查看数据摘要
./manage.sh clean       # 清理旧数据
./manage.sh test        # 测试运行
./manage.sh uninstall   # 卸载服务
```

#### 详细文档

- [Ubuntu快速部署指南](SERVER_QUICKSTART.md) - 3分钟快速部署
- [Ubuntu完整部署文档](DEPLOY_UBUNTU.md) - 详细部署说明

## 数据格式

### 最新数据文件：`data/latest.json`

```json
{
  "crawl_time": "2025-10-23T17:30:00",
  "platforms": {
    "哔哩哔哩": {
      "platform": "哔哩哔哩",
      "timestamp": "2025-10-23T17:30:01",
      "data": [
        {
          "title": "热搜标题",
          "url": "https://...",
          "hot": "热度值"
        }
      ]
    }
  }
}
```

### 历史数据：`data/hotsearch_YYYYMMDD_HHMMSS.json`

每次运行都会保存一份带时间戳的历史记录。

## 配置说明

编辑 `config.json` 可以自定义配置：

```json
{
  "crawler": {
    "data_dir": "data",        // 数据目录
    "log_dir": "logs",         // 日志目录
    "platforms": [...]         // 要爬取的平台列表
  },
  "scheduler": {
    "interval_hours": 1,       // 运行间隔（小时）
    "run_on_startup": true,    // 启动时立即运行
    "save_history": true       // 是否保存历史记录
  },
  "request": {
    "timeout": 10,             // 请求超时时间（秒）
    "retry": 3,                // 失败重试次数
    "delay_between_requests": 1 // 请求间隔（秒）
  }
}
```

## 日志说明

日志文件保存在 `logs/` 目录，按月分割：
- 文件名格式：`crawler_YYYYMM.log`
- 日志级别：INFO（包含所有操作记录）
- 同时输出到控制台和文件

## 停止运行

按 `Ctrl+C` 可以优雅地停止程序。

## 后台运行

### 使用 nohup（Linux/macOS）

```bash
nohup python3 scheduler.py > output.log 2>&1 &
```

### 使用 screen（Linux/macOS）

```bash
screen -S hotsearch
python3 scheduler.py
# 按 Ctrl+A 然后按 D 分离会话
# 恢复会话：screen -r hotsearch
```

### 使用 systemd（Linux）

创建服务文件 `/etc/systemd/system/hotsearch.service`：

```ini
[Unit]
Description=07173 Hot Search Crawler
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/热点爬取
ExecStart=/usr/bin/python3 scheduler.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务：
```bash
sudo systemctl enable hotsearch
sudo systemctl start hotsearch
sudo systemctl status hotsearch
```

## API 说明

本爬虫使用第三方API：
- 接口：`https://api.pearktrue.cn/api/dailyhot/`
- 参数：`?title=平台名称`
- 返回：JSON格式数据

## 注意事项

1. 请遵守API使用规范，不要过于频繁请求
2. 建议间隔时间不少于30分钟
3. 数据仅供学习和个人使用
4. 定期清理历史数据文件以节省空间

## 故障排查

### 问题：请求失败或超时
- 检查网络连接
- 确认API服务是否正常
- 增加重试次数或超时时间

### 问题：数据格式错误
- 检查API返回格式是否变化
- 查看日志文件获取详细错误信息

### 问题：权限错误
- 确保对 `data/` 和 `logs/` 目录有写入权限
- Linux/macOS 用户可能需要 `chmod +x run.sh`

## 开发者信息

- Python版本要求：3.7+
- 主要依赖：requests, schedule
- 编码：UTF-8

## 许可证

本项目仅供学习和研究使用。

## 更新日志

### v1.1.0 (2025-10-23)
- 🚀 新增Ubuntu服务器一键部署方案
- 🎮 新增服务管理工具（manage.sh）
- 🔧 新增systemd服务支持
- 📖 新增完整部署文档

### v1.0.0 (2025-10-23)
- ✨ 初始版本发布
- ✅ 支持16个平台热搜爬取
- ⏰ 实现定时调度功能
- 💾 数据持久化存储
- 📊 完整日志系统
