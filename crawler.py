#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
07173游戏热搜爬虫
支持多平台热搜数据抓取，定时运行，数据持久化
"""

import requests
import json
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
import logging


class HotSearchCrawler:
    """07173热搜爬虫核心类"""

    # API基础URL
    API_BASE_URL = "https://api.pearktrue.cn/api/dailyhot/"

    # 支持的平台列表（根据07173网站的平台）
    PLATFORMS = [
        "哔哩哔哩",
        "抖音",
        "微博",
        "知乎",
        "百度",
        "少数派",
        "IT之家",
        "澎湃新闻",
        "今日头条",
        "36氪",
        "稀土掘金",
        "腾讯新闻",
        "网易新闻",
        "英雄联盟",
        "原神",
        "微信读书",
        "贴吧",
    ]

    def __init__(self, data_dir: str = "data", log_dir: str = "logs"):
        """
        初始化爬虫

        Args:
            data_dir: 数据存储目录
            log_dir: 日志存储目录
        """
        self.data_dir = Path(data_dir)
        self.log_dir = Path(log_dir)

        # 创建必要的目录
        self.data_dir.mkdir(exist_ok=True)
        self.log_dir.mkdir(exist_ok=True)

        # 配置日志
        self._setup_logging()

        # 请求会话
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/json',
        })

    def _setup_logging(self):
        """配置日志系统"""
        log_file = self.log_dir / f"crawler_{datetime.now().strftime('%Y%m')}.log"

        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def fetch_platform_data(self, platform: str, retry: int = 3) -> Optional[Dict]:
        """
        获取单个平台的热搜数据

        Args:
            platform: 平台名称
            retry: 重试次数

        Returns:
            热搜数据字典，失败返回None
        """
        url = f"{self.API_BASE_URL}?title={platform}"

        for attempt in range(retry):
            try:
                self.logger.info(f"正在获取【{platform}】热搜数据 (尝试 {attempt + 1}/{retry})")

                response = self.session.get(url, timeout=10)
                response.raise_for_status()

                data = response.json()

                # 检查API返回状态
                if data.get('code') == 200 and 'data' in data:
                    self.logger.info(f"成功获取【{platform}】热搜数据，共 {len(data['data'])} 条")
                    return {
                        'platform': platform,
                        'timestamp': datetime.now().isoformat(),
                        'data': data['data']
                    }
                else:
                    self.logger.warning(f"【{platform}】API返回异常: {data}")

            except requests.RequestException as e:
                self.logger.error(f"【{platform}】请求失败 (尝试 {attempt + 1}/{retry}): {e}")
                if attempt < retry - 1:
                    time.sleep(2 ** attempt)  # 指数退避
            except Exception as e:
                self.logger.error(f"【{platform}】解析数据失败: {e}")
                break

        return None

    def fetch_all_platforms(self, platforms: Optional[List[str]] = None) -> Dict:
        """
        获取所有平台的热搜数据

        Args:
            platforms: 指定平台列表，默认为所有支持的平台

        Returns:
            包含所有平台数据的字典
        """
        if platforms is None:
            platforms = self.PLATFORMS

        self.logger.info(f"开始爬取 {len(platforms)} 个平台的热搜数据")
        start_time = time.time()

        results = {
            'crawl_time': datetime.now().isoformat(),
            'platforms': {}
        }

        for platform in platforms:
            data = self.fetch_platform_data(platform)
            if data:
                results['platforms'][platform] = data
            time.sleep(1)  # 避免请求过快

        elapsed = time.time() - start_time
        self.logger.info(f"爬取完成，耗时 {elapsed:.2f} 秒，成功 {len(results['platforms'])}/{len(platforms)} 个平台")

        return results

    def save_data(self, data: Dict, filename: Optional[str] = None) -> Path:
        """
        保存数据到JSON文件

        Args:
            data: 要保存的数据
            filename: 文件名，默认使用时间戳

        Returns:
            保存的文件路径
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"hotsearch_{timestamp}.json"

        filepath = self.data_dir / filename

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)

            self.logger.info(f"数据已保存到: {filepath}")
            return filepath

        except Exception as e:
            self.logger.error(f"保存数据失败: {e}")
            raise

    def save_latest(self, data: Dict) -> Path:
        """
        保存为最新数据文件（覆盖式）

        Args:
            data: 要保存的数据

        Returns:
            保存的文件路径
        """
        return self.save_data(data, filename="latest.json")

    def run_once(self, save_history: bool = True) -> Dict:
        """
        执行一次完整的爬取流程

        Args:
            save_history: 是否保存历史记录

        Returns:
            爬取的数据
        """
        self.logger.info("=" * 60)
        self.logger.info("开始执行爬取任务")

        # 爬取数据
        data = self.fetch_all_platforms()

        # 保存最新数据
        self.save_latest(data)

        # 保存历史记录
        if save_history:
            self.save_data(data)

        self.logger.info("爬取任务完成")
        self.logger.info("=" * 60)

        return data


def main():
    """主函数：单次运行示例"""
    crawler = HotSearchCrawler()
    crawler.run_once()


if __name__ == "__main__":
    main()
