#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试微博API可用性
"""
import requests
import json
import time

API_BASE = "https://api.pearktrue.cn/api/dailyhot/"

# 测试不同的平台名称
platforms_to_test = [
    ("微博", "weibo"),
    ("微博热搜", "weibo"),
    ("新浪微博", "weibo"),
    ("Weibo", "weibo"),
]

print("=" * 60)
print("测试微博API可用性")
print("=" * 60)

for display_name, param_name in platforms_to_test:
    print(f"\n尝试平台名称: {display_name} (参数: {param_name})")
    
    try:
        url = f"{API_BASE}?title={param_name}"
        print(f"URL: {url}")
        
        response = requests.get(url, timeout=10)
        print(f"状态码: {response.status_code}")
        
        data = response.json()
        print(f"响应: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}")
        
        if data.get('code') == 200:
            print(f"✅ 成功！数据量: {len(data.get('data', []))} 条")
            break
        elif data.get('code') == 500:
            print(f"❌ 500错误 - 外部接口请求失败（可能是微博官方API临时故障）")
        else:
            print(f"❌ 其他错误: {data.get('msg')}")
            
    except Exception as e:
        print(f"❌ 请求异常: {e}")
    
    time.sleep(1)  # 避免请求过快

# 测试贴吧
print("\n" + "=" * 60)
print("测试贴吧API")
print("=" * 60)

tieba_names = ["贴吧", "百度贴吧", "tieba"]
for name in tieba_names:
    print(f"\n尝试: {name}")
    try:
        url = f"{API_BASE}?title={name}"
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data.get('code') == 200:
            print(f"✅ 成功！")
            break
        else:
            print(f"❌ {data.get('code')} - {data.get('msg')}")
    except Exception as e:
        print(f"❌ 异常: {e}")
    time.sleep(1)
