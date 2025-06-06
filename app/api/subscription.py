# app/api/subscription.py
from fastapi import APIRouter, Depends, Form, HTTPException
from sqlalchemy.orm import Session
from app.models.user import SubscriptionPlan, User
from app.middleware.auth import get_current_user
from app.database import get_db

router = APIRouter()

@router.post("/subscription/update")
async def update_subscription(
    plan: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if plan not in SubscriptionPlan._value2member_map_:
        raise HTTPException(status_code=400, detail="Invalid subscription plan")

    current_user.subscription = SubscriptionPlan(plan)
    db.commit()
    return {"message": f"Subscription updated to {plan}"}
