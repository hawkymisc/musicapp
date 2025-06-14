# デプロイ前チェックリスト

## 🚨 人手作業が必要な項目

### **1. Azure アカウント準備**
- [ ] Azure アカウント作成 (https://azure.microsoft.com/ja-jp/free/)
- [ ] Azure CLI インストール
  ```bash
  # macOS
  brew install azure-cli
  
  # Windows
  # Azure CLI インストーラーをダウンロード
  
  # Ubuntu/Debian
  curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
  ```
- [ ] Azure にログイン
  ```bash
  az login
  ```
- [ ] サブスクリプション確認
  ```bash
  az account list --output table
  ```

### **2. ドメイン準備（オプション）**
- [ ] ドメイン取得（お名前.com、ムームードメイン等）
- [ ] DNS 管理画面アクセス確認
- [ ] CNAME レコード設定権限確認

### **3. Firebase 準備**
- [ ] Firebase プロジェクト作成 (https://console.firebase.google.com/)
- [ ] Authentication 有効化
- [ ] Admin SDK サービスアカウントキー生成
  ```
  Firebase Console > プロジェクト設定 > サービスアカウント > 
  「新しい秘密鍵の生成」クリック > JSONファイルダウンロード
  ```
- [ ] ダウンロードしたファイルを `firebase-credentials.json` として保存

### **4. 支払い情報（推定月額費用）**
- [ ] Azure 支払い方法設定
- [ ] 予算アラート設定（推奨: ¥15,000/月）

**推定月額費用:**
```
Container Apps (0.5vCPU, 1GB):    約¥2,000
PostgreSQL Basic (B1ms):          約¥6,000  
Blob Storage (100GB):             約¥1,000
Container Registry (Basic):       約¥500
合計:                             約¥9,500/月
```

---

## ✅ 自動実行される項目

### **インフラストラクチャ**
- [x] Azure リソースグループ作成
- [x] PostgreSQL データベース作成・設定
- [x] Blob Storage 作成・設定
- [x] Container Registry 作成
- [x] Container Apps 環境作成

### **アプリケーション**
- [x] Docker イメージビルド・プッシュ
- [x] 環境変数設定
- [x] アプリケーションデプロイ
- [x] ヘルスチェック確認

### **セキュリティ**
- [x] HTTPS 自動設定
- [x] ファイアウォール設定
- [x] 認証情報の安全な管理

---

## 🚀 デプロイ実行手順

### **ステップ1: 前提条件確認**
```bash
# Azure CLI インストール確認
az --version

# ログイン確認
az account show

# Docker 確認
docker --version
```

### **ステップ2: Firebase 設定**
```bash
# Firebase 認証情報ファイルを配置
cp /path/to/your/firebase-credentials.json ./firebase-credentials.json
```

### **ステップ3: デプロイ実行**
```bash
# デプロイスクリプト実行
./deploy/azure-deploy.sh minimal
```

### **ステップ4: 動作確認**
```bash
# ヘルスチェック
curl https://YOUR_APP_URL/health

# API 確認
curl https://YOUR_APP_URL/api/v1/features/
```

---

## 📊 デプロイ完了後の確認項目

### **基本動作確認**
- [ ] アプリケーション起動確認
- [ ] データベース接続確認
- [ ] ストレージ接続確認
- [ ] API エンドポイント確認

### **セキュリティ確認**
- [ ] HTTPS 接続確認
- [ ] 認証機能確認
- [ ] レート制限確認
- [ ] CORS 設定確認

### **機能確認**
- [ ] ユーザー登録・ログイン
- [ ] 楽曲アップロード
- [ ] 楽曲ストリーミング
- [ ] 楽曲検索
- [ ] 決済機能無効確認

---

## 🔧 トラブルシューティング

### **よくある問題**

#### **1. Azure CLI ログインエラー**
```bash
# ブラウザでログイン
az login

# デバイスコードでログイン
az login --use-device-code
```

#### **2. リソース作成権限エラー**
- サブスクリプションの共同作成者権限が必要
- 管理者に権限付与を依頼

#### **3. Docker ビルドエラー**
```bash
# Docker デーモン起動確認
docker info

# キャッシュクリア
docker system prune -f
```

#### **4. データベース接続エラー**
- ファイアウォール設定確認
- 接続文字列確認
- パスワード特殊文字エスケープ

---

## 🗑️ クリーンアップ（削除）

### **リソース削除**
```bash
# 全リソース削除
./deploy/azure-deploy.sh cleanup

# 手動削除
az group delete --name indie-music-rg
```

### **ローカルファイル削除**
```bash
# 認証情報ファイル削除
rm .deployment-secrets.txt
rm firebase-credentials.json
```

---

## 📞 サポート

### **問題発生時の連絡先**
- Azure サポート: https://azure.microsoft.com/ja-jp/support/
- Firebase サポート: https://firebase.google.com/support/

### **ログ確認方法**
```bash
# Container Apps ログ確認
az containerapp logs show \
  --name indie-music-api \
  --resource-group indie-music-rg \
  --follow

# データベースログ確認
az postgres server-logs list \
  --resource-group indie-music-rg \
  --server indie-music-db-server
```

---

**次のステップ**: 上記の人手作業項目を完了してから `./deploy/azure-deploy.sh minimal` を実行してください。