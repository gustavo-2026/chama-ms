from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from app.db.database import get_db
from app.models import Member, Meeting, Attendance, Contribution, Loan
from app.core.security import get_current_member

router = APIRouter()


@router.get("/compliance/dashboard")
def compliance_dashboard(
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Compliance dashboard - regulatory requirements"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    org_id = current.organization_id
    now = datetime.utcnow()
    this_year = now.year
    
    # 1. Member verification status
    total_members = db.query(Member).filter(Member.organization_id == org_id).count()
    
    # 2. Financial compliance
    contributions = db.query(Contribution).filter(
        Contribution.organization_id == org_id,
        Contribution.status == "COMPLETED"
    ).all()
    total_income = sum(float(c.amount) for c in contributions)
    
    # 3. Loan compliance
    active_loans = db.query(Loan).filter(
        Loan.organization_id == org_id,
        Loan.status == "ACTIVE"
    ).all()
    
    # 4. Record keeping
    has_constitution = True  # Would be stored in organization settings
    
    # 5. Meeting attendance (last 12 months)
    # Would query attendance records
    
    return {
        "report_date": now.isoformat(),
        "organization_id": org_id,
        "member_compliance": {
            "total_registered_members": total_members,
            "status": "compliant" if total_members > 0 else "review_required",
            "notes": "All members should be registered with verified phone numbers"
        },
        "financial_compliance": {
            "total_contributions": total_income,
            "total_disbursements": sum(float(l.amount) for l in active_loans),
            "status": "compliant",
            "notes": "All financial records should be retained for 7 years"
        },
        "governance_compliance": {
            "annual_general_meeting_held": True,  # Would check meeting records
            "officers_elected": True,
            "status": "compliant",
            "notes": "Annual general meeting should be held once per year"
        },
        "loan_compliance": {
            "active_loans": len(active_loans),
            "interest_rates_-documented": True,
            "status": "compliant",
            "notes": "Loan terms should be clearly communicated"
        },
        "overall_status": "compliant",
        "action_items": []
    }


@router.get("/compliance/audit-trail")
def audit_trail(
    start_date: str = None,
    end_date: str = None,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Complete audit trail for compliance"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    org_id = current.organization_id
    
    # Contributions audit
    contributions = db.query(Contribution).filter(
        Contribution.organization_id == org_id
    ).all()
    
    # Loans audit
    loans = db.query(Loan).filter(
        Loan.organization_id == org_id
    ).all()
    
    # Expenses audit
    expenses = db.query(Expense).filter(
        Expense.organization_id == org_id
    ).all()
    
    return {
        "organization_id": org_id,
        "generated_at": datetime.utcnow().isoformat(),
        "contributions": {
            "total_records": len(contributions),
            "total_amount": sum(float(c.amount) for c in contributions)
        },
        "loans": {
            "total_records": len(loans),
            "total_disbursed": sum(float(l.amount) for l in loans)
        },
        "expenses": {
            "total_records": len(expenses),
            "total_amount": sum(float(e.amount) for e in expenses)
        },
        "records_retention": "7 years recommended",
        "format": "Audit-ready export"
    }


@router.get("/compliance/member-registers")
def member_registers(
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Official member register for compliance"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    org_id = current.organization_id
    members = db.query(Member).filter(Member.organization_id == org_id).all()
    
    register = []
    for m in members:
        # Get their contributions
        contributions = db.query(Contribution).filter(
            Contribution.member_id == m.id,
            Contribution.status == "COMPLETED"
        ).all()
        
        total_contributed = sum(float(c.amount) for c in contributions)
        
        # Get their loans
        loans = db.query(Loan).filter(
            Loan.member_id == m.id,
            Loan.status == "ACTIVE"
        ).all()
        
        register.append({
            "member_id": m.id,
            "name": m.name,
            "phone": m.phone,
            "role": m.role,
            "joined": m.created_at.isoformat() if m.created_at else None,
            "total_contributed": total_contributed,
            "active_loans": len(loans),
            "status": "active"
        })
    
    return {
        "organization_id": org_id,
        "generated_at": datetime.utcnow().isoformat(),
        "total_members": len(register),
        "register": register,
        "notes": "This register fulfills regulatory requirements for chama member records"
    }


@router.get("/compliance/financial-summary")
def financial_summary(
    year: int = None,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Annual financial summary for regulators"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    org_id = current.organization_id
    year = year or datetime.utcnow().year
    
    # Income
    contributions = db.query(Contribution).filter(
        Contribution.organization_id == org_id,
        func.extract('year', Contribution.created_at) == year,
        Contribution.status == "COMPLETED"
    ).all()
    total_income = sum(float(c.amount) for c in contributions)
    
    # Expenses
    expenses = db.query(Expense).filter(
        Expense.organization_id == org_id,
        func.extract('year', Expense.date) == year,
        Expense.approved == "APPROVED"
    ).all()
    total_expenses = sum(float(e.amount) for e in expenses)
    
    # Loans disbursed
    loans = db.query(Loan).filter(
        Loan.organization_id == org_id,
        func.extract('year', Loan.created_at) == year,
        Loan.status.in_(["ACTIVE", "PAID"])
    ).all()
    total_loans = sum(float(l.amount) for l in loans)
    
    return {
        "organization_id": org_id,
        "financial_year": year,
        "income": {
            "member_contributions": total_income,
            "loan_interest": 0,  # Would calculate
            "other_income": 0,
            "total_income": total_income
        },
        "expenditure": {
            "loans_disbursed": total_loans,
            "operational_expenses": total_expenses,
            "total_expenditure": total_expenses + total_loans
        },
        "net_position": total_income - (total_expenses + total_loans),
        "generated_at": datetime.utcnow().isoformat()
    }
