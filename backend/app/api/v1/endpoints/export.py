from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models import Member, Contribution, Loan, TransactionStatus, LoanStatus
from app.core.security import get_current_member
import csv
import io

router = APIRouter()


def generate_csv(data: list, headers: list) -> str:
    """Generate CSV string from data"""
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=headers)
    writer.writeheader()
    for row in data:
        writer.writerow(row)
    return output.getvalue()


@router.get("/export/members")
def export_members_csv(
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Export members to CSV"""
    members = db.query(Member).filter(
        Member.organization_id == current.organization_id
    ).all()
    
    data = [
        {
            "Name": m.name,
            "Phone": m.phone,
            "Role": m.role,
            "Tier": m.contribution_tier,
            "M-Pesa Linked": "Yes" if m.mpesa_linked else "No",
            "Joined": m.created_at.strftime("%Y-%m-%d") if m.created_at else ""
        }
        for m in members
    ]
    
    csv_content = generate_csv(data, ["Name", "Phone", "Role", "Tier", "M-Pesa Linked", "Joined"])
    
    return {
        "filename": "members.csv",
        "content": csv_content,
        "type": "text/csv"
    }


@router.get("/export/contributions")
def export_contributions_csv(
    period_month: int = None,
    period_year: int = None,
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Export contributions to CSV"""
    query = db.query(Contribution).filter(
        Contribution.organization_id == current.organization_id,
        Contribution.status == TransactionStatus.COMPLETED
    )
    
    if period_month:
        query = query.filter(Contribution.period_month == period_month)
    if period_year:
        query = query.filter(Contribution.period_year == period_year)
    
    contributions = query.all()
    
    # Get member names
    member_ids = list(set(c.member_id for c in contributions))
    members = db.query(Member).filter(Member.id.in_(member_ids)).all()
    member_names = {m.id: m.name for m in members}
    
    data = [
        {
            "Date": c.created_at.strftime("%Y-%m-%d") if c.created_at else "",
            "Member": member_names.get(c.member_id, "Unknown"),
            "Amount": float(c.amount),
            "Method": c.method,
            "Period": f"{c.period_month}/{c.period_year}" if c.period_month else "N/A",
            "Receipt": c.mpesa_receipt or ""
        }
        for c in contributions
    ]
    
    csv_content = generate_csv(data, ["Date", "Member", "Amount", "Method", "Period", "Receipt"])
    
    return {
        "filename": f"contributions_{period_year or 'all'}.csv",
        "content": csv_content,
        "type": "text/csv"
    }


@router.get("/export/loans")
def export_loans_csv(
    db: Session = Depends(get_db),
    current: Member = Depends(get_current_member)
):
    """Export loans to CSV"""
    loans = db.query(Loan).filter(
        Loan.organization_id == current.organization_id
    ).all()
    
    # Get member names
    member_ids = list(set(l.member_id for l in loans))
    members = db.query(Member).filter(Member.id.in_(member_ids)).all()
    member_names = {m.id: m.name for m in members}
    
    data = [
        {
            "Date": l.created_at.strftime("%Y-%m-%d") if l.created_at else "",
            "Member": member_names.get(l.member_id, "Unknown"),
            "Amount": float(l.amount),
            "Interest Rate": float(l.interest_rate),
            "Status": l.status,
            "Due Date": l.due_date.strftime("%Y-%m-%d") if l.due_date else "",
            "Purpose": l.purpose or ""
        }
        for l in loans
    ]
    
    csv_content = generate_csv(data, ["Date", "Member", "Amount", "Interest Rate", "Status", "Due Date", "Purpose"])
    
    return {
        "filename": "loans.csv",
        "content": csv_content,
        "type": "text/csv"
    }
