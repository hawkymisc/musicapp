from fastapi import APIRouter
from app.api.v1 import auth, tracks, stream, purchases, users, artists

api_router = APIRouter()

# 各エンドポイントルーターをAPI v1にマウント
api_router.include_router(auth.router, prefix="/v1/auth", tags=["認証"])
api_router.include_router(tracks.router, prefix="/v1/tracks", tags=["楽曲"])
api_router.include_router(stream.router, prefix="/v1/stream", tags=["ストリーミング"])
api_router.include_router(purchases.router, prefix="/v1/purchases", tags=["購入"])
api_router.include_router(users.router, prefix="/v1/users", tags=["ユーザー"])
api_router.include_router(artists.router, prefix="/v1/artists", tags=["アーティスト"])
