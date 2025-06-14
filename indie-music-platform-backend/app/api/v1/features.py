from fastapi import APIRouter
from typing import Dict, Any

from app.core.feature_flags import feature_flags

router = APIRouter()

@router.get("/", response_model=Dict[str, Any])
async def get_feature_flags() -> Dict[str, Any]:
    """
    クライアント向けの機能フラグ情報を取得
    """
    all_flags = feature_flags.get_all_flags()
    
    # クライアントに安全に公開できる情報のみを返す
    public_flags = {
        "payment": {
            "enabled": all_flags.get("payment", {}).get("enabled", False),
            "methods_enabled": all_flags.get("payment", {}).get("methods_enabled", False),
            "downloads_enabled": all_flags.get("payment", {}).get("downloads_enabled", False),
            "coming_soon_message": all_flags.get("payment", {}).get("coming_soon_message", ""),
            "test_mode": all_flags.get("payment", {}).get("test_mode", False)
        },
        "features": all_flags.get("features", {}),
        "ui": all_flags.get("ui", {}),
        "limits": {
            "max_file_size_mb": all_flags.get("limits", {}).get("max_file_size_mb", 100),
            "max_uploads_per_day": all_flags.get("limits", {}).get("max_uploads_per_day", 10),
            "max_playlist_size": all_flags.get("limits", {}).get("max_playlist_size", 1000)
        }
    }
    
    return public_flags

@router.get("/payment", response_model=Dict[str, Any])
async def get_payment_features() -> Dict[str, Any]:
    """
    決済機能の設定情報を取得
    """
    payment_config = feature_flags.get_payment_config()
    
    return {
        "enabled": payment_config.get("enabled", False),
        "methods_enabled": payment_config.get("methods_enabled", False),
        "downloads_enabled": payment_config.get("downloads_enabled", False),
        "coming_soon_message": payment_config.get("coming_soon_message", ""),
        "test_mode": payment_config.get("test_mode", False),
        "webhook_enabled": payment_config.get("webhook_enabled", False)
    }

@router.get("/status")
async def get_service_status() -> Dict[str, Any]:
    """
    サービス全体の機能状態を取得
    """
    payment_config = feature_flags.get_payment_config()
    
    return {
        "service_name": "インディーズミュージックプラットフォーム",
        "version": "1.0.0",
        "status": "operational",
        "features": {
            "streaming": True,
            "uploads": True,
            "user_accounts": True,
            "search": True,
            "playlists": feature_flags.is_enabled("features.playlist_sharing"),
            "payments": payment_config.get("enabled", False),
            "downloads": payment_config.get("downloads_enabled", False),
            "social": feature_flags.is_enabled("features.social_features"),
            "analytics": feature_flags.is_enabled("features.analytics_dashboard")
        },
        "maintenance_mode": feature_flags.is_enabled("ui.maintenance_mode"),
        "beta_features": feature_flags.is_enabled("ui.enable_beta_features")
    }