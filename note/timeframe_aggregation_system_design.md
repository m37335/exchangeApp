# 時間足集計システム設計書

## 📋 プロジェクト概要

**プロジェクト名**: Exchange Analytics System - 時間足集計システム  
**作成日**: 2025 年 8 月 15 日  
**バージョン**: 1.0.0  
**目的**: 5 分足データから 1 時間足、4 時間足、日足を自動集計・保存するシステム

---

## 🎯 システム要件

### 基本要件

- 5 分足データを基に各時間足を自動集計
- リアルタイム性よりもデータ完全性を重視
- シンプルで保守性の高い設計
- PostgreSQL データベースでの管理

### 技術要件

- **処理時間**: 各集計 60 秒以内
- **メモリ使用量**: 200MB 以内
- **データ整合性**: 重複回避・エラーハンドリング
- **実行環境**: Docker コンテナ内の crontab

---

## 🏗️ システム設計

### アーキテクチャ

```
Yahoo Finance API
       ↓
5分足データ取得 (simple_data_fetcher.py)
       ↓
price_dataテーブル (yahoo_finance_5m_continuous)
       ↓
各時間足集計スクリプト
       ↓
price_dataテーブル (各時間足データ)
```

### データフロー

1. **5 分足取得**: 5 分間隔で Yahoo Finance からデータ取得
2. **1 時間足集計**: 毎時 05 分に前 1 時間分を集計
3. **4 時間足集計**: 4 時間ごと 05 分に前 4 時間分を集計
4. **日足集計**: 毎日 00:05 に前日分を集計

---

## 📅 実行スケジュール

### crontab 設定

```bash
# 5分足データ取得（既存）
*/5 * * * 1-5 cd /app && export $(cat .env | grep -v '^#' | xargs) && timeout 300 python scripts/cron/simple_data_fetcher.py >> /app/logs/simple_data_fetcher.log 2>&1

# 1時間足集計（新規）
5 * * * 1-6 cd /app && export $(cat .env | grep -v '^#' | xargs) && timeout 120 python scripts/cron/hourly_aggregator.py >> /app/logs/hourly_aggregator.log 2>&1

# 4時間足集計（新規）
5 */4 * * 1-6 cd /app && export $(cat .env | grep -v '^#' | xargs) && timeout 180 python scripts/cron/four_hour_aggregator.py >> /app/logs/four_hour_aggregator.log 2>&1

# 日足集計（新規）
5 0 * * 1-6 cd /app && export $(cat .env | grep -v '^#' | xargs) && timeout 300 python scripts/cron/daily_aggregator.py >> /app/logs/daily_aggregator.log 2>&1
```

### 実行タイミング詳細

- **1 時間足**: 毎時 05 分（月-土）
- **4 時間足**: 00:05, 04:05, 08:05, 12:05, 16:05, 20:05（月-土）
- **日足**: 毎日 00:05（月-土）

### 為替市場営業時間の考慮

- **月曜日**: 日本時間 07:00 開始
- **金曜日**: 日本時間 06:00 終了
- **土日**: 休場
- **土曜日実行**: 金曜日データの確定を待つため、土曜日も実行

---

## 🗄️ データベース設計

### テーブル構造

```sql
-- price_dataテーブル（既存）
CREATE TABLE price_data (
    id SERIAL PRIMARY KEY,
    currency_pair VARCHAR(10) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    data_timestamp TIMESTAMP WITH TIME ZONE,
    fetched_at TIMESTAMP WITH TIME ZONE,
    open_price NUMERIC(10,5) NOT NULL,
    high_price NUMERIC(10,5) NOT NULL,
    low_price NUMERIC(10,5) NOT NULL,
    close_price NUMERIC(10,5) NOT NULL,
    volume BIGINT,
    data_source VARCHAR(50) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL,
    version INTEGER NOT NULL DEFAULT 1
);
```

### データソース識別

- `yahoo_finance_5m_continuous`: 5 分足データ（継続取得）
- `yahoo_finance_1h_aggregated`: 1 時間足データ（集計）
- `yahoo_finance_4h_aggregated`: 4 時間足データ（集計）
- `yahoo_finance_1d_aggregated`: 日足データ（集計）

### 制約・インデックス

```sql
-- ユニーク制約
UNIQUE(currency_pair, timestamp, data_source)

-- インデックス
INDEX idx_price_data_timestamp (timestamp DESC)
INDEX idx_price_data_currency (currency_pair)
INDEX idx_price_data_currency_timestamp_composite (currency_pair, timestamp DESC)
```

---

## 📊 集計ロジック

### OHLCV 計算方法

```python
# 1時間足集計例
def aggregate_1h_data(start_time, end_time):
    # 期間内の5分足データを取得
    # 始値: 期間最初の5分足の始値
    # 高値: 期間内の5分足の最高値
    # 安値: 期間内の5分足の最低値
    # 終値: 期間最後の5分足の終値
    # 取引量: 期間内の5分足の合計
```

### SQL 集計クエリ例

```sql
-- 1時間足集計
SELECT
    DATE_TRUNC('hour', timestamp) as hour_timestamp,
    FIRST_VALUE(open_price) OVER (PARTITION BY DATE_TRUNC('hour', timestamp) ORDER BY timestamp) as open_price,
    MAX(high_price) as high_price,
    MIN(low_price) as low_price,
    LAST_VALUE(close_price) OVER (PARTITION BY DATE_TRUNC('hour', timestamp) ORDER BY timestamp) as close_price,
    SUM(volume) as volume
FROM price_data
WHERE data_source = 'yahoo_finance_5m_continuous'
    AND timestamp >= '2025-08-15 00:00:00+09'
    AND timestamp < '2025-08-15 01:00:00+09'
GROUP BY DATE_TRUNC('hour', timestamp)
```

### 重複回避

- `(currency_pair, timestamp, data_source)`の複合ユニーク制約
- 既存データの確認後、新規挿入または更新
- エラーハンドリングによる重複処理

---

## 🔧 実装計画

### Phase 1: 1 時間足集計（優先度: 高）

- [ ] `hourly_aggregator.py`スクリプト作成
- [ ] 集計ロジック実装
- [ ] エラーハンドリング実装
- [ ] テスト実行
- [ ] crontab 設定追加

### Phase 2: 4 時間足集計（優先度: 中）

- [ ] `four_hour_aggregator.py`スクリプト作成
- [ ] 集計ロジック実装
- [ ] テスト実行
- [ ] crontab 設定追加

### Phase 3: 日足集計（優先度: 中）

- [ ] `daily_aggregator.py`スクリプト作成
- [ ] 集計ロジック実装
- [ ] テスト実行
- [ ] crontab 設定追加

### Phase 4: 統合テスト（優先度: 高）

- [ ] 全時間足の動作確認
- [ ] パフォーマンステスト
- [ ] エラー処理テスト
- [ ] 本番環境デプロイ

---

## 📁 ファイル構成

### 新規作成ファイル

```
/app/scripts/cron/
├── hourly_aggregator.py      # 1時間足集計スクリプト
├── four_hour_aggregator.py   # 4時間足集計スクリプト
└── daily_aggregator.py       # 日足集計スクリプト

/app/logs/
├── hourly_aggregator.log     # 1時間足集計ログ
├── four_hour_aggregator.log  # 4時間足集計ログ
└── daily_aggregator.log      # 日足集計ログ
```

### 更新ファイル

```
/app/current_crontab.txt      # crontab設定更新
```

---

## 📈 監視・ログ

### ログファイル

- `/app/logs/hourly_aggregator.log`
- `/app/logs/four_hour_aggregator.log`
- `/app/logs/daily_aggregator.log`

### 監視項目

- 実行時間
- 処理件数
- エラー発生率
- データ整合性

### ログ形式

```python
# 成功ログ例
2025-08-15 01:05:00 - INFO - 1時間足集計開始: 2025-08-15 00:00:00+09:00
2025-08-15 01:05:02 - INFO - 集計完了: 12件の5分足から1時間足を生成
2025-08-15 01:05:03 - INFO - データベース保存完了: 1件

# エラーログ例
2025-08-15 01:05:00 - ERROR - データベース接続エラー: connection timeout
2025-08-15 01:05:00 - ERROR - 集計処理エラー: insufficient data
```

---

## ⚠️ 制約・注意事項

### 技術制約

- 処理時間: 各集計 60 秒以内
- メモリ使用量: 200MB 以内
- データベース接続: 非同期処理
- タイムアウト: crontab の timeout 設定

### 運用制約

- 為替市場営業時間外のデータ取得
- 土曜日のデータ確定待ち
- システムメンテナンス時の停止
- データベース負荷の考慮

### エラーハンドリング

- データ不足時の処理
- データベース接続エラー
- 重複データの処理
- 部分的な失敗時の対応

---

## 🧪 テスト計画

### 単体テスト

- 集計ロジックの正確性
- エラーハンドリング
- データ型変換
- 重複回避機能

### 統合テスト

- データベース接続
- crontab 実行
- ログ出力
- パフォーマンス

### 本番テスト

- 実際のデータでの動作確認
- 長時間実行の安定性
- エラー発生時の復旧
- データ整合性の確認

---

## 📊 パフォーマンス目標

### 処理時間

- 1 時間足集計: 10 秒以内
- 4 時間足集計: 15 秒以内
- 日足集計: 20 秒以内
- 合計処理時間: 60 秒以内

### メモリ使用量

- 各集計スクリプト: 50MB 以内
- 合計メモリ使用量: 200MB 以内

### データ処理量

- 1 時間足: 12 件の 5 分足から 1 件の 1 時間足
- 4 時間足: 48 件の 5 分足から 1 件の 4 時間足
- 日足: 288 件の 5 分足から 1 件の日足

---

## 🔄 更新履歴

| 日付       | バージョン | 更新内容 | 担当者 |
| ---------- | ---------- | -------- | ------ |
| 2025-08-15 | 1.0.0      | 初版作成 | -      |

---

## 📞 連絡先・参考資料

### 関連ドキュメント

- [Exchange Analytics System CLI 機能説明書](../docs/2025-08-15_CLI機能_ExchangeAnalyticsSystem_CLI機能説明書.md)
- [PostgreSQL 移行ガイド](../data/POSTGRESQL_BASE_DATA_README.md)

### 技術スタック

- **言語**: Python 3.9+
- **データベース**: PostgreSQL 13+
- **ORM**: SQLAlchemy (asyncio)
- **スケジューラー**: crontab
- **ログ**: Python logging

---

_このドキュメントは継続的に更新されます。最新版は常にこのファイルを参照してください。_
