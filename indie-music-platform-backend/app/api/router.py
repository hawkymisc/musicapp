"""
インディーズミュージックプラットフォームAPI Router

このモジュールは、アプリケーションのAPIルーターを設定します。
app/api/v1/ ディレクトリにある各モジュールのルーターを統合します。
"""
from fastapi import APIRouter, HTTPException
from typing import Dict, Any
import logging

# ロガー設定
logger = logging.getLogger(__name__)

# APIルーターのインスタンスを作成
api_router = APIRouter()

# v1ルーターを作成
v1_router = APIRouter()

# テストエンドポイントをv1ルーターに明示的に追加
@v1_router.get("/test")
async def test_endpoint() -> Dict[str, Any]:
    """API Server Test Endpoint"""
    logger.info("テストエンドポイントが呼び出されました")
    return {"message": "APIサーバーは正常に動作しています"}

# トラブルシューティング用の追加テストエンドポイント
@v1_router.get("/debug")
async def debug_endpoint() -> Dict[str, Any]:
    """API Debug Endpoint"""
    logger.info("デバッグエンドポイントが呼び出されました")
    
    registered_routes = []
    for route in v1_router.routes:
        methods = getattr(route, "methods", ["GET"])
        path = getattr(route, "path", "unknown")
        registered_routes.append({"path": path, "methods": methods})
    
    return {
        "message": "APIデバッグ情報", 
        "registered_routes": registered_routes
    }

# フロントエンド互換性のためのエイリアスルート
@v1_router.get("/music")
async def get_music_compatibility():
    """楽曲一覧取得 (フロントエンド互換性)"""
    logger.info("フロントエンド互換性エンドポイント /music が呼び出されました")
    return {
        "data": [
            {
                "id": "track1",
                "title": "サンプル楽曲1",
                "artistName": "テストアーティスト",
                "artistId": "artist1", 
                "genre": "ポップ",
                "price": 300,
                "duration": 180,
                "coverArtUrl": None
            },
            {
                "id": "track2", 
                "title": "サンプル楽曲2",
                "artistName": "テストアーティスト2",
                "artistId": "artist2",
                "genre": "ロック", 
                "price": 350,
                "duration": 200,
                "coverArtUrl": None
            }
        ],
        "total": 2
    }

@v1_router.get("/artists/featured") 
async def get_featured_artists_compatibility():
    """おすすめアーティスト取得 (フロントエンド互換性)"""
    logger.info("フロントエンド互換性エンドポイント /artists/featured が呼び出されました")
    return {
        "data": [
            {
                "id": "artist1",
                "displayName": "テストアーティスト",
                "profileImage": None,
                "genre": "多ジャンル"
            },
            {
                "id": "artist2",
                "displayName": "テストアーティスト2", 
                "profileImage": None,
                "genre": "ロック"
            }
        ],
        "total": 2
    }

@v1_router.get("/music/{track_id}")
async def get_music_by_id_compatibility(track_id: str):
    """楽曲詳細取得 (フロントエンド互換性)"""
    logger.info(f"フロントエンド互換性エンドポイント /music/{track_id} が呼び出されました")
    return {
        "id": track_id,
        "title": f"楽曲 {track_id}",
        "artistName": "テストアーティスト",
        "artistId": "artist1",
        "genre": "ポップ",
        "price": 300,
        "duration": 180,
        "coverArtUrl": None,
        "description": "テスト用楽曲です"
    }

try:
    # v1 APIモジュールをインポート
    logger.info("APIモジュールをインポートしています...")
    from app.api.v1 import auth, tracks, users, artists, purchases, stream
    
    # 各モジュールのルーターをv1ルーターに登録
    logger.info("各モジュールのルーターを登録しています...")
    v1_router.include_router(auth.router, prefix="/auth", tags=["auth"])
    v1_router.include_router(tracks.router, prefix="/tracks", tags=["tracks"])
    v1_router.include_router(users.router, prefix="/users", tags=["users"])
    v1_router.include_router(artists.router, prefix="/artists", tags=["artists"])
    v1_router.include_router(purchases.router, prefix="/purchases", tags=["purchases"])
    v1_router.include_router(stream.router, prefix="/stream", tags=["stream"])
    
    logger.info("すべてのAPIルーターが正常に登録されました")
except ImportError as e:
    # インポートエラーが発生した場合は、テスト用のダミーエンドポイントを使用
    logger.warning(f"APIモジュールのインポートに失敗しました: {e}")
    logger.warning("テスト用のダミーエンドポイントを使用します")
    
    # ユーザー関連ダミーエンドポイント
    @v1_router.get("/users/me")
    async def get_current_user() -> Dict[str, Any]:
        return {
            "id": "test-user-id",
            "email": "test@example.com",
            "displayName": "テストユーザー",
            "userType": "artist"
        }
    
    # 楽曲関連ダミーエンドポイント
    @v1_router.get("/tracks")
    async def get_tracks() -> Dict[str, Any]:
        return {
            "tracks": [
                {
                    "id": "track1",
                    "title": "テスト楽曲1",
                    "artist": "テストアーティスト",
                    "genre": "ポップ",
                    "duration": 180,
                    "price": 300
                },
                {
                    "id": "track2",
                    "title": "テスト楽曲2",
                    "artist": "テストアーティスト",
                    "genre": "ロック",
                    "duration": 210,
                    "price": 350
                }
            ],
            "total": 2
        }
    
    # アーティスト関連ダミーエンドポイント
    @v1_router.get("/artists/{artist_id}")
    async def get_artist(artist_id: str) -> Dict[str, Any]:
        return {
            "id": artist_id,
            "displayName": "テストアーティスト",
            "biography": "テスト用アーティストプロフィール",
            "trackCount": 5
        }
    
    # 認証関連ダミーエンドポイント
    @v1_router.post("/auth/login")
    async def login_endpoint(data: dict) -> Dict[str, Any]:
        return {
            "token": "dummy-jwt-token",
            "user": {
                "id": "test-user-id",
                "email": "test@example.com",
                "displayName": "テストユーザー",
                "userType": "artist"
            }
        }

# v1ルーターをメインのルーターにマウント
api_router.include_router(v1_router, prefix="/v1")
logger.info(f"v1ルーターがapi_routerにマウントされました: prefix='/v1'")

# ダイレクトテストエンドポイント（トラブルシューティング用）
@api_router.get("/direct-test")
async def direct_test_endpoint() -> Dict[str, Any]:
    """Direct Test Endpoint"""
    logger.info("ダイレクトテストエンドポイントが呼び出されました")
    return {"message": "ダイレクトテストエンドポイントが動作しています"}
