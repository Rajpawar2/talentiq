import logging
import smtplib
import socket
from abc import ABC, abstractmethod
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Dict, Any, Optional

from app.config import settings

logger = logging.getLogger("talentiq.email")


class EmailDeliveryError(Exception):
    """Raised when email delivery fails with a descriptive, user-actionable message."""
    pass


class BaseEmailProvider(ABC):
    """Abstract Base Class for email providers (SMTP, Mock, SendGrid, etc.)."""

    @abstractmethod
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: str,
    ) -> bool:
        """Send an email to a single recipient."""
        pass


class SMTPEmailProvider(BaseEmailProvider):
    """Production-ready SMTP email provider with detailed diagnostics."""

    def __init__(
        self,
        host: Optional[str] = None,
        port: Optional[int] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        from_email: Optional[str] = None,
        from_name: Optional[str] = None,
        use_tls: Optional[bool] = None,
    ):
        self.host = (host or settings.SMTP_HOST).strip()
        self.port = port or settings.SMTP_PORT
        self.username = (username or settings.SMTP_USERNAME).strip()
        self.password = password or settings.SMTP_PASSWORD
        self.from_email = (from_email or settings.EMAIL_FROM).strip()
        self.from_name = (from_name or settings.EMAIL_FROM_NAME).strip()
        self.use_tls = use_tls if use_tls is not None else settings.SMTP_USE_TLS

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: str,
    ) -> bool:
        if not self.host:
            logger.error("[SMTP ERROR] SMTP_HOST is not configured in environment variables.")
            raise EmailDeliveryError("SMTP_HOST is not configured. Please set SMTP_HOST or enable EMAIL_MOCK_MODE=true for local testing.")

        if not self.from_email:
            logger.error("[SMTP ERROR] EMAIL_FROM is not configured.")
            raise EmailDeliveryError("EMAIL_FROM sender address is not configured.")

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{self.from_name} <{self.from_email}>"
        msg["To"] = to_email

        # Attach plain text and HTML versions
        part1 = MIMEText(text_body, "plain", "utf-8")
        part2 = MIMEText(html_body, "html", "utf-8")
        msg.attach(part1)
        msg.attach(part2)

        logger.info("[SMTP] Connecting to %s:%s (TLS=%s, From=%s)...", self.host, self.port, self.use_tls, self.from_email)

        try:
            if self.port == 465:
                # SSL Direct Connection
                with smtplib.SMTP_SSL(self.host, self.port, timeout=15) as server:
                    if self.username and self.password:
                        server.login(self.username, self.password)
                    server.sendmail(self.from_email, [to_email], msg.as_string())
            else:
                # Standard SMTP + opportunistic/required STARTTLS
                with smtplib.SMTP(self.host, self.port, timeout=15) as server:
                    server.ehlo()
                    if self.use_tls:
                        if server.has_extn('STARTTLS'):
                            server.starttls()
                            server.ehlo()
                        else:
                            logger.warning("[SMTP] STARTTLS requested but server does not advertise extension. Proceeding in plain text.")
                    if self.username and self.password:
                        server.login(self.username, self.password)
                    server.sendmail(self.from_email, [to_email], msg.as_string())

            logger.info("[SMTP] Email successfully delivered to recipient: %s", to_email)
            return True

        except smtplib.SMTPAuthenticationError as exc:
            logger.error("[SMTP AUTH ERROR] Authentication failed for user '%s': %s", self.username, exc.smtp_error.decode(errors='replace') if hasattr(exc, 'smtp_error') else str(exc))
            raise EmailDeliveryError("SMTP authentication failed. Please verify your SMTP_USERNAME and SMTP_PASSWORD.") from exc

        except smtplib.SMTPRecipientsRefused as exc:
            logger.error("[SMTP RECIPIENT ERROR] Recipient '%s' refused: %s", to_email, str(exc))
            raise EmailDeliveryError(f"Recipient address '{to_email}' was rejected by SMTP server.") from exc

        except smtplib.SMTPConnectError as exc:
            logger.error("[SMTP CONNECT ERROR] Could not connect to %s:%s: %s", self.host, self.port, str(exc))
            raise EmailDeliveryError(f"Could not connect to SMTP server at {self.host}:{self.port}.") from exc

        except (socket.timeout, TimeoutError) as exc:
            logger.error("[SMTP TIMEOUT] Connection to %s:%s timed out.", self.host, self.port)
            raise EmailDeliveryError(f"Connection to SMTP server at {self.host}:{self.port} timed out.") from exc

        except Exception as exc:
            logger.error("[SMTP UNEXPECTED ERROR] Failed to send email to %s: %s", to_email, str(exc))
            raise EmailDeliveryError(f"SMTP email delivery failed: {str(exc)}") from exc


class MockEmailProvider(BaseEmailProvider):
    """
    Development & Testing Mock Provider.
    Does not make network calls. Stores sent messages in memory.
    """

    def __init__(self):
        self.sent_messages: List[Dict[str, Any]] = []

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: str,
    ) -> bool:
        message_data = {
            "to": to_email,
            "subject": subject,
            "html_body": html_body,
            "text_body": text_body,
        }
        self.sent_messages.append(message_data)
        return True

    def clear(self):
        """Clears test message history."""
        self.sent_messages.clear()


class EmailService:
    """
    High-level Email Service for TalentIQ.
    Manages templating, provider selection, and transactional delivery for candidate lifecycle.
    """

    def __init__(self, provider: Optional[BaseEmailProvider] = None):
        self._custom_provider = provider

    @property
    def provider(self) -> BaseEmailProvider:
        if self._custom_provider:
            return self._custom_provider
        if settings.EMAIL_MOCK_MODE or settings.EMAIL_PROVIDER.lower() == "mock":
            if not hasattr(self, "_mock_provider"):
                self._mock_provider = MockEmailProvider()
            return self._mock_provider
        return SMTPEmailProvider()

    @provider.setter
    def provider(self, new_provider: Optional[BaseEmailProvider]):
        self._custom_provider = new_provider

    def send_password_reset_token(self, to_email: str, user_name: str, reset_token: str) -> bool:
        """
        Architecture hook for future Forgot Password flow.
        """
        clean_email = to_email.strip().lower()
        subject = "Reset your TalentIQ password"
        clean_name = user_name.strip() if user_name else "User"

        text_body = f"""TalentIQ Password Reset

Hello {clean_name},

A password reset was requested for your account. Use the following code to proceed:

{reset_token}

This code expires in 15 minutes. If you did not make this request, you can safely ignore this message.
"""
        html_body = f"""<p>Hello {clean_name},</p><p>Use code <strong>{reset_token}</strong> to reset your password.</p>"""

        return self.provider.send_email(
            to_email=clean_email,
            subject=subject,
            html_body=html_body,
            text_body=text_body,
        )


# Global singleton instance
email_service = EmailService()
