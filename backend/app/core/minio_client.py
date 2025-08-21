"""MinIO client configuration"""
from __future__ import annotations

import boto3
from botocore.client import Config
from app.core.config import settings


def get_minio_client():
    """Create a MinIO/S3 client if configuration is provided"""
    if not settings.MINIO_ENDPOINT:
        return None
    return boto3.client(
        "s3",
        endpoint_url=settings.MINIO_ENDPOINT,
        aws_access_key_id=settings.MINIO_ACCESS_KEY,
        aws_secret_access_key=settings.MINIO_SECRET_KEY,
        region_name=settings.MINIO_REGION,
        config=Config(signature_version="s3v4"),
    )
