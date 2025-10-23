# 数据采集增强方案 - 时间序列预测与算法治理

> **研究方向**: 时间序列预测、算法治理
> **目标**: 尽可能多地采集原始数据，为后续研究做准备
> **原则**: 先采集，后分析

## 🎯 核心目标

### 研究需求
1. **时间序列预测** - 需要长期、连续、多维度的时序数据
2. **算法治理** - 需要了解平台推荐算法的行为模式
3. **舆情分析** - 需要追踪话题演变和情感变化
4. **跨平台传播** - 需要研究信息在不同平台间的流动

### 数据采集原则
- ✅ **全量采集** - 不遗漏任何有价值的数据字段
- ✅ **高频采集** - 捕捉快速变化的热点
- ✅ **多源采集** - 覆盖更多平台和数据源
- ✅ **原始保存** - 保留完整的原始数据，不做预处理
- ✅ **可追溯** - 每条数据都有时间戳和来源标记

## 📊 当前能采集到的数据（已实现）

### 基础热搜数据
```json
{
  "id": "BV1cFW2zVEUV",
  "title": "标题",
  "desc": "描述",
  "cover": "封面图URL",
  "author": "作者/来源",
  "timestamp": 1760954405000,
  "hot": 6481884,
  "url": "详情链接",
  "mobileUrl": "移动端链接"
}
```

**采集频率**: 每小时
**平台数量**: 16个
**每次数据量**: ~500KB

## 🚀 建议扩展的数据维度

### 1. 增加采集频率 ⭐⭐⭐⭐⭐

**为什么重要**:
- 时间序列预测需要密集的时间点
- 捕捉热点的爆发和衰减过程
- 研究算法的推荐更新频率

**实施方案**:
```python
# 当前: 每小时采集 (每天24次)
# 建议:
#   - 常规采集: 每30分钟 (每天48次)
#   - 重点时段: 每15分钟 (早8-10点, 晚6-11点)
#   - 突发事件: 每5-10分钟

# 配置示例
config = {
    "normal_interval": 30,  # 分钟
    "peak_hours": [(8, 10), (18, 23)],
    "peak_interval": 15,    # 分钟
    "emergency_interval": 5  # 分钟，手动触发
}
```

**数据量影响**:
- 30分钟间隔: 12MB/天 → 24MB/天
- 15分钟间隔: 12MB/天 → 48MB/天

### 2. 扩展平台覆盖 ⭐⭐⭐⭐⭐

**当前平台** (16个):
- 社交媒体: 哔哩哔哩、抖音、微博、贴吧
- 知识社区: 知乎、少数派、稀土掘金、微信读书
- 新闻媒体: IT之家、澎湃新闻、今日头条、36氪、腾讯新闻、网易新闻
- 游戏: 英雄联盟、原神

**建议新增平台**:
```python
# 社交媒体类
"小红书",      # 年轻用户为主，消费类热点
"豆瓣",        # 文艺青年，影视书籍热点
"快手",        # 下沉市场，不同用户群体

# 新闻资讯类
"虎嗅",        # 科技商业
"界面新闻",    # 财经新闻
"观察者网",    # 时事政治
"环球时报",    # 国际新闻

# 垂直领域
"虎扑",        # 体育
"NGA",         # 游戏
"雪球",        # 财经投资
"脉脉",        # 职场

# 视频平台
"优酷",        # 视频热度
"爱奇艺",      # 视频热度
"西瓜视频",    # 短视频

# 购物平台
"淘宝热搜",    # 消费趋势
"京东热搜",    # 消费趋势
```

**API支持查询**:
```python
# 测试平台是否可用
test_platforms = [
    "小红书", "豆瓣", "快手", "虎扑", "NGA",
    "雪球", "虎嗅", "界面新闻"
]

for platform in test_platforms:
    url = f"https://api.pearktrue.cn/api/dailyhot/?title={platform}"
    # 测试API响应
```

### 3. 详情页数据采集 ⭐⭐⭐⭐⭐

**为什么重要**:
- 用户互动数据是算法推荐的核心指标
- 评论区反映真实舆情
- 传播路径分析的关键数据

#### 3.1 B站详情数据

**可采集字段**:
```python
{
  # 基础信息
  "bvid": "BV号",
  "aid": "AV号",
  "title": "标题",
  "desc": "简介",
  "duration": "时长（秒）",
  "pubdate": "发布时间",

  # 互动数据 ⭐⭐⭐⭐⭐
  "view": "播放量",
  "danmaku": "弹幕数",
  "reply": "评论数",
  "favorite": "收藏数",
  "coin": "投币数",
  "share": "分享数",
  "like": "点赞数",

  # 作者信息
  "owner": {
    "mid": "UP主ID",
    "name": "UP主昵称",
    "face": "头像",
    "fans": "粉丝数"
  },

  # 分区信息
  "tid": "分区ID",
  "tname": "分区名称",

  # 标签
  "tags": ["标签1", "标签2"]
}
```

**API接口**:
```python
# B站视频信息API（官方，稳定）
url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"

# 评论API
url = f"https://api.bilibili.com/x/v2/reply?type=1&oid={aid}&pn=1&ps=20"
```

#### 3.2 微博详情数据

**可采集字段**:
```python
{
  # 基础信息
  "mid": "微博ID",
  "text": "正文",
  "created_at": "发布时间",
  "source": "来源",

  # 互动数据 ⭐⭐⭐⭐⭐
  "reposts_count": "转发数",
  "comments_count": "评论数",
  "attitudes_count": "点赞数",

  # 作者信息
  "user": {
    "id": "用户ID",
    "screen_name": "昵称",
    "followers_count": "粉丝数",
    "verified": "是否认证"
  },

  # 话题标签
  "topics": ["#话题1#", "#话题2#"]
}
```

**注意**: 微博需要登录，有反爬限制

#### 3.3 知乎详情数据

**可采集字段**:
```python
{
  # 问题信息
  "question_id": "问题ID",
  "title": "问题标题",
  "created_time": "创建时间",

  # 互动数据 ⭐⭐⭐⭐⭐
  "answer_count": "回答数",
  "follower_count": "关注人数",
  "visit_count": "浏览量",

  # 话题
  "topics": ["话题1", "话题2"]
}
```

### 4. 历史排名追踪 ⭐⭐⭐⭐⭐

**为什么重要**:
- 时间序列预测的核心数据
- 研究热点的生命周期
- 分析算法的推荐策略

**数据结构设计**:
```python
{
  "热搜内容标识": "unique_id",  # 通过title相似度匹配
  "首次出现": {
    "时间": "2025-10-23 10:00:00",
    "平台": "哔哩哔哩",
    "排名": 15,
    "热度": 10000
  },
  "历史记录": [
    {
      "时间": "2025-10-23 10:00:00",
      "排名": 15,
      "热度": 10000,
      "排名变化": "+5"
    },
    {
      "时间": "2025-10-23 11:00:00",
      "排名": 8,
      "热度": 50000,
      "排名变化": "+7"
    },
    {
      "时间": "2025-10-23 12:00:00",
      "排名": 3,
      "热度": 150000,
      "排名变化": "+5"
    }
  ],
  "统计数据": {
    "最高排名": 3,
    "最高热度": 150000,
    "持续时长": "8小时",
    "总采集次数": 8,
    "热度增长率": "+1400%"
  }
}
```

### 5. 跨平台关联数据 ⭐⭐⭐⭐

**为什么重要**:
- 研究信息跨平台传播
- 分析不同平台算法差异
- 识别营销推广行为

**数据结构**:
```python
{
  "话题标识": "网易逆水寒新游戏",
  "首次出现": {
    "平台": "哔哩哔哩",
    "时间": "2025-10-23 10:00:00"
  },
  "跨平台记录": [
    {
      "平台": "哔哩哔哩",
      "标题": "【十三元凶：生死弈】PV首曝",
      "首次出现": "10:00",
      "最高排名": 1,
      "最高热度": 6481884
    },
    {
      "平台": "微博",
      "标题": "逆水寒新游戏十三元凶",
      "首次出现": "12:00",  # 延迟2小时
      "最高排名": 5,
      "最高热度": 850000
    },
    {
      "平台": "知乎",
      "标题": "如何评价网易新游戏十三元凶",
      "首次出现": "14:00",  # 延迟4小时
      "最高排名": 8,
      "最高热度": 320000
    }
  ],
  "传播分析": {
    "总平台数": 3,
    "总热度": 7651884,
    "传播时差": "4小时",
    "主导平台": "哔哩哔哩"
  }
}
```

### 6. 元数据和上下文 ⭐⭐⭐

**时间上下文**:
```python
{
  "采集时间": "2025-10-23 10:00:00",
  "星期": "周三",
  "是否节假日": false,
  "是否周末": false,
  "时段": "上午",  # 凌晨/上午/中午/下午/傍晚/晚上/深夜
  "季节": "秋季",
  "月份": 10,
  "小时": 10
}
```

**平台元数据**:
```python
{
  "平台名称": "哔哩哔哩",
  "平台类型": "视频",
  "目标用户": "年轻人",
  "主要内容": ["游戏", "动画", "科技"],
  "日活跃用户": "3亿+",
  "热搜榜数量": 100
}
```

## 🏗️ 技术实现方案

### 方案1: 增强当前爬虫（推荐）⭐⭐⭐⭐⭐

**优点**: 基于现有API，稳定可靠，快速实现
**缺点**: 受限于API提供的字段

```python
# 1. 增加采集频率
class EnhancedScheduler:
    def __init__(self):
        self.normal_interval = 30  # 分钟
        self.peak_interval = 15
        self.peak_hours = [(8, 10), (18, 23)]

    def should_run_now(self):
        current_hour = datetime.now().hour
        is_peak = any(start <= current_hour < end
                     for start, end in self.peak_hours)
        return is_peak

# 2. 扩展平台列表
EXTENDED_PLATFORMS = [
    # 原有16个平台
    "哔哩哔哩", "抖音", "微博", "知乎", "百度",
    # ...

    # 新增平台（需要测试API支持）
    "小红书", "豆瓣", "快手", "虎扑", "NGA"
]

# 3. 保存原始数据
def save_raw_data(data):
    # 保存完整的API响应
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filepath = f"raw_data/{timestamp}_full.json"
    with open(filepath, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
```

### 方案2: 添加详情页采集（中期目标）⭐⭐⭐⭐

**B站详情采集**:
```python
class BilibiliDetailsCrawler:
    def fetch_video_stats(self, bvid):
        """获取B站视频详细数据"""
        url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"

        try:
            resp = requests.get(url, timeout=10)
            data = resp.json()

            if data['code'] == 0:
                stat = data['data']['stat']
                return {
                    'bvid': bvid,
                    'view': stat['view'],      # 播放量
                    'danmaku': stat['danmaku'], # 弹幕数
                    'reply': stat['reply'],     # 评论数
                    'favorite': stat['favorite'], # 收藏数
                    'coin': stat['coin'],       # 投币数
                    'share': stat['share'],     # 分享数
                    'like': stat['like'],       # 点赞数
                    'collected_at': datetime.now().isoformat()
                }
        except Exception as e:
            logger.error(f"获取B站详情失败: {e}")
            return None

    def fetch_top_comments(self, aid, count=20):
        """获取热门评论"""
        url = f"https://api.bilibili.com/x/v2/reply?type=1&oid={aid}&sort=2&ps={count}"
        # 实现评论采集...
```

**数据采集策略**:
- 只采集TOP 10热搜的详情（降低请求量）
- 每6小时采集一次详情
- 错峰采集，避免被限流

### 方案3: 历史数据库（立即实施）⭐⭐⭐⭐⭐

**数据库设计**:
```sql
-- 原始热搜数据表
CREATE TABLE hotsearch_raw (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform TEXT NOT NULL,
    item_id TEXT,
    title TEXT NOT NULL,
    description TEXT,
    author TEXT,
    hot INTEGER,
    url TEXT,
    rank INTEGER,
    collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    data_json TEXT  -- 完整的原始JSON
);

-- 排名历史表（时序分析核心）
CREATE TABLE ranking_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform TEXT NOT NULL,
    item_id TEXT NOT NULL,
    title TEXT NOT NULL,
    rank INTEGER NOT NULL,
    hot INTEGER NOT NULL,
    collected_at TIMESTAMP NOT NULL,
    rank_change INTEGER,  -- 排名变化
    hot_change INTEGER,   -- 热度变化
    INDEX idx_platform_time (platform, collected_at),
    INDEX idx_item_tracking (platform, item_id, collected_at)
);

-- 详情数据表
CREATE TABLE item_details (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform TEXT NOT NULL,
    item_id TEXT NOT NULL,
    view_count INTEGER,
    like_count INTEGER,
    comment_count INTEGER,
    share_count INTEGER,
    collected_at TIMESTAMP NOT NULL,
    details_json TEXT  -- 完整详情数据
);

-- 跨平台关联表
CREATE TABLE cross_platform (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id TEXT NOT NULL,  -- 话题唯一标识
    platform TEXT NOT NULL,
    item_id TEXT NOT NULL,
    title TEXT NOT NULL,
    first_seen TIMESTAMP NOT NULL,
    similarity_score FLOAT  -- 相似度分数
);
```

**实现代码**:
```python
import sqlite3
from datetime import datetime

class HotSearchDatabase:
    def __init__(self, db_path='data/hotsearch.db'):
        self.conn = sqlite3.connect(db_path)
        self.create_tables()

    def create_tables(self):
        """创建数据表"""
        # 执行上述SQL...

    def insert_hotsearch(self, platform, data):
        """插入热搜数据"""
        cursor = self.conn.cursor()

        for rank, item in enumerate(data, 1):
            # 插入原始数据
            cursor.execute('''
                INSERT INTO hotsearch_raw
                (platform, item_id, title, description, author, hot, url, rank, data_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                platform,
                item.get('id'),
                item.get('title'),
                item.get('desc'),
                item.get('author'),
                item.get('hot'),
                item.get('url'),
                rank,
                json.dumps(item, ensure_ascii=False)
            ))

            # 插入排名历史
            cursor.execute('''
                INSERT INTO ranking_history
                (platform, item_id, title, rank, hot, collected_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                platform,
                item.get('id'),
                item.get('title'),
                rank,
                item.get('hot'),
                datetime.now()
            ))

        self.conn.commit()

    def get_item_history(self, platform, item_id, days=7):
        """查询单个热搜的历史数据"""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT rank, hot, collected_at
            FROM ranking_history
            WHERE platform = ? AND item_id = ?
            AND collected_at >= datetime('now', '-' || ? || ' days')
            ORDER BY collected_at
        ''', (platform, item_id, days))

        return cursor.fetchall()
```

## 📦 数据存储方案

### 目录结构
```
热点爬取/
├── data/
│   ├── database/
│   │   └── hotsearch.db          # SQLite数据库
│   ├── raw_json/                 # 原始JSON备份
│   │   ├── 2025/10/23/
│   │   │   ├── 10_00_full.json
│   │   │   ├── 11_00_full.json
│   │   │   └── ...
│   ├── details/                  # 详情页数据
│   │   ├── bilibili/
│   │   └── weibo/
│   └── exports/                  # 导出数据
│       ├── daily/
│       └── weekly/
└── logs/
    └── crawler_202510.log
```

### 数据规模估算

**基础热搜数据**:
- 当前频率（1小时）: 12MB/天
- 30分钟频率: 24MB/天
- 15分钟频率: 48MB/天

**详情页数据** (TOP10, 6小时一次):
- B站详情: 4次/天 × 10��� × 16平台 ≈ 2MB/天
- 评论数据: 额外 10MB/天

**总计**:
- 保守估计: 30MB/天 ≈ 1GB/月
- 完整方案: 60MB/天 ≈ 2GB/月
- 一年数据: 12-24GB

**建议存储**: 预留50GB空间

## 🚀 实施计划

### Phase 1: 基础增强（1周内）⭐⭐⭐⭐⭐

**目标**: 提高数据量和质量

1. **数据库实现**
   ```bash
   - 设计SQLite数据库结构
   - 实现数据插入和查询
   - 修改爬虫对接数据库
   ```

2. **增加采集频率**
   ```bash
   - 修改scheduler为30分钟间隔
   - 实现peak时段15分钟采集
   - 配置文件支持自定义间隔
   ```

3. **测试新平台**
   ```bash
   - 测试小红书、豆瓣等新平台API
   - 添加可用平台到配置
   - 更新平台列表
   ```

### Phase 2: 详情采集（2-4周）⭐⭐⭐⭐

**目标**: 采集互动数据

1. **B站详情采集**
   ```bash
   - 实现B站API详情获取
   - TOP10热搜详情采集
   - 6小时间隔采集
   ```

2. **数据关联**
   ```bash
   - 详情数据与热搜关联
   - 时序数据对齐
   - 跨平台匹配逻辑
   ```

### Phase 3: 持续运行（长期）⭐⭐⭐⭐⭐

**目标**: 积累数据

1. **稳定运行**
   ```bash
   - 服务器部署
   - 监控和告警
   - 自动重启机制
   ```

2. **数据备份**
   ```bash
   - 每日数据备份
   - 数据库定期导出
   - 云端同步
   ```

3. **建议至少运行3-6个月** 以获得有价值的时序数据

## 💡 关键建议

### 1. 立即开始积累数据
- 🔥 **现在就部署到服务器**
- 🔥 **连续运行3-6个月**
- 时间序列预测需要足够长的历史数据

### 2. 数据完整性优先
- 保存完整的原始JSON
- 不要过滤或筛选数据
- 记录所有采集失败的情况

### 3. 采集频率权衡
- 30分钟是性价比最高的频率
- 可以捕捉到大部分热点变化
- 不会对API造成过大压力

### 4. 重点平台深度采集
- B站、微博、知乎的详情数据最有价值
- 可以开始时只采集这3个平台的详情
- 逐步扩展到其他平台

### 5. 伦理和合规
- 遵守robots.txt
- 控制请求频率
- 不采集用户隐私数据
- 数据仅用于学术研究

## 📊 数据价值评估

### 时间序列预测
- ⭐⭐⭐⭐⭐ 排名历史数据
- ⭐⭐⭐⭐⭐ 热度变化数据
- ⭐⭐⭐⭐ 时间上下文数据
- ⭐⭐⭐⭐ 跨平台传播数据

### 算法治理
- ⭐⭐⭐⭐⭐ 排名算法行为
- ⭐⭐⭐⭐⭐ 推荐更新频率
- ⭐⭐⭐⭐ 跨平台差异
- ⭐⭐⭐⭐ 内容分类偏好

### 舆情分析
- ⭐⭐⭐⭐⭐ 话题演变轨迹
- ⭐⭐⭐⭐ 用户互动数据
- ⭐⭐⭐⭐ 跨平台传播
- ⭐⭐⭐ 评论情感数据

## 🎯 下一步行动

1. **确认技术方案**
   - 是否同意30分钟采集频率？
   - 是否需要详情页采集？
   - 需要哪些新平台？

2. **开始实施**
   - 我可以帮你实现Phase 1（数据库+增频）
   - 部署到Ubuntu服务器
   - 开始长期数据积累

3. **设定目标**
   - 计划运行多久？（建议≥3个月）
   - 预期数据量？
   - 存储空间准备好了吗？

---

**你想先实现哪些功能？我可以立即开始编写代码！**
