# 📋 Crontab Configuration Files

Exchange Analytics システムの crontab 設定ファイル管理

## 📁 ディレクトリ構造

```
config/crontab/
├── example/        # テスト・サンプル用設定
├── production/     # 本番運用設定
├── docs/          # ドキュメント・ガイド
└── README.md      # このファイル
```

## 🔧 **example/** - テスト用設定

| ファイル              | 用途         | 説明                       |
| --------------------- | ------------ | -------------------------- |
| `example_crontab.txt` | 基本テスト   | 最初の cron 動作確認用     |
| `test_crontab.txt`    | 機能テスト   | 各コンポーネント動作テスト |
| `crontab-example.txt` | サンプル設定 | 設定方法の参考例           |

## 🚀 **production/** - 本番設定

| ファイル                          | 用途                  | 説明                                   |
| --------------------------------- | --------------------- | -------------------------------------- |
| `integrated_analysis_crontab.txt` | **🔗 統合相関分析版** | **通貨相関分析システム対応・最新推奨** |
| `integrated_simple_crontab.txt`   | 🔗 統合分析簡易版     | 統合相関分析の軽量バージョン           |
| `production_crontab_final.txt`    | 🎯 従来版最新設定     | 従来システムの推奨設定（参考用）       |
| `crontab_with_yahoo_finance.txt`  | Yahoo Finance 統合    | データソース二重化対応版               |
| `production_crontab.txt`          | 基本本番設定          | シンプルな初期設定（参考用）           |

### 📁 backup/ - 廃止ファイル

| ファイル                       | 理由               |
| ------------------------------ | ------------------ |
| `fixed_crontab.txt`            | final 版に統合済み |
| `fixed_production_crontab.txt` | final 版に統合済み |
| `production_crontab_v2.txt`    | final 版に統合済み |

## 📚 **docs/** - ドキュメント

| ファイル           | 用途       | 説明                   |
| ------------------ | ---------- | ---------------------- |
| `crontab_guide.md` | 完全ガイド | crontab 設定の詳細説明 |

## 🛠️ **使用方法**

### テスト設定の適用

```bash
# テスト用設定を適用
crontab config/crontab/example/test_crontab.txt

# 設定確認
crontab -l
```

### 本番設定の適用

```bash
# 🎯 最新の本番設定を適用（推奨）
crontab config/crontab/production/production_crontab_final.txt

# または、シンボリックリンク経由
crontab current_crontab.txt

# 設定確認
crontab -l
```

### 設定選択ガイド

- **🎯 production_crontab_final.txt**: 最新・推奨設定（通常はこれを使用）
- **📊 crontab_with_yahoo_finance.txt**: Yahoo Finance 重視の場合
- **⚙️ production_crontab.txt**: シンプルな基本設定

### 設定のバックアップ

```bash
# 現在の設定をバックアップ
crontab -l > config/crontab/backup/crontab_backup_$(date +%Y%m%d_%H%M%S).txt
```

## ⚠️ **注意事項**

1. **環境変数**: `.env`ファイルが正しく設定されていることを確認
2. **パス**: スクリプトパスが`scripts/`ディレクトリに更新されていることを確認
3. **権限**: crontab ファイルとスクリプトファイルの実行権限を確認
4. **ログ**: `/app/logs/`ディレクトリの存在と書き込み権限を確認

## 🔄 **アップグレード手順**

1. 現在の crontab 設定をバックアップ
2. 新しい設定ファイルを確認
3. 段階的に設定を更新
4. ログでの動作確認

## 📞 **トラブルシューティング**

- ログファイル: `/app/logs/`
- 設定確認: `crontab -l`
- プロセス確認: `ps aux | grep cron`
- サービス再起動: `service cron restart`
