# 🚀 デプロイメントスクリプト使用ガイド

このディレクトリには、インディーズミュージックプラットフォームのデプロイと運用管理用のスクリプトが含まれています。

## 📋 スクリプト一覧

### 1. `azure-deploy.sh` - メインデプロイスクリプト
完全なAzureデプロイメントを自動化します。

```bash
# 初回デプロイ（推奨）
./deploy/azure-deploy.sh minimal

# デプロイ後チェックのみ実行
./deploy/azure-deploy.sh check

# 全リソース削除
./deploy/azure-deploy.sh cleanup
```

**機能:**
- Azure リソース作成（PostgreSQL, Storage, Container Registry, Container Apps）
- Docker イメージビルド・プッシュ
- アプリケーションデプロイ
- リビジョン管理（自動的に最新リビジョンに切り替え）
- デプロイ後の動作確認

### 2. `health-check.sh` - ヘルスチェックスクリプト
アプリケーションの動作状況を確認します。

```bash
# クイックチェック
./deploy/health-check.sh

# フルチェック（詳細情報付き）
./deploy/health-check.sh full

# 継続監視（30秒間隔）
./deploy/health-check.sh monitor

# エラー詳細診断
./deploy/health-check.sh diagnose
```

**機能:**
- ヘルスエンドポイント確認
- 基本API エンドポイント確認
- Container App 状態確認
- ログエラー検索
- リビジョン情報表示

### 3. `troubleshoot.sh` - トラブルシューティングスクリプト
問題発生時の診断と修復を行います。

```bash
# 全体トラブルシューティング
./deploy/troubleshoot.sh

# ログ詳細分析
./deploy/troubleshoot.sh logs

# アプリケーション再起動
./deploy/troubleshoot.sh restart

# 完全再ビルドとデプロイ
./deploy/troubleshoot.sh rebuild

# 依存関係チェック
./deploy/troubleshoot.sh deps

# ネットワーク診断
./deploy/troubleshoot.sh network
```

**機能:**
- ログパターン分析
- 依存関係診断
- アプリケーション再起動
- イメージ再ビルド
- ネットワーク診断

## 🔄 典型的なワークフロー

### 初回デプロイ
```bash
# 1. 前提条件確認
az login
az account show

# 2. Firebase認証情報配置
# firebase-credentials.json をプロジェクトルートに配置

# 3. 完全デプロイ実行
./deploy/azure-deploy.sh minimal
```

### 日常運用
```bash
# アプリケーション状態確認
./deploy/health-check.sh full

# 問題発生時の診断
./deploy/troubleshoot.sh

# コード更新後の再デプロイ
./deploy/troubleshoot.sh rebuild
```

### 監視・メンテナンス
```bash
# 継続監視
./deploy/health-check.sh monitor

# 定期的なヘルスチェック
./deploy/health-check.sh full

# ログ確認
./deploy/troubleshoot.sh logs
```

## ⚠️ 重要な注意事項

### 前提条件
1. **Azure CLI** がインストールされていること
2. **Docker** がインストールされていること  
3. **Azure アカウント** にログインしていること
4. **適切な権限** を持っていること（Contributor以上）

### 必要ファイル
- `firebase-credentials.json` - Firebase Service Account キー
- `requirements.txt` - Python依存関係リスト
- `Dockerfile` - Docker イメージビルド用

### 環境変数設定
デプロイスクリプトが自動設定する環境変数:
```bash
ENVIRONMENT=production
PAYMENT_ENABLED=false
DATABASE_URL=postgresql://...
AZURE_STORAGE_ACCOUNT_NAME=...
AZURE_STORAGE_ACCOUNT_KEY=...
FIREBASE_CREDENTIALS_PATH=...
```

## 🔧 カスタマイズ

### 設定値の変更
各スクリプトの冒頭で設定値を変更できます:

```bash
# azure-deploy.sh
RESOURCE_GROUP="indie-music-rg"
LOCATION="japaneast"
APP_NAME="indie-music-api"
DB_SERVER_NAME="indie-music-db-server-$(date +%s)"
STORAGE_ACCOUNT="indiemusicstorage$(date +%s)"
CONTAINER_REGISTRY="indiemusicregistry"
```

### 新しいチェック項目の追加
`health-check.sh` にエンドポイントを追加:

```bash
endpoints=(
    "/docs:API ドキュメント"
    "/api/v1/features/:機能API"
    "/api/v1/tracks/:楽曲API"        # 新規追加
    "/openapi.json:OpenAPI仕様"
)
```

## 📊 ログとデバッグ

### ログファイル位置
- Azure Container Apps ログ: `az containerapp logs show`
- デプロイ実行ログ: `.deployment-secrets.txt`
- 一時診断ログ: `/tmp/app_logs.txt`

### デバッグオプション
詳細な実行ログを表示:
```bash
# Bash デバッグモード
bash -x ./deploy/azure-deploy.sh minimal

# Azure CLI詳細出力
az containerapp logs show --name indie-music-api --resource-group indie-music-rg --follow
```

## 🆘 トラブルシューティング

### よくある問題と解決策

#### 1. slowapi ModuleNotFoundError
```bash
# 解決方法
./deploy/troubleshoot.sh rebuild
```

#### 2. ヘルスチェック失敗
```bash
# 診断実行
./deploy/health-check.sh diagnose

# アプリ再起動
./deploy/troubleshoot.sh restart
```

#### 3. リビジョン切り替え問題
```bash
# 手動切り替え
az containerapp revision set-mode --name indie-music-api --resource-group indie-music-rg --mode multiple
az containerapp ingress traffic set --name indie-music-api --resource-group indie-music-rg --revision-weight LATEST_REVISION=100
```

#### 4. 依存関係問題
```bash
# 依存関係診断
./deploy/troubleshoot.sh deps

# requirements.txt 確認・修正後
./deploy/troubleshoot.sh rebuild
```

## 🎯 次のステップ

1. **CI/CD パイプライン構築** - GitHub Actions との統合
2. **監視システム導入** - Application Insights 設定
3. **セキュリティ強化** - Azure Key Vault 統合
4. **カスタムドメイン設定** - 独自ドメイン + SSL証明書

---

## 📞 サポート

問題が解決しない場合:
1. `./deploy/troubleshoot.sh all` で全体診断を実行
2. ログファイル (`/tmp/app_logs.txt`) を確認
3. Azure Portal でリソース状態を確認
4. 必要に応じて `./deploy/azure-deploy.sh cleanup` でリソース削除後、再デプロイ