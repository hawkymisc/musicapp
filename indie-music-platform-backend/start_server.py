#!/usr/bin/env python3
"""
ポート競合解決とサーバー起動スクリプト
"""
import sys
import os
import logging
import subprocess
import signal

# ログ設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def find_port_usage(port):
    """指定ポートを使用しているプロセスを特定"""
    try:
        result = subprocess.run(
            ['lsof', '-i', f':{port}'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0 and result.stdout.strip():
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:  # ヘッダー行を除く
                process_info = lines[1].split()
                if len(process_info) >= 2:
                    command = process_info[0]
                    pid = process_info[1]
                    return {'command': command, 'pid': pid}
        
        return None
        
    except Exception as e:
        logger.error(f"ポート使用状況確認エラー: {e}")
        return None

def kill_port_process(port):
    """指定ポートを使用しているプロセスを終了"""
    process_info = find_port_usage(port)
    
    if not process_info:
        logger.info(f"ポート {port} は使用されていません")
        return True
    
    command = process_info['command']
    pid = process_info['pid']
    
    logger.info(f"ポート {port} を使用中: {command} (PID: {pid})")
    
    # Pythonプロセスの場合は安全に終了を試行
    if 'python' in command.lower():
        try:
            logger.info(f"Pythonプロセス (PID: {pid}) の終了を試行します...")
            
            # まず SIGTERM で優雅な終了を試行
            os.kill(int(pid), signal.SIGTERM)
            
            # 3秒待機して確認
            import time
            time.sleep(3)
            
            # プロセスがまだ存在するか確認
            if find_port_usage(port):
                logger.warning(f"プロセス {pid} がまだ実行中です。強制終了を試行します...")
                os.kill(int(pid), signal.SIGKILL)
                time.sleep(1)
            
            # 最終確認
            if not find_port_usage(port):
                logger.info(f"✓ プロセス {pid} を正常に終了しました")
                return True
            else:
                logger.error(f"✗ プロセス {pid} の終了に失敗しました")
                return False
                
        except ProcessLookupError:
            logger.info("プロセスは既に終了していました")
            return True
        except PermissionError:
            logger.error(f"プロセス {pid} を終了する権限がありません")
            return False
        except Exception as e:
            logger.error(f"プロセス終了エラー: {e}")
            return False
    else:
        logger.warning(f"非Pythonプロセス ({command}) は手動で終了してください")
        return False

def start_server(port=8000):
    """指定ポートでサーバーを起動"""
    logger.info(f"=== ポート {port} でサーバー起動 ===")
    
    project_root = os.path.dirname(os.path.abspath(__file__))
    python_path = os.path.join(project_root, '.venv', 'bin', 'python')
    
    cmd = [
        python_path,
        '-m', 'uvicorn',
        'app.main:app',
        '--host', '127.0.0.1',
        '--port', str(port),
        '--reload'
    ]
    
    logger.info(f"サーバー起動コマンド: {' '.join(cmd)}")
    logger.info("サーバーを起動します...")
    logger.info("終了するには Ctrl+C を押してください")
    
    try:
        # サーバーを起動（フォアグラウンドで実行）
        subprocess.run(cmd, cwd=project_root)
    except KeyboardInterrupt:
        logger.info("\\nサーバーを停止します...")
    except Exception as e:
        logger.error(f"サーバー起動エラー: {e}")
        return False
    
    return True

def main():
    """メイン実行関数"""
    logger.info("=== ポート競合解決とサーバー起動 ===")
    
    # まずポート8000の状況を確認
    logger.info("ポート8000の使用状況を確認します...")
    
    port_8000_info = find_port_usage(8000)
    
    if port_8000_info:
        logger.info(f"ポート8000は {port_8000_info['command']} (PID: {port_8000_info['pid']}) によって使用中です")
        
        # ユーザーに確認
        print("\\n選択してください:")
        print("1. ポート8000を使用中のプロセスを終了してポート8000で起動")
        print("2. ポート8001で起動")
        print("3. 他のポートを指定")
        print("4. 何もせずに終了")
        
        choice = input("\\n選択 (1-4): ").strip()
        
        if choice == "1":
            if kill_port_process(8000):
                return start_server(8000)
            else:
                logger.error("ポート8000のクリアに失敗しました")
                return False
        elif choice == "2":
            return start_server(8001)
        elif choice == "3":
            try:
                custom_port = int(input("使用するポート番号を入力してください: "))
                return start_server(custom_port)
            except ValueError:
                logger.error("無効なポート番号です")
                return False
        else:
            logger.info("操作をキャンセルしました")
            return False
    else:
        logger.info("ポート8000は利用可能です")
        return start_server(8000)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
