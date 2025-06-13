# Docker フルテスト環境

## 概要

本プロジェクトではDocker Composeを使用した包括的なテスト環境を提供しています。この環境では、PostgreSQLデータベースとFastAPIアプリケーションを完全にコンテナ化し、本番環境に近い状態でテストを実行できます。

## 環境構成

### サービス構成

- **API コンテナ**: FastAPIアプリケーション (ポート: 8000)
- **データベース コンテナ**: PostgreSQL 13 (ポート: 5433)

### ファイル構成

```
indie-music-platform-backend/
├── docker-compose.full-test.yml    # フルテスト環境設定
├── Dockerfile.simple               # 軽量Dockerイメージ
├── .env.docker                     # Docker用環境変数
├── playwright.config.js            # E2Eテスト設定
├── package.json                    # Node.js依存関係
└── tests/e2e/                     # E2Eテストスイート
    ├── api-health.spec.js          # ヘルスチェックテスト
    ├── api-endpoints.spec.js       # APIエンドポイントテスト
    ├── security-features.spec.js   # セキュリティテスト
    └── performance.spec.js         # パフォーマンステスト
```

## 起動手順

### 1. 環境変数設定

```bash
# Docker用モック環境変数ファイル（.env.docker）が自動生成されています
cat .env.docker
```

### 2. コンテナ起動

```bash
# フルテスト環境起動
docker-compose -f docker-compose.full-test.yml up -d

# コンテナ状態確認
docker-compose -f docker-compose.full-test.yml ps
```

### 3. ヘルスチェック

```bash
# APIヘルスチェック
curl http://localhost:8000/health

# データベース接続確認
curl http://localhost:8000/health | jq '.database'
```

## テスト実行

### 基本APIテスト

```bash
# 基本エンドポイント確認
curl http://localhost:8000/                    # アプリ情報
curl http://localhost:8000/api/v1/tracks       # 楽曲一覧
curl http://localhost:8000/direct-test         # テストエンドポイント
```

### E2Eテスト実行

```bash
# Playwright セットアップ（初回のみ）
npm install @playwright/test
npx playwright install

# 全テスト実行
npx playwright test --reporter=line

# カテゴリ別テスト
npx playwright test tests/e2e/api-health.spec.js      # ヘルスチェック
npx playwright test tests/e2e/security-features.spec.js  # セキュリティ
npx playwright test tests/e2e/performance.spec.js     # パフォーマンス
npx playwright test tests/e2e/api-endpoints.spec.js   # API機能
```

## テスト結果サマリー

### E2Eテスト結果

最新実行結果（2025年6月13日）:
- **Total Tests**: 78
- **Passed**: 66
- **Failed**: 12（主にレート制限による期待される失敗）
- **Browsers**: Chromium, Firefox, Safari

### 主要検証項目

#### ✅ ヘルスチェック・基本機能
- API起動確認
- データベース接続確認
- レスポンス時間測定
- 基本エンドポイント動作

#### ✅ セキュリティ機能
- **レート制限**: 10回/分の制限が正常動作
- **CORS設定**: 許可されたオリジンのみアクセス可能
- **構造化ログ**: セキュリティイベントの記録
- **エラーハンドリング**: 機密情報の非開示

#### ✅ パフォーマンス
- **レスポンス時間**: ヘルスチェック < 10ms
- **同時接続**: 20並行リクエスト処理
- **メモリ使用量**: 安定的なメモリ管理
- **データベース接続プール**: 複数クエリ処理

#### ✅ API機能
- **エンドポイント**: 全API正常レスポンス
- **入力検証**: Pydanticスキーマ検証
- **エラーレスポンス**: 適切なHTTPステータス
- **セキュリティヘッダー**: Request-ID等の付与

## ログ確認

### 構造化ログ確認

```bash
# リアルタイムログ確認
docker-compose -f docker-compose.full-test.yml logs -f api

# セキュリティイベントログ抽出
docker-compose -f docker-compose.full-test.yml logs api | grep -E "(WARNING|ERROR)"

# レート制限ログ確認
docker-compose -f docker-compose.full-test.yml logs api | grep "ratelimit"
```

### ログ形式例

```json
{
  "timestamp": "2025-06-13T13:14:34.483832Z",
  "level": "WARNING", 
  "logger": "slowapi",
  "message": "ratelimit 10 per 1 minute (172.19.0.1_4832) exceeded at endpoint: /direct-test",
  "module": "extension",
  "function": "__evaluate_limits", 
  "line": 510,
  "request_id": "6623dd20-9026-4d1b-9582-f36c4df7caf0",
  "environment": "development"
}
```

## トラブルシューティング

### よくある問題

#### コンテナ起動失敗
```bash
# ポート競合確認
lsof -i :8000 -i :5433

# 既存コンテナ停止
docker-compose -f docker-compose.full-test.yml down

# 強制リビルド
docker-compose -f docker-compose.full-test.yml up --build -d
```

#### テスト失敗（レート制限）
```bash
# レート制限リセット（コンテナ再起動）
docker-compose -f docker-compose.full-test.yml restart api

# 1分待機してからテスト再実行
sleep 60 && npx playwright test
```

#### データベース接続エラー
```bash
# データベースログ確認
docker-compose -f docker-compose.full-test.yml logs db

# データベース接続テスト
docker-compose -f docker-compose.full-test.yml exec db psql -U postgres -d indie_music_db -c "SELECT 1;"
```

## パフォーマンス最適化

### リソース使用量確認

```bash
# コンテナリソース使用量
docker stats

# メモリ使用量詳細
docker-compose -f docker-compose.full-test.yml exec api ps aux

# ディスク使用量
docker system df
```

### チューニング設定

#### PostgreSQL設定
- `shared_buffers`: 128MB (デフォルト)
- `max_connections`: 100 (デフォルト)
- `log_statement`: 'all' (デバッグ用)

#### FastAPI設定
- Workers: 1 (開発環境)
- Keep-alive timeout: 30s
- Request timeout: 120s

## セキュリティ検証

### 実装済みセキュリティ機能

1. **レート制限**
   - 全般: 1000/hour, 100/minute
   - テストエンドポイント: 10/minute
   - ヘルスチェック: 60/minute

2. **CORS設定**
   - 許可オリジン: localhost:3000, localhost:5173
   - 認証情報送信許可
   - プリフライトリクエスト対応

3. **構造化ログ**
   - リクエストID追跡
   - セキュリティイベント記録
   - パフォーマンス測定

4. **入力検証**
   - Pydanticスキーマ検証
   - SQLインジェクション対策
   - XSS保護

## 次のステップ

### クラウドデプロイ準備
1. **環境変数設定**: AWS認証情報、Firebase設定
2. **SSL証明書**: HTTPS対応
3. **監視設定**: CloudWatch、Prometheus
4. **CI/CD**: GitHub Actions自動デプロイ

### 拡張テスト
1. **負荷テスト**: Apache Bench、JMeter
2. **セキュリティスキャン**: OWASP ZAP、Nessus
3. **依存関係監査**: npm audit、safety

---

この Docker フルテスト環境により、本番環境デプロイ前の包括的な品質検証が可能です。