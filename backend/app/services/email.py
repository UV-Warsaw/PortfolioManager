"""Email service for sending transactional messages via SMTP.

If SMTP is not configured (smtp_host is None), the reset URL is logged at
WARNING level so developers can complete the flow locally without a real mail
server.
"""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from ..core.config import settings

logger = logging.getLogger(__name__)


def send_password_reset_email(email: str, reset_url: str) -> None:
    """
    Send a password-reset email to the given address.

    If SMTP credentials are not configured, logs the reset URL at WARNING
    level so local development flows remain functional without a mail server.

    Args:
        email: Recipient email address.
        reset_url: Full URL the user must visit to complete the reset.
    """
    if not settings.smtp_host:
        logger.warning(
            "SMTP not configured — password reset URL for %s: %s",
            email,
            reset_url,
        )
        return

    subject = "Reset your Portfolio Manager password"
    body_text = (
        f"You requested a password reset.\n\n"
        f"Click the link below to set a new password. "
        f"The link expires in {settings.password_reset_expire_hours} hour(s).\n\n"
        f"{reset_url}\n\n"
        f"If you did not request this, ignore this message."
    )
    body_html = f"""
<html>
  <body>
    <p>You requested a password reset.</p>
    <p>
      Click the link below to set a new password.
      The link expires in <strong>{settings.password_reset_expire_hours} hour(s)</strong>.
    </p>
    <p><a href="{reset_url}">{reset_url}</a></p>
    <p>If you did not request this, ignore this message.</p>
  </body>
</html>
"""

    message = MIMEMultipart("alternative")
    message["Subject"] = subject
    message["From"] = settings.smtp_from
    message["To"] = email
    message.attach(MIMEText(body_text, "plain"))
    message.attach(MIMEText(body_html, "html"))

    with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
        server.ehlo()
        server.starttls()
        if settings.smtp_user and settings.smtp_password:
            server.login(settings.smtp_user, settings.smtp_password)
        server.sendmail(settings.smtp_from, email, message.as_string())

    logger.info("Password reset email sent to %s", email)
