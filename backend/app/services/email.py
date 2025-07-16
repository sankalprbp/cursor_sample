"""
Email Service
Handles sending emails for authentication, notifications, and alerts
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, List
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


class EmailService:
    """Email service for sending various types of emails"""
    
    def __init__(self):
        self.smtp_server = getattr(settings, 'SMTP_SERVER', 'localhost')
        self.smtp_port = getattr(settings, 'SMTP_PORT', 587)
        self.smtp_username = getattr(settings, 'SMTP_USERNAME', '')
        self.smtp_password = getattr(settings, 'SMTP_PASSWORD', '')
        self.from_email = getattr(settings, 'FROM_EMAIL', 'noreply@voiceagent.com')
        self.frontend_url = getattr(settings, 'FRONTEND_URL', 'http://localhost:3000')
    
    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Send an email
        
        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML content of the email
            text_content: Plain text content (optional)
        
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = to_email
            
            # Add text content
            if text_content:
                text_part = MIMEText(text_content, 'plain')
                msg.attach(text_part)
            
            # Add HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            if self.smtp_username and self.smtp_password:
                # Use SMTP authentication
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.starttls()
                    server.login(self.smtp_username, self.smtp_password)
                    server.send_message(msg)
            else:
                # Local SMTP server (development)
                with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                    server.send_message(msg)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {str(e)}")
            return False
    
    async def send_verification_email(self, email: str, token: str, username: str) -> bool:
        """Send email verification email"""
        verification_url = f"{self.frontend_url}/verify-email?token={token}"
        
        subject = "Verify Your Email Address"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .button {{ 
                    display: inline-block; 
                    padding: 12px 24px; 
                    background-color: #4CAF50; 
                    color: white; 
                    text-decoration: none; 
                    border-radius: 5px; 
                    margin: 20px 0;
                }}
                .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to Voice Agent Platform!</h1>
                </div>
                <div class="content">
                    <h2>Hello {username},</h2>
                    <p>Thank you for registering with our Voice Agent Platform. To complete your registration, please verify your email address by clicking the button below:</p>
                    
                    <a href="{verification_url}" class="button">Verify Email Address</a>
                    
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="word-break: break-all;">{verification_url}</p>
                    
                    <p>This verification link will expire in 24 hours.</p>
                    
                    <p>If you didn't create an account with us, please ignore this email.</p>
                    
                    <p>Best regards,<br>The Voice Agent Team</p>
                </div>
                <div class="footer">
                    <p>&copy; 2024 Voice Agent Platform. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Welcome to Voice Agent Platform!
        
        Hello {username},
        
        Thank you for registering with our Voice Agent Platform. To complete your registration, please verify your email address by visiting this link:
        
        {verification_url}
        
        This verification link will expire in 24 hours.
        
        If you didn't create an account with us, please ignore this email.
        
        Best regards,
        The Voice Agent Team
        """
        
        return await self.send_email(email, subject, html_content, text_content)
    
    async def send_password_reset_email(self, email: str, token: str, username: str) -> bool:
        """Send password reset email"""
        reset_url = f"{self.frontend_url}/reset-password?token={token}"
        
        subject = "Reset Your Password"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #FF6B35; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .button {{ 
                    display: inline-block; 
                    padding: 12px 24px; 
                    background-color: #FF6B35; 
                    color: white; 
                    text-decoration: none; 
                    border-radius: 5px; 
                    margin: 20px 0;
                }}
                .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; }}
                .warning {{ background-color: #FFF3CD; border: 1px solid #FFEAA7; padding: 10px; border-radius: 5px; margin: 15px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Password Reset Request</h1>
                </div>
                <div class="content">
                    <h2>Hello {username},</h2>
                    <p>We received a request to reset your password for your Voice Agent Platform account.</p>
                    
                    <p>Click the button below to reset your password:</p>
                    
                    <a href="{reset_url}" class="button">Reset Password</a>
                    
                    <p>Or copy and paste this link into your browser:</p>
                    <p style="word-break: break-all;">{reset_url}</p>
                    
                    <div class="warning">
                        <strong>Important:</strong> This password reset link will expire in 1 hour for security reasons.
                    </div>
                    
                    <p>If you didn't request this password reset, please ignore this email. Your password will remain unchanged.</p>
                    
                    <p>For security reasons, if you continue to receive these emails, please contact our support team.</p>
                    
                    <p>Best regards,<br>The Voice Agent Team</p>
                </div>
                <div class="footer">
                    <p>&copy; 2024 Voice Agent Platform. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Password Reset Request
        
        Hello {username},
        
        We received a request to reset your password for your Voice Agent Platform account.
        
        To reset your password, please visit this link:
        {reset_url}
        
        This password reset link will expire in 1 hour for security reasons.
        
        If you didn't request this password reset, please ignore this email. Your password will remain unchanged.
        
        Best regards,
        The Voice Agent Team
        """
        
        return await self.send_email(email, subject, html_content, text_content)
    
    async def send_welcome_email(self, email: str, username: str) -> bool:
        """Send welcome email after successful verification"""
        subject = "Welcome to Voice Agent Platform!"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .button {{ 
                    display: inline-block; 
                    padding: 12px 24px; 
                    background-color: #4CAF50; 
                    color: white; 
                    text-decoration: none; 
                    border-radius: 5px; 
                    margin: 20px 0;
                }}
                .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; }}
                .feature {{ margin: 15px 0; padding: 10px; background-color: white; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🎉 Welcome to Voice Agent Platform!</h1>
                </div>
                <div class="content">
                    <h2>Hello {username},</h2>
                    <p>Congratulations! Your email has been verified and your account is now fully activated.</p>
                    
                    <p>You can now enjoy all the features of our Voice Agent Platform:</p>
                    
                    <div class="feature">
                        <strong>🤖 AI Voice Agents:</strong> Create and deploy intelligent voice agents for your business
                    </div>
                    
                    <div class="feature">
                        <strong>📞 Call Management:</strong> Handle incoming and outgoing calls with AI assistance
                    </div>
                    
                    <div class="feature">
                        <strong>📊 Analytics:</strong> Track performance and gain insights from your voice interactions
                    </div>
                    
                    <div class="feature">
                        <strong>🔧 Customization:</strong> Configure your voice agents to match your business needs
                    </div>
                    
                    <a href="{self.frontend_url}/dashboard" class="button">Go to Dashboard</a>
                    
                    <p>If you have any questions or need help getting started, don't hesitate to reach out to our support team.</p>
                    
                    <p>Best regards,<br>The Voice Agent Team</p>
                </div>
                <div class="footer">
                    <p>&copy; 2024 Voice Agent Platform. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Welcome to Voice Agent Platform!
        
        Hello {username},
        
        Congratulations! Your email has been verified and your account is now fully activated.
        
        You can now enjoy all the features of our Voice Agent Platform:
        
        - AI Voice Agents: Create and deploy intelligent voice agents for your business
        - Call Management: Handle incoming and outgoing calls with AI assistance  
        - Analytics: Track performance and gain insights from your voice interactions
        - Customization: Configure your voice agents to match your business needs
        
        Visit your dashboard: {self.frontend_url}/dashboard
        
        If you have any questions or need help getting started, don't hesitate to reach out to our support team.
        
        Best regards,
        The Voice Agent Team
        """
        
        return await self.send_email(email, subject, html_content, text_content)
    
    async def send_security_alert(self, email: str, username: str, action: str, ip_address: str = None) -> bool:
        """Send security alert email"""
        subject = f"Security Alert: {action}"
        
        location_info = f" from IP {ip_address}" if ip_address else ""
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #DC3545; color: white; padding: 20px; text-align: center; }}
                .content {{ padding: 20px; background-color: #f9f9f9; }}
                .alert {{ background-color: #F8D7DA; border: 1px solid #F5C6CB; padding: 15px; border-radius: 5px; margin: 15px 0; }}
                .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔒 Security Alert</h1>
                </div>
                <div class="content">
                    <h2>Hello {username},</h2>
                    
                    <div class="alert">
                        <strong>Security Action Detected:</strong> {action}{location_info}
                    </div>
                    
                    <p>If this was you, no further action is required.</p>
                    
                    <p>If you did not perform this action, please:</p>
                    <ul>
                        <li>Change your password immediately</li>
                        <li>Review your account activity</li>
                        <li>Contact our support team</li>
                    </ul>
                    
                    <p>Best regards,<br>The Voice Agent Security Team</p>
                </div>
                <div class="footer">
                    <p>&copy; 2024 Voice Agent Platform. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_content = f"""
        Security Alert: {action}
        
        Hello {username},
        
        Security Action Detected: {action}{location_info}
        
        If this was you, no further action is required.
        
        If you did not perform this action, please:
        - Change your password immediately
        - Review your account activity  
        - Contact our support team
        
        Best regards,
        The Voice Agent Security Team
        """
        
        return await self.send_email(email, subject, html_content, text_content)


# Global email service instance
email_service = EmailService()