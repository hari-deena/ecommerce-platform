import structlog

logger = structlog.get_logger(__name__)


async def send_email(*, to: str, subject: str, body: str) -> None:
    """Thin mail-sending port used by password reset / order notifications.

    TODO: wire to SMTP (aiosmtplib) or AWS SES using settings.SMTP_* /
    AWS credentials. Logging instead of raising keeps auth flows from failing
    hard during local development when no mail provider is configured.
    """
    logger.info("email_dispatch", to=to, subject=subject)
