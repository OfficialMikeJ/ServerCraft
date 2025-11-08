#!/usr/bin/env python3
"""
Create a test admin user for testing purposes
"""

import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
import os
from dotenv import load_dotenv
from pathlib import Path
import uuid
from datetime import datetime, timezone
from passlib.context import CryptContext

# Load environment
ROOT_DIR = Path(__file__).parent / "backend"
load_dotenv(ROOT_DIR / '.env')

mongo_url = os.environ['MONGO_URL']
db_name = os.environ['DB_NAME']

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

async def create_test_admin():
    client = AsyncIOMotorClient(mongo_url)
    db = client[db_name]
    
    # Check if test admin already exists
    existing = await db.users.find_one({"email": "testadmin@servercraft.com"})
    if existing:
        print("Test admin user already exists")
        client.close()
        return
    
    # Create test admin user
    test_admin = {
        "id": str(uuid.uuid4()),
        "username": "testadmin",
        "email": "testadmin@servercraft.com",
        "hashed_password": pwd_context.hash("testpassword123"),
        "role": "admin",
        "permissions": {},
        "locked": False,
        "created_at": datetime.now(timezone.utc)
    }
    
    await db.users.insert_one(test_admin)
    print("Test admin user created:")
    print("  Email: testadmin@servercraft.com")
    print("  Password: testpassword123")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(create_test_admin())