# 🚀 デプロイ準備ガイド（Playwright自動化）

## 現在の状況

Playwrightを使用してメインプロファイルでAzureとFirebaseにアクセスしました。
以下の手順で認証情報を収集し、デプロイを準備します。

---

## 🔵 Azure Portal での作業

### **現在の状態**
- ✅ Azure Portal アクセス済み
- 🔄 手動サインインが必要

### **手動作業手順**

#### **1. Azure アカウントサインイン**
```
1. 現在開いているAzure Portal画面でサインイン
2. Microsoftアカウントまたは組織アカウントを使用
3. 多要素認証の完了
```

#### **2. サブスクリプション情報収集**
```
1. Azure Portal > サブスクリプション
2. 「サブスクリプションID」をコピー
3. 「ディレクトリID (テナントID)」をコピー
```

#### **3. 無料枠確認**
```
1. Azure Portal > 「無料サービス」で検索
2. 利用可能な無料枠を確認
3. Container Apps, PostgreSQL等の料金確認
```

---

## 🔥 Firebase Console での作業

### **現在の状態**
- ✅ Firebase Console アクセス済み
- 🔄 手動サインインが必要

### **手動作業手順**

#### **1. Firebase プロジェクト作成**
```
1. 現在開いているFirebase Console画面でサインイン
2. 「プロジェクトを作成」クリック
3. プロジェクト名: indie-music-platform
4. Google Analytics: 無効でも可
```

#### **2. Authentication 設定**
```
1. プロジェクト > Authentication > 始める
2. 「Sign-in method」タブ
3. 「メール/パスワード」を有効化
4. 「Google」を有効化（推奨）
```

#### **3. Service Account キー取得**
```
1. プロジェクト設定 ⚙️ > 「サービスアカウント」タブ
2. 「新しい秘密鍵の生成」クリック
3. JSONファイルをダウンロード
4. ファイル名を firebase-credentials.json に変更
```

---

## 🤖 自動化継続手順

認証完了後、以下のスクリプトで自動化を継続できます：

### **1. Azure CLI セットアップ**
```bash
# Azure CLI インストール
brew install azure-cli

# ログイン（ブラウザが開きます）
az login

# サブスクリプション確認
az account list --output table
```

### **2. Firebase 認証ファイル配置**
```bash
# ダウンロードしたJSONファイルを移動
mv ~/Downloads/indie-music-platform-*.json ./firebase-credentials.json

# 確認
ls -la firebase-credentials.json
```

### **3. デプロイ前最終確認**
```bash
# Azure ログイン状態確認
az account show

# Firebase ファイル確認
cat firebase-credentials.json | jq .project_id
```

---

## 📋 収集すべき情報チェックリスト

### **Azure 情報**
- [ ] サブスクリプションID
- [ ] テナントID
- [ ] Azure CLI ログイン完了

### **Firebase 情報**
- [ ] プロジェクトID
- [ ] Service Account JSON ファイル
- [ ] Authentication 設定完了

### **オプション**
- [ ] ドメイン取得（例：your-app.com）
- [ ] DNS 設定権限

---

## 🎯 次のアクション

### **準備完了後の実行**
```bash
# 環境確認
./deploy/pre-deployment-checklist.md

# デプロイ実行
./deploy/azure-deploy.sh minimal
```

### **推定時間**
```
手動認証作業: 15分
自動デプロイ: 25分
合計: 40分
```

### **推定コスト**
```
月額: ¥9,500
- Container Apps: ¥2,000
- PostgreSQL: ¥6,000
- Storage: ¥1,000
- その他: ¥500
```

---

## 🔧 トラブルシューティング

### **よくある問題**

#### **Azure サインインエラー**
```
- ブラウザのプライベートモードを試す
- 異なるMicrosoftアカウントを使用
- 組織アカウントの場合は管理者に確認
```

#### **Firebase プロジェクト作成エラー**
```
- Googleアカウントの確認
- プロジェクト名の重複確認
- ブラウザキャッシュのクリア
```

#### **Service Account キー取得エラー**
```
- プロジェクトオーナー権限の確認
- ブラウザの拡張機能を無効化
- 異なるブラウザで試行
```

---

## 🎉 完了後の確認

すべての準備が完了したら以下で確認：

```bash
# Azure 接続確認
az account show --output table

# Firebase ファイル確認
jq .project_id firebase-credentials.json

# デプロイ準備完了
echo "🚀 デプロイ準備完了！"
```

準備が完了しましたら、「準備完了」とお知らせください。
即座にデプロイを実行できます！