from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import Optional
from app.db.database import get_db
from app.models import Member, Contribution, Loan, TransactionStatus, LoanStatus
from app.core.security import get_current_member

router = APIRouter()


@router.get("/analytics/overview")
def analytics_overview(
    db: Session = Depends(get_db),
    current = Depends(get_current_member)
):
    """Get overview analytics"""
    org_id = current.organization_id
    
    # Member stats
    total_members = db.query(Member).filter(Member.organization_id == org_id).count()
    
    # Contribution stats
    contributions = db.query(Contribution).filter(
        Contribution.organization_id == org_id,
        Contribution.status == TransactionStatus.COMPLETED
    ).all()
    total_contributions = sum(float(c.amount) for c in contributions)
    
    # Loan stats
    active_loans = db.query(Loan).filter(
        Loan.organization_id == org_id,
        Loan.status == LoanStatus.ACTIVE
    ).all()
    total_outstanding = sum(float(l.amount) for l in active_loans)
    
    # Calculate percentages
    members_with_contributions = len(set(c.member_id for c in contributions))
    participation_rate = (members_with_contributions / total_members * 100) if total_members > 0 else 0
    
    return {
        "total_members": total_members,
        "participation_rate": round(participation_rate, 1),
        "total_contributions": total_contributions,
        "active_loans": len(active_loans),
        "total_outstanding": total_outstanding,
        "available": total_contributions - total_outstanding,
    }


@router.get("/analytics/member-activity")
def member_activity(
    days: int = 30,
    db: Session = Depends(get_db),
    current = Depends(get_current_member)
):
    """Get member activity over time"""
    org_id = current.organization_id
    since = datetime.utcnow() - timedelta(days=days)
    
    # Get contributions by date
    contributions = db.query(
        func.date(Contribution.created_at).label('date'),
        func.count(Contribution.id).label('count'),
        func.sum(Contribution.amount).label('total')
    ).filter(
        Contribution.organization_id == org_id,
        Contribution.created_at >= since,
        Contribution.status == TransactionStatus.COMPLETED
    ).group_by(func.date(Contribution.created_at)).all()
    
    # Get loans by date
    loans = db.query(
        func.date(Loan.created_at).label('date'),
        func.count(Loan.id).label('count'),
        func.sum(Loan.amount).label('total')
    ).filter(
        Loan.organization_id == org_id,
        Loan.created_at >= since
    ).group_by(func.date(Loan.created_at)).all()
    
    return {
        "contributions": [
            {"date": str(c.date), "count": c.count, "total": float(c.total or 0)}
            for c in contributions
        ],
        "loans": [
            {"date": str(l.date), "count": l.count, "total": float(l.total or 0)}
            for l in loans
        ]
    }


@router.get("/analytics/retention")
def member_retention(
    db: Session = Depends(get_db),
    current = Depends(get_current_member)
):
    """Get member retention metrics"""
    org_id = current.organization_id
    
    # Members by join date
    now = datetime.utcnow()
    this_month = datetime(now.year, now.month, 1)
    last_month = this_month - timedelta(days=1)
    two_months_ago = last_month - timedelta(days=1)
    
    joined_this_month = db.query(Member).filter(
        Member.organization_id == org_id,
        Member.created_at >= this_month
    ).count()
    
    joined_last_month = db.query(Member).filter(
        Member.organization_id == org_id,
        Member.created_at >= last_month,
        Member.created_at < this_month
    ).count()
    
    total_members = db.query(Member).filter(Member.organization_id == org_id).count()
    
    # Active members (contributed in last 30 days)
    thirty_days_ago = now - timedelta(days=30)
    active_members = db.query(Contribution.member_id).filter(
        Contribution.organization_id == org_id,
        Contribution.created_at >= thirty_days_ago,
        Contribution.status == TransactionStatus.COMPLETED
    ).distinct().count()
    
    retention_rate = (active_members / total_members * 100) if total_members > 0 else 0
    
    return {
        "total_members": total_members,
        "joined_this_month": joined_this_month,
        "joined_last_month": joined_last_month,
        "active_members": active_members,
        "retention_rate": round(retention_rate, 1),
    }


@router.get("/analytics/top-contributors")
def top_contributors(
    limit: int = 10,
    db: Session = Depends(get_db),
    current = Depends(get_current_member)
):
    """Get top contributing members"""
    org_id = current.organization_id
    
    results = db.query(
        Member.id,
        Member.name,
        func.sum(Contribution.amount).label('total')
    ).join(
        Contribution, Member.id == Contribution.member_id
    ).filter(
        Member.organization_id == org_id,
        Contribution.status == TransactionStatus.COMPLETED
    ).group_by(Member.id, Member.name).order_by(
        func.sum(Contribution.amount).desc()
    ).limit(limit).all()
    
    return [
        {"member_id": r.id, "name": r.name, "total": float(r.total or 0)}
        for r in results
    ]


@router.get("/analytics/financial-ratios")
def financial_ratios(
    db: Session = Depends(get_db),
    current = Depends(get_current_member)
):
    """Calculate financial health ratios"""
    org_id = current.organization_id
    
    # Total capital
    contributions = db.query(Contribution).filter(
        Contribution.organization_id == org_id,
        Contribution.status == TransactionStatus.COMPLETED
    ).all()
    total_capital = sum(float(c.amount) for c in contributions)
    
    # Outstanding loans
    loans = db.query(Loan).filter(
        Loan.organization_id == org_id,
        Loan.status == LoanStatus.ACTIVE
    ).all()
    total_loans = sum(float(l.amount) for l in loans)
    
    # Calculate ratios
    if total_capital > 0:
        loan_to_capital = (total_loans / total_capital) * 100
        liquidity_ratio = ((total_capital - total_loans) / total_capital) * 100
    else:
        loan_to_capital = 0
        liquidity_ratio = 0
    
    return {
        "total_capital": total_capital,
        "total_outstanding_loans": total_loans,
        "loan_to_capital_ratio": round(loan_to_capital, 1),
        "liquidity_ratio": round(liquidity_ratio, 1),
        "health_status": "Healthy" if liquidity_ratio > 50 else "Needs Attention"
    }
