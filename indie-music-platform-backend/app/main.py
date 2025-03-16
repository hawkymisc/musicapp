from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.openapi.docs import get_swagger_ui_html
from starlette.staticfiles import StaticFiles
import time
import logging
from typing import Callable
import uvicorn

from app.api.router import api_router
from app.core.config import settings
from app.db.session import create_tables

# ロガー設定
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# FastAPIインスタンスの作成
app = FastAPI(
    title="インディーズミュージックアプリAPI",
    description="インディーズミュージシャンが楽曲を販売・配信するためのAPI",
    version="0.1.0"
)

# ミドルウェア設定
# リクエスト処理時間のロギング
@app.middleware("http")
async def add_process_time_header(request: Request, call_next: Callable):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info(f"Path: {request.url.path} Process time: {process_time:.4f}s")
    return response

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

# 例外ハンドラー
@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "サーバー内部エラーが発生しました。"}
    )

# 静的ファイルの設定（必要な場合）
# app.mount("/static", StaticFiles(directory="static"), name="static")

# アプリケーション起動時のイベント
@app.on_event("startup")
async def startup_event():
    logger.info("アプリケーションを起動しています...")
    create_tables()  # データベーステーブルの作成
    logger.info("アプリケーションが正常に起動しました")

# アプリケーション終了時のイベント
@app.on_event("shutdown")
async def shutdown_event():
    logger.info("アプリケーションを終了しています...")

# ヘルスチェックエンドポイント
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Root エンドポイント
@app.get("/")
async def root():
    return {
        "name": "インディーズミュージックアプリAPI",
        "version": "0.1.0",
        "docs_url": "/docs"
    }

# 開発サーバーの起動（直接このファイルを実行した場合）
if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)


