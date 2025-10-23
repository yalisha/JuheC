#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
外部API调度器
限制调用频率：每天最多1次，确保不超过月度免费配额

月度配额:
- Twitter Trends: 100次/月
- Reddit API: 50次/月
- YouTube API: 70次/月

每天1次调用 = 30次/月 < 最低配额(50次)
"""

import schedule
import time
import logging
import json
from pathlib import Path
from datetime import datetime, timedelta
from external_apis import ExternalAPICrawler


class ExternalAPIScheduler:
    """外部API调度器 - 每天调用1次"""

    def __init__(self, data_dir: str = "data", log_dir: str = "logs"):
        """
        初始化调度器

        Args:
            data_dir: 数据目录
            log_dir: 日志目录
        """
        self.data_dir = Path(data_dir)
        self.log_dir = Path(log_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.log_dir.mkdir(exist_ok=True)

        # 设置日志
        log_file = self.log_dir / "external_api.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

        # 状态文件 - 记录最后一次调用时间
        self.status_file = self.data_dir / "external_api_status.json"

        # 初始化爬虫
        self.crawler = ExternalAPICrawler()

    def can_crawl_today(self) -> bool:
        """
        检查今天是否已经调用过API

        Returns:
            True if 今天还没调用过, False if 今天已经调用过
        """
        if not self.status_file.exists():
            return True

        try:
            with open(self.status_file, 'r', encoding='utf-8') as f:
                status = json.load(f)

            last_crawl = datetime.fromisoformat(status.get('last_crawl_time', '2000-01-01'))
            today = datetime.now().date()

            # 如果最后一次调用不是今天，则可以调用
            return last_crawl.date() < today

        except Exception as e:
            self.logger.error(f"读取状态文件失败: {e}")
            return True

    def update_status(self):
        """更新状态文件"""
        status = {
            'last_crawl_time': datetime.now().isoformat(),
            'total_calls_this_month': self._get_monthly_calls() + 1
        }

        try:
            with open(self.status_file, 'w', encoding='utf-8') as f:
                json.dump(status, f, ensure_ascii=False, indent=2)
        except Exception as e:
            self.logger.error(f"更新状态文件失败: {e}")

    def _get_monthly_calls(self) -> int:
        """获取本月已调用次数"""
        if not self.status_file.exists():
            return 0

        try:
            with open(self.status_file, 'r', encoding='utf-8') as f:
                status = json.load(f)

            last_crawl = datetime.fromisoformat(status.get('last_crawl_time', '2000-01-01'))
            current_month = datetime.now().month

            # 如果是同一个月，返回次数；否则重置为0
            if last_crawl.month == current_month:
                return status.get('total_calls_this_month', 0)
            else:
                return 0

        except Exception as e:
            self.logger.error(f"读取月度调用次数失败: {e}")
            return 0

    def job(self):
        """执行外部API爬取任务"""
        # 检查今天是否已经调用过
        if not self.can_crawl_today():
            self.logger.info("⏭️  今天已经调用过外部API，跳过本次调用")
            return

        self.logger.info("🌐 开始外部API爬取...")

        try:
            # 调用API
            results = self.crawler.fetch_all_external()

            # 保存数据
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.data_dir / f"external_{timestamp}.json"

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)

            # 统计信息
            total_items = sum(len(p['data']) for p in results['platforms'].values())
            monthly_calls = self._get_monthly_calls() + 1

            self.logger.info(f"✅ 外部API爬取完成")
            self.logger.info(f"   平台数: {len(results['platforms'])}")
            self.logger.info(f"   总条目: {total_items}")
            self.logger.info(f"   本月调用: {monthly_calls} 次")
            self.logger.info(f"   保存到: {output_file}")

            # 更新状态
            self.update_status()

        except Exception as e:
            self.logger.error(f"❌ 外部API爬取失败: {e}")
            import traceback
            self.logger.error(traceback.format_exc())

    def run(self, daily_hour: int = 2):
        """
        运行调度器

        Args:
            daily_hour: 每天执行的小时（默认凌晨2点）
        """
        self.logger.info(f"🚀 外部API调度器启动")
        self.logger.info(f"⏰ 执行时间: 每天 {daily_hour:02d}:00")
        self.logger.info(f"📊 API配额限制:")
        self.logger.info(f"   - Twitter: 100次/月")
        self.logger.info(f"   - Reddit: 50次/月")
        self.logger.info(f"   - YouTube: 70次/月")
        self.logger.info(f"   - 调度策略: 每天1次 = 30次/月 ✅")

        # 设置定时任务 - 每天指定时间执行
        schedule.every().day.at(f"{daily_hour:02d}:00").do(self.job)

        # 立即执行一次（如果今天还没执行过）
        self.job()

        # 进入调度循环
        while True:
            schedule.run_pending()
            time.sleep(60)  # 每分钟检查一次


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="外部API调度器 - 每天调用1次")
    parser.add_argument('--hour', type=int, default=2,
                        help='每天执行的小时 (0-23)，默认为2（凌晨2点）')
    parser.add_argument('--once', action='store_true',
                        help='只执行一次（测试用）')

    args = parser.parse_args()

    scheduler = ExternalAPIScheduler()

    if args.once:
        # 测试模式 - 只执行一次
        print("📝 测试模式 - 只执行一次")
        scheduler.job()
    else:
        # 正常模式 - 定时调度
        scheduler.run(daily_hour=args.hour)
