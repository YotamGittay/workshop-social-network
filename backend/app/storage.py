import json
import os
import time
import uuid

import boto3
from botocore.client import Config

S3_ENDPOINT = os.getenv("S3_ENDPOINT", "http://blob:9000")
S3_ACCESS_KEY = os.getenv("S3_ACCESS_KEY", "minioadmin")
S3_SECRET_KEY = os.getenv("S3_SECRET_KEY", "minioadmin")
S3_BUCKET = os.getenv("S3_BUCKET", "images")

MAX_UPLOAD_BYTES = 5 * 1024 * 1024  # 5 MB
ALLOWED_TYPES = {
    "image/jpeg": ".jpg",
    "image/png": ".png",
    "image/gif": ".gif",
    "image/webp": ".webp",
}

s3 = boto3.client(
    "s3",
    endpoint_url=S3_ENDPOINT,
    aws_access_key_id=S3_ACCESS_KEY,
    aws_secret_access_key=S3_SECRET_KEY,
    config=Config(signature_version="s3v4"),
)


def ensure_bucket(retries: int = 30, delay: float = 1.0) -> None:
    """Create the bucket (if missing) and make it public-read. Retries while
    MinIO is still starting — compose only guarantees start order."""
    policy = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": "*",
                "Action": ["s3:GetObject"],
                "Resource": [f"arn:aws:s3:::{S3_BUCKET}/*"],
            }
        ],
    }
    for attempt in range(retries):
        try:
            existing = {b["Name"] for b in s3.list_buckets().get("Buckets", [])}
            if S3_BUCKET not in existing:
                s3.create_bucket(Bucket=S3_BUCKET)
            s3.put_bucket_policy(Bucket=S3_BUCKET, Policy=json.dumps(policy))
            return
        except Exception:
            if attempt == retries - 1:
                raise
            time.sleep(delay)


def upload_image(data: bytes, content_type: str) -> str:
    """Store image bytes in the bucket, return the object key."""
    key = f"{uuid.uuid4().hex}{ALLOWED_TYPES[content_type]}"
    s3.put_object(Bucket=S3_BUCKET, Key=key, Body=data, ContentType=content_type)
    return key
