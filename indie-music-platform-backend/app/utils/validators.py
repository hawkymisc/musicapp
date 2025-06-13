"""
入力値検証とセキュリティ
認証済みでないデータの入力値検証関数を提供
"""

import re
import os
import magic
import hashlib
from typing import Optional, List, Dict, Any, Union
from fastapi import HTTPException, UploadFile
from starlette.status import HTTP_400_BAD_REQUEST, HTTP_413_REQUEST_ENTITY_TOO_LARGE
import logging

logger = logging.getLogger(__name__)

# ==================== 定数 ====================

# ファイルサイズ制限
MAX_AUDIO_FILE_SIZE = 100 * 1024 * 1024  # 100MB
MAX_IMAGE_FILE_SIZE = 10 * 1024 * 1024   # 10MB
MAX_FILENAME_LENGTH = 255

# 許可されたファイル形式
ALLOWED_AUDIO_MIME_TYPES = {
    'audio/mpeg',      # MP3
    'audio/wav',       # WAV
    'audio/flac',      # FLAC
    'audio/aac',       # AAC
    'audio/ogg',       # OGG
}

ALLOWED_IMAGE_MIME_TYPES = {
    'image/jpeg',      # JPEG
    'image/png',       # PNG
    'image/webp',      # WebP
}

ALLOWED_AUDIO_EXTENSIONS = {'.mp3', '.wav', '.flac', '.aac', '.ogg'}
ALLOWED_IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.webp'}

# 危険なファイル拡張子
DANGEROUS_EXTENSIONS = {
    '.exe', '.bat', '.cmd', '.com', '.pif', '.scr', '.vbs', '.js', 
    '.jar', '.php', '.asp', '.aspx', '.jsp', '.sh', '.py', '.pl'
}

# パストラバーサル攻撃パターン
BLOCKED_PATH_PATTERNS = [
    r'\.\./',      # パストラバーサル
    r'\.\.\\\\',  # パストラバーサル（Windows）
    r'/etc/',      # システム設定ディレクトリ
    r'/var/',      # システム設定ディレクトリ
    r'C:\\\\',       # Windows システム設定ディレクトリ
    r'~/\.',       # 隠しファイル
]

# 文字列長制限
MAX_STRING_LENGTH = 10000
MAX_TITLE_LENGTH = 200
MAX_DESCRIPTION_LENGTH = 2000
MAX_SEARCH_LENGTH = 100

# 正規表現パターン
EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
FIREBASE_UID_PATTERN = re.compile(r'^[a-zA-Z0-9]{10,128}$')
UUID_PATTERN = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.IGNORECASE)

# SQLインジェクション検出パターン
SQL_INJECTION_PATTERNS = [
    r"(\s|^)(union|select|insert|update|delete|drop|create|alter|exec|execute)(\s|\()",
    r"(\s|^)(or|and)\s+\d+\s*=\s*\d+",
    r"'(\s|;|--|#)",
    r"--(\s|$)",
    r"/\*.*?\*/",
    r"xp_cmdshell",
    r"sp_executesql",
]

# XSS攻撃検出パターン
XSS_PATTERNS = [
    r"<script[^>]*>.*?</script>",
    r"javascript:",
    r"on\w+\s*=",
    r"<iframe[^>]*>",
    r"<object[^>]*>",
    r"<embed[^>]*>",
    r"eval\s*\(",
    r"expression\s*\(",
]

# ==================== 検証関数 ====================

class ValidationError(HTTPException):
    """入力検証エラー"""
    def __init__(self, detail: str, status_code: int = HTTP_400_BAD_REQUEST):
        super().__init__(status_code=status_code, detail=detail)

def validate_string_length(value: str, field_name: str, max_length: int, min_length: int = 0) -> str:
    """文字列長検証"""
    if not isinstance(value, str):
        raise ValidationError(f"{field_name}は文字列である必要があります")
    
    if len(value) < min_length:
        raise ValidationError(f"{field_name}は{min_length}文字以上である必要があります")
    
    if len(value) > max_length:
        raise ValidationError(f"{field_name}は{max_length}文字以下である必要があります")
    
    return value.strip()

def validate_email(email: str) -> str:
    """メールアドレス検証"""
    email = validate_string_length(email, "メールアドレス", 254, 5)
    
    if not EMAIL_PATTERN.match(email):
        raise ValidationError("無効なメールアドレス形式です")
    
    return email.lower()

def validate_firebase_uid(firebase_uid: str) -> str:
    """Firebase UID形式検証"""
    firebase_uid = validate_string_length(firebase_uid, "Firebase UID", 128, 10)
    
    if not FIREBASE_UID_PATTERN.match(firebase_uid):
        raise ValidationError("無効なFirebase UID形式です")
    
    return firebase_uid

def validate_uuid(uuid_str: str, field_name: str = "UUID") -> str:
    """UUID形式検証"""
    if not isinstance(uuid_str, str):
        raise ValidationError(f"{field_name}は文字列である必要があります")
    
    if not UUID_PATTERN.match(uuid_str):
        raise ValidationError(f"無効な{field_name}形式です")
    
    return uuid_str.lower()

def detect_sql_injection(value: str) -> bool:
    """SQLインジェクション攻撃を検出"""
    if not isinstance(value, str):
        return False
    
    value_lower = value.lower()
    
    for pattern in SQL_INJECTION_PATTERNS:
        if re.search(pattern, value_lower, re.IGNORECASE):
            logger.warning(f"SQLインジェクション攻撃の可能性を検出: {pattern}")
            return True
    
    return False

def detect_xss_attempt(value: str) -> bool:
    """XSS攻撃を検出"""
    if not isinstance(value, str):
        return False
    
    value_lower = value.lower()
    
    for pattern in XSS_PATTERNS:
        if re.search(pattern, value_lower, re.IGNORECASE):
            logger.warning(f"XSS攻撃の可能性を検出: {pattern}")
            return True
    
    return False

def sanitize_string(value: str, field_name: str, max_length: int = MAX_STRING_LENGTH) -> str:
    """文字列サニタイズと検証"""
    if not isinstance(value, str):
        raise ValidationError(f"{field_name}は文字列である必要があります")
    
    # 長さ検証
    value = validate_string_length(value, field_name, max_length)
    
    # SQLインジェクション検出
    if detect_sql_injection(value):
        raise ValidationError(f"{field_name}に危険な文字列が含まれています")
    
    # XSS検出
    if detect_xss_attempt(value):
        raise ValidationError(f"{field_name}にスクリプトが含まれています")
    
    # 制御文字を除去
    value = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', value)
    
    # 前後の空白を除去
    return value.strip()

def validate_filename(filename: str, file_type: str = "file") -> str:
    """ファイル名の安全性検証"""
    if not filename:
        raise ValidationError("ファイル名が指定されていません")
    
    # 長さ検証
    if len(filename) > MAX_FILENAME_LENGTH:
        raise ValidationError(f"ファイル名は{MAX_FILENAME_LENGTH}文字以下である必要があります")
    
    # 危険なパス文字を検出
    for pattern in BLOCKED_PATH_PATTERNS:
        if re.search(pattern, filename, re.IGNORECASE):
            raise ValidationError("ファイル名に危険な文字列が含まれています")
    
    # 危険な拡張子検証
    name_lower = filename.lower()
    for ext in DANGEROUS_EXTENSIONS:
        if ext in name_lower:
            raise ValidationError("危険なファイル形式です")
    
    # ファイル拡張子検証
    ext = os.path.splitext(filename)[1].lower()
    
    if file_type == "audio" and ext not in ALLOWED_AUDIO_EXTENSIONS:
        raise ValidationError(f"許可されていない音声ファイル形式です。対応形式: {', '.join(ALLOWED_AUDIO_EXTENSIONS)}")
    
    if file_type == "image" and ext not in ALLOWED_IMAGE_EXTENSIONS:
        raise ValidationError(f"許可されていない画像ファイル形式です。対応形式: {', '.join(ALLOWED_IMAGE_EXTENSIONS)}")
    
    return filename

def validate_file_content(file: UploadFile, file_type: str = "file") -> bool:
    """ファイル内容検証"""
    if not file:
        raise ValidationError("ファイルが指定されていません")
    
    # ファイルサイズ検証
    file.file.seek(0, 2)  # ファイル末尾に移動
    size = file.file.tell()
    file.file.seek(0)     # ファイル先頭に戻る
    
    max_size = MAX_AUDIO_FILE_SIZE if file_type == "audio" else MAX_IMAGE_FILE_SIZE
    
    if size > max_size:
        max_size_mb = max_size / (1024 * 1024)
        raise ValidationError(
            f"ファイルサイズが制限を超えています。最大{max_size_mb:.0f}MBです",
            status_code=HTTP_413_REQUEST_ENTITY_TOO_LARGE
        )
    
    if size == 0:
        raise ValidationError("空のファイルはアップロードできません")
    
    # ファイル名検証
    validate_filename(file.filename, file_type)
    
    # MIME型検証（python-magicを使用してファイル内容から判定）
    try:
        file_content = file.file.read(1024)  # 最初の1KB読み取り
        file.file.seek(0)  # ファイル先頭に戻る
        
        mime_type = magic.from_buffer(file_content, mime=True)
        
        if file_type == "audio" and mime_type not in ALLOWED_AUDIO_MIME_TYPES:
            raise ValidationError(f"許可されていない音声ファイル形式です: {mime_type}")
        
        if file_type == "image" and mime_type not in ALLOWED_IMAGE_MIME_TYPES:
            raise ValidationError(f"許可されていない画像ファイル形式です: {mime_type}")
            
    except Exception as e:
        logger.error(f"ファイル内容検証でエラー: {e}")
        raise ValidationError("ファイル形式を判定できませんでした")
    
    return True

def validate_numeric_range(value: Union[int, float], field_name: str, 
                          min_value: Optional[Union[int, float]] = None, 
                          max_value: Optional[Union[int, float]] = None) -> Union[int, float]:
    """数値範囲検証"""
    if not isinstance(value, (int, float)):
        raise ValidationError(f"{field_name}は数値である必要があります")
    
    if min_value is not None and value < min_value:
        raise ValidationError(f"{field_name}は{min_value}以上である必要があります")
    
    if max_value is not None and value > max_value:
        raise ValidationError(f"{field_name}は{max_value}以下である必要があります")
    
    return value

def validate_price(price: Union[int, float]) -> float:
    """価格検証"""
    price = validate_numeric_range(price, "価格", 0, 999999)
    
    # 小数点以下2桁まで丸める
    return round(float(price), 2)

def validate_duration(duration: int) -> int:
    """再生時間検証（秒）"""
    return int(validate_numeric_range(duration, "再生時間", 1, 7200))  # 1秒〜2時間

def validate_search_query(query: str) -> str:
    """検索クエリ検証"""
    if not query:
        return ""
    
    query = sanitize_string(query, "検索クエリ", MAX_SEARCH_LENGTH)
    
    # 検索文字列の最小長検証
    if len(query.strip()) < 1:
        return ""
    
    return query

def validate_track_title(title: str) -> str:
    """楽曲名検証"""
    return sanitize_string(title, "楽曲名", MAX_TITLE_LENGTH)

def validate_track_description(description: str) -> str:
    """楽曲説明検証"""
    if not description:
        return ""
    
    return sanitize_string(description, "楽曲説明", MAX_DESCRIPTION_LENGTH)

def validate_user_display_name(display_name: str) -> str:
    """ユーザー表示名検証"""
    display_name = sanitize_string(display_name, "表示名", 50)
    
    if len(display_name.strip()) < 1:
        raise ValidationError("表示名は1文字以上である必要があります")
    
    return display_name

def calculate_file_hash(file: UploadFile) -> str:
    """ファイルのSHA256ハッシュ値を計算（重複検出に使用）"""
    hasher = hashlib.sha256()
    
    file.file.seek(0)
    while chunk := file.file.read(8192):
        hasher.update(chunk)
    file.file.seek(0)
    
    return hasher.hexdigest()

def validate_pagination_params(skip: int = 0, limit: int = 100) -> tuple[int, int]:
    """ページネーションパラメータ検証"""
    skip = validate_numeric_range(skip, "skip", 0, 100000)
    limit = validate_numeric_range(limit, "limit", 1, 100)
    
    return int(skip), int(limit)

# ==================== 楽曲関連の複合検証 ====================

def validate_track_data(title: str, description: Optional[str], genre: str, 
                       duration: int, price: Union[int, float]) -> Dict[str, Any]:
    """楽曲データの複合検証"""
    validated_data = {
        "title": validate_track_title(title),
        "description": validate_track_description(description or ""),
        "genre": sanitize_string(genre, "ジャンル", 50),
        "duration": validate_duration(duration),
        "price": validate_price(price)
    }
    
    return validated_data

def validate_audio_upload(file: UploadFile) -> Dict[str, Any]:
    """音声ファイルアップロードの複合検証"""
    validate_file_content(file, "audio")
    
    return {
        "filename": validate_filename(file.filename, "audio"),
        "size": file.size if hasattr(file, 'size') else 0,
        "content_type": file.content_type,
        "file_hash": calculate_file_hash(file)
    }

def validate_image_upload(file: UploadFile) -> Dict[str, Any]:
    """画像ファイルアップロードの複合検証"""
    validate_file_content(file, "image")
    
    return {
        "filename": validate_filename(file.filename, "image"),
        "size": file.size if hasattr(file, 'size') else 0,
        "content_type": file.content_type,
        "file_hash": calculate_file_hash(file)
    }

# ==================== セキュリティログ ====================

def log_security_event(event_type: str, details: Dict[str, Any], user_id: Optional[str] = None):
    """セキュリティイベントをログに記録"""
    log_data = {
        "event_type": event_type,
        "user_id": user_id,
        "details": details,
        "timestamp": __import__("datetime").datetime.utcnow().isoformat()
    }
    
    logger.warning(f"Security Event: {event_type}", extra=log_data)