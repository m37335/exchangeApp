"""
Technical Indicators for Real Trading Analysis
実トレード用テクニカル指標分析システム

設計書参照:
- trade_chart_settings_2025.md

機能:
- RSI (期間14, レベル70/50/30)
- MACD (12,26,9)
- ボリンジャーバンド (20,2)
- マルチタイムフレーム分析
"""

import sys
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
import pytz
import ta
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# プロジェクトパスを追加
sys.path.append("/app")

from ...utils.logging_config import get_infrastructure_logger

logger = get_infrastructure_logger()


class TechnicalIndicatorsAnalyzer:
    """実トレード用テクニカル指標アナライザー"""

    def __init__(self):
        self.console = Console()
        self.jst = pytz.timezone("Asia/Tokyo")

        # 設定値（trade_chart_settings_2025.mdに基づく）
        # RSI設定（複数期間対応）
        self.rsi_period = 14  # デフォルト期間
        self.rsi_long = 70  # 長期RSI
        self.rsi_medium = 50  # 中期RSI
        self.rsi_short = 30  # 短期RSI
        self.rsi_levels = {"overbought": 70, "neutral": 50, "oversold": 30}

        self.macd_fast = 12
        self.macd_slow = 26
        self.macd_signal = 9

        self.bb_period = 20
        self.bb_std = 2

        # 移動平均線設定
        self.ma_short = 20  # 短期移動平均
        self.ma_medium = 50  # 中期移動平均
        self.ma_long = 200  # 長期移動平均

        logger.info("Initialized Technical Indicators Analyzer")

    def calculate_rsi(
        self, data: pd.DataFrame, timeframe: str = "D1", period: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        RSI計算 (複数期間対応)

        Args:
            data: OHLCV データ
            timeframe: 時間軸 (D1, H4, H1, M5)
            period: 指定期間（Noneの場合はデフォルト値を使用）

        Returns:
            Dict: RSI値と分析結果
        """
        try:
            # 期間の決定
            if period is not None:
                rsi_period = period
            else:
                rsi_period = self.rsi_period

            # データ型の詳細ログ
            logger.info(f"RSI calculation - Data type: {type(data)}")
            logger.info(
                f"RSI calculation - Data shape: {getattr(data, 'shape', 'N/A')}"
            )
            logger.info(
                f"RSI calculation - Data columns: {getattr(data, 'columns', 'N/A')}"
            )

            # データがnumpy配列の場合はDataFrameに変換
            if isinstance(data, np.ndarray):
                logger.warning("Data is numpy array, converting to DataFrame")
                return {"error": "データ形式エラー: DataFrameが必要"}

            # データが辞書の場合はDataFrameに変換を試行
            if isinstance(data, dict):
                try:
                    data = pd.DataFrame(data)
                except Exception as e:
                    logger.error(f"Failed to convert dict to DataFrame: {str(e)}")
                    return {"error": "データ変換エラー"}

            if len(data) < rsi_period:
                logger.warning(
                    f"Insufficient data for RSI calculation: {len(data)} < {rsi_period}"
                )
                return {"error": "データ不足"}

            # Close列が存在するかチェック
            if "Close" not in data.columns:
                logger.error("Close column not found in data")
                return {"error": "Close列が見つかりません"}

            close = data["Close"]
            rsi = ta.momentum.RSIIndicator(close, window=rsi_period).rsi()

            current_rsi = rsi.iloc[-1] if not np.isnan(rsi.iloc[-1]) else None
            previous_rsi = (
                rsi.iloc[-2] if len(rsi) > 1 and not np.isnan(rsi.iloc[-2]) else None
            )

            # RSI状態判定
            rsi_state = self._classify_rsi_state(current_rsi)

            # シグナル判定
            signal = self._analyze_rsi_signal(current_rsi, previous_rsi, timeframe)

            # ダイバージェンス検出（簡易版）
            divergence = self._detect_rsi_divergence(data, rsi, periods=5)

            result = {
                "indicator": "RSI",
                "timeframe": timeframe,
                "period": rsi_period,
                "current_value": round(current_rsi, 2) if current_rsi else None,
                "previous_value": round(previous_rsi, 2) if previous_rsi else None,
                "state": rsi_state,
                "signal": signal,
                "divergence": divergence,
                "levels": self.rsi_levels,
                "timestamp": datetime.now(self.jst).isoformat(),
                "data_points": len(data),
            }

            # 期間に応じてキーを設定
            if rsi_period == 70:
                result["rsi_long"] = result["current_value"]
            elif rsi_period == 50:
                result["rsi_medium"] = result["current_value"]
            elif rsi_period == 30:
                result["rsi_short"] = result["current_value"]

            logger.info(
                f"RSI calculated for {timeframe}: {current_rsi:.2f} ({rsi_state})"
            )
            return result

        except Exception as e:
            logger.error(f"RSI calculation error: {str(e)}")
            return {"error": str(e)}

    def calculate_macd(
        self, data: pd.DataFrame, timeframe: str = "D1"
    ) -> Dict[str, Any]:
        """
        MACD計算 (12,26,9)

        Args:
            data: OHLCV データ
            timeframe: 時間軸

        Returns:
            Dict: MACD値と分析結果
        """
        try:
            # データがnumpy配列の場合はDataFrameに変換
            if isinstance(data, np.ndarray):
                logger.warning("Data is numpy array, converting to DataFrame")
                return {"error": "データ形式エラー: DataFrameが必要"}

            # データが辞書の場合はDataFrameに変換を試行
            if isinstance(data, dict):
                try:
                    data = pd.DataFrame(data)
                except Exception as e:
                    logger.error(f"Failed to convert dict to DataFrame: {str(e)}")
                    return {"error": "データ変換エラー"}

            required_periods = max(self.macd_slow, self.macd_signal) + 10
            if len(data) < required_periods:
                logger.warning(
                    f"Insufficient data for MACD calculation: {len(data)} < {required_periods}"
                )
                return {"error": "データ不足"}

            # Close列が存在するかチェック
            if "Close" not in data.columns:
                logger.error("Close column not found in data")
                return {"error": "Close列が見つかりません"}

            close = data["Close"]
            macd_indicator = ta.trend.MACD(
                close,
                window_fast=self.macd_fast,
                window_slow=self.macd_slow,
                window_sign=self.macd_signal,
            )
            macd_line = macd_indicator.macd()
            signal_line = macd_indicator.macd_signal()
            histogram = macd_indicator.macd_diff()

            current_macd = (
                macd_line.iloc[-1] if not np.isnan(macd_line.iloc[-1]) else None
            )
            current_signal = (
                signal_line.iloc[-1] if not np.isnan(signal_line.iloc[-1]) else None
            )
            current_histogram = (
                histogram.iloc[-1] if not np.isnan(histogram.iloc[-1]) else None
            )

            previous_macd = (
                macd_line.iloc[-2]
                if len(macd_line) > 1 and not np.isnan(macd_line.iloc[-2])
                else None
            )
            previous_signal = (
                signal_line.iloc[-2]
                if len(signal_line) > 1 and not np.isnan(signal_line.iloc[-2])
                else None
            )

            # クロス判定
            cross_signal = self._analyze_macd_cross(
                current_macd, current_signal, previous_macd, previous_signal
            )

            # ゼロライン位置判定
            zero_line_position = (
                "above"
                if current_macd > 0
                else "below" if current_macd < 0 else "neutral"
            )

            result = {
                "indicator": "MACD",
                "timeframe": timeframe,
                "parameters": f"{self.macd_fast},{self.macd_slow},{self.macd_signal}",
                "macd_line": round(current_macd, 6) if current_macd else None,
                "signal_line": round(current_signal, 6) if current_signal else None,
                "histogram": round(current_histogram, 6) if current_histogram else None,
                "cross_signal": cross_signal,
                "zero_line_position": zero_line_position,
                "timestamp": datetime.now(self.jst).isoformat(),
                "data_points": len(data),
            }

            logger.info(f"MACD calculated for {timeframe}: {cross_signal}")
            return result

        except Exception as e:
            logger.error(f"MACD calculation error: {str(e)}")
            return {"error": str(e)}

    def calculate_bollinger_bands(
        self, data: pd.DataFrame, timeframe: str = "H4"
    ) -> Dict[str, Any]:
        """
        ボリンジャーバンド計算 (期間20, 偏差2)

        Args:
            data: OHLCV データ
            timeframe: 時間軸

        Returns:
            Dict: ボリンジャーバンド値と分析結果
        """
        try:
            # データがnumpy配列の場合はDataFrameに変換
            if isinstance(data, np.ndarray):
                logger.warning("Data is numpy array, converting to DataFrame")
                return {"error": "データ形式エラー: DataFrameが必要"}

            # データが辞書の場合はDataFrameに変換を試行
            if isinstance(data, dict):
                try:
                    data = pd.DataFrame(data)
                except Exception as e:
                    logger.error(f"Failed to convert dict to DataFrame: {str(e)}")
                    return {"error": "データ変換エラー"}

            if len(data) < self.bb_period + 5:
                logger.warning(
                    f"Insufficient data for Bollinger Bands: {len(data)} < {self.bb_period + 5}"
                )
                return {"error": "データ不足"}

            # Close列が存在するかチェック
            if "Close" not in data.columns:
                logger.error("Close column not found in data")
                return {"error": "Close列が見つかりません"}

            close = data["Close"]
            bb_indicator = ta.volatility.BollingerBands(
                close,
                window=self.bb_period,
                window_dev=self.bb_std,
            )
            upper = bb_indicator.bollinger_hband()
            middle = bb_indicator.bollinger_mavg()
            lower = bb_indicator.bollinger_lband()

            current_close = close.iloc[-1]
            current_upper = upper.iloc[-1] if not np.isnan(upper.iloc[-1]) else None
            current_middle = middle.iloc[-1] if not np.isnan(middle.iloc[-1]) else None
            current_lower = lower.iloc[-1] if not np.isnan(lower.iloc[-1]) else None

            # バンド位置分析
            band_position = self._analyze_bb_position(
                current_close, current_upper, current_middle, current_lower
            )

            # バンドウォーク検出
            band_walk = self._detect_band_walk(close, upper, lower, periods=5)

            # バンド幅分析
            band_width = (
                ((current_upper - current_lower) / current_middle) * 100
                if current_middle
                else None
            )

            result = {
                "indicator": "Bollinger Bands",
                "timeframe": timeframe,
                "parameters": f"BB({self.bb_period},{self.bb_std})",
                "current_price": round(current_close, 4),
                "upper_band": round(current_upper, 4) if current_upper else None,
                "middle_band": round(current_middle, 4) if current_middle else None,
                "lower_band": round(current_lower, 4) if current_lower else None,
                "band_position": band_position,
                "band_walk": band_walk,
                "band_width_percent": round(band_width, 2) if band_width else None,
                "timestamp": datetime.now(self.jst).isoformat(),
                "data_points": len(data),
            }

            logger.info(f"Bollinger Bands calculated for {timeframe}: {band_position}")
            return result

        except Exception as e:
            logger.error(f"Bollinger Bands calculation error: {str(e)}")
            return {"error": str(e)}

    def calculate_moving_averages(
        self,
        data: pd.DataFrame,
        timeframe: str = "D1",
        ma_type: str = "SMA",
        period: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        移動平均線計算

        Args:
            data: OHLCV データ
            timeframe: 時間軸
            ma_type: 移動平均線タイプ ("SMA" or "EMA")
            period: 指定期間（Noneの場合はデフォルト値を使用）

        Returns:
            Dict: 移動平均線値と分析結果
        """
        try:
            # データがnumpy配列の場合はDataFrameに変換
            if isinstance(data, np.ndarray):
                logger.warning("Data is numpy array, converting to DataFrame")
                return {"error": "データ形式エラー: DataFrameが必要"}

            # データが辞書の場合はDataFrameに変換を試行
            if isinstance(data, dict):
                try:
                    data = pd.DataFrame(data)
                except Exception as e:
                    logger.error(f"Failed to convert dict to DataFrame: {str(e)}")
                    return {"error": "データ変換エラー"}

            # 期間の決定
            if period is not None:
                # 指定された期間で単一の移動平均を計算
                ma_period = period
                required_periods = ma_period + 10

                if len(data) < required_periods:
                    logger.warning(
                        f"Insufficient data for Moving Average: {len(data)} < {required_periods}"
                    )
                    return {"error": f"データ不足（{required_periods}件必要）"}

                # Close列が存在するかチェック
                if "Close" not in data.columns:
                    logger.error("Close column not found in data")
                    return {"error": "Close列が見つかりません"}

                close = data["Close"]
                current_price = close.iloc[-1]

                # 指定された期間の移動平均を計算
                if ma_type.upper() == "EMA":
                    ma_value = ta.trend.EMAIndicator(
                        close, window=ma_period
                    ).ema_indicator()
                else:
                    ma_value = ta.trend.SMAIndicator(
                        close, window=ma_period
                    ).sma_indicator()

                current_ma = (
                    ma_value.iloc[-1] if not np.isnan(ma_value.iloc[-1]) else None
                )
                previous_ma = (
                    ma_value.iloc[-2]
                    if len(ma_value) > 1 and not np.isnan(ma_value.iloc[-2])
                    else None
                )

                # 移動平均の位置関係を分析
                ma_position = self._analyze_single_ma_position(
                    current_price, current_ma
                )

                # 移動平均の傾きを分析
                ma_slope = self._analyze_single_ma_slope(ma_value, periods=5)

                # 結果を返す
                result = {
                    "indicator": f"Moving Average ({ma_type.upper()})",
                    "timeframe": timeframe,
                    "parameters": f"{ma_type.upper()}({ma_period})",
                    "current_price": round(current_price, 4),
                    f"ma_{ma_period}": round(current_ma, 4) if current_ma else None,
                    "ma_position": ma_position,
                    "ma_slope": ma_slope,
                    "timestamp": datetime.now(self.jst).isoformat(),
                    "data_points": len(data),
                }

                # 期間に応じてキーを設定
                if ma_period == 200:
                    result["ma_long"] = result[f"ma_{ma_period}"]
                elif ma_period == 50:
                    result["ma_medium"] = result[f"ma_{ma_period}"]
                elif ma_period == 20:
                    result["ma_short"] = result[f"ma_{ma_period}"]

                return result

            else:
                # 従来の3期間（短期20, 中期50, 長期200）での計算
                required_periods = self.ma_long + 10
                if len(data) < required_periods:
                    logger.warning(
                        f"Insufficient data for Moving Averages: {len(data)} < {required_periods}"
                    )
                    return {"error": f"データ不足（{required_periods}件必要）"}

                # Close列が存在するかチェック
                if "Close" not in data.columns:
                    logger.error("Close column not found in data")
                    return {"error": "Close列が見つかりません"}

                close = data["Close"]
                current_price = close.iloc[-1]

                # 各期間の移動平均を計算
                ma_short = ta.trend.SMAIndicator(
                    close, window=self.ma_short
                ).sma_indicator()
                ma_medium = ta.trend.SMAIndicator(
                    close, window=self.ma_medium
                ).sma_indicator()
                ma_long = ta.trend.SMAIndicator(
                    close, window=self.ma_long
                ).sma_indicator()

                # 現在値を取得
                current_ma_short = (
                    ma_short.iloc[-1] if not np.isnan(ma_short.iloc[-1]) else None
                )
                current_ma_medium = (
                    ma_medium.iloc[-1] if not np.isnan(ma_medium.iloc[-1]) else None
                )
                current_ma_long = (
                    ma_long.iloc[-1] if not np.isnan(ma_long.iloc[-1]) else None
                )

                # 前回値を取得
                previous_ma_short = (
                    ma_short.iloc[-2]
                    if len(ma_short) > 1 and not np.isnan(ma_short.iloc[-2])
                    else None
                )
                previous_ma_medium = (
                    ma_medium.iloc[-2]
                    if len(ma_medium) > 1 and not np.isnan(ma_medium.iloc[-2])
                    else None
                )
                previous_ma_long = (
                    ma_long.iloc[-2]
                    if len(ma_long) > 1 and not np.isnan(ma_long.iloc[-2])
                    else None
                )

                # 移動平均の位置関係を分析
                ma_position = self._analyze_ma_position(
                    current_price, current_ma_short, current_ma_medium, current_ma_long
                )

                # 移動平均の傾きを分析
                ma_slope = self._analyze_ma_slope(
                    ma_short, ma_medium, ma_long, periods=5
                )

                # ゴールデンクロス・デッドクロス検出
                cross_signals = self._detect_ma_crosses(
                    ma_short,
                    ma_medium,
                    ma_long,
                    previous_ma_short,
                    previous_ma_medium,
                    previous_ma_long,
                )

                # サポート・レジスタンスレベル
                support_resistance = self._identify_ma_support_resistance(
                    current_ma_short, current_ma_medium, current_ma_long
                )

                result = {
                    "indicator": "Moving Averages",
                    "timeframe": timeframe,
                    "parameters": f"MA({self.ma_short},{self.ma_medium},{self.ma_long})",
                    "current_price": round(current_price, 4),
                    "ma_short": (
                        round(current_ma_short, 4) if current_ma_short else None
                    ),
                    "ma_medium": (
                        round(current_ma_medium, 4) if current_ma_medium else None
                    ),
                    "ma_long": round(current_ma_long, 4) if current_ma_long else None,
                    "ma_position": ma_position,
                    "ma_slope": ma_slope,
                    "cross_signals": cross_signals,
                    "support_resistance": support_resistance,
                    "timestamp": datetime.now(self.jst).isoformat(),
                    "data_points": len(data),
                }

                return result

        except Exception as e:
            logger.error(f"Moving Averages calculation error: {str(e)}")
            return {"error": f"計算エラー: {str(e)}"}

    def multi_timeframe_analysis(
        self, data_dict: Dict[str, pd.DataFrame]
    ) -> Dict[str, Any]:
        """
        マルチタイムフレーム分析

        Args:
            data_dict: {"D1": df, "H4": df, "H1": df, "M5": df}

        Returns:
            Dict: 総合分析結果
        """
        try:
            analysis_result = {
                "analysis_type": "Multi-Timeframe Technical Analysis",
                "timestamp": datetime.now(self.jst).isoformat(),
                "timeframes": {},
            }

            # D1: RSI + MACD (大局判断) - MACDに必要なデータが不足の場合は長期データを取得
            if "D1" in data_dict:
                d1_analysis = {}
                d1_rsi = self.calculate_rsi(data_dict["D1"], "D1")

                # MACD計算に必要なデータ量チェック
                required_periods = max(self.macd_slow, self.macd_signal) + 10
                if len(data_dict["D1"]) < required_periods:
                    logger.warning(
                        f"D1 MACD: データ不足 {len(data_dict['D1'])} < {required_periods}. 長期データ取得を推奨"
                    )
                    d1_macd = {
                        "indicator": "MACD",
                        "timeframe": "D1",
                        "error": f"データ不足 ({len(data_dict['D1'])}件 < {required_periods}件必要)",
                        "recommendation": "3ヶ月以上の履歴データで再分析してください",
                    }
                else:
                    d1_macd = self.calculate_macd(data_dict["D1"], "D1")

                d1_analysis["RSI"] = d1_rsi
                d1_analysis["MACD"] = d1_macd
                d1_analysis["purpose"] = "大局判断"
                analysis_result["timeframes"]["D1"] = d1_analysis

            # H4: RSI + ボリンジャーバンド (戦術)
            if "H4" in data_dict:
                h4_analysis = {}
                h4_rsi = self.calculate_rsi(data_dict["H4"], "H4")
                h4_bb = self.calculate_bollinger_bands(data_dict["H4"], "H4")
                h4_ma = self.calculate_moving_averages(data_dict["H4"], "H4")
                h4_analysis["RSI"] = h4_rsi
                h4_analysis["BollingerBands"] = h4_bb
                h4_analysis["MovingAverages"] = h4_ma
                h4_analysis["purpose"] = "戦術判断"
                analysis_result["timeframes"]["H4"] = h4_analysis

            # H1: RSI + ボリンジャーバンド (ゾーン)
            if "H1" in data_dict:
                h1_analysis = {}
                h1_rsi = self.calculate_rsi(data_dict["H1"], "H1")
                h1_bb = self.calculate_bollinger_bands(data_dict["H1"], "H1")
                h1_ma = self.calculate_moving_averages(data_dict["H1"], "H1")
                h1_analysis["RSI"] = h1_rsi
                h1_analysis["BollingerBands"] = h1_bb
                h1_analysis["MovingAverages"] = h1_ma
                h1_analysis["purpose"] = "ゾーン決定"
                analysis_result["timeframes"]["H1"] = h1_analysis

            # M5: RSI (タイミング)
            if "M5" in data_dict:
                m5_analysis = {}
                m5_rsi = self.calculate_rsi(data_dict["M5"], "M5")
                m5_analysis["RSI"] = m5_rsi
                m5_analysis["purpose"] = "タイミング"
                analysis_result["timeframes"]["M5"] = m5_analysis

            # 総合判断
            overall_signal = self._generate_overall_signal(analysis_result)
            analysis_result["overall_signal"] = overall_signal

            logger.info("Multi-timeframe analysis completed")
            return analysis_result

        except Exception as e:
            logger.error(f"Multi-timeframe analysis error: {str(e)}")
            return {"error": str(e)}

    def _classify_rsi_state(self, rsi_value: float) -> str:
        """RSI状態分類"""
        if rsi_value is None:
            return "unknown"
        elif rsi_value >= self.rsi_levels["overbought"]:
            return "overbought"
        elif rsi_value <= self.rsi_levels["oversold"]:
            return "oversold"
        else:
            return "neutral"

    def _analyze_rsi_signal(
        self, current: float, previous: float, timeframe: str
    ) -> str:
        """RSIシグナル分析"""
        if current is None or previous is None:
            return "no_signal"

        # レベルクロス判定
        if (
            previous < self.rsi_levels["oversold"]
            and current >= self.rsi_levels["oversold"]
        ):
            return "buy_signal"
        elif (
            previous > self.rsi_levels["overbought"]
            and current <= self.rsi_levels["overbought"]
        ):
            return "sell_signal"

        # M5での特別ルール
        if timeframe == "M5":
            if current >= self.rsi_levels["overbought"]:
                return "sell_timing"
            elif current <= self.rsi_levels["oversold"]:
                return "buy_timing"

        return "neutral"

    def _detect_rsi_divergence(
        self, data: pd.DataFrame, rsi: np.ndarray, periods: int = 5
    ) -> str:
        """RSIダイバージェンス検出（簡易版）"""
        try:
            # データ形式チェック
            if isinstance(data, np.ndarray):
                logger.warning("Data is numpy array in _detect_rsi_divergence")
                return "data_format_error"

            if not isinstance(data, pd.DataFrame):
                logger.warning("Data is not DataFrame in _detect_rsi_divergence")
                return "data_format_error"

            if len(data) < periods * 2:
                return "insufficient_data"

            # High列が存在するかチェック
            if "High" not in data.columns:
                logger.warning("High column not found in data for divergence detection")
                return "missing_high_column"

            recent_highs = data["High"].rolling(periods).max().iloc[-periods:]
            recent_rsi = rsi[-periods:]

            # 価格とRSIの方向性比較（簡易）
            price_trend = recent_highs.iloc[-1] - recent_highs.iloc[0]
            rsi_trend = recent_rsi.iloc[-1] - recent_rsi.iloc[0]

            if price_trend > 0 and rsi_trend < 0:
                return "bearish_divergence"
            elif price_trend < 0 and rsi_trend > 0:
                return "bullish_divergence"
            else:
                return "no_divergence"

        except Exception as e:
            logger.error(f"Error in _detect_rsi_divergence: {str(e)}")
            return "detection_error"

    def _analyze_macd_cross(
        self, macd: float, signal: float, prev_macd: float, prev_signal: float
    ) -> str:
        """MACDクロス分析"""
        if any(x is None for x in [macd, signal, prev_macd, prev_signal]):
            return "no_signal"

        # ゴールデンクロス
        if prev_macd <= prev_signal and macd > signal:
            return "golden_cross"
        # デッドクロス
        elif prev_macd >= prev_signal and macd < signal:
            return "dead_cross"
        else:
            return "no_cross"

    def _analyze_bb_position(
        self, price: float, upper: float, middle: float, lower: float
    ) -> str:
        """ボリンジャーバンド位置分析"""
        if any(x is None for x in [upper, middle, lower]):
            return "unknown"

        if price >= upper:
            return "above_upper_band"
        elif price <= lower:
            return "below_lower_band"
        elif price > middle:
            return "above_middle"
        else:
            return "below_middle"

    def _detect_band_walk(
        self, close: np.ndarray, upper: np.ndarray, lower: np.ndarray, periods: int = 5
    ) -> str:
        """バンドウォーク検出"""
        try:
            recent_close = close[-periods:]
            recent_upper = upper[-periods:]
            recent_lower = lower[-periods:]

            # 上バンドウォーク
            upper_touches = sum(recent_close >= recent_upper * 0.99)  # 99%以上
            if upper_touches >= periods * 0.6:  # 60%以上
                return "upper_band_walk"

            # 下バンドウォーク
            lower_touches = sum(recent_close <= recent_lower * 1.01)  # 101%以下
            if lower_touches >= periods * 0.6:
                return "lower_band_walk"

            return "no_band_walk"

        except Exception:
            return "detection_error"

    def _analyze_ma_position(
        self, price: float, ma_short: float, ma_medium: float, ma_long: float
    ) -> str:
        """移動平均線の位置関係を分析"""
        if any(x is None for x in [ma_short, ma_medium, ma_long]):
            return "unknown"

        # 理想的な上昇トレンド: 価格 > 短期 > 中期 > 長期
        if price > ma_short > ma_medium > ma_long:
            return "strong_uptrend"
        # 上昇トレンド: 短期 > 中期 > 長期
        elif ma_short > ma_medium > ma_long:
            return "uptrend"
        # 理想的な下降トレンド: 価格 < 短期 < 中期 < 長期
        elif price < ma_short < ma_medium < ma_long:
            return "strong_downtrend"
        # 下降トレンド: 短期 < 中期 < 長期
        elif ma_short < ma_medium < ma_long:
            return "downtrend"
        # 揉み合い
        else:
            return "sideways"

    def _analyze_ma_slope(
        self,
        ma_short: pd.Series,
        ma_medium: pd.Series,
        ma_long: pd.Series,
        periods: int = 5,
    ) -> Dict[str, str]:
        """移動平均線の傾きを分析"""
        try:
            recent_short = ma_short[-periods:]
            recent_medium = ma_medium[-periods:]
            recent_long = ma_long[-periods:]

            # 傾き計算（簡易版）
            short_slope = (
                "up" if recent_short.iloc[-1] > recent_short.iloc[0] else "down"
            )
            medium_slope = (
                "up" if recent_medium.iloc[-1] > recent_medium.iloc[0] else "down"
            )
            long_slope = "up" if recent_long.iloc[-1] > recent_long.iloc[0] else "down"

            return {
                "short_slope": short_slope,
                "medium_slope": medium_slope,
                "long_slope": long_slope,
                "trend_alignment": (
                    "aligned"
                    if short_slope == medium_slope == long_slope
                    else "diverging"
                ),
            }

        except Exception:
            return {
                "short_slope": "unknown",
                "medium_slope": "unknown",
                "long_slope": "unknown",
                "trend_alignment": "unknown",
            }

    def _detect_ma_crosses(
        self,
        ma_short: pd.Series,
        ma_medium: pd.Series,
        ma_long: pd.Series,
        prev_short: float,
        prev_medium: float,
        prev_long: float,
    ) -> Dict[str, str]:
        """移動平均線のクロス検出"""
        signals = {}

        # 短期と中期のクロス
        if prev_short and prev_medium:
            if prev_short <= prev_medium and ma_short.iloc[-1] > ma_medium.iloc[-1]:
                signals["short_medium"] = "golden_cross"
            elif prev_short >= prev_medium and ma_short.iloc[-1] < ma_medium.iloc[-1]:
                signals["short_medium"] = "dead_cross"
            else:
                signals["short_medium"] = "no_cross"

        # 中期と長期のクロス
        if prev_medium and prev_long:
            if prev_medium <= prev_long and ma_medium.iloc[-1] > ma_long.iloc[-1]:
                signals["medium_long"] = "golden_cross"
            elif prev_medium >= prev_long and ma_medium.iloc[-1] < ma_long.iloc[-1]:
                signals["medium_long"] = "dead_cross"
            else:
                signals["medium_long"] = "no_cross"

        # 短期と長期のクロス
        if prev_short and prev_long:
            if prev_short <= prev_long and ma_short.iloc[-1] > ma_long.iloc[-1]:
                signals["short_long"] = "golden_cross"
            elif prev_short >= prev_long and ma_short.iloc[-1] < ma_long.iloc[-1]:
                signals["short_long"] = "dead_cross"
            else:
                signals["short_long"] = "no_cross"

        return signals

    def _identify_ma_support_resistance(
        self, ma_short: float, ma_medium: float, ma_long: float
    ) -> Dict[str, float]:
        """移動平均線をサポート・レジスタンスとして識別"""
        levels = {}

        if ma_short:
            levels["ma_20"] = round(ma_short, 4)
        if ma_medium:
            levels["ma_50"] = round(ma_medium, 4)
        if ma_long:
            levels["ma_200"] = round(ma_long, 4)

        return levels

    def _generate_overall_signal(self, analysis: Dict[str, Any]) -> Dict[str, Any]:
        """総合シグナル生成"""
        signals = []

        # 各時間軸からシグナル抽出
        for tf, data in analysis.get("timeframes", {}).items():
            if "RSI" in data and "signal" in data["RSI"]:
                rsi_signal = data["RSI"]["signal"]
                if rsi_signal not in ["neutral", "no_signal"]:
                    signals.append(f"{tf}_RSI_{rsi_signal}")

            if "MACD" in data and "cross_signal" in data["MACD"]:
                macd_signal = data["MACD"]["cross_signal"]
                if macd_signal not in ["no_cross", "no_signal"]:
                    signals.append(f"{tf}_MACD_{macd_signal}")

            if "MovingAverages" in data and "cross_signals" in data["MovingAverages"]:
                ma_crosses = data["MovingAverages"]["cross_signals"]
                for cross_type, cross_signal in ma_crosses.items():
                    if cross_signal not in ["no_cross"]:
                        signals.append(f"{tf}_MA_{cross_type}_{cross_signal}")

        # 総合判断ロジック（簡易版）
        buy_signals = len([s for s in signals if "buy" in s or "golden" in s])
        sell_signals = len([s for s in signals if "sell" in s or "dead" in s])

        if buy_signals > sell_signals:
            overall = "bullish"
        elif sell_signals > buy_signals:
            overall = "bearish"
        else:
            overall = "neutral"

        return {
            "direction": overall,
            "signal_count": len(signals),
            "buy_signals": buy_signals,
            "sell_signals": sell_signals,
            "confidence": min(abs(buy_signals - sell_signals) * 20, 100),
        }

    def display_analysis_table(
        self, analysis: Dict[str, Any], currency_pair: str = "USD/JPY"
    ) -> None:
        """分析結果をテーブル表示"""
        self.console.print(f"\n📊 Technical Analysis Report - {currency_pair}")

        for timeframe, data in analysis.get("timeframes", {}).items():
            table = Table(title=f"⏰ {timeframe} - {data.get('purpose', '')}")
            table.add_column("指標", style="cyan")
            table.add_column("値", style="green")
            table.add_column("状態", style="yellow")
            table.add_column("シグナル", style="red")

            if "RSI" in data:
                rsi = data["RSI"]
                table.add_row(
                    "RSI(14)",
                    str(rsi.get("current_value", "N/A")),
                    rsi.get("state", "N/A"),
                    rsi.get("signal", "N/A"),
                )

            if "MACD" in data:
                macd = data["MACD"]
                table.add_row(
                    "MACD(12,26,9)",
                    f"{macd.get('macd_line', 'N/A')}",
                    macd.get("zero_line_position", "N/A"),
                    macd.get("cross_signal", "N/A"),
                )

            if "BollingerBands" in data:
                bb = data["BollingerBands"]
                table.add_row(
                    "BB(20,2)",
                    f"{bb.get('current_price', 'N/A')}",
                    bb.get("band_position", "N/A"),
                    bb.get("band_walk", "N/A"),
                )

            if "MovingAverages" in data:
                ma = data["MovingAverages"]
                # 3つの期間すべての値を表示
                ma_values = (
                    f"20:{ma.get('ma_short', 'N/A')} | "
                    f"50:{ma.get('ma_medium', 'N/A')} | "
                    f"200:{ma.get('ma_long', 'N/A')}"
                )

                # クロスシグナルを取得
                cross_signals = ma.get("cross_signals", {})
                cross_info = []
                if cross_signals.get("short_medium") != "no_cross":
                    cross_info.append(
                        f"20-50:{cross_signals.get('short_medium', 'N/A')}"
                    )
                if cross_signals.get("medium_long") != "no_cross":
                    cross_info.append(
                        f"50-200:{cross_signals.get('medium_long', 'N/A')}"
                    )

                signal_display = " | ".join(cross_info) if cross_info else "no_cross"

                table.add_row(
                    "MA(20,50,200)",
                    f"{ma.get('current_price', 'N/A')}",
                    ma.get("ma_position", "N/A"),
                    f"{ma_values}\n{signal_display}",
                )

            self.console.print(table)

        # 総合シグナル表示
        overall = analysis.get("overall_signal", {})
        if overall:
            signal_panel = Panel.fit(
                f"方向: {overall.get('direction', 'N/A')}\n"
                f"信頼度: {overall.get('confidence', 0)}%\n"
                f"シグナル数: {overall.get('signal_count', 0)}",
                title="🎯 総合判断",
            )
            self.console.print(signal_panel)

    def _analyze_single_ma_position(self, price: float, ma_value: float) -> str:
        """
        単一移動平均線の位置関係を分析

        Args:
            price: 現在価格
            ma_value: 移動平均値

        Returns:
            str: 位置関係の分析結果
        """
        if ma_value is None:
            return "unknown"

        if price > ma_value:
            return "uptrend"
        elif price < ma_value:
            return "downtrend"
        else:
            return "neutral"

    def _analyze_single_ma_slope(self, ma_series: pd.Series, periods: int = 5) -> str:
        """
        単一移動平均線の傾きを分析

        Args:
            ma_series: 移動平均線の時系列データ
            periods: 分析期間

        Returns:
            str: 傾きの分析結果
        """
        if len(ma_series) < periods + 1:
            return "insufficient_data"

        recent_values = ma_series.tail(periods + 1).dropna()
        if len(recent_values) < 2:
            return "insufficient_data"

        # 線形回帰で傾きを計算
        x = np.arange(len(recent_values))
        y = recent_values.values
        slope = np.polyfit(x, y, 1)[0]

        if slope > 0.001:
            return "rising"
        elif slope < -0.001:
            return "falling"
        else:
            return "flat"
