#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库模块 - SQLite存储和时序追踪
支持原始数据保存、排名历史追踪、详情数据存储
"""

import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Tuple


class HotSearchDatabase:
    """热搜数据库管理类"""

    def __init__(self, db_path: str = "data/hotsearch.db"):
        """
        初始化数据库连接

        Args:
            db_path: 数据库文件路径
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row  # 允许按列名访问

        self.logger = logging.getLogger(__name__)
        self.create_tables()

    def create_tables(self):
        """创建所有必要的数据表"""
        cursor = self.conn.cursor()

        # 1. 原始热搜数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS hotsearch_raw (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                item_id TEXT,
                title TEXT NOT NULL,
                description TEXT,
                author TEXT,
                hot INTEGER,
                url TEXT,
                mobile_url TEXT,
                cover TEXT,
                rank_position INTEGER,
                timestamp BIGINT,
                collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                data_json TEXT NOT NULL,
                UNIQUE(platform, item_id, collected_at)
            )
        ''')

        # 2. 排名历史表（时序分析核心）
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ranking_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                item_id TEXT NOT NULL,
                title TEXT NOT NULL,
                rank_position INTEGER NOT NULL,
                hot INTEGER NOT NULL,
                collected_at TIMESTAMP NOT NULL,
                rank_change INTEGER,
                hot_change INTEGER,
                hot_growth_rate REAL
            )
        ''')

        # 3. 详情数据表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS item_details (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                item_id TEXT NOT NULL,
                view_count INTEGER,
                like_count INTEGER,
                comment_count INTEGER,
                share_count INTEGER,
                favorite_count INTEGER,
                coin_count INTEGER,
                danmaku_count INTEGER,
                collected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                details_json TEXT
            )
        ''')

        # 4. 跨平台关联表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS cross_platform (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic_hash TEXT NOT NULL,
                platform TEXT NOT NULL,
                item_id TEXT NOT NULL,
                title TEXT NOT NULL,
                first_seen TIMESTAMP NOT NULL,
                last_seen TIMESTAMP,
                max_rank INTEGER,
                max_hot INTEGER,
                similarity_score REAL
            )
        ''')

        # 创建索引以提升查询性能
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_raw_platform_time
            ON hotsearch_raw(platform, collected_at)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_history_item_time
            ON ranking_history(platform, item_id, collected_at)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_history_time
            ON ranking_history(collected_at)
        ''')

        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_details_item
            ON item_details(platform, item_id, collected_at)
        ''')

        self.conn.commit()
        self.logger.info("数据库表创建完成")

    def insert_hotsearch_batch(self, platform: str, items: List[Dict]) -> int:
        """
        批量插入热搜数据

        Args:
            platform: 平台名称
            items: 热搜数据列表

        Returns:
            插入的记录数
        """
        cursor = self.conn.cursor()
        inserted = 0
        collected_at = datetime.now()

        for rank, item in enumerate(items, 1):
            try:
                # 插入原始数据
                cursor.execute('''
                    INSERT OR IGNORE INTO hotsearch_raw
                    (platform, item_id, title, description, author, hot, url,
                     mobile_url, cover, rank_position, timestamp, collected_at, data_json)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    platform,
                    item.get('id', ''),
                    item.get('title', ''),
                    item.get('desc', ''),
                    item.get('author', ''),
                    item.get('hot', 0),
                    item.get('url', ''),
                    item.get('mobileUrl', ''),
                    item.get('cover', ''),
                    rank,
                    item.get('timestamp', 0),
                    collected_at,
                    json.dumps(item, ensure_ascii=False)
                ))

                # 计算排名和热度变化
                rank_change, hot_change, hot_growth_rate = self._calculate_changes(
                    platform, item.get('id', ''), rank, item.get('hot', 0)
                )

                # 插入排名历史
                cursor.execute('''
                    INSERT INTO ranking_history
                    (platform, item_id, title, rank_position, hot, collected_at,
                     rank_change, hot_change, hot_growth_rate)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    platform,
                    item.get('id', ''),
                    item.get('title', ''),
                    rank,
                    item.get('hot', 0),
                    collected_at,
                    rank_change,
                    hot_change,
                    hot_growth_rate
                ))

                inserted += 1

            except sqlite3.IntegrityError as e:
                self.logger.warning(f"数据已存在，跳过: {platform} - {item.get('title', '')}")
            except Exception as e:
                self.logger.error(f"插入数据失败: {e}", exc_info=True)

        self.conn.commit()
        self.logger.info(f"成功插入 {inserted}/{len(items)} 条数据 [{platform}]")
        return inserted

    def _calculate_changes(self, platform: str, item_id: str,
                          current_rank: int, current_hot: int) -> Tuple[Optional[int], Optional[int], Optional[float]]:
        """
        计算排名和热度变化

        Returns:
            (rank_change, hot_change, hot_growth_rate)
        """
        cursor = self.conn.cursor()

        # 查询上一次的数据
        cursor.execute('''
            SELECT rank_position, hot
            FROM ranking_history
            WHERE platform = ? AND item_id = ?
            ORDER BY collected_at DESC
            LIMIT 1
        ''', (platform, item_id))

        row = cursor.fetchone()
        if not row:
            return None, None, None

        prev_rank, prev_hot = row[0], row[1]

        # 计算变化（排名下降是正向，所以是prev - current）
        rank_change = prev_rank - current_rank
        hot_change = current_hot - prev_hot
        hot_growth_rate = (hot_change / prev_hot * 100) if prev_hot > 0 else 0

        return rank_change, hot_change, hot_growth_rate

    def get_item_history(self, platform: str, item_id: str,
                        hours: int = 24) -> List[Dict]:
        """
        获取单个热搜的历史数据

        Args:
            platform: 平台名称
            item_id: 热搜ID
            hours: 查询最近多少小时的数据

        Returns:
            历史数据列表
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT rank_position, hot, collected_at, rank_change, hot_change, hot_growth_rate
            FROM ranking_history
            WHERE platform = ? AND item_id = ?
            AND collected_at >= datetime('now', '-' || ? || ' hours')
            ORDER BY collected_at ASC
        ''', (platform, item_id, hours))

        return [dict(row) for row in cursor.fetchall()]

    def get_trending_topics(self, platform: str, hours: int = 24,
                           min_appearances: int = 3) -> List[Dict]:
        """
        获取持续上榜的热点话题

        Args:
            platform: 平台名称
            hours: 时间范围
            min_appearances: 最小出现次数

        Returns:
            热点话题列表
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT
                item_id,
                title,
                COUNT(*) as appearances,
                MIN(rank_position) as best_rank,
                MAX(hot) as max_hot,
                AVG(hot) as avg_hot,
                MIN(collected_at) as first_seen,
                MAX(collected_at) as last_seen
            FROM ranking_history
            WHERE platform = ?
            AND collected_at >= datetime('now', '-' || ? || ' hours')
            GROUP BY item_id, title
            HAVING COUNT(*) >= ?
            ORDER BY max_hot DESC
            LIMIT 50
        ''', (platform, hours, min_appearances))

        return [dict(row) for row in cursor.fetchall()]

    def get_fastest_rising(self, platform: str, limit: int = 10) -> List[Dict]:
        """
        获取最快上升的热搜

        Args:
            platform: 平台名称
            limit: 返回数量

        Returns:
            快速上升的热搜列表
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT
                item_id,
                title,
                rank_position,
                hot,
                rank_change,
                hot_change,
                hot_growth_rate,
                collected_at
            FROM ranking_history
            WHERE platform = ?
            AND rank_change IS NOT NULL
            AND rank_change > 0
            ORDER BY collected_at DESC, rank_change DESC
            LIMIT ?
        ''', (platform, limit))

        return [dict(row) for row in cursor.fetchall()]

    def insert_item_details(self, platform: str, item_id: str, details: Dict) -> bool:
        """
        插入详情数据

        Args:
            platform: 平台名称
            item_id: 热搜ID
            details: 详情数据字典

        Returns:
            是否插入成功
        """
        cursor = self.conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO item_details
                (platform, item_id, view_count, like_count, comment_count,
                 share_count, favorite_count, coin_count, danmaku_count, details_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                platform,
                item_id,
                details.get('view', 0),
                details.get('like', 0),
                details.get('reply', 0),
                details.get('share', 0),
                details.get('favorite', 0),
                details.get('coin', 0),
                details.get('danmaku', 0),
                json.dumps(details, ensure_ascii=False)
            ))

            self.conn.commit()
            return True

        except Exception as e:
            self.logger.error(f"插入详情数据失败: {e}")
            return False

    def get_statistics(self, platform: Optional[str] = None) -> Dict:
        """
        获取数据库统计信息

        Args:
            platform: 平台名称，None表示所有平台

        Returns:
            统计信息字典
        """
        cursor = self.conn.cursor()

        stats = {}

        # 总记录数
        if platform:
            cursor.execute('SELECT COUNT(*) FROM hotsearch_raw WHERE platform = ?', (platform,))
        else:
            cursor.execute('SELECT COUNT(*) FROM hotsearch_raw')
        stats['total_records'] = cursor.fetchone()[0]

        # 历史记录数
        if platform:
            cursor.execute('SELECT COUNT(*) FROM ranking_history WHERE platform = ?', (platform,))
        else:
            cursor.execute('SELECT COUNT(*) FROM ranking_history')
        stats['history_records'] = cursor.fetchone()[0]

        # 时间范围
        cursor.execute('SELECT MIN(collected_at), MAX(collected_at) FROM hotsearch_raw')
        row = cursor.fetchone()
        stats['earliest_record'] = row[0]
        stats['latest_record'] = row[1]

        # 平台数量
        if not platform:
            cursor.execute('SELECT COUNT(DISTINCT platform) FROM hotsearch_raw')
            stats['platform_count'] = cursor.fetchone()[0]

        # 详情数据数量
        if platform:
            cursor.execute('SELECT COUNT(*) FROM item_details WHERE platform = ?', (platform,))
        else:
            cursor.execute('SELECT COUNT(*) FROM item_details')
        stats['details_count'] = cursor.fetchone()[0]

        return stats

    def export_to_csv(self, output_path: str, platform: Optional[str] = None,
                     start_date: Optional[str] = None, end_date: Optional[str] = None):
        """
        导出数据为CSV文件

        Args:
            output_path: 输出文件路径
            platform: 平台筛选
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
        """
        import csv

        cursor = self.conn.cursor()

        # 构建查询
        query = 'SELECT * FROM ranking_history WHERE 1=1'
        params = []

        if platform:
            query += ' AND platform = ?'
            params.append(platform)

        if start_date:
            query += ' AND date(collected_at) >= ?'
            params.append(start_date)

        if end_date:
            query += ' AND date(collected_at) <= ?'
            params.append(end_date)

        query += ' ORDER BY collected_at, platform, rank_position'

        cursor.execute(query, params)

        # 写入CSV
        with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)

            # 写入表头
            writer.writerow([desc[0] for desc in cursor.description])

            # 写入数据
            writer.writerows(cursor.fetchall())

        self.logger.info(f"数据已导出到: {output_path}")

    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            self.logger.info("数据库连接已关闭")

    def __enter__(self):
        """上下文管理器入口"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """上下文管理器退出"""
        self.close()


# 数据库工具函数
def get_database() -> HotSearchDatabase:
    """获取数据库实例"""
    return HotSearchDatabase()


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(level=logging.INFO)

    with get_database() as db:
        # 打印统计信息
        stats = db.get_statistics()
        print("\n数据库统计信息:")
        print(f"  总记录数: {stats['total_records']}")
        print(f"  历史记录数: {stats['history_records']}")
        print(f"  平台数量: {stats.get('platform_count', 'N/A')}")
        print(f"  详情数据: {stats['details_count']}")
        print(f"  最早记录: {stats['earliest_record']}")
        print(f"  最新记录: {stats['latest_record']}")
