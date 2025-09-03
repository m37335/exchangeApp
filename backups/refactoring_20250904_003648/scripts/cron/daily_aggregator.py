#!/usr/bin/env python3
"""
Daily Aggregator - 日足集計スクリプト

責任:
- 5分足データから日足を集計
- PostgreSQLデータベースへの保存
- エラーハンドリングとログ出力
"""

import asyncio
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Tuple

import pytz

# 環境変数を自動設定
os.environ["DATABASE_URL"] = (
    "postgresql+asyncpg://exchange_analytics_user:"
    "exchange_password@localhost:5432/exchange_analytics_production_db"
)

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from advanced_data.base_aggregator import (
    BaseAggregator, AggregationError, InsufficientDataError
)

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("/app/logs/daily_aggregator.log"),
        logging.StreamHandler(),
    ],
)
logger = logging.getLogger(__name__)


class DailyAggregator(BaseAggregator):
    """
    日足集計クラス

    責任:
    - 日足データの集計
    - 前日の5分足データからOHLCV計算
    - データベースへの保存
    """

    def __init__(self):
        super().__init__("1d", "yahoo_finance_1d_aggregated")

    async def get_aggregation_period(self) -> Tuple[datetime, datetime]:
        """
        集計期間を取得

        Returns:
            tuple: (start_time, end_time) 前日の期間
        """
        # 前日の期間計算
        now = datetime.now(pytz.timezone("Asia/Tokyo"))

        # 前日の開始時刻
        start_time = (now - timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        # 前日の終了時刻（23:55まで）
        end_time = start_time + timedelta(days=1) - timedelta(minutes=5)

        logger.info(f"📅 日足集計期間: {start_time} - {end_time}")
        return start_time, end_time

    async def aggregate_and_save(self):
        """
        日足集計と保存を実行

        Workflow:
        1. 集計期間の決定
        2. 5分足データの取得
        3. OHLCV計算
        4. 重複チェック
        5. データベース保存
        """
        try:
            # Step 1: 集計期間決定
            start_time, end_time = await self.get_aggregation_period()

            # Step 2: データ取得
            five_min_data = await self.get_five_min_data(start_time, end_time)
            if not five_min_data:
                logger.warning("⚠️ 集計対象データがありません")
                return

            # Step 3: 集計計算
            aggregated_data = await self.calculate_ohlcv(five_min_data)

            # Step 4: 重複チェック
            existing = await self.check_duplicate(aggregated_data.timestamp)
            if existing:
                logger.info("ℹ️ 既存データが存在します。スキップします。")
                return

            # Step 5: データ保存
            await self.save_aggregated_data(aggregated_data)
            logger.info(f"✅ 日足データを保存しました: {aggregated_data.timestamp}")

        except InsufficientDataError:
            logger.warning("⚠️ 集計対象データが不足しています")
            # 正常終了（エラーではない）
        except AggregationError as e:
            logger.error(f"❌ 集計処理エラー: {e}")
            raise
        except Exception as e:
            logger.error(f"❌ 予期しないエラー: {e}")
            raise


async def main():
    """メイン関数"""
    aggregator = None
    try:
        # 初期化
        aggregator = DailyAggregator()
        await aggregator.initialize_database()

        # 集計実行
        await aggregator.aggregate_and_save()
        logger.info("✅ 日足集計が正常に完了しました")

    except Exception as e:
        logger.error(f"❌ 日足集計エラー: {e}")
        sys.exit(1)
    finally:
        # クリーンアップ
        if aggregator:
            await aggregator.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
