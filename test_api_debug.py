#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
调试外部API返回格式
"""

import http.client
import json

RAPIDAPI_KEY = "e69e6c1b6dmsh73481792f82a139p13666ajsn3c0e61b0d6d3"

print("=" * 60)
print("测试 Twitter Trends API")
print("=" * 60)
try:
    conn = http.client.HTTPSConnection("twitter-trends-by-location.p.rapidapi.com")
    headers = {
        'x-rapidapi-key': RAPIDAPI_KEY,
        'x-rapidapi-host': "twitter-trends-by-location.p.rapidapi.com"
    }
    conn.request("GET", "/location/f719fcd7bc333af4b3d78d0e65893e5e", headers=headers)
    res = conn.getresponse()
    data = res.read()

    print(f"状态码: {res.status}")
    print(f"响应头: {dict(res.headers)}")
    print(f"\n原始响应（前1000字符）:")
    print(data.decode("utf-8")[:1000])

    result = json.loads(data.decode("utf-8"))
    print(f"\n解析后的数据类型: {type(result)}")
    print(f"数据结构: {json.dumps(result, indent=2, ensure_ascii=False)[:2000]}")

    conn.close()
except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("测试 Reddit API")
print("=" * 60)
try:
    conn = http.client.HTTPSConnection("reddapi.p.rapidapi.com")
    headers = {
        'x-rapidapi-key': RAPIDAPI_KEY,
        'x-rapidapi-host': "reddapi.p.rapidapi.com",
        'Content-Type': "application/json"
    }

    # 尝试不同的端点
    endpoints = [
        "/api/v2/subreddit_hot?subreddit=all&limit=10",
        "/subreddit/all/hot?limit=10",
        "/r/all/hot.json?limit=10"
    ]

    for endpoint in endpoints:
        print(f"\n尝试端点: {endpoint}")
        try:
            conn = http.client.HTTPSConnection("reddapi.p.rapidapi.com")
            conn.request("GET", endpoint, headers=headers)
            res = conn.getresponse()
            data = res.read()

            print(f"状态码: {res.status}")
            if res.status == 200:
                print(f"原始响应（前1000字符）:")
                print(data.decode("utf-8")[:1000])

                result = json.loads(data.decode("utf-8"))
                print(f"数据类型: {type(result)}")
                print(f"数据键: {result.keys() if isinstance(result, dict) else 'not dict'}")
                break
            else:
                print(f"失败: {data.decode('utf-8')[:200]}")

            conn.close()
        except Exception as e:
            print(f"端点错误: {e}")

except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("测试 YouTube API (Social Media Master)")
print("=" * 60)
try:
    conn = http.client.HTTPSConnection("social-media-master.p.rapidapi.com")
    headers = {
        'x-rapidapi-key': RAPIDAPI_KEY,
        'x-rapidapi-host': "social-media-master.p.rapidapi.com"
    }

    # 尝试不同的端点
    endpoints = [
        "/youtube/trending?region=US",
        "/trending/youtube?country=US",
        "/api/youtube/trending"
    ]

    for endpoint in endpoints:
        print(f"\n尝试端点: {endpoint}")
        try:
            conn = http.client.HTTPSConnection("social-media-master.p.rapidapi.com")
            conn.request("GET", endpoint, headers=headers)
            res = conn.getresponse()
            data = res.read()

            print(f"状态码: {res.status}")
            if res.status == 200:
                print(f"原始响应（前1000字符）:")
                print(data.decode("utf-8")[:1000])

                result = json.loads(data.decode("utf-8"))
                print(f"数据类型: {type(result)}")
                if isinstance(result, dict):
                    print(f"数据键: {result.keys()}")
                break
            else:
                print(f"失败: {data.decode('utf-8')[:200]}")

            conn.close()
        except Exception as e:
            print(f"端点错误: {e}")

except Exception as e:
    print(f"错误: {e}")
    import traceback
    traceback.print_exc()
