from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, UploadFile, File, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict, EmailStr
from typing import List, Optional, Dict, Any
import uuid
from datetime import datetime, timezone, timedelta
from passlib.context import CryptContext
from jose import JWTError, jwt
import docker
import json
import asyncio
import aiofiles
from bs4 import BeautifulSoup
import re

# Import security modules
from security import (
    PasswordValidator,
    AccountSecurity,
    AuditLogger,
    InputSanitizer,
    FileUploadValidator,
    SessionManager
)

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Security instances
account_security = AccountSecurity(db)
audit_logger = AuditLogger(db)
session_manager = SessionManager(db)

# Rate Limiter
limiter = Limiter(key_func=get_remote_address)

# Docker client
try:
    docker_client = docker.from_env()
except Exception as e:
    docker_client = None

# JWT Settings
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480
REFRESH_TOKEN_EXPIRE_DAYS = 30

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security_bearer = HTTPBearer()

# Create the main app
app = FastAPI()
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

api_router = APIRouter(prefix="/api")

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Models
class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: EmailStr
    role: str = "admin"
    permissions: Dict[str, Any] = Field(default_factory=dict)
    locked: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    role: str = "admin"
    permissions: Dict[str, Any] = Field(default_factory=dict)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    user: User

class RefreshTokenRequest(BaseModel):
    refresh_token: str

# Helper Functions
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(request: Request, credentials: HTTPAuthorizationCredentials = Depends(security_bearer)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Validate token type
        if payload.get("type") != "access":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
        # Validate session
        is_valid = await session_manager.validate_session(token)
        if not is_valid:
            raise HTTPException(status_code=401, detail="Session expired or invalid")
        
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    user = await db.users.find_one({"id": user_id}, {"_id": 0, "hashed_password": 0})
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    # Check if account is locked
    if user.get("locked"):
        raise HTTPException(status_code=403, detail="Account is locked")
    
    return User(**user)

def get_client_ip(request: Request) -> str:
    """Get client IP address"""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0]
    return request.client.host if request.client else "unknown"

# Middleware for security headers
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    # Add security headers manually
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

# Auth Routes with Rate Limiting
@api_router.post("/auth/login", response_model=Token)
@limiter.limit("10/minute")
async def login(request: Request, credentials: UserLogin):
    ip_address = get_client_ip(request)
    
    # Check if account is locked
    is_locked = await account_security.is_account_locked(credentials.email)
    if is_locked:
        raise HTTPException(
            status_code=403,
            detail="Account is temporarily locked due to multiple failed login attempts. Please try again later."
        )
    
    user_data = await db.users.find_one({"email": credentials.email}, {"_id": 0})
    if not user_data or not verify_password(credentials.password, user_data["hashed_password"]):
        await account_security.record_failed_login(credentials.email, ip_address)
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user = User(**{k: v for k, v in user_data.items() if k != "hashed_password"})
    
    # Create tokens
    access_token = create_access_token(data={"sub": user.id})
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    # Create session
    user_agent = request.headers.get("User-Agent", "Unknown")
    await session_manager.create_session(user.id, access_token, ip_address, user_agent)
    await account_security.record_successful_login(user.email, ip_address, user_agent)
    await audit_logger.log(user.id, "login", "user", {"email": user.email}, ip_address)
    
    logger.info(f"User logged in: {user.email}")
    
    return Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer", user=user)

@api_router.post("/auth/refresh", response_model=Token)
@limiter.limit("10/minute")
async def refresh_token(request: Request, token_request: RefreshTokenRequest):
    try:
        payload = jwt.decode(token_request.refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")
        
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user_data = await db.users.find_one({"id": user_id}, {"_id": 0, "hashed_password": 0})
        if not user_data:
            raise HTTPException(status_code=401, detail="User not found")
        
        user = User(**user_data)
        
        # Create new tokens
        new_access_token = create_access_token(data={"sub": user.id})
        new_refresh_token = create_refresh_token(data={"sub": user.id})
        
        # Create new session
        ip_address = get_client_ip(request)
        user_agent = request.headers.get("User-Agent", "Unknown")
        await session_manager.create_session(user.id, new_access_token, ip_address, user_agent)
        
        return Token(access_token=new_access_token, refresh_token=new_refresh_token, token_type="bearer", user=user)
        
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

@api_router.post("/auth/logout")
async def logout(request: Request, current_user: User = Depends(get_current_user), credentials: HTTPAuthorizationCredentials = Depends(security_bearer)):
    token = credentials.credentials
    await session_manager.invalidate_session(token)
    
    ip_address = get_client_ip(request)
    await audit_logger.log(current_user.id, "logout", "user", {}, ip_address)
    
    return {"message": "Logged out successfully"}

# Stats endpoint
@api_router.get("/stats")
@limiter.limit("30/minute")
async def get_stats(request: Request, current_user: User = Depends(get_current_user)):
    total_nodes = await db.nodes.count_documents({})
    total_servers = await db.servers.count_documents({})
    running_servers = await db.servers.count_documents({"status": "running"})
    total_users = await db.users.count_documents({})
    
    return {
        "total_nodes": total_nodes,
        "total_servers": total_servers,
        "running_servers": running_servers,
        "total_users": total_users
    }

# Security audit endpoint (admin only)
@api_router.get("/security/audit-logs")
@limiter.limit("30/minute")
async def get_audit_logs(
    request: Request,
    current_user: User = Depends(get_current_user),
    limit: int = 100,
    skip: int = 0
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    logs = await db.audit_logs.find({}, {"_id": 0}).sort("timestamp", -1).skip(skip).limit(limit).to_list(limit)
    return logs

@api_router.get("/security/login-history")
@limiter.limit("30/minute")
async def get_login_history(
    request: Request,
    current_user: User = Depends(get_current_user),
    limit: int = 50
):
    history = await db.login_history.find(
        {"email": current_user.email},
        {"_id": 0}
    ).sort("timestamp", -1).limit(limit).to_list(limit)
    return history

# ============================================
# Plugin Management System
# ============================================

class Plugin(BaseModel):
    """Plugin metadata"""
    id: str
    name: str
    version: str
    description: Optional[str] = None
    author: Optional[str] = None
    enabled: bool = False
    installed_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    manifest: Dict[str, Any] = {}

class PluginUploadResponse(BaseModel):
    success: bool
    message: str
    plugin_id: Optional[str] = None

# Plugin storage directory
PLUGIN_DIR = Path("/app/plugins")
PLUGIN_DIR.mkdir(exist_ok=True)

def validate_plugin_manifest(manifest: Dict[str, Any]) -> tuple[bool, str]:
    """Validate plugin manifest structure"""
    required_fields = ['id', 'name', 'version', 'description']
    for field in required_fields:
        if field not in manifest:
            return False, f"Missing required field: {field}"
    
    # Validate plugin ID format (lowercase, hyphens only)
    if not re.match(r'^[a-z0-9-]+$', manifest['id']):
        return False, "Invalid plugin ID format (use lowercase and hyphens only)"
    
    return True, "Valid"

@api_router.post("/plugins/upload", response_model=PluginUploadResponse)
@limiter.limit("5/hour")
async def upload_plugin(
    request: Request,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user)
):
    """
    Upload and install a plugin (Admin only)
    """
    # Check admin permission
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Validate file type
        if not file.filename.endswith('.zip'):
            raise HTTPException(status_code=400, detail="Only .zip files are allowed")
        
        # Validate file size (max 10MB)
        content = await file.read()
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")
        
        # Save to temporary location
        temp_path = PLUGIN_DIR / f"temp_{uuid.uuid4()}.zip"
        async with aiofiles.open(temp_path, 'wb') as f:
            await f.write(content)
        
        # Extract and validate
        import zipfile
        extract_path = PLUGIN_DIR / f"temp_{uuid.uuid4()}"
        extract_path.mkdir(exist_ok=True)
        
        with zipfile.ZipFile(temp_path, 'r') as zip_ref:
            # Security: Check for path traversal attacks
            for member in zip_ref.namelist():
                if '..' in member or member.startswith('/'):
                    temp_path.unlink()
                    raise HTTPException(status_code=400, detail="Invalid zip file structure")
            zip_ref.extractall(extract_path)
        
        # Find manifest.json
        manifest_files = list(extract_path.glob("**/manifest.json"))
        if not manifest_files:
            temp_path.unlink()
            raise HTTPException(status_code=400, detail="manifest.json not found in plugin")
        
        manifest_path = manifest_files[0]
        plugin_root = manifest_path.parent
        
        # Read and validate manifest
        async with aiofiles.open(manifest_path, 'r') as f:
            manifest_content = await f.read()
        manifest = json.loads(manifest_content)
        
        is_valid, message = validate_plugin_manifest(manifest)
        if not is_valid:
            temp_path.unlink()
            raise HTTPException(status_code=400, detail=message)
        
        plugin_id = manifest['id']
        
        # Check if plugin already exists
        existing = await db.plugins.find_one({"id": plugin_id}, {"_id": 0})
        if existing:
            temp_path.unlink()
            raise HTTPException(status_code=400, detail="Plugin already installed")
        
        # Move to final location
        final_plugin_path = PLUGIN_DIR / plugin_id
        if final_plugin_path.exists():
            import shutil
            shutil.rmtree(final_plugin_path)
        
        import shutil
        shutil.move(str(plugin_root), str(final_plugin_path))
        
        # Clean up
        temp_path.unlink()
        shutil.rmtree(extract_path, ignore_errors=True)
        
        # Save to database
        plugin = Plugin(
            id=plugin_id,
            name=manifest['name'],
            version=manifest['version'],
            description=manifest.get('description'),
            author=manifest.get('author'),
            enabled=False,
            manifest=manifest
        )
        
        await db.plugins.insert_one(plugin.model_dump())
        
        ip_address = get_client_ip(request)
        await audit_logger.log(
            current_user.id,
            "upload_plugin",
            "plugin",
            {"plugin_id": plugin_id},
            ip_address
        )
        
        logger.info(f"Plugin uploaded: {plugin_id} by {current_user.email}")
        
        return PluginUploadResponse(
            success=True,
            message="Plugin uploaded successfully",
            plugin_id=plugin_id
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to upload plugin: {e}")
        raise HTTPException(status_code=500, detail="Failed to upload plugin")

@api_router.get("/plugins", response_model=List[Plugin])
async def get_plugins(current_user: User = Depends(get_current_user)):
    """Get all installed plugins"""
    try:
        plugins = await db.plugins.find({}, {"_id": 0}).to_list(length=None)
        return plugins
    except Exception as e:
        logger.error(f"Failed to fetch plugins: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch plugins")

@api_router.put("/plugins/{plugin_id}/enable")
async def enable_plugin(
    plugin_id: str,
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Enable a plugin (Admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        result = await db.plugins.update_one(
            {"id": plugin_id},
            {"$set": {"enabled": True}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Plugin not found")
        
        ip_address = get_client_ip(request)
        await audit_logger.log(
            current_user.id,
            "enable_plugin",
            "plugin",
            {"plugin_id": plugin_id},
            ip_address
        )
        
        logger.info(f"Plugin enabled: {plugin_id}")
        return {"success": True, "message": "Plugin enabled"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to enable plugin: {e}")
        raise HTTPException(status_code=500, detail="Failed to enable plugin")

@api_router.put("/plugins/{plugin_id}/disable")
async def disable_plugin(
    plugin_id: str,
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Disable a plugin (Admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        result = await db.plugins.update_one(
            {"id": plugin_id},
            {"$set": {"enabled": False}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Plugin not found")
        
        ip_address = get_client_ip(request)
        await audit_logger.log(
            current_user.id,
            "disable_plugin",
            "plugin",
            {"plugin_id": plugin_id},
            ip_address
        )
        
        logger.info(f"Plugin disabled: {plugin_id}")
        return {"success": True, "message": "Plugin disabled"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to disable plugin: {e}")
        raise HTTPException(status_code=500, detail="Failed to disable plugin")

@api_router.delete("/plugins/{plugin_id}")
async def delete_plugin(
    plugin_id: str,
    request: Request,
    current_user: User = Depends(get_current_user)
):
    """Delete a plugin (Admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    try:
        # Delete from database
        result = await db.plugins.delete_one({"id": plugin_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Plugin not found")
        
        # Delete plugin files
        plugin_path = PLUGIN_DIR / plugin_id
        if plugin_path.exists():
            import shutil
            shutil.rmtree(plugin_path)
        
        ip_address = get_client_ip(request)
        await audit_logger.log(
            current_user.id,
            "delete_plugin",
            "plugin",
            {"plugin_id": plugin_id},
            ip_address
        )
        
        logger.info(f"Plugin deleted: {plugin_id}")
        return {"success": True, "message": "Plugin deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete plugin: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete plugin")

# Include router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
