"""
ServerCraft Plugin Template - Backend

This is the main backend file for your plugin.
All API endpoints and business logic should be defined here.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

# Create plugin router
router = APIRouter()

class PluginConfig(BaseModel):
    """Configuration model for your plugin"""
    api_key: Optional[str] = None
    enabled: bool = True

class PluginResponse(BaseModel):
    """Standard response model"""
    success: bool
    message: str
    data: Optional[Dict[str, Any]] = None

# Plugin initialization
def init_plugin(db, config: Dict[str, Any]):
    """
    Called when plugin is loaded
    
    Args:
        db: MongoDB database connection
        config: Plugin configuration from manifest.json
    """
    logger.info(f"Initializing plugin: {config.get('name')}")
    # Perform any initialization tasks
    # Create database collections, load settings, etc.
    return True

# Plugin cleanup
def cleanup_plugin():
    """
    Called when plugin is disabled or unloaded
    """
    logger.info("Cleaning up plugin")
    # Perform cleanup tasks
    pass

# Example API endpoint
@router.get("/plugin/status", response_model=PluginResponse)
async def get_plugin_status():
    """
    Example endpoint - returns plugin status
    """
    return PluginResponse(
        success=True,
        message="Plugin is active",
        data={"status": "running"}
    )

@router.post("/plugin/action", response_model=PluginResponse)
async def perform_action(data: Dict[str, Any]):
    """
    Example action endpoint
    """
    try:
        # Your plugin logic here
        result = {"processed": True}
        return PluginResponse(
            success=True,
            message="Action completed",
            data=result
        )
    except Exception as e:
        logger.error(f"Plugin action failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Helper function to access ServerCraft API
async def call_servercraft_api(endpoint: str, method: str = "GET", data: Optional[Dict] = None):
    """
    Helper to call main ServerCraft API endpoints
    Plugins should use this instead of direct database access
    
    Args:
        endpoint: API endpoint path (e.g., '/api/servers')
        method: HTTP method
        data: Request data for POST/PUT
    """
    # This will be injected by the plugin system
    pass
