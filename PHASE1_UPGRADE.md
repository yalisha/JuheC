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
