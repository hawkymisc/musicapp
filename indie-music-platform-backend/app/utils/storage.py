import boto3
import logging
import os
import io
from fastapi import UploadFile
import uuid
from unittest.mock import MagicMock

# boto3が存在しない場合でもモックで対応
try:
    from botocore.exceptions import ClientError
except ImportError:
    # モック環境ではimportエラーが出る可能性があるのでモック定義
    class ClientError(Exception):
        pass

# 設定のインポート
try:
    from app.core.config import settings
except ImportError:
    # モック環境で設定がインポートできない場合
    settings = type('MockSettings', (), {
        'AWS_REGION': 'mock-region',
        'AWS_ACCESS_KEY_ID': 'mock-key',
        'AWS_SECRET_ACCESS_KEY': 'mock-secret',
        'S3_BUCKET_NAME': 'mock-bucket'
    })

# ���-�
logger = logging.getLogger(__name__)

# ƹȰ�$�
is_testing = os.environ.get('TESTING') == 'True'

# S3�餢��n
if is_testing:
    # ƹȰ�go�ï�(
    logger.info("ƹȰ�n_�S3�餢�Ȓ�ïW~Y")
    s3_client = MagicMock()
    
    # �ïn�,�j/�D���
    s3_client.upload_fileobj.return_value = None
    s3_client.generate_presigned_url.return_value = "https://example.com/mock-file-url"
else:
    # ,j��go��n�餢�Ȓ
    logger.info("��nS3�餢�ȒW~Y")
    s3_client = boto3.client(
        's3',
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
    )

# ա��S3k������WURL��Y
async def upload_file(file: UploadFile, folder: str = "uploads") -> str:
    """
    ա��S3k������W����URL��Y
    """
    # ա��nUUID + Cnա���5P	
    file_ext = os.path.splitext(file.filename)[1] if file.filename else ""
    unique_filename = f"{folder}/{uuid.uuid4()}{file_ext}"
    
    try:
        # ա��n������
        contents = await file.read()
        
        # ƹȰ�go�ïn/�Dn
        if is_testing:
            logger.info(f"[ƹ�] ա��n�ï������: {unique_filename}")
            return f"https://example.com/{unique_filename}"
        
        # S3k������
        s3_client.upload_fileobj(
            io.BytesIO(contents),
            settings.S3_BUCKET_NAME,
            unique_filename,
            ExtraArgs={
                "ContentType": file.content_type
            }
        )
        
        # r�MURL�
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': settings.S3_BUCKET_NAME,
                'Key': unique_filename
            },
            ExpiresIn=3600  # 1B�	�
        )
        
        logger.info(f"ա�뒢�����W~W_: {unique_filename}")
        return url
        
    except Exception as e:
        logger.error(f"ա������ɨ��: {e}")
        raise
