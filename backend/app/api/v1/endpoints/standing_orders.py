from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime, timedelta
from app.db.database import get_db
from app.models import Member, StandingOrder
from app.core.security import get_current_member

router = APIRouter()


class StandingOrderCreate(BaseModel):
    member_id: str
    amount: float
    frequency: str  # weekly, biweekly, monthly
    day_of_week: int = None  # 0=Monday, 6=Sunday
    day_of_month: int = None  # 1-31


class StandingOrderResponse(BaseModel):
    id: str
    organization_id: str
    member_id: str
    amount: float
    frequency: str
    day_of_week: int = None
    day_of_month: int = None
    status: str
    last_run: datetime = None
    next_run: datetime = None
    created_at: datetime
    
    class Config:
        from_attributes = True


def calculate_next_run(frequency: str, day_of_week: int = None, day_of_month: int = None) -> datetime:
    """Calculate next run date for standing order"""
    now = datetime.utcnow()
    
    if frequency == "weekly":
        # Next occurrence of day_of_week
        days_ahead = day_of_week - now.weekday()
        if days_ahead <= 0:
            days_ahead += 7
        return now + timedelta(days=days_ahead)
    
    elif frequency == "biweekly":
        days_ahead = 14
        return now + timedelta(days=days_ahead)
    
    elif frequency == "monthly":
        # Next occurrence of day_of_month
        if day_of_month and day_of_month <= 28:
            if now.day <= day_of_month:
                return now.replace(day=day_of_month)
            else:
                return (now + timedelta(days=32)).replace(day=day_of_month)
        # Default to 1st of next month
        return (now + timedelta(days=32)).replace(day=1)
    
    return now + timedelta(days=30)


@router.get("/standing-orders", response_model=List[StandingOrderResponse])
def list_standing_orders(
    status: str = None,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """List standing orders"""
    query = db.query(StandingOrder).filter(
        StandingOrder.organization_id == current.organization_id
    )
    if status:
        query = query.filter(StandingOrder.status == status)
    return query.order_by(StandingOrder.created_at.desc()).all()


@router.post("/standing-orders", response_model=StandingOrderResponse, status_code=201)
def create_standing_order(
    order: StandingOrderCreate,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Create a standing order (member or Chair/Treasurer)"""
    # Verify member
    member = db.query(Member).filter(
        Member.id == order.member_id,
        Member.organization_id == current.organization_id
    ).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    # Verify frequency
    if order.frequency not in ["weekly", "biweekly", "monthly"]:
        raise HTTPException(status_code=400, detail="Invalid frequency")
    
    new_order = StandingOrder(
        organization_id=current.organization_id,
        member_id=order.member_id,
        amount=order.amount,
        frequency=order.frequency,
        day_of_week=order.day_of_week,
        day_of_month=order.day_of_month,
        next_run=calculate_next_run(order.frequency, order.day_of_week, order.day_of_month)
    )
    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order


@router.patch("/standing-orders/{order_id}/pause")
def pause_standing_order(
    order_id: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Pause a standing order"""
    order = db.query(StandingOrder).filter(
        StandingOrder.id == order_id,
        StandingOrder.organization_id == current.organization_id
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Standing order not found")
    
    order.status = "PAUSED"
    db.commit()
    return {"message": "Standing order paused"}


@router.patch("/standing-orders/{order_id}/resume")
def resume_standing_order(
    order_id: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Resume a standing order"""
    order = db.query(StandingOrder).filter(
        StandingOrder.id == order_id,
        StandingOrder.organization_id == current.organization_id
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Standing order not found")
    
    order.status = "ACTIVE"
    order.next_run = calculate_next_run(order.frequency, order.day_of_week, order.day_of_month)
    db.commit()
    return {"message": "Standing order resumed"}


@router.delete("/standing-orders/{order_id}")
def cancel_standing_order(
    order_id: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Cancel a standing order"""
    order = db.query(StandingOrder).filter(
        StandingOrder.id == order_id,
        StandingOrder.organization_id == current.organization_id
    ).first()
    if not order:
        raise HTTPException(status_code=404, detail="Standing order not found")
    
    order.status = "CANCELLED"
    db.commit()
    return {"message": "Standing order cancelled"}
