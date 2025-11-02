from datetime import datetime, timezone, timedelta
from typing import Optional
import re
import logging
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

# Password Security
class PasswordValidator:
    @staticmethod
    def validate_strength(password: str) -> tuple[bool, str]:
        """Validate password strength"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'[0-9]', password):
            return False, "Password must contain at least one number"
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character"
        
        # Check for common weak passwords
        weak_passwords = ['Password123!', 'Admin123!', '12345678!A']
        if password in weak_passwords:
            return False, "Password is too common. Please choose a stronger password"
        
        return True, "Password is strong"

# Account Security
class AccountSecurity:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.max_failed_attempts = 5
        self.lockout_duration = timedelta(minutes=15)
    
    async def record_failed_login(self, email: str, ip_address: str):
        """Record a failed login attempt"""
        await self.db.failed_logins.insert_one({
            "email": email,
            "ip_address": ip_address,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "success": False
        })
        
        # Check if account should be locked
        recent_failures = await self.db.failed_logins.count_documents({
            "email": email,
            "timestamp": {"$gte": (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()}
        })
        
        if recent_failures >= self.max_failed_attempts:
            await self.lock_account(email)
            logger.warning(f"Account locked due to multiple failed attempts: {email}")
    
    async def record_successful_login(self, email: str, ip_address: str, user_agent: str):
        """Record a successful login"""
        await self.db.login_history.insert_one({
            "email": email,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "success": True
        })
    
    async def lock_account(self, email: str):
        """Lock user account"""
        await self.db.users.update_one(
            {"email": email},
            {
                "$set": {
                    "locked": True,
                    "locked_at": datetime.now(timezone.utc).isoformat(),
                    "locked_until": (datetime.now(timezone.utc) + self.lockout_duration).isoformat()
                }
            }
        )
    
    async def is_account_locked(self, email: str) -> bool:
        """Check if account is locked"""
        user = await self.db.users.find_one({"email": email}, {"locked": 1, "locked_until": 1})
        
        if not user or not user.get("locked"):
            return False
        
        # Check if lockout has expired
        locked_until = user.get("locked_until")
        if locked_until:
            locked_until_dt = datetime.fromisoformat(locked_until)
            if datetime.now(timezone.utc) > locked_until_dt:
                # Unlock account
                await self.db.users.update_one(
                    {"email": email},
                    {"$set": {"locked": False, "locked_until": None}}
                )
                return False
        
        return True

# Audit Logging
class AuditLogger:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
    
    async def log(self, user_id: str, action: str, resource: str, details: dict = None, ip_address: str = None):
        """Log audit event"""
        await self.db.audit_logs.insert_one({
            "user_id": user_id,
            "action": action,
            "resource": resource,
            "details": details or {},
            "ip_address": ip_address,
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        logger.info(f"AUDIT: User {user_id} performed {action} on {resource}")

# Input Sanitization
class InputSanitizer:
    @staticmethod
    def sanitize_string(text: str, max_length: int = 1000) -> str:
        """Sanitize string input"""
        if not text:
            return ""
        
        # Remove null bytes
        text = text.replace('\x00', '')
        
        # Limit length
        text = text[:max_length]
        
        # Remove dangerous HTML/script tags
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'<iframe[^>]*>.*?</iframe>', '', text, flags=re.IGNORECASE | re.DOTALL)
        
        return text.strip()
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename to prevent path traversal"""
        # Remove path separators and dangerous characters
        filename = re.sub(r'[/\\]', '', filename)
        filename = re.sub(r'[^a-zA-Z0-9._-]', '_', filename)
        return filename[:255]  # Limit filename length

# File Upload Security
class FileUploadValidator:
    # Allowed file extensions
    ALLOWED_EXTENSIONS = {
        'plugin': ['.zip'],
        'theme': ['.zip'],
        'config': ['.cfg', '.txt', '.json', '.xml'],
        'modlist': ['.html', '.htm']
    }
    
    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    
    @staticmethod
    def validate_file_type(filename: str, file_type: str) -> tuple[bool, str]:
        """Validate file extension"""
        if file_type not in FileUploadValidator.ALLOWED_EXTENSIONS:
            return False, "Invalid file type category"
        
        allowed = FileUploadValidator.ALLOWED_EXTENSIONS[file_type]
        file_ext = '.' + filename.rsplit('.', 1)[-1].lower() if '.' in filename else ''
        
        if file_ext not in allowed:
            return False, f"File type not allowed. Allowed: {', '.join(allowed)}"
        
        return True, "File type valid"
    
    @staticmethod
    def validate_file_size(file_size: int) -> tuple[bool, str]:
        """Validate file size"""
        if file_size > FileUploadValidator.MAX_FILE_SIZE:
            return False, f"File too large. Maximum size: {FileUploadValidator.MAX_FILE_SIZE / 1024 / 1024}MB"
        
        return True, "File size valid"

# Session Management
class SessionManager:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.session_timeout = timedelta(hours=8)
        self.max_sessions_per_user = 3
    
    async def create_session(self, user_id: str, token: str, ip_address: str, user_agent: str):
        """Create a new session"""
        # Check existing sessions
        session_count = await self.db.sessions.count_documents({"user_id": user_id, "active": True})
        
        if session_count >= self.max_sessions_per_user:
            # Remove oldest session
            oldest = await self.db.sessions.find_one(
                {"user_id": user_id, "active": True},
                sort=[("created_at", 1)]
            )
            if oldest:
                await self.db.sessions.update_one(
                    {"_id": oldest["_id"]},
                    {"$set": {"active": False}}
                )
        
        await self.db.sessions.insert_one({
            "user_id": user_id,
            "token": token,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_activity": datetime.now(timezone.utc).isoformat(),
            "expires_at": (datetime.now(timezone.utc) + self.session_timeout).isoformat(),
            "active": True
        })
    
    async def validate_session(self, token: str) -> bool:
        """Validate if session is still active"""
        session = await self.db.sessions.find_one({"token": token, "active": True})
        
        if not session:
            return False
        
        # Check if expired
        expires_at = datetime.fromisoformat(session["expires_at"])
        if datetime.now(timezone.utc) > expires_at:
            await self.db.sessions.update_one(
                {"token": token},
                {"$set": {"active": False}}
            )
            return False
        
        # Update last activity
        await self.db.sessions.update_one(
            {"token": token},
            {"$set": {"last_activity": datetime.now(timezone.utc).isoformat()}}
        )
        
        return True
    
    async def invalidate_session(self, token: str):
        """Invalidate a session"""
        await self.db.sessions.update_one(
            {"token": token},
            {"$set": {"active": False}}
        )
