from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from app.db.database import get_db
from app.models import Member
from app.core.security import get_current_member

router = APIRouter()


class InvestmentCreate(BaseModel):
    name: str
    investment_type: str
    principal: float
    expected_return: float = 0
    investment_date: datetime
    maturity_date: datetime = None
    institution: str = None
    account_number: str = None
    notes: str = None


class InvestmentUpdate(BaseModel):
    name: str = None
    status: str = None
    current_value: float = None
    expected_return: float = None
    actual_return: float = None
    maturity_date: datetime = None
    notes: str = None


class InvestmentResponse(BaseModel):
    id: str
    organization_id: str
    name: str
    investment_type: str
    status: str
    principal: float
    current_value: float
    expected_return: float
    actual_return: float
    investment_date: datetime
    maturity_date: datetime = None
    institution: str = None
    
    class Config:
        from_attributes = True


@router.get("/investments", response_model=List[InvestmentResponse])
def list_investments(
    investment_type: str = None,
    status: str = "ACTIVE",
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """List all investments"""
    query = db.query(Investment).filter(
        Investment.organization_id == current.organization_id
    )
    
    if investment_type:
        query = query.filter(Investment.investment_type == investment_type)
    if status:
        query = query.filter(Investment.status == status)
    
    return query.order_by(Investment.investment_date.desc()).all()


@router.get("/investments/{investment_id}", response_model=InvestmentResponse)
def get_investment(
    investment_id: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Get investment details"""
    investment = db.query(Investment).filter(
        Investment.id == investment_id,
        Investment.organization_id == current.organization_id
    ).first()
    
    if not investment:
        raise HTTPException(status_code=404, detail="Investment not found")
    
    return investment


@router.post("/investments", response_model=InvestmentResponse, status_code=201)
def create_investment(
    investment: InvestmentCreate,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Create investment (Chair/Treasurer only)"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    new_investment = Investment(
        organization_id=current.organization_id,
        name=investment.name,
        investment_type=investment.investment_type,
        principal=investment.principal,
        current_value=investment.principal,
        expected_return=investment.expected_return,
        investment_date=investment.investment_date,
        maturity_date=investment.maturity_date,
        institution=investment.institution,
        account_number=investment.account_number,
        notes=investment.notes
    )
    db.add(new_investment)
    db.commit()
    db.refresh(new_investment)
    return new_investment


@router.patch("/investments/{investment_id}", response_model=InvestmentResponse)
def update_investment(
    investment_id: str,
    investment_update: InvestmentUpdate,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Update investment"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    investment = db.query(Investment).filter(
        Investment.id == investment_id,
        Investment.organization_id == current.organization_id
    ).first()
    
    if not investment:
        raise HTTPException(status_code=404, detail="Investment not found")
    
    for field, value in investment_update.model_dump(exclude_unset=True).items():
        setattr(investment, field, value)
    
    db.commit()
    db.refresh(investment)
    return investment


@router.delete("/investments/{investment_id}")
def delete_investment(
    investment_id: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Delete investment"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    investment = db.query(Investment).filter(
        Investment.id == investment_id,
        Investment.organization_id == current.organization_id
    ).first()
    
    if not investment:
        raise HTTPException(status_code=404, detail="Investment not found")
    
    db.delete(investment)
    db.commit()
    
    return {"message": "Investment deleted"}


@router.get("/investments/summary")
def investments_summary(
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Get investment summary"""
    investments = db.query(Investment).filter(
        Investment.organization_id == current.organization_id,
        Investment.status != "CLOSED"
    ).all()
    
    total_invested = sum(float(i.principal) for i in investments)
    total_current = sum(float(i.current_value or 0) for i in investments)
    total_expected = sum(float(i.principal) * (1 + float(i.expected_return or 0)/100) for i in investments)
    
    gains = total_current - total_invested
    
    return {
        "total_investments": len(investments),
        "total_invested": total_invested,
        "current_value": total_current,
        "expected_value": total_expected,
        "total_gains": gains,
        "gains_percent": round((gains / total_invested * 100), 2) if total_invested > 0 else 0
    }


@router.post("/investments/{investment_id}/returns")
def add_return(
    investment_id: str,
    amount: float,
    return_type: str = "INTEREST",
    notes: str = None,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Record investment return"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    investment = db.query(Investment).filter(
        Investment.id == investment_id,
        Investment.organization_id == current.organization_id
    ).first()
    
    if not investment:
        raise HTTPException(status_code=404, detail="Investment not found")
    
    # Record return
    return_record = InvestmentReturn(
        investment_id=investment_id,
        amount=amount,
        return_type=return_type,
        notes=notes
    )
    db.add(return_record)
    
    # Update current value
    investment.current_value = float(investment.current_value or 0) + amount
    
    db.commit()
    
    return {"message": "Return recorded", "new_value": float(investment.current_value)}


@router.post("/investments/{investment_id}/close")
def close_investment(
    investment_id: str,
    final_value: float,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Close an investment"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    investment = db.query(Investment).filter(
        Investment.id == investment_id,
        Investment.organization_id == current.organization_id
    ).first()
    
    if not investment:
        raise HTTPException(status_code=404, detail="Investment not found")
    
    investment.status = InvestmentStatus.CLOSED
    investment.current_value = final_value
    investment.closed_date = datetime.utcnow()
    
    # Calculate actual return
    principal = float(investment.principal)
    if principal > 0:
        investment.actual_return = ((final_value - principal) / principal) * 100
    
    db.commit()
    
    return {"message": "Investment closed", "final_value": final_value}
