"""
Two-Factor Authentication (2FA) Module
Provides TOTP-based 2FA functionality for ServerCraft
"""

import pyotp
import qrcode
import io
import base64
import secrets
from typing import Optional, List, Tuple
from datetime import datetime, timezone

class TwoFactorAuth:
    """Handle 2FA operations"""
    
    @staticmethod
    def generate_secret() -> str:
        """Generate a new TOTP secret"""
        return pyotp.random_base32()
    
    @staticmethod
    def generate_qr_code(secret: str, username: str, issuer: str = "ServerCraft") -> str:
        """
        Generate QR code for 2FA setup
        
        Args:
            secret: TOTP secret
            username: User's email or username
            issuer: Application name
            
        Returns:
            Base64 encoded QR code image
        """
        # Create provisioning URI
        totp = pyotp.TOTP(secret)
        provisioning_uri = totp.provisioning_uri(
            name=username,
            issuer_name=issuer
        )
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(provisioning_uri)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return f"data:image/png;base64,{img_base64}"
    
    @staticmethod
    def verify_token(secret: str, token: str) -> bool:
        """
        Verify a TOTP token
        
        Args:
            secret: User's TOTP secret
            token: Token entered by user (6 digits)
            
        Returns:
            True if token is valid
        """
        totp = pyotp.TOTP(secret)
        # Allow 1 time step before/after for clock skew
        return totp.verify(token, valid_window=1)
    
    @staticmethod
    def generate_backup_codes(count: int = 10) -> List[str]:
        """
        Generate backup recovery codes
        
        Args:
            count: Number of codes to generate
            
        Returns:
            List of backup codes (format: XXXX-XXXX-XXXX)
        """
        codes = []
        for _ in range(count):
            # Generate 12 character alphanumeric code
            code = secrets.token_hex(6).upper()
            # Format as XXXX-XXXX-XXXX
            formatted_code = f"{code[0:4]}-{code[4:8]}-{code[8:12]}"
            codes.append(formatted_code)
        return codes
    
    @staticmethod
    def hash_backup_code(code: str) -> str:
        """Hash a backup code for secure storage"""
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        # Remove hyphens before hashing
        clean_code = code.replace("-", "")
        return pwd_context.hash(clean_code)
    
    @staticmethod
    def verify_backup_code(code: str, hashed_code: str) -> bool:
        """Verify a backup code against its hash"""
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        # Remove hyphens before verifying
        clean_code = code.replace("-", "")
        return pwd_context.verify(clean_code, hashed_code)


class TrustedDevice:
    """Manage trusted devices for 2FA bypass"""
    
    @staticmethod
    def generate_device_token() -> str:
        """Generate a unique device token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def create_device_fingerprint(user_agent: str, ip_address: str) -> str:
        """Create a device fingerprint from user agent and IP"""
        import hashlib
        fingerprint_data = f"{user_agent}:{ip_address}"
        return hashlib.sha256(fingerprint_data.encode()).hexdigest()
    
    @staticmethod
    def is_device_trusted(device_token: str, user_devices: List[dict]) -> bool:
        """Check if device token exists in user's trusted devices"""
        for device in user_devices:
            if device.get('token') == device_token:
                # Check if device hasn't expired (30 days)
                created_at = datetime.fromisoformat(device.get('created_at'))
                age_days = (datetime.now(timezone.utc) - created_at).days
                if age_days < 30:
                    return True
        return False
