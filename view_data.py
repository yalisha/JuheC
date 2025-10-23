#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据查看工具
用于查看和分析爬取的热搜数据
"""

import json
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List


class DataViewer:
    """数据查看器"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)

    def load_latest(self) -> Dict:
        """加载最新数据"""
        latest_file = self.data_dir / "latest.json"
        if not latest_file.exists():
            print("错误: 未找到最新数据文件")
            sys.exit(1)

        with open(latest_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def load_history(self, filename: str) -> Dict:
        """加载历史数据"""
        filepath = self.data_dir / filename
        if not filepath.exists():
            print(f"错误: 文件不存在 {filename}")
            sys.exit(1)

        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def list_history(self) -> List[Path]:
        """列出所有历史文件"""
        return sorted(self.data_dir.glob("hotsearch_*.json"), reverse=True)

    def print_summary(self, data: Dict):
        """打印数据摘要"""
        print("\n" + "=" * 70)
        print(f"爬取时间: {data['crawl_time']}")
        print(f"平台数量: {len(data['platforms'])}")
        print("=" * 70)

        total_items = 0
        for platform, info in sorted(data['platforms'].items()):
            count = len(info['data'])
            total_items += count
            print(f"  📊 {platform:15s} {count:3d} 条")

        print("=" * 70)
        print(f"总计: {total_items} 条热搜\n")

    def print_platform(self, data: Dict, platform: str, limit: int = 10):
        """打印单个平台的热搜"""
        if platform not in data['platforms']:
            print(f"错误: 平台 '{platform}' 不存在")
            print(f"可用平台: {', '.join(data['platforms'].keys())}")
            return

        platform_data = data['platforms'][platform]
        items = platform_data['data']

        print("\n" + "=" * 70)
        print(f"平台: {platform}")
        print(f"更新时间: {platform_data['timestamp']}")
        print(f"热搜数量: {len(items)}")
        print("=" * 70)

        for i, item in enumerate(items[:limit], 1):
            title = item.get('title', 'N/A')
            hot = item.get('hot', 'N/A')
            url = item.get('url', 'N/A')

            print(f"\n{i:2d}. {title}")
            print(f"    🔥 热度: {hot}")
            print(f"    🔗 链接: {url[:60]}..." if len(url) > 60 else f"    🔗 链接: {url}")

        if len(items) > limit:
            print(f"\n... 还有 {len(items) - limit} 条 ...")

        print()

    def print_top_all(self, data: Dict, top_n: int = 5):
        """打印所有平台的前N条热搜"""
        print("\n" + "=" * 70)
        print(f"各平台 TOP {top_n} 热搜")
        print("=" * 70)

        for platform, info in sorted(data['platforms'].items()):
            print(f"\n【{platform}】")
            items = info['data'][:top_n]
            for i, item in enumerate(items, 1):
                title = item.get('title', 'N/A')
                hot = item.get('hot', 'N/A')
                print(f"  {i}. {title[:50]}... (🔥 {hot})")

        print()


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='07173热搜数据查看工具')
    parser.add_argument(
        '--platform', '-p',
        type=str,
        help='查看指定平台的热搜'
    )
    parser.add_argument(
        '--limit', '-l',
        type=int,
        default=10,
        help='显示的数量限制'
    )
    parser.add_argument(
        '--top', '-t',
        type=int,
        help='显示所有平台的前N条热搜'
    )
    parser.add_argument(
        '--history',
        action='store_true',
        help='列出历史记录'
    )
    parser.add_argument(
        '--file', '-f',
        type=str,
        help='加载指定的历史文件'
    )

    args = parser.parse_args()

    viewer = DataViewer()

    # 列出历史记录
    if args.history:
        history_files = viewer.list_history()
        print(f"\n找到 {len(history_files)} 个历史文件:\n")
        for i, filepath in enumerate(history_files[:20], 1):
            size_kb = filepath.stat().st_size / 1024
            print(f"{i:2d}. {filepath.name} ({size_kb:.1f} KB)")
        if len(history_files) > 20:
            print(f"\n... 还有 {len(history_files) - 20} 个文件 ...")
        print()
        return

    # 加载数据
    if args.file:
        data = viewer.load_history(args.file)
    else:
        data = viewer.load_latest()

    # 显示数据
    if args.platform:
        viewer.print_platform(data, args.platform, args.limit)
    elif args.top:
        viewer.print_top_all(data, args.top)
    else:
        viewer.print_summary(data)


if __name__ == "__main__":
    main()
