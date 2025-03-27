import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()

# Email configuration
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USERNAME = os.getenv("SMTP_USERNAME")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
FROM_EMAIL = os.getenv("FROM_EMAIL")

def send_email(to_email: str, subject: str, html_content: str) -> bool:
    """Send an email using the configured SMTP server"""
    try:
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = FROM_EMAIL
        message["To"] = to_email

        html_part = MIMEText(html_content, "html")
        message.attach(html_part)

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.login(SMTP_USERNAME, SMTP_PASSWORD)
            server.sendmail(FROM_EMAIL, to_email, message.as_string())
        
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def send_verification_email(to_email: str, verification_code: str) -> bool:
    """Send an email verification email"""
    subject = "Verify Your Email Address"
    verification_url = f"http://localhost:8000/verify-email?code={verification_code}"
    
    html_content = f"""
    <html>
    <body>
        <h2>Verify Your Email Address</h2>
        <p>Please click the link below to verify your email address:</p>
        <p><a href="{verification_url}">Verify Email</a></p>
        <p>If you didn't request this, you can ignore this email.</p>
    </body>
    </html>
    """
    
    return send_email(to_email, subject, html_content)

def send_password_reset_email(to_email: str, reset_token: str) -> bool:
    """Send a password reset email"""
    subject = "Reset Your Password"
    reset_url = f"http://localhost:8000/reset-password?token={reset_token}"
    
    html_content = f"""
    <html>
    <body>
        <h2>Reset Your Password</h2>
        <p>Please click the link below to reset your password:</p>
        <p><a href="{reset_url}">Reset Password</a></p>
        <p>If you didn't request this, you can ignore this email.</p>
    </body>
    </html>
    """
    
    return send_email(to_email, subject, html_content)