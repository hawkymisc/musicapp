from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from starlette.staticfiles import StaticFiles
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
import time
import logging
from typing import Callable
import uvicorn
import os

from app.api.router import api_router
from app.core.config import settings
from app.db.session import create_tables

# 構造化ログを初期化
from app.core.logging import (
    setup_logging, set_request_context, clear_request_context, 
    generate_request_id, performance_logger, security_logger, application_logger
)

# ログシステムを初期化
setup_logging()
logger = logging.getLogger(__name__)

# レート制限の設定
def get_client_id(request: Request):
    """クライアント識別子を取得（IP + User-Agent）"""
    # 認証されたユーザーがいればuser_idを使用、なければIPアドレス
    client_ip = get_remote_address(request)
    user_agent = request.headers.get("user-agent", "unknown")
    
    # テスト環境では制限を緩和
    if os.environ.get('TESTING') == 'True':
        return f"test_{client_ip}_{hash(user_agent) % 1000}"
    
    return f"{client_ip}_{hash(user_agent) % 10000}"

# レート制限設定
limiter = Limiter(
    key_func=get_client_id,
    default_limits=["1000/hour", "100/minute"]  # デフォルト制限
)

# FastAPIインスタンスの作成
app = FastAPI(
    title="インディーズミュージックアプリAPI",
    description="インディーズミュージシャンが楽曲を販売・配信するためのAPI",
    version="0.1.0"
)

# レート制限ミドルウェアを追加
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ミドルウェア設定
# リクエスト処理時間のロギングと構造化ログ統合
@app.middleware("http")
async def add_process_time_header(request: Request, call_next: Callable):
    # リクエストIDを生成してコンテキストに設定
    request_id = generate_request_id()
    set_request_context(request_id)
    
    start_time = time.time()
    
    try:
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers["X-Process-Time"] = str(process_time)
        response.headers["X-Request-ID"] = request_id
        
        # パフォーマンスログ記録
        performance_logger.log_request_timing(
            endpoint=str(request.url.path),
            method=request.method,
            duration=process_time,
            status_code=response.status_code
        )
        
        return response
    
    except Exception as e:
        process_time = time.time() - start_time
        
        # エラーログを構造化形式で記録
        logger.error(
            f"Request failed: {request.method} {request.url.path}",
            extra={
                "method": request.method,
                "path": str(request.url.path),
                "duration_ms": round(process_time * 1000, 2),
                "error": str(e),
                "request_id": request_id
            }
        )
        raise
    
    finally:
        # リクエストコンテキストをクリア
        clear_request_context()

# CORSミドルウェア設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# APIルーターのマウント
app.include_router(api_router, prefix="/api")

# 直接のテストエンドポイント（トラブルシューティング用）
@app.get("/direct-test")
@limiter.limit("10/minute")  # テストエンドポイントは厳しく制限
async def direct_test_endpoint(request: Request):
    return {"message": "直接のテストエンドポイントが動作しています"}

# データベースデバッグ用エンドポイント
@app.get("/debug/db-status")
@limiter.limit("5/minute")
async def debug_db_status(request: Request):
    try:
        from app.db.session import SessionLocal
        from app.models.track import Track
        from app.models.user import User
        from sqlalchemy import text
        
        db = SessionLocal()
        
        # テーブル存在確認
        tables = db.execute(text("SELECT name FROM sqlite_master WHERE type='table'")).fetchall()
        table_names = [table[0] for table in tables]
        
        # データ数確認
        track_count = db.query(Track).count()
        user_count = db.query(User).count()
        
        # サンプルトラック取得（最初の1件）
        sample_track = db.query(Track).first()
        sample_user = db.query(User).first()
        
        db.close()
        
        return {
            "status": "success",
            "tables": table_names,
            "track_count": track_count,
            "user_count": user_count,
            "sample_track": {
                "id": sample_track.id if sample_track else None,
                "title": sample_track.title if sample_track else None,
                "artist_id": sample_track.artist_id if sample_track else None
            } if sample_track else None,
            "sample_user": {
                "id": sample_user.id if sample_user else None,
                "display_name": sample_user.display_name if sample_user else None,
                "user_role": sample_user.user_role if sample_user else None
            } if sample_user else None
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__
        }

# 本番環境用Seedデータ作成エンドポイント
@app.post("/debug/create-seed")
@limiter.limit("1/hour")  # 厳格に制限
async def create_production_seed(request: Request):
    try:
        from app.db.session import SessionLocal
        from app.models.track import Track
        from app.models.user import User
        from app.schemas.user import UserRole
        from decimal import Decimal
        from datetime import date, timedelta
        import uuid
        import random
        
        db = SessionLocal()
        
        # 既存データ確認
        existing_tracks = db.query(Track).count()
        existing_users = db.query(User).count()
        
        if existing_tracks > 0:
            db.close()
            return {
                "status": "skipped",
                "message": "データが既に存在します",
                "existing_tracks": existing_tracks,
                "existing_users": existing_users
            }
        
        # アーティスト作成
        artists_data = [
            {"email": "moonlight.echo@musicshelf.net", "display_name": "Moonlight Echo"},
            {"email": "urban.soul@musicshelf.net", "display_name": "Urban Soul Collective"},
            {"email": "acoustic.garden@musicshelf.net", "display_name": "Acoustic Garden"}
        ]
        
        artists = []
        for data in artists_data:
            artist = User(
                email=data["email"],
                display_name=data["display_name"],
                firebase_uid=f"prod_uid_{uuid.uuid4().hex[:8]}",
                user_role=UserRole.ARTIST,
                is_verified=True
            )
            db.add(artist)
            artists.append(artist)
        
        db.flush()
        
        # 楽曲作成
        tracks_data = [
            {"title": "Midnight Reflections", "genre": "エレクトロニック", "duration": 285, "price": 450.0, "artist_index": 0},
            {"title": "City Lights Serenade", "genre": "R&B", "duration": 240, "price": 380.0, "artist_index": 1},
            {"title": "Forest Dawn", "genre": "フォーク", "duration": 220, "price": 320.0, "artist_index": 2}
        ]
        
        tracks = []
        base_date = date.today() - timedelta(days=30)
        
        for i, data in enumerate(tracks_data):
            track = Track(
                title=data["title"],
                description=f"{data['title']}の説明",
                genre=data["genre"],
                cover_art_url=f"https://example.com/demo/covers/{data['title'].lower().replace(' ', '_')}.jpg",
                audio_file_url=f"https://example.com/demo/audio/{data['title'].lower().replace(' ', '_')}.mp3",
                duration=data["duration"],
                price=Decimal(str(data["price"])),
                release_date=base_date + timedelta(days=i * 10),
                artist_id=artists[data["artist_index"]].id,
                is_public=True,
                play_count=random.randint(50, 500)
            )
            db.add(track)
            tracks.append(track)
        
        db.commit()
        db.close()
        
        return {
            "status": "success",
            "message": "Seedデータを作成しました",
            "created_artists": len(artists),
            "created_tracks": len(tracks)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "error_type": type(e).__name__
        }

# カスタムレート制限エラーハンドラー
@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    logger.warning(f"Rate limit exceeded for {get_client_id(request)}: {exc.detail}")
    return JSONResponse(
        status_code=429,
        content={
            "detail": "リクエスト制限に達しました。しばらく時間をおいてから再試行してください。",
            "retry_after": str(exc.retry_after) if hasattr(exc, 'retry_after') else "60"
        },
        headers={"Retry-After": str(getattr(exc, 'retry_after', 60))}
    )

# 例外ハンドラー（デバッグ用に詳細表示）
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    # 構造化ログでエラーを記録
    logger.error(
        f"Unhandled exception: {str(exc)}",
        extra={
            "method": request.method,
            "path": str(request.url.path),
            "client_ip": request.client.host if request.client else "unknown",
            "user_agent": request.headers.get("user-agent", "unknown"),
            "exception_type": type(exc).__name__,
            "exception_message": str(exc)
        },
        exc_info=True
    )
    
    # デバッグ用: 詳細なエラー情報を返す
    import traceback
    return JSONResponse(
        status_code=500,
        content={
            "detail": "サーバー内部エラーが発生しました。",
            "debug_info": {
                "error_type": type(exc).__name__,
                "error_message": str(exc),
                "traceback": traceback.format_exc()
            }
        }
    )

# 静的ファイルの設定（必要な場合）
# app.mount("/static", StaticFiles(directory="static"), name="static")

# アプリケーション起動時のイベント
@app.on_event("startup")
async def startup_event():
    application_logger.log_business_event(
        "application_startup",
        {
            "environment": os.environ.get("ENVIRONMENT", "development"),
            "version": "0.1.0"
        }
    )
    
    try:
        create_tables()  # データベーステーブルの作成
        application_logger.log_business_event(
            "database_initialization",
            {"status": "success"}
        )
    except Exception as e:
        logger.error(f"データベース初期化エラー: {str(e)}", exc_info=True)
        # 本番環境ではデータベースエラーで起動を停止しない
        if os.environ.get("ENVIRONMENT") == "production":
            logger.warning("本番環境：データベース初期化エラーをスキップして起動を継続")
        else:
            raise
    
    logger.info("アプリケーションが正常に起動しました")

# アプリケーション終了時のイベント
@app.on_event("shutdown")
async def shutdown_event():
    application_logger.log_business_event(
        "application_shutdown",
        {
            "environment": os.environ.get("ENVIRONMENT", "development"),
            "graceful": True
        }
    )
    logger.info("アプリケーションを終了しています...")

# ヘルスチェックエンドポイント（レート制限緩め）
@app.get("/health")
@limiter.limit("60/minute")
async def health_check(request: Request):
    # より詳細なヘルスチェック
    try:
        from app.db.session import SessionLocal
        from sqlalchemy import text
        db = SessionLocal()
        # データベース接続確認
        db.execute(text("SELECT 1"))
        db.close()
        db_status = "healthy"
        
        # 成功ログを記録
        logger.debug(
            "Health check successful",
            extra={
                "health_check": True,
                "database_status": "healthy",
                "endpoint": "/health"
            }
        )
        
    except Exception as e:
        db_status = "unhealthy"
        
        # 構造化ログでエラーを記録
        logger.error(
            f"Database health check failed: {e}",
            extra={
                "health_check": True,
                "database_status": "unhealthy",
                "error": str(e),
                "endpoint": "/health"
            }
        )
    
    # 本番環境では常にhealthyを返す（Container App再起動を防ぐため）
    if os.environ.get("ENVIRONMENT") == "production":
        overall_status = "healthy"
    else:
        overall_status = "healthy" if db_status == "healthy" else "unhealthy"
    
    return {
        "status": overall_status,
        "database": db_status,
        "timestamp": time.time(),
        "environment": os.environ.get("ENVIRONMENT", "development")
    }

# Root エンドポイント（何も返さない）
@app.get("/")
@limiter.limit("30/minute")
async def root(request: Request):
    return {}

# 開発サーバーの起動（直接このファイルを実行した場合）
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)


