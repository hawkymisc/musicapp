"""
構造化ログシステム
JSON形式での出力とセキュリティイベントトラッキング
"""

import json
import sys
import os
import time
import uuid
from datetime import datetime
from typing import Dict, Any, Optional, Union
import logging
import logging.config
from contextvars import ContextVar
from functools import wraps

# リクエストコンテキスト
request_id_var: ContextVar[str] = ContextVar('request_id', default='')
user_id_var: ContextVar[str] = ContextVar('user_id', default='')

class StructuredFormatter(logging.Formatter):
    """JSON形式での構造化ログフォーマッタ"""
    
    def __init__(self, include_extra: bool = True):
        super().__init__()
        self.include_extra = include_extra
    
    def format(self, record: logging.LogRecord) -> str:
        # 基本ログ情報
        log_data = {
            "timestamp": datetime.utcfromtimestamp(record.created).isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # リクエストコンテキスト情報
        request_id = request_id_var.get('')
        user_id = user_id_var.get('')
        
        if request_id:
            log_data["request_id"] = request_id
        if user_id:
            log_data["user_id"] = user_id
        
        # 例外情報
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info) if record.exc_info else None
            }
        
        # 追加のextraフィールドを含める
        if self.include_extra:
            for key, value in record.__dict__.items():
                if key not in {
                    'name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 
                    'filename', 'module', 'lineno', 'funcName', 'created', 
                    'msecs', 'relativeCreated', 'thread', 'threadName', 
                    'processName', 'process', 'getMessage', 'exc_info', 'exc_text', 
                    'stack_info', 'message'
                }:
                    # JSONシリアライズ可能性をチェック
                    try:
                        json.dumps(value)
                        log_data[key] = value
                    except (TypeError, ValueError):
                        log_data[key] = str(value)
        
        # 環境情報
        log_data["environment"] = os.environ.get("ENVIRONMENT", "development")
        
        return json.dumps(log_data, ensure_ascii=False)

class SecurityLogger:
    """セキュリティイベント専用ロガー"""
    
    def __init__(self):
        self.logger = logging.getLogger("security")
    
    def log_authentication_attempt(self, success: bool, user_id: Optional[str] = None, 
                                  ip_address: Optional[str] = None, user_agent: Optional[str] = None,
                                  failure_reason: Optional[str] = None):
        """認証試行をログ記録"""
        event_data = {
            "event_type": "authentication_attempt",
            "success": success,
            "user_id": user_id,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "failure_reason": failure_reason,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        if success:
            self.logger.info("Authentication successful", extra=event_data)
        else:
            self.logger.warning("Authentication failed", extra=event_data)
    
    def log_authorization_failure(self, user_id: str, resource: str, action: str, 
                                 ip_address: Optional[str] = None):
        """認可失敗をログ記録"""
        event_data = {
            "event_type": "authorization_failure",
            "user_id": user_id,
            "resource": resource,
            "action": action,
            "ip_address": ip_address,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        self.logger.warning("Authorization failed", extra=event_data)
    
    def log_suspicious_activity(self, activity_type: str, details: Dict[str, Any], 
                               user_id: Optional[str] = None, ip_address: Optional[str] = None):
        """不審な活動をログ記録"""
        event_data = {
            "event_type": "suspicious_activity",
            "activity_type": activity_type,
            "details": details,
            "user_id": user_id,
            "ip_address": ip_address,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        self.logger.error("Suspicious activity detected", extra=event_data)
    
    def log_data_access(self, user_id: str, resource_type: str, resource_id: str, 
                       action: str, ip_address: Optional[str] = None):
        """データアクセスをログ記録"""
        event_data = {
            "event_type": "data_access",
            "user_id": user_id,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "action": action,
            "ip_address": ip_address,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        self.logger.info("Data access", extra=event_data)

class PerformanceLogger:
    """パフォーマンス専用ロガー"""
    
    def __init__(self):
        self.logger = logging.getLogger("performance")
    
    def log_request_timing(self, endpoint: str, method: str, duration: float, 
                          status_code: int, user_id: Optional[str] = None):
        """リクエスト処理時間をログ記録"""
        event_data = {
            "event_type": "request_timing",
            "endpoint": endpoint,
            "method": method,
            "duration_ms": round(duration * 1000, 2),
            "status_code": status_code,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        # 処理時間によってログレベルを調整
        if duration > 5.0:  # 5秒
            self.logger.error("Very slow response", extra=event_data)
        elif duration > 2.0:  # 2秒
            self.logger.warning("Slow response", extra=event_data)
        elif duration > 1.0:  # 1秒
            self.logger.info("Moderately slow response", extra=event_data)
        else:
            self.logger.debug("Normal response time", extra=event_data)
    
    def log_database_query(self, query_type: str, duration: float, rows_affected: Optional[int] = None):
        """データベースクエリ処理時間をログ記録"""
        event_data = {
            "event_type": "database_query",
            "query_type": query_type,
            "duration_ms": round(duration * 1000, 2),
            "rows_affected": rows_affected,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        if duration > 1.0:  # 1秒
            self.logger.warning("Slow database query", extra=event_data)
        else:
            self.logger.debug("Database query", extra=event_data)

class ApplicationLogger:
    """アプリケーション専用ロガー"""
    
    def __init__(self):
        self.logger = logging.getLogger("application")
    
    def log_user_action(self, user_id: str, action: str, resource_type: Optional[str] = None, 
                       resource_id: Optional[str] = None, details: Optional[Dict[str, Any]] = None):
        """ユーザーアクションをログ記録"""
        event_data = {
            "event_type": "user_action",
            "user_id": user_id,
            "action": action,
            "resource_type": resource_type,
            "resource_id": resource_id,
            "details": details or {},
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        self.logger.info("User action", extra=event_data)
    
    def log_business_event(self, event_type: str, details: Dict[str, Any], 
                          user_id: Optional[str] = None):
        """ビジネスイベントをログ記録"""
        event_data = {
            "event_type": "business_event",
            "business_event_type": event_type,
            "details": details,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
        
        self.logger.info("Business event", extra=event_data)

# セットアップ関数
def setup_logging():
    """ログシステムを初期化"""
    
    # ログレベルを環境変数から設定
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    
    # テスト時はログレベルを下げる
    if os.environ.get("TESTING") == "True":
        log_level = "WARNING"
    
    # ログ設定
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "structured": {
                "()": StructuredFormatter,
                "include_extra": True
            },
            "simple": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "structured" if os.environ.get("STRUCTURED_LOGS", "true").lower() == "true" else "simple",
                "stream": sys.stdout
            },
            "security_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "INFO",
                "formatter": "structured",
                "filename": "logs/security.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf-8"
            },
            "error_file": {
                "class": "logging.handlers.RotatingFileHandler",
                "level": "ERROR",
                "formatter": "structured",
                "filename": "logs/error.log",
                "maxBytes": 10485760,  # 10MB
                "backupCount": 5,
                "encoding": "utf-8"
            }
        },
        "loggers": {
            "": {  # root logger
                "level": log_level,
                "handlers": ["console", "error_file"]
            },
            "security": {
                "level": "INFO",
                "handlers": ["console", "security_file", "error_file"],
                "propagate": False
            },
            "performance": {
                "level": "DEBUG",
                "handlers": ["console"],
                "propagate": False
            },
            "application": {
                "level": "INFO",
                "handlers": ["console"],
                "propagate": False
            },
            "sqlalchemy.engine": {
                "level": "WARNING",  # SQLクエリログは抑制
                "handlers": ["console"],
                "propagate": False
            }
        }
    }
    
    # ログディレクトリを作成
    os.makedirs("logs", exist_ok=True)
    
    logging.config.dictConfig(logging_config)

# リクエストコンテキスト管理
def set_request_context(request_id: str, user_id: Optional[str] = None):
    """リクエストコンテキストを設定"""
    request_id_var.set(request_id)
    if user_id:
        user_id_var.set(user_id)

def clear_request_context():
    """リクエストコンテキストをクリア"""
    request_id_var.set('')
    user_id_var.set('')

def generate_request_id() -> str:
    """リクエストIDを生成"""
    return str(uuid.uuid4())

# デコレータ
def log_performance(logger_name: str = "performance"):
    """関数の処理時間をログ記録するデコレータ"""
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.time()
            logger = logging.getLogger(logger_name)
            
            try:
                result = await func(*args, **kwargs)
                duration = time.time() - start_time
                
                logger.info(f"Function {func.__name__} completed", extra={
                    "function_name": func.__name__,
                    "duration_ms": round(duration * 1000, 2),
                    "success": True
                })
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                
                logger.error(f"Function {func.__name__} failed", extra={
                    "function_name": func.__name__,
                    "duration_ms": round(duration * 1000, 2),
                    "success": False,
                    "error": str(e)
                })
                
                raise
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.time()
            logger = logging.getLogger(logger_name)
            
            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                
                logger.info(f"Function {func.__name__} completed", extra={
                    "function_name": func.__name__,
                    "duration_ms": round(duration * 1000, 2),
                    "success": True
                })
                
                return result
            except Exception as e:
                duration = time.time() - start_time
                
                logger.error(f"Function {func.__name__} failed", extra={
                    "function_name": func.__name__,
                    "duration_ms": round(duration * 1000, 2),
                    "success": False,
                    "error": str(e)
                })
                
                raise
        
        # 非同期関数かどうかを判定
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator

# グローバルインスタンス
security_logger = SecurityLogger()
performance_logger = PerformanceLogger()
application_logger = ApplicationLogger()

# 初期化
setup_logging()