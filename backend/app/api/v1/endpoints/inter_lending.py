from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta
from app.db.database import get_db
from app.models import Member, Organization
from app.core.security import get_current_member

router = APIRouter()


class InterChamaLoanCreate(BaseModel):
    borrower_organization_id: str
    federation_id: str
    amount: float
    interest_rate: float = 8.0
    purpose: str = None
    duration_months: int = 6


class InterChamaLoanResponse(BaseModel):
    id: str
    lender_organization_id: str
    borrower_organization_id: str
    federation_id: str
    amount: float
    interest_rate: str
    status: str
    purpose: str = None
    created_at: datetime
    due_date: datetime = None
    
    class Config:
        from_attributes = True


# === INTER-CHAMA LENDING ===

@router.get("/inter-lending", response_model=List[InterChamaLoanResponse])
def list_inter_chama_loans(
    as_lender: bool = None,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """List inter-chama loans"""
    query = db.query(InterChamaLoan).filter(
        (InterChamaLoan.lender_organization_id == current.organization_id) |
        (InterChamaLoan.borrower_organization_id == current.organization_id)
    )
    
    if as_lender is not None:
        if as_lender:
            query = query.filter(InterChamaLoan.lender_organization_id == current.organization_id)
        else:
            query = query.filter(InterChamaLoan.borrower_organization_id == current.organization_id)
    
    return query.order_by(InterChamaLoan.created_at.desc()).all()


@router.get("/inter-lending/{loan_id}", response_model=InterChamaLoanResponse)
def get_inter_chama_loan(
    loan_id: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Get inter-chama loan details"""
    loan = db.query(InterChamaLoan).filter(InterChamaLoan.id == loan_id).first()
    
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    
    # Verify access
    if (loan.lender_organization_id != current.organization_id and 
        loan.borrower_organization_id != current.organization_id):
        raise HTTPException(status_code=403, detail="Not authorized")
    
    return loan


@router.post("/inter-lending", response_model=InterChamaLoanResponse)
def request_inter_chama_loan(
    loan_req: InterChamaLoanCreate,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Request a loan from another chama"""
    # Verify both orgs are in the federation
    lender_member = db.query(FederationMember).filter(
        FederationMember.federation_id == loan_req.federation_id,
        FederationMember.organization_id == current.organization_id
    ).first()
    
    borrower_member = db.query(FederationMember).filter(
        FederationMember.federation_id == loan_req.federation_id,
        FederationMember.organization_id == loan_req.borrower_organization_id
    ).first()
    
    if not lender_member or not borrower_member:
        raise HTTPException(status_code=400, detail="Both organizations must be federation members")
    
    # Check federation allows inter-lending
    federation = db.query(Federation).filter(Federation.id == loan_req.federation_id).first()
    if not federation or not federation.allow_inter_lending:
        raise HTTPException(status_code=400, detail="Inter-lending not allowed in this federation")
    
    # Create loan request
    due_date = datetime.utcnow() + timedelta(days=30 * loan_req.duration_months)
    
    new_loan = InterChamaLoan(
        lender_organization_id=current.organization_id,
        borrower_organization_id=loan_req.borrower_organization_id,
        federation_id=loan_req.federation_id,
        amount=loan_req.amount,
        interest_rate=str(loan_req.interest_rate),
        purpose=loan_req.purpose,
        due_date=due_date
    )
    db.add(new_loan)
    db.commit()
    db.refresh(new_loan)
    
    return new_loan


@router.post("/inter-lending/{loan_id}/approve")
def approve_inter_chama_loan(
    loan_id: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Approve inter-chama loan (lender's leadership)"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    loan = db.query(InterChamaLoan).filter(InterChamaLoan.id == loan_id).first()
    
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    
    if loan.lender_organization_id != current.organization_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if loan.status != InterChamaLoanStatus.PENDING:
        raise HTTPException(status_code=400, detail="Loan already processed")
    
    loan.status = InterChamaLoanStatus.APPROVED
    loan.approved_by = current.id
    loan.approved_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Loan approved"}


@router.post("/inter-lending/{loan_id}/disburse")
def disburse_inter_chama_loan(
    loan_id: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Disburse approved loan"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    loan = db.query(InterChamaLoan).filter(InterChamaLoan.id == loan_id).first()
    
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    
    if loan.lender_organization_id != current.organization_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if loan.status != InterChamaLoanStatus.APPROVED:
        raise HTTPException(status_code=400, detail="Loan must be approved first")
    
    loan.status = InterChamaLoanStatus.ACTIVE
    loan.disbursed_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Loan disbursed"}


@router.post("/inter-lending/{loan_id}/repay")
def repay_inter_chama_loan(
    loan_id: str,
    amount: float,
    note: str = None,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Record repayment"""
    loan = db.query(InterChamaLoan).filter(InterChamaLoan.id == loan_id).first()
    
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    
    if loan.borrower_organization_id != current.organization_id:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    if loan.status != InterChamaLoanStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Loan not active")
    
    # Calculate interest
    loan_amount = float(loan.amount)
    rate = float(loan.interest_rate)
    interest = (loan_amount * rate / 100) * 6 / 12  # Simplified 6-month calc
    principal = amount - interest
    
    # Record repayment
    repayment = InterChamaRepayment(
        loan_id=loan_id,
        amount=amount,
        principal=principal,
        interest=interest,
        paid_by=current.id,
        note=note
    )
    db.add(repayment)
    
    # Check if fully repaid
    total_paid = db.query(InterChamaRepayment).filter(
        InterChamaRepayment.loan_id == loan_id
    ).all()
    
    total = sum(r.amount for r in total_paid) + amount
    if total >= loan_amount + interest:
        loan.status = InterChamaLoanStatus.REPAID
        loan.fully_repaid_at = datetime.utcnow()
    
    db.commit()
    
    return {"message": "Repayment recorded"}


@router.get("/inter-lending/{loan_id}/repayments")
def get_loan_repayments(
    loan_id: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Get repayment history"""
    loan = db.query(InterChamaLoan).filter(InterChamaLoan.id == loan_id).first()
    
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    
    repayments = db.query(InterChamaRepayment).filter(
        InterChamaRepayment.loan_id == loan_id
    ).order_by(InterChamaRepayment.paid_at.desc()).all()
    
    return [
        {
            "id": r.id,
            "amount": float(r.amount),
            "principal": float(r.principal),
            "interest": float(r.interest),
            "paid_at": r.paid_at.isoformat()
        }
        for r in repayments
    ]
