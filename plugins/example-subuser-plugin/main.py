"""
ServerCraft Enhanced Sub-User Management Plugin

Provides advanced sub-user management capabilities with granular control.
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging
import uuid

logger = logging.getLogger(__name__)
router = APIRouter()

# Database will be injected by plugin system
db = None

class SubUserPermissions(BaseModel):
    """Granular permissions for sub-users"""
    server_access: List[str] = []  # List of server IDs
    can_start: bool = False
    can_stop: bool = False
    can_restart: bool = False
    can_view_console: bool = False
    can_send_commands: bool = False
    can_view_files: bool = False
    can_upload_files: bool = False
    can_edit_files: bool = False
    can_delete_files: bool = False
    can_view_backups: bool = False
    can_create_backups: bool = False
    can_restore_backups: bool = False
    fully_restricted: bool = False  # Full access restriction

class SubUser(BaseModel):
    """Enhanced sub-user model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    username: str
    admin_id: str  # Parent admin user
    permissions: SubUserPermissions
    status: str = "active"  # 'active', 'suspended', 'banned'
    suspension_reason: Optional[str] = None
    suspension_until: Optional[str] = None
    ban_reason: Optional[str] = None
    banned_at: Optional[str] = None
    ip_blocks: List[str] = []  # Blocked IP addresses
    last_login: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class CreateSubUserRequest(BaseModel):
    email: EmailStr
    username: str
    permissions: SubUserPermissions

class UpdatePermissionsRequest(BaseModel):
    permissions: SubUserPermissions

class SuspendRequest(BaseModel):
    reason: str
    duration_days: Optional[int] = None  # None = indefinite

class BanRequest(BaseModel):
    reason: str

class IPBlockRequest(BaseModel):
    ip_address: str
    reason: Optional[str] = None

def init_plugin(database, config: Dict[str, Any]):
    """
    Initialize enhanced sub-user plugin
    """
    global db
    db = database
    logger.info("Enhanced Sub-User Management plugin initialized")
    return True

def cleanup_plugin():
    """
    Cleanup plugin
    """
    logger.info("Enhanced Sub-User Management plugin cleaned up")
    pass

@router.get("/subusers", response_model=List[SubUser])
async def get_subusers(admin_id: Optional[str] = None):
    """
    Get all sub-users (filtered by admin if provided)
    """
    try:
        query = {}
        if admin_id:
            query["admin_id"] = admin_id
        
        subusers = await db.enhanced_subusers.find(query, {"_id": 0}).to_list(length=None)
        return subusers
    except Exception as e:
        logger.error(f"Failed to fetch sub-users: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch sub-users")

@router.post("/subusers", response_model=SubUser)
async def create_subuser(request: CreateSubUserRequest, admin_id: str):
    """
    Create a new sub-user (Admin only)
    """
    try:
        # Check if email already exists
        existing = await db.enhanced_subusers.find_one({"email": request.email}, {"_id": 0})
        if existing:
            raise HTTPException(status_code=400, detail="Email already in use")
        
        # Create sub-user
        subuser = SubUser(
            email=request.email,
            username=request.username,
            admin_id=admin_id,
            permissions=request.permissions
        )
        
        await db.enhanced_subusers.insert_one(subuser.dict())
        
        logger.info(f"Created sub-user: {subuser.email} for admin {admin_id}")
        return subuser
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create sub-user: {e}")
        raise HTTPException(status_code=500, detail="Failed to create sub-user")

@router.delete("/subusers/{user_id}")
async def delete_subuser(user_id: str, admin_id: str):
    """
    Delete a sub-user (Admin only)
    """
    try:
        result = await db.enhanced_subusers.delete_one(
            {"id": user_id, "admin_id": admin_id}
        )
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Sub-user not found or unauthorized")
        
        logger.info(f"Deleted sub-user: {user_id}")
        return {"success": True, "message": "Sub-user deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete sub-user: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete sub-user")

@router.put("/subusers/{user_id}/suspend")
async def suspend_subuser(user_id: str, request: SuspendRequest, admin_id: str):
    """
    Suspend a sub-user account
    """
    try:
        suspension_until = None
        if request.duration_days:
            suspension_until = (datetime.now() + timedelta(days=request.duration_days)).isoformat()
        
        result = await db.enhanced_subusers.update_one(
            {"id": user_id, "admin_id": admin_id},
            {"$set": {
                "status": "suspended",
                "suspension_reason": request.reason,
                "suspension_until": suspension_until,
                "updated_at": datetime.now().isoformat()
            }}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Sub-user not found or unauthorized")
        
        logger.info(f"Suspended sub-user: {user_id}")
        return {"success": True, "message": "Sub-user suspended"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to suspend sub-user: {e}")
        raise HTTPException(status_code=500, detail="Failed to suspend sub-user")

@router.put("/subusers/{user_id}/unsuspend")
async def unsuspend_subuser(user_id: str, admin_id: str):
    """
    Remove suspension from a sub-user
    """
    try:
        result = await db.enhanced_subusers.update_one(
            {"id": user_id, "admin_id": admin_id},
            {"$set": {
                "status": "active",
                "suspension_reason": None,
                "suspension_until": None,
                "updated_at": datetime.now().isoformat()
            }}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Sub-user not found or unauthorized")
        
        logger.info(f"Unsuspended sub-user: {user_id}")
        return {"success": True, "message": "Sub-user unsuspended"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to unsuspend sub-user: {e}")
        raise HTTPException(status_code=500, detail="Failed to unsuspend sub-user")

@router.put("/subusers/{user_id}/ban")
async def ban_subuser(user_id: str, request: BanRequest, admin_id: str):
    """
    Ban a sub-user account
    """
    try:
        result = await db.enhanced_subusers.update_one(
            {"id": user_id, "admin_id": admin_id},
            {"$set": {
                "status": "banned",
                "ban_reason": request.reason,
                "banned_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Sub-user not found or unauthorized")
        
        logger.info(f"Banned sub-user: {user_id}")
        return {"success": True, "message": "Sub-user banned"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to ban sub-user: {e}")
        raise HTTPException(status_code=500, detail="Failed to ban sub-user")

@router.put("/subusers/{user_id}/unban")
async def unban_subuser(user_id: str, admin_id: str):
    """
    Remove ban from a sub-user
    """
    try:
        result = await db.enhanced_subusers.update_one(
            {"id": user_id, "admin_id": admin_id},
            {"$set": {
                "status": "active",
                "ban_reason": None,
                "banned_at": None,
                "updated_at": datetime.now().isoformat()
            }}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Sub-user not found or unauthorized")
        
        logger.info(f"Unbanned sub-user: {user_id}")
        return {"success": True, "message": "Sub-user unbanned"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to unban sub-user: {e}")
        raise HTTPException(status_code=500, detail="Failed to unban sub-user")

@router.post("/subusers/{user_id}/ip-block")
async def add_ip_block(user_id: str, request: IPBlockRequest, admin_id: str):
    """
    Add an IP address to the block list for a sub-user
    """
    try:
        result = await db.enhanced_subusers.update_one(
            {"id": user_id, "admin_id": admin_id},
            {"$addToSet": {"ip_blocks": request.ip_address}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Sub-user not found or unauthorized")
        
        logger.info(f"Added IP block for sub-user {user_id}: {request.ip_address}")
        return {"success": True, "message": "IP address blocked"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to add IP block: {e}")
        raise HTTPException(status_code=500, detail="Failed to add IP block")

@router.delete("/subusers/{user_id}/ip-block/{ip_address}")
async def remove_ip_block(user_id: str, ip_address: str, admin_id: str):
    """
    Remove an IP address from the block list
    """
    try:
        result = await db.enhanced_subusers.update_one(
            {"id": user_id, "admin_id": admin_id},
            {"$pull": {"ip_blocks": ip_address}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Sub-user not found or unauthorized")
        
        logger.info(f"Removed IP block for sub-user {user_id}: {ip_address}")
        return {"success": True, "message": "IP block removed"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to remove IP block: {e}")
        raise HTTPException(status_code=500, detail="Failed to remove IP block")

@router.put("/subusers/{user_id}/permissions")
async def update_permissions(user_id: str, request: UpdatePermissionsRequest, admin_id: str):
    """
    Update sub-user permissions
    """
    try:
        # Validate that admin cannot give full admin privileges
        if hasattr(request.permissions, 'is_admin') and request.permissions.is_admin:
            raise HTTPException(
                status_code=403,
                detail="Cannot grant admin privileges to sub-users"
            )
        
        result = await db.enhanced_subusers.update_one(
            {"id": user_id, "admin_id": admin_id},
            {"$set": {
                "permissions": request.permissions.dict(),
                "updated_at": datetime.now().isoformat()
            }}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Sub-user not found or unauthorized")
        
        logger.info(f"Updated permissions for sub-user: {user_id}")
        return {"success": True, "message": "Permissions updated"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update permissions: {e}")
        raise HTTPException(status_code=500, detail="Failed to update permissions")

@router.get("/subusers/{user_id}/check-access")
async def check_access(user_id: str, request: Request):
    """
    Check if sub-user has access (checks status, IP blocks, etc.)
    """
    try:
        subuser = await db.enhanced_subusers.find_one({"id": user_id}, {"_id": 0})
        if not subuser:
            raise HTTPException(status_code=404, detail="Sub-user not found")
        
        # Check if banned
        if subuser["status"] == "banned":
            return {
                "allowed": False,
                "reason": f"Account banned: {subuser.get('ban_reason', 'No reason provided')}"
            }
        
        # Check if suspended
        if subuser["status"] == "suspended":
            if subuser.get("suspension_until"):
                suspension_end = datetime.fromisoformat(subuser["suspension_until"])
                if datetime.now() < suspension_end:
                    return {
                        "allowed": False,
                        "reason": f"Account suspended until {subuser['suspension_until']}"
                    }
                else:
                    # Auto-unsuspend if time has passed
                    await db.enhanced_subusers.update_one(
                        {"id": user_id},
                        {"$set": {"status": "active", "suspension_until": None}}
                    )
            else:
                return {
                    "allowed": False,
                    "reason": "Account suspended indefinitely"
                }
        
        # Check IP block
        client_ip = request.client.host if request.client else None
        if client_ip and client_ip in subuser.get("ip_blocks", []):
            return {
                "allowed": False,
                "reason": "IP address blocked"
            }
        
        # Check if fully restricted
        if subuser.get("permissions", {}).get("fully_restricted", False):
            return {
                "allowed": False,
                "reason": "Account access fully restricted"
            }
        
        return {"allowed": True, "permissions": subuser.get("permissions", {})}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to check access: {e}")
        raise HTTPException(status_code=500, detail="Failed to check access")
