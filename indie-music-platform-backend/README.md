# インディーズミュージックアプリ - バックエンド

インディーズミュージシャンが事務所を介さず直接収益化できる環境を提供する音楽アプリケーションのバックエンドAPIサーバーです。

## 機能概要

MVPフェーズでの主な機能：

- ユーザー登録・認証（アーティスト/リスナー）
- 楽曲のアップロード、管理（アーティスト向け）
- 楽曲の検索、再生（ストリーミング）
- 楽曲の購入・ダウンロード
- シンプルな収益ダッシュボード（アーティスト向け）
- 基本的なプロフィール管理

## 技術スタック

- **バックエンド**: FastAPI
- **データベース**: PostgreSQL
- **ORM**: SQLAlchemy
- **マイグレーション**: Alembic
- **認証**: Firebase Authentication
- **ストレージ**: AWS S3
- **決済処理**: Stripe
- **コンテナ化**: Docker, Docker Compose

## 開発環境セットアップ

### 前提条件

- Docker と Docker Compose がインストールされていること
- AWS アカウント（S3バケットの作成と認証情報）
- Firebase プロジェクト（認証用）
- Stripe アカウント（決済処理用）

### 環境変数の設定

`.env.example` ファイルを `.env` にコピーして、必要な環境変数を設定します。

```bash
cp .env.example .env
```

以下の環境変数を設定してください：

- PostgreSQL 接続情報
- AWS 認証情報と S3 バケット名
- Firebase 認証情報のパス
- Stripe API キー

### Firebase認証情報の配置

Firebase プロジェクトからダウンロードした認証情報の JSON ファイルを `firebase-credentials.json` という名前でプロジェクトルートに配置します。

### Docker での起動

Docker Compose を使用して開発環境を起動します。

```bash
docker-compose up -d
```

これにより、APIサーバーとPostgreSQLデータベースが起動します。

### マイグレーションの実行

初回起動時やスキーマ変更時にはマイグレーションを実行してデータベースを初期化します。

```bash
docker-compose exec api alembic upgrade head
```

## 開発ワークフロー

### APIサーバーの起動

```bash
# Docker Compose での起動
docker-compose up -d

# ログの確認
docker-compose logs -f api
```

### APIドキュメントの確認

FastAPI の自動生成 Swagger UI ドキュメントは以下の URL でアクセスできます：

```
http://localhost:8000/docs
```

### コード変更とホットリロード

FastAPI は開発モードでホットリロードに対応しているため、コードを変更すると自動的にサーバーが再起動します。

### テストの実行

```bash
# すべてのテストを実行
docker-compose exec api pytest

# 特定のテストファイルを実行
docker-compose exec api pytest tests/api/test_tracks.py

# テストカバレッジレポート
docker-compose exec api pytest --cov=app
```

### マイグレーションの作成

スキーマ変更時には新しいマイグレーションを作成します。

```bash
# マイグレーションファイルの生成
docker-compose exec api alembic revision --autogenerate -m "変更の説明"

# マイグレーションの適用
docker-compose exec api alembic upgrade head
```

## API エンドポイント概要

### 認証関連

- `POST /api/v1/auth/register` - ユーザー登録
- `GET /api/v1/auth/me` - 現在のユーザー情報取得
- `PUT /api/v1/auth/me` - ユーザー情報更新

### 楽曲関連

- `GET /api/v1/tracks/` - 楽曲一覧取得
- `POST /api/v1/tracks/` - 新規楽曲登録（アーティストのみ）
- `GET /api/v1/tracks/{track_id}` - 楽曲詳細取得
- `PUT /api/v1/tracks/{track_id}` - 楽曲情報更新（所有アーティストのみ）
- `DELETE /api/v1/tracks/{track_id}` - 楽曲削除（所有アーティストのみ）
- `POST /api/v1/tracks/upload/cover` - カバーアート画像アップロード
- `POST /api/v1/tracks/upload/audio` - 音声ファイルアップロード
- `GET /api/v1/tracks/artist/{artist_id}` - アーティストの楽曲一覧取得
- `GET /api/v1/tracks/search` - 楽曲検索

### ストリーミング関連

- `POST /api/v1/stream/{track_id}` - ストリーミングURL取得
- `POST /api/v1/stream/{track_id}/play` - 再生カウント記録

### 購入関連

- `POST /api/v1/purchases/` - 楽曲購入
- `GET /api/v1/purchases/` - 購入履歴取得
- `GET /api/v1/purchases/{purchase_id}` - 購入詳細取得
- `GET /api/v1/purchases/track/{track_id}/download` - 購入済み楽曲のダウンロードURL取得

### アーティスト関連

- `GET /api/v1/artists/revenue` - アーティスト収益情報取得
- `GET /api/v1/artists/stats` - アーティスト統計情報取得

## デプロイメント

### 本番環境用 Docker イメージのビルド

```bash
docker build -t indie-music-app-api:latest .
```

### AWS へのデプロイ例（ECS）

AWS ECS（Elastic Container Service）を使用した本番環境へのデプロイ例：

1. ECR（Elastic Container Registry）にイメージをプッシュ
2. ECS タスク定義とサービスを作成
3. RDS PostgreSQL インスタンスを設定
4. マイグレーションを実行
5. ロードバランサーと Auto Scaling を設定

詳細なデプロイ手順は `deployment.md` を参照してください。

## トラブルシューティング

### 一般的な問題と解決策

1. **データベース接続エラー**
   - PostgreSQL サービスが起動しているか確認
   - `.env` ファイルの接続情報が正しいか確認

2. **S3 アップロードエラー**
   - AWS 認証情報が正しく設定されているか確認
   - S3 バケットが存在し、適切なアクセス権限があるか確認

3. **Firebase 認証エラー**
   - Firebase 認証情報ファイルが正しく配置されているか確認
   - Firebase プロジェクトで認証機能が有効になっているか確認

## コントリビューション

バグ報告や機能リクエスト、プルリクエストは大歓迎です。コントリビューションの前に、以下の点を確認してください：

1. 新しい機能や修正は、適切なテストを含めてください
2. コードスタイルは Black フォーマッターに従ってください
3. コミットメッセージは明確で説明的にしてください

## ライセンス

このプロジェクトは MIT ライセンスの下で提供されています。詳細は `LICENSE` ファイルを参照してください。

## 開発者向け詳細情報

より詳細な開発者向け情報は以下のドキュメントを参照してください：

- [API 詳細仕様書](docs/api-specs.md)
- [データモデル定義](docs/data-models.md)
- [サービス層仕様](docs/services.md)
- [テスト戦略](docs/testing.md)
- [本番環境デプロイガイド](docs/deployment.md)
