"""
機能フラグ管理システム

環境変数またはJSONファイルで機能のON/OFFを制御
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path

class FeatureFlags:
    """機能フラグ管理クラス"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file or os.environ.get("FEATURE_FLAGS_CONFIG", "./feature_flags.json")
        self._flags: Dict[str, Any] = {}
        self._load_flags()
    
    def _load_flags(self):
        """設定ファイルまたは環境変数から機能フラグを読み込み"""
        # デフォルト設定
        self._flags = {
            "payment": {
                "enabled": True,
                "methods_enabled": True,
                "downloads_enabled": True,
                "coming_soon_message": "決済機能は近日公開予定です。現在は無料でお楽しみいただけます。"
            },
            "features": {
                "subscription_plans": False,
                "live_streaming": False,
                "social_features": True,
                "analytics_dashboard": True,
                "artist_verification": False
            },
            "limits": {
                "max_uploads_per_day": 10,
                "max_file_size_mb": 100,
                "free_streaming_limit": 100
            }
        }
        
        # JSONファイルから読み込み（存在する場合）
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    file_flags = json.load(f)
                    self._merge_flags(file_flags)
            except Exception as e:
                print(f"Warning: Could not load feature flags from {self.config_file}: {e}")
        
        # 環境変数からオーバーライド
        self._load_from_env()
    
    def _merge_flags(self, new_flags: Dict[str, Any]):
        """新しいフラグ設定を既存設定にマージ"""
        for key, value in new_flags.items():
            if isinstance(value, dict) and key in self._flags:
                self._flags[key].update(value)
            else:
                self._flags[key] = value
    
    def _load_from_env(self):
        """環境変数から機能フラグを読み込み"""
        # 決済機能
        if "PAYMENT_ENABLED" in os.environ:
            self._flags["payment"]["enabled"] = self._parse_bool(os.environ["PAYMENT_ENABLED"])
        
        if "PAYMENT_METHODS_ENABLED" in os.environ:
            self._flags["payment"]["methods_enabled"] = self._parse_bool(os.environ["PAYMENT_METHODS_ENABLED"])
        
        if "PURCHASE_DOWNLOADS_ENABLED" in os.environ:
            self._flags["payment"]["downloads_enabled"] = self._parse_bool(os.environ["PURCHASE_DOWNLOADS_ENABLED"])
        
        if "PAYMENT_COMING_SOON_MESSAGE" in os.environ:
            self._flags["payment"]["coming_soon_message"] = os.environ["PAYMENT_COMING_SOON_MESSAGE"]
        
        # その他の機能
        feature_mappings = {
            "SUBSCRIPTION_PLANS_ENABLED": ("features", "subscription_plans"),
            "LIVE_STREAMING_ENABLED": ("features", "live_streaming"),
            "SOCIAL_FEATURES_ENABLED": ("features", "social_features"),
            "ANALYTICS_DASHBOARD_ENABLED": ("features", "analytics_dashboard"),
            "ARTIST_VERIFICATION_ENABLED": ("features", "artist_verification"),
        }
        
        for env_var, (category, key) in feature_mappings.items():
            if env_var in os.environ:
                self._flags[category][key] = self._parse_bool(os.environ[env_var])
        
        # 制限値
        limit_mappings = {
            "MAX_UPLOADS_PER_DAY": ("limits", "max_uploads_per_day"),
            "MAX_FILE_SIZE_MB": ("limits", "max_file_size_mb"),
            "FREE_STREAMING_LIMIT": ("limits", "free_streaming_limit"),
        }
        
        for env_var, (category, key) in limit_mappings.items():
            if env_var in os.environ:
                try:
                    self._flags[category][key] = int(os.environ[env_var])
                except ValueError:
                    print(f"Warning: Invalid integer value for {env_var}")
    
    def _parse_bool(self, value: str) -> bool:
        """文字列をbooleanに変換"""
        return value.lower() in ("true", "1", "yes", "on", "enabled")
    
    def is_enabled(self, feature_path: str) -> bool:
        """機能が有効かどうかチェック"""
        try:
            keys = feature_path.split('.')
            value = self._flags
            for key in keys:
                value = value[key]
            return bool(value)
        except (KeyError, TypeError):
            return False
    
    def get_value(self, feature_path: str, default: Any = None) -> Any:
        """機能フラグの値を取得"""
        try:
            keys = feature_path.split('.')
            value = self._flags
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return default
    
    def get_payment_config(self) -> Dict[str, Any]:
        """決済機能の設定を取得"""
        return self._flags.get("payment", {})
    
    def get_all_flags(self) -> Dict[str, Any]:
        """すべての機能フラグを取得"""
        return self._flags.copy()
    
    def save_to_file(self, file_path: Optional[str] = None):
        """現在の設定をJSONファイルに保存"""
        file_path = file_path or self.config_file
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self._flags, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving feature flags to {file_path}: {e}")


# グローバルインスタンス
feature_flags = FeatureFlags()

# 便利な関数
def is_payment_enabled() -> bool:
    """決済機能が有効かどうか"""
    return feature_flags.is_enabled("payment.enabled")

def is_feature_enabled(feature: str) -> bool:
    """指定された機能が有効かどうか"""
    return feature_flags.is_enabled(feature)

def get_payment_coming_soon_message() -> str:
    """決済機能のComing Soonメッセージを取得"""
    return feature_flags.get_value("payment.coming_soon_message", "決済機能は準備中です。")

def get_feature_value(feature: str, default: Any = None) -> Any:
    """機能設定値を取得"""
    return feature_flags.get_value(feature, default)