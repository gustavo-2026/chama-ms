from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal
from datetime import datetime, timedelta
from app.db.database import get_db
from app.models import Loan, Member, LoanStatus, LoanRepayment, TransactionStatus
from app.schemas.schemas import LoanCreate, LoanResponse, LoanRepaymentCreate, LoanRepaymentResponse

router = APIRouter()


def get_current_member(db: Session = Depends(get_db)):
    member = db.query(Member).first()
    if not member:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return member


@router.get("/", response_model=List[LoanResponse])
def list_loans(
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """List all loans"""
    loans = db.query(Loan).filter(
        Loan.organization_id == current.organization_id
    ).order_by(Loan.created_at.desc()).all()
    return loans


@router.post("/", response_model=LoanResponse, status_code=status.HTTP_201_CREATED)
def create_loan(
    loan: LoanCreate,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Apply for a loan"""
    # Verify member
    member = db.query(Member).filter(
        Member.id == loan.member_id,
        Member.organization_id == current.organization_id
    ).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    # Check for existing pending/active loans
    existing = db.query(Loan).filter(
        Loan.member_id == loan.member_id,
        Loan.status.in_([LoanStatus.PENDING, LoanStatus.ACTIVE])
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Member has an existing pending or active loan"
        )
    
    new_loan = Loan(
        organization_id=current.organization_id,
        member_id=loan.member_id,
        amount=loan.amount,
        interest_rate=loan.interest_rate,
        purpose=loan.purpose,
        status=LoanStatus.PENDING,
    )
    db.add(new_loan)
    db.commit()
    db.refresh(new_loan)
    return new_loan


@router.patch("/{loan_id}/approve", response_model=LoanResponse)
def approve_loan(
    loan_id: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Approve a loan (Treasurer/Chair only)"""
    loan = db.query(Loan).filter(
        Loan.id == loan_id,
        Loan.organization_id == current.organization_id
    ).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    
    if loan.status != LoanStatus.PENDING:
        raise HTTPException(status_code=400, detail="Loan is not pending")
    
    # Check role permission
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized to approve loans")
    
    loan.status = LoanStatus.ACTIVE
    loan.approved_at = datetime.utcnow()
    loan.due_date = datetime.utcnow() + timedelta(days=30)  # 30 days default
    
    db.commit()
    db.refresh(loan)
    return loan


@router.patch("/{loan_id}/reject", response_model=LoanResponse)
def reject_loan(
    loan_id: str,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Reject a loan"""
    loan = db.query(Loan).filter(
        Loan.id == loan_id,
        Loan.organization_id == current.organization_id
    ).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    
    if loan.status != LoanStatus.PENDING:
        raise HTTPException(status_code=400, detail="Loan is not pending")
    
    loan.status = LoanStatus.REJECTED
    db.commit()
    db.refresh(loan)
    return loan


@router.post("/{loan_id}/repay", response_model=LoanRepaymentResponse)
def repay_loan(
    loan_id: str,
    repayment: LoanRepaymentCreate,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Record a loan repayment"""
    loan = db.query(Loan).filter(
        Loan.id == loan_id,
        Loan.organization_id == current.organization_id
    ).first()
    if not loan:
        raise HTTPException(status_code=404, detail="Loan not found")
    
    if loan.status != LoanStatus.ACTIVE:
        raise HTTPException(status_code=400, detail="Loan is not active")
    
    new_repayment = LoanRepayment(
        loan_id=loan_id,
        amount=repayment.amount,
        method=repayment.method,
        status=TransactionStatus.COMPLETED,  # Assume completed for now
    )
    db.add(new_repayment)
    
    # Check if fully paid
    total_paid = sum(r.amount for r in loan.repayments) + repayment.amount
    if total_paid >= loan.amount:
        loan.status = LoanStatus.PAID
    
    db.commit()
    db.refresh(new_repayment)
    return new_repayment
