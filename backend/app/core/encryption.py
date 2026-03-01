from cryptography.fernet import Fernet
from app.core.config import settings
import base64
import hashlib

# Generate key from SECRET_KEY
def get_encryption_key() -> bytes:
    """Generate encryption key from SECRET_KEY"""
    key = hashlib.sha256(settings.SECRET_KEY.encode()).digest()
    return base64.urlsafe_b64encode(key)


class DataEncryption:
    """Encrypt/decrypt sensitive data"""
    
    def __init__(self):
        self.cipher = Fernet(get_encryption_key())
    
    def encrypt(self, data: str) -> str:
        """Encrypt a string"""
        if not data:
            return data
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt a string"""
        if not encrypted_data:
            return encrypted_data
        return self.cipher.decrypt(encrypted_data.encode()).decode()
    
    def mask_phone(self, phone: str) -> str:
        """Mask phone number"""
        if not phone:
            return ""
        if len(phone) <= 4:
            return "***"
        return phone[:3] + "***" + phone[-3:]
    
    def mask_email(self, email: str) -> str:
        """Mask email"""
        if not email:
            return ""
        parts = email.split("@")
        if len(parts) != 2:
            return "***@***"
        username = parts[0]
        domain = parts[1]
        if len(username) <= 2:
            masked_username = "**"
        else:
            masked_username = username[0] + "*" * (len(username) - 2) + username[-1]
        return f"{masked_username}@{domain}"


# Singleton instance
encryption = DataEncryption()
