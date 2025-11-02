from fastapi import FastAPI, APIRouter, HTTPException, Depends, status, UploadFile, File
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
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

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Docker client
try:
    docker_client = docker.from_env()
except Exception as e:
    logger = logging.getLogger(__name__)
    logger.warning(f"Docker not available: {e}")
    docker_client = None

# JWT Settings
SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "your-secret-key-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

# Create the main app
app = FastAPI()
api_router = APIRouter(prefix="/api")

# Models
class User(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: str
    role: str = "admin"  # admin or subuser
    permissions: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class UserCreate(BaseModel):
    username: str
    email: str
    password: str
    role: str = "admin"
    permissions: Dict[str, Any] = Field(default_factory=dict)

class UserLogin(BaseModel):
    email: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

class Node(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    host: str
    port: int = 2375
    cpu_cores: int
    ram_gb: int
    storage_gb: int
    used_cpu: float = 0
    used_ram: float = 0
    used_storage: float = 0
    status: str = "online"  # online, offline, maintenance
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class NodeCreate(BaseModel):
    name: str
    host: str
    port: int = 2375
    cpu_cores: int
    ram_gb: int
    storage_gb: int

class GameServer(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    game_type: str  # arma3, rust, dayz, etc.
    node_id: str
    container_id: Optional[str] = None
    port: int
    cpu_limit: float
    ram_limit_gb: float
    storage_limit_gb: float
    status: str = "stopped"  # stopped, starting, running, stopping, error
    config: Dict[str, Any] = Field(default_factory=dict)
    owner_id: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class GameServerCreate(BaseModel):
    name: str
    game_type: str
    node_id: str
    port: int
    cpu_limit: float
    ram_limit_gb: float
    storage_limit_gb: float
    config: Dict[str, Any] = Field(default_factory=dict)

class Allocation(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    node_id: str
    port: int
    protocol: str = "tcp"
    assigned_to: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ModList(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    server_id: str
    name: str
    mods: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ServerSelling(BaseModel):
    model_config = ConfigDict(extra="ignore")
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    enabled: bool = False
    game_types: List[str] = Field(default_factory=list)
    pricing: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

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
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    user = await db.users.find_one({"id": user_id}, {"_id": 0})
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return User(**user)

# Auth Routes
@api_router.post("/auth/register", response_model=Token)
async def register(user_data: UserCreate):
    existing = await db.users.find_one({"email": user_data.email}, {"_id": 0})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_pw = hash_password(user_data.password)
    user = User(
        username=user_data.username,
        email=user_data.email,
        role=user_data.role,
        permissions=user_data.permissions
    )
    
    user_dict = user.model_dump()
    user_dict["hashed_password"] = hashed_pw
    user_dict["created_at"] = user_dict["created_at"].isoformat()
    
    await db.users.insert_one(user_dict)
    
    access_token = create_access_token(data={"sub": user.id})
    return Token(access_token=access_token, token_type="bearer", user=user)

@api_router.post("/auth/login", response_model=Token)
async def login(credentials: UserLogin):
    user_data = await db.users.find_one({"email": credentials.email}, {"_id": 0})
    if not user_data or not verify_password(credentials.password, user_data["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user = User(**{k: v for k, v in user_data.items() if k != "hashed_password"})
    access_token = create_access_token(data={"sub": user.id})
    return Token(access_token=access_token, token_type="bearer", user=user)

# Node Routes
@api_router.post("/nodes", response_model=Node)
async def create_node(node_data: NodeCreate, current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can create nodes")
    
    node = Node(**node_data.model_dump())
    node_dict = node.model_dump()
    node_dict["created_at"] = node_dict["created_at"].isoformat()
    
    await db.nodes.insert_one(node_dict)
    return node

@api_router.get("/nodes", response_model=List[Node])
async def get_nodes(current_user: User = Depends(get_current_user)):
    nodes = await db.nodes.find({}, {"_id": 0}).to_list(1000)
    for node in nodes:
        if isinstance(node.get("created_at"), str):
            node["created_at"] = datetime.fromisoformat(node["created_at"])
    return nodes

@api_router.get("/nodes/{node_id}", response_model=Node)
async def get_node(node_id: str, current_user: User = Depends(get_current_user)):
    node = await db.nodes.find_one({"id": node_id}, {"_id": 0})
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    if isinstance(node.get("created_at"), str):
        node["created_at"] = datetime.fromisoformat(node["created_at"])
    return Node(**node)

@api_router.put("/nodes/{node_id}", response_model=Node)
async def update_node(node_id: str, node_data: NodeCreate, current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can update nodes")
    
    existing = await db.nodes.find_one({"id": node_id}, {"_id": 0})
    if not existing:
        raise HTTPException(status_code=404, detail="Node not found")
    
    update_data = node_data.model_dump()
    await db.nodes.update_one({"id": node_id}, {"$set": update_data})
    
    updated = await db.nodes.find_one({"id": node_id}, {"_id": 0})
    if isinstance(updated.get("created_at"), str):
        updated["created_at"] = datetime.fromisoformat(updated["created_at"])
    return Node(**updated)

@api_router.delete("/nodes/{node_id}")
async def delete_node(node_id: str, current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete nodes")
    
    result = await db.nodes.delete_one({"id": node_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Node not found")
    return {"message": "Node deleted successfully"}

# Game Server Routes
@api_router.post("/servers", response_model=GameServer)
async def create_server(server_data: GameServerCreate, current_user: User = Depends(get_current_user)):
    node = await db.nodes.find_one({"id": server_data.node_id}, {"_id": 0})
    if not node:
        raise HTTPException(status_code=404, detail="Node not found")
    
    server = GameServer(**server_data.model_dump(), owner_id=current_user.id)
    server_dict = server.model_dump()
    server_dict["created_at"] = server_dict["created_at"].isoformat()
    
    await db.servers.insert_one(server_dict)
    return server

@api_router.get("/servers", response_model=List[GameServer])
async def get_servers(current_user: User = Depends(get_current_user)):
    query = {} if current_user.role == "admin" else {"owner_id": current_user.id}
    servers = await db.servers.find(query, {"_id": 0}).to_list(1000)
    for server in servers:
        if isinstance(server.get("created_at"), str):
            server["created_at"] = datetime.fromisoformat(server["created_at"])
    return servers

@api_router.get("/servers/{server_id}", response_model=GameServer)
async def get_server(server_id: str, current_user: User = Depends(get_current_user)):
    server = await db.servers.find_one({"id": server_id}, {"_id": 0})
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    if isinstance(server.get("created_at"), str):
        server["created_at"] = datetime.fromisoformat(server["created_at"])
    return GameServer(**server)

@api_router.post("/servers/{server_id}/start")
async def start_server(server_id: str, current_user: User = Depends(get_current_user)):
    server = await db.servers.find_one({"id": server_id}, {"_id": 0})
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    if not docker_client:
        raise HTTPException(status_code=503, detail="Docker not available")
    
    try:
        container_name = f"gameserver_{server['game_type']}_{server_id[:8]}"
        
        # Game-specific container configurations
        game_configs = {
            "arma3": {
                "image": "acemod/arma3server:latest",
                "environment": {
                    "SERVER_NAME": server.get("name", "Arma 3 Server"),
                    "SERVER_PASSWORD": server.get("config", {}).get("password", ""),
                    "ADMIN_PASSWORD": server.get("config", {}).get("admin_password", ""),
                }
            },
            "rust": {
                "image": "didstopia/rust-server:latest",
                "environment": {
                    "RUST_SERVER_NAME": server.get("name", "Rust Server"),
                    "RUST_SERVER_WORLDSIZE": "3000",
                    "RUST_SERVER_SEED": "12345",
                }
            }
        }
        
        config = game_configs.get(server["game_type"], game_configs["arma3"])
        
        container = docker_client.containers.run(
            config["image"],
            name=container_name,
            detach=True,
            ports={f"{server['port']}/tcp": server['port']},
            environment=config["environment"],
            mem_limit=f"{server['ram_limit_gb']}g",
            cpu_quota=int(server['cpu_limit'] * 100000)
        )
        
        await db.servers.update_one(
            {"id": server_id},
            {"$set": {"container_id": container.id, "status": "running"}}
        )
        
        return {"message": "Server started successfully", "container_id": container.id}
    except Exception as e:
        await db.servers.update_one({"id": server_id}, {"$set": {"status": "error"}})
        raise HTTPException(status_code=500, detail=f"Failed to start server: {str(e)}")

@api_router.post("/servers/{server_id}/stop")
async def stop_server(server_id: str, current_user: User = Depends(get_current_user)):
    server = await db.servers.find_one({"id": server_id}, {"_id": 0})
    if not server or not server.get("container_id"):
        raise HTTPException(status_code=404, detail="Server not found or not running")
    
    if not docker_client:
        raise HTTPException(status_code=503, detail="Docker not available")
    
    try:
        container = docker_client.containers.get(server["container_id"])
        container.stop()
        await db.servers.update_one({"id": server_id}, {"$set": {"status": "stopped"}})
        return {"message": "Server stopped successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to stop server: {str(e)}")

@api_router.post("/servers/{server_id}/restart")
async def restart_server(server_id: str, current_user: User = Depends(get_current_user)):
    await stop_server(server_id, current_user)
    await asyncio.sleep(2)
    return await start_server(server_id, current_user)

@api_router.delete("/servers/{server_id}")
async def delete_server(server_id: str, current_user: User = Depends(get_current_user)):
    server = await db.servers.find_one({"id": server_id}, {"_id": 0})
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    if server.get("container_id") and docker_client:
        try:
            container = docker_client.containers.get(server["container_id"])
            container.stop()
            container.remove()
        except:
            pass
    
    await db.servers.delete_one({"id": server_id})
    return {"message": "Server deleted successfully"}

# File Management Routes
@api_router.get("/servers/{server_id}/files")
async def list_files(server_id: str, path: str = "/", current_user: User = Depends(get_current_user)):
    server = await db.servers.find_one({"id": server_id}, {"_id": 0})
    if not server or not server.get("container_id"):
        raise HTTPException(status_code=404, detail="Server not found or not running")
    
    # Mock file listing for now
    files = [
        {"name": "server.cfg", "type": "file", "size": 1024, "modified": datetime.now(timezone.utc).isoformat()},
        {"name": "mods", "type": "directory", "size": 0, "modified": datetime.now(timezone.utc).isoformat()},
        {"name": "missions", "type": "directory", "size": 0, "modified": datetime.now(timezone.utc).isoformat()},
    ]
    return {"path": path, "files": files}

@api_router.post("/servers/{server_id}/files/upload")
async def upload_file(server_id: str, file: UploadFile = File(...), path: str = "/", current_user: User = Depends(get_current_user)):
    server = await db.servers.find_one({"id": server_id}, {"_id": 0})
    if not server:
        raise HTTPException(status_code=404, detail="Server not found")
    
    return {"message": "File uploaded successfully", "filename": file.filename}

# Arma 3 Workshop Integration
@api_router.post("/servers/{server_id}/arma3/modlist")
async def upload_arma3_modlist(server_id: str, file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    server = await db.servers.find_one({"id": server_id}, {"_id": 0})
    if not server or server["game_type"] != "arma3":
        raise HTTPException(status_code=400, detail="Server must be Arma 3")
    
    content = await file.read()
    html_content = content.decode('utf-8')
    
    soup = BeautifulSoup(html_content, 'html.parser')
    mods = []
    
    for link in soup.find_all('a', href=True):
        href = link['href']
        if 'steamcommunity.com/sharedfiles' in href or 'workshop' in href:
            mod_id = re.search(r'id=(\d+)', href)
            if mod_id:
                mods.append({
                    "id": mod_id.group(1),
                    "name": link.get_text(strip=True),
                    "url": href
                })
    
    mod_list = ModList(
        server_id=server_id,
        name=file.filename,
        mods=mods
    )
    
    mod_dict = mod_list.model_dump()
    mod_dict["created_at"] = mod_dict["created_at"].isoformat()
    
    await db.mod_lists.insert_one(mod_dict)
    return {"message": "Mod list uploaded", "mods_count": len(mods), "mods": mods}

@api_router.get("/servers/{server_id}/arma3/modlists")
async def get_arma3_modlists(server_id: str, current_user: User = Depends(get_current_user)):
    mod_lists = await db.mod_lists.find({"server_id": server_id}, {"_id": 0}).to_list(1000)
    return mod_lists

# Sub-User Management
@api_router.get("/users", response_model=List[User])
async def get_users(current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can view users")
    users = await db.users.find({}, {"_id": 0, "hashed_password": 0}).to_list(1000)
    for user in users:
        if isinstance(user.get("created_at"), str):
            user["created_at"] = datetime.fromisoformat(user["created_at"])
    return users

@api_router.put("/users/{user_id}/permissions")
async def update_user_permissions(user_id: str, permissions: Dict[str, Any], current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can update permissions")
    
    await db.users.update_one({"id": user_id}, {"$set": {"permissions": permissions}})
    return {"message": "Permissions updated successfully"}

# Server Selling
@api_router.get("/selling/config")
async def get_selling_config(current_user: User = Depends(get_current_user)):
    config = await db.selling_config.find_one({}, {"_id": 0})
    if not config:
        config = ServerSelling().model_dump()
    return config

@api_router.put("/selling/config")
async def update_selling_config(config_data: ServerSelling, current_user: User = Depends(get_current_user)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can update selling config")
    
    config_dict = config_data.model_dump()
    config_dict["created_at"] = config_dict["created_at"].isoformat()
    
    await db.selling_config.update_one({}, {"$set": config_dict}, upsert=True)
    return {"message": "Selling config updated successfully"}

# Stats
@api_router.get("/stats")
async def get_stats(current_user: User = Depends(get_current_user)):
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

# Include router
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=os.environ.get('CORS_ORIGINS', '*').split(','),
    allow_methods=["*"],
    allow_headers=["*"],
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()