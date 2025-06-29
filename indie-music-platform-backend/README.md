# インディーズミュージックアプリ - バックエンド

インディーズミュージシャンが事務所を介さず直接収益化できる環境を提供する音楽アプリケーションのバックエンドAPIサーバーです。

## 🎯 機能概要

MVPフェーズでの主な機能：

- **ユーザー管理**: アーティスト/リスナー登録・認証・プロフィール管理
- **楽曲管理**: アップロード・メタデータ編集・公開設定（アーティスト向け）
- **音楽体験**: 検索・試聴・ストリーミング再生・プレイリスト
- **収益化**: 楽曲販売・ダウンロード・直接収益化システム
- **分析機能**: 再生統計・売上分析・収益ダッシュボード（アーティスト向け）
- **決済処理**: Stripe統合による安全な楽曲購入システム

## 🏗 技術スタック

- **バックエンド**: FastAPI (Python 3.11+)
- **データベース**: PostgreSQL + SQLAlchemy ORM
- **マイグレーション**: Alembic
- **認証**: Firebase Authentication + JWT
- **ストレージ**: AWS S3 (音声ファイル・カバーアート)
- **決済処理**: Stripe API
- **コンテナ化**: Docker + Docker Compose
- **API文書**: OpenAPI/Swagger UI自動生成

## 🛡️ 品質・セキュリティ

### 包括的テスト基盤
- **セキュリティテスト**: OWASP Top 10対応フレームワーク
- **異常系テスト**: ネットワーク・HTTP・データベース障害対応
- **データ検証テスト**: 入力バリデーション・型チェック
- **境界値テスト**: 数値・文字列・時間の限界値
- **統合テスト**: 外部サービス連携・フルスタック
- **基本APIテスト**: 全エンドポイント機能確認

### セキュリティ対策
- **認証・認可**: Firebase JWT + ロールベースアクセス制御
- **データ保護**: 入力サニタイゼーション・SQLインジェクション対策
- **API セキュリティ**: レート制限・CORS設定・HTTPSエンドポイント
- **ファイル安全性**: アップロードファイル検証・パストラバーサル対策

## 🚀 開発環境セットアップ

### 前提条件

- Docker と Docker Compose
- AWS アカウント（S3バケット）
- Firebase プロジェクト（認証用）
- Stripe アカウント（決済処理用）

### 環境変数の設定

```bash
cp .env.example .env
# 以下の環境変数を設定：
# - PostgreSQL 接続情報
# - AWS 認証情報と S3 バケット名
# - Firebase 認証情報のパス
# - Stripe API キー
```

### Firebase認証情報の配置

Firebase プロジェクトからダウンロードした認証情報を配置：

```bash
# firebase-credentials.json をプロジェクトルートに配置
```

### Docker での起動

```bash
# 開発環境起動
docker-compose up -d

# フルテスト環境起動（包括的テスト用）
docker-compose -f docker-compose.full-test.yml up -d

# データベースマイグレーション実行
docker-compose exec api alembic upgrade head

# Seedデータ作成（テスト用）
docker-compose exec api python seed_data.py

# API確認
curl http://localhost:8000/
```

## 🧪 テスト実行

### 基本テスト実行

```bash
# 推奨：テストランナー使用
./scripts/run-tests.sh --quick           # 基本テスト
./scripts/run-tests.sh --full            # 全テストスイート
./scripts/run-tests.sh --security-only   # セキュリティのみ

# 直接pytest使用
pytest tests/api/ tests/services/        # 基本機能テスト
pytest tests/security/                   # セキュリティテスト
pytest tests/validation/                 # データ検証テスト
pytest tests/edge_cases/                 # 境界値テスト

# カバレッジ付きテスト実行
pytest --cov=app --cov-report=html
```

### E2Eテスト実行（Playwright）

```bash
# Playwrightブラウザインストール
npm install @playwright/test
npx playwright install

# E2Eテスト実行（Docker環境必須）
docker-compose -f docker-compose.full-test.yml up -d
npx playwright test                      # 全ブラウザテスト
npx playwright test --reporter=line      # 簡潔出力
npx playwright test --project=chromium   # Chrome のみ

# テストカテゴリ別実行
npx playwright test tests/e2e/api-health.spec.js     # ヘルスチェック
npx playwright test tests/e2e/security-features.spec.js  # セキュリティ
npx playwright test tests/e2e/performance.spec.js    # パフォーマンス
```

### テストカテゴリ詳細

```bash
# セキュリティ脆弱性テスト（OWASP Top 10）
pytest tests/security/test_security_vulnerabilities.py -v

# 異常系・エラーハンドリングテスト
pytest tests/comprehensive/test_error_cases_extended.py -v

# データバリデーション・境界値テスト
pytest tests/validation/test_data_validation_comprehensive.py -v
pytest tests/edge_cases/test_boundary_edge_cases.py -v

# フルスタック統合テスト
pytest tests/integration/test_full_integration.py -v
```

## 📖 API エンドポイント

### 認証関連 (`/api/v1/auth/`)
- `POST /register` - ユーザー登録
- `GET /me` - 現在のユーザー情報取得
- `PUT /me` - ユーザー情報更新

### 楽曲関連 (`/api/v1/tracks/`)
- `GET /` - 楽曲一覧取得（検索・フィルタリング対応）
- `POST /` - 新規楽曲登録（アーティストのみ）
- `GET /{track_id}` - 楽曲詳細取得
- `PUT /{track_id}` - 楽曲情報更新（所有者のみ）
- `DELETE /{track_id}` - 楽曲削除（所有者のみ）
- `POST /upload/audio` - 音声ファイルアップロード
- `POST /upload/cover` - カバーアートアップロード

### ユーザー・アーティスト (`/api/v1/users/`, `/api/v1/artists/`)
- `GET /users/{user_id}` - ユーザープロフィール取得
- `GET /artists/{artist_id}` - アーティスト情報・楽曲一覧
- `GET /artists/{artist_id}/revenue` - 収益情報（本人のみ）
- `GET /artists/{artist_id}/statistics` - 統計情報（本人のみ）

### 購入・決済 (`/api/v1/purchases/`)
- `POST /` - 楽曲購入（Stripe決済）
- `GET /` - 購入履歴取得
- `GET /track/{track_id}/download` - 購入済み楽曲ダウンロード

### ストリーミング (`/api/v1/stream/`)
- `GET /{track_id}/url` - ストリーミングURL取得
- `POST /{track_id}/play` - 再生記録・統計更新

## 📊 API ドキュメント

FastAPI自動生成ドキュメント：

```
http://localhost:8000/docs      # Swagger UI
http://localhost:8000/redoc     # ReDoc
http://localhost:8000/openapi.json  # OpenAPI仕様書
```

## 🔧 開発ワークフロー

### コード変更とテスト

```bash
# ホットリロード開発
uvicorn app.main:app --reload

# コード変更後のテスト実行
pytest tests/api/test_tracks.py -v

# 新機能追加時の包括テスト
pytest tests/comprehensive/ -k "新機能名"
```

### データベースマイグレーション

```bash
# 新しいマイグレーション作成
alembic revision --autogenerate -m "変更の説明"

# マイグレーション適用
alembic upgrade head

# マイグレーション履歴確認
alembic history
```

### Seedデータ管理

```bash
# テスト用Seedデータ作成
python seed_data.py

# Seedデータの内容：
# - アーティスト 6名、リスナー 5名
# - 楽曲 12曲（6ジャンル × 2曲）
# - 購入履歴 14件
# - 現実的な日本語コンテンツ
```

## 🚢 デプロイメント

### Azure Container Apps デプロイ（推奨）

**完全自動化デプロイメント** - 包括的なスクリプトで簡単デプロイ

#### 🚀 クイックスタート

```bash
# 1. 前提条件確認
az login                              # Azure CLI ログイン
az account show                       # サブスクリプション確認

# 2. Firebase認証情報配置
# firebase-credentials.json をプロジェクトルートに配置

# 3. 完全自動デプロイ実行
./deploy/azure-deploy.sh minimal
```

**作成されるリソース:**
- PostgreSQL Database (Azure Database for PostgreSQL)
- Azure Storage Account (音楽ファイル・カバーアート)
- Azure Container Registry (Docker images)
- Azure Container Apps (アプリケーション実行環境)
- 自動SSL証明書・HTTPS化

#### 📊 運用管理スクリプト

```bash
# ヘルスチェック
./deploy/health-check.sh              # クイックチェック
./deploy/health-check.sh full         # 詳細チェック
./deploy/health-check.sh monitor      # 継続監視

# トラブルシューティング
./deploy/troubleshoot.sh              # 全体診断
./deploy/troubleshoot.sh restart      # アプリ再起動
./deploy/troubleshoot.sh rebuild      # 完全再ビルド

# リソース削除
./deploy/azure-deploy.sh cleanup      # 全リソース削除
```

#### 🔧 デプロイスクリプト詳細

各スクリプトの詳細な使用方法: **[deploy/README.md](deploy/README.md)**

**主な機能:**
- ✅ Azure プロバイダー自動登録
- ✅ 依存関係エラー自動修正
- ✅ リビジョン管理・自動切り替え
- ✅ デプロイ後動作確認
- ✅ 包括的トラブルシューティング
- ✅ ログ分析・エラー診断

#### 💰 推定運用コスト

```
月額: 約¥9,500
- Container Apps: ¥2,000
- PostgreSQL: ¥6,000  
- Storage: ¥1,000
- Container Registry: ¥500
```

### 従来のAWS ECS デプロイ

```bash
# 本番イメージビルド
docker build -t indie-music-api:latest .

# 本番環境での起動
docker run -p 8000:8000 --env-file .env.prod indie-music-api:latest
```

**AWS リソース構成:**
1. **ECR**: Docker imageをpush
2. **RDS**: PostgreSQL本番データベース
3. **ECS**: TaskDefinition + Service作成
4. **ALB**: ロードバランサー設定
5. **S3**: 音声ファイル・カバーアート保存

詳細手順: [docs/deployment.md](docs/deployment.md)

## 🐛 トラブルシューティング

### デプロイ関連問題

**自動診断スクリプト使用（推奨）**
```bash
# 包括的問題診断
./deploy/troubleshoot.sh

# 特定問題の診断
./deploy/troubleshoot.sh logs      # ログ分析
./deploy/troubleshoot.sh deps      # 依存関係チェック
./deploy/troubleshoot.sh network   # ネットワーク診断
```

**よくあるデプロイエラーと解決策**
```bash
# slowapi ModuleNotFoundError
./deploy/troubleshoot.sh rebuild

# ヘルスチェック失敗
./deploy/health-check.sh diagnose
./deploy/troubleshoot.sh restart

# Azure プロバイダー未登録エラー
# → 自動で解決されます（スクリプト内で自動登録）

# リビジョン切り替え問題
./deploy/azure-deploy.sh check     # 自動リビジョン管理
```

### 開発環境問題

**データベース接続エラー**
```bash
# PostgreSQL起動確認
docker-compose ps
# 接続テスト
docker-compose exec api python -c "from app.db.session import SessionLocal; SessionLocal()"
```

**S3/Azure Storage アップロードエラー**
```bash
# AWS認証情報確認（従来環境）
aws s3 ls s3://your-bucket-name
aws iam get-user

# Azure Storage確認（新環境）
az storage account list --output table
az storage container list --account-name YOUR_STORAGE_ACCOUNT
```

**Firebase認証エラー**
```bash
# 認証情報ファイル確認
ls -la firebase-credentials.json
# Firebase接続テスト
python -c "import firebase_admin; print('Firebase OK')"
```

**テスト実行エラー**
```bash
# テストデータベース初期化
python -c "from app.db.base import Base; from app.db.session import engine; Base.metadata.create_all(bind=engine)"

# Seedデータ再作成
python seed_data.py
```

### デプロイ監視とログ

**リアルタイム監視**
```bash
# 継続的ヘルスチェック
./deploy/health-check.sh monitor

# リアルタイムログ確認
az containerapp logs show --name indie-music-api --resource-group indie-music-rg --follow
```

**デバッグ情報収集**
```bash
# 詳細診断レポート生成
./deploy/troubleshoot.sh > debug-report.txt

# Azure リソース状態確認
az containerapp show --name indie-music-api --resource-group indie-music-rg
az containerapp revision list --name indie-music-api --resource-group indie-music-rg
```

## 🤝 コントリビューション

### 開発ガイドライン

1. **新機能開発**
   - 適切なテストケースを追加
   - セキュリティ考慮事項を確認
   - API文書を更新

2. **コードスタイル**
   - Black フォーマッター使用
   - isort でimport整理
   - type hints 使用推奨

3. **テスト要件**
   - 新機能の単体テスト
   - 統合テスト更新
   - セキュリティテスト考慮

### プルリクエスト手順

```bash
# 1. フィーチャーブランチ作成
git checkout -b feature/新機能名

# 2. 開発・テスト
pytest tests/

# 3. コミット
git add .
git commit -m "feat: 新機能の説明"

# 4. プッシュ・PR作成
git push origin feature/新機能名
```

## 📚 詳細ドキュメント

- **[包括的テスト計画](docs/comprehensive-testing-plan.md)** - システム全体のテスト戦略
- **[セキュリティテストレポート](docs/comprehensive-testing-final-report.md)** - セキュリティ・品質保証詳細
- **[API詳細仕様書](docs/api-specs.md)** - エンドポイント仕様
- **[データモデル定義](docs/data-models.md)** - データベーススキーマ
- **[サービス層仕様](docs/services.md)** - ビジネスロジック設計
- **[デプロイガイド](docs/deployment.md)** - 本番環境構築手順

## 📈 プロジェクト状況

### 完了機能
- ✅ ユーザー認証・認可システム
- ✅ 楽曲アップロード・管理機能
- ✅ 検索・ストリーミング機能
- ✅ 決済・購入システム
- ✅ 収益ダッシュボード
- ✅ 包括的テスト基盤
- ✅ セキュリティ対策（OWASP準拠）
- ✅ **Azure Container Apps 本番デプロイ完了**
- ✅ **完全自動化デプロイメントスクリプト**
- ✅ **包括的監視・トラブルシューティング環境**

### 品質指標
- **テストカバレッジ**: 70%目標（設定済み）
- **セキュリティ**: OWASP Top 10フレームワーク実装完了
- **API品質**: OpenAPI仕様準拠
- **コード品質**: 型チェック・リント対応
- **CI/CD**: GitHub Actions自動化完了
- **E2Eテスト**: Playwright自動化（66 passed）
- **Docker環境**: フルテスト環境構築完了
- **本番環境**: Azure Container Apps 稼働中
- **運用管理**: 自動化スクリプト完備

## 📄 ライセンス

MIT License - 詳細は [LICENSE](LICENSE) ファイルを参照

---

## 🎵 プロジェクトビジョン

**インディーズアーティストの創作活動を技術で支援し、音楽業界の民主化を実現する**

このプロジェクトは、アーティストが自由に音楽を発表し、適正な対価を得られる持続可能な音楽エコシステムの構築を目指しています。