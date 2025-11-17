"""
Email Service using Resend API
Handles sending emails for password reset, verification, etc.
"""
import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)

try:
    import resend
    RESEND_AVAILABLE = True
except ImportError:
    RESEND_AVAILABLE = False
    logger.warning("Resend package not installed. Email functionality will be disabled.")


class EmailService:
    """Email service for sending transactional emails"""

    def __init__(self):
        self.api_key = os.getenv('RESEND_API_KEY')
        self.from_email = os.getenv('FROM_EMAIL', 'noreply@yourdomain.com')

        if RESEND_AVAILABLE and self.api_key and self.api_key != 'your_resend_api_key_here':
            resend.api_key = self.api_key
            self.enabled = True
            logger.info("✅ Email service initialized")
        else:
            self.enabled = False
            logger.warning("⚠️  Email service disabled. Set RESEND_API_KEY to enable.")

    def send_password_reset_email(self, to_email: str, reset_link: str) -> bool:
        """
        Send password reset email

        Args:
            to_email: Recipient email address
            reset_link: Password reset link

        Returns:
            bool: True if sent successfully
        """
        if not self.enabled:
            logger.warning(f"Email service disabled. Would have sent password reset to {to_email}")
            logger.info(f"Reset link: {reset_link}")
            return False

        try:
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #4F46E5; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 30px; background: #f9fafb; }}
                    .button {{
                        display: inline-block;
                        padding: 12px 24px;
                        background: #4F46E5;
                        color: white;
                        text-decoration: none;
                        border-radius: 6px;
                        margin: 20px 0;
                    }}
                    .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🔐 Password Reset Request</h1>
                    </div>
                    <div class="content">
                        <p>Hi there,</p>
                        <p>We received a request to reset your password for your DocuMind Voice account.</p>
                        <p>Click the button below to reset your password:</p>
                        <div style="text-align: center;">
                            <a href="{reset_link}" class="button">Reset Password</a>
                        </div>
                        <p style="color: #6b7280; font-size: 14px;">
                            Or copy and paste this link into your browser:<br>
                            <code>{reset_link}</code>
                        </p>
                        <p><strong>This link will expire in 1 hour.</strong></p>
                        <p>If you didn't request a password reset, you can safely ignore this email.</p>
                    </div>
                    <div class="footer">
                        <p>DocuMind Voice - Voice-Enabled PDF Q&A</p>
                        <p>This is an automated email, please do not reply.</p>
                    </div>
                </div>
            </body>
            </html>
            """

            params = {
                "from": self.from_email,
                "to": [to_email],
                "subject": "Reset Your Password - DocuMind Voice",
                "html": html_content
            }

            response = resend.Emails.send(params)
            logger.info(f"✅ Password reset email sent to {to_email}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to send password reset email: {e}")
            return False

    def send_verification_email(self, to_email: str, verification_code: str) -> bool:
        """
        Send email verification code

        Args:
            to_email: Recipient email address
            verification_code: 6-digit verification code

        Returns:
            bool: True if sent successfully
        """
        if not self.enabled:
            logger.warning(f"Email service disabled. Would have sent verification code to {to_email}")
            logger.info(f"Verification code: {verification_code}")
            return False

        try:
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #4F46E5; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 30px; background: #f9fafb; }}
                    .code {{
                        font-size: 32px;
                        font-weight: bold;
                        letter-spacing: 8px;
                        text-align: center;
                        background: white;
                        padding: 20px;
                        margin: 20px 0;
                        border: 2px dashed #4F46E5;
                        border-radius: 8px;
                    }}
                    .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>✉️ Verify Your Email</h1>
                    </div>
                    <div class="content">
                        <p>Hi there,</p>
                        <p>Thank you for signing up for DocuMind Voice!</p>
                        <p>Enter this verification code to verify your email address:</p>
                        <div class="code">{verification_code}</div>
                        <p><strong>This code will expire in 24 hours.</strong></p>
                        <p>Verifying your email unlocks higher usage limits:</p>
                        <ul>
                            <li>10 documents (instead of 5)</li>
                            <li>100 queries per day (instead of 50)</li>
                        </ul>
                    </div>
                    <div class="footer">
                        <p>DocuMind Voice - Voice-Enabled PDF Q&A</p>
                        <p>This is an automated email, please do not reply.</p>
                    </div>
                </div>
            </body>
            </html>
            """

            params = {
                "from": self.from_email,
                "to": [to_email],
                "subject": "Verify Your Email - DocuMind Voice",
                "html": html_content
            }

            response = resend.Emails.send(params)
            logger.info(f"✅ Verification email sent to {to_email}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to send verification email: {e}")
            return False

    def send_welcome_email(self, to_email: str, name: str = None) -> bool:
        """
        Send welcome email to new users

        Args:
            to_email: Recipient email address
            name: User's name (optional)

        Returns:
            bool: True if sent successfully
        """
        if not self.enabled:
            return False

        try:
            greeting = f"Hi {name}," if name else "Hi there,"

            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #4F46E5; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 30px; background: #f9fafb; }}
                    .footer {{ text-align: center; padding: 20px; color: #6b7280; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎉 Welcome to DocuMind Voice!</h1>
                    </div>
                    <div class="content">
                        <p>{greeting}</p>
                        <p>Welcome to DocuMind Voice - your AI-powered PDF assistant with voice support!</p>
                        <h3>What you can do:</h3>
                        <ul>
                            <li>📄 Upload PDF documents</li>
                            <li>🎤 Ask questions using voice or text</li>
                            <li>🔊 Listen to AI responses</li>
                            <li>📊 Extract tables and images from PDFs</li>
                        </ul>
                        <p><strong>Your beta plan includes:</strong></p>
                        <ul>
                            <li>5 documents</li>
                            <li>50 queries per day</li>
                            <li>Full voice features</li>
                        </ul>
                        <p>💡 <strong>Tip:</strong> Verify your email to unlock 10 documents and 100 queries per day!</p>
                    </div>
                    <div class="footer">
                        <p>DocuMind Voice - Voice-Enabled PDF Q&A</p>
                        <p>Need help? Reply to this email or contact support.</p>
                    </div>
                </div>
            </body>
            </html>
            """

            params = {
                "from": self.from_email,
                "to": [to_email],
                "subject": "Welcome to DocuMind Voice! 🎉",
                "html": html_content
            }

            response = resend.Emails.send(params)
            logger.info(f"✅ Welcome email sent to {to_email}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to send welcome email: {e}")
            return False


# Singleton instance
_email_service = None


def get_email_service() -> EmailService:
    """Get or create email service instance"""
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
