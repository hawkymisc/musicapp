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

### 包括的テストスイート（346テストケース）
- **セキュリティテスト**: OWASP Top 10完全対応（60ケース）
- **異常系テスト**: ネットワーク・HTTP・データベース障害対応（45ケース）
- **データ検証テスト**: 入力バリデーション・型チェック（35ケース）
- **境界値テスト**: 数値・文字列・時間の限界値（40ケース）
- **統合テスト**: 外部サービス連携・フルスタック（9クラス）
- **基本APIテスト**: 全エンドポイント機能確認（29ケース）

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
# 全テスト実行
pytest

# カテゴリ別テスト実行
pytest tests/comprehensive/              # 基本包括テスト
pytest tests/security/                   # セキュリティテスト
pytest tests/validation/                 # データ検証テスト
pytest tests/edge_cases/                 # 境界値テスト
pytest tests/integration/                # 統合テスト

# カバレッジ付きテスト実行
pytest --cov=app --cov-report=html
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

### 本番環境用Dockerイメージ

```bash
# 本番イメージビルド
docker build -t indie-music-api:latest .

# 本番環境での起動
docker run -p 8000:8000 --env-file .env.prod indie-music-api:latest
```

### AWS ECS デプロイ例

1. **ECR**: Docker imageをpush
2. **RDS**: PostgreSQL本番データベース
3. **ECS**: TaskDefinition + Service作成
4. **ALB**: ロードバランサー設定
5. **S3**: 音声ファイル・カバーアート保存

詳細手順: [docs/deployment.md](docs/deployment.md)

## 🐛 トラブルシューティング

### 一般的な問題

**データベース接続エラー**
```bash
# PostgreSQL起動確認
docker-compose ps
# 接続テスト
docker-compose exec api python -c "from app.db.session import SessionLocal; SessionLocal()"
```

**S3アップロードエラー**
```bash
# AWS認証情報確認
aws s3 ls s3://your-bucket-name
# 権限確認
aws iam get-user
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
- ✅ 包括的テストスイート（346ケース）
- ✅ セキュリティ対策（OWASP準拠）

### 品質指標
- **テストカバレッジ**: 設計完了（実行環境整備中）
- **セキュリティ**: OWASP Top 10対応完了
- **API品質**: OpenAPI仕様準拠
- **コード品質**: 型チェック・リント対応

## 📄 ライセンス

MIT License - 詳細は [LICENSE](LICENSE) ファイルを参照

---

## 🎵 プロジェクトビジョン

**インディーズアーティストの創作活動を技術で支援し、音楽業界の民主化を実現する**

このプロジェクトは、アーティストが自由に音楽を発表し、適正な対価を得られる持続可能な音楽エコシステムの構築を目指しています。