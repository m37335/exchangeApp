# 🚀 Exchange Analytics CLI ユーザーガイド

**Exchange Analytics System - 通貨分析システム管理 CLI**

## 📋 目次

1. [概要](#概要)
2. [基本コマンド](#基本コマンド)
3. [システム監視コマンド](#システム監視コマンド)
4. [データ管理コマンド](#データ管理コマンド)
5. [AI 分析コマンド](#ai分析コマンド)
6. [設定管理コマンド](#設定管理コマンド)
7. [API 管理コマンド](#api管理コマンド)
8. [アラート設定コマンド](#アラート設定コマンド)
9. [システム復旧コマンド](#システム復旧コマンド)
10. [使用例とベストプラクティス](#使用例とベストプラクティス)
11. [トラブルシューティング](#トラブルシューティング)

---

## 概要

Exchange Analytics CLI は、通貨分析システムの管理・運用を行うコマンドラインツールです。システムの監視、データ管理、AI 分析、設定管理など、包括的な機能を提供します。

### 基本構文

```bash
./exchange-analytics [OPTIONS] COMMAND [ARGS]...
```

### オプション

- `--version`, `-v`: バージョン情報を表示
- `--verbose`, `-V`: 詳細ログを表示
- `--config`, `-c PATH`: 設定ファイルパス
- `--help`, `-h`: ヘルプを表示

---

## 基本コマンド

### 1. システム全体のステータス確認

```bash
./exchange-analytics status
```

**機能**: システム全体の状態を確認
**出力例**:

```
🔍 システムステータス確認中...
                         📊 System Status
┏━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Component            ┃ Status     ┃ Details                    ┃
┡━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ Domain Layer         │ ✅ Healthy │ Models & Entities Ready    │
│ Application Layer    │ ✅ Healthy │ Services & Use Cases Ready │
│ Infrastructure Layer │ ✅ Healthy │ DB, Cache, APIs Ready      │
│ Presentation Layer   │ ✅ Healthy │ REST API, CLI Ready        │
│ Cron Service         │ ✅ Healthy │ Running                    │
│ PostgreSQL           │ ✅ Healthy │ Running                    │
│ Redis Cache          │ ✅ Healthy │ Running                    │
│ API Server           │ ✅ Healthy │ Running                    │
└──────────────────────┴────────────┴────────────────────────────┘
```

### 2. システム情報表示

```bash
./exchange-analytics info
```

**機能**: システムの基本情報を表示
**出力例**:

```
            🔧 System Information
┏━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ Property          ┃ Value                  ┃
┡━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━┩
│ System            │ Linux 6.10.14-linuxkit │
│ Python Version    │ 3.11.13                │
│ Architecture      │ x86_64                 │
│ Current Time      │ 2025-09-06 00:39:07    │
│ Working Directory │ /app                   │
│ Log Directory     │ logs/                  │
│ Config Directory  │ config/                │
└───────────────────┴────────────────────────┘
```

---

## システム監視コマンド

### 1. システムヘルスチェック

```bash
./exchange-analytics system health [OPTIONS]
```

**機能**: システムのヘルスチェックを実行
**オプション**:

- `--host`, `-h TEXT`: ホスト [default: localhost]
- `--port`, `-p INTEGER`: ポート [default: 8000]
- `--detailed`, `-d`: 詳細ヘルスチェック
- `--continuous`, `-c`: 継続監視
- `--interval`, `-i INTEGER`: 監視間隔（秒） [default: 5]

**出力例**:

```
🏥 ヘルスチェック実行中... (http://localhost:8000)
╭─ 🏥 Health Check Results ──╮
│ Status: healthy            │
│ ⏰ Timestamp: None         │
│ 📦 Version: 1.0.0          │
│ 🔧 Service: exchanging-app │
╰────────────────────────────╯
```

### 2. アクティブなアラート表示

```bash
./exchange-analytics system alerts
```

**機能**: 現在アクティブなアラートを表示

### 3. ログ監視・表示

```bash
./exchange-analytics system logs
```

**機能**: システムログの監視・表示

### 4. システムメトリクス監視

```bash
./exchange-analytics system metrics
```

**機能**: システムメトリクスの監視

---

## データ管理コマンド

### 1. データ表示

#### データベースのデータを表示

```bash
./exchange-analytics data show list [OPTIONS]
```

**機能**: データベースのデータを表示
**オプション**:

- `--limit`, `-l INTEGER`: 表示件数 [default: 30]
- `--pair`, `-p TEXT`: 通貨ペア [default: USD/JPY]
- `--table`, `-t TEXT`: テーブル名 [default: price_data]
- `--timeframe`, `-tf TEXT`: 時間足 (5m, 1h, 4h, 1d) [default: 5m]
- `--source`, `-s TEXT`: データソース (real, aggregated, ongoing, all) [default: all]
- `--indicator-type`, `-it TEXT`: 指標タイプ (RSI, MACD, SMA 等)
- `--period`, `-pr FLOAT`: 指標期間

**使用例**:

```bash
# 基本のデータ表示
./exchange-analytics data show list

# 特定のテーブルのデータ表示
./exchange-analytics data show list --table price_data --limit 50

# テクニカル指標の表示
./exchange-analytics data show list --table technical_indicators --indicator-type RSI
```

#### データベースの状態を表示

```bash
./exchange-analytics data show status
```

**機能**: データベースの状態を表示
**出力例**:

```
📊 データベース状態確認中...
                   📊 データベース状態
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ 項目               ┃ 値                               ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ データベース       │ PostgreSQL                       │
│ データベース名     │ exchange_analytics_production_db │
│ ユーザー           │ exchange_analytics_user          │
│ バージョン         │ PostgreSQL                       │
│ データベースサイズ │ 6520 MB                          │
└────────────────────┴──────────────────────────────────┘
```

### 2. データ取得

#### 為替レートデータを取得

```bash
./exchange-analytics data fetch fetch [OPTIONS]
```

**機能**: 為替レートデータを取得
**オプション**:

- `--pairs`, `-p TEXT`: 通貨ペア（カンマ区切り） [default: USD/JPY,EUR/USD,GBP/JPY]
- `--source`, `-s TEXT`: データソース [default: alpha_vantage]
- `--interval`, `-i TEXT`: 時間間隔 [default: 1min]
- `--days`, `-d INTEGER`: 取得日数 [default: 7]
- `--force`, `-f`: 強制実行

**使用例**:

```bash
# 基本のデータ取得
./exchange-analytics data fetch fetch

# 複数通貨ペアのデータ取得
./exchange-analytics data fetch fetch --pairs "USD/JPY,EUR/USD" --days 30

# 特定ソースからのデータ取得
./exchange-analytics data fetch fetch --source "fixer" --interval "1hour"
```

#### システム初期化

```bash
./exchange-analytics data fetch init
```

**機能**: システム初期化（基盤データ復元 + 差分データ取得）

#### 基盤データ復元

```bash
./exchange-analytics data fetch restore-base
```

**機能**: 基盤データを復元（SQLite バックアップから）

#### 差分データ更新

```bash
./exchange-analytics data fetch update
```

**機能**: 差分データを取得・更新

### 3. バックアップ・復元

```bash
./exchange-analytics data backup [OPTIONS]
```

**機能**: データのバックアップ・復元

### 4. 計算・分析

```bash
./exchange-analytics data calc [OPTIONS]
```

**機能**: データの計算・分析

### 5. データ管理

```bash
./exchange-analytics data manage [OPTIONS]
```

**機能**: データの管理操作

---

## AI 分析コマンド

### 1. 統合 AI 分析レポート生成

```bash
./exchange-analytics ai analyze [OPTIONS]
```

**機能**: 統合 AI 分析レポートを生成（TA-Lib 標準版）
**オプション**:

- `--test`: テストモード（Discord 送信なし）
- `--no-optimization`: 最適化機能を無効にする
- `--chart`: H1 チャートを生成する
- `--force`, `-f`: 確認をスキップ

**使用例**:

```bash
# 基本のAI分析
./exchange-analytics ai analyze

# テストモードでの分析
./exchange-analytics ai analyze --test

# チャート付きの分析
./exchange-analytics ai analyze --chart
```

### 2. Discord 通知テスト

```bash
./exchange-analytics ai discord-test
```

**機能**: Discord 通知のテスト

### 3. AI 分析レポート一覧表示

```bash
./exchange-analytics ai reports [OPTIONS]
```

**機能**: AI 分析レポートの一覧表示
**オプション**:

- `--limit`, `-n INTEGER`: 表示件数 [default: 10]
- `--pair`, `-p TEXT`: 通貨ペアフィルタ

**使用例**:

```bash
# 基本のレポート一覧
./exchange-analytics ai reports

# 件数制限付きレポート一覧
./exchange-analytics ai reports --limit 5

# 特定通貨ペアのレポート一覧
./exchange-analytics ai reports --pair USD/JPY
```

---

## 設定管理コマンド

### 1. 設定表示

```bash
./exchange-analytics config show
```

**機能**: 現在の設定を表示
**出力例**:

```
⚙️ 設定表示 (環境: default)
                                ⚙️ Configuration Settings (default)
┏━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━┓
┃ Category ┃ Key                          ┃ Value                                          ┃ Type ┃
┡━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━┩
│ api      │ api.alpha_vantage.api_key    │ ****hidden****                                 │ str  │
│ api      │ api.alpha_vantage.rate_limit │ 500                                            │ int  │
│ database │ database.url                 │ postgresql://localhost:5432/exchange_analytics │ str  │
│ cache    │ cache.redis_url              │ redis://localhost:6379/0                       │ str  │
│ discord  │ discord.webhook_url          │ ****hidden****                                 │ str  │
└──────────┴──────────────────────────────┴────────────────────────────────────────────────┴──────┘
```

### 2. 環境変数表示

```bash
./exchange-analytics config env
```

**機能**: 環境変数の一覧を表示
**出力例**:

```
🌍 環境変数一覧
                                             🔧 Environment Variables

┏━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ Variable              ┃ Value                                                                         ┃ Status ┃
┡━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━┩
│ DATABASE_URL          │ postgresql+asyncpg://exchange_analytics_user:exchange_password@localhost:543… │ ✅ Set │
│ REDIS_URL             │ redis://localhost:6379/0                                                      │ ✅ Set │
│ ALPHA_VANTAGE_API_KEY │ ****hidden**** (len: 16)                                                      │ ✅ Set │
│ OPENAI_API_KEY        │ ****hidden**** (len: 164)                                                     │ ✅ Set │
│ DISCORD_WEBHOOK_URL   │ https://canary.discord.com/api/webhooks/1403643478361116672/nf6aIMHvPjNVX4x1… │ ✅ Set │
└───────────────────────┴───────────────────────────────────────────────────────────────────────────────┴────────┘
```

### 3. 設定検証

```bash
./exchange-analytics config validate
```

**機能**: 設定の検証

### 4. 設定更新

```bash
./exchange-analytics config set [OPTIONS]
```

**機能**: 設定の更新

### 5. 設定削除

```bash
./exchange-analytics config delete [OPTIONS]
```

**機能**: 設定の削除

### 6. 設定エクスポート

```bash
./exchange-analytics config export [OPTIONS]
```

**機能**: 設定をファイルにエクスポート

### 7. 設定ツリー表示

```bash
./exchange-analytics config tree
```

**機能**: 設定をツリー形式で表示

---

## API 管理コマンド

### 1. API サーバー状態確認

```bash
./exchange-analytics api status
```

**機能**: API サーバーの状態を確認
**出力例**:

```
🔍 API サーバー状態確認中...
⠙ ヘルスチェック中...
╭─────── 📊 API Server Status ────────╮
│ ✅ API サーバー稼働中               │
│                                     │
│ 🌐 URL: http://localhost:8000       │
│ 📚 Docs: http://localhost:8000/docs │
│ 🏥 Status: healthy                  │
│ ⏰ Timestamp: unknown               │
│ 📦 Version: 1.0.0                   │
╰─────────────────────────────────────╯
```

### 2. API サーバーヘルスチェック

```bash
./exchange-analytics api health
```

**機能**: API サーバーのヘルスチェック
**出力例**:

```
🏥 ヘルスチェック実行中... (基本)
✅ Status: healthy
⏰ Timestamp: None
📦 Version: 1.0.0
```

### 3. API サーバー制御

```bash
# APIサーバー起動
./exchange-analytics api start

# APIサーバー停止
./exchange-analytics api stop

# APIサーバー再起動
./exchange-analytics api restart
```

**機能**: API サーバーの起動・停止・再起動

### 4. API サーバーメトリクス取得

```bash
./exchange-analytics api metrics
```

**機能**: API サーバーのメトリクス取得

---

## アラート設定コマンド

### 1. アラート設定表示

```bash
./exchange-analytics alert-config show
```

**機能**: アラート設定を表示
**出力例**:

```
🚨 アラート設定
                💰 レート閾値アラート設定
┏━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━┳━━━━━━━━━━━━━━┳━━━━━━━━┓
┃ 通貨ペア ┃ 上限閾値 ┃ 下限閾値 ┃ チェック間隔 ┃ 重要度 ┃
┡━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━╇━━━━━━━━━━━━━━╇━━━━━━━━┩
│ USD/JPY  │ 151.0    │ 140.0    │ 5分          │ HIGH   │
│ EUR/USD  │ 1.15     │ 1.05     │ 5分          │ MEDIUM │
└──────────┴──────────┴──────────┴──────────────┴────────┘
          📊 パターン検出アラート設定
┏━━━━━━━━━━━━━━━━┳━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━┓
┃ パターンタイプ ┃ 有効 ┃ 最小信頼度 ┃ 重要度 ┃
┡━━━━━━━━━━━━━━━━╇━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━┩
│ reversal       │ ✅   │ 85%        │ HIGH   │
│ continuation   │ ✅   │ 80%        │ MEDIUM │
│ divergence     │ ✅   │ 90%        │ HIGH   │
└────────────────┴──────┴────────────┴────────┘
```

### 2. アラート設定検証

```bash
./exchange-analytics alert-config validate
```

**機能**: アラート設定の検証
**出力例**:

```
🔍 アラート設定検証結果
✅ 設定は有効です
🎉 設定に問題はありません
```

### 3. アラート設定編集

```bash
./exchange-analytics alert-config edit [OPTIONS]
```

**機能**: アラート設定の編集

### 4. アラート設定再読み込み

```bash
./exchange-analytics alert-config reload
```

**機能**: アラート設定の再読み込み

---

## システム復旧コマンド

### 1. システム状態確認

```bash
./exchange-analytics recovery status
```

**機能**: システム全体の状態を確認
**出力例**:

```
🔍 システム状態確認中...

============================================================
📊 Exchange Analytics システム状態レポート
============================================================
🟢 ⚡ Cron
   状態: ✅ 動作中

🟢 ⚡ PostgreSQL
   状態: ✅ 動作中

🟢 ⚡ Redis
   状態: ✅ 動作中

🟢 ⚡ API Server
   状態: ✅ 動作中

🔴 💡 Data Scheduler
   状態: ❌ 停止中
   復旧: cd /app && export $(cat .env | grep -v '^#' | xargs) && export PYTHONPATH=/app && nohup python scripts/cron/advanced_data/data_scheduler.py > /app/logs/data_scheduler.log 2>&1 &

🟢 💡 Performance Monitor
   状態: ✅ 正常動作

============================================================
```

### 2. 復旧機能テスト

```bash
./exchange-analytics recovery test
```

**機能**: 復旧機能のテスト実行
**出力例**:

```
🧪 復旧機能テストを開始します...
                  🔧 復旧機能テスト結果
┏━━━━━━━━━━━━━━━━━━━━┳━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃ テスト項目         ┃ 結果 ┃ 詳細                      ┃
┡━━━━━━━━━━━━━━━━━━━━╇━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━┩
│ スクリプト存在確認 │ ✅   │ system_recovery.py が存在 │
│ Python実行環境     │ ✅   │ Python 3.x で実行可能     │
│ ログディレクトリ   │ ✅   │ Python 3.x で実行可能     │
│ 権限確認           │ ✅   │ サービス起動権限あり      │
└────────────────────┴──────┴───────────────────────────┘
```

### 3. 自動復旧実行

```bash
./exchange-analytics recovery auto [OPTIONS]
```

**機能**: システム自動復旧を実行

### 4. 手動復旧ガイド表示

```bash
./exchange-analytics recovery manual
```

**機能**: 手動復旧ガイドを表示

### 5. 復旧ログ表示

```bash
./exchange-analytics recovery logs
```

**機能**: 復旧ログを表示

---

## 使用例とベストプラクティス

### 日常的な使用例

#### 1. システム状態の確認

```bash
# システム全体の状態確認
./exchange-analytics status

# 詳細なヘルスチェック
./exchange-analytics system health --detailed

# システム情報の確認
./exchange-analytics info
```

#### 2. データの確認

```bash
# 最新の価格データ確認
./exchange-analytics data show list --limit 10

# 特定通貨ペアのデータ確認
./exchange-analytics data show list --pair EUR/USD --limit 20

# データベース状態確認
./exchange-analytics data show status
```

#### 3. ログの確認

```bash
# システムログの確認
./exchange-analytics system logs

# アラートの確認
./exchange-analytics system alerts
```

### 緊急時の使用例

#### 1. システム復旧

```bash
# システム状態の詳細確認
./exchange-analytics recovery status

# 自動復旧の実行
./exchange-analytics recovery auto

# 復旧機能のテスト
./exchange-analytics recovery test
```

#### 2. サービス制御

```bash
# APIサーバーの再起動
./exchange-analytics api restart

# APIサーバーの状態確認
./exchange-analytics api status
```

### 設定変更時の使用例

#### 1. 設定の確認

```bash
# 現在の設定確認
./exchange-analytics config show

# 環境変数確認
./exchange-analytics config env

# 設定の検証
./exchange-analytics config validate
```

#### 2. アラート設定の確認

```bash
# アラート設定確認
./exchange-analytics alert-config show

# アラート設定検証
./exchange-analytics alert-config validate
```

### ベストプラクティス

#### 1. 定期的な監視

```bash
# 毎日のシステム状態確認
./exchange-analytics status

# 週次の詳細ヘルスチェック
./exchange-analytics system health --detailed
```

#### 2. データ管理

```bash
# 定期的なデータ取得
./exchange-analytics data fetch fetch --days 1

# データベース状態の確認
./exchange-analytics data show status
```

#### 3. ログ管理

```bash
# 定期的なログ確認
./exchange-analytics system logs

# アラートの確認
./exchange-analytics system alerts
```

---

## トラブルシューティング

### よくある問題と解決方法

#### 1. コマンドが実行できない

**問題**: `./exchange-analytics: command not found`

**解決方法**:

```bash
# 実行権限の確認
ls -la exchange-analytics

# 実行権限の付与
chmod +x exchange-analytics

# パスの確認
pwd
```

#### 2. データベース接続エラー

**問題**: データベース接続に失敗

**解決方法**:

```bash
# データベース状態確認
./exchange-analytics data show status

# システム状態確認
./exchange-analytics status

# 復旧の実行
./exchange-analytics recovery auto
```

#### 3. API サーバーが応答しない

**問題**: API サーバーが応答しない

**解決方法**:

```bash
# APIサーバー状態確認
./exchange-analytics api status

# APIサーバー再起動
./exchange-analytics api restart

# ヘルスチェック
./exchange-analytics api health
```

#### 4. 設定エラー

**問題**: 設定に問題がある

**解決方法**:

```bash
# 設定の検証
./exchange-analytics config validate

# 設定の表示
./exchange-analytics config show

# 環境変数の確認
./exchange-analytics config env
```

### ログの確認方法

#### 1. システムログの確認

```bash
# システムログの表示
./exchange-analytics system logs

# 特定のログファイルの確認
tail -f /var/log/exchange-analytics/system_monitor.log
```

#### 2. エラーログの確認

```bash
# エラーログの検索
grep -i "error\|failed\|exception" logs/*.log

# パフォーマンス分析
grep "実行時間\|execution time" logs/*.log
```

### サポート情報

#### 1. システム情報の収集

```bash
# システム情報の表示
./exchange-analytics info

# 詳細なシステム状態
./exchange-analytics status

# 復旧機能テスト
./exchange-analytics recovery test
```

#### 2. 設定情報の収集

```bash
# 設定の表示
./exchange-analytics config show

# 環境変数の表示
./exchange-analytics config env

# アラート設定の表示
./exchange-analytics alert-config show
```

---

## クイックリファレンス

### よく使うコマンド一覧

#### 基本コマンド

```bash
# システム状態確認
./exchange-analytics status

# システム情報表示
./exchange-analytics info

# ヘルプ表示
./exchange-analytics --help
```

#### システム監視

```bash
# ヘルスチェック
./exchange-analytics system health

# ログ確認
./exchange-analytics system logs

# アラート確認
./exchange-analytics system alerts

# メトリクス確認
./exchange-analytics system metrics
```

#### データ管理

```bash
# データ一覧表示
./exchange-analytics data show list

# データベース状態確認
./exchange-analytics data show status

# データ取得
./exchange-analytics data fetch fetch

# データバックアップ
./exchange-analytics data backup
```

#### AI 分析

```bash
# AI分析実行
./exchange-analytics ai analyze

# Discord通知テスト
./exchange-analytics ai discord-test

# 分析レポート一覧
./exchange-analytics ai reports
```

#### 設定管理

```bash
# 設定表示
./exchange-analytics config show

# 環境変数表示
./exchange-analytics config env

# 設定検証
./exchange-analytics config validate
```

#### API 管理

```bash
# API状態確認
./exchange-analytics api status

# API再起動
./exchange-analytics api restart

# APIヘルスチェック
./exchange-analytics api health
```

#### システム復旧

```bash
# システム状態確認
./exchange-analytics recovery status

# 自動復旧
./exchange-analytics recovery auto

# 復旧テスト
./exchange-analytics recovery test
```

### コマンドの覚え方

#### 階層構造

```
exchange-analytics
├── system (監視)
│   ├── health
│   ├── logs
│   ├── alerts
│   └── metrics
├── data (データ)
│   ├── show
│   │   ├── list
│   │   └── status
│   ├── fetch
│   │   └── fetch
│   └── backup
├── ai (AI分析)
│   ├── analyze
│   ├── discord-test
│   └── reports
├── config (設定)
│   ├── show
│   ├── env
│   └── validate
├── api (API管理)
│   ├── status
│   ├── restart
│   └── health
└── recovery (復旧)
    ├── status
    ├── auto
    └── test
```

#### 使用頻度別

- **毎日**: `status`, `system health`, `data show list`
- **週次**: `system health --detailed`, `config validate`
- **月次**: `recovery test`, `ai analyze`
- **緊急時**: `recovery status`, `recovery auto`, `api restart`

---

## まとめ

Exchange Analytics CLI は、通貨分析システムの包括的な管理ツールです。このガイドに従って、システムの監視、データ管理、AI 分析、設定管理などを効率的に行うことができます。

### 主要なコマンドの覚え方

- **基本**: `status`, `info` - システムの基本情報
- **監視**: `system health`, `system logs` - システム監視
- **データ**: `data show list`, `data fetch fetch` - データ管理
- **AI**: `ai analyze`, `ai reports` - AI 分析
- **設定**: `config show`, `config validate` - 設定管理
- **復旧**: `recovery status`, `recovery auto` - システム復旧

### 定期的なメンテナンス

1. **毎日**: `./exchange-analytics status`
2. **週次**: `./exchange-analytics system health --detailed`
3. **月次**: `./exchange-analytics config validate`

このガイドを参考に、Exchange Analytics CLI を効果的に活用してください。

---

**📚 関連ドキュメント**

- [README.md](../README.md) - システム概要
- [API Documentation](API_DOCUMENTATION.md) - API 仕様書
- [Configuration Guide](CONFIGURATION_GUIDE.md) - 設定ガイド

**🆘 サポート**

- 問題が発生した場合は、トラブルシューティングセクションを参照
- 詳細なログは `./exchange-analytics system logs` で確認
- システム復旧は `./exchange-analytics recovery auto` で実行
