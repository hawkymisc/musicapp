#!/usr/bin/env python3
"""
詳細なサーバー起動前チェック
"""
import sys
import os
import logging

# ログ設定
logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_environment():
    """環境チェック"""
    logger.info("=== 環境チェック ===")
    logger.info(f"Python バージョン: {sys.version}")
    logger.info(f"プラットフォーム: {sys.platform}")
    logger.info(f"作業ディレクトリ: {os.getcwd()}")
    logger.info(f"sys.path: {sys.path[:3]}...")  # 最初の3つだけ表示

def check_imports():
    """必要なモジュールのインポートチェック"""
    logger.info("=== モジュールインポートチェック ===")
    
    modules_to_check = [
        'fastapi',
        'uvicorn', 
        'sqlalchemy',
        'pydantic',
        'starlette'
    ]
    
    for module_name in modules_to_check:
        try:
            module = __import__(module_name)
            version = getattr(module, '__version__', 'バージョン不明')
            logger.info(f"✓ {module_name} {version}")
        except ImportError as e:
            logger.error(f"✗ {module_name}: {e}")
            return False
    
    return True

def check_app_modules():
    """アプリケーションモジュールのチェック"""
    logger.info("=== アプリケーションモジュールチェック ===")
    
    # プロジェクトルートをsys.pathに追加
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
        logger.info(f"プロジェクトルートを追加: {project_root}")
    
    app_modules = [
        ('app.core.config', '設定'),
        ('app.db.session', 'データベースセッション'),
        ('app.api.router', 'APIルーター'),
        ('app.main', 'メインアプリケーション')
    ]
    
    for module_name, description in app_modules:
        try:
            __import__(module_name)
            logger.info(f"✓ {description} ({module_name})")
        except ImportError as e:
            logger.error(f"✗ {description} ({module_name}): {e}")
            return False
        except Exception as e:
            logger.error(f"✗ {description} ({module_name}) - その他のエラー: {e}")
            return False
    
    return True

def check_fastapi_app():
    """FastAPIアプリケーションオブジェクトのチェック"""
    logger.info("=== FastAPIアプリケーションチェック ===")
    
    try:
        from app.main import app
        logger.info(f"✓ アプリケーションオブジェクト取得成功: {type(app)}")
        
        # アプリケーションの基本情報
        logger.info(f"アプリケーション名: {app.title}")
        logger.info(f"バージョン: {app.version}")
        logger.info(f"ルート数: {len(app.routes)}")
        
        return app
    except Exception as e:
        logger.error(f"✗ アプリケーションオブジェクト取得失敗: {e}")
        return None

def check_uvicorn_config():
    """Uvicorn設定のチェック"""
    logger.info("=== Uvicorn設定チェック ===")
    
    try:
        import uvicorn
        from app.main import app
        
        # 基本設定
        config = uvicorn.Config(
            app=app,
            host="127.0.0.1",
            port=8000,
            reload=False,
            log_level="info"
        )
        
        logger.info("✓ Uvicorn設定作成成功")
        logger.info(f"ホスト: {config.host}")
        logger.info(f"ポート: {config.port}")
        logger.info(f"リロード: {config.reload}")
        
        # サーバーオブジェクト作成テスト
        server = uvicorn.Server(config)
        logger.info("✓ Uvicornサーバーオブジェクト作成成功")
        
        return True
    except Exception as e:
        logger.error(f"✗ Uvicorn設定エラー: {e}")
        return False

def check_port_availability():
    """ポート8000の使用状況チェック"""
    logger.info("=== ポート使用状況チェック ===")
    
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', 8000))
            logger.info("✓ ポート8000は使用可能です")
            return True
    except OSError as e:
        logger.warning(f"ポート8000は使用中またはアクセス不可: {e}")
        return False

def main():
    """メイン実行関数"""
    logger.info("=== サーバー起動前チェック開始 ===")
    
    checks = [
        ("環境チェック", check_environment),
        ("モジュールインポート", check_imports),
        ("アプリケーションモジュール", check_app_modules),
        ("FastAPIアプリケーション", check_fastapi_app),
        ("Uvicorn設定", check_uvicorn_config),
        ("ポート使用状況", check_port_availability),
    ]
    
    results = {}
    for check_name, check_func in checks:
        logger.info(f"\n--- {check_name} ---")
        try:
            if check_name == "環境チェック":
                check_func()
                results[check_name] = True
            else:
                result = check_func()
                results[check_name] = bool(result)
        except Exception as e:
            logger.error(f"{check_name}中にエラー: {e}")
            results[check_name] = False
    
    logger.info("\n=== チェック結果サマリー ===")
    all_passed = True
    for check_name, result in results.items():
        status = "✓ 成功" if result else "✗ 失敗"
        logger.info(f"{check_name}: {status}")
        if not result:
            all_passed = False
    
    if all_passed:
        logger.info("\n✓ 全チェック通過: サーバー起動準備完了")
        logger.info("手動でサーバーを起動してください:")
        logger.info("  ./.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000")
    else:
        logger.info("\n✗ 一部チェック失敗: 問題を解決してから再実行してください")
    
    return all_passed

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
