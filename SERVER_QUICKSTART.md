# Ubuntu 服务器快速部署（3分钟）

## 🚀 三步部署

### 1️⃣ 上传项目到服务器

**方法A: 使用 rsync（推荐）**
```bash
# 在本地macOS执行
rsync -avz --exclude 'data/*' --exclude 'logs/*' \
  "/Users/mac/Documents/computerscience/小工具/热点爬取/" \
  user@your-server-ip:/home/user/hotsearch/
```

**方法B: 使用 scp**
```bash
# 在本地macOS执行
scp -r "/Users/mac/Documents/computerscience/小工具/热点爬取" \
  user@your-server-ip:/home/user/
```

### 2️⃣ SSH登录服务器并部署

```bash
# 登录服务器
ssh user@your-server-ip

# 进入项目目录
cd hotsearch  # 或 热点爬取

# 一键部署
sudo bash deploy.sh
```

### 3️⃣ 完成！

部署脚本会自动完成所有配置，包括：
- ✅ 安装依赖
- ✅ 创建systemd服务
- ✅ 启动定时爬虫
- ✅ 设置开机自启

## 📋 部署后验证

```bash
# 检查服务状态
./manage.sh status

# 查看实时日志
./manage.sh logs

# 查看数据
./manage.sh data
```

## 🎮 常用命令

```bash
# 查看状态
./manage.sh status

# 重启服务
./manage.sh restart

# 查看数据
./manage.sh data

# 清理旧数据
./manage.sh clean
```

## 📂 重要文件位置

```
项目目录/
├── data/latest.json          # 最新数据
├── data/hotsearch_*.json     # 历史数据
└── logs/crawler_*.log        # 日志文件
```

## 🔧 修改配置

### 修改运行间隔

编辑 `config.json`，修改 `interval_hours`：

```json
{
  "scheduler": {
    "interval_hours": 2  # 改为2小时运行一次
  }
}
```

修改后重启服务：
```bash
./manage.sh restart
```

### 修改抓取平台

编辑 `config.json`，在 `platforms` 数组中添加/删除平台。

## 🚨 故障排查

### 服务未启动
```bash
# 查看详细日志
sudo journalctl -u hotsearch-crawler -n 50

# 手动测试
python3 scheduler.py --once
```

### 依赖安装失败
```bash
# 使用国内镜像
pip3 install -r requirements.txt \
  -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 查看完整文档
```bash
cat DEPLOY_UBUNTU.md
```

## 📊 监控数据

### 查看最新抓取
```bash
python3 view_data.py
```

### 查看指定平台
```bash
python3 view_data.py --platform 哔哩哔哩 --limit 10
```

### 下载数据到本地
```bash
# 在本地执行
scp user@server:/home/user/hotsearch/data/latest.json ./
```

## 🔄 更新代码

```bash
# 1. 停止服务
./manage.sh stop

# 2. 上传新代码（本地执行）
rsync -avz new-code/ user@server:/home/user/hotsearch/

# 3. 重启服务（服务器执行）
./manage.sh restart
```

## ⚙️ 系统要求

- Ubuntu 18.04+ / Debian 10+
- Python 3.7+
- sudo权限
- 互联网连接

## 📞 需要帮助？

查看完整部署文档：
```bash
cat DEPLOY_UBUNTU.md
```

---

**就这么简单！3分钟完成部署，爬虫每小时自动运行！** 🎉
