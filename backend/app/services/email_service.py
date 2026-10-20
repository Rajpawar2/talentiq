import logging
import smtplib
from abc import ABC, abstractmethod
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import List, Dict, Any, Optional

from app.config import settings

logger = logging.getLogger(__name__)


class EmailDeliveryError(Exception):
    """Raised when email delivery fails."""
    pass


class BaseEmailProvider(ABC):
    """Abstract Base Class for email providers (SMTP, SendGrid, SES, Mock, etc.)."""

    @abstractmethod
    def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: str
    ) -> bool:
        """Send an email to a single recipient."""
        pass


class SMTPEmailProvider(BaseEmailProvider):
    """Production-ready SMTP email provider with TLS/SSL support."""

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
        self.host = host or settings.SMTP_HOST
        self.port = port or settings.SMTP_PORT
        self.username = username or settings.SMTP_USERNAME
        self.password = password or settings.SMTP_PASSWORD
        self.from_email = from_email or settings.EMAIL_FROM
        self.from_name = from_name or settings.EMAIL_FROM_NAME
        self.use_tls = use_tls if use_tls is not None else settings.SMTP_USE_TLS

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: str
    ) -> bool:
        if not self.host:
            raise EmailDeliveryError("SMTP_HOST is not configured.")

        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = f"{self.from_name} <{self.from_email}>"
        msg["To"] = to_email

        # Attach plain text then HTML version
        part1 = MIMEText(text_body, "plain", "utf-8")
        part2 = MIMEText(html_body, "html", "utf-8")
        msg.attach(part1)
        msg.attach(part2)

        try:
            if self.port == 465:
                # SSL Direct
                with smtplib.SMTP_SSL(self.host, self.port, timeout=15) as server:
                    if self.username and self.password:
                        server.login(self.username, self.password)
                    server.sendmail(self.from_email, [to_email], msg.as_string())
            else:
                # Standard SMTP + STARTTLS
                with smtplib.SMTP(self.host, self.port, timeout=15) as server:
                    if self.use_tls:
                        server.starttls()
                    if self.username and self.password:
                        server.login(self.username, self.password)
                    server.sendmail(self.from_email, [to_email], msg.as_string())

            logger.info("Email successfully sent via SMTP to recipient: %s", to_email)
            return True
        except Exception as exc:
            logger.error("Failed to send SMTP email to %s: %s", to_email, str(exc))
            raise EmailDeliveryError(f"SMTP delivery failed: {str(exc)}") from exc


class MockEmailProvider(BaseEmailProvider):
    """
    Development & Testing Mock Provider.
    Does not make network calls. Stores sent messages in memory for test assertions.
    """

    def __init__(self):
        self.sent_messages: List[Dict[str, Any]] = []

    def send_email(
        self,
        to_email: str,
        subject: str,
        html_body: str,
        text_body: str
    ) -> bool:
        message_data = {
            "to": to_email,
            "subject": subject,
            "html_body": html_body,
            "text_body": text_body,
        }
        self.sent_messages.append(message_data)
        logger.info(
            "[MOCK EMAIL] Delivered to: %s | Subject: '%s' (Mock mode active)",
            to_email,
            subject
        )
        return True

    def clear(self):
        """Clears test message history."""
        self.sent_messages.clear()


class EmailService:
    """
    High-level Email Service for TalentIQ.
    Manages templating, provider selection, and delivery for verification & account lifecycle.
    """

    def __init__(self, provider: Optional[BaseEmailProvider] = None):
        if provider:
            self.provider = provider
        elif settings.EMAIL_MOCK_MODE or settings.EMAIL_PROVIDER.lower() == "mock":
            self.provider = MockEmailProvider()
        else:
            self.provider = SMTPEmailProvider()

    def send_verification_otp(self, to_email: str, user_name: str, otp: str) -> bool:
        """
        Sends the 6-digit registration OTP in a professional TalentIQ branded email.
        """
        subject = f"{otp} is your TalentIQ verification code"
        clean_name = user_name.strip() if user_name else "Candidate"

        html_body = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Verify your TalentIQ email</title>
</head>
<body style="margin: 0; padding: 0; background-color: #020617; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; color: #f8fafc;">
  <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0" style="background-color: #020617; padding: 40px 20px;">
    <tr>
      <td align="center">
        <!-- Main Card Container -->
        <table role="presentation" width="100%" style="max-width: 520px; background-color: #0f172a; border: 1px solid #1e293b; border-radius: 16px; overflow: hidden; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);" cellspacing="0" cellpadding="0" border="0">
          <!-- Header Bar -->
          <tr>
            <td style="background: linear-gradient(135deg, #0284c7 0%, #38bdf8 100%); height: 4px;"></td>
          </tr>
          
          <!-- Logo & Branding -->
          <tr>
            <td style="padding: 36px 36px 20px 36px; text-align: center;">
              <div style="display: inline-block; background-color: #ffffff; padding: 8px 18px; border-radius: 10px;">
                <span style="font-size: 20px; font-weight: 800; color: #0284c7; letter-spacing: -0.5px;">Talent<span style="color: #0f172a;">IQ</span></span>
              </div>
              <h1 style="margin: 24px 0 8px 0; font-size: 24px; font-weight: 700; color: #ffffff; letter-spacing: -0.5px;">
                Verify your email address
              </h1>
              <p style="margin: 0; font-size: 14px; color: #94a3b8; line-height: 1.5;">
                Hello {clean_name}, thank you for joining TalentIQ. Use the verification code below to complete your registration.
              </p>
            </td>
          </tr>

          <!-- OTP Code Box -->
          <tr>
            <td style="padding: 10px 36px 24px 36px;" align="center">
              <table role="presentation" cellspacing="0" cellpadding="0" border="0" style="margin: 0 auto;">
                <tr>
                  <td style="background-color: #020617; border: 1px solid #38bdf8; border-radius: 12px; padding: 18px 36px; text-align: center;">
                    <span style="font-family: 'SFMono-Regular', Consolas, 'Liberation Mono', Menlo, Courier, monospace; font-size: 36px; font-weight: 800; letter-spacing: 10px; color: #38bdf8; display: inline-block; padding-left: 10px;">
                      {otp}
                    </span>
                  </td>
                </tr>
              </table>
              <p style="margin: 16px 0 0 0; font-size: 13px; font-weight: 500; color: #cbd5e1;">
                ⏱ This code expires in <span style="color: #38bdf8; font-weight: 600;">{settings.OTP_EXPIRE_MINUTES} minutes</span>.
              </p>
            </td>
          </tr>

          <!-- Security Notice -->
          <tr>
            <td style="padding: 0 36px 36px 36px;">
              <div style="background-color: #1e293b; border-left: 3px solid #64748b; border-radius: 6px; padding: 12px 16px;">
                <p style="margin: 0; font-size: 12px; color: #94a3b8; line-height: 1.5;">
                  <strong>Security notice:</strong> If you did not create an account on TalentIQ, you can safely ignore this email. Never share this code with anyone. TalentIQ will never ask for your code over the phone or email.
                </p>
              </div>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="background-color: #090d16; padding: 20px 36px; border-top: 1px solid #1e293b; text-align: center;">
              <p style="margin: 0; font-size: 11px; color: #64748b;">
                © 2026 TalentIQ Inc. Autonomous AI Interview Simulation & Evaluation.
              </p>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</body>
</html>"""

        text_body = f"""TalentIQ Email Verification

Hello {clean_name},

Use the 6-digit verification code below to complete your registration:

{otp}

This code expires in {settings.OTP_EXPIRE_MINUTES} minutes.

Security Notice:
If you did not request this verification code, please disregard this email. Never share this code with anyone.

© 2026 TalentIQ Inc.
"""

        return self.provider.send_email(
            to_email=to_email,
            subject=subject,
            html_body=html_body,
            text_body=text_body
        )

    def send_password_reset_token(self, to_email: str, user_name: str, reset_token: str) -> bool:
        """
        Architecture hook for future Forgot Password flow.
        Kept separate from registration OTPs.
        """
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
            to_email=to_email,
            subject=subject,
            html_body=html_body,
            text_body=text_body
        )


# Global singleton instance
email_service = EmailService()
