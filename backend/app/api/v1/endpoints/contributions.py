from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from decimal import Decimal
from datetime import datetime
from app.db.database import get_db
from app.models import Contribution, Member, TransactionStatus
from app.schemas.schemas import ContributionCreate, ContributionResponse, ContributionSummary

router = APIRouter()


def get_current_member(db: Session = Depends(get_db)):
    member = db.query(Member).first()
    if not member:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return member


@router.get("/", response_model=List[ContributionResponse])
def list_contributions(
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """List all contributions"""
    contributions = db.query(Contribution).filter(
        Contribution.organization_id == current.organization_id
    ).order_by(Contribution.created_at.desc()).all()
    return contributions


@router.post("/", response_model=ContributionResponse, status_code=status.HTTP_201_CREATED)
def create_contribution(
    contribution: ContributionCreate,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Record a new contribution"""
    # Verify member belongs to organization
    member = db.query(Member).filter(
        Member.id == contribution.member_id,
        Member.organization_id == current.organization_id
    ).first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    new_contribution = Contribution(
        organization_id=current.organization_id,
        member_id=contribution.member_id,
        amount=contribution.amount,
        method=contribution.method,
        period_month=contribution.period_month,
        period_year=contribution.period_year,
        note=contribution.note,
        status=TransactionStatus.COMPLETED,  # Cash contributions are completed immediately
    )
    db.add(new_contribution)
    db.commit()
    db.refresh(new_contribution)
    return new_contribution


@router.get("/summary", response_model=ContributionSummary)
def contribution_summary(
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Get contribution summary"""
    org_id = current.organization_id
    
    # Total contributions
    total = db.query(Contribution).filter(
        Contribution.organization_id == org_id,
        Contribution.status == TransactionStatus.COMPLETED
    ).all()
    total_amount = sum(c.amount for c in total)
    
    # Member count
    member_count = db.query(Member).filter(Member.organization_id == org_id).count()
    
    # This month
    now = datetime.now()
    this_month = db.query(Contribution).filter(
        Contribution.organization_id == org_id,
        Contribution.period_month == now.month,
        Contribution.period_year == now.year,
        Contribution.status == TransactionStatus.COMPLETED
    ).all()
    month_amount = sum(c.amount for c in this_month)
    
    # Pending
    pending = db.query(Contribution).filter(
        Contribution.organization_id == org_id,
        Contribution.status == TransactionStatus.PENDING
    ).all()
    pending_amount = sum(p.amount for p in pending)
    
    return ContributionSummary(
        total_contributions=total_amount or Decimal("0"),
        member_count=member_count,
        this_month=month_amount or Decimal("0"),
        pending=pending_amount or Decimal("0"),
    )
