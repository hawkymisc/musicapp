#!/bin/bash

# Azure デプロイスクリプト
# 使用方法: ./deploy/azure-deploy.sh [option]
# オプション: minimal | full

set -e

# 設定
RESOURCE_GROUP="indie-music-rg"
LOCATION="japaneast"
APP_NAME="indie-music-api"
DB_SERVER_NAME="indie-music-db-server-$(date +%s)"
STORAGE_ACCOUNT="indiemusicstorage$(date +%s)"
CONTAINER_REGISTRY="indiemusicregistry"

# カラー出力用
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 前提条件チェック
check_prerequisites() {
    print_status "前提条件をチェックしています..."
    
    # Azure CLI チェック
    if ! command -v az &> /dev/null; then
        print_error "Azure CLI がインストールされていません。"
        print_error "インストール: https://docs.microsoft.com/ja-jp/cli/azure/install-azure-cli"
        exit 1
    fi
    
    # ログイン状態チェック
    if ! az account show &> /dev/null; then
        print_error "Azure にログインしていません。"
        print_error "実行してください: az login"
        exit 1
    fi
    
    # Docker チェック
    if ! command -v docker &> /dev/null; then
        print_error "Docker がインストールされていません。"
        exit 1
    fi
    
    print_success "前提条件チェック完了"
}

# リソースグループ作成
create_resource_group() {
    print_status "リソースグループを作成しています..."
    
    az group create \
        --name $RESOURCE_GROUP \
        --location $LOCATION \
        --output table
    
    print_success "リソースグループ作成完了: $RESOURCE_GROUP"
}

# PostgreSQL データベース作成
create_database() {
    print_status "PostgreSQL データベースを作成しています..."
    
    # 管理者パスワード生成
    DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    echo "データベースパスワード: $DB_PASSWORD" > .deployment-secrets.txt
    
    az postgres server create \
        --resource-group $RESOURCE_GROUP \
        --name $DB_SERVER_NAME \
        --location $LOCATION \
        --admin-user adminuser \
        --admin-password "$DB_PASSWORD" \
        --sku-name B_Gen5_1 \
        --version 11 \
        --storage-size 102400 \
        --output table
    
    # ファイアウォール設定
    az postgres server firewall-rule create \
        --resource-group $RESOURCE_GROUP \
        --server $DB_SERVER_NAME \
        --name AllowAzureServices \
        --start-ip-address 0.0.0.0 \
        --end-ip-address 0.0.0.0
    
    # データベース作成
    az postgres db create \
        --resource-group $RESOURCE_GROUP \
        --server-name $DB_SERVER_NAME \
        --name indie_music_db
    
    print_success "データベース作成完了: $DB_SERVER_NAME"
}

# ストレージアカウント作成
create_storage() {
    print_status "ストレージアカウントを作成しています..."
    
    az storage account create \
        --name $STORAGE_ACCOUNT \
        --resource-group $RESOURCE_GROUP \
        --location $LOCATION \
        --sku Standard_LRS \
        --output table
    
    # コンテナ作成
    STORAGE_KEY=$(az storage account keys list \
        --resource-group $RESOURCE_GROUP \
        --account-name $STORAGE_ACCOUNT \
        --query '[0].value' \
        --output tsv)
    
    az storage container create \
        --name music-files \
        --account-name $STORAGE_ACCOUNT \
        --account-key $STORAGE_KEY
    
    az storage container create \
        --name cover-images \
        --account-name $STORAGE_ACCOUNT \
        --account-key $STORAGE_KEY
    
    echo "ストレージアカウント: $STORAGE_ACCOUNT" >> .deployment-secrets.txt
    echo "ストレージキー: $STORAGE_KEY" >> .deployment-secrets.txt
    
    print_success "ストレージ作成完了: $STORAGE_ACCOUNT"
}

# Container Registry 作成
create_registry() {
    print_status "Container Registry を作成しています..."
    
    az acr create \
        --resource-group $RESOURCE_GROUP \
        --name $CONTAINER_REGISTRY \
        --sku Basic \
        --output table
    
    print_success "Container Registry 作成完了: $CONTAINER_REGISTRY"
}

# Docker イメージビルド・プッシュ
build_and_push_image() {
    print_status "Docker イメージをビルドしています..."
    
    # レジストリにログイン
    az acr login --name $CONTAINER_REGISTRY
    
    # イメージビルド・プッシュ
    az acr build \
        --registry $CONTAINER_REGISTRY \
        --image indie-music-api:latest \
        --file Dockerfile.simple \
        .
    
    print_success "Docker イメージプッシュ完了"
}

# Container Apps 環境作成
create_container_env() {
    print_status "Container Apps 環境を作成しています..."
    
    # Container Apps 拡張機能有効化
    az extension add --name containerapp --upgrade
    az provider register --namespace Microsoft.App
    az provider register --namespace Microsoft.OperationalInsights
    
    # 環境作成
    az containerapp env create \
        --name indie-music-env \
        --resource-group $RESOURCE_GROUP \
        --location $LOCATION \
        --output table
    
    print_success "Container Apps 環境作成完了"
}

# アプリケーションデプロイ
deploy_application() {
    print_status "アプリケーションをデプロイしています..."
    
    # 環境変数設定
    DB_PASSWORD=$(grep "データベースパスワード:" .deployment-secrets.txt | cut -d' ' -f2)
    STORAGE_KEY=$(grep "ストレージキー:" .deployment-secrets.txt | cut -d' ' -f2)
    
    DATABASE_URL="postgresql://adminuser:${DB_PASSWORD}@${DB_SERVER_NAME}.postgres.database.azure.com:5432/indie_music_db?sslmode=require"
    
    az containerapp create \
        --name $APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --environment indie-music-env \
        --image ${CONTAINER_REGISTRY}.azurecr.io/indie-music-api:latest \
        --target-port 8000 \
        --ingress 'external' \
        --registry-server ${CONTAINER_REGISTRY}.azurecr.io \
        --cpu 0.5 \
        --memory 1Gi \
        --min-replicas 1 \
        --max-replicas 3 \
        --env-vars \
            ENVIRONMENT=production \
            PAYMENT_ENABLED=false \
            DATABASE_URL="$DATABASE_URL" \
            AZURE_STORAGE_ACCOUNT_NAME=$STORAGE_ACCOUNT \
            AZURE_STORAGE_ACCOUNT_KEY="$STORAGE_KEY" \
            FIREBASE_CREDENTIALS_PATH="/app/tests/mocks/firebase_credentials.json" \
        --output table
    
    print_success "アプリケーションデプロイ完了"
}

# デプロイ情報表示
show_deployment_info() {
    print_success "デプロイ完了！"
    
    APP_URL=$(az containerapp show \
        --name $APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --query properties.configuration.ingress.fqdn \
        --output tsv)
    
    echo ""
    echo "=================================================="
    echo "          デプロイ情報"
    echo "=================================================="
    echo "アプリケーションURL: https://$APP_URL"
    echo "ヘルスチェック: https://$APP_URL/health"
    echo "API ドキュメント: https://$APP_URL/docs"
    echo ""
    echo "リソース情報:"
    echo "- リソースグループ: $RESOURCE_GROUP"
    echo "- データベース: $DB_SERVER_NAME"
    echo "- ストレージ: $STORAGE_ACCOUNT"
    echo "- Container Registry: $CONTAINER_REGISTRY"
    echo ""
    echo "認証情報は .deployment-secrets.txt に保存されています"
    echo "=================================================="
}

# クリーンアップ（オプション）
cleanup() {
    print_warning "リソースを削除しています..."
    
    read -p "本当にすべてのリソースを削除しますか？ (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        az group delete --name $RESOURCE_GROUP --yes --no-wait
        print_success "削除開始しました（バックグラウンドで実行中）"
    else
        print_status "削除をキャンセルしました"
    fi
}

# メイン実行
main() {
    case "${1:-deploy}" in
        "minimal"|"deploy")
            print_status "最小構成でデプロイを開始します..."
            check_prerequisites
            create_resource_group
            create_database
            create_storage
            create_registry
            build_and_push_image
            create_container_env
            deploy_application
            show_deployment_info
            ;;
        "cleanup")
            cleanup
            ;;
        *)
            echo "使用方法: $0 [minimal|cleanup]"
            echo "  minimal: 最小構成でデプロイ"
            echo "  cleanup: リソース削除"
            exit 1
            ;;
    esac
}

# デプロイ後チェック関数
post_deploy_check() {
    print_status "デプロイ後チェックを開始します..."
    
    APP_URL=$(az containerapp show \
        --name $APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --query properties.configuration.ingress.fqdn \
        --output tsv)
    
    if [[ -z "$APP_URL" ]]; then
        print_error "アプリケーションURLを取得できませんでした"
        return 1
    fi
    
    APP_URL="https://$APP_URL"
    print_status "アプリケーションURL: $APP_URL"
    
    # 起動待機
    print_status "アプリケーション起動を待機中..."
    sleep 30
    
    # ヘルスチェック（最大5回試行）
    print_status "ヘルスチェック実行中..."
    for i in {1..5}; do
        print_status "試行 $i/5..."
        if curl -s --max-time 30 "$APP_URL/health" > /dev/null 2>&1; then
            print_success "ヘルスチェック成功！"
            break
        elif [[ $i -eq 5 ]]; then
            print_warning "ヘルスチェック失敗。ログを確認してください。"
            return 1
        else
            print_status "30秒後に再試行..."
            sleep 30
        fi
    done
    
    # 基本エンドポイントチェック
    print_status "基本エンドポイントチェック中..."
    
    if curl -s --max-time 10 "$APP_URL/docs" > /dev/null 2>&1; then
        print_success "API ドキュメント (/docs) アクセス可能"
    else
        print_warning "API ドキュメント (/docs) アクセス不可"
    fi
    
    if curl -s --max-time 10 "$APP_URL/api/v1/features/" > /dev/null 2>&1; then
        print_success "機能API (/api/v1/features/) アクセス可能"
    else
        print_warning "機能API (/api/v1/features/) アクセス不可"
    fi
    
    # ログチェック
    print_status "最新ログチェック..."
    local log_errors=$(az containerapp logs show \
        --name $APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --tail 10 \
        --query "[?contains(Log, 'ERROR') || contains(Log, 'CRITICAL')].Log" \
        --output tsv 2>/dev/null)
    
    if [[ -n "$log_errors" ]]; then
        print_warning "ログにエラーが検出されました:"
        echo "$log_errors"
    else
        print_success "ログに重大なエラーは検出されませんでした"
    fi
    
    print_success "デプロイ後チェック完了"
    return 0
}

# リビジョン管理関数
manage_revisions() {
    print_status "リビジョン管理を実行中..."
    
    # 複数リビジョンモードに設定
    az containerapp revision set-mode \
        --name $APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --mode multiple > /dev/null 2>&1
    
    # アクティブなリビジョンを取得
    local revisions=$(az containerapp revision list \
        --name $APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --query "[?properties.active].name" \
        --output tsv)
    
    local revision_count=$(echo "$revisions" | wc -l | tr -d ' ')
    
    if [[ $revision_count -gt 1 ]]; then
        print_status "$revision_count 個のアクティブリビジョンが見つかりました"
        
        # 最新リビジョンを取得
        local latest_revision=$(echo "$revisions" | sort | tail -1)
        print_status "最新リビジョン: $latest_revision"
        
        # 最新リビジョンに100%トラフィックを設定
        local traffic_args=""
        for rev in $revisions; do
            if [[ "$rev" == "$latest_revision" ]]; then
                traffic_args="$traffic_args --revision-weight $rev=100"
            else
                traffic_args="$traffic_args --revision-weight $rev=0"
            fi
        done
        
        az containerapp ingress traffic set \
            --name $APP_NAME \
            --resource-group $RESOURCE_GROUP \
            $traffic_args > /dev/null 2>&1
        
        print_success "トラフィックを最新リビジョンに切り替えました"
        
        # 古いリビジョンを無効化
        for rev in $revisions; do
            if [[ "$rev" != "$latest_revision" ]]; then
                az containerapp revision deactivate \
                    --name $APP_NAME \
                    --resource-group $RESOURCE_GROUP \
                    --revision "$rev" > /dev/null 2>&1
                print_status "古いリビジョン $rev を無効化しました"
            fi
        done
    fi
    
    print_success "リビジョン管理完了"
}

# 拡張されたメイン実行
main() {
    case "${1:-deploy}" in
        "minimal"|"deploy")
            print_status "最小構成でデプロイを開始します..."
            check_prerequisites
            create_resource_group
            create_database
            create_storage
            create_registry
            build_and_push_image
            create_container_env
            deploy_application
            manage_revisions
            post_deploy_check
            show_deployment_info
            ;;
        "check")
            print_status "デプロイ後チェックのみ実行します..."
            check_prerequisites
            post_deploy_check
            ;;
        "cleanup")
            cleanup
            ;;
        *)
            echo "使用方法: $0 [minimal|check|cleanup]"
            echo "  minimal: 最小構成でデプロイ"
            echo "  check: デプロイ後チェックのみ実行"
            echo "  cleanup: リソース削除"
            exit 1
            ;;
    esac
}

# スクリプト実行
main "$@"