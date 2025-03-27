import uuid
from datetime import datetime, timedelta

def generate_verification_code() -> str:
    """Generate a unique verification code"""
    return str(uuid.uuid4())

def generate_reset_token() -> str:
    """Generate a unique password reset token"""
    return str(uuid.uuid4())