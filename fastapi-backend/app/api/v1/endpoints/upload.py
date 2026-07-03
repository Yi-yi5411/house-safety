"""File upload API endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile, status

from app.api.deps import get_current_user
from app.core.exceptions import AppException
from app.models.user import User
from app.schemas.common import UploadResponse
from app.utils.oss import generate_object_key, upload_file

router = APIRouter()

MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB

ALLOWED_CONTENT_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


@router.post(
    "/image",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_image(
    file: UploadFile,
    current_user: Annotated[User, Depends(get_current_user)],
) -> UploadResponse:
    """Upload an image file to Aliyun OSS."""
    if file.content_type not in ALLOWED_CONTENT_TYPES:
        raise AppException(
            detail=f"Unsupported content type: {file.content_type}",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise AppException(
            detail=f"File size exceeds {MAX_FILE_SIZE / 1024 / 1024} MB limit",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    object_key = generate_object_key(file.filename or "upload")
    file_url = await upload_file(
        content, object_key, content_type=file.content_type
    )

    return UploadResponse(
        file_url=file_url,
        file_name=file.filename or "upload",
        file_size=len(content),
    )


@router.post(
    "/file",
    response_model=UploadResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_file_endpoint(
    file: UploadFile,
    current_user: Annotated[User, Depends(get_current_user)],
) -> UploadResponse:
    """Upload any file to Aliyun OSS."""
    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise AppException(
            detail=f"File size exceeds {MAX_FILE_SIZE / 1024 / 1024} MB limit",
            status_code=status.HTTP_400_BAD_REQUEST,
        )

    object_key = generate_object_key(file.filename or "upload")
    file_url = await upload_file(
        content,
        object_key,
        content_type=file.content_type or "application/octet-stream",
    )

    return UploadResponse(
        file_url=file_url,
        file_name=file.filename or "upload",
        file_size=len(content),
    )
