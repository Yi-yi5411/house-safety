"""Email sending utility using aiosmtplib."""

from __future__ import annotations

from email.mime.text import MIMEText

import aiosmtplib
from loguru import logger

from app.core.config import get_settings


async def send_email_code(email: str, code: str) -> None:
    """Send a verification code email via SMTP.

    Args:
        email: Recipient email address.
        code: 6-digit verification code.
    """
    settings = get_settings()

    subject = "房屋安全鉴定系统 - 验证码"
    body = (
        f"您好！\n\n"
        f"您的验证码是：{code}\n\n"
        f"该验证码 5 分钟内有效，请尽快完成验证。\n"
        f"如非本人操作，请忽略此邮件。\n\n"
        f"—— 房屋安全鉴定系统"
    )

    message = MIMEText(body, "plain", "utf-8")
    message["Subject"] = subject
    message["From"] = settings.smtp_user
    message["To"] = email

    try:
        smtp = aiosmtplib.SMTP(
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            use_tls=settings.smtp_tls,
        )
        await smtp.connect()
        await smtp.login(settings.smtp_user, settings.smtp_password)
        await smtp.send_message(message)
        await smtp.quit()
        logger.info(f"Verification email sent to {email}")
    except Exception as exc:
        logger.error(f"Email send failed for {email}: {exc}")
        raise
