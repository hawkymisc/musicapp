#!/bin/bash

# インディーズミュージックプラットフォーム ヘルスチェックスクリプト
# 使用方法: ./deploy/health-check.sh [option]
# オプション: quick | full | monitor

set -e

# 設定
RESOURCE_GROUP="indie-music-rg"
APP_NAME="indie-music-api"

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

# アプリケーションURL取得
get_app_url() {
    local app_url=$(az containerapp show \
        --name $APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --query properties.configuration.ingress.fqdn \
        --output tsv 2>/dev/null)
    
    if [[ -z "$app_url" ]]; then
        print_error "アプリケーションURLを取得できませんでした"
        return 1
    fi
    
    echo "https://$app_url"
}

# クイックチェック
quick_check() {
    print_status "クイックヘルスチェック開始..."
    
    local app_url=$(get_app_url)
    if [[ $? -ne 0 ]]; then
        return 1
    fi
    
    print_status "URL: $app_url"
    
    # ヘルスチェック
    print_status "ヘルスチェック実行中..."
    if response=$(curl -s --max-time 15 "$app_url/health"); then
        print_success "ヘルスチェック成功"
        echo "Response: $response"
        return 0
    else
        print_error "ヘルスチェック失敗"
        return 1
    fi
}

# フルチェック
full_check() {
    print_status "フルヘルスチェック開始..."
    
    local app_url=$(get_app_url)
    if [[ $? -ne 0 ]]; then
        return 1
    fi
    
    print_status "URL: $app_url"
    
    # Container App状態チェック
    print_status "Container App状態確認中..."
    local app_status=$(az containerapp show \
        --name $APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --query properties.runningStatus \
        --output tsv 2>/dev/null)
    
    if [[ "$app_status" == "Running" ]]; then
        print_success "Container App稼働中"
    else
        print_warning "Container App状態: $app_status"
    fi
    
    # ヘルスチェック（リトライ付き）
    print_status "ヘルスチェック実行中（最大3回試行）..."
    for i in {1..3}; do
        print_status "試行 $i/3..."
        if response=$(curl -s --max-time 20 "$app_url/health"); then
            print_success "ヘルスチェック成功"
            echo "Response: $response"
            break
        elif [[ $i -eq 3 ]]; then
            print_error "ヘルスチェック失敗"
            return 1
        else
            print_status "10秒後に再試行..."
            sleep 10
        fi
    done
    
    # 基本エンドポイントチェック
    print_status "基本エンドポイントチェック中..."
    
    endpoints=(
        "/docs:API ドキュメント"
        "/api/v1/features/:機能API"
        "/openapi.json:OpenAPI仕様"
    )
    
    for endpoint_info in "${endpoints[@]}"; do
        IFS=':' read -r endpoint description <<< "$endpoint_info"
        if curl -s --max-time 10 "$app_url$endpoint" > /dev/null 2>&1; then
            print_success "$description ($endpoint) アクセス可能"
        else
            print_warning "$description ($endpoint) アクセス不可"
        fi
    done
    
    # リビジョン情報
    print_status "リビジョン情報確認中..."
    az containerapp revision list \
        --name $APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --query "[?properties.active].{Name:name, Active:properties.active, TrafficWeight:properties.trafficWeight, Created:properties.creationTimestamp}" \
        --output table 2>/dev/null
    
    # ログチェック
    print_status "最新ログチェック中..."
    local recent_logs=$(az containerapp logs show \
        --name $APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --tail 5 \
        --query "[].Log" \
        --output tsv 2>/dev/null)
    
    if [[ -n "$recent_logs" ]]; then
        print_success "最新ログ:"
        echo "$recent_logs"
    else
        print_warning "ログを取得できませんでした"
    fi
    
    print_success "フルヘルスチェック完了"
}

# 継続監視
monitor_check() {
    print_status "継続監視モード開始（Ctrl+Cで停止）..."
    
    local app_url=$(get_app_url)
    if [[ $? -ne 0 ]]; then
        return 1
    fi
    
    print_status "URL: $app_url"
    print_status "30秒間隔でヘルスチェックを実行します..."
    
    local success_count=0
    local failure_count=0
    
    while true; do
        local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
        
        if curl -s --max-time 10 "$app_url/health" > /dev/null 2>&1; then
            success_count=$((success_count + 1))
            print_success "[$timestamp] ヘルスチェック成功 (連続成功: $success_count)"
        else
            failure_count=$((failure_count + 1))
            print_error "[$timestamp] ヘルスチェック失敗 (連続失敗: $failure_count)"
        fi
        
        sleep 30
    done
}

# エラー詳細診断
diagnose_errors() {
    print_status "エラー詳細診断開始..."
    
    # Container App詳細状態
    print_status "Container App詳細状態:"
    az containerapp show \
        --name $APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --query "{Name:name, Status:properties.runningStatus, Replicas:properties.template.scale, LastModified:systemData.lastModifiedAt}" \
        --output table 2>/dev/null
    
    # エラーログ検索
    print_status "エラーログ検索中..."
    local error_logs=$(az containerapp logs show \
        --name $APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --tail 20 \
        --query "[?contains(Log, 'ERROR') || contains(Log, 'CRITICAL') || contains(Log, 'FATAL') || contains(Log, 'Exception')].Log" \
        --output tsv 2>/dev/null)
    
    if [[ -n "$error_logs" ]]; then
        print_error "エラーログが見つかりました:"
        echo "$error_logs"
    else
        print_success "重大なエラーログは見つかりませんでした"
    fi
    
    # リソース使用状況
    print_status "リソース使用状況確認中..."
    az containerapp show \
        --name $APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --query "properties.template.containers[0].resources" \
        --output table 2>/dev/null
    
    print_success "エラー詳細診断完了"
}

# 使用方法表示
show_usage() {
    echo "使用方法: $0 [option]"
    echo ""
    echo "オプション:"
    echo "  quick      - クイックヘルスチェック（デフォルト）"
    echo "  full       - フルヘルスチェック"
    echo "  monitor    - 継続監視モード"
    echo "  diagnose   - エラー詳細診断"
    echo "  help       - このヘルプを表示"
    echo ""
    echo "例:"
    echo "  $0                 # クイックチェック"
    echo "  $0 full           # フルチェック"
    echo "  $0 monitor        # 継続監視"
    echo "  $0 diagnose       # エラー診断"
}

# メイン実行
main() {
    case "${1:-quick}" in
        "quick")
            quick_check
            ;;
        "full")
            full_check
            ;;
        "monitor")
            monitor_check
            ;;
        "diagnose")
            diagnose_errors
            ;;
        "help"|"-h"|"--help")
            show_usage
            ;;
        *)
            echo "不明なオプション: $1"
            show_usage
            exit 1
            ;;
    esac
}

# 前提条件チェック
if ! command -v az &> /dev/null; then
    print_error "Azure CLI がインストールされていません"
    exit 1
fi

if ! az account show &> /dev/null; then
    print_error "Azure にログインしていません"
    exit 1
fi

# スクリプト実行
main "$@"