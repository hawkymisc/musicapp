#!/usr/bin/env python3
"""
簡単なライブラリチェックとサーバー起動テスト
"""
import sys
import os

def check_libraries():
    """必要なライブラリのチェック"""
    print("=== ライブラリチェック ===")
    
    libraries = [
        'subprocess',
        'time',
        'logging',
        'requests'
    ]
    
    for lib in libraries:
        try:
            __import__(lib)
            print(f"✓ {lib}")
        except ImportError:
            print(f"✗ {lib} - インストールが必要")
            return False
    
    return True

def check_environment():
    """環境チェック"""
    print("=== 環境チェック ===")
    
    # 作業ディレクトリ
    current_dir = os.getcwd()
    print(f"作業ディレクトリ: {current_dir}")
    
    # Python実行パス
    backend_dir = os.path.dirname(os.path.abspath(__file__))
    python_path = os.path.join(backend_dir, '.venv', 'bin', 'python')
    
    if os.path.exists(python_path):
        print(f"✓ Python実行ファイル: {python_path}")
    else:
        print(f"✗ Python実行ファイルが見つかりません: {python_path}")
        return False
    
    # アプリケーションファイル
    app_main = os.path.join(backend_dir, 'app', 'main.py')
    if os.path.exists(app_main):
        print(f"✓ アプリケーションファイル: {app_main}")
    else:
        print(f"✗ アプリケーションファイルが見つかりません: {app_main}")
        return False
    
    return True

def test_simple_import():
    """シンプルなアプリケーションインポートテスト"""
    print("=== アプリケーションインポートテスト ===")
    
    try:
        # sys.pathにプロジェクトルートを追加
        project_root = os.path.dirname(os.path.abspath(__file__))
        if project_root not in sys.path:
            sys.path.insert(0, project_root)
        
        from app.main import app
        print("✓ アプリケーションインポート成功")
        print(f"アプリケーション名: {app.title}")
        return True
        
    except Exception as e:
        print(f"✗ アプリケーションインポート失敗: {e}")
        return False

def main():
    """メイン実行関数"""
    print("=== 事前チェック開始 ===")
    
    checks = [
        ("ライブラリ", check_libraries),
        ("環境", check_environment),
        ("アプリケーションインポート", test_simple_import),
    ]
    
    for check_name, check_func in checks:
        print(f"\n--- {check_name}チェック ---")
        try:
            result = check_func()
            if result:
                print(f"✓ {check_name}チェック成功")
            else:
                print(f"✗ {check_name}チェック失敗")
                return False
        except Exception as e:
            print(f"✗ {check_name}チェック中にエラー: {e}")
            return False
    
    print("\n" + "="*50)
    print("🎉 すべての事前チェックが成功しました！")
    print("サーバー起動の準備が整っています")
    print("="*50)
    return True

if __name__ == "__main__":
    success = main()
    if success:
        print("\n次のステップ: サーバーを手動で起動してください")
        print("コマンド: ./.venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8001")
    else:
        print("\n問題を解決してから再実行してください")
    
    sys.exit(0 if success else 1)
