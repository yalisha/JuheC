#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
外部API集成模块
支持Twitter、Reddit、YouTube等国外平台数据采集

免费API配额限制：
- Twitter Trends By Location: 100次/月
- ReddAPI: 50次/月
- Social Media Master: 70次/月

调用策略：每天最多调用1次，确保一个月不超过配额
"""

import http.client
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path


class ExternalAPICrawler:
    """外部API爬虫类"""

    # RapidAPI密钥
    RAPIDAPI_KEY = "e69e6c1b6dmsh73481792f82a139p13666ajsn3c0e61b0d6d3"

    def __init__(self):
        """初始化外部API爬虫"""
        self.logger = logging.getLogger(__name__)

    def fetch_twitter_trends(self, location_id: str = "f719fcd7bc333af4b3d78d0e65893e5e") -> Optional[Dict]:
        """
        获取Twitter热门趋势

        Args:
            location_id: 地区ID（默认为美国）
                - f719fcd7bc333af4b3d78d0e65893e5e: United States (美国)
                - 1: Worldwide (全球)

        Returns:
            Twitter趋势数据
        """
        try:
            conn = http.client.HTTPSConnection("twitter-trends-by-location.p.rapidapi.com")

            headers = {
                'x-rapidapi-key': self.RAPIDAPI_KEY,
                'x-rapidapi-host': "twitter-trends-by-location.p.rapidapi.com"
            }

            conn.request("GET", f"/location/{location_id}", headers=headers)

            res = conn.getresponse()
            data = res.read()

            result = json.loads(data.decode("utf-8"))

            # 检查API响应状态
            if result.get('status') != 'SUCCESS':
                self.logger.error(f"Twitter API返回错误: {result.get('message')}")
                return None

            trending_data = result.get('trending', {})
            location_name = trending_data.get('name', 'Unknown')

            self.logger.info(f"成功获取Twitter趋势数据: {location_name}")

            # 转换为统一格式
            trends = []
            for item in trending_data.get('trends', [])[:50]:  # 取前50个
                trends.append({
                    'id': item.get('name', ''),
                    'title': item.get('name', ''),
                    'desc': f"Rank {item.get('rank', 0)}" + (f" | {item.get('domain', '')}" if item.get('domain') else ""),
                    'url': item.get('webUrl', ''),
                    'hot': item.get('postCount', 0) or 0,
                    'mobileUrl': item.get('mobileIntent', ''),
                    'rank': item.get('rank', 0),
                    'domain': item.get('domain', ''),
                    'timestamp': int(datetime.now().timestamp() * 1000)
                })

            return {
                'platform': 'Twitter',
                'location': location_name,
                'location_type': trending_data.get('locationType', 'Unknown'),
                'timestamp': datetime.now().isoformat(),
                'data': trends
            }

        except Exception as e:
            self.logger.error(f"获取Twitter数据失败: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return None
        finally:
            if 'conn' in locals():
                conn.close()

    def fetch_reddit_hot(self, subreddit: str = "popular", limit: int = 50) -> Optional[Dict]:
        """
        获取Reddit热门帖子

        注意：需要先在RapidAPI控制台查看ReddAPI的正确端点
        当前端点可能不正确，需要根据API文档调整

        Args:
            subreddit: 子版块名称（默认popular）
            limit: 获取数量

        Returns:
            Reddit热门数据
        """
        try:
            conn = http.client.HTTPSConnection("reddapi.p.rapidapi.com")

            headers = {
                'x-rapidapi-key': self.RAPIDAPI_KEY,
                'x-rapidapi-host': "reddapi.p.rapidapi.com"
            }

            # TODO: 需要根据RapidAPI文档更新正确的端点
            # 目前使用的端点返回404，需要查看API文档
            endpoint = f"/hot?subreddit={subreddit}&limit={limit}"

            conn.request("GET", endpoint, headers=headers)

            res = conn.getresponse()
            data = res.read()

            if res.status != 200:
                self.logger.error(f"Reddit API错误 {res.status}: {data.decode('utf-8')[:200]}")
                return None

            result = json.loads(data.decode("utf-8"))

            self.logger.info(f"成功获取Reddit数据")

            # 转换为统一格式（需要根据实际响应调整）
            trends = []
            if isinstance(result, dict) and 'data' in result:
                for idx, item in enumerate(result['data'].get('children', [])[:limit], 1):
                    post = item.get('data', {})
                    trends.append({
                        'id': post.get('id', ''),
                        'title': post.get('title', ''),
                        'desc': post.get('selftext', '')[:200] if post.get('selftext') else '',
                        'author': post.get('author', ''),
                        'url': f"https://reddit.com{post.get('permalink', '')}",
                        'hot': post.get('score', 0) + post.get('num_comments', 0),
                        'score': post.get('score', 0),
                        'comments': post.get('num_comments', 0),
                        'timestamp': int(post.get('created_utc', 0) * 1000)
                    })

            return {
                'platform': 'Reddit',
                'subreddit': subreddit,
                'timestamp': datetime.now().isoformat(),
                'data': trends
            }

        except Exception as e:
            self.logger.error(f"获取Reddit数据失败: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return None
        finally:
            if 'conn' in locals():
                conn.close()

    def fetch_youtube_trending(self, region: str = "US") -> Optional[Dict]:
        """
        获取YouTube趋势视频

        注意：需要先在RapidAPI控制台查看Social Media Master的正确端点
        当前端点可能不正确，需要根据API文档调整

        Args:
            region: 地区代码（US, GB, JP等）

        Returns:
            YouTube趋势数据
        """
        try:
            conn = http.client.HTTPSConnection("social-media-master.p.rapidapi.com")

            headers = {
                'x-rapidapi-key': self.RAPIDAPI_KEY,
                'x-rapidapi-host': "social-media-master.p.rapidapi.com"
            }

            # TODO: 需要根据RapidAPI文档更新正确的端点
            # 目前使用的端点返回404，需要查看API文档
            endpoint = f"/trending?platform=youtube&region={region}"

            conn.request("GET", endpoint, headers=headers)

            res = conn.getresponse()
            data = res.read()

            if res.status != 200:
                self.logger.error(f"YouTube API错误 {res.status}: {data.decode('utf-8')[:200]}")
                return None

            result = json.loads(data.decode("utf-8"))

            self.logger.info(f"成功获取YouTube数据")

            # 转换为统一格式（需要根据实际响应调整）
            trends = []
            if isinstance(result, list):
                for item in result[:50]:
                    trends.append({
                        'id': item.get('id', ''),
                        'title': item.get('title', ''),
                        'desc': item.get('description', '')[:200] if item.get('description') else '',
                        'author': item.get('channel_title', ''),
                        'url': f"https://youtube.com/watch?v={item.get('id', '')}",
                        'hot': item.get('view_count', 0),
                        'views': item.get('view_count', 0),
                        'likes': item.get('like_count', 0),
                        'timestamp': int(datetime.now().timestamp() * 1000),
                        'cover': item.get('thumbnail', '')
                    })

            return {
                'platform': 'YouTube',
                'region': region,
                'timestamp': datetime.now().isoformat(),
                'data': trends
            }

        except Exception as e:
            self.logger.error(f"获取YouTube数据失败: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return None
        finally:
            if 'conn' in locals():
                conn.close()

    def fetch_all_external(self) -> Dict:
        """
        获取所有外部平台数据

        注意：此函数会消耗API配额，建议每天最多调用1次

        Returns:
            所有外部平台数据
        """
        results = {
            'crawl_time': datetime.now().isoformat(),
            'platforms': {}
        }

        # Twitter - 唯一正常工作的API
        twitter_data = self.fetch_twitter_trends()
        if twitter_data:
            results['platforms']['Twitter'] = twitter_data

        # Reddit - 端点需要修复
        # 暂时注释掉，需要在RapidAPI控制台查看正确的端点
        # reddit_data = self.fetch_reddit_hot()
        # if reddit_data:
        #     results['platforms']['Reddit'] = reddit_data

        # YouTube - 端点需要修复
        # 暂时注释掉，需要在RapidAPI控制台查看正确的端点
        # youtube_data = self.fetch_youtube_trending()
        # if youtube_data:
        #     results['platforms']['YouTube'] = youtube_data

        self.logger.info(f"外部API爬取完成，成功 {len(results['platforms'])} 个平台")

        return results


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    crawler = ExternalAPICrawler()

    # 测试Twitter
    print("\n" + "=" * 60)
    print("测试Twitter API")
    print("=" * 60)
    twitter_data = crawler.fetch_twitter_trends()
    if twitter_data:
        print(f"✅ 获取到 {len(twitter_data['data'])} 条Twitter趋势")
        print(f"📍 地区: {twitter_data['location']} ({twitter_data['location_type']})")
        if twitter_data['data']:
            print(f"\n前3条示例:")
            for i, item in enumerate(twitter_data['data'][:3], 1):
                print(f"{i}. {item['title']} - 热度:{item['hot']} - {item['desc']}")
    else:
        print("❌ Twitter API调用失败")

    # 测试所有
    print("\n" + "=" * 60)
    print("测试所有外部API")
    print("=" * 60)
    all_data = crawler.fetch_all_external()
    print(f"总共获取 {len(all_data['platforms'])} 个平台数据")
    for platform, data in all_data['platforms'].items():
        print(f"  - {platform}: {len(data['data'])} 条数据")
