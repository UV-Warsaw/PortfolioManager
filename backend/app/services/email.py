"""Email service for sending transactional messages via SMTP.

If SMTP is not configured (smtp_host is None), the verification code is logged
at WARNING level so developers can complete the flow locally without a real
mail server.
"""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from ..core.config import settings

logger = logging.getLogger(__name__)


def send_password_reset_code(email: str, code: str) -> None:
    """
    Send a 6-digit password-reset verification code to the given address.

    If SMTP credentials are not configured, logs the code at WARNING level
    so local development flows remain functional without a mail server.

    Args:
        email: Recipient email address.
        code: 6-digit verification code to send.
    """
    if not settings.smtp_host:
        logger.warning(
            "SMTP not configured - password reset code for %s: %s",
            email,
            code,
        )
        return

    subject = "Your Portfolio Manager verification code"
    body_text = (
        f"You requested a password reset.\n\n"
        f"Your verification code is: {code}\n\n"
        f"It expires in {settings.password_reset_expire_hours} hour(s).\n\n"
        f"If you did not request this, ignore this message."
    )
    body_html = f"""
<html>
  <body>
    <p>You requested a password reset.</p>
    <p>Your verification code is:</p>
    <p style="font-size:2em;letter-spacing:0.2em;font-weight:bold">{code}</p>
    <p>It expires in <strong>{settings.password_reset_expire_hours} hour(s)</strong>.</p>
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

    logger.info("Password reset code sent to %s", email)
