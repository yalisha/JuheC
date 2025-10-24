#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import http.client
import json

conn = http.client.HTTPSConnection("reddapi.p.rapidapi.com")

headers = {
    'x-rapidapi-key': "e69e6c1b6dmsh73481792f82a139p13666ajsn3c0e61b0d6d3",
    'x-rapidapi-host': "reddapi.p.rapidapi.com"
}

print("测试Reddit API端点: /api/scrape/top")
print("=" * 60)

conn.request("GET", "/api/scrape/top?subreddit=askreddit&limit=50", headers=headers)

res = conn.getresponse()
data = res.read()

print(f"状态码: {res.status}")
print(f"\n响应数据（前2000字符）:")
print(data.decode("utf-8")[:2000])

if res.status == 200:
    try:
        result = json.loads(data.decode("utf-8"))
        print(f"\n数据类型: {type(result)}")
        
        if isinstance(result, dict):
            print(f"数据键: {result.keys()}")
            if 'posts' in result:
                print(f"帖子数量: {len(result.get('posts', []))}")
                if result['posts']:
                    print(f"\n第一条帖子示例:")
                    first_post = result['posts'][0]
                    print(json.dumps(first_post, indent=2, ensure_ascii=False)[:1000])
        elif isinstance(result, list):
            print(f"列表长度: {len(result)}")
            if result:
                print(f"\n第一条数据示例:")
                print(json.dumps(result[0], indent=2, ensure_ascii=False)[:1000])
                
    except json.JSONDecodeError as e:
        print(f"JSON解析失败: {e}")
else:
    print(f"\n错误响应: {data.decode('utf-8')}")

conn.close()
