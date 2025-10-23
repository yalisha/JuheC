#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
外部API集成模块
支持Twitter、Reddit、YouTube等国外平台数据采集
"""

import http.client
import json
import logging
from typing import Dict, List, Optional
from datetime import datetime


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
            location_id: 地区ID（默认为全球）

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

            self.logger.info(f"成功获取Twitter趋势数据")

            # 转换为统一格式
            trends = []
            if isinstance(result, list) and len(result) > 0:
                for item in result[0].get('trends', [])[:50]:  # 取前50个
                    trends.append({
                        'id': item.get('name', ''),
                        'title': item.get('name', ''),
                        'desc': item.get('query', ''),
                        'url': item.get('url', ''),
                        'hot': item.get('tweet_volume', 0) or 0,
                        'timestamp': int(datetime.now().timestamp() * 1000)
                    })

            return {
                'platform': 'Twitter',
                'timestamp': datetime.now().isoformat(),
                'data': trends
            }

        except Exception as e:
            self.logger.error(f"获取Twitter数据失败: {e}")
            return None
        finally:
            if 'conn' in locals():
                conn.close()

    def fetch_reddit_hot(self, subreddit: str = "all", limit: int = 50) -> Optional[Dict]:
        """
        获取Reddit热门帖子

        Args:
            subreddit: 子版块名称（默认all）
            limit: 获取数量

        Returns:
            Reddit热门数据
        """
        try:
            conn = http.client.HTTPSConnection("reddapi.p.rapidapi.com")

            headers = {
                'x-rapidapi-key': self.RAPIDAPI_KEY,
                'x-rapidapi-host': "reddapi.p.rapidapi.com",
                'Content-Type': "application/json"
            }

            # 获取热门帖子的API路径（需要根据实际API调整）
            # 这里使用通用的获取方法
            endpoint = f"/api/v2/subreddit_hot?subreddit={subreddit}&limit={limit}"
            conn.request("GET", endpoint, headers=headers)

            res = conn.getresponse()
            data = res.read()

            result = json.loads(data.decode("utf-8"))

            self.logger.info(f"成功获取Reddit数据")

            # 转换为统一格式
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
                        'timestamp': int(post.get('created_utc', 0) * 1000)
                    })

            return {
                'platform': 'Reddit',
                'timestamp': datetime.now().isoformat(),
                'data': trends
            }

        except Exception as e:
            self.logger.error(f"获取Reddit数据失败: {e}")
            return None
        finally:
            if 'conn' in locals():
                conn.close()

    def fetch_youtube_trending(self, region: str = "US", category: str = "0") -> Optional[Dict]:
        """
        获取YouTube趋势视频

        Args:
            region: 地区代码
            category: 分类ID

        Returns:
            YouTube趋势数据
        """
        try:
            conn = http.client.HTTPSConnection("social-media-master.p.rapidapi.com")

            headers = {
                'x-rapidapi-key': self.RAPIDAPI_KEY,
                'x-rapidapi-host': "social-media-master.p.rapidapi.com"
            }

            # YouTube趋势API端点（需要根据实际API文档调整）
            endpoint = f"/youtube/trending?region={region}&category={category}"
            conn.request("GET", endpoint, headers=headers)

            res = conn.getresponse()
            data = res.read()

            result = json.loads(data.decode("utf-8"))

            self.logger.info(f"成功获取YouTube数据")

            # 转换为统一格式
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
                        'timestamp': int(datetime.now().timestamp() * 1000),
                        'cover': item.get('thumbnail', '')
                    })

            return {
                'platform': 'YouTube',
                'timestamp': datetime.now().isoformat(),
                'data': trends
            }

        except Exception as e:
            self.logger.error(f"获取YouTube数据失败: {e}")
            return None
        finally:
            if 'conn' in locals():
                conn.close()

    def fetch_all_external(self) -> Dict:
        """
        获取所有外部平台数据

        Returns:
            所有外部平台数据
        """
        results = {
            'crawl_time': datetime.now().isoformat(),
            'platforms': {}
        }

        # Twitter
        twitter_data = self.fetch_twitter_trends()
        if twitter_data:
            results['platforms']['Twitter'] = twitter_data

        # Reddit
        reddit_data = self.fetch_reddit_hot()
        if reddit_data:
            results['platforms']['Reddit'] = reddit_data

        # YouTube (注释掉，因为需要根据实际API调整)
        # youtube_data = self.fetch_youtube_trending()
        # if youtube_data:
        #     results['platforms']['YouTube'] = youtube_data

        self.logger.info(f"外部API爬取完成，成功 {len(results['platforms'])} 个平台")

        return results


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)

    crawler = ExternalAPICrawler()

    # 测试Twitter
    print("\n=== 测试Twitter API ===")
    twitter_data = crawler.fetch_twitter_trends()
    if twitter_data:
        print(f"获取到 {len(twitter_data['data'])} 条Twitter趋势")
        print(f"示例: {twitter_data['data'][0] if twitter_data['data'] else 'None'}")

    # 测试Reddit
    print("\n=== 测试Reddit API ===")
    reddit_data = crawler.fetch_reddit_hot()
    if reddit_data:
        print(f"获取到 {len(reddit_data['data'])} 条Reddit热门")
        print(f"示例: {reddit_data['data'][0] if reddit_data['data'] else 'None'}")

    # 测试所有
    print("\n=== 测试所有外部API ===")
    all_data = crawler.fetch_all_external()
    print(f"总共获取 {len(all_data['platforms'])} 个平台数据")
