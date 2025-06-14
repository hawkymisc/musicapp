# Microsoft Azure デプロイガイド

## 🎯 Azure デプロイ概要

Microsoft Azureを使用してインディーズミュージックプラットフォームをデプロイするための包括的なガイドです。

## 🏗️ 必要なAzureサービス

### **1. 🚀 アプリケーション ホスティング**

#### **Azure Container Apps（推奨）**
```bash
# コンテナベースの自動スケーリング
- 用途: FastAPIアプリケーションのホスティング
- 特徴: 自動スケーリング、HTTPS自動設定、カスタムドメイン対応
- 料金: 従量課金（vCPU秒、メモリGB秒）
```

#### **代替案: Azure App Service**
```bash
# PaaS環境でのアプリケーション実行
- 用途: Dockerコンテナ直接デプロイ
- 特徴: マネージドサービス、CI/CD統合
- 料金: プラン制（B1: ¥1,500/月〜）
```

### **2. 📊 データベース**

#### **Azure Database for PostgreSQL（推奨）**
```bash
# マネージドPostgreSQLサービス
リソース名: indie-music-db-server
プラン: Basic B1ms（1vCore, 2GB RAM）
ストレージ: 100GB
料金: 約¥6,000/月
設定:
- SSL接続必須
- 自動バックアップ7日間
- 日本東部リージョン
```

### **3. 💾 ストレージ**

#### **Azure Blob Storage**
```bash
# 音楽ファイル・画像保存
アカウント名: indiemusicstorageaccount
レプリケーション: LRS（ローカル冗長ストレージ）
アクセス層: Hot（頻繁アクセス）
コンテナ:
- music-files（音楽ファイル）
- cover-images（カバーアート）
- user-uploads（ユーザーアップロード）
料金: 約¥1,000/月（100GB想定）
```

### **4. 🔐 セキュリティ・認証**

#### **Azure Key Vault**
```bash
# 秘密情報の安全な管理
Vault名: indie-music-keyvault
保存する秘密:
- データベース接続文字列
- Stripeシークレットキー
- Firebase認証情報
- ストレージアクセスキー
料金: 約¥500/月
```

### **5. 🚦 ネットワーク・セキュリティ**

#### **Azure Application Gateway（推奨）**
```bash
# ロードバランサー・WAF
- SSL証明書管理
- WAF（Web Application Firewall）
- 自動スケーリング
- カスタムドメイン設定
料金: 約¥10,000/月
```

#### **代替案: Azure CDN + Azure Front Door**
```bash
# グローバル配信・DDoS保護
- CDN配信
- DDoS Protection
- 地理的ルーティング
料金: 約¥5,000/月
```

### **6. 📊 監視・ログ**

#### **Azure Application Insights**
```bash
# アプリケーション監視
- パフォーマンス監視
- エラー追跡
- ユーザー行動分析
- アラート設定
料金: 従量課金（基本無料枠あり）
```

#### **Azure Log Analytics**
```bash
# ログ収集・分析
- 構造化ログ収集
- セキュリティイベント分析
- ダッシュボード作成
料金: ¥500/GB/月
```

### **7. ⚡ キャッシュ・セッション**

#### **Azure Cache for Redis**
```bash
# セッション・キャッシュ管理
プラン: Basic C0（250MB）
用途:
- ユーザーセッション
- API レスポンスキャッシュ
- レート制限カウンタ
料金: 約¥2,000/月
```

---

## 💰 月額料金見積もり

### **スタートアップ構成（〜100ユーザー）**
```
Azure Container Apps       : ¥ 2,000
PostgreSQL Basic B1ms      : ¥ 6,000
Blob Storage (100GB)       : ¥ 1,000
Key Vault                  : ¥   500
Application Insights       : ¥     0（基本無料）
Redis Basic C0             : ¥ 2,000
Application Gateway        : ¥10,000
----------------------------------------
合計                       : ¥21,500/月
```

### **エコノミー構成（〜50ユーザー）**
```
App Service B1             : ¥ 1,500
PostgreSQL Basic B1ms      : ¥ 6,000
Blob Storage (50GB)        : ¥   500
Key Vault                  : ¥   500
Application Insights       : ¥     0
----------------------------------------
合計                       : ¥ 8,500/月
```

---

## 🚀 デプロイ手順

### **Phase 1: 基盤リソース作成**

#### 1. リソースグループ作成
```bash
az group create \
  --name indie-music-rg \
  --location japaneast
```

#### 2. PostgreSQLデータベース作成
```bash
az postgres server create \
  --resource-group indie-music-rg \
  --name indie-music-db-server \
  --location japaneast \
  --admin-user adminuser \
  --admin-password "SecurePassword123!" \
  --sku-name B_Gen5_1 \
  --version 13

# データベース作成
az postgres db create \
  --resource-group indie-music-rg \
  --server-name indie-music-db-server \
  --name indie_music_db
```

#### 3. ストレージアカウント作成
```bash
az storage account create \
  --name indiemusicstorageaccount \
  --resource-group indie-music-rg \
  --location japaneast \
  --sku Standard_LRS

# Blobコンテナ作成
az storage container create \
  --name music-files \
  --account-name indiemusicstorageaccount

az storage container create \
  --name cover-images \
  --account-name indiemusicstorageaccount
```

#### 4. Key Vault作成
```bash
az keyvault create \
  --name indie-music-keyvault \
  --resource-group indie-music-rg \
  --location japaneast
```

### **Phase 2: アプリケーションデプロイ**

#### 1. Container Registry作成
```bash
az acr create \
  --resource-group indie-music-rg \
  --name indiemusicregistry \
  --sku Basic
```

#### 2. Dockerイメージビルド・プッシュ
```bash
# ローカルでビルド
docker build -t indie-music-api:latest .

# ACRにプッシュ
az acr login --name indiemusicregistry
docker tag indie-music-api:latest indiemusicregistry.azurecr.io/indie-music-api:latest
docker push indiemusicregistry.azurecr.io/indie-music-api:latest
```

#### 3. Container Apps環境作成
```bash
az containerapp env create \
  --name indie-music-env \
  --resource-group indie-music-rg \
  --location japaneast
```

#### 4. アプリケーションデプロイ
```bash
az containerapp create \
  --name indie-music-api \
  --resource-group indie-music-rg \
  --environment indie-music-env \
  --image indiemusicregistry.azurecr.io/indie-music-api:latest \
  --target-port 8000 \
  --ingress 'external' \
  --registry-server indiemusicregistry.azurecr.io \
  --env-vars \
    ENVIRONMENT=production \
    DATABASE_URL=secretref:database-url \
    STRIPE_API_KEY=secretref:stripe-api-key
```

### **Phase 3: SSL証明書・ドメイン設定**

#### 1. カスタムドメイン設定
```bash
az containerapp hostname add \
  --hostname yourdomain.com \
  --name indie-music-api \
  --resource-group indie-music-rg
```

#### 2. SSL証明書設定
```bash
# Let's Encryptまたは持参証明書の設定
az containerapp ssl upload \
  --certificate-file certificate.pfx \
  --certificate-password "password" \
  --name indie-music-api \
  --resource-group indie-music-rg
```

---

## 🔒 セキュリティ設定

### **1. Network Security Group**
```bash
# HTTPSのみ許可
az network nsg rule create \
  --resource-group indie-music-rg \
  --nsg-name indie-music-nsg \
  --name AllowHTTPS \
  --protocol Tcp \
  --direction Inbound \
  --priority 1000 \
  --source-address-prefix '*' \
  --source-port-range '*' \
  --destination-address-prefix '*' \
  --destination-port-range 443 \
  --access Allow
```

### **2. Azure Key Vault設定**
```bash
# 秘密情報を安全に保存
az keyvault secret set \
  --vault-name indie-music-keyvault \
  --name database-url \
  --value "postgresql://adminuser:SecurePassword123!@indie-music-db-server.postgres.database.azure.com:5432/indie_music_db?sslmode=require"

az keyvault secret set \
  --vault-name indie-music-keyvault \
  --name stripe-api-key \
  --value "sk_live_YOUR_STRIPE_KEY"
```

### **3. Managed Identity設定**
```bash
# アプリケーションがKey Vaultにアクセス
az containerapp identity assign \
  --name indie-music-api \
  --resource-group indie-music-rg \
  --system-assigned
```

---

## 📊 監視・ログ設定

### **1. Application Insights**
```bash
az monitor app-insights component create \
  --app indie-music-insights \
  --location japaneast \
  --resource-group indie-music-rg \
  --application-type web
```

### **2. アラート設定**
```bash
# エラー率アラート
az monitor metrics alert create \
  --name "High Error Rate" \
  --resource-group indie-music-rg \
  --scopes "/subscriptions/YOUR_SUBSCRIPTION/resourceGroups/indie-music-rg/providers/Microsoft.App/containerApps/indie-music-api" \
  --condition "avg requests/failed > 10" \
  --description "High error rate detected"
```

---

## 🔄 CI/CD設定（GitHub Actions）

### **1. GitHub Secrets設定**
```bash
# GitHub リポジトリに以下のシークレットを追加
AZURE_CREDENTIALS          # Azure サービスプリンシパル
AZURE_SUBSCRIPTION_ID      # Azure サブスクリプション ID
AZURE_RESOURCE_GROUP       # indie-music-rg
AZURE_CONTAINER_REGISTRY   # indiemusicregistry.azurecr.io
```

### **2. デプロイワークフロー**
```yaml
# .github/workflows/azure-deploy.yml
name: Deploy to Azure

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    
    - name: Login to Azure
      uses: azure/login@v1
      with:
        creds: ${{ secrets.AZURE_CREDENTIALS }}
    
    - name: Build and push image
      run: |
        az acr build --registry ${{ secrets.AZURE_CONTAINER_REGISTRY }} --image indie-music-api:${{ github.sha }} .
    
    - name: Deploy to Container Apps
      run: |
        az containerapp update \
          --name indie-music-api \
          --resource-group ${{ secrets.AZURE_RESOURCE_GROUP }} \
          --image ${{ secrets.AZURE_CONTAINER_REGISTRY }}/indie-music-api:${{ github.sha }}
```

---

## 🚨 トラブルシューティング

### **よくある問題**

#### 1. データベース接続エラー
```bash
# PostgreSQL ファイアウォール設定確認
az postgres server firewall-rule create \
  --resource-group indie-music-rg \
  --server indie-music-db-server \
  --name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0
```

#### 2. ストレージアクセスエラー
```bash
# CORS設定
az storage cors add \
  --methods GET PUT POST \
  --origins https://yourdomain.com \
  --services b \
  --account-name indiemusicstorageaccount
```

#### 3. SSL証明書エラー
```bash
# 証明書検証
az containerapp hostname list \
  --name indie-music-api \
  --resource-group indie-music-rg
```

---

## 📋 デプロイ前チェックリスト

### **✅ 必須項目**
- [ ] Azure サブスクリプション作成
- [ ] リソースグループ作成
- [ ] PostgreSQL データベース設定
- [ ] Blob Storage設定
- [ ] Key Vault設定
- [ ] 本番環境変数設定
- [ ] ドメイン取得・DNS設定
- [ ] SSL証明書設定

### **✅ セキュリティ項目**
- [ ] Network Security Group設定
- [ ] Key Vault アクセス制御
- [ ] Managed Identity設定
- [ ] HTTPS強制リダイレクト
- [ ] CORS設定
- [ ] WAF（Web Application Firewall）設定

### **✅ 監視項目**
- [ ] Application Insights設定
- [ ] アラート設定
- [ ] ログ Analytics設定
- [ ] ダッシュボード作成

### **✅ 運用項目**
- [ ] バックアップ設定
- [ ] 自動スケーリング設定
- [ ] CI/CD パイプライン設定
- [ ] 災害復旧計画

---

## 🎯 デプロイ後の確認事項

```bash
# 1. アプリケーション起動確認
curl https://yourdomain.com/health

# 2. データベース接続確認
curl https://yourdomain.com/api/v1/tracks

# 3. ファイルアップロード確認
# （管理画面からテストファイルアップロード）

# 4. 決済機能確認
# （Stripeテストカードでの決済テスト）

# 5. 監視ダッシュボード確認
# Application Insights でメトリクス確認
```

---

この Azure デプロイガイドに従って、段階的にデプロイを進めることで、安全で拡張可能なプラットフォームが構築できます。