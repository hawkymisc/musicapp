#!/usr/bin/env python3
"""
異なるポートでのサーバー起動テスト
"""
import sys
import os
import logging
import subprocess

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_port_usage():
    """現在のポート使用状況を確認"""
    logger.info("=== ポート使用状況確認 ===")
    
    ports_to_check = [8000, 8001, 8002]
    
    for port in ports_to_check:
        try:
            result = subprocess.run(
                ['lsof', '-i', f':{port}'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0 and result.stdout.strip():
                logger.warning(f"ポート {port} は使用中:")
                logger.warning(result.stdout)
            else:
                logger.info(f"ポート {port} は利用可能")
                
        except subprocess.TimeoutExpired:
            logger.warning(f"ポート {port} のチェックがタイムアウト")
        except FileNotFoundError:
            logger.info("lsof コマンドが見つかりません（ポートチェックをスキップ）")
            break
        except Exception as e:
            logger.error(f"ポート {port} チェック中にエラー: {e}")

def try_simple_server_start():
    """シンプルなサーバー起動を試行"""
    logger.info("=== シンプルなサーバー起動テスト ===")
    
    # プロジェクトルートをsys.pathに追加
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    try:
        # Python実行可能ファイルのパス
        python_path = os.path.join(project_root, '.venv', 'bin', 'python')
        
        if not os.path.exists(python_path):
            logger.error(f"Python実行ファイルが見つかりません: {python_path}")
            return False
        
        logger.info(f"Python実行ファイル確認: {python_path}")
        
        # 異なるポートでサーバー起動を試行
        ports_to_try = [8001, 8002, 8003]
        
        for port in ports_to_try:
            logger.info(f"ポート {port} でサーバー起動を試行します...")
            
            try:
                # 短時間でのテスト起動
                cmd = [
                    python_path,
                    '-m', 'uvicorn',
                    'app.main:app',
                    '--host', '127.0.0.1',
                    '--port', str(port),
                    '--log-level', 'info'
                ]
                
                logger.info(f"実行コマンド: {' '.join(cmd)}")
                
                # 3秒間だけ起動を試行
                process = subprocess.Popen(
                    cmd,
                    cwd=project_root,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )
                
                # 3秒待機
                try:
                    stdout, stderr = process.communicate(timeout=3)
                    logger.info(f"プロセス終了コード: {process.returncode}")
                    if stdout:
                        logger.info(f"標準出力: {stdout}")
                    if stderr:
                        logger.error(f"標準エラー: {stderr}")
                        
                except subprocess.TimeoutExpired:
                    logger.info("3秒後にプロセスを終了します...")
                    process.terminate()
                    try:
                        stdout, stderr = process.communicate(timeout=2)
                        logger.info("✓ サーバーが正常に起動し、終了しました")
                        
                        if stdout:
                            logger.info(f"出力: {stdout}")
                        if stderr and "Shutting down" not in stderr:
                            logger.warning(f"警告: {stderr}")
                            
                        return True
                        
                    except subprocess.TimeoutExpired:
                        logger.warning("プロセスの強制終了を実行します...")
                        process.kill()
                        process.communicate()
                
            except Exception as e:
                logger.error(f"ポート {port} での起動エラー: {e}")
                continue
        
        logger.error("すべてのポートでの起動に失敗しました")
        return False
        
    except Exception as e:
        logger.error(f"サーバー起動テストエラー: {e}", exc_info=True)
        return False

def main():
    """メイン実行関数"""
    logger.info("=== 異なるポートでのサーバー起動テスト開始 ===")
    
    # ポート使用状況確認
    check_port_usage()
    
    # サーバー起動テスト
    success = try_simple_server_start()
    
    if success:
        logger.info("✓ サーバー起動テスト成功")
        logger.info("推奨: 利用可能なポートでフロントエンドとの接続テストを実行してください")
    else:
        logger.error("✗ サーバー起動テスト失敗")
        logger.error("追加の調査が必要です")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
