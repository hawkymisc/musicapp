#!/usr/bin/env python3
"""
サーバー起動問題のデバッグスクリプト
段階的にモジュールをインポートして問題箇所を特定する
"""
import sys
import os
import logging

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_basic_imports():
    """基本的なモジュールのインポートテスト"""
    logger.info("=== 基本モジュールのインポートテスト ===")
    
    try:
        import fastapi
        logger.info(f"✓ FastAPI バージョン: {fastapi.__version__}")
    except Exception as e:
        logger.error(f"✗ FastAPI インポートエラー: {e}")
        return False
    
    try:
        import uvicorn
        logger.info(f"✓ Uvicorn バージョン: {uvicorn.__version__}")
    except Exception as e:
        logger.error(f"✗ Uvicorn インポートエラー: {e}")
        return False
    
    try:
        import sqlalchemy
        logger.info(f"✓ SQLAlchemy バージョン: {sqlalchemy.__version__}")
    except Exception as e:
        logger.error(f"✗ SQLAlchemy インポートエラー: {e}")
        return False
    
    return True

def test_app_imports():
    """アプリケーションモジュールのインポートテスト"""
    logger.info("=== アプリケーションモジュールのインポートテスト ===")
    
    # sys.pathの確認
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
        logger.info(f"プロジェクトルートをsys.pathに追加: {project_root}")
    
    try:
        from app.core.config import settings
        logger.info("✓ 設定モジュール: インポート成功")
    except Exception as e:
        logger.error(f"✗ 設定モジュール インポートエラー: {e}")
        return False
    
    try:
        from app.db.session import create_tables
        logger.info("✓ データベースセッション: インポート成功")
    except Exception as e:
        logger.error(f"✗ データベースセッション インポートエラー: {e}")
        return False
    
    try:
        from app.api.router import api_router
        logger.info("✓ APIルーター: インポート成功")
    except Exception as e:
        logger.error(f"✗ APIルーター インポートエラー: {e}")
        return False
    
    return True

def test_simple_fastapi():
    """シンプルなFastAPIアプリケーションのテスト"""
    logger.info("=== シンプルなFastAPIアプリケーションテスト ===")
    
    try:
        from fastapi import FastAPI
        
        # シンプルなアプリケーション作成
        simple_app = FastAPI(title="Test App")
        
        @simple_app.get("/")
        async def root():
            return {"message": "Hello World"}
        
        logger.info("✓ シンプルなFastAPIアプリケーション作成成功")
        return True
        
    except Exception as e:
        logger.error(f"✗ シンプルなFastAPIアプリケーション作成エラー: {e}")
        return False

def test_main_app():
    """メインアプリケーションのインポートテスト"""
    logger.info("=== メインアプリケーションのインポートテスト ===")
    
    try:
        from app.main import app
        logger.info("✓ メインアプリケーション: インポート成功")
        return True
    except Exception as e:
        logger.error(f"✗ メインアプリケーション インポートエラー: {e}")
        return False

def main():
    """メイン実行関数"""
    logger.info("=== サーバー起動問題デバッグ開始 ===")
    logger.info(f"Python バージョン: {sys.version}")
    logger.info(f"作業ディレクトリ: {os.getcwd()}")
    
    # 段階的なテスト実行
    tests = [
        ("基本モジュール", test_basic_imports),
        ("アプリケーションモジュール", test_app_imports),
        ("シンプルなFastAPI", test_simple_fastapi),
        ("メインアプリケーション", test_main_app),
    ]
    
    for test_name, test_func in tests:
        logger.info(f"\n--- {test_name}のテスト ---")
        try:
            success = test_func()
            if not success:
                logger.error(f"{test_name}のテストで問題が発見されました。")
                return False
        except Exception as e:
            logger.error(f"{test_name}のテスト中に予期しないエラー: {e}", exc_info=True)
            return False
    
    logger.info("\n=== すべてのテストが完了しました ===")
    return True

if __name__ == "__main__":
    success = main()
    if success:
        logger.info("デバッグ完了: 問題は見つかりませんでした")
    else:
        logger.error("デバッグ完了: 問題が発見されました")
        sys.exit(1)
