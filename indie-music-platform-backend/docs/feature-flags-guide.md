# 機能フラグ管理ガイド

## 概要

インディーズミュージックプラットフォームでは、決済機能をはじめとする各種機能を環境変数またはJSONファイルで動的に制御できる機能フラグシステムを導入しています。

## 🎯 主な用途

### **決済機能の制御**
- **本番デプロイ前**: 決済なしで安全にデプロイ
- **段階的ロールアウト**: 一部ユーザーのみに決済機能を提供
- **緊急停止**: 問題発生時に即座に決済機能を無効化

### **新機能のテスト**
- **ベータ機能**: 限定ユーザーでの新機能テスト
- **A/Bテスト**: 異なる機能バージョンの比較検証

### **運用制御**
- **メンテナンス**: 計画的なサービス停止
- **負荷制御**: 高負荷時の機能制限

---

## 🔧 設定方法

### **方法1: 環境変数（推奨）**

```bash
# 決済機能の制御
export PAYMENT_ENABLED=false
export PAYMENT_COMING_SOON_MESSAGE="決済機能は近日公開予定です！"

# アプリケーション起動
uvicorn app.main:app --reload
```

### **方法2: JSONファイル**

```bash
# 設定ファイル指定
export FEATURE_FLAGS_CONFIG=./feature_flags.no-payment.json

# または直接ファイル編集
cp feature_flags.no-payment.json feature_flags.json
```

### **方法3: 組み合わせ**
```bash
# JSONファイルをベースに環境変数で上書き
export FEATURE_FLAGS_CONFIG=./feature_flags.json
export PAYMENT_ENABLED=false
```

---

## 📋 主要な機能フラグ

### **決済関連**
```bash
PAYMENT_ENABLED=true/false                    # 決済機能全体
PAYMENT_METHODS_ENABLED=true/false            # 支払い方法管理
PURCHASE_DOWNLOADS_ENABLED=true/false         # 購入済みダウンロード
PAYMENT_COMING_SOON_MESSAGE="メッセージ"       # Coming Soonメッセージ
```

### **機能制御**
```bash
SUBSCRIPTION_PLANS_ENABLED=true/false         # サブスクリプション
LIVE_STREAMING_ENABLED=true/false            # ライブ配信
SOCIAL_FEATURES_ENABLED=true/false           # ソーシャル機能
ANALYTICS_DASHBOARD_ENABLED=true/false       # 分析ダッシュボード
ARTIST_VERIFICATION_ENABLED=true/false       # アーティスト認証
```

### **制限値**
```bash
MAX_UPLOADS_PER_DAY=10                       # 1日のアップロード上限
MAX_FILE_SIZE_MB=100                         # ファイルサイズ上限
FREE_STREAMING_LIMIT=100                     # 無料ストリーミング上限
```

---

## 🚀 実用的な使用例

### **シナリオ1: 決済なしでデプロイ**

```bash
# 環境変数設定
export PAYMENT_ENABLED=false
export PAYMENT_COMING_SOON_MESSAGE="🎵 決済機能は近日公開予定です！現在は全楽曲を無料でお楽しみいただけます。"

# または設定ファイル使用
cp .env.no-payment .env
```

**結果:**
- 購入ボタンが「決済準備中」に変更
- ダウンロードは無料で利用可能
- Coming Soonメッセージ表示

### **シナリオ2: 段階的決済機能導入**

```bash
# Phase 1: 基本決済のみ
export PAYMENT_ENABLED=true
export PAYMENT_METHODS_ENABLED=false

# Phase 2: 支払い方法管理追加
export PAYMENT_METHODS_ENABLED=true
```

### **シナリオ3: 緊急メンテナンス**

```bash
# 決済機能のみ停止
export PAYMENT_ENABLED=false
export PAYMENT_COMING_SOON_MESSAGE="決済システムのメンテナンス中です。しばらくお待ちください。"

# 全体メンテナンス
export MAINTENANCE_MODE=true
```

---

## 🎛️ API エンドポイント

### **機能フラグ取得**
```bash
# 全機能フラグ取得
GET /api/v1/features/

# 決済機能のみ取得
GET /api/v1/features/payment

# サービス状態取得
GET /api/v1/features/status
```

### **レスポンス例**
```json
{
  "payment": {
    "enabled": false,
    "coming_soon_message": "決済機能は近日公開予定です！",
    "downloads_enabled": true
  },
  "features": {
    "social_features": true,
    "analytics_dashboard": true
  }
}
```

---

## 🎨 フロントエンド統合

### **PurchaseButton コンポーネント**
```jsx
import PurchaseButton from './components/common/PurchaseButton';

// 自動的に機能フラグを確認して表示を切り替え
<PurchaseButton 
  track={track} 
  userId={userId} 
  onPurchaseSuccess={handleSuccess} 
/>
```

### **DownloadButton コンポーネント**
```jsx
import DownloadButton from './components/common/DownloadButton';

// 決済状態に応じて無料/有料ダウンロードを切り替え
<DownloadButton 
  track={track} 
  userId={userId} 
/>
```

---

## 📊 モニタリングとログ

### **機能フラグの確認**
```bash
# 現在の設定確認
curl http://localhost:8000/api/v1/features/ | jq

# 決済機能状態確認
curl http://localhost:8000/api/v1/features/payment | jq
```

### **ログ出力例**
```
INFO: 決済機能が無効なため、purchasesルーターをスキップしました
INFO: 機能フラグ: payment.enabled=false
```

---

## 🔄 デプロイメント戦略

### **ブルーグリーンデプロイ**
```bash
# Blue環境（現在の本番）
PAYMENT_ENABLED=true

# Green環境（新バージョンテスト）
PAYMENT_ENABLED=false
FEATURE_FLAGS_CONFIG=./feature_flags.new-version.json
```

### **カナリアリリース**
```bash
# カナリアインスタンス（10%のユーザー）
PAYMENT_ENABLED=true
PAYMENT_TEST_MODE=true

# メインインスタンス（90%のユーザー）
PAYMENT_ENABLED=false
```

---

## 🛠️ 設定ファイルテンプレート

### **本番環境用**
```json
{
  "payment": {
    "enabled": true,
    "methods_enabled": true,
    "downloads_enabled": true,
    "webhook_enabled": true
  },
  "features": {
    "subscription_plans": true,
    "analytics_dashboard": true,
    "artist_verification": true
  }
}
```

### **開発環境用**
```json
{
  "payment": {
    "enabled": false,
    "downloads_enabled": true,
    "coming_soon_message": "開発環境では決済機能は無効です。"
  },
  "debug": {
    "enable_detailed_logging": true,
    "show_debug_info": true
  }
}
```

---

## 🚨 注意事項

### **本番環境での注意点**
1. **決済機能の切り替えは慎重に**: ユーザーの購入途中での無効化は避ける
2. **ログ監視**: 機能切り替え後は必ずエラーログを確認
3. **ロールバック準備**: 問題発生時の即座の復旧手順を準備

### **開発時の注意点**
1. **環境変数の優先順位**: 環境変数 > JSONファイル > デフォルト値
2. **キャッシュクリア**: 設定変更後はアプリケーション再起動が必要
3. **テスト環境**: 本番と同じ機能フラグ設定でのテストを推奨

---

## 📝 よくある質問

### **Q: 決済機能を無効にしても購入履歴は残りますか？**
A: はい、データベースの購入履歴は保持されます。APIエンドポイントのみが無効化されます。

### **Q: 機能フラグの変更は即座に反映されますか？**
A: 環境変数の変更は アプリケーション再起動が必要です。リアルタイム反映には外部設定サービスの導入を検討してください。

### **Q: 複数の設定ファイルを使い分けできますか？**
A: はい、`FEATURE_FLAGS_CONFIG`環境変数で指定できます。

---

この機能フラグシステムにより、安全で柔軟なサービス運用が可能になります。