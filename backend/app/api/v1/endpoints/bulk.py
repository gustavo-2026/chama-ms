from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from datetime import datetime
from decimal import Decimal
from app.db.database import get_db
from app.models import Member, Loan, Contribution, TransactionStatus
from app.core.security import get_current_member
import requests

router = APIRouter()


class DisbursementRequest(BaseModel):
    type: str  # dividend, loan_repayment, withdrawal
    period_month: int = None
    period_year: int = None
    amounts: dict = None  # {member_id: amount}


class BulkDisbursementResponse(BaseModel):
    total: float
    successful: int
    failed: int
    transactions: list


@router.post("/bulk-disbursement", response_model=BulkDisbursementResponse)
def bulk_disbursement(
    request: DisbursementRequest,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Bulk disburse funds to members (Chair/Treasurer only)"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    org_id = current.organization_id
    
    # Get recipients and amounts
    if request.type == "dividend":
        if not request.period_month or not request.period_year:
            raise HTTPException(status_code=400, detail="Period required for dividends")
        
        # Get contributions for period
        contributions = db.query(Contribution).filter(
            Contribution.organization_id == org_id,
            Contribution.period_month == request.period_month,
            Contribution.period_year == request.period_year,
            Contribution.status == TransactionStatus.COMPLETED
        ).all()
        
        # Calculate totals per member
        member_amounts = {}
        for c in contributions:
            member_amounts[c.member_id] = member_amounts.get(c.member_id, 0) + float(c.amount)
        
        # Get members with M-Pesa
        recipients = []
        for mid, amount in member_amounts.items():
            member = db.query(Member).filter(Member.id == mid).first()
            if member and member.mpesa_linked and member.mpesa_phone:
                recipients.append({
                    "member_id": mid,
                    "phone": member.mpesa_phone,
                    "amount": amount / len(member_amounts)  # Equal split
                })
    
    elif request.type == "custom" and request.amounts:
        # Custom amounts
        recipients = []
        for mid, amount in request.amounts.items():
            member = db.query(Member).filter(Member.id == mid).first()
            if member and member.mpesa_linked and member.mpesa_phone:
                recipients.append({
                    "member_id": mid,
                    "phone": member.mpesa_phone,
                    "amount": amount
                })
    
    else:
        raise HTTPException(status_code=400, detail="Invalid request")
    
    # Process disbursements (simplified - in production, call M-Pesa B2C API)
    successful = 0
    failed = 0
    transactions = []
    
    for recipient in recipients:
        # TODO: Actually call M-Pesa B2C here
        # For now, simulate
        transactions.append({
            "member_id": recipient["member_id"],
            "phone": recipient["phone"],
            "amount": recipient["amount"],
            "status": "queued"  # Would be "success" or "failed" after API call
        })
        successful += 1
    
    return BulkDisbursementResponse(
        total=sum(r["amount"] for r in recipients),
        successful=successful,
        failed=failed,
        transactions=transactions
    )


@router.get("/reconciliation")
def reconciliation(
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """M-Pesa transaction reconciliation"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    org_id = current.organization_id
    
    # Get all completed contributions
    contributions = db.query(Contribution).filter(
        Contribution.organization_id == org_id,
        Contribution.method == "MPESA",
        Contribution.status == TransactionStatus.COMPLETED
    ).all()
    
    total_contributions = sum(float(c.amount) for c in contributions)
    
    # Summary
    return {
        "period": datetime.utcnow().strftime("%Y-%m"),
        "total_contributions": total_contributions,
        "contribution_count": len(contributions),
        "average_contribution": total_contributions / len(contributions) if contributions else 0,
        # In production, would compare with M-Pesa API statements
    }
