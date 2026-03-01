from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from decimal import Decimal
from app.db.database import get_db
from app.models import Member, Contribution, Loan, Contribution, TransactionStatus, LoanStatus
from app.schemas.schemas import TreasurySummary, DividendDisburseRequest

router = APIRouter()


def get_current_member(db: Session = Depends(get_db)):
    member = db.query(Member).first()
    if not member:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return member


@router.get("/summary", response_model=TreasurySummary)
def treasury_summary(
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Get treasury summary"""
    org_id = current.organization_id
    
    # Total capital (completed contributions)
    total = db.query(Contribution).filter(
        Contribution.organization_id == org_id,
        Contribution.status == TransactionStatus.COMPLETED
    ).all()
    total_capital = sum(c.amount for c in total)
    
    # Member count
    member_count = db.query(Member).filter(Member.organization_id == org_id).count()
    
    # Active loans (locked capital)
    active_loans = db.query(Loan).filter(
        Loan.organization_id == org_id,
        Loan.status == LoanStatus.ACTIVE
    ).all()
    locked = sum(l.amount for l in active_loans)
    
    # Available = total - locked
    available = total_capital - locked
    
    # Pending contributions
    pending = db.query(Contribution).filter(
        Contribution.organization_id == org_id,
        Contribution.status == TransactionStatus.PENDING
    ).all()
    pending_amount = sum(p.amount for p in pending)
    
    return TreasurySummary(
        total_capital=total_capital or Decimal("0"),
        available=available or Decimal("0"),
        locked_in_loans=locked or Decimal("0"),
        pending_contributions=pending_amount or Decimal("0"),
        member_count=member_count,
        active_loans=len(active_loans),
    )


@router.post("/disburse")
def disburse_dividends(
    request: DividendDisburseRequest,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Trigger dividend disbursement (B2C)"""
    # Check role
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Get contributions for the period
    contributions = db.query(Contribution).filter(
        Contribution.organization_id == current.organization_id,
        Contribution.period_month == request.period_month,
        Contribution.period_year == request.period_year,
        Contribution.status == TransactionStatus.COMPLETED
    ).all()
    
    if not contributions:
        raise HTTPException(status_code=400, detail="No contributions for this period")
    
    # Calculate dividend per member (simplified - equal split)
    total = sum(c.amount for c in contributions)
    members = db.query(Member).filter(Member.organization_id == current.organization_id).all()
    
    if not members:
        raise HTTPException(status_code=400, detail="No members found")
    
    dividend_per_member = total / len(members)
    
    # Queue B2C payments (simplified - in production, call M-Pesa B2C API)
    results = []
    for member in members:
        if member.mpesa_linked and member.mpesa_phone:
            results.append({
                "member_id": member.id,
                "phone": member.mpesa_phone,
                "amount": float(dividend_per_member),
                "status": "queued"
            })
    
    return {
        "period": f"{request.period_month}/{request.period_year}",
        "total_distributed": float(total),
        "per_member": float(dividend_per_member),
        "recipients": len(results),
        "payments": results
    }
