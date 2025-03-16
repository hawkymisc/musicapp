import boto3
import os
from fastapi import UploadFile, HTTPException
from botocore.exceptions import ClientError
from starlette.status import HTTP_500_INTERNAL_SERVER_ERROR
from datetime import datetime, timedelta
import uuid


# S3クライアントの初期化
s3_client = boto3.client(
    's3',
    aws_access_key_id=os.environ.get("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.environ.get("AWS_SECRET_ACCESS_KEY"),
    region_name=os.environ.get("AWS_REGION")
)

BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")


async def upload_file_to_s3(file: UploadFile, object_name: str) -> str:
    """
    ファイルをS3にアップロード
    """
    try:
        # Streamからファイルデータを読み込む
        file_data = await file.read()
        
        # S3にアップロード
        s3_client.put_object(
            Bucket=BUCKET_NAME,
            Key=object_name,
            Body=file_data,
            ContentType=file.content_type
        )
        
        # アップロードしたファイルのURLを返す
        url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{object_name}"
        return url
    
    except ClientError as e:
        # S3アップロードエラー
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ファイルのアップロードに失敗しました: {str(e)}"
        )
    except Exception as e:
        # その他のエラー
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"エラーが発生しました: {str(e)}"
        )


def generate_presigned_url(object_name: str, expiration: int = 3600) -> str:
    """
    S3の署名付きURLを生成
    """
    try:
        response = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': BUCKET_NAME,
                'Key': object_name
            },
            ExpiresIn=expiration
        )
        return response
    except ClientError as e:
        raise HTTPException(
            status_code=HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"署名付きURLの生成に失敗しました: {str(e)}"
        )


