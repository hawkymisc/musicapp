from pydantic import BaseSettings
from typing import List
import os
from dotenv import load_dotenv

# .envファイルの読み込み
load_dotenv()


class Settings(BaseSettings):
    PROJECT_NAME: str = "インディーズミュージックアプリ"
    API_V1_STR: str = "/api/v1"

    # PostgreSQL接続設定
    POSTGRES_SERVER: str = os.environ.get("POSTGRES_SERVER", "localhost")
    POSTGRES_USER: str = os.environ.get("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.environ.get("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.environ.get("POSTGRES_DB", "indie_music_db")
    POSTGRES_PORT: str = os.environ.get("POSTGRES_PORT", "5432")
    DATABASE_URL: str = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"

    # CORS設定
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",  # React開発サーバー
        "http://localhost:5173",  # Vite開発サーバー
        "http://localhost:8080",
        "https://yourdomain.com"  # 本番ドメイン
    ]

    # AWS設定
    AWS_ACCESS_KEY_ID: str = os.environ.get("AWS_ACCESS_KEY_ID", "")
    AWS_SECRET_ACCESS_KEY: str = os.environ.get("AWS_SECRET_ACCESS_KEY", "")
    AWS_REGION: str = os.environ.get("AWS_REGION", "ap-northeast-1")
    S3_BUCKET_NAME: str = os.environ.get("S3_BUCKET_NAME", "indie-music-app")

    # Firebase設定
    FIREBASE_CREDENTIALS_PATH: str = os.environ.get("FIREBASE_CREDENTIALS_PATH", "./firebase-credentials.json")

    # Stripe設定
    STRIPE_API_KEY: str = os.environ.get("STRIPE_API_KEY", "")
    STRIPE_WEBHOOK_SECRET: str = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

    # プラットフォーム手数料
    PLATFORM_FEE_PERCENTAGE: float = 15.0  # 15%
    
    # 機能フラグ設定
    PAYMENT_ENABLED: bool = os.environ.get("PAYMENT_ENABLED", "true").lower() in ("true", "1", "yes", "on")
    PAYMENT_METHODS_ENABLED: bool = os.environ.get("PAYMENT_METHODS_ENABLED", "true").lower() in ("true", "1", "yes", "on")
    PURCHASE_DOWNLOADS_ENABLED: bool = os.environ.get("PURCHASE_DOWNLOADS_ENABLED", "true").lower() in ("true", "1", "yes", "on")
    
    # 決済機能設定
    PAYMENT_COMING_SOON_MESSAGE: str = os.environ.get(
        "PAYMENT_COMING_SOON_MESSAGE", 
        "決済機能は近日公開予定です。現在は無料でお楽しみいただけます。"
    )

    class Config:
        case_sensitive = True


# 設定インスタンスの作成
settings = Settings()


