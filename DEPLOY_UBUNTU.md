# Ubuntu 服务器部署指南

完整的Ubuntu服务器部署方案，包含systemd服务自动启动。

## 📋 系统要求

- **操作系统**: Ubuntu 18.04+ / Debian 10+
- **Python**: 3.7+
- **权限**: sudo权限（用于安装系统服务）
- **网络**: 可访问互联网

## 🚀 一键部署

### 方法1: 自动部署脚本（推荐）

```bash
# 1. 上传项目到服务器
# 可以使用 scp, rsync, git clone 等方式

# 2. 进入项目目录
cd 热点爬取/

# 3. 运行自动部署脚本
sudo bash deploy.sh
```

部署脚本会自动完成：
- ✅ 检查并安装Python环境
- ✅ 安装项目依赖
- ✅ 创建数据和日志目录
- ✅ 测试运行爬虫
- ✅ 创建systemd服务
- ✅ 启动并启用服务

### 方法2: 手动部署

```bash
# 1. 安装Python和pip
sudo apt update
sudo apt install -y python3 python3-pip

# 2. 安装项目依赖
pip3 install -r requirements.txt

# 3. 测试运行
python3 scheduler.py --once

# 4. 创建systemd服务（见下文）
```

## 📦 上传项目到服务器

### 使用 SCP

```bash
# 从本地上传（在macOS上执行）
scp -r "/Users/mac/Documents/computerscience/小工具/热点爬取" user@your-server:/home/user/
```

### 使用 rsync（推荐）

```bash
# 更高效的同步方式
rsync -avz --exclude 'data/*' --exclude 'logs/*' \
  "/Users/mac/Documents/computerscience/小工具/热点爬取/" \
  user@your-server:/home/user/热点爬取/
```

### 使用 Git

```bash
# 如果项目已上传到Git仓库
ssh user@your-server
git clone your-repo-url
cd 热点爬取
```

## 🔧 systemd 服务配置

### 服务文件位置
`/etc/systemd/system/hotsearch-crawler.service`

### 服务配置内容

```ini
[Unit]
Description=07173 Hot Search Crawler
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=your-username
WorkingDirectory=/path/to/热点爬取
ExecStart=/usr/bin/python3 /path/to/热点爬取/scheduler.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

Environment="PYTHONUNBUFFERED=1"

NoNewPrivileges=true
PrivateTmp=true

[Install]
WantedBy=multi-user.target
```

### 手动创建服务

```bash
# 1. 创建服务文件
sudo nano /etc/systemd/system/hotsearch-crawler.service

# 2. 粘贴上述配置内容（修改路径和用户名）

# 3. 重载systemd
sudo systemctl daemon-reload

# 4. 启用服务
sudo systemctl enable hotsearch-crawler

# 5. 启动服务
sudo systemctl start hotsearch-crawler
```

## 🎮 服务管理

### 使用管理脚本（推荐）

```bash
# 查看状态
./manage.sh status

# 启动服务
./manage.sh start

# 停止服务
./manage.sh stop

# 重启服务
./manage.sh restart

# 查看实时日志
./manage.sh logs

# 查看应用日志
./manage.sh logs-app

# 查看数据
./manage.sh data

# 清理旧数据
./manage.sh clean

# 测试运行
./manage.sh test

# 卸载服务
./manage.sh uninstall
```

### 使用 systemctl 命令

```bash
# 查看服务状态
sudo systemctl status hotsearch-crawler

# 启动服务
sudo systemctl start hotsearch-crawler

# 停止服务
sudo systemctl stop hotsearch-crawler

# 重启服务
sudo systemctl restart hotsearch-crawler

# 查看实时日志
sudo journalctl -u hotsearch-crawler -f

# 查看最近100行日志
sudo journalctl -u hotsearch-crawler -n 100

# 启用开机自启
sudo systemctl enable hotsearch-crawler

# 禁用开机自启
sudo systemctl disable hotsearch-crawler
```

## 📊 监控和维护

### 检查服务运行状态

```bash
# 快速检查
sudo systemctl is-active hotsearch-crawler

# 详细状态
./manage.sh status
```

### 查看日志

```bash
# 系统日志（推荐用于调试）
sudo journalctl -u hotsearch-crawler -f

# 应用日志
tail -f logs/crawler_*.log

# 查看错误日志
sudo journalctl -u hotsearch-crawler -p err
```

### 数据管理

```bash
# 查看数据摘要
python3 view_data.py

# 查看指定平台
python3 view_data.py --platform 哔哩哔哩

# 查看数据文件大小
du -sh data/

# 统计文件数量
ls -l data/*.json | wc -l

# 清理旧数据（保留最近7天）
./manage.sh clean
```

### 自动清理脚本

创建定时任务自动清理旧数据：

```bash
# 编辑crontab
crontab -e

# 添加以下行（每天凌晨3点清理）
0 3 * * * find /path/to/热点爬取/data -name "hotsearch_*.json" -mtime +7 -delete
```

## 🔒 安全建议

### 1. 使用非root用户运行

```bash
# 服务配置中使用普通用户
User=your-username
```

### 2. 限制文件权限

```bash
# 设置合适的权限
chmod 755 *.sh *.py
chmod 644 *.json *.txt *.md
chmod 700 data/ logs/
```

### 3. 防火墙配置

爬虫只需要出站网络访问，不需要开放任何端口。

### 4. 定期备份

```bash
# 备份数据到其他位置
rsync -av data/ /backup/hotsearch/$(date +%Y%m%d)/
```

## 🚨 故障排查

### 问题1: 服务启动失败

```bash
# 查看详细错误信息
sudo systemctl status hotsearch-crawler -l

# 查看日志
sudo journalctl -u hotsearch-crawler -n 50

# 检查Python路径
which python3

# 测试手动运行
cd /path/to/热点爬取
python3 scheduler.py --once
```

### 问题2: 依赖安装失败

```bash
# 使用国内镜像
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 升级pip
pip3 install --upgrade pip
```

### 问题3: 权限错误

```bash
# 确保目录权限正确
sudo chown -R your-username:your-username /path/to/热点爬取

# 确保可以写入数据和日志
chmod 755 data/ logs/
```

### 问题4: 网络连接问题

```bash
# 测试网络连接
curl -I https://api.pearktrue.cn/api/dailyhot/

# 测试DNS解析
nslookup api.pearktrue.cn

# 检查代理设置（如果需要）
echo $http_proxy
echo $https_proxy
```

### 问题5: 服务意外停止

```bash
# 查看服务日志查找原因
sudo journalctl -u hotsearch-crawler -n 200

# 检查系统资源
free -h
df -h

# 重启服务
sudo systemctl restart hotsearch-crawler
```

## 📈 性能优化

### 1. 调整运行间隔

编辑 `config.json`：
```json
{
  "scheduler": {
    "interval_hours": 2
  }
}
```

重启服务生效：
```bash
sudo systemctl restart hotsearch-crawler
```

### 2. 限制历史数据

只保存最新数据，不保存历史：
```json
{
  "scheduler": {
    "save_history": false
  }
}
```

### 3. 资源限制

在服务配置中添加资源限制：
```ini
[Service]
MemoryLimit=200M
CPUQuota=20%
```

## 🔄 更新部署

```bash
# 1. 停止服务
sudo systemctl stop hotsearch-crawler

# 2. 备份数据
cp -r data/ data.backup/

# 3. 更新代码
rsync -av new-code/ /path/to/热点爬取/

# 4. 更新依赖
pip3 install -r requirements.txt --upgrade

# 5. 测试运行
python3 scheduler.py --once

# 6. 重启服务
sudo systemctl start hotsearch-crawler
```

## 📱 远程访问数据

### 通过SSH查看

```bash
# SSH登录后
./manage.sh data
```

### 通过SCP下载

```bash
# 下载最新数据到本地
scp user@server:/path/to/热点爬取/data/latest.json ./
```

### 搭建简单Web服务（可选）

```bash
# 在data目录启动HTTP服务器（仅用于临时访问）
cd data
python3 -m http.server 8000

# 然后通过浏览器访问
# http://your-server-ip:8000/latest.json
```

## ✅ 部署检查清单

部署完成后，检查以下项目：

- [ ] Python环境正确安装（python3 --version）
- [ ] 依赖包安装成功（pip3 list）
- [ ] 测试运行成功（python3 scheduler.py --once）
- [ ] systemd服务已创建
- [ ] 服务运行正常（systemctl status）
- [ ] 开机自启已启用（systemctl is-enabled）
- [ ] 数据文件正常生成（ls data/）
- [ ] 日志文件正常写入（ls logs/）
- [ ] 可以查看数据（python3 view_data.py）

## 📞 技术支持

如遇到问题：
1. 查看日志文件获取详细错误信息
2. 检查网络连接和API服务状态
3. 确认Python版本和依赖包是否正确
4. 参考故障排查章节

---

**部署完成后，爬虫将每小时自动运行，数据保存在 `data/` 目录！**
