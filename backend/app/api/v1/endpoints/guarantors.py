from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime
from app.db.database import get_db
from app.models import Member, Loan, LoanGuarantor
from app.core.security import get_current_member

router = APIRouter()


class LoanGuarantorCreate(BaseModel):
    member_id: str
    amount_guaranteed: float


class LoanGuarantorResponse(BaseModel):
    id: str
    loan_id: str
    member_id: str
    status: str
    amount_guaranteed: str
    created_at: datetime
    
    class Config:
        from_attributes = True


@router.get("/loans/{loan_id}/guarantors", response_model=List[LoanGuarantorResponse])
def get_loan_guarantors(
    loan_id: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Get guarantors for a loan"""
    # Verify loan belongs to org
    loan = db.query(Loan).filter(
        Loan.id == loan_id,
        Loan.organization_id == current.organization_id
    ).first()
    
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    
    guarantors = db.query(LoanGuarantor).filter(
        LoanGuarantor.loan_id == loan_id
    ).all()
    
    # Get member names
    member_ids = [g.member_id for g in guarantors]
    members = db.query(Member).filter(Member.id.in_(member_ids)).all()
    member_map = {m.id: m.name for m in members}
    
    result = []
    for g in guarantors:
        result.append({
            **LoanGuarantorResponse.model_validate(g).model_dump(),
            "member_name": member_map.get(g.member_id, "Unknown")
        })
    
    return result


@router.post("/loans/{loan_id}/guarantors", response_model=LoanGuarantorResponse, status_code=201)
def add_guarantor(
    loan_id: str,
    guarantor: LoanGuarantorCreate,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Add guarantor to a loan (Chair/Treasurer only)"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Verify loan
    loan = db.query(Loan).filter(
        Loan.id == loan_id,
        Loan.organization_id == current.organization_id
    ).first()
    
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    
    # Verify member
    member = db.query(Member).filter(
        Member.id == guarantor.member_id,
        Member.organization_id == current.organization_id
    ).first()
    
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    # Check if already a guarantor
    existing = db.query(LoanGuarantor).filter(
        LoanGuarantor.loan_id == loan_id,
        LoanGuarantor.member_id == guarantor.member_id
    ).first()
    
    if existing:
        raise HTTPException(status_code=400, detail="Already a guarantor")
    
    new_guarantor = LoanGuarantor(
        loan_id=loan_id,
        member_id=guarantor.member_id,
        amount_guaranteed=str(guarantor.amount_guaranteed),
    )
    db.add(new_guarantor)
    db.commit()
    db.refresh(new_guarantor)
    return new_guarantor


@router.patch("/loans/{loan_id}/guarantors/{guarantor_id}/approve")
def approve_guarantor(
    loan_id: str,
    guarantor_id: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Approve guarantor (Chair/Treasurer only)"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    guarantor = db.query(LoanGuarantor).filter(
        LoanGuarantor.id == guarantor_id,
        LoanGuarantor.loan_id == loan_id
    ).first()
    
    if not guarantor:
        raise HTTPException(status_code=404, detail="Guarantor not found")
    
    guarantor.status = "APPROVED"
    guarantor.responded_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Guarantor approved"}


@router.patch("/loans/{loan_id}/guarantors/{guarantor_id}/reject")
def reject_guarantor(
    loan_id: str,
    guarantor_id: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Reject guarantor"""
    guarantor = db.query(LoanGuarantor).filter(
        LoanGuarantor.id == guarantor_id,
        LoanGuarantor.loan_id == loan_id
    ).first()
    
    if not guarantor:
        raise HTTPException(status_code=404, detail="Guarantor not found")
    
    # Only the guarantor themselves or Chair can reject
    if current.role not in ["TREASURER", "CHAIR"] and current.id != guarantor.member_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    guarantor.status = "REJECTED"
    guarantor.responded_at = datetime.utcnow()
    db.commit()
    
    return {"message": "Guarantor rejected"}


@router.delete("/loans/{loan_id}/guarantors/{guarantor_id}")
def remove_guarantor(
    loan_id: str,
    guarantor_id: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Remove guarantor from loan"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    guarantor = db.query(LoanGuarantor).filter(
        LoanGuarantor.id == guarantor_id,
        LoanGuarantor.loan_id == loan_id
    ).first()
    
    if not guarantor:
        raise HTTPException(status_code=404, detail="Guarantor not found")
    
    db.delete(guarantor)
    db.commit()
    
    return {"message": "Guarantor removed"}
