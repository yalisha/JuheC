# Phase 1 数据增强升级说明

## 🎉 升级完成！

已成功实现Phase 1的所有核心功能，为时间序列预测和算法治理研究提供更强大的数据采集能力。

## ✨ 新增功能

### 1. SQLite数据库存储 ⭐⭐⭐⭐⭐

**替代JSON文件存储，支持高效的时序查询和数据分析**

#### 数据库表结构：
- **hotsearch_raw** - 原始热搜数据（完整JSON保留）
- **ranking_history** - 排名历史追踪（时序分析核心）
- **item_details** - 详情数据（播放量、点赞等）
- **cross_platform** - 跨平台关联

#### 核心字段：
```python
{
    "platform": "哔哩哔哩",
    "rank_position": 1,
    "hot": 6481884,
    "collected_at": "2025-10-23 20:28:25",
    "rank_change": +5,        # 排名变化
    "hot_change": +1500000,   # 热度变化
    "hot_growth_rate": 30.5   # 热度增长率(%)
}
```

#### 时序分析功能：
```python
from database import get_database

with get_database() as db:
    # 查询单个热搜的历史
    history = db.get_item_history('哔哩哔哩', 'BV1234', hours=24)

    # 查询持续上榜的热点
    trending = db.get_trending_topics('哔哩哔哩', hours=24, min_appearances=5)

    # 查询最快上升的热搜
    rising = db.get_fastest_rising('哔哩哔哩', limit=10)

    # 导出为CSV
    db.export_to_csv('output.csv', platform='微博', start_date='2025-10-01')
```

### 2. 30分钟采集频率 ⭐⭐⭐⭐⭐

**从每小时1次提升到每30分钟1次，数据密度翻倍**

#### 配置方式：
```bash
# 方法1：使用配置文件
# 编辑 config.json:
{
  "scheduler": {
    "interval_minutes": 30  # 改为30分钟
  }
}

# 方法2：命令行参数
python3 scheduler.py --interval 30  # 30分钟间隔
python3 scheduler.py --interval 15  # 15分钟间隔（高峰期）
```

#### 数据量提升：
- 之前: 24次/天
- 现在: 48次/天
- 数据量: 12MB/天 → 24MB/天

### 3. 外部API集成 ⭐⭐⭐⭐

**支持Twitter、Reddit、YouTube等国外平台数据采集**

#### 新增模块：`external_apis.py`

```python
from external_apis import ExternalAPICrawler

crawler = ExternalAPICrawler()

# Twitter趋势
twitter_data = crawler.fetch_twitter_trends()

# Reddit热门
reddit_data = crawler.fetch_reddit_hot(subreddit='all')

# YouTube趋势（需要API调整）
# youtube_data = crawler.fetch_youtube_trending()

# 一次性获取所有
all_external = crawler.fetch_all_external()
```

#### API配置：
已集成RapidAPI的3个服务：
- Twitter Trends By Location
- ReddAPI
- Social Media Master

**注意**: 外部API目前默认关闭，需要手动启用：
```python
crawler = HotSearchCrawler(use_external_apis=True)
```

### 4. 自动排名追踪 ⭐⭐⭐⭐⭐

**自动计算每条热搜的排名和热度变化**

#### 追踪指标：
- `rank_change` - 排名变化（+5表示上升5位）
- `hot_change` - 热度变化（绝对值）
- `hot_growth_rate` - 热度增长率（百分比）

#### 查询示例：
```python
# 获取最快上升的热搜
rising = db.get_fastest_rising('哔哩哔哩', limit=10)

for item in rising:
    print(f"{item['title']}")
    print(f"  排名变化: +{item['rank_change']}")
    print(f"  热度增长: {item['hot_growth_rate']:.1f}%")
```

## 📊 测试结果

### 数据库性能：
```
✅ 单次爬取: 16个平台，693条原始数据，700条历史记录
✅ 数据库大小: 1.2MB
✅ 耗时: 20.89秒
✅ 插入成功率: 100%
```

### 数据统计：
```
总记录数: 693
历史记录数: 700
最新记录: 2025-10-23 20:28:25
```

## 🚀 使用方法

### 方法1：继续使用现有方式（自动启用数据库）

```bash
# 单次运行
python3 scheduler.py --once

# 定时运行（30分钟间隔）
python3 scheduler.py --interval 30

# 或使用脚本
./run.sh
```

**现在会自动：**
- ✅ 保存到SQLite数据库
- ✅ 保存到JSON文件（兼容）
- ✅ 追踪排名变化
- ✅ 每30分钟运行一次

### 方法2：Python编程接口

```python
from crawler import HotSearchCrawler
from database import get_database

# 创建爬虫（启用所有新功能）
crawler = HotSearchCrawler(
    use_database=True,           # 使用数据库
    use_external_apis=False      # 暂不启用外部API
)

# 运行一次
crawler.run_once()

# 查询数据库
with get_database() as db:
    # 获取统计信息
    stats = db.get_statistics()
    print(f"总记录数: {stats['total_records']}")

    # 查询热搜历史
    history = db.get_item_history('哔哩哔哩', 'BV1234', hours=24)

    # 导出数据
    db.export_to_csv('hotsearch_data.csv', platform='微博')
```

## 📁 文件结构

```
热点爬取/
├── database.py          ⭐ 新增 - 数据库模块
├── external_apis.py     ⭐ 新增 - 外部API模块
├── crawler.py           ✏️ 升级 - 集成数据库
├── scheduler.py         ✏️ 升级 - 支持分钟间隔
├── config.json          ✏️ 升级 - 新增配置项
├── data/
│   ├── hotsearch.db    ⭐ 新增 - SQLite数据库
│   ├── latest.json      (保留)
│   └── hotsearch_*.json (保留)
└── logs/
    └── crawler_*.log
```

## 🔧 配置说明

### config.json 新增配置：

```json
{
  "scheduler": {
    "interval_minutes": 30,      // 改为分钟间隔
    "use_database": true          // 启用数据库
  }
}
```

## 📈 数据规模估算

### 基础配置（30分钟间隔）：
- 每次采集: 16平台 × 平均45条 = 720条
- 每天: 48次 × 720条 = 34,560条
- 数据库大小: 约50MB/天（包含索引）
- 每月: ~1.5GB
- 每年: ~18GB

### 建议：
- 定期清理3个月以前的数据
- 或导出为CSV后删除数据库记录
- 保留50GB空间充足

## 🎯 学术研究价值

### 1. 时间序列预测 ⭐⭐⭐⭐⭐
- ✅ 30分钟粒度的时序数据
- ✅ 完整的排名历史
- ✅ 热度变化率追踪
- ✅ 可导出为CSV用于机器学习

### 2. 算法治理研究 ⭐⭐⭐⭐⭐
- ✅ 观察平台推荐算法行为
- ✅ 分析排名更新频率
- ✅ 研究热度计算机制
- ✅ 跨平台算法对比

### 3. 舆情分析 ⭐⭐⭐⭐
- ✅ 话题生命周期追踪
- ✅ 热点演变路径
- ✅ 跨平台传播分析

## ⚠️ 注意事项

### 1. 外部API
- 默认关闭（需要测试和调整）
- RapidAPI有请求限制
- 建议先测试再启用

### 2. 数据库维护
```python
# 定期备份
cp data/hotsearch.db data/backup_$(date +%Y%m%d).db

# 查看数据库大小
du -h data/hotsearch.db

# 清理旧数据（保留最近30天）
DELETE FROM ranking_history WHERE collected_at < datetime('now', '-30 days');
VACUUM;
```

### 3. 性能优化
- 数据库已建立索引，查询效率高
- 建议每月清理一次旧数据
- CSV导出适合大规模分析

## 🔜 下一步计划（Phase 2）

1. **B站详情数据采集** - 播放量、点赞、评论等
2. **情感分析** - 使用SnowNLP分析标题情感
3. **跨平台关联** - 自动识别相同话题
4. **数据可视化** - 生成趋势图表
5. **日报/周报** - 自动生成分析报告

## 📝 更新日志

### v1.2.0 (2025-10-23) - Phase 1完成 ⭐

**核心功能：**
- ✅ SQLite数据库存储和时序追踪
- ✅ 30分钟采集频率
- ✅ 外部API集成框架（Twitter、Reddit）
- ✅ 自动排名变化计算
- ✅ CSV导出功能
- ✅ 数据库查询API

**兼容性：**
- ✅ 向后兼容，保留JSON文件存储
- ✅ 现有脚本无需修改
- ✅ 平滑升级

---

**现在可以开始长期运行，积累宝贵的时序数据！** 🚀

## 📝 Phase 1.1 更新 - 外部API配额管理 (2025-10-23)

### 免费API配额限制 ⚠️

您的外部API为免费层级，每个API每月有调用次数限制：

| API服务 | 月度配额 | 每日策略 | 月度消耗 |
|---------|----------|----------|----------|
| Twitter Trends By Location | 100次/月 | 1次/天 | 30次/月 ✅ |
| ReddAPI | 50次/月 | 1次/天 | 30次/月 ✅ |
| Social Media Master (YouTube) | 70次/月 | 1次/天 | 30次/月 ✅ |

**调用策略**：每天最多调用1次，确保一个月不超过最低配额(50次)，留有20次余量用于调试和测试。

### 外部API独立调度器 🕐

为了避免超出免费配额，创建了独立的外部API调度器：

#### 文件：`external_scheduler.py`

**核心功能**：
- ✅ 每天自动调用1次（默认凌晨2点）
- ✅ 自动检测当天是否已调用（防止重复调用）
- ✅ 月度调用次数统计
- ✅ 状态文件记录（`data/external_api_status.json`）
- ✅ 数据保存到独立文件（`data/external_YYYYMMDD_HHMMSS.json`）

#### 使用方法：

**1. 测试模式（只执行一次）**
```bash
python3 external_scheduler.py --once
```

**2. 定时运行（默认凌晨2点）**
```bash
python3 external_scheduler.py
```

**3. 自定义执行时间**
```bash
# 每天凌晨3点执行
python3 external_scheduler.py --hour 3

# 每天中午12点执行
python3 external_scheduler.py --hour 12
```

**4. 后台运行（推荐）**
```bash
# 使用nohup
nohup python3 external_scheduler.py > logs/external_api.log 2>&1 &

# 或使用screen
screen -S external_api
python3 external_scheduler.py
# 按 Ctrl+A 然后 D 分离
```

#### 系统集成：

**方法1：独立运行**（推荐）
```bash
# 主爬虫：每30分钟运行一次（中文平台）
python3 scheduler.py --interval 30

# 外部API：每天运行一次（外国平台）
python3 external_scheduler.py --hour 2
```

**方法2：systemd服务**（Ubuntu服务器）

创建 `/etc/systemd/system/hotsearch-external.service`:

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

启动服务：
```bash
sudo systemctl enable hotsearch-external
sudo systemctl start hotsearch-external
sudo systemctl status hotsearch-external
```

### 外部API数据格式修复 ✅

#### Twitter API - 已修复 ✅

**问题**：原来的数据解析路径不正确，导致返回空数组  
**修复**：更新解析路径为 `result['trending']['trends']`  
**测试结果**：✅ 成功获取40条Twitter趋势数据

**数据格式**：
```json
{
  "platform": "Twitter",
  "location": "United States",
  "location_type": "Country",
  "timestamp": "2025-10-23T20:40:31",
  "data": [
    {
      "id": "#oufc",
      "title": "#oufc",
      "desc": "Rank 1",
      "url": "https://twitter.com/search?q=%22%23oufc%22",
      "hot": 0,
      "rank": 1,
      "domain": "",
      "timestamp": 1729708831000
    },
    {
      "id": "Hillary",
      "title": "Hillary",
      "desc": "Rank 3 | Politics",
      "url": "https://twitter.com/search?q=%22Hillary%22",
      "hot": 68400,
      "rank": 3,
      "domain": "Politics",
      "timestamp": 1729708831000
    }
  ]
}
```

#### Reddit API - 待修复 ⏸️

**状态**：API端点不存在，需要在RapidAPI控制台查看正确端点  
**错误信息**：`Endpoint '/hot' does not exist`  
**解决方案**：登录 RapidAPI → 查看 ReddAPI 文档 → 更新正确端点

#### YouTube API - 待修复 ⏸️

**状态**：API端点不存在，需要在RapidAPI控制台查看正确端点  
**错误信息**：`Endpoint '/trending' does not exist`  
**解决方案**：登录 RapidAPI → 查看 Social Media Master 文档 → 更新正确端点

### 配额监控和保护 📊

#### 状态文件：`data/external_api_status.json`

```json
{
  "last_crawl_time": "2025-10-23T20:40:31",
  "total_calls_this_month": 1
}
```

**保护机制**：
- ✅ 每日限制检查（同一天只允许调用1次）
- ✅ 月度统计（自动重置到下个月）
- ✅ 状态持久化（程序重启不影响限制）
- ✅ 日志记录（所有调用都有日志可查）

**预期月度消耗**：
- 正常运行：30次/月（每月30天）
- 余量保留：20次（用于调试和补漏）
- 安全余量：67%（20/30）

### 数据采集计划 📈

#### 中文平台（现有系统）
- **频率**：每30分钟1次
- **平台数**：16个（哔哩哔哩、微博、知乎、抖音等）
- **日数据量**：48次 × 16平台 × 50条/平台 ≈ 38,400条/天
- **存储方式**：SQLite数据库 + JSON文件

#### 外国平台（新增系统）
- **频率**：每天1次
- **平台数**：1个（Twitter，Reddit/YouTube待修复）
- **日数据量**：1次 × 1平台 × 40条/平台 = 40条/天
- **存储方式**：JSON文件

#### 总数据量预估

| 时间周期 | 中文平台 | 外国平台 | 总计 |
|---------|---------|---------|------|
| 1天 | 38,400条 | 40条 | 38,440条 |
| 1周 | 268,800条 | 280条 | 269,080条 |
| 1月 | 1,152,000条 | 1,200条 | 1,153,200条 |
| 3月 | 3,456,000条 | 3,600条 | 3,459,600条 |

**存储容量预估**：
- SQLite数据库：~150MB/月
- JSON文件：~800MB/月
- 总计：~950MB/月

### 学术研究价值 🎓

#### 1. 时间序列预测
- **中文平台**：30分钟粒度，高频时序数据，适合短期预测模型
- **外国平台**：日粒度，长期趋势数据，适合趋势分析

#### 2. 算法治理
- **跨平台对比**：中外平台推荐算法行为差异分析
- **热点生命周期**：从出现到消失的完整轨迹追踪

#### 3. 舆情分析
- **话题传播**：热点在不同平台间的传播路径
- **情感演化**：结合后续情感分析的时序变化

#### 4. 跨文化研究
- **热点差异**：中文社交平台 vs 英文社交平台的关注点差异
- **传播速度**：不同文化背景下热点的传播速度对比

### 后续优化建议 🔮

1. **Reddit/YouTube API修复** - 需要查看RapidAPI文档更新正确端点
2. **数据库优化** - 添加索引、分区表提升查询性能
3. **数据清洗** - 去重、标准化、质量控制
4. **可视化看板** - 实时热点趋势可视化
5. **情感分析** - Phase 2：集成情感分析模型

---

**更新时间**：2025-10-23  
**版本**：Phase 1.1 - 配额管理与调度优化

---

## 🎉 Phase 1.2 更新 - Reddit API修复 (2025-10-23)

### Reddit API端点修复 ✅

**问题**：原来的端点 `/hot` 返回404错误  
**解决方案**：使用正确的端点 `/api/scrape/top`  
**测试结果**：✅ 成功获取50条Reddit热门帖子

### Reddit数据格式

**API端点**：
```
GET /api/scrape/top?subreddit={subreddit}&limit={limit}
```

**支持的子版块**：
- `all` - 全站热门（默认）
- `askreddit` - 问答社区
- `worldnews` - 世界新闻
- `funny` - 搞笑内容
- `gaming` - 游戏讨论
- `technology` - 科技新闻
- 等其他任意公开子版块

**数据格式**：
```json
{
  "platform": "Reddit",
  "subreddit": "all",
  "timestamp": "2025-10-23T21:02:49",
  "data": [
    {
      "id": "1odoqkr",
      "title": "My neighbor sent me a text forcing me to pay...",
      "desc": "",
      "author": "throwaway_reddi",
      "subreddit": "AskReddit",
      "url": "https://reddit.com/r/AskReddit/comments/1odoqkr",
      "hot": 82995,
      "score": 82995,
      "comments": 16001,
      "upvote_ratio": 0.94,
      "created": 1761176710.0,
      "timestamp": 1761176710000
    }
  ]
}
```

**字段说明**：
- `hot`: 热度（等于score，用于统一接口）
- `score`: 点赞数（ups）
- `comments`: 评论数
- `upvote_ratio`: 点赞比率（0-1之间）
- `created`: 发布时间（Unix时间戳）

### 外部API完整集成状态

| API服务 | 状态 | 数据量 | 测试结果 |
|---------|------|--------|---------|
| Twitter Trends By Location | ✅ 正常 | 40条/次 | 美国热门趋势 |
| ReddAPI | ✅ 正常 | 50条/次 | 全站热门帖子 |
| Social Media Master (YouTube) | ⏸️ 待修复 | - | 端点404 |

**当前采集能力**：
- 每天1次调用
- 2个平台（Twitter + Reddit）
- 90条数据/次
- 月度数据：2,700条（90条 × 30天）

**API配额消耗**（2个平台）：
- Twitter: 30次/月（余量70次）
- Reddit: 30次/月（余量20次）
- 总余量：50%安全边际

### 数据采集总结

#### 中文平台
- **频率**：每30分钟
- **平台数**：16个
- **日数据量**：38,400条
- **月数据量**：1,152,000条

#### 国际平台
- **频率**：每天1次
- **平台数**：2个（Twitter + Reddit）
- **日数据量**：90条（40条Twitter + 50条Reddit）
- **月数据量**：2,700条

#### 总计
- **日数据量**：38,490条
- **月数据量**：1,154,700条
- **存储容量**：~950MB/月

### 测试结果

```bash
$ python3 external_scheduler.py --once

📝 测试模式 - 只执行一次
2025-10-23 21:02:49 - INFO - 🌐 开始外部API爬取...
2025-10-23 21:02:51 - INFO - 成功获取Twitter趋势数据: United States
2025-10-23 21:03:00 - INFO - 成功获取Reddit数据: r/all
2025-10-23 21:03:00 - INFO - 外部API爬取完成，成功 2 个平台
2025-10-23 21:03:00 - INFO - ✅ 外部API爬取完成
2025-10-23 21:03:00 - INFO -    平台数: 2
2025-10-23 21:03:00 - INFO -    总条目: 90
2025-10-23 21:03:00 - INFO -    本月调用: 1 次
2025-10-23 21:03:00 - INFO -    保存到: data/external_20251023_210300.json
```

**数据示例**：

**Twitter数据**：
1. #oufc - 热度:0 - Rank 1
2. #swfc - 热度:4041 - Rank 2
3. Hillary - 热度:68400 - Rank 3 | Politics

**Reddit数据**：
1. My neighbor sent me a text... (分数:82995, 评论:16001)
2. Oddly Affirming (分数:75495, 评论:846)
3. Only cat owners know... (分数:68660, 评论:412)

### 学术研究价值增强 🎓

#### 1. 跨文化对比研究
- **中文社交平台**：微博、知乎、抖音、B站等16个平台
- **英文社交平台**：Twitter（热门标签）、Reddit（社区讨论）
- **对比维度**：
  - 热点话题差异
  - 传播速度对比
  - 用户参与度（评论、点赞）
  - 话题生命周期

#### 2. 时间序列预测
- **中文平台**：30分钟粒度，适合短期预测
- **国际平台**：日粒度，适合趋势分析
- **预测目标**：
  - 热度变化预测
  - 排名变化预测
  - 评论数增长预测

#### 3. 算法治理研究
- **推荐算法差异**：
  - 中文平台：内容审核、流量分配
  - Reddit：社区投票机制、upvote_ratio分析
  - Twitter：趋势算法、地域性热点
- **研究方向**：
  - 算法透明度
  - 信息茧房效应
  - 平台治理机制

#### 4. 舆情分析
- **跨平台传播**：同一话题在不同平台的传播路径
- **情感演化**：结合后续情感分析的时序变化
- **公众关注度**：热度、评论数、点赞数的综合分析

### 后续优化方向 🔮

1. **YouTube API修复** - 查看Social Media Master API文档更新端点
2. **多地区支持** - Twitter支持不同国家/地区的趋势
3. **更多子版块** - Reddit支持多个子版块组合采集
4. **数据清洗** - 去重、标准化、质量控制
5. **情感分析** - Phase 2：集成情感分析模型

---

**更新时间**：2025-10-23  
**版本**：Phase 1.2 - Reddit API修复  
**状态**：✅ 2/3个外部API正常工作
