#!/bin/bash

# インディーズミュージックプラットフォーム トラブルシューティングスクリプト
# 使用方法: ./deploy/troubleshoot.sh [option]
# オプション: logs | restart | rebuild | deps | network | all

set -e

# 設定
RESOURCE_GROUP="indie-music-rg"
APP_NAME="indie-music-api"
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

# ログ詳細分析
analyze_logs() {
    print_status "ログ詳細分析開始..."
    
    # 全ログ取得
    print_status "全ログ取得中..."
    az containerapp logs show \
        --name $APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --tail 50 > /tmp/app_logs.txt 2>/dev/null
    
    if [[ -f /tmp/app_logs.txt ]]; then
        print_success "ログファイル作成: /tmp/app_logs.txt"
        
        # エラーパターン検索
        print_status "エラーパターン分析中..."
        local error_patterns=(
            "ModuleNotFoundError"
            "ImportError"
            "ConnectionError"
            "TimeoutError"
            "HTTP 500"
            "HTTP 502"
            "HTTP 503"
            "CRITICAL"
            "FATAL"
            "Exception"
        )
        
        for pattern in "${error_patterns[@]}"; do
            local count=$(grep -c "$pattern" /tmp/app_logs.txt 2>/dev/null || echo "0")
            if [[ $count -gt 0 ]]; then
                print_warning "$pattern: $count 件検出"
                grep "$pattern" /tmp/app_logs.txt | head -3
            fi
        done
        
        # 起動パターン検索
        print_status "起動パターン分析中..."
        local startup_patterns=(
            "Started server process"
            "Uvicorn running"
            "Application startup complete"
            "Listening on"
        )
        
        for pattern in "${startup_patterns[@]}"; do
            if grep -q "$pattern" /tmp/app_logs.txt 2>/dev/null; then
                print_success "起動パターン '$pattern' 検出"
            fi
        done
        
    else
        print_error "ログ取得に失敗しました"
    fi
    
    print_success "ログ詳細分析完了"
}

# アプリケーション再起動
restart_app() {
    print_status "アプリケーション再起動開始..."
    
    # 現在のリビジョン取得
    local current_revision=$(az containerapp revision list \
        --name $APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --query "[?properties.active && properties.trafficWeight > 0].name" \
        --output tsv 2>/dev/null | head -1)
    
    if [[ -n "$current_revision" ]]; then
        print_status "現在のリビジョン: $current_revision"
        
        # リビジョン再起動
        print_status "リビジョン再起動中..."
        az containerapp revision restart \
            --name $APP_NAME \
            --resource-group $RESOURCE_GROUP \
            --revision $current_revision 2>/dev/null || {
                print_warning "リビジョン再起動コマンドが利用できません。Container App更新で代替..."
                az containerapp update \
                    --name $APP_NAME \
                    --resource-group $RESOURCE_GROUP > /dev/null 2>&1
            }
        
        print_success "再起動完了"
        
        # 再起動後の状態確認
        print_status "再起動後の状態確認中..."
        sleep 30
        ./deploy/health-check.sh quick
        
    else
        print_error "アクティブなリビジョンが見つかりません"
    fi
}

# イメージ再ビルドとデプロイ
rebuild_and_deploy() {
    print_status "イメージ再ビルドとデプロイ開始..."
    
    # 依存関係確認
    print_status "requirements.txt の確認..."
    if [[ ! -f "requirements.txt" ]]; then
        print_error "requirements.txt が見つかりません"
        return 1
    fi
    
    local missing_deps=()
    
    # 重要な依存関係チェック
    local required_deps=(
        "fastapi"
        "uvicorn"
        "slowapi"
        "sqlalchemy"
        "psycopg2-binary"
    )
    
    for dep in "${required_deps[@]}"; do
        if ! grep -q "^$dep" requirements.txt; then
            missing_deps+=("$dep")
        fi
    done
    
    if [[ ${#missing_deps[@]} -gt 0 ]]; then
        print_error "不足している依存関係: ${missing_deps[*]}"
        print_status "requirements.txt に追加してください"
        return 1
    fi
    
    print_success "依存関係チェック完了"
    
    # Container Registry ログイン
    print_status "Container Registry ログイン中..."
    az acr login --name $CONTAINER_REGISTRY > /dev/null 2>&1
    
    # イメージビルド
    print_status "Docker イメージ再ビルド中..."
    az acr build \
        --registry $CONTAINER_REGISTRY \
        --image indie-music-api:latest \
        --file Dockerfile \
        . > /dev/null 2>&1
    
    print_success "イメージ再ビルド完了"
    
    # アプリケーション更新
    print_status "アプリケーション更新中..."
    az containerapp update \
        --name $APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --image ${CONTAINER_REGISTRY}.azurecr.io/indie-music-api:latest > /dev/null 2>&1
    
    print_success "アプリケーション更新完了"
    
    # リビジョン管理
    print_status "リビジョン管理実行中..."
    ./deploy/azure-deploy.sh check > /dev/null 2>&1 || print_warning "デプロイ後チェックでエラーが発生しました"
    
    print_success "再ビルドとデプロイ完了"
}

# 依存関係トラブルシューティング
check_dependencies() {
    print_status "依存関係トラブルシューティング開始..."
    
    # requirements.txt 詳細チェック
    print_status "requirements.txt 詳細分析..."
    if [[ -f "requirements.txt" ]]; then
        local total_deps=$(grep -c "^[^#]" requirements.txt 2>/dev/null || echo "0")
        print_status "依存関係数: $total_deps"
        
        # 重複チェック
        local duplicates=$(grep "^[^#]" requirements.txt | cut -d'=' -f1 | sort | uniq -d)
        if [[ -n "$duplicates" ]]; then
            print_warning "重複している依存関係:"
            echo "$duplicates"
        else
            print_success "重複なし"
        fi
        
        # バージョン固定チェック
        local unversioned=$(grep "^[^#]" requirements.txt | grep -v "==")
        if [[ -n "$unversioned" ]]; then
            print_warning "バージョン固定されていない依存関係:"
            echo "$unversioned"
        else
            print_success "全ての依存関係でバージョン固定済み"
        fi
        
    else
        print_error "requirements.txt が見つかりません"
    fi
    
    # Python バージョン確認
    print_status "Dockerfile Python バージョン確認..."
    if [[ -f "Dockerfile" ]]; then
        local python_version=$(grep "FROM python:" Dockerfile | head -1)
        print_status "使用中の Python: $python_version"
    else
        print_warning "Dockerfile が見つかりません"
    fi
    
    # 推奨修正の提案
    print_status "推奨修正事項:"
    echo "1. slowapi==0.1.9 が requirements.txt に含まれていることを確認"
    echo "2. 全ての依存関係でバージョンを固定"
    echo "3. Python 3.10-slim イメージの使用"
    echo "4. 不要な依存関係の削除"
    
    print_success "依存関係チェック完了"
}

# ネットワーク診断
network_diagnosis() {
    print_status "ネットワーク診断開始..."
    
    # アプリケーションURL取得
    local app_url=$(az containerapp show \
        --name $APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --query properties.configuration.ingress.fqdn \
        --output tsv 2>/dev/null)
    
    if [[ -z "$app_url" ]]; then
        print_error "アプリケーションURLを取得できませんでした"
        return 1
    fi
    
    app_url="https://$app_url"
    print_status "診断対象URL: $app_url"
    
    # DNS解決チェック
    print_status "DNS解決チェック..."
    if nslookup "$(echo $app_url | sed 's|https://||')" > /dev/null 2>&1; then
        print_success "DNS解決成功"
    else
        print_error "DNS解決失敗"
    fi
    
    # SSL/TLS チェック
    print_status "SSL/TLS チェック..."
    if curl -s --max-time 10 "$app_url" > /dev/null 2>&1; then
        print_success "SSL/TLS接続成功"
    else
        print_warning "SSL/TLS接続に問題があります"
    fi
    
    # ポート確認
    print_status "ポート設定確認..."
    local target_port=$(az containerapp show \
        --name $APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --query properties.configuration.ingress.targetPort \
        --output tsv 2>/dev/null)
    print_status "設定されているターゲットポート: $target_port"
    
    # 外部アクセス設定確認
    local external=$(az containerapp show \
        --name $APP_NAME \
        --resource-group $RESOURCE_GROUP \
        --query properties.configuration.ingress.external \
        --output tsv 2>/dev/null)
    print_status "外部アクセス設定: $external"
    
    print_success "ネットワーク診断完了"
}

# 全体トラブルシューティング
comprehensive_troubleshoot() {
    print_status "全体トラブルシューティング開始..."
    
    echo "======================"
    echo "1. ログ分析"
    echo "======================"
    analyze_logs
    
    echo ""
    echo "======================"
    echo "2. 依存関係チェック"
    echo "======================"
    check_dependencies
    
    echo ""
    echo "======================"
    echo "3. ネットワーク診断"
    echo "======================"
    network_diagnosis
    
    echo ""
    echo "======================"
    echo "4. 状態確認"
    echo "======================"
    ./deploy/health-check.sh full
    
    print_success "全体トラブルシューティング完了"
}

# 使用方法表示
show_usage() {
    echo "使用方法: $0 [option]"
    echo ""
    echo "オプション:"
    echo "  logs       - ログ詳細分析"
    echo "  restart    - アプリケーション再起動"
    echo "  rebuild    - イメージ再ビルドとデプロイ"
    echo "  deps       - 依存関係チェック"
    echo "  network    - ネットワーク診断"
    echo "  all        - 全体トラブルシューティング（デフォルト）"
    echo "  help       - このヘルプを表示"
    echo ""
    echo "例:"
    echo "  $0 logs       # ログ分析のみ"
    echo "  $0 restart    # アプリ再起動"
    echo "  $0 rebuild    # 完全再ビルド"
}

# メイン実行
main() {
    case "${1:-all}" in
        "logs")
            analyze_logs
            ;;
        "restart")
            restart_app
            ;;
        "rebuild")
            rebuild_and_deploy
            ;;
        "deps")
            check_dependencies
            ;;
        "network")
            network_diagnosis
            ;;
        "all")
            comprehensive_troubleshoot
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