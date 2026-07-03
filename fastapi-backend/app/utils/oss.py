"""Aliyun OSS file upload utility."""

from __future__ import annotations

import uuid

import oss2
from loguru import logger

from app.core.config import get_settings

_bucket: oss2.Bucket | None = None


def _get_bucket() -> oss2.Bucket:
    """Return a singleton OSS Bucket instance."""
    global _bucket
    if _bucket is None:
        settings = get_settings()
        auth = oss2.Auth(
            settings.oss_access_key_id, settings.oss_access_key_secret
        )
        _bucket = oss2.Bucket(
            auth,
            f"https://{settings.oss_endpoint}",
            settings.oss_bucket_name,
        )
    return _bucket


def generate_object_key(original_filename: str) -> str:
    """Generate a unique OSS object key from the original filename."""
    ext = original_filename.rsplit(".", 1)[-1] if "." in original_filename else ""
    unique_name = f"{uuid.uuid4().hex}.{ext}" if ext else uuid.uuid4().hex
    return f"uploads/{unique_name}"


async def upload_file(
    file_bytes: bytes,
    object_key: str,
    content_type: str = "application/octet-stream",
) -> str:
    """Upload bytes to Aliyun OSS and return the public URL.

    Args:
        file_bytes: Raw file content.
        object_key: OSS object key (path within bucket).
        content_type: MIME type of the file.

    Returns:
        Public URL of the uploaded file.
    """
    bucket = _get_bucket()
    settings = get_settings()

    headers = {"Content-Type": content_type}
    try:
        bucket.put_object(object_key, file_bytes, headers=headers)
        url = f"https://{settings.oss_bucket_name}.{settings.oss_endpoint}/{object_key}"
        logger.info(f"File uploaded to OSS: {url}")
        return url
    except oss2.exceptions.OssError as exc:
        logger.error(f"OSS upload failed for {object_key}: {exc}")
        raise


async def upload_file_from_path(
    file_path: str,
    object_key: str,
    content_type: str = "application/octet-stream",
) -> str:
    """Upload a local file to Aliyun OSS and return the public URL."""
    bucket = _get_bucket()
    settings = get_settings()

    headers = {"Content-Type": content_type}
    try:
        bucket.put_object_from_file(object_key, file_path, headers=headers)
        url = f"https://{settings.oss_bucket_name}.{settings.oss_endpoint}/{object_key}"
        logger.info(f"File uploaded to OSS from path: {url}")
        return url
    except oss2.exceptions.OssError as exc:
        logger.error(f"OSS upload failed for {object_key}: {exc}")
        raise


async def delete_file(object_key: str) -> bool:
    """Delete a file from Aliyun OSS."""
    bucket = _get_bucket()
    try:
        result = bucket.delete_object(object_key)
        logger.info(f"OSS file deleted: {object_key}, status={result.status}")
        return result.status == 204
    except oss2.exceptions.OssError as exc:
        logger.error(f"OSS delete failed for {object_key}: {exc}")
        raise
