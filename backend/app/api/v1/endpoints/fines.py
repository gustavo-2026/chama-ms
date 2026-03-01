from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
from app.db.database import get_db
from app.models import Member, Fine
from app.core.security import get_current_member

router = APIRouter()


class FineCreate(BaseModel):
    member_id: str
    reason: str  # LATE_CONTRIBUTION, ABSENT_MEETING, OTHER
    amount: Decimal
    note: str = None


class FineResponse(BaseModel):
    id: str
    organization_id: str
    member_id: str
    reason: str
    amount: Decimal
    status: str
    note: str = None
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.get("/fines", response_model=List[FineResponse])
def list_fines(
    status: str = None,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """List all fines"""
    query = db.query(Fine).filter(Fine.organization_id == current.organization_id)
    
    if status:
        query = query.filter(Fine.status == status)
    
    return query.order_by(Fine.created_at.desc()).all()


@router.post("/fines", response_model=FineResponse, status_code=201)
def create_fine(
    fine: FineCreate,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Create a fine (Chair/Treasurer only)"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Verify member
    member = db.query(Member).filter(
        Member.id == fine.member_id,
        Member.organization_id == current.organization_id
    ).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    new_fine = Fine(
        organization_id=current.organization_id,
        member_id=fine.member_id,
        reason=fine.reason,
        amount=fine.amount,
        note=fine.note,
    )
    db.add(new_fine)
    db.commit()
    db.refresh(new_fine)
    return new_fine


@router.patch("/fines/{fine_id}/pay", response_model=FineResponse)
def pay_fine(
    fine_id: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Mark fine as paid"""
    fine = db.query(Fine).filter(
        Fine.id == fine_id,
        Fine.organization_id == current.organization_id
    ).first()
    
    if not fine:
        raise HTTPException(status_code=404, detail="Fine not found")
    
    if fine.status != "PENDING":
        raise HTTPException(status_code=400, detail="Fine already settled")
    
    fine.status = "PAID"
    fine.paid_at = datetime.utcnow()
    db.commit()
    db.refresh(fine)
    return fine


@router.patch("/fines/{fine_id}/waive", response_model=FineResponse)
def waive_fine(
    fine_id: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Waive a fine (Chair only)"""
    if current.role != "CHAIR":
        raise HTTPException(status_code=403, detail="Only chair can waive fines")
    
    fine = db.query(Fine).filter(
        Fine.id == fine_id,
        Fine.organization_id == current.organization_id
    ).first()
    
    if not fine:
        raise HTTPException(status_code=404, detail="Fine not found")
    
    fine.status = "WAIVED"
    db.commit()
    db.refresh(fine)
    return fine


@router.get("/fines/summary")
def fines_summary(
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Get fines summary"""
    org_id = current.organization_id
    
    pending = db.query(Fine).filter(
        Fine.organization_id == org_id,
        Fine.status == "PENDING"
    ).all()
    
    paid = db.query(Fine).filter(
        Fine.organization_id == org_id,
        Fine.status == "PAID"
    ).all()
    
    return {
        "pending_count": len(pending),
        "pending_amount": sum(float(f.amount) for f in pending),
        "paid_count": len(paid),
        "paid_amount": sum(float(f.amount) for f in paid),
    }
