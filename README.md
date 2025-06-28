# 🎵 Indie Music Platform（インディーズミュージックプラットフォーム）

独立系アーティストが楽曲を直接販売・収益化できる包括的音楽プラットフォーム

## 🚀 プロジェクト概要

### 目的
インディーズアーティストがレコードレーベルに依存せず、楽曲を直接リスナーに販売し収益化できるプラットフォームを提供

### 主要機能
- **アーティスト機能**: 楽曲アップロード・価格設定・売上分析・収益管理
- **リスナー機能**: 楽曲検索・試聴・購入・ダウンロード・ライブラリ管理
- **音楽プレイヤー**: ストリーミング再生・シャッフル・リピート・プレイリスト
- **決済システム**: Stripe統合による安全な楽曲購入
- **分析ダッシュボード**: 詳細な売上・再生統計・収益分析

## 🏗️ アーキテクチャ

### フロントエンド
- **React 18** + **Vite** - モダンなWebアプリケーション
- **React Router** - SPA ルーティング
- **Styled Components** - CSS-in-JS スタイリング
- **Chart.js** - データ可視化・分析グラフ
- **Howler.js** - 高品質音声再生
- **Firebase Authentication** - 認証システム

### バックエンド
- **FastAPI** - 高性能 Python Web フレームワーク
- **PostgreSQL** - リレーショナルデータベース
- **SQLAlchemy** - ORM + **Alembic** - マイグレーション
- **Pydantic** - データバリデーション
- **Firebase Admin SDK** - 認証・認可

### インフラ・DevOps
- **Azure Container Apps** - 本番環境
- **AWS S3** - ファイルストレージ（音声・画像）
- **GitHub Actions** - CI/CD パイプライン
- **Docker** - コンテナ化

## 📊 現在の完成度: **92%**

### ✅ 完了済み機能

#### 🎨 **UI/UX**
- レスポンシブデザイン（モバイル・タブレット対応）
- スケルトンローダー・ローディングスピナー
- アクセシビリティ向上（フォーカススタイル・キーボードナビゲーション）

#### ⚡ **パフォーマンス**
- バンドルチャンク分割（461KB + 178KB charts）
- APIレスポンス5分キャッシュ
- カスタムフック（useApi, useLocalStorage）

#### 🔒 **セキュリティ**
- 包括的入力検証ユーティリティ
- 詳細ログシステム（本番・開発環境対応）
- APIエラーハンドリング・監視機能

#### 🎵 **音楽プレイヤー**
- シャッフル・リピート機能（1曲/全曲/なし）
- 楽曲終了時自動次曲再生
- プレイリスト管理・再生履歴

#### 📈 **アナリティクス**
- 売上推移グラフ（線・棒グラフ切替）
- 楽曲別統計（再生・DL・いいね・シェア）
- 収益メトリクス・期間別比較（7日・30日・90日）
- 収益内訳（ドーナツチャート）

#### 🧪 **品質保証**
- **35個の単体テスト**（全通過）
- E2Eテスト環境構築
- テストカバレッジ報告

## 🚀 クイックスタート

### 前提条件
- Node.js 18+ 
- Python 3.9+
- PostgreSQL 13+
- Docker（オプション）

### 1. 環境設定

```bash
# リポジトリクローン
git clone https://github.com/hawkymisc/musicapp.git
cd musicapp

# 環境変数設定
cp indie-music-platform-backend/.env.example indie-music-platform-backend/.env
cp indie-music-platform-frontend/.env.example indie-music-platform-frontend/.env
```

### 2. バックエンド起動

```bash
cd indie-music-platform-backend

# 依存関係インストール
pip install -r requirements.txt

# データベースマイグレーション
alembic upgrade head

# シードデータ作成（オプション）
python create_seed_data.py

# サーバー起動
uvicorn app.main:app --reload
```

### 3. フロントエンド起動

```bash
cd indie-music-platform-frontend

# 依存関係インストール
npm install

# 開発サーバー起動
npm run dev
```

### 4. アクセス
- フロントエンド: http://localhost:5173
- バックエンドAPI: http://localhost:8000
- API仕様書: http://localhost:8000/docs

## 🐳 Docker での起動

```bash
cd indie-music-platform-backend
docker-compose up -d
```

## 🧪 テスト実行

### バックエンドテスト
```bash
cd indie-music-platform-backend
pytest
```

### フロントエンドテスト
```bash
cd indie-music-platform-frontend

# 単体テスト
npm test

# E2Eテスト
npm run test:e2e
```

### ビルド
```bash
cd indie-music-platform-frontend
npm run build
```

## 📁 プロジェクト構造

```
musicapp/
├── indie-music-platform-backend/     # FastAPI バックエンド
│   ├── app/
│   │   ├── api/v1/                   # API エンドポイント
│   │   ├── models/                   # データベースモデル
│   │   ├── services/                 # ビジネスロジック
│   │   └── schemas/                  # Pydantic スキーマ
│   └── tests/                        # バックエンドテスト
├── indie-music-platform-frontend/    # React フロントエンド
│   ├── src/
│   │   ├── components/               # React コンポーネント
│   │   ├── pages/                    # ページコンポーネント
│   │   ├── services/                 # API クライアント
│   │   ├── contexts/                 # React Context
│   │   └── utils/                    # ユーティリティ
│   └── e2e/                         # E2Eテスト
└── docs/                            # プロジェクト文書
```

## 📋 主要APIエンドポイント

### 認証
- `POST /api/v1/auth/register` - ユーザー登録
- `POST /api/v1/auth/login` - ログイン

### 楽曲管理
- `GET /api/v1/tracks` - 楽曲検索・一覧
- `POST /api/v1/tracks` - 楽曲アップロード
- `GET /api/v1/tracks/{id}` - 楽曲詳細

### 購入・決済
- `POST /api/v1/purchases` - 楽曲購入
- `GET /api/v1/purchases/history` - 購入履歴

### ストリーミング
- `GET /api/v1/stream/{track_id}` - 音声ストリーミング
- `POST /api/v1/stream/play` - 再生回数記録

## 🎯 ビジネスモデル

- **収益モデル**: プラットフォーム手数料 15%
- **アーティスト**: 楽曲売上の85%を受領
- **価格設定**: アーティストが自由に設定可能

## 🔧 設定

### 必須環境変数

#### バックエンド（.env）
```env
DATABASE_URL=postgresql://user:password@localhost/musicapp
SECRET_KEY=your-secret-key
FIREBASE_CREDENTIALS_PATH=./firebase-credentials.json
AWS_ACCESS_KEY_ID=your-aws-key
AWS_SECRET_ACCESS_KEY=your-aws-secret
S3_BUCKET_NAME=your-s3-bucket
STRIPE_SECRET_KEY=your-stripe-secret
```

#### フロントエンド（.env）
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_FIREBASE_API_KEY=your-firebase-key
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_STRIPE_PUBLISHABLE_KEY=your-stripe-publishable-key
```

## 🚀 デプロイ

### Azure Container Apps（本番環境）
```bash
cd indie-music-platform-backend/deploy
./azure-deploy.sh
```

### 静的サイト（フロントエンド）
```bash
cd indie-music-platform-frontend
npm run build
# dist/ フォルダを Azure Static Web Apps にデプロイ
```

## 🤝 コントリビューション

1. このリポジトリをフォーク
2. feature ブランチを作成: `git checkout -b feature/新機能`
3. 変更をコミット: `git commit -m '新機能を追加'`
4. ブランチにプッシュ: `git push origin feature/新機能`
5. プルリクエストを作成

## 📄 ライセンス

MIT License - 詳細は [LICENSE](LICENSE) ファイルを参照

## 📞 サポート

- **Issues**: [GitHub Issues](https://github.com/hawkymisc/musicapp/issues)
- **ドキュメント**: [docs/](./docs/) フォルダ参照
- **開発ガイド**: [CLAUDE.md](./CLAUDE.md)

## 🏆 主要機能デモ

### アーティスト向け
1. **楽曲アップロード**: ドラッグ&ドロップで簡単アップロード
2. **売上分析**: Chart.js による詳細グラフ
3. **収益管理**: リアルタイム売上追跡

### リスナー向け
1. **楽曲検索**: 高度なフィルター・ソート機能
2. **音楽プレイヤー**: Spotify風の操作性
3. **ライブラリ**: 購入楽曲の管理・整理

---

**🎵 独立系アーティストの音楽を世界に届ける革新的プラットフォーム 🎵**