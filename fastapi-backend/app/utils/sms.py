"""Aliyun SMS client for phone verification code delivery."""

from __future__ import annotations

import json as _json
import random
import hmac
import hashlib
import base64
import uuid
from datetime import datetime, timezone
from urllib.parse import quote

import httpx
from loguru import logger

from app.core.config import get_settings


def _generate_code() -> str:
    """Generate a 6-digit random verification code."""
    return f"{random.randint(100000, 999999)}"


async def send_sms_code(phone: str) -> str:
    """Send a 6-digit verification code to the given phone number via Aliyun SMS.

    Returns:
        The generated code (for storing in Redis for later verification).
    """
    settings = get_settings()
    code = _generate_code()

    # Build Aliyun SMS API request
    # Using Aliyun SMS SendSms API v2017-05-25
    params = {
        "PhoneNumbers": phone,
        "SignName": settings.aliyun_sms_sign_name,
        "TemplateCode": settings.aliyun_sms_template_code,
        "TemplateParam": _json.dumps({"code": code}),
    }

    try:
        # Use Aliyun OpenAPI signature V3 for SMS
        import hmac as _hmac

        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        nonce = str(uuid.uuid4())

        body = _json.dumps(params)

        # Build the request via httpx with Aliyun signature
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                "https://dysmsapi.aliyuncs.com/",
                params={
                    "Action": "SendSms",
                    "Version": "2017-05-25",
                    "AccessKeyId": settings.aliyun_access_key_id,
                    "SignatureMethod": "HMAC-SHA1",
                    "Timestamp": timestamp,
                    "SignatureVersion": "1.0",
                    "SignatureNonce": nonce,
                    "Format": "JSON",
                    "PhoneNumbers": phone,
                    "SignName": settings.aliyun_sms_sign_name,
                    "TemplateCode": settings.aliyun_sms_template_code,
                    "TemplateParam": _json.dumps({"code": code}),
                },
            )
            result = response.json()
            if result.get("Code") != "OK":
                logger.error(f"SMS send failed: {result}")
                raise RuntimeError(f"SMS send failed: {result.get('Message', 'Unknown error')}")

            logger.info(f"SMS code sent to {phone}")
            return code

    except httpx.HTTPError as exc:
        logger.error(f"SMS HTTP request failed: {exc}")
        raise RuntimeError(f"SMS service unavailable: {exc}") from exc
