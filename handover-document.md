# インディーズミュージックプラットフォーム開発 - 引き継ぎ資料

## プロジェクト概要
- フロントエンド (React/Vite) とバックエンド (FastAPI/SQLAlchemy) で構成されたインディーズミュージックプラットフォーム
- アーティストが楽曲をアップロードし、リスナーが購入・ストリーミングできるサービス
- 個人開発プロジェクトで、MVPフェーズの実装を進行中

## 現状
1. プロジェクト構造確認済み
   - バックエンド: FastAPI + SQLAlchemy + PostgreSQL (本番)/SQLite (テスト)
   - フロントエンド: React + Vite + styled-components

2. Poetry環境構築済み
   - バックエンドの依存関係をrequirements.txtからPoetryに移行
   - 主要パッケージ：fastapi, uvicorn, sqlalchemy, psycopg2-binary, alembic, pytest等

3. フロントエンド開発サーバー
   - `npm run dev` コマンドで正常に起動確認済み
   - 開発環境ではモックAPIを使用するよう構成

4. バックエンド開発準備
   - テスト環境向けに設定ファイルと Firebase クレデンシャルのモック作成
   - コードの不足していた部分（importなど）を修正

## 修正内容とポイント

### 1. TestClient初期化問題の解決
- 問題: TestClientの初期化時に `app` キーワード引数のエラーが発生
- 原因: FastAPI 0.95.1とhttpx 0.28.1のバージョン互換性の問題
- 解決策: httpxのバージョンを0.24.1にダウングレード
  ```toml
  # pyproject.toml
  [tool.poetry.group.dev.dependencies]
  pytest = "^8.3.5"
  httpx = "0.24.1"  # 0.28.1から変更
  ```

### 2. Firebase初期化の改善
- 問題: テスト実行時にFirebaseの初期化が必要になる
- 解決策: security.pyを修正し、Firebaseの初期化を遅延させ、テスト中は初期化しないように変更
  ```python
  # テスト中やFirebase設定が存在しない場合は初期化しない
  if os.environ.get('TESTING') == 'True':
      return
  ```

### 3. テスト環境の設定
- テスト用の環境変数設定を追加
  ```python
  os.environ['TESTING'] = 'True'
  os.environ['DATABASE_URL'] = 'sqlite:///:memory:'
  ```
- Firebaseのモック化を改善
  ```python
  @patch('firebase_admin.auth.verify_id_token')
  def test_get_current_user(mock_verify_token, client, db, test_listener):
      mock_verify_token.return_value = {"uid": "firebaseuid_listener"}
      # テストコード...
  ```

## 次のステップ
1. テスト実行環境の構築
   - Poetryの環境を適切に設定
   - テスト用のモックを完成させる
   ```bash
   cd indie-music-platform-backend
   poetry install
   PYTHONPATH=$PWD poetry run pytest tests/api/test_auth.py -v
   ```

2. バックエンドの動作確認
   - 単体テスト実行と修正
   - 開発サーバー起動
   ```bash
   cd indie-music-platform-backend
   poetry run uvicorn app.main:app --reload
   ```
   - APIエンドポイントの動作確認（Swagger UI: http://localhost:8000/docs）

3. フロントエンドとバックエンドの結合
   - mockApi.jsからバックエンドAPIへの切り替え
   ```javascript
   // src/api/index.js などを作成して実際のAPIクライアントを実装
   import axios from 'axios';

   const api = axios.create({
     baseURL: 'http://localhost:8000/api',
   });
   
   export const getNewReleases = async (limit = 8) => {
     const response = await api.get('/v1/tracks', { params: { limit } });
     return response.data;
   };
   // 他のAPI関数も同様に実装
   ```

4. エンドツーエンドの動作確認
   - 登録・ログインフロー
   - 楽曲アップロードフロー
   - 楽曲検索・再生フロー
   - 購入フロー

## 注意事項とヒント
1. **Firebase認証**
   - 開発環境ではFirebaseのモックを使用
   - 本番環境では正しいFirebaseのクレデンシャルが必要

2. **データベース操作**
   - 開発環境ではSQLiteを使用
   - 本番環境ではPostgreSQLに接続
   - マイグレーションはAlembicで管理: `poetry run alembic upgrade head`

3. **ファイルアップロード**
   - S3の設定が必要（本番環境）
   - 開発環境ではローカルストレージも選択肢

4. **決済処理**
   - Stripeの設定が必要
   - テスト環境では Stripe のテストモードを使用

## 環境構築コマンド（参考）
```bash
# バックエンド
cd indie-music-platform-backend
poetry install  # 依存関係のインストール
PYTHONPATH=$PWD poetry run pytest  # テスト実行
poetry run uvicorn app.main:app --reload  # 開発サーバー起動

# フロントエンド
cd indie-music-platform-frontend
npm install
npm run dev  # 開発サーバー起動
```

## ファイル構造の重要なポイント
- バックエンドの主要ファイル:
  - `app/main.py`: アプリケーションのエントリーポイント
  - `app/api/router.py`: APIルーターの設定
  - `app/models/`: データベースモデル
  - `app/schemas/`: Pydanticスキーマ
  - `app/services/`: ビジネスロジック
  - `app/core/`: 設定・セキュリティなどのコア機能

- フロントエンドの主要ファイル:
  - `src/App.jsx`: アプリケーションのルート
  - `src/router.jsx`: ルーティング設定
  - `src/pages/`: 各ページコンポーネント
  - `src/mockApi.js`: 開発用モックAPI（後で実際のAPIに置き換え）

## 今後の展望
- MVP機能の完成後、ユーザーテストを実施
- フィードバックに基づいて機能を改善・追加
- プレイリスト機能の追加を検討
- モバイルアプリ対応も将来的に視野に

これらの作業を完成させることで、MVPとしての基本機能が利用可能になり、初期テスト運用を開始できる状態になります。
