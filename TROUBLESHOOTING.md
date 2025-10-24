# 故障排查指南

本文档记录常见问题和解决方案。

## 常见问题

### 1. 微博API返回500错误 ⚠️

**错误信息**：
```
【微博】API返回异常: {'code': 500, 'msg': '外部接口请求失败'}
```

**原因**：
- 微博官方API临时性故障
- API服务提供商（pearktrue.cn）的微博数据源不稳定

**解决方案**：
- ✅ 等待几分钟后自动重试（爬虫有3次重试机制）
- ✅ 大多数情况下会在下一次采集时恢复正常
- ⚠️ 如果持续失败超过24小时，可能需要联系API服务商

**验证方法**：
```bash
# 手动测试微博API
curl "https://api.pearktrue.cn/api/dailyhot/?title=微博"
```

**实际影响**：
- 微博偶尔失败不影响其他16个中文平台的数据采集
- 系统会继续采集其他平台数据

### 2. 百度贴吧平台名称错误 ✅ 已修复

**错误信息**：
```
【贴吧】API返回异常: {'code': 400, 'msg': '不支持的平台名称，请检查 title 参数'}
```

**原因**：
- API要求的平台名称是"百度贴吧"而不是"贴吧"

**解决方案**：
- ✅ 已在 config.json 和 crawler.py 中修复
- ✅ 更新平台名称："贴吧" → "百度贴吧"

**修复文件**：
- `config.json` - line 23
- `crawler.py` - line 44

### 3. Twitter API临时性错误 ⚠️

**错误信息**：
```
Twitter API返回错误: ac-s7leddh-lb.levwxae.mongodb.net
```

**原因**：
- Twitter Trends API的后端MongoDB数据库连接问题
- RapidAPI的Twitter服务临时性故障

**解决方案**：
- ✅ 等待API服务恢复（通常几小时内）
- ✅ 每天1次调用策略确保不会错过太多数据
- ℹ️ Reddit数据仍然正常采集

**实际影响**：
- 当天Twitter数据缺失，但不影响Reddit和中文平台
- 次日调用时通常会恢复正常

### 4. 外部API配额超限 🚫

**错误信息**：
```
You have exceeded the MONTHLY quota
```

**原因**：
- 免费API配额用完（Twitter: 100次/月, Reddit: 50次/月）

**预防措施**：
- ✅ 使用 `external_scheduler.py` 限制每天1次调用
- ✅ 自动检测当天是否已调用（防止重复）
- ✅ 状态文件监控：`data/external_api_status.json`

**检查配额使用**：
```bash
cat data/external_api_status.json
```

**应急方案**：
- 等到下个月配额重置
- 或者升级到付费计划（不推荐，免费配额足够）

### 5. 数据库写入失败 ❌

**错误信息**：
```
database is locked
```

**原因**：
- 多个进程同时写入SQLite数据库

**解决方案**：
- ✅ 确保只运行一个爬虫实例
- ✅ 检查是否有卡住的进程：`ps aux | grep crawler`
- ✅ 杀死重复进程：`pkill -f crawler.py`

**预防措施**：
- 使用systemd服务管理（自动防止重复启动）

### 6. JSON解析错误 ⚠️

**错误信息**：
```
JSONDecodeError: Expecting value: line 1 column 1
```

**原因**：
- API返回了非JSON格式的响应（通常是HTML错误页面）
- 网络请求超时

**解决方案**：
- ✅ 爬虫会自动重试3次
- ✅ 检查网络连接
- ✅ 查看日志获取详细错误信息

## 平台可用性状态

### 中文平台（17个）

| 平台 | 状态 | 平均数据量 | 备注 |
|------|------|-----------|------|
| 哔哩哔哩 | ✅ 稳定 | 100条 | - |
| 抖音 | ✅ 稳定 | 100条 | - |
| 微博 | ⚠️ 偶尔500 | 52条 | 临时性故障，通常会恢复 |
| 知乎 | ✅ 稳定 | 30条 | - |
| 百度 | ✅ 稳定 | 50条 | - |
| 少数派 | ✅ 稳定 | 40条 | - |
| IT之家 | ✅ 稳定 | 48条 | - |
| 澎湃新闻 | ✅ 稳定 | 20条 | - |
| 今日头条 | ✅ 稳定 | 50条 | - |
| 36氪 | ✅ 稳定 | 50条 | - |
| 稀土掘金 | ✅ 稳定 | 50条 | - |
| 腾讯新闻 | ✅ 稳定 | 50条 | - |
| 网易新闻 | ✅ 稳定 | 40条 | - |
| 英雄联盟 | ✅ 稳定 | 30条 | - |
| 原神 | ✅ 稳定 | 20条 | - |
| 微信读书 | ✅ 稳定 | 20条 | - |
| 百度贴吧 | ✅ 已修复 | 30条 | 之前名称错误，已修复 |

**总计**：17个平台，16个稳定，1个偶尔故障（微博）

### 国际平台（2个）

| 平台 | 状态 | 平均数据量 | 备注 |
|------|------|-----------|------|
| Twitter | ⚠️ 偶尔故障 | 40条 | MongoDB连接问题，通常会恢复 |
| Reddit | ✅ 稳定 | 50条 | 最稳定的国际平台 |

**总计**：2个平台，1个稳定，1个偶尔故障（Twitter）

## 日志查看

### 查看最新日志
```bash
# 中文平台日志
tail -f logs/crawler_$(date +%Y%m).log

# 外部API日志
tail -f logs/external_api.log
```

### 查看错误日志
```bash
# 只看错误和警告
grep -E "ERROR|WARNING" logs/crawler_$(date +%Y%m).log | tail -20
```

### 查看特定平台
```bash
# 查看微博相关日志
grep "微博" logs/crawler_$(date +%Y%m).log | tail -10

# 查看Twitter相关日志
grep "Twitter" logs/external_api.log | tail -10
```

## 性能优化

### 如果爬虫运行缓慢

1. **检查网络连接**
```bash
ping api.pearktrue.cn
```

2. **调整请求间隔**
```json
// config.json
{
  "request": {
    "delay_between_requests": 0.5  // 从1秒减少到0.5秒
  }
}
```

3. **减少重试次数**
```json
{
  "request": {
    "retry": 2  // 从3次减少到2次
  }
}
```

### 如果数据库查询缓慢

```bash
# 重建数据库索引
sqlite3 data/hotsearch.db "REINDEX;"

# 清理数据库
sqlite3 data/hotsearch.db "VACUUM;"
```

## 数据恢复

### 恢复误删的数据

```bash
# 从JSON文件重新导入数据库
python3 -c "
from database import HotSearchDatabase
import json

db = HotSearchDatabase('data/hotsearch.db')

# 读取JSON文件
with open('data/hotsearch_20251023_120000.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# 重新插入数据（这里需要根据实际情况调整）
for platform, pdata in data['platforms'].items():
    db.save_platform_data(platform, pdata)
"
```

## 联系支持

如果遇到以上未列出的问题：

1. **查看完整日志**：`logs/crawler_*.log` 和 `logs/external_api.log`
2. **检查GitHub Issues**：[提交问题](https://github.com/yalisha/JuheC/issues)
3. **API服务商**：https://api.pearktrue.cn/

## 更新记录

- **2025-10-24**: 添加微博500错误、Twitter临时故障说明
- **2025-10-24**: 修复百度贴吧平台名称错误
- **2025-10-23**: 初始版本
