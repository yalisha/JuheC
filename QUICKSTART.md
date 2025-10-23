# 快速开始指南

## 一键启动

```bash
./run.sh
```

就这么简单！程序会每小时自动抓取一次所有平台的热搜数据。

## 常用命令

### 1. 单次运行（测试用）

```bash
python3 crawler.py
```

或

```bash
python3 scheduler.py --once
```

### 2. 定时运行（每小时）

```bash
python3 scheduler.py
```

### 3. 自定义时间间隔

```bash
# 每2小时运行一次
python3 scheduler.py --interval 2

# 每30分钟运行一次（0.5小时）
python3 scheduler.py --interval 0.5
```

### 4. 查看数据

```bash
# 查看摘要
python3 view_data.py

# 查看指定平台（前10条）
python3 view_data.py --platform 哔哩哔哩

# 查看指定平台（前20条）
python3 view_data.py --platform 微博 --limit 20

# 查看所有平台的前5条
python3 view_data.py --top 5

# 查看历史记录列表
python3 view_data.py --history

# 查看指定历史文件
python3 view_data.py --file hotsearch_20251023_171149.json
```

## 数据文件位置

- **最新数据**: `data/latest.json` - 始终保持最新的一次抓取结果
- **历史数据**: `data/hotsearch_YYYYMMDD_HHMMSS.json` - 每次运行的历史记录
- **日志文件**: `logs/crawler_YYYYMM.log` - 按月分割的运行日志

## 后台运行

### macOS/Linux

```bash
# 使用 nohup
nohup python3 scheduler.py > output.log 2>&1 &

# 或使用 screen
screen -S hotsearch
python3 scheduler.py
# 按 Ctrl+A 然后按 D 分离会话
```

### 查看后台运行状态

```bash
# 查看进程
ps aux | grep scheduler

# 查看日志
tail -f logs/crawler_*.log
```

### 停止后台运行

```bash
# 找到进程ID
ps aux | grep scheduler

# 终止进程（替换 PID 为实际的进程ID）
kill PID
```

## 支持的平台（16个）

✅ 哔哩哔哩、抖音、微博、知乎、百度
✅ 少数派、IT之家、澎湃新闻、今日头条、36氪
✅ 稀土掘金、腾讯新闻、网易新闻
✅ 英雄联盟、原神、微信读书

## 故障排查

### 1. 安装依赖失败

```bash
# 使用国内镜像
pip3 install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 2. 权限错误

```bash
# 给脚本添加执行权限
chmod +x run.sh
chmod +x view_data.py
chmod +x crawler.py
chmod +x scheduler.py
```

### 3. 查看详细日志

```bash
# 查看最新日志
tail -50 logs/crawler_*.log

# 实时查看日志
tail -f logs/crawler_*.log
```

### 4. 清理旧数据

```bash
# 保留最近7天的数据，删除更早的
find data -name "hotsearch_*.json" -mtime +7 -delete

# 查看数据目录大小
du -sh data/
```

## 定制化

### 修改抓取的平台

编辑 [config.json](config.json)，在 `platforms` 数组中添加或删除平台名称。

### 修改运行间隔

1. 直接使用命令行参数：
   ```bash
   python3 scheduler.py --interval 2
   ```

2. 或编辑 [config.json](config.json)，修改 `scheduler.interval_hours` 的值。

### 关闭历史记录保存

如果只需要最新数据，不想保存历史记录：

编辑 [config.json](config.json)，将 `scheduler.save_history` 设置为 `false`。

## 性能参考

- 单次完整抓取耗时：约 20-25 秒
- 数据文件大小：约 400-500 KB/次
- 内存占用：约 30-50 MB
- CPU占用：运行时约 5-10%，待机时几乎为 0

## 技术栈

- Python 3.7+
- requests - HTTP 请求
- schedule - 定时任务
- logging - 日志系统

## 进阶使用

### 数据分析

可以使用 Python 脚本读取 JSON 数据进行分析：

```python
import json

with open('data/latest.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 统计各平台热度总和
for platform, info in data['platforms'].items():
    total_hot = sum(int(item.get('hot', 0)) for item in info['data'] if str(item.get('hot', '')).isdigit())
    print(f"{platform}: {total_hot:,}")
```

### 导出到其他格式

可以轻松将 JSON 数据转换为 CSV、Excel 等格式用于进一步分析。

## 许可与免责

- 本工具仅供学习和个人使用
- 请遵守相关网站的 robots.txt 和服务条款
- 不要过度频繁地请求 API
- 使用第三方API，请遵守其使用规范

## 问题反馈

如有问题或建议，请通过以下方式反馈：
- 查看日志文件获取详细错误信息
- 确认网络连接和 API 服务状态
- 检查 Python 版本和依赖包是否正确安装
