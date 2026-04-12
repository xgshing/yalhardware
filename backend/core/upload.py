import os
import uuid

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from qcloud_cos import CosConfig, CosS3Client


def upload_image(file, folder: str) -> str:
    """Save one image and return a URL that the frontend can use directly."""
    ext = os.path.splitext(file.name)[1]
    key = f"{folder}/{uuid.uuid4()}{ext}"

    if settings.DEBUG:
        path = default_storage.save(key, ContentFile(file.read()))
        return settings.MEDIA_URL + path

    required_settings = [
        "COS_SECRET_ID",
        "COS_SECRET_KEY",
        "COS_REGION",
        "COS_BUCKET",
        "COS_BASE_URL",
    ]
    missing = [name for name in required_settings if not getattr(settings, name, None)]
    if missing:
        raise RuntimeError(f"Missing COS settings: {', '.join(missing)}")

    config = CosConfig(
        Region=settings.COS_REGION,
        SecretId=settings.COS_SECRET_ID,
        SecretKey=settings.COS_SECRET_KEY,
    )
    client = CosS3Client(config)

    file.seek(0)
    client.put_object(
        Bucket=settings.COS_BUCKET,
        Body=file.read(),
        Key=key,
    )
    return f"{settings.COS_BASE_URL.rstrip('/')}/{key}"
