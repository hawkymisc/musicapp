"""
改善版Firebase初期化モジュール

このモジュールは、app/core/security.pyのFirebase初期化部分を改善し、
より堅牢なエラーハンドリングと初期化管理を提供します。
"""
import os
import logging
import json
from typing import Optional, Dict, Any

# モジュールレベルのロガー
logger = logging.getLogger(__name__)

# Firebaseアプリインスタンス
firebase_app = None

def init_firebase() -> Optional[object]:
    """
    Firebase認証を初期化する
    
    Returns:
        Optional[object]: 初期化されたFirebaseアプリインスタンス、またはNone
    """
    global firebase_app
    
    # 既に初期化済みの場合は何もしない
    if firebase_app is not None:
        return firebase_app
    
    # テスト環境ではモックを使用
    if os.environ.get('TESTING') == 'True':
        logger.info("テストモードのため、Firebase初期化をスキップします")
        return None
    
    try:
        # Firebase Admin SDKのインポート（必要な場合のみ）
        import firebase_admin
        from firebase_admin import credentials
        
        # 認証情報ファイルのパスを取得
        cred_path = os.environ.get("FIREBASE_CREDENTIALS_PATH")
        if not cred_path:
            logger.warning("FIREBASE_CREDENTIALS_PATH環境変数が設定されていません")
            return None
        
        if not os.path.exists(cred_path):
            logger.warning(f"Firebase認証情報ファイルが見つかりません: {cred_path}")
            
            # 開発環境では、テスト用のダミー認証情報を作成
            if os.environ.get('DEVELOPMENT') == 'True':
                logger.info("開発モードのため、ダミー認証情報を作成します")
                dummy_cred_path = os.path.join(os.getcwd(), 'firebase-credentials-dev.json')
                
                # ダミー認証情報を作成
                dummy_cred = {
                    "type": "service_account",
                    "project_id": "dummy-project",
                    "private_key_id": "dummy-key-id",
                    "private_key": "dummy-private-key",
                    "client_email": "dummy@example.com",
                    "client_id": "dummy-client-id",
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/dummy%40example.com"
                }
                
                # ダミー認証情報をファイルに保存
                with open(dummy_cred_path, 'w') as f:
                    json.dump(dummy_cred, f)
                
                cred_path = dummy_cred_path
            else:
                return None
        
        # 認証情報ファイルを読み込み
        logger.info(f"Firebaseを初期化します: {cred_path}")
        cred = credentials.Certificate(cred_path)
        
        # Firebase初期化
        firebase_app = firebase_admin.initialize_app(cred)
        logger.info("Firebase初期化が完了しました")
        return firebase_app
        
    except ImportError as e:
        logger.warning(f"Firebase Admin SDKがインストールされていません: {e}")
        return None
    except Exception as e:
        logger.error(f"Firebase初期化エラー: {e}")
        return None

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    Firebaseトークンを検証する
    
    Args:
        token (str): 検証するトークン
    
    Returns:
        Optional[Dict[str, Any]]: デコードされたトークン情報またはNone
    """
    # Firebase初期化
    if not init_firebase() and os.environ.get('TESTING') != 'True':
        logger.error("Firebaseが初期化されていないためトークン検証ができません")
        return None
    
    try:
        # テストモードの場合
        if os.environ.get('TESTING') == 'True':
            # テスト用トークン処理
            if token == "artist_token":
                return {"uid": "firebaseuid_artist"}
            elif token == "listener_token":
                return {"uid": "firebaseuid_listener"}
            else:
                return None
        else:
            # Firebase認証モジュールをインポート
            from firebase_admin import auth
            
            # トークン検証
            decoded_token = auth.verify_id_token(token)
            return decoded_token
    except Exception as e:
        logger.error(f"トークン検証エラー: {e}")
        return None
