"""
ServerCraft Billing Plugin

Adds billing capabilities to ServerCraft for monetizing game servers.
Supports per-slot and per-server pricing with multiple subscription periods.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging
import uuid

logger = logging.getLogger(__name__)
router = APIRouter()

# Database will be injected by plugin system
db = None

class BillingPlan(BaseModel):
    """Billing plan configuration"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    pricing_type: str  # 'per_slot' or 'per_server'
    price_monthly: float
    price_3months: Optional[float] = None
    price_6months: Optional[float] = None
    price_12months: Optional[float] = None
    currency: str = "USD"
    active: bool = True
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class Subscription(BaseModel):
    """Server subscription"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    server_id: str
    plan_id: str
    user_id: str
    billing_period: str  # '1month', '3months', '6months', '12months'
    slots: Optional[int] = None  # For per-slot billing
    total_price: float
    status: str = "active"  # 'active', 'suspended', 'cancelled'
    start_date: str = Field(default_factory=lambda: datetime.now().isoformat())
    end_date: str
    auto_renew: bool = True
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat())

class CreatePlanRequest(BaseModel):
    name: str
    description: Optional[str] = None
    pricing_type: str
    price_monthly: float
    price_3months: Optional[float] = None
    price_6months: Optional[float] = None
    price_12months: Optional[float] = None

class CreateSubscriptionRequest(BaseModel):
    server_id: str
    plan_id: str
    billing_period: str
    slots: Optional[int] = None

def init_plugin(database, config: Dict[str, Any]):
    """
    Initialize billing plugin
    """
    global db
    db = database
    logger.info("Billing plugin initialized")
    return True

def cleanup_plugin():
    """
    Cleanup billing plugin
    """
    logger.info("Billing plugin cleaned up")
    pass

@router.get("/billing/plans", response_model=List[BillingPlan])
async def get_billing_plans():
    """
    Get all billing plans
    """
    try:
        plans = await db.billing_plans.find({"active": True}, {"_id": 0}).to_list(length=None)
        return plans
    except Exception as e:
        logger.error(f"Failed to fetch billing plans: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch billing plans")

@router.post("/billing/plans", response_model=BillingPlan)
async def create_billing_plan(plan: CreatePlanRequest):
    """
    Create a new billing plan (Admin only)
    """
    try:
        # Validate pricing type
        if plan.pricing_type not in ["per_slot", "per_server"]:
            raise HTTPException(status_code=400, detail="Invalid pricing type")
        
        billing_plan = BillingPlan(**plan.dict())
        await db.billing_plans.insert_one(billing_plan.dict())
        
        logger.info(f"Created billing plan: {billing_plan.name}")
        return billing_plan
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create billing plan: {e}")
        raise HTTPException(status_code=500, detail="Failed to create billing plan")

@router.get("/billing/subscriptions", response_model=List[Subscription])
async def get_subscriptions(user_id: Optional[str] = None):
    """
    Get subscriptions (filtered by user if provided)
    """
    try:
        query = {}
        if user_id:
            query["user_id"] = user_id
        
        subscriptions = await db.billing_subscriptions.find(query, {"_id": 0}).to_list(length=None)
        return subscriptions
    except Exception as e:
        logger.error(f"Failed to fetch subscriptions: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch subscriptions")

@router.post("/billing/subscribe", response_model=Subscription)
async def create_subscription(request: CreateSubscriptionRequest, user_id: str):
    """
    Create a new subscription for a server
    """
    try:
        # Get billing plan
        plan = await db.billing_plans.find_one({"id": request.plan_id}, {"_id": 0})
        if not plan:
            raise HTTPException(status_code=404, detail="Billing plan not found")
        
        # Calculate price based on billing period
        price_map = {
            "1month": plan["price_monthly"],
            "3months": plan.get("price_3months", plan["price_monthly"] * 3),
            "6months": plan.get("price_6months", plan["price_monthly"] * 6),
            "12months": plan.get("price_12months", plan["price_monthly"] * 12)
        }
        
        if request.billing_period not in price_map:
            raise HTTPException(status_code=400, detail="Invalid billing period")
        
        total_price = price_map[request.billing_period]
        
        # If per-slot pricing, multiply by slots
        if plan["pricing_type"] == "per_slot":
            if not request.slots:
                raise HTTPException(status_code=400, detail="Slots required for per-slot pricing")
            total_price *= request.slots
        
        # Calculate end date
        months = int(request.billing_period.replace("months", "").replace("month", ""))
        end_date = (datetime.now() + timedelta(days=30 * months)).isoformat()
        
        # Create subscription
        subscription = Subscription(
            server_id=request.server_id,
            plan_id=request.plan_id,
            user_id=user_id,
            billing_period=request.billing_period,
            slots=request.slots,
            total_price=total_price,
            end_date=end_date
        )
        
        await db.billing_subscriptions.insert_one(subscription.dict())
        
        logger.info(f"Created subscription for server {request.server_id}")
        return subscription
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create subscription: {e}")
        raise HTTPException(status_code=500, detail="Failed to create subscription")

@router.put("/billing/subscription/{subscription_id}/cancel")
async def cancel_subscription(subscription_id: str):
    """
    Cancel a subscription
    """
    try:
        result = await db.billing_subscriptions.update_one(
            {"id": subscription_id},
            {"$set": {"status": "cancelled", "auto_renew": False}}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Subscription not found")
        
        logger.info(f"Cancelled subscription: {subscription_id}")
        return {"success": True, "message": "Subscription cancelled"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel subscription: {e}")
        raise HTTPException(status_code=500, detail="Failed to cancel subscription")
