#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
定时任务调度器
支持每小时自动运行爬虫任务
"""

import schedule
import time
from datetime import datetime
import logging
from pathlib import Path
import signal
import sys

from crawler import HotSearchCrawler


class CrawlerScheduler:
    """爬虫定时调度器"""

    def __init__(self, interval_minutes: int = 30):
        """
        初始化调度器

        Args:
            interval_minutes: 运行间隔（分钟）
        """
        self.interval_minutes = interval_minutes
        self.crawler = HotSearchCrawler()
        self.is_running = True
        self.logger = logging.getLogger(__name__)

        # 注册信号处理
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """处理中断信号"""
        self.logger.info(f"\n收到信号 {signum}，正在优雅退出...")
        self.is_running = False

    def job(self):
        """要执行的任务"""
        try:
            self.logger.info(f"[定时任务] 开始执行 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            self.crawler.run_once(save_history=True)
            self.logger.info(f"[定时任务] 执行完成 - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        except Exception as e:
            self.logger.error(f"[定时任务] 执行失败: {e}", exc_info=True)

    def run(self):
        """启动调度器"""
        self.logger.info("=" * 80)
        self.logger.info(f"爬虫调度器启动成功")
        self.logger.info(f"运行间隔: 每 {self.interval_minutes} 分钟")
        self.logger.info(f"启动时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("=" * 80)

        # 立即执行一次
        self.logger.info("立即执行首次任务...")
        self.job()

        # 设置定时任务
        schedule.every(self.interval_minutes).minutes.do(self.job)

        # 主循环
        self.logger.info(f"\n等待下次执行...")
        while self.is_running:
            try:
                schedule.run_pending()
                time.sleep(1)
            except KeyboardInterrupt:
                break
            except Exception as e:
                self.logger.error(f"调度器运行异常: {e}", exc_info=True)
                time.sleep(60)  # 发生错误时等待1分钟后继续

        self.logger.info("调度器已停止")


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='07173热搜爬虫定时调度器')
    parser.add_argument(
        '--interval',
        type=int,
        default=30,
        help='运行间隔（分钟），默认为30分钟'
    )
    parser.add_argument(
        '--once',
        action='store_true',
        help='仅运行一次，不启动定时任务'
    )

    args = parser.parse_args()

    if args.once:
        # 单次运行模式
        crawler = HotSearchCrawler()
        crawler.run_once()
    else:
        # 定时运行模式
        scheduler = CrawlerScheduler(interval_minutes=args.interval)
        scheduler.run()


if __name__ == "__main__":
    main()
