# 热搜数据采集系统

综合性热搜数据采集系统，支持16个中文平台 + 3个国际平台的实时热点数据抓取，为学术研究提供高质量时序数据。

## 🎯 研究方向

- **时间序列预测**：30分钟粒度的高频时序数据
- **算法治理**：平台推荐算法行为分析
- **舆情分析**：跨平台话题生命周期追踪
- **跨文化研究**：中外平台热点差异对比

## ✨ 核心功能

### 数据采集
- ✅ **16个中文平台**：哔哩哔哩、微博、知乎、抖音、百度、少数派、IT之家、澎湃新闻、今日头条、36氪、稀土掘金、腾讯新闻、网易新闻、英雄联盟、原神、微信读书
- ✅ **3个国际平台**：Twitter（已实现）、Reddit（待修复）、YouTube（待修复）

### 数据存储
- ✅ **SQLite数据库**：支持时序查询和数据分析
  - hotsearch_raw：原始数据
  - ranking_history：排名历史追踪（自动计算rank_change、hot_change、hot_growth_rate）
  - item_details：详情数据
  - cross_platform：跨平台关联
- ✅ **JSON文件**：向后兼容，便于数据交换

### 调度系统
- ✅ **中文平台调度器**：每30分钟采集1次（48次/天）
- ✅ **国际平台调度器**：每天采集1次（保护免费API配额）
- ✅ **systemd服务集成**：支持Ubuntu服务器自动运行

### 数据分析
- ✅ **时序查询**：查询单个热搜的历史变化
- ✅ **趋势分析**：查询持续上榜的热点话题
- ✅ **热度追踪**：查询最快上升的热搜
- ✅ **CSV导出**：导出数据用于学术分析

## 📊 数据量预估

| 时间周期 | 中文平台 | 国际平台 | 总计 | 存储容量 |
|---------|---------|---------|------|---------|
| 1天 | 38,400条 | 40条 | 38,440条 | ~32MB |
| 1周 | 268,800条 | 280条 | 269,080条 | ~224MB |
| 1月 | 1,152,000条 | 1,200条 | 1,153,200条 | ~950MB |
| 3月 | 3,456,000条 | 3,600条 | 3,459,600条 | ~2.8GB |

## 🚀 快速开始

### 1. 安装依赖

```bash
pip3 install -r requirements.txt
```

### 2. 本地测试

```bash
# 测试中文平台爬虫（单次）
python3 crawler.py

# 测试外部API（单次）
python3 external_scheduler.py --once

# 查看数据库数据
python3 -c "from database import HotSearchDatabase; db = HotSearchDatabase('data/hotsearch.db'); print(db.get_statistics())"
```

### 3. 启动定时任务

```bash
# 启动中文平台调度器（每30分钟）
python3 scheduler.py --interval 30

# 启动国际平台调度器（每天凌晨2点）
python3 external_scheduler.py --hour 2
```

## 🖥️ Ubuntu服务器部署

### 一键部署（推荐）

```bash
# 1. 克隆代码
git clone git@github.com:yalisha/JuheC.git
cd JuheC

# 2. 运行部署脚本
sudo bash deploy.sh

# 3. 启动服务
sudo systemctl start hotsearch-crawler
sudo systemctl start hotsearch-external

# 4. 查看状态
./manage.sh status
```

### 手动配置

#### 中文平台服务：`/etc/systemd/system/hotsearch-crawler.service`

```ini
[Unit]
Description=HotSearch Crawler (30min)
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/热点爬取
ExecStart=/usr/bin/python3 scheduler.py --interval 30
Restart=always
RestartSec=600

[Install]
WantedBy=multi-user.target
```

#### 国际平台服务：`/etc/systemd/system/hotsearch-external.service`

```ini
[Unit]
Description=External API Scheduler (Daily)
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/热点爬取
ExecStart=/usr/bin/python3 external_scheduler.py --hour 2
Restart=always
RestartSec=3600

[Install]
WantedBy=multi-user.target
```

#### 启动服务

```bash
sudo systemctl daemon-reload
sudo systemctl enable hotsearch-crawler hotsearch-external
sudo systemctl start hotsearch-crawler hotsearch-external
```

## 📁 项目结构

```
热点爬取/
├── crawler.py              # 中文平台爬虫
├── scheduler.py            # 中文平台调度器（30分钟）
├── external_apis.py        # 国际平台API封装
├── external_scheduler.py   # 国际平台调度器（每天1次）
├── database.py             # SQLite数据库模块
├── config.json             # 配置文件
├── requirements.txt        # Python依赖
├── run.sh                  # 快速启动脚本
├── deploy.sh               # Ubuntu部署脚本
├── manage.sh               # 服务管理脚本
├── data/                   # 数据目录
│   ├── hotsearch.db        # SQLite数据库
│   ├── latest.json         # 最新中文平台数据
│   ├── hotsearch_*.json    # 历史中文平台数据
│   ├── external_*.json     # 国际平台数据
│   └── external_api_status.json  # API调用状态
└── logs/                   # 日志目录
    ├── crawler_*.log       # 中文平台日志
    └── external_api.log    # 国际平台日志
```

## 🔧 配置说明

### config.json

```json
{
  "crawler": {
    "data_dir": "data",
    "log_dir": "logs",
    "platforms": ["哔哩哔哩", "微博", "知乎", ...]
  },
  "scheduler": {
    "interval_minutes": 30,    // 30分钟采集1次
    "run_on_startup": true,
    "save_history": true,
    "use_database": true       // 启用SQLite数据库
  },
  "request": {
    "timeout": 10,
    "retry": 3,
    "delay_between_requests": 1
  }
}
```

### 外部API配额管理 ⚠️

免费API每月调用次数限制：

| API服务 | 月度配额 | 每日策略 | 月度消耗 | 余量 |
|---------|----------|----------|----------|------|
| Twitter Trends | 100次/月 | 1次/天 | 30次/月 | 70次 |
| ReddAPI | 50次/月 | 1次/天 | 30次/月 | 20次 |
| Social Media Master | 70次/月 | 1次/天 | 30次/月 | 40次 |

**保护机制**：
- ✅ 每天最多调用1次（自动检测当天是否已调用）
- ✅ 月度统计和状态持久化
- ✅ 完整的日志记录

## 📊 数据库查询示例

### Python API

```python
from database import HotSearchDatabase

db = HotSearchDatabase('data/hotsearch.db')

# 查询单个热搜的历史
history = db.get_item_history('哔哩哔哩', 'BV1234', hours=24)

# 查询持续上榜的热点
trending = db.get_trending_topics('微博', hours=24, min_appearances=5)

# 查询最快上升的热搜
rising = db.get_fastest_rising('知乎', limit=10)

# 导出为CSV
db.export_to_csv('output.csv', platform='抖音', start_date='2025-10-01')

# 统计信息
stats = db.get_statistics()
print(f"总记录数: {stats['total_records']}")
print(f"最新记录: {stats['latest_record']}")
```

### SQL查询

```sql
-- 查询哔哩哔哩过去24小时的热度Top10
SELECT title, MAX(hot) as max_hot, 
       COUNT(*) as appearances,
       MAX(hot) - MIN(hot) as hot_growth
FROM ranking_history
WHERE platform = '哔哩哔哩'
  AND collected_at > datetime('now', '-24 hours')
GROUP BY item_id
ORDER BY max_hot DESC
LIMIT 10;

-- 查询排名上升最快的热搜
SELECT title, rank_change, hot_change, hot_growth_rate
FROM ranking_history
WHERE rank_change > 0
ORDER BY rank_change DESC
LIMIT 20;
```

## 🛠️ 服务管理

```bash
./manage.sh status      # 查看服务状态
./manage.sh start       # 启动服务
./manage.sh stop        # 停止服务
./manage.sh restart     # 重启服务
./manage.sh logs        # 查看实时日志
./manage.sh data        # 查看数据摘要
./manage.sh clean       # 清理旧数据
./manage.sh test        # 测试运行
./manage.sh uninstall   # 卸载服务
```

## 📖 文档

- [Phase 1 升级说明](PHASE1_UPGRADE.md) - 数据增强功能详解
- [Ubuntu部署文档](DEPLOY_UBUNTU.md) - 详细部署说明
- [快速部署指南](SERVER_QUICKSTART.md) - 3分钟快速部署

## ⚠️ 注意事项

1. **API配额保护**：外部API为免费层级，必须使用 `external_scheduler.py` 避免超出配额
2. **数据清理**：建议定期清理3个月以前的JSON历史文件（数据库数据可保留）
3. **网络要求**：外部API需要能访问国际网络
4. **存储空间**：建议预留至少10GB空间用于长期数据积累
5. **合规使用**：数据仅供学术研究使用，请遵守相关API使用条款

## 🔍 故障排查

### 中文平台数据为空
- 检查网络连接
- 确认API `https://api.pearktrue.cn/api/dailyhot/` 是否正常
- 查看日志：`tail -f logs/crawler_*.log`

### 外部API调用失败
- 检查RapidAPI密钥是否有效
- 确认API配额是否已用完（查看 `data/external_api_status.json`）
- 查看日志：`tail -f logs/external_api.log`

### 数据库查询慢
- 检查是否创建了索引
- 考虑按月份分表
- 定期清理过期数据

## 📈 数据示例

### 中文平台数据（latest.json）

```json
{
  "crawl_time": "2025-10-23T20:28:25",
  "platforms": {
    "哔哩哔哩": {
      "platform": "哔哩哔哩",
      "timestamp": "2025-10-23T20:28:25",
      "data": [
        {
          "id": "BV1234",
          "title": "热搜标题",
          "desc": "热搜描述",
          "url": "https://...",
          "hot": 6481884,
          "timestamp": 1729684105000
        }
      ]
    }
  }
}
```

### 国际平台数据（external_*.json）

```json
{
  "crawl_time": "2025-10-23T20:40:31",
  "platforms": {
    "Twitter": {
      "platform": "Twitter",
      "location": "United States",
      "timestamp": "2025-10-23T20:40:31",
      "data": [
        {
          "id": "Hillary",
          "title": "Hillary",
          "desc": "Rank 3 | Politics",
          "url": "https://twitter.com/search?q=%22Hillary%22",
          "hot": 68400,
          "rank": 3,
          "domain": "Politics"
        }
      ]
    }
  }
}
```

## 📜 更新日志

### v1.2.0 (2025-10-23) - Phase 1.1
- ✨ 新增外部API独立调度器
- 🔒 API配额保护机制
- ✅ Twitter API数据格式修复
- 📊 月度调用统计
- 📖 完善文档和使用指南

### v1.1.0 (2025-10-23) - Phase 1
- 🗄️ SQLite数据库存储系统
- ⚡ 30分钟采集频率
- 🌐 外部API集成框架
- 📈 时序数据自动追踪
- 🎓 学术研究数据支持

### v1.0.0 (2025-10-23)
- ✨ 初始版本发布
- ✅ 支持16个中文平台
- ⏰ 定时调度功能
- 💾 数据持久化存储

## 📄 许可证

本项目仅供学术研究使用。使用本系统采集的数据时，请遵守：
1. 相关平台的服务条款
2. API提供方的使用限制
3. 学术诚信和数据隐私保护原则

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📧 联系方式

- GitHub: [yalisha/JuheC](https://github.com/yalisha/JuheC)
- Issues: [提交问题](https://github.com/yalisha/JuheC/issues)
