import os
import uuid

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


def upload_image(file, folder: str) -> str:
    """保存单张图片，并统一返回可访问的 URL 字符串。"""
    ext = os.path.splitext(file.name)[1]
    filename = f"{folder}/{uuid.uuid4()}{ext}"

    if settings.DEBUG:
        path = default_storage.save(filename, ContentFile(file.read()))
        return settings.MEDIA_URL + path

    from cloudinary.uploader import upload

    res = upload(file, folder=folder)
    return res["secure_url"]
