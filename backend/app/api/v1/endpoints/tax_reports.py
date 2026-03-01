from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from app.db.database import get_db
from app.models import Member, Contribution, Loan
from app.core.security import get_current_member

router = APIRouter()


@router.get("/reports/tax")
def tax_report(
    year: int,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Generate tax report for a year"""
    org_id = current.organization_id
    
    # Total contributions (income to chama)
    contributions = db.query(Contribution).filter(
        Contribution.organization_id == org_id,
        func.extract('year', Contribution.created_at) == year,
        Contribution.status == "COMPLETED"
    ).all()
    total_income = sum(float(c.amount) for c in contributions)
    
    # Total interest earned from loans
    loans = db.query(Loan).filter(
        Loan.organization_id == org_id,
        func.extract('year', Loan.approved_at) == year,
        Loan.status == "PAID"
    ).all()
    interest_earned = sum(float(l.amount) * float(l.interest_rate) / 100 for l in loans)
    
    # Total expenses
    expenses = db.query(Expense).filter(
        Expense.organization_id == org_id,
        func.extract('year', Expense.date) == year,
        Expense.approved == "APPROVED"
    ).all()
    total_expenses = sum(float(e.amount) for e in expenses)
    
    # Calculate net
    net = total_income - total_expenses
    
    return {
        "year": year,
        "organization_id": org_id,
        "total_contributions": total_income,
        "interest_earned": interest_earned,
        "total_expenses": total_expenses,
        "net": net,
        "summary": "This report is for informational purposes. Consult a tax professional for filing."
    }


@router.get("/reports/audit")
def audit_export(
    year: int,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Export data for external auditors"""
    if current.role not in ["TREASURER", "CHAIR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    org_id = current.organization_id
    
    # Members
    members = db.query(Member).filter(Member.organization_id == org_id).all()
    
    # Contributions
    contributions = db.query(Contribution).filter(
        Contribution.organization_id == org_id,
        func.extract('year', Contribution.created_at) == year
    ).all()
    
    # Loans
    loans = db.query(Loan).filter(
        Loan.organization_id == org_id,
        func.extract('year', Loan.created_at) == year
    ).all()
    
    # Expenses
    expenses = db.query(Expense).filter(
        Expense.organization_id == org_id,
        func.extract('year', Expense.date) == year
    ).all()
    
    return {
        "export_date": datetime.utcnow().isoformat(),
        "year": year,
        "organization_id": org_id,
        "members_count": len(members),
        "contributions_count": len(contributions),
        "contributions_total": sum(float(c.amount) for c in contributions),
        "loans_count": len(loans),
        "loans_total": sum(float(l.amount) for l in loans),
        "expenses_count": len(expenses),
        "expenses_total": sum(float(e.amount) for e in expenses),
        "format": "This data is prepared for external audit review"
    }


@router.get("/reports/annual")
def annual_statement(
    year: int,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Annual financial statement"""
    org_id = current.organization_id
    
    # Monthly breakdown
    monthly_data = []
    for month in range(1, 13):
        contributions = db.query(Contribution).filter(
            Contribution.organization_id == org_id,
            func.extract('year', Contribution.created_at) == year,
            func.extract('month', Contribution.created_at) == month,
            Contribution.status == "COMPLETED"
        ).all()
        
        expenses = db.query(Expense).filter(
            Expense.organization_id == org_id,
            func.extract('year', Expense.date) == year,
            func.extract('month', Expense.date) == month,
            Expense.approved == "APPROVED"
        ).all()
        
        monthly_data.append({
            "month": month,
            "contributions": sum(float(c.amount) for c in contributions),
            "expenses": sum(float(e.amount) for e in expenses),
            "net": sum(float(c.amount) for c in contributions) - sum(float(e.amount) for e in expenses)
        })
    
    total_contributions = sum(m["contributions"] for m in monthly_data)
    total_expenses = sum(m["expenses"] for m in monthly_data)
    
    return {
        "year": year,
        "organization_id": org_id,
        "monthly": monthly_data,
        "totals": {
            "contributions": total_contributions,
            "expenses": total_expenses,
            "net": total_contributions - total_expenses
        }
    }
