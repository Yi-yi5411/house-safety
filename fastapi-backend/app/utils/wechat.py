"""WeChat login and user info utility."""

from __future__ import annotations

from typing import Any

import httpx
from loguru import logger

from app.core.config import get_settings

WECHAT_TOKEN_URL = "https://api.weixin.qq.com/sns/jscode2session"
WECHAT_ACCESS_TOKEN_URL = "https://api.weixin.qq.com/cgi-bin/token"
WECHAT_USERINFO_URL = "https://api.weixin.qq.com/sns/userinfo"


async def code_to_session(code: str) -> dict[str, Any]:
    """Exchange a WeChat Mini Program login code for session info.

    Returns dict containing openid, session_key, unionid (if available).

    In WeChat DevTools, uni.login() returns a mock code that cannot be
    verified by the real WeChat API.  When that happens we return a
    deterministic dev openid so login still works during development.
    """
    settings = get_settings()
    params = {
        "appid": settings.wechat_app_id,
        "secret": settings.wechat_app_secret,
        "js_code": code,
        "grant_type": "authorization_code",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(WECHAT_TOKEN_URL, params=params)
            result = response.json()
            if "errcode" in result and result["errcode"] != 0:
                errcode = result.get("errcode")
                errmsg = result.get("errmsg", "unknown")
                logger.warning(f"WeChat code2session error: {result}")

                # DevTools mock code – generate a deterministic dev openid
                if errcode in (40029, 40125, -1):
                    logger.info("Using dev openid for WeChat DevTools mock code")
                    return {
                        "openid": f"dev_{code[:16]}",
                        "session_key": "dev_session_key",
                    }

                from fastapi import HTTPException

                raise HTTPException(
                    status_code=502,
                    detail=f"WeChat login failed: {errmsg} (errcode: {errcode})",
                )
            logger.info(f"WeChat session obtained for openid={result.get('openid')}")
            return result
    except httpx.HTTPError as exc:
        logger.error(f"WeChat code2session HTTP error: {exc}")
        raise


async def get_access_token() -> str:
    """Obtain a WeChat server access_token."""
    settings = get_settings()
    params = {
        "grant_type": "client_credential",
        "appid": settings.wechat_app_id,
        "secret": settings.wechat_app_secret,
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(WECHAT_ACCESS_TOKEN_URL, params=params)
            result = response.json()
            if "access_token" not in result:
                raise ValueError(
                    f"Failed to get access_token: {result.get('errmsg', 'unknown')}"
                )
            return result["access_token"]
    except httpx.HTTPError as exc:
        logger.error(f"WeChat access_token HTTP error: {exc}")
        raise


async def get_user_info(
    access_token: str, openid: str
) -> dict[str, Any]:
    """Fetch WeChat user profile info."""
    params = {
        "access_token": access_token,
        "openid": openid,
        "lang": "zh_CN",
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(WECHAT_USERINFO_URL, params=params)
            return response.json()
    except httpx.HTTPError as exc:
        logger.error(f"WeChat userinfo HTTP error: {exc}")
        raise
